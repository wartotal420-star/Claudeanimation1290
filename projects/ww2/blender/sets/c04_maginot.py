# Inside a Maginot Line fort (chapter 2 shot 28, chapters 3-4 reuse it). Three coords, the camera looks +z down a vaulted
# concrete casemate: room x -3.6..3.6, z -3..14, walls to y 2.1 then a barrel vault to y 3.4. The card table at
# (0, 0, 4.2) (top 0.76): soldiers sit round it at (-1.0, 0, 4.4), (1.0, 0, 4.4), (0, 0, 5.2) and one stands at (1.9, 0, 6.2).
# Bunk beds on the -x wall (z 6..12), the gun embrasure on the +x wall at z 9 (daylight and a peaceful field outside),
# a narrow-gauge rail in the floor along x -2.4, caged lamps on the vault (warm), pipes, posters, a gramophone, wine, a
# stove with a glowing door, ammunition racks, a telephone exchange; a steel blast door at the far end (z 14).
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached, set_world
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK

def build(M, D):
    random.seed(1939); KS.reset(); rnd = random.Random(1940)
    K = Kit("maginot")
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1); bg.inputs[1].default_value = 1.0
    CON = grime("mgcon", "#a8a294", 0.35, 2.0); CON2 = grime("mgcon2", "#8a8478", 0.45, 2.0); FL = grime("mgfloor", "#6a665e", 0.4, 3.0)
    PAINT = pm("#5a6a5a", 0.5, 0.2); STEEL = CK.wm("mgsteel", "#4a5248", "#2a2e28", 0.5, 0.5, 14, 0.7); WD = IK.grain("mgwood", "#8a6a42", "#5a4024", "X", 1.0, 0.6)
    RED = pm("#8a2a22", 0.6); BR = brass()
    W2, YS, YV, Z0, Z1 = 3.6, 2.1, 3.4, -3.0, 14.0
    K.box((0, -0.05, 5.5), (8, 0.1, 18), FL, 0, 0)
    for sd in (-1, 1):
        K.box((sd * (W2 + 0.15), YS / 2, 5.5), (0.3, YS, 18), CON, 0, 0)
        K.box((sd * (W2 - 0.01), 0.5, 5.5), (0.03, 1.0, 17), PAINT, 0, 0)
        K.box((sd * (W2 - 0.02), 1.02, 5.5), (0.04, 0.05, 17), RED, 0, 0)
    n = 16
    VR = lambda am: math.atan2(-(YV - YS) * math.cos(am), W2 * math.sin(am))
    for k in range(n):   # the barrel vault in strips
        a0 = math.pi * k / n; a1 = math.pi * (k + 1) / n; am = (a0 + a1) / 2
        x = W2 * math.cos(am); y = YS + (YV - YS) * math.sin(am)
        K.box((x, y + 0.1, 5.5), (W2 * math.pi / n * 1.15, 0.2, 18), CON2, 0, 0, 0, VR(am))
    for k in range(6): K.box((0, 0.0, -1 + k * 3), (0.0, 0.0, 0.0), CON, 0, 0) if False else None
    K.box((0, YV / 2, Z0 - 0.15), (8, YV + 0.4, 0.3), CON, 0, 0)
    K.box((0, YV / 2, Z1 + 0.15), (8, YV + 0.4, 0.3), CON, 0, 0)
    for k in range(6):   # ribs
        z = -1.5 + k * 3.0
        for j in range(n):
            am = math.pi * (j + 0.5) / n; x = (W2 - 0.08) * math.cos(am); y = YS + (YV - YS - 0.08) * math.sin(am)
            K.box((x, y, z), (W2 * math.pi / n * 1.15, 0.16, 0.3), CON2, 0, 0.02, 0, VR(am))
        for sd in (-1, 1): K.box((sd * (W2 - 0.08), YS / 2, z), (0.16, YS, 0.3), CON2, 0, 0.02)
    # pipes and cables along the vault, caged lamps with warm light
    for j, (x, y, r, col) in enumerate(((-2.6, 2.6, 0.07, "#5a6a5a"), (-2.3, 2.75, 0.04, "#8a2a22"), (2.5, 2.65, 0.06, "#4a5a7a"), (2.75, 2.45, 0.03, "#2a2a2a"))):
        K.cyl((x, y, 5.5), r, 17, pm(col, 0.4, 0.4), 10, "z")
        for k in range(8): K.box((x, y + r + 0.04, -2 + k * 2.2), (0.05, 0.08, 0.04), STEEL, 0, 0)
    for z in (0.5, 4.2, 8.0, 11.5):
        K.cyl((0, 3.3, z), 0.01, 0.15, STEEL, 6)
        K.sphere((0, 3.12, z), 0.07, em("#ffd9a0", 18.0), 10)
        for a in range(4): K.box((0.08 * math.cos(a * R90), 3.12, z + 0.08 * math.sin(a * R90)), (0.01, 0.16, 0.01), STEEL, 0, 0)
        K.cyl((0, 3.22, z), 0.12, 0.04, STEEL, 12)
        lib.light("POINT", T(0, 3.0, z), 70 if z != 4.2 else 120, (1.0, 0.72, 0.42), 0.08)
    # narrow-gauge rail in the floor, a little ammunition wagon
    for sd in (-0.3, 0.3): K.box((-2.4 + sd, 0.012, 5.5), (0.05, 0.03, 17), pm("#8a8a8a", 0.3, 0.9), 0, 0)
    wg = CK.X(-2.4, 0, 1.0, R90)
    wg.box(K, (0, 0.45, 0), (1.2, 0.5, 0.7), STEEL, 0.02)
    for sd in (-1, 1):
        for xx in (-0.4, 0.4): wg.cyl(K, (xx, 0.13, sd * 0.32), 0.12, 0.05, STEEL, 12, "z")
    for k in range(6): wg.box(K, (-0.4 + (k % 3) * 0.4, 0.78, -0.15 + (k // 3) * 0.3), (0.3, 0.16, 0.22), WD, 0.01)
    # card table, stools, cards, wine, glasses, an ashtray, candle stub, the gramophone
    K.box((0, 0.74, 4.2), (1.3, 0.05, 0.9), WD, 0, 0.01)
    for dx in (-0.55, 0.55):
        for dz in (-0.35, 0.35): K.cyl((dx, 0.36, 4.2 + dz), 0.03, 0.72, WD, 6)
    K.box((0, 0.768, 4.2), (1.1, 0.004, 0.7), cloth("#2a5a3a"), 0, 0)
    for k in range(14):
        a = rnd.uniform(-0.5, 0.5); x = rnd.uniform(-0.4, 0.4); z = 4.2 + rnd.uniform(-0.25, 0.25)
        K.box((x, 0.775 + k * 0.0005, z), (0.06, 0.002, 0.09), pm("#f4f0e6", 0.5), a, 0)
        if k % 3 == 0: K.box((x, 0.777 + k * 0.0005, z), (0.025, 0.001, 0.03), pm("#b81e1e" if k % 2 else "#141414", 0.5), a, 0)
    K.box((0.0, 0.79, 4.2), (0.065, 0.03, 0.095), pm("#3a5a9a", 0.5), 0.2, 0.002)
    BOT = pm("#1e3a1e", 0.08, 0.2); WINE = pm("#5a0e14", 0.1)
    for k, (x, z) in enumerate(((0.42, 4.45), (-0.45, 3.95), (0.5, 3.9))):
        K.cyl((x, 0.9, z), 0.04, 0.24, BOT, 12); K.cyl((x, 1.07, z), 0.014, 0.1, BOT, 8)
    for k, (x, z) in enumerate(((0.25, 4.35), (-0.3, 4.4), (0.1, 4.0))): K.cyl((x, 0.82, z), 0.03, 0.09, lib.glass("mgglass"), 10); K.cyl((x, 0.8, z), 0.026, 0.04, WINE, 10)
    K.cyl((-0.2, 0.78, 3.95), 0.06, 0.02, pm("#c8c4b8", 0.3, 0.5), 12)
    for k in range(3): K.cyl((-0.2 + 0.03 * k, 0.795, 3.95), 0.004, 0.06, pm("#e8e0d0", 0.6), 6, "x", yaw=k)
    for k, (x, z) in enumerate(((-1.0, 4.4), (1.0, 4.4), (0, 5.2))): K.cyl((x, 0.24, z), 0.2, 0.48, WD, 12)
    gx, gz = 2.9, 3.0
    K.box((gx, 0.4, gz), (0.6, 0.8, 0.5), WD, 0, 0.02); K.box((gx, 0.88, gz), (0.45, 0.16, 0.42), wood("#6a3a1a", "#3a1a08", 10, 0.3), 0, 0.01)
    K.cyl((gx, 0.97, gz), 0.17, 0.01, pm("#141414", 0.2), 20)
    K.cyl((gx - 0.18, 1.2, gz + 0.12), 0.03, 0.4, BR, 8, "y", None, 0, 0, 0.6)
    K.cyl((gx - 0.38, 1.42, gz + 0.12), 0.25, 0.4, BR, 16, "x", 0.04, 0, 0, 0)
    # bunks on the -x wall with blankets, kit bags, helmets on hooks
    for k, z in enumerate((6.6, 9.0, 11.4)):
        for lv in (0.45, 1.35):
            K.box((-3.0, lv, z), (0.95, 0.08, 2.0), STEEL, 0, 0.01)
            K.box((-3.0, lv + 0.08, z), (0.85, 0.1, 1.9), cloth(["#6a6a4a", "#4a4a5a", "#7a5a3a"][k]), 0, 0.03)
            K.box((-3.0, lv + 0.16, z - 0.8), (0.6, 0.12, 0.3), cloth("#e8e0d0"), 0, 0.04)
        for dz in (-1.0, 1.0):
            for sx in (-1, 1): K.cyl((-3.0 + sx * 0.45, 0.9, z + dz), 0.025, 1.8, STEEL, 6)
        K.sphere((-3.45, 1.85, z + 0.5), 0.17, CK.wm("adrian", "#5a6a5a", "#3a4038", 0.5, 0.3, 20, 0.7), 12, (1.0, 0.7, 1.15))
        K.cyl((-2.6, 0.2, z + 0.6), 0.2, 0.4, cloth("#7a6a48"), 10, "x")
    # +x wall: the embrasure with a machine gun, daylight and a calm meadow outside; telephone exchange; posters
    ez = 9.0
    K.box((W2 + 0.15, 1.3, ez), (0.32, 0.5, 1.0), pm("#0a0a0a", 0.9), 0, 0)
    out = IK.panel("mgout", (W2 + 0.6, 1.3, ez), 1.4, 0.8, IK.img_mat("mgouti", IK.landscape_img(1940, 384, 220), 1.0, emit=2.2), -R90)
    K.box((W2 - 0.25, 1.05, ez), (0.5, 0.06, 1.2), CON2, 0, 0.02)
    K.box((W2 - 0.55, 1.18, ez), (0.7, 0.14, 0.18), STEEL, 0, 0.02); K.cyl((W2 - 0.05, 1.22, ez), 0.025, 0.6, STEEL, 8, "x")
    K.box((W2 - 0.9, 1.0, ez), (0.08, 0.5, 0.08), STEEL, 0, 0)
    lib.light("AREA", T(W2 - 0.1, 1.3, ez), 40, (0.85, 0.9, 1.0), 0.6).rotation_euler = (0, math.radians(90), 0)
    K.box((W2 - 0.12, 1.4, 6.6), (0.2, 1.0, 1.2), STEEL, 0, 0.02)
    for r in range(4):
        for c in range(6): K.cyl((W2 - 0.23, 1.15 + r * 0.17, 6.15 + c * 0.18), 0.02, 0.03, BR, 8, "x")
    K.cyl((W2 - 0.3, 1.0, 6.6), 0.06, 0.08, pm("#141414", 0.3), 10)
    for k, (z, bg, lines) in enumerate(((0.8, "#e8d8a8", [("ILS NE", 0.13), ("PASSERONT", 0.1), ("PAS!", 0.14)]), (11.8, "#2a3a6a", [("VIN", 0.18), ("ROUGE", 0.1), ("1 FR", 0.08)]),
                                       (2.2, "#c8202a", [("SILENCE", 0.14), ("L'ENNEMI", 0.08), ("ÉCOUTE", 0.08)]))):
        poster(K, (W2 - 0.03, 1.6, z), 0.6, 0.85, R90, bg, lines, "#1a1a1a" if bg != "#2a3a6a" and bg != "#c8202a" else "#f2ead6")
    sign(K, (0, 2.0, Z1 - 0.05), 2.6, 0.32, math.pi, "OUVRAGE DU HACKENBERG", "#1e2a1e", pm("#f2ead6", 0.5), "sans")
    K.box((-1.5, 1.5, -2.88), (0.5, 0.65, 0.02), paper("#f2ead6", 0.2), 0, 0)
    text("MAI\n1940", (-1.5, 1.52, -2.86), 0.12, pm("#a81e1e", 0.5), math.pi, "serif", 0.001)
    # the steel blast door at the far end, a stove with glowing door, crates of ammunition, a bicycle
    K.box((0, 1.1, Z1 - 0.06), (1.8, 2.2, 0.12), STEEL, 0, 0.02)
    for j in range(5): K.sphere((-0.7 + j * 0.35, 1.9, Z1 - 0.13), 0.025, STEEL, 6)
    K.cyl((0.6, 1.1, Z1 - 0.16), 0.08, 0.12, STEEL, 12, "z")
    K.cyl((2.6, 0.45, 12.0), 0.3, 0.9, pm("#2a2a2a", 0.4, 0.6), 16); K.box((2.32, 0.4, 12.0), (0.05, 0.22, 0.2), em("#ff6a1a", 6.0), 0, 0)
    K.cyl((2.6, 1.9, 12.0), 0.07, 2.0, pm("#2a2a2a", 0.4, 0.6), 10)
    lib.light("POINT", T(2.2, 0.45, 12.0), 30, (1.0, 0.45, 0.15), 0.1)
    for k in range(8): KS.crate(K, (1.7 + (k % 2) * 0.62, 0.25 + (k // 4) * 0.5, 10.5 + ((k // 2) % 2) * 0.62), 0.6, WD, 0.0)
    for k in range(6): K.cyl((-1.6 + k * 0.12, 0.25, -2.6), 0.04, 0.5, BR, 8)
    # warm fill from behind the camera, cool rim from the embrasure end
    lib.light("AREA", T(0, 2.4, -2.6), 260, (1.0, 0.78, 0.55), 2.5).rotation_euler = (math.radians(-80), 0, math.pi)
    K.build()
    return {}
