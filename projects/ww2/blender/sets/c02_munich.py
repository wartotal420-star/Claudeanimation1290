# Munich, the Führerbau conference room, night of 29-30 September 1938 (chapter 2 shots 31-33). Three coords, the camera
# looks +z: room x -7..7, z -4..10, ceiling 5.2. The conference table runs along x at z 4.0 (5.2 x 1.5, top 0.78) with the
# agreement, maps, ink and coffee. The four leaders stand behind it at z 5.4 (x -2.1 Chamberlain, -0.7 Daladier,
# 0.7 Hitler, 2.1 Mussolini); aides at the back (z 8.5). Fireplace with a real fire in the back wall (x 0, z 9.8), a large
# landscape over it; tall night windows on the -x wall with drapes; sofas and a side table on +x; chandeliers.
# Near side of the table (z 2.2..3.2) stays clear for close-ups.
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached, set_world
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK
from sets.void import fire, candle, inkwell, cup, lathe

def build(M, D):
    random.seed(1938); KS.reset(); rnd = random.Random(38)
    K = Kit("munich")
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.01, 0.012, 0.02, 1); bg.inputs[1].default_value = 1.0
    FL = lib.parquet("mufloor", "#7a4a28", "#4a2a14"); PAN = IK.grain("mupan", "#7a4e2a", "#3e220e", "Y", 1.0, 0.35, 0.2)
    DK = IK.grain("mudk", "#4a2a14", "#22100a", "X", 1.0, 0.35, 0.2); PL = lib.plaster("muplast", "#e8dcc0")
    GILT = lib.gilt("mugilt"); BR = brass(); MARB = lib.marble("mumarble"); VEL = IK.velvet("muvel", "#6a1a1a", 0.9)
    BAIZE = lib.cloth("mubaize", "#2a4a34"); LEATH = pm("#5a2a1a", 0.45); PAPER = paper()
    RH = 5.2
    K.box((0, -0.05, 3), (14.4, 0.1, 14.4), FL, 0, 0)
    K.box((0, 0.006, 3.5), (9, 0.012, 7), lib.carpet("murug", "#2a3a6a", "#c8a24a"), 0, 0.003)
    K.box((0, RH + 0.1, 3), (14.4, 0.2, 14.4), PL, 0, 0)
    for k in range(5): K.box((0, RH - 0.12, -2 + k * 3), (14, 0.25, 0.3), DK, 0, 0.02)
    for k in range(5): K.box((-6 + k * 3, RH - 0.12, 3), (0.3, 0.25, 14), DK, 0, 0.02)
    K.box((0, RH / 2, 10.15), (14.4, RH, 0.3), PAN, 0, 0); K.box((0, RH / 2, -4.15), (14.4, RH, 0.3), PAN, 0, 0)
    for sd in (-1, 1): K.box((sd * 7.15, RH / 2, 3), (0.3, RH, 14.4), PAN, 0, 0)
    for k in range(9):   # raised panels on the back wall
        x = -6.2 + k * 1.55
        if abs(x) < 1.8: continue
        for y in (0.7, 2.6): K.box((x, y, 9.97), (1.25, 1.2 if y < 1 else 2.2, 0.04), DK, 0, 0.02)
    K.box((0, 3.95, 9.96), (14, 0.08, 0.06), GILT, 0, 0.01); K.box((0, 4.9, 9.95), (14, 0.25, 0.1), DK, 0, 0.02)
    # fireplace + painting
    for sd in (-1, 1): K.box((sd * 1.1, 0.7, 9.75), (0.45, 1.4, 0.5), MARB, 0, 0.02)
    K.box((0, 1.55, 9.7), (2.9, 0.3, 0.65), MARB, 0, 0.02); K.box((0, 0.7, 9.98), (1.8, 1.4, 0.05), pm("#0e0a08", 0.9), 0, 0)
    K.box((0, 0.03, 9.4), (3.0, 0.06, 0.9), MARB, 0, 0.01)
    for k in range(4): K.cyl((-0.3 + k * 0.2, 0.12, 9.75), 0.07, 0.7, wood("#4a3020", "#2a1a10", 8), 8, "z", yaw=0.2 * k)
    fire("mufire", (0, 0.12, 9.72), 0.38, 9, True, 300)
    IK.framed("mupaint", (0, 3.0, 9.98), 2.6, 1.6, IK.img_mat("mupainti", IK.landscape_img(1938, 384, 240, house=True), 0.55, coat=0.3), GILT, 0, 0.12, 0.08)
    for sd in (-1, 1): candle(f"muc{sd}", (sd * 1.1, 1.7, 9.6), 0.24, 3 + sd, 0.8)
    K.box((0.6, 1.79, 9.62), (0.3, 0.18, 0.12), wood("#3a1e0e", "#1a0c06", 10), 0, 0.02)
    # -x wall: tall night windows with drapes
    for z in (0.0, 3.5, 7.0):
        K.box((-7.0, 2.6, z), (0.06, 3.2, 1.4), em("#1e2c5a", 1.2), 0, 0)
        for j in range(4): K.box((-6.95, 1.0 + j * 1.07, z), (0.06, 0.05, 1.45), PAN, 0, 0.005)
        K.box((-6.95, 2.6, z), (0.06, 3.2, 0.05), PAN, 0, 0.005)
        for sd in (-1, 1): IK.drape(f"mud{z}{sd}", (-6.8, 4.5, z + sd * 0.95), 0.7, 4.4, VEL, -R90, 4, 0.06, gather=sd * 0.8)
        K.box((-6.8, 4.55, z), (0.15, 0.3, 2.4), GILT, 0, 0.02)
        lib.light("AREA", T(-7.4, 2.6, z), 60, (0.5, 0.62, 1.0), 1.2).rotation_euler = (0, math.radians(90), 0)
    # +x: sofas, side table with decanter, a globe, a bust, the door
    for k, z in enumerate((1.0, 5.5)):
        K.box((6.3, 0.25, z), (0.9, 0.5, 2.2), LEATH, 0, 0.08); K.box((6.75, 0.7, z), (0.25, 0.7, 2.2), LEATH, 0, 0.08)
        for sd in (-1, 1): K.box((6.3, 0.55, z + sd * 1.1), (0.9, 0.35, 0.2), LEATH, 0, 0.06)
    K.box((5.6, 0.5, 3.3), (0.6, 0.04, 0.6), DK, 0, 0.01); K.cyl((5.6, 0.25, 3.3), 0.04, 0.5, DK, 8)
    K.cyl((5.6, 0.62, 3.3), 0.07, 0.2, lib.glass("mudec"), 14); K.cyl((5.5, 0.56, 3.45), 0.03, 0.08, lib.glass("mudec"), 10)
    K.cyl((6.6, 0.5, 8.6), 0.25, 1.0, MARB, 14); K.sphere((6.6, 1.3, 8.6), 0.22, MARB, 12, (0.8, 1.2, 0.7))
    K.box((7.0, 1.3, -2.5), (0.12, 2.6, 1.6), DK, 0, 0.02); K.cyl((6.9, 1.2, -2.0), 0.03, 0.15, BR, 8, "x")
    # the conference table: baize, the agreement under a pen, maps of the Sudetenland, ink, coffee, ashtrays, nameplates
    K.box((0, 0.76, 4.0), (5.2, 0.06, 1.5), DK, 0, 0.02); K.box((0, 0.795, 4.0), (5.0, 0.01, 1.3), BAIZE, 0, 0.003)
    for sx in (-1, 1):
        for sz in (-1, 1): lathe(f"mutl{sx}{sz}", [(0.0, 0.0), (0.09, 0.0), (0.06, 0.12), (0.05, 0.4), (0.08, 0.55), (0.06, 0.72), (0.0, 0.72)], (sx * 2.3, 0, 4.0 + sz * 0.55), DK, 16)
    doc = IK.img_mat("muagr", IK.doc_img(5, "AGREEMENT", 256, 340, seal=True), 0.8)
    CK.quad_uv("muagree", [(0.18, 0.802, 3.62), (-0.18, 0.802, 3.62), (-0.18, 0.802, 4.1), (0.18, 0.802, 4.1)], doc)
    mapm = CK.img_file_mat("mumap", "c02_map_1938s.jpg", 0.6)
    me_pts = [(1.4, 0.803, 3.55), (0.5, 0.803, 3.55), (0.5, 0.803, 4.25), (1.4, 0.803, 4.25)]
    # crop the map texture to central Europe
    o = CK.quad_uv("mumapq", me_pts, mapm, ((0.13, 0.67), (0.19, 0.67), (0.19, 0.82), (0.13, 0.82)))
    for k, x in enumerate((-2.1, -0.7, 0.7, 2.1)):
        K.box((x, 0.8, 4.55), (0.42, 0.006, 0.32), PAPER, rnd.uniform(-0.2, 0.2), 0)
        inkwell(f"muink{k}", (x + 0.3, 0.8, 4.4)) if k % 2 == 0 else cup(f"mucup{k}", (x + 0.3, 0.8, 4.45))
        K.cyl((x - 0.3, 0.81, 4.45), 0.07, 0.02, pm("#c8c4b8", 0.3, 0.5), 14)
    for k in range(4): K.box((-1.5 + k * 0.05, 0.81 + k * 0.012, 3.7), (0.3, 0.012, 0.42), PAPER, 0.3 * k, 0.002)
    K.cyl((0.0, 0.81, 3.5), 0.006, 0.16, pm("#141414", 0.2, 0.3), 8, "x", yaw=0.4)
    for k in range(2): K.cyl((-2.4 + k * 4.8, 0.86, 3.6), 0.05, 0.12, BR, 12)
    for k, x in enumerate((-2.1, -0.7, 0.7, 2.1)):   # chairs pushed back behind the leaders
        IK.chair(f"much{k}", x, 6.25, math.pi, DK, LEATH, 0.5, True, GILT)
    for k, x in enumerate((-1.4, 0.0, 1.4)): IK.chair(f"muchn{k}", x, 2.0, 0.0, DK, LEATH, 0.5, True, GILT)
    # chandeliers + lamps
    for x in (-3.0, 3.0):
        K.cyl((x, RH - 0.5, 4), 0.02, 1.0, GILT, 8)
        K.torus((x, RH - 1.1, 4), 0.6, 0.025, GILT, 30, 6, "y")
        for j in range(8):
            a = j / 8 * math.tau; K.cyl((x + 0.6 * math.cos(a), RH - 1.0, 4 + 0.6 * math.sin(a)), 0.018, 0.12, pm("#f2ecdc", 0.4), 8)
            K.sphere((x + 0.6 * math.cos(a), RH - 0.9, 4 + 0.6 * math.sin(a)), 0.03, em("#ffe2b0", 14.0), 6)
        lib.light("POINT", T(x, RH - 1.0, 4), 350, (1.0, 0.72, 0.45), 0.5)
    for x in (-2.6, 2.6):
        K.cyl((x, 0.83, 3.4), 0.07, 0.05, BR, 12); K.cyl((x, 1.0, 3.4), 0.012, 0.35, BR, 6)
        K.cyl((x, 1.22, 3.4), 0.16, 0.18, pm("#e8c890", 0.7), 14, "y", 0.1); lib.light("POINT", T(x, 1.18, 3.4), 30, (1.0, 0.7, 0.42), 0.06)
    lib.light("AREA", T(0, 3.2, -3.6), 380, (1.0, 0.8, 0.6), 4.0, size_y=1.5).rotation_euler = (math.radians(-70), 0, math.pi)
    K.build()
    return {}
