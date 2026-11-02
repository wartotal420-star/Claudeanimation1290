# Chapter 5: the Western Desert, Egypt / Libya 1940-41. Dunes, a coast-road track with telegraph poles and signposts,
# the pyramids far off, palms at a small oasis; a British camp (truck, tents, brew-up) and Rommel's tanks.
# Layout (three coords): flat hard sand where people stand: x -30..30, z -5..40 (dunes rise outside it); the track
# runs along x at z 12 (Italian column, prisoners); the British camp at x 8..18, z 18..26 (truck at (14, 0, 24), tea
# brew at (10, 0, 19)); the dune crest behind it at z 34..40 (Rommel's tanks burst over it, shot 24, frames
# 2165-2235); Rommel's tank for shots 23/25 at (0, 0, 9), nose toward -z (the camera), turret hatch top y 3.3.
# The pyramids at z 900; oasis palms at x -40..-20, z 30..50.
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, crate, barrel, stripes, R90
from .c05_kit import (sky, ground_mat, height_mesh, sun_light, area, point, truck, panzer, lathe, tube, worn, mat_once, cached, empty, smoke_mat, smoke_column, loft_k)
from .front import oil_drum, sandbag_wall, sandmat

def H(x, z):
    flat = max(0.0, min(1.0, max(abs(x) - 30, z - 33, -5 - z) / 10))
    d = 4.0 * (0.5 + 0.5 * noise.noise(Vector((x * 0.018, z * 0.03, 0.4)))) + 1.2 * noise.noise(Vector((x * 0.07, z * 0.05, 2.0)))
    crest = 3.5 * math.exp(-((z - 37) / 4.0) ** 2) * (1 - 0.3 * math.cos(x * 0.08))
    return 0.15 * noise.noise(Vector((x * 0.1, z * 0.1, 5))) + flat * max(0.0, d) + crest

def sand_mat():
    def mk():
        m = lib.principled("c5sand", hexc("#d8b47a"), 0.85); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); big = n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 0.04; big.inputs["Detail"].default_value = 4; l.new(tc.outputs["Object"], big.inputs["Vector"])
        r = lib.ramp(n, l, big.outputs["Fac"], [(0.3, hexc("#b8783a")), (0.5, hexc("#cc9a5a")), (0.7, hexc("#dcb070"))])
        l.new(r.outputs["Color"], b.inputs["Base Color"])
        wv = n.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 2.2; wv.inputs["Distortion"].default_value = 6; wv.inputs["Detail"].default_value = 3; l.new(tc.outputs["Object"], wv.inputs["Vector"])
        fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 30; l.new(tc.outputs["Object"], fn.inputs["Vector"])
        ad = n.new("ShaderNodeMath"); ad.operation = "MULTIPLY_ADD"; ad.inputs[1].default_value = 0.3; l.new(wv.outputs["Fac"], ad.inputs[0]); l.new(fn.outputs["Fac"], ad.inputs[2])
        lib.bump(n, l, ad.outputs[0], 0.35, 0.02); return m
    return cached("c5sand", mk)

def palm(K, x, y, z, h, lean, rnd):
    trunk = wood("#7a6040", "#4a3a24", 20, 0.9); fr = pm("#3a6a2a", 0.8); fr2 = pm("#5a7a30", 0.8)
    top = (x + lean * h, y + h, z + lean * h * 0.3)
    tube(f"palm{x}{z}", [(x, y, z), (x + lean * h * 0.3, y + h * 0.5, z + lean * h * 0.1), top], 0.22, trunk, taper=lambda f: 1.1 - 0.5 * f)
    for k in range(11):
        a = k / 11 * math.tau + rnd.random() * 0.3; L = rnd.uniform(3.0, 4.2)
        p1 = (top[0] + math.cos(a) * L * 0.5, top[1] + 0.6, top[2] + math.sin(a) * L * 0.5); p2 = (top[0] + math.cos(a) * L, top[1] - 1.2, top[2] + math.sin(a) * L)
        tube(f"pf{x}{z}{k}", [top, p1, p2], 0.28, fr if k % 2 else fr2, taper=lambda f: 1.0 - 0.95 * f)
    for k in range(5): K.sphere((top[0] + 0.25 * math.cos(k), top[1] - 0.3, top[2] + 0.25 * math.sin(k)), 0.14, pm("#6a3a1a", 0.6), 8)

def build(M, D):
    random.seed(1941); K_.reset(); rnd = random.Random(8); sid = D.get("id", 0)
    sky((0.1, 0.28, 0.62), (0.4, 0.56, 0.8), (0.9, 0.78, 0.6), sun_dir=(0.3, 0.75, 0.4), sun_col=(1.0, 0.9, 0.7), glow=0.6, strength=0.8)
    height_mesh("sand", -260, 260, -60, 420, 1.6, H, sand_mat())
    far = ground_mat("c5sandfar", [(0.3, "#c89a5a"), (0.6, "#dcb87a")], 0.002, 0.05)
    height_mesh("sandfar", -3000, 3000, 420, 4000, 60, lambda x, z: 2.0 * noise.noise(Vector((x * 0.003, z * 0.003, 1.0))) - 3, far)
    K = Kit("des")
    # pyramids of Giza on the horizon
    PY = grime("c5pyr", "#d8b880", 0.25)
    for (x, z, s) in ((-260, 1100, 140), (-110, 1300, 130), (40, 1450, 70)):
        rings = [[(x + s * (1 - f) * math.cos(a), f * s * 0.95, z + s * (1 - f) * math.sin(a)) for a in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4)] for f in (0.0, 0.999)]
        loft_k(K, rings, PY)
    # the track: wheel ruts, telegraph poles with wire, signposts, oil-drum markers
    for k in range(70):
        K.box((-120 + k * 3.5, 0.02 + H(-120 + k * 3.5, 12), 11.2 + 0.2 * math.sin(k)), (3.6, 0.03, 0.35), pm("#b88a52", 0.95), 0, 0.0)
        K.box((-120 + k * 3.5, 0.02 + H(-120 + k * 3.5, 13), 12.9 + 0.2 * math.sin(k * 1.3)), (3.6, 0.03, 0.35), pm("#b88a52", 0.95), 0, 0.0)
    POLE = wood("#6a5a42", "#3a3020", 8, 0.8)
    for k in range(9):
        x = -100 + k * 26; y0 = H(x, 4.0)
        K.cyl((x, y0 + 3.2, 4.0), 0.09, 6.4, POLE, 8); K.box((x, y0 + 6.1, 4.0), (0.12, 0.1, 1.4), POLE, 0, 0.01)
        if k < 8:
            for sd in (-0.6, 0.6): tube(f"tw{k}{sd}", [(x, y0 + 6.2, 4 + sd), (x + 13, y0 + 5.6, 4 + sd), (x + 26, H(x + 26, 4) + 6.2, 4 + sd)], 0.012, pm("#1a1a1a", 0.5), 6, 0)
    SG = wood("#c8b890", "#8a7a58", 12, 0.8)
    K.cyl((-6, 1.4 + H(-6, 15.5), 15.5), 0.07, 2.8, SG, 8)
    for k, (s, yaw, y) in enumerate((("SIDI BARRANI  30", 0.25, 2.55), ("MERSA MATRUH  130", -0.3, 2.2), ("CAIRO  350", 0.1, 1.85))):
        K.box((-6 + 0.5 * math.cos(yaw), y + H(-6, 15.5), 15.5 - 0.5 * math.sin(yaw)), (1.5, 0.26, 0.04), SG, yaw, 0.01)
        text(s, (-6 + 0.5 * math.cos(yaw) - 0.03 * math.sin(yaw), y + H(-6, 15.5), 15.5 - 0.5 * math.sin(yaw) - 0.03 * math.cos(yaw)), 0.12, pm("#2a1a10", 0.7), yaw, "sans", 0.002, fit=1.35)
    drum = mat_once("c5drum", lambda: worn("c5drum", "#c8b080", "#6a4a2a", 0.6, 0.4, 8, 0.6, "#8a6a3a"))
    for k, (x, z, ly) in enumerate(((-18, 9.5, False), (-17.3, 9.9, False), (22, 9.0, False), (26, 15.5, True), (-24, 15.8, True), (5, 30, False), (5.7, 30.4, False))):
        oil_drum(f"dr{k}", (x, H(x, z), z), drum, ly, k)
    # British camp: bell tents, the truck, a brew-up (stove, kettle, tins, mugs), boxes, a camouflage net
    TENT = cloth("#c8b48a")
    for k, (x, z) in enumerate(((20, 22), (24, 26), (18, 29))):
        lathe(f"tent{k}", [(2.2, 0.0), (2.0, 0.5), (0.1, 3.0), (0.0, 3.05)], (x, H(x, z), z), TENT, 24)
        K.cyl((x, H(x, z) + 1.6, z), 0.04, 3.2, POLE, 6)
        for j in range(6): a = j / 6 * math.tau; tube(f"guy{k}{j}", [(x + 2.1 * math.cos(a), H(x, z) + 0.45, z + 2.1 * math.sin(a)), (x + 3.4 * math.cos(a), H(x, z), z + 3.4 * math.sin(a))], 0.01, pm("#c8b890", 0.8), 2, 0)
    truck("bedford", (14, H(14, 24), 24), 2.8, "#b89a62", "#a88a5a")
    bx0 = (10.0, H(10, 19), 19.0)
    K.cyl((bx0[0], bx0[1] + 0.25, bx0[2]), 0.25, 0.5, pm("#5a5a50", 0.5, 0.5), 14)            # petrol-tin stove
    K.cyl((bx0[0], bx0[1] + 0.62, bx0[2]), 0.14, 0.2, pm("#8a8a88", 0.3, 0.8), 16); K.cyl((bx0[0] + 0.17, bx0[1] + 0.66, bx0[2]), 0.02, 0.12, pm("#8a8a88", 0.3, 0.8), 6, "x")
    for k in range(4): K.cyl((bx0[0] - 0.9 + k * 0.25, bx0[1] + 0.06, bx0[2] - 0.6 + (k % 2) * 0.2), 0.045, 0.1, pm("#e8e0d0", 0.3), 12)
    for k in range(5): crate(K, (8.5 + (k % 3) * 0.9, H(8.5, 21) + 0.3 + (k // 3) * 0.55, 21.5 + (k % 2) * 0.3), 0.7, wood("#a88a5a", "#6a5a3a", 10, 0.8), 0.1 * k)
    text("RATIONS", (8.5, H(8.5, 21) + 0.32, 21.13), 0.1, pm("#2a1a10", 0.7), 0, "sans", 0.002)
    for k in range(30): K.box((16 + rnd.uniform(-4, 4), 3.0 + rnd.uniform(-0.2, 0.2), 25 + rnd.uniform(-4, 4)), (0.6, 0.05, 0.6), cloth(("#b89a62", "#9a8050", "#c8aa70")[k % 3]), rnd.uniform(0, 3), 0.0, rnd.uniform(-0.3, 0.3))
    sand = sandmat()
    sandbag_wall("dsb1", (4.5, H(4.5, 20), 20.5), 0.3, 6, 3, sand, 2)
    # abandoned Italian kit along the track for the prisoner shot: helmets, rifles, a broken-down lorry
    truck("fiat", (-28, H(-28, 20), 20), 0.9, "#8a8458", "#8a7a5a")
    for k in range(10):
        x, z = rnd.uniform(-24, 24), rnd.uniform(14, 18)
        K.sphere((x, H(x, z) + 0.05, z), 0.14, pm("#6a6a4a", 0.5, 0.3), 10, (1, 0.6, 1))
        K.box((x + 0.6, H(x, z) + 0.04, z + 0.3), (1.1, 0.04, 0.05), wood("#5a3a1e", "#2a1a0e", 10, 0.6), rnd.uniform(0, 3), 0.0)
    for k in range(8):                       # rocks and camel thorn
        x, z = rnd.uniform(-35, 35), rnd.uniform(-4, 32)
        if abs(z - 12) < 3: continue
        lib.blob(f"rock{k}", T(x, H(x, z), z), (rnd.uniform(0.3, 0.9), rnd.uniform(0.2, 0.5), rnd.uniform(0.3, 0.8)), pm("#a88a62", 0.9), 0.1, k)
        for j in range(7): tube(f"thorn{k}{j}", [(x + 1.2, H(x, z), z + 0.5), (x + 1.2 + rnd.uniform(-0.5, 0.5), H(x, z) + rnd.uniform(0.3, 0.7), z + 0.5 + rnd.uniform(-0.5, 0.5))], 0.015, pm("#6a5a32", 0.9), 3, 0)
    for k, (x, z) in enumerate(((-9, 4), (-8.2, 3.6), (7.5, 3.0), (8.1, 3.5), (-12, 22), (13, 6))):
        K.box((x, H(x, z) + 0.23, z), (0.18, 0.46, 0.34), mat_once("c5jerry", lambda: worn("c5jerry", "#6a6a42", "#3a3a2a", 0.6, 0.3, 20, 0.6)), 0.3 * k, 0.03)
    for k, (x, z) in enumerate(((-10.5, 5.5), (-11.3, 6.1), (9.8, 4.6))): crate(K, (x, H(x, z) + 0.25, z), 0.55, wood("#8a7a52", "#5a4a2a", 10, 0.8), 0.2 * k)
    sandbag_wall("dsb2", (-13, H(-13, 8), 8), 0.5, 7, 3, sand, 5); sandbag_wall("dsb3", (14, H(14, 9), 9), -0.4, 6, 3, sand, 6)
    K.cyl((-13.0, H(-13, 9) + 1.1, 9.4), 0.07, 2.4, pm("#3a3a32", 0.5, 0.5), 8, "z", None, 0.5, 0, -0.6)
    burnt = mat_once("c5burnt", lambda: worn("c5burnt", "#2a2420", "#6a3a1e", 0.9, 0.3, 8, 0.55, "#141010"))
    truck("wreck", (-22, H(-22, 28), 28), 2.2, "#2a2420", load=lambda K2, P, yaw: None)
    for k in range(6): lib.blob(f"wrk{k}", T(-22 + rnd.uniform(-2, 2), H(-22, 28) + 0.4, 28 + rnd.uniform(-2, 2)), (0.6, 0.3, 0.5), burnt, 0.2, k)
    K.build()
    for k, (x, z, h, ln) in enumerate(((-34, 38, 9, 0.12), (-28, 44, 11, -0.08), (-22, 36, 8, 0.15), (-38, 48, 10, 0.05), (-25, 52, 12, -0.1))):
        palm(K, x, H(x, z), z, h, ln, rnd)
    K.build()
    # ---------------- the tanks ----------------
    T0 = empty("rommeltank"); kz = Kit("rtank"); panzer("rt", (0, 0, 0), 0.0, "#b89a62", True, kz)
    for o in kz.build(): o.parent = T0
    T0.location = T(0, H(0, 9), 9); T0.rotation_euler = (0, 0, 0)
    pz = []
    for k in range(3):
        e = empty(f"pz{k}"); kk = Kit(f"pzk{k}"); panzer(f"p{k}", (0, 0, 0), 0.0, "#c0a068", k != 1, kk)
        for o in kk.build(): o.parent = e
        pz.append(e)
    dust = smoke_mat("c5dust", "#c8a878", 0.35)
    for k in range(3): smoke_column(f"dust{k}", (-6 + k * 9, H(-6 + k * 9, 44), 46), 6, 2.5, 5, dust, drift=(4, 4), seed=k, puffs=6)
    sun_light((-0.35, -0.8, -0.3), 5.5, (1.0, 0.9, 0.72), 1.0)
    area((0, 15, -20), (0, 1, 15), 1600, (0.6, 0.72, 1.0), 30)
    area((0, 2, -8), (0, 1.2, 10), 500, (1.0, 0.75, 0.5), 12)          # warm sand bounce on faces
    def hd(e, x, z, yaw, pitch=0.0):
        e.location = T(x, H(x, z), z); e.rotation_euler = (pitch, 0, yaw + math.pi / 2)
    def update(f):
        # Rommel's tank (shots 23/25): nose to the camera; it rolls in during shot 23
        u = max(0.0, min(1.0, (f - 2086) / 45)) if 2086 <= f < 2157 else 1.0
        if 2086 <= f < 2157 or 2284 <= f < 2329: hd(T0, 0, 9 + 10 * (1 - u) ** 2, 0.0)
        else: hd(T0, -40, 60, 0.0)
        for k, e in enumerate(pz):
            if 2157 <= f < 2239:
                v = max(0.0, (f - 2168 - k * 9) / 40); z = 46 - 13 * min(v, 1.4); x = -8 + k * 9
                hd(e, x, z, (k - 1) * 0.15)
            else:
                hd(e, -14 + k * 9, 52, 0.0)
    update(2086)
    return {"update": update}
