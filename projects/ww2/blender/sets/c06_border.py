# Chapter 6: the Soviet border at dawn, 22 June 1941, and a Soviet airfield caught on the ground.
# Border (three coords): wheat fields at y 0; the dirt road runs along z (x -3..3); the border at z 20: a striped
# red-green frontier post at (4.5, 0, 19), a barrier pole across the road, a wooden watchtower at (-12, 0, 24), barbed
# wire along z 20 except the road; a birch copse at x -30..-15, z 0..20; a log guard hut at (9, 0, 14).
# German tanks roll down the road from z 90 toward the camera (update: frames 244-500 and 884-958), infantry walks in
# the wheat (cards); artillery flashes on the far horizon (cards).
# Airfield region (x 100..170, z -10..60): grass strip, rows of I-16 fighters (most wrecked, burning), a hangar on
# fire, fuel drums; keep x 118..132, z 0..12 clear (people). Camera for it looks +z from around (125, 1.5, -6).
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, crate, barrel, stripes, R90
from .c05_kit import (sky, ground_mat, height_mesh, sun_light, area, point, truck, panzer, i16, pose, lathe, tube, worn, mat_once, cached, empty,
                      smoke_mat, smoke_column, fire, he111, clone, show, fsphere)
from .front import oil_drum, sandbag_wall, sandmat
from .warroom import barbed_coil

def wheat_mat():
    def mk():
        m = lib.principled("c6wheat", hexc("#c8a84a"), 0.85); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.08; nz.inputs["Detail"].default_value = 5; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = lib.ramp(n, l, nz.outputs["Fac"], [(0.3, hexc("#a8883a")), (0.5, hexc("#c8a84a")), (0.7, hexc("#d8bc62"))]); l.new(r.outputs["Color"], b.inputs["Base Color"])
        fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 60; fn.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], fn.inputs["Vector"]); lib.bump(n, l, fn.outputs["Fac"], 0.8, 0.05)
        return m
    return cached("c6wheat", mk)

def wheat_tufts(name, pts, rnd, mat):
    """dense standing stalks with heads (one mesh)"""
    K = Kit(name)
    for (x, y, z) in pts:
        for j in range(5):
            dx, dz = rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25); h = rnd.uniform(0.8, 1.05)
            K.box((x + dx, y + h / 2, z + dz), (0.012, h, 0.012), mat, rnd.uniform(0, 3), 0.0, rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12))
            K.box((x + dx, y + h + 0.05, z + dz), (0.03, 0.11, 0.03), mat, 0, 0.0)
    K.build()

def build(M, D):
    random.seed(1941); K_.reset(); rnd = random.Random(22); sid = D.get("id", 0)
    sky((0.22, 0.3, 0.52), (0.72, 0.56, 0.5), (1.0, 0.66, 0.36), sun_dir=(-0.75, 0.08, -0.65), sun_col=(1.0, 0.55, 0.2), glow=1.0, disc=20.0, clouds=0.8,
        cloud_col=(1.0, 0.75, 0.55), cloud_shade=(0.5, 0.42, 0.5))
    road = ground_mat("c6road", [(0.3, "#6a5a42"), (0.6, "#8a7452")], 0.3, 3)
    def H(x, z): return 0.3 * noise.noise(Vector((x * 0.05, z * 0.05, 0.3))) * min(1.0, abs(x) / 6)
    height_mesh("field", -120, 200, -40, 260, 2.0, H, wheat_mat())
    K = Kit("border"); K.box((0, 0.02, 100), (6, 0.04, 300), road, 0, 0.0)
    for x in (-1.6, 1.6):
        for k in range(100): K.box((x, 0.045, -40 + k * 3), (0.35, 0.02, 3.1), pm("#4a3a28", 0.95), 0, 0.0)
    rnd2 = random.Random(5)
    wheat_tufts("wheat", [(x, H(x, z), z) for x, z in ((rnd2.uniform(-22, 22), rnd2.uniform(-6, 40)) for _ in range(900)) if abs(x) > 3.6], rnd2, pm("#d0b058", 0.8))
    # the frontier post: striped red-green, a red plate with a star; the barrier; the watchtower; the guard hut
    for k in range(10): K.box((4.5, 0.15 + k * 0.3, 19), (0.22, 0.3, 0.22), pm("#a81e22" if k % 2 else "#2a5a2a", 0.5), 0, 0.01)
    K.box((4.5, 3.2, 18.88), (0.5, 0.5, 0.04), pm("#a81e22", 0.4), 0, 0.01)
    lathe("bstar", [(0.0, -0.12), (0.14, 0.0), (0.0, 0.12)], (4.5, 3.2, 18.85), K_.gold(), 5, tilt=__import__("mathutils").Matrix.Rotation(math.radians(90), 3, "X"))
    text("СССР", (4.5, 2.9, 18.85), 0.09, K_.gold(), 0, "sans", 0.002)
    for k in range(12): K.box((-1.0 + k * 0.5, 1.0, 20), (0.5, 0.12, 0.12), pm("#e8e0d0" if k % 2 else "#a81e22", 0.5), 0, 0.01)
    K.box((3.6, 0.55, 20), (0.2, 1.1, 0.2), wood("#5a4a32", "#3a3020", 8, 0.8), 0, 0.01)
    TW = wood("#6a5a42", "#3a3020", 6, 0.85)
    for sx in (-1, 1):
        for sz in (-1, 1): K.box((-12 + sx * 1.2, 3.5, 24 + sz * 1.2), (0.2, 7.0, 0.2), TW, 0, 0.0, sz * 0.06, -sx * 0.06)
    K.box((-12, 6.6, 24), (2.8, 0.15, 2.8), TW, 0, 0.01); K.box((-12, 7.3, 24), (2.8, 1.2, 0.08), TW, 0, 0.0)
    K.cyl((-12, 8.6, 24), 2.2, 1.0, wood("#4a3a28", "#2a2018", 6, 0.9), 4, "y", 0.2, math.pi / 4)
    for j in range(6): K.box((-12, 1.0 + j * 1.0, 22.8), (2.4, 0.1, 0.1), TW, 0, 0.0, 0, 0.4 * (1 if j % 2 else -1))
    LOG = wood("#7a6040", "#4a3a24", 4, 0.85)
    for j in range(8): K.cyl((9, 0.15 + j * 0.28, 14), 0.15, 4.0, LOG, 10, "z")
    for j in range(8): K.cyl((9, 0.15 + j * 0.28, 14), 0.15, 3.0, LOG, 10, "x") if j % 3 == 0 else None
    K.box((9, 2.5, 14), (3.6, 0.1, 4.6), pm("#5a4a3a", 0.9), 0, 0.02, 0, 0.0); K.box((7.5, 1.3, 14), (0.06, 0.8, 0.9), pm("#1a2230", 0.1), 0, 0.0)
    K.cyl((9, 2.75, 14), 2.3, 1.0, wood("#5a4a32", "#3a3020", 6, 0.9), 4, "z", 0.1)
    bw = mat_once("c6wire", lambda: worn("c6wire", "#4a4440", "#6a3a1e", 0.5, 0.8, 20, 0.6))
    for k in range(10):
        x0 = 4 + k * 4 if k < 5 else -4 - (k - 5) * 4
        for e in (0,): K.cyl((x0, 0.7, 20.3), 0.05, 1.4, TW, 6)
        for y in (0.3, 0.7, 1.1): K.box((x0 + (2 if k < 5 else -2), y, 20.3), (4, 0.012, 0.012), pm("#4a4440", 0.5, 0.8), 0, 0.0)
    # birches
    bark = mat_once("c6birch", lambda: worn("c6birch", "#e8e4dc", "#2a2a2a", 0.7, 0.0, 10, 0.75, "#c8c4bc"))
    leaves = [pm("#5a7a32", 0.8), pm("#6a8a3a", 0.8), pm("#4a6a2a", 0.8)]
    for k in range(40):
        x, z = rnd.uniform(-34, -14), rnd.uniform(-6, 22); h = rnd.uniform(8, 13)
        K.cyl((x, h / 2, z), 0.14, h, bark, 8, "y", 0.08)
        for j in range(5): fsphere(K, (x + rnd.uniform(-1.2, 1.2), h * (0.6 + 0.1 * j), z + rnd.uniform(-1.2, 1.2)), rnd.uniform(1.0, 1.8), leaves[(k + j) % 3], 10, (1, 0.8, 1))
    # a village on the Soviet side behind the camera, and haystacks
    for k, (x, z) in enumerate(((16, -14), (22, -10), (-14, -16), (28, -22))):
        for j in range(10): K.cyl((x, 0.15 + j * 0.28, z), 0.15, 5.0, LOG, 10, "x")
        K.cyl((x, 3.6, z), 3.2, 5.6, pm("#5a4a3a", 0.9), 4, "x", 0.2, math.pi / 4)
        K.box((x, 1.5, z - 2.0), (0.8, 0.9, 0.05), pm("#2a4a7a", 0.4), 0, 0.02)
    for k, (x, z) in enumerate(((-9, 6), (12, 30), (-20, 40), (18, 5))): K.cyl((x, 1.4, z), 1.6, 2.8, wheat_mat(), 14, "y", 0.2)
    K.build()
    # ---------------- the airfield region ----------------
    A = Kit("afield"); grass = ground_mat("c6grass", [(0.3, "#4a5a2a"), (0.6, "#6a7a3a")], 0.05, 3)
    A.box((135, 0.03, 25), (90, 0.04, 90), grass, 0, 0.0)
    smm = smoke_mat("c6smoke", "#1e1a18", 0.55)
    planes = []
    for k in range(10):
        x = 108 + (k % 5) * 12; z = 18 + (k // 5) * 16; wr = k not in (1, 7)
        e = i16(f"i16_{k}", wrecked=wr); pose(e, (x, 1.25, z), math.pi + rnd.uniform(-0.2, 0.2), 0.12 if not wr else rnd.uniform(-0.2, 0.1), 0.0 if not wr else rnd.uniform(-0.3, 0.3))
        if wr and k % 2 == 0:
            fire(f"pfire{k}", (x, 0.3, z), 1.4, seed=k, energy=2000)
            smoke_column(f"psm{k}", (x, 2.5, z), 30, 1.5, 6, smm, drift=(10, 18), seed=k, puffs=10)
    HG = mat_once("c6hangar", lambda: worn("c6hangar", "#5a5a52", "#2a2420", 0.7, 0.3, 3, 0.6, "#1a1614"))
    A.cyl((150, 0.0, 58), 10, 22, HG, 24, "x"); A.box((150, -5, 58), (22.4, 10, 20.4), pm("#3a3430", 0.8), 0, 0.0)
    fire("hfire", (148, 5, 55), 4.0, seed=7, energy=12000); smoke_column("hsm", (148, 10, 56), 60, 4, 14, smm, drift=(20, 30), seed=3, puffs=12)
    for k in range(8): oil_drum(f"c6dr{k}", (116 + (k % 4) * 0.7, 0, 4 + (k // 4) * 0.7), mat_once("c6drum", lambda: worn("c6drum", "#4a5a3a", "#2a2a22", 0.6, 0.4, 8, 0.6)))
    for k in range(5): lib.blob(f"crater{k}", T(112 + k * 9, -0.2, 10 + (k % 2) * 7), (2.0, 0.4, 2.0), pm("#2a2018", 0.95), 0.3, k)
    A.box((135, 4, 70), (90, 8, 1), pm("#3a4a2a", 0.9), 0, 0.0)
    A.build()
    truck("c6truck", (140, 0, 6), 0.6, "#4a5a3a", "#5a6a48")
    # ---------------- moving German tanks and bombers ----------------
    tanks = []
    for k in range(5):
        e = empty(f"gt{k}"); kk = Kit(f"gtk{k}"); panzer(f"g{k}", (0, 0, 0), 0.0, "#5a5e5a", k != 0, kk)
        for o in kk.build(): o.parent = e
        tanks.append(e)
    he = he111("c6he"); bombers = [he] + [clone(he, f"c6he{k}") for k in range(1, 6)]
    sun_light((0.75, -0.25, 0.6), 4.0, (1.0, 0.6, 0.3), 1.0)
    area((0, 30, -40), (0, 0, 30), 9000, (0.5, 0.55, 0.9), 40)
    area((125, 30, -30), (125, 0, 30), 9000, (0.6, 0.55, 0.8), 40)
    def update(f):
        for k, e in enumerate(tanks):
            u = max(0, f - 244) if f < 700 else max(0, f - 884)
            z = 40 + k * 16 - 0.22 * u; x = (-1.2 if k % 2 else 1.2)
            e.location = T(x, 0.02, z); e.rotation_euler = (0, 0, math.pi / 2 + math.pi * 0)
            e.rotation_euler = (0, 0, math.pi / 2)
        for k, e in enumerate(bombers):
            if 950 <= f < 1140:
                u = f - 950; pose(e, (110 + k * 14 - 0.5 * u, 70 + (k % 2) * 8, 90 + (k % 3) * 12 - 2.2 * u), math.pi, 0, 0)
            else:
                u = f - 160; pose(e, (-30 + k * 16, 140 + (k % 2) * 12, 200 + (k % 3) * 15 - 2.0 * u), math.pi, 0, 0)
    update(244)
    return {"update": update}
