# Chapter 5: an RAF fighter airfield in Kent, summer 1940 (shot 9: the pilots scramble).
# Layout (three coords): mown grass at y 0. The dispersal hut at x 7..12, z 6..10 (veranda facing -x), deckchairs and
# the scramble bell in front of it (x 5..7); three Spitfires parked nose-up in earth blast pens at (-6, 0, 13),
# (-17, 0, 18), (3, 0, 28); a hangar at z 45..60; windsock at (-30, 0, 40); a fuel bowser at (-1, 0, 20).
# Pilots run from the hut (x 6, z 6..8) to the planes, crossing x 6 -> -5 at z 5..8; keep |z - 6.5| < 2, x -6..7 clear.
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, crate, barrel, stripes, R90
from .c05_kit import (spitfire, pose, sky, ground_mat, height_mesh, sun_light, area, point, truck, lathe, tube, worn, mat_once, cached, lattice_mast)
from .front import sandbag_wall, sandmat

def grass_mat():
    def mk():
        m = lib.principled("c5mown", hexc("#5a8a32"), 0.9); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sp.inputs[0])
        mu = n.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = 0.4; l.new(sp.outputs[1], mu.inputs[0])
        sn = n.new("ShaderNodeMath"); sn.operation = "SINE"; l.new(mu.outputs[0], sn.inputs[0])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.08; nz.inputs["Detail"].default_value = 5; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = lib.ramp(n, l, nz.outputs["Fac"], [(0.3, hexc("#3a5a22")), (0.5, hexc("#56782e")), (0.62, hexc("#7a8a3e")), (0.75, hexc("#8a8a4a"))])
        st = n.new("ShaderNodeMix"); st.data_type = "RGBA"; st.blend_type = "MULTIPLY"; st.inputs[0].default_value = 0.12; l.new(r.outputs["Color"], st.inputs[6])
        gt = n.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; l.new(sn.outputs[0], gt.inputs[0]); l.new(gt.outputs[0], st.inputs[7])
        fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 40; fn.inputs["Detail"].default_value = 8; l.new(tc.outputs["Object"], fn.inputs["Vector"])
        mm = n.new("ShaderNodeMix"); mm.data_type = "RGBA"; mm.blend_type = "MULTIPLY"; mm.inputs[0].default_value = 0.35; l.new(st.outputs[2], mm.inputs[6]); l.new(fn.outputs["Color"], mm.inputs[7])
        l.new(mm.outputs[2], b.inputs["Base Color"]); lib.bump(n, l, fn.outputs["Fac"], 0.5, 0.02)
        return m
    return cached("c5mown", mk)

def pen(K, c, yaw, mat, sbag):
    """U-shaped earth blast pen (open toward -z local)"""
    cw, sw = math.cos(yaw), math.sin(yaw); P = lambda lx, lz: (c[0] + lx * cw + lz * sw, 0, c[2] - lx * sw + lz * cw)
    for lx, lz, L, a in ((-7.5, 2, 12, 0), (7.5, 2, 12, 0), (0, 8, 15, R90)):
        x, _, z = P(lx, lz)
        K.box((x, 0.75, z), (3.2, 1.5, L), mat, yaw + a, 0.12)
        K.box((x, 1.6, z), (1.8, 0.4, L - 0.4), mat, yaw + a, 0.1)
        for j in range(int(L / 0.62)):
            for r in range(2): K.box((x + (j * 0.62 - L / 2) * math.cos(yaw + a) + 1.65 * math.sin(yaw + a) * (1 if a == 0 else 1), 0.15 + r * 0.26, z - (j * 0.62 - L / 2) * math.sin(yaw + a) + 1.65 * math.cos(yaw + a)), (0.6, 0.26, 0.36), sbag, yaw + a, 0.08)

def build(M, D):
    random.seed(1940); K_.reset(); rnd = random.Random(21)
    sky((0.16, 0.36, 0.72), (0.45, 0.62, 0.86), (0.86, 0.88, 0.9), sun_dir=(0.5, 0.55, 0.6), sun_col=(1.0, 0.85, 0.55), glow=0.5, clouds=1.0, cloud_scale=1.5)
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, 0, 0)); g = bpy.context.object; g.scale = (600, 600, 1); bpy.ops.object.transform_apply(scale=True)
    g.data.materials.append(grass_mat())
    trees = Kit("af_trees"); leaf = [pm("#2e4a22", 0.9), pm("#3a5a2a", 0.9), pm("#4a6a2e", 0.9)]
    for k in range(120):                      # hedgerow trees round the field
        a = rnd.uniform(-0.9, 2.6); d = rnd.uniform(140, 230); x, z = d * math.cos(a) * -1, d * math.sin(a) + 60
        h = rnd.uniform(9, 16); trees.cyl((x, h * 0.25, z), 0.4, h * 0.5, pm("#3a2a1e", 0.9), 6)
        for j in range(4): trees.sphere((x + rnd.uniform(-2, 2), h * (0.55 + 0.12 * j), z + rnd.uniform(-2, 2)), h * rnd.uniform(0.22, 0.32), leaf[(k + j) % 3], 10)
    trees.build()
    K = Kit("af"); earth = ground_mat("c5earth", [(0.3, "#3a4a22"), (0.5, "#5a5a32"), (0.7, "#6a5a3a")], 0.6, 6, 0.9, 1.0)
    sbag = sandmat()
    for c, yw in (((-6, 0, 13), 0.15), ((-17, 0, 18), -0.1), ((3, 0, 28), 0.05)): pen(K, c, yw, earth, sbag)
    # ---------------- dispersal hut with a veranda, deckchairs, bell, blackboard ----------------
    HW = wood("#3a4a32", "#24301e", 5, 0.8); TR = wood("#e8e0c8", "#b8b098", 5, 0.6)
    K.box((9.5, 1.4, 8), (5, 2.8, 4), HW, 0, 0.03)
    for k in range(10): K.box((6.98, 0.2 + k * 0.27, 8), (0.04, 0.04, 4.0), pm("#2a3424", 0.8), 0, 0.0)
    K.box((9.5, 3.0, 8), (5.6, 0.25, 4.8), pm("#2a2a2a", 0.85), 0, 0.03)
    K.box((6.2, 2.7, 8), (1.6, 0.08, 4.6), pm("#2a2a2a", 0.85), 0, 0.02, 0, 0.12)
    for z in (6.0, 8.0, 10.0): K.cyl((5.5, 1.35, z), 0.06, 2.7, TR, 8)
    K.box((6.95, 1.1, 7.0), (0.06, 2.1, 0.9), pm("#5a3a22", 0.7), 0, 0.01)
    for z in (8.6, 9.6): K.box((6.95, 1.6, z), (0.06, 0.8, 0.7), pm("#1a2230", 0.05), 0, 0.01)
    for z in (8.6, 9.6): K.box((6.92, 1.6, z), (0.04, 0.9, 0.05), TR, 0, 0.0)
    sign(K, (6.92, 2.45, 8.0), 2.2, 0.36, R90, "No. 92 SQUADRON - DISPERSAL", "#1e2a4a", pm("#f0e8d0", 0.6), "sans", None, 0.04)
    K.box((6.9, 1.35, 9.05), (0.04, 0.65, 0.8), pm("#1a1a1a", 0.8), 0, 0.01)                        # the state board
    for k, s in enumerate(("A  FLT   READY", "B  FLT   READY", "WIND  SW 10")):
        text(s, (6.87, 1.55 - k * 0.17, 9.05), 0.07, pm("#f0f0e8", 0.7), R90, "mono", 0.001, fit=0.72)
    K.cyl((5.6, 1.1, 5.3), 0.05, 2.2, wood("#6a4a2a", "#3a2a1a", 8, 0.7), 8)                      # the scramble bell on its post
    K.box((5.6, 2.15, 5.3), (0.5, 0.06, 0.06), wood("#6a4a2a", "#3a2a1a", 8, 0.7), 0, 0.01)
    lathe("bell", [(0.0, 0.0), (0.16, 0.0), (0.14, 0.04), (0.09, 0.2), (0.05, 0.26), (0.0, 0.27)], (5.4, 1.78, 5.3), brass(), 24)
    for k, (x, z, yw) in enumerate(((4.6, 7.2, 1.1), (4.4, 8.6, 1.6), (4.8, 10.2, 1.9), (3.8, 9.6, 1.3))):   # deckchairs (striped canvas)
        cw, sw = math.cos(yw), math.sin(yw); P = lambda lx, ly, lz: (x + lx * cw + lz * sw, ly, z - lx * sw + lz * cw)
        fr = wood("#9a7a4a", "#6a4a2a", 10, 0.6)
        for sd in (-1, 1):
            K.box(P(sd * 0.28, 0.45, 0.0), (0.04, 0.04, 1.2), fr, yw, 0.005, -0.75)
            K.box(P(sd * 0.28, 0.3, 0.35), (0.04, 0.04, 0.8), fr, yw, 0.005, 0.8)
        K.box(P(0, 0.42, 0.05), (0.52, 0.02, 1.15), stripes(f"dc{k % 2}", "#e8e0c8", ("#2a5a9a", "#c84a3a")[k % 2], 30, 0), yw, 0.0, -0.75)
    K.box((3.7, 0.4, 6.0), (0.6, 0.04, 0.6), wood("#6a4428", "#3a2414", 6, 0.4), 0, 0.01)               # table with tea things
    K.cyl((3.7, 0.2, 6.0), 0.03, 0.4, pm("#3a3a3a", 0.5, 0.5), 6)
    for k in range(3): K.cyl((3.6 + k * 0.1, 0.46, 5.95 + 0.05 * k), 0.04, 0.09, pm("#f2ece0", 0.3), 14)
    K.cyl((3.85, 0.48, 6.15), 0.08, 0.14, pm("#8a8a90", 0.3, 0.8), 16)
    for k in range(3): K.box((3.5 + k * 0.05, 0.43, 6.15), (0.16, 0.01, 0.2), paper("#f0e8d0"), 0.3 * k, 0.0)
    # bicycle, flying helmets on the chairs, a parachute pack, a gramophone on the veranda rail, a dog bowl
    K.torus((7.5, 0.35, 5.1), 0.33, 0.02, pm("#1a1a1a", 0.6), 20, 6, "x"); K.torus((7.5, 0.35, 4.1), 0.33, 0.02, pm("#1a1a1a", 0.6), 20, 6, "x")
    K.box((7.5, 0.65, 4.6), (0.04, 0.04, 1.0), pm("#1e3a2a", 0.4, 0.4), 0, 0.0, 0.3)
    K.box((4.3, 0.55, 8.6), (0.3, 0.2, 0.25), pm("#5a3a1e", 0.6), 0.4, 0.04)
    K.box((5.0, 0.15, 7.6), (0.4, 0.3, 0.35), cloth("#8a7a5a"), 0.2, 0.06)
    K.cyl((6.4, 0.9, 9.4), 0.15, 0.12, pm("#3a1a12", 0.4), 16); K.cyl((6.4, 1.1, 9.4), 0.12, 0.25, brass(), 16, "y", 0.02)
    # ---------------- hangar, bowser, trolley-acc, windsock, fire tender ----------------
    HG = mat_once("c5hangar", lambda: worn("c5hangar", "#5a5e52", "#3a3a34", 0.6, 0.4, 2, 0.7))
    K.cyl((-8, 0.0, 52), 14, 30, HG, 32, "z")
    K.box((-8, -7, 52), (30, 14, 30.4), pm("#4a4a40", 0.8), 0, 0.0)
    K.box((-8, 4.5, 36.9), (24, 9, 0.2), pm("#141414", 0.9), 0, 0.0)
    sign(K, (-8, 10.4, 36.7), 8, 1.2, 0, "92", "#5a5e52", pm("#e8e0c8", 0.7), "sans", None, 0.05)
    BRK = K_.brick("c5ctl", "#8a5a42", "#6a4232", "#4a3e36", 3.0)
    K.box((22, 3, 40), (10, 6, 7), BRK, 0, 0.05); K.box((22, 6.6, 40), (6, 1.2, 4), glassm(), 0, 0.03); K.box((22, 7.3, 40), (6.6, 0.2, 4.6), pm("#2a2a2a", 0.8), 0, 0.02)
    K.box((22, 3.1, 36.45), (9.6, 0.06, 0.12), pm("#e8e0c8", 0.6), 0, 0.0)
    def bowser(K2, P, yaw):
        K2.cyl(P(-1.4, 1.75, 0), 0.95, 3.0, mat_once("c5bow", lambda: worn("c5bow", "#4a5a3a", "#2a2a22", 0.6, 0.2, 9, 0.66)), 20, "x", None, yaw)
        for k in range(3): K2.cyl(P(-2.6 + k * 1.2, 1.75, 0), 0.98, 0.08, pm("#2a2a24", 0.6), 20, "x", None, yaw)
    truck("bowser", (-1.0, 0, 21), 2.6, "#4a5a3a", load=bowser)
    for k, (x, z) in enumerate(((-3.0, 10.5), (-14.0, 15.5))):                                        # trolley-accs with cables
        K.box((x, 0.55, z), (1.2, 0.6, 0.7), pm("#2a3a2a", 0.6, 0.3), 0.2, 0.04)
        for sd in (-1, 1): K.cyl((x + sd * 0.45, 0.2, z), 0.2, 0.1, pm("#1a1a1a", 0.85), 14, "z")
        tube(f"cable{k}", [(x, 0.7, z), (x - 1.0, 0.05, z + 0.8), (x - 2.0, 0.6, z + 2.0)], 0.03, pm("#1a1a1a", 0.6))
    K.cyl((-30, 4, 40), 0.06, 8, pm("#e8e0d0", 0.5), 8)
    lathe("sock", [(0.45, 0.0), (0.3, 2.6)], (-30, 7.6, 40), stripes("sock", "#e86a2a", "#f2ece0", 3.0, 2), 16, cap=False, tilt=__import__("mathutils").Matrix.Rotation(math.radians(80), 3, "Z"))
    for k in range(6): barrel(K, (12 + (k % 3) * 0.7, 0.45, 14 + (k // 3) * 0.7), 0.3, 0.9, pm("#3a4a3a", 0.6, 0.3), pm("#2a2a24", 0.5, 0.5))
    K.build()
    sand = sandmat()
    sandbag_wall("afsb1", (10.5, 0, 4.5), 0.0, 6, 3, sand, 4); sandbag_wall("afsb2", (13.2, 0, 7.0), R90, 5, 3, sand, 5)
    # ---------------- the Spitfires, parked nose-up on their wheels ----------------
    th = math.atan2(0.95, 5.65)
    for k, (c, yw, code) in enumerate((((-6, 0, 13.5), math.pi + 0.15, ("QJ", "F")), ((-17, 0, 18.5), math.pi - 0.1, ("QJ", "R")), ((3, 0, 28.5), math.pi + 0.05, ("QJ", "S")))):
        e = spitfire(f"psp{k}", code[0], code[1], spin=False, gear_down=True)
        pose(e, (c[0], 2.04 + 1.15 * math.sin(th), c[2]), yw, th, 0.0)
    e = spitfire("psp3", "QJ", "N", spin=False, gear_down=True); pose(e, (-2.5, 2.04 + 1.15 * math.sin(th), 9.5), math.pi + 0.5, th, 0.0)
    K2 = Kit("af2")
    for k in range(10): barrel(K2, (14 + (k % 5) * 0.65, 0.45, 20 + (k // 5) * 0.65), 0.3, 0.9, pm("#3a4a3a", 0.6, 0.3), pm("#2a2a24", 0.5, 0.5))
    for k in range(4): crate(K2, (-9 + k * 0.7, 0.25, 7.5 + (k % 2) * 0.6), 0.5, wood("#6a6040", "#4a4028", 10, 0.8), 0.2 * k)
    K2.box((-8.5, 0.5, 6.5), (1.4, 0.06, 0.8), pm("#3a3a3a", 0.5, 0.4), 0, 0.01)
    for k in range(6): K2.cyl((-9.0 + k * 0.2, 0.75, 6.5), 0.08, 0.45, pm("#c8a02a", 0.3, 0.8), 10, "z")
    for k in range(3): K2.torus((-8.5 + (k - 1) * 0.6, 0.2, 6.5 + 0.0), 0.18, 0.04, pm("#1a1a1a", 0.8), 12, 6, "x")
    K2.build()
    truck("ftender", (16, 0, 12), 1.9, "#b81e1a", load=lambda K3, P, yaw: K3.cyl(P(-1.4, 1.6, 0), 0.8, 2.8, pm("#b81e1a", 0.4), 18, "x", None, yaw))
    # ---------------- light: high summer sun, warm; cool sky fill ----------------
    sun_light((-0.45, -0.7, -0.55), 4.8, (1.0, 0.9, 0.72), 1.2)
    area((0, 20, -20), (0, 0, 10), 6000, (0.6, 0.72, 1.0), 30)
    return {}
