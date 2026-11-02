# Chapter 6: Stalin's study in the Kremlin, June 1941. Dark wood panelling, a long green-baize conference table, Stalin's
# desk heaped with ignored warning letters (stamped WARNING), telephones, a green lamp, the big wall map of the Eastern
# Front (maps/c06_east1941.png, with the three Barbarossa arrows), portraits, tall windows onto the Kremlin towers
# (red stars) in the grey dawn, red curtains, a globe, a samovar.
# Layout (three coords): room x -7..7, z -5..8, ceiling y 4.6. The wall map on the back wall x -2.4..2.4, y 0.9..4.1
# (z 7.82); the desk x 2.6..4.6, z 3.0..4.1 (top y 0.78) with the letter pile; Stalin stands/sits behind it at
# (3.6, 0, 4.6); the conference table x -1.2..1.2, z -3.5..3.0 (top 0.76) down the middle; keep x -2..2, z 3.6..7
# clear (people at the map); windows in the left wall (x 7) at z -2 and 3.5.
import bpy, math, random, os
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, R90
from .c05_kit import (sky, area, point, spot, sun_light, lathe, tube, worn, mat_once, cached, img_mat, wall_quad, smoke_mat)
from . import ikit as I
MAPS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps")

def build(M, D):
    random.seed(1941); K_.reset(); rnd = random.Random(41)
    sky((0.25, 0.3, 0.42), (0.55, 0.5, 0.52), (0.85, 0.62, 0.45), sun_dir=(-1, 0.1, 0.2), sun_col=(1.0, 0.6, 0.3), glow=0.8)
    K = Kit("krem")
    PAN = wood("#5a3a22", "#2e1c0e", 5, 0.35); PAN2 = wood("#4a2e18", "#22140a", 6, 0.4); WAL = grime("krwall", "#d8ccb0", 0.15)
    K.box((0, -0.05, 1.5), (14.2, 0.1, 13.2), I.planks("krfloor", "#6a4428", "#3a2414", "Y", 0.14, 1.2, 0.3, 0.3), 0, 0)
    K.box((0, 4.65, 1.5), (14.2, 0.1, 13.2), grime("krceil", "#e8e0cc", 0.2), 0, 0)
    K.box((0, 2.3, 7.95), (14.2, 4.6, 0.2), WAL, 0, 0); K.box((0, 2.3, -5.0), (14.2, 4.6, 0.2), WAL, 0, 0); K.box((-7.05, 2.3, 1.5), (0.2, 4.6, 13), WAL, 0, 0)
    for z0, z1 in ((-5, -3.1), (-0.9, 2.4), (4.6, 8)): K.box((7.05, 2.3, (z0 + z1) / 2), (0.2, 4.6, z1 - z0), WAL, 0, 0)
    for zc in (-2.0, 3.5):
        K.box((7.05, 0.45, zc), (0.2, 0.9, 2.2), WAL, 0, 0); K.box((7.05, 4.15, zc), (0.2, 1.0, 2.2), WAL, 0, 0)
        for k in range(3): K.box((6.98, 0.9 + k * 1.37, zc), (0.08, 0.06, 2.2), PAN2, 0, 0.005)
        K.box((6.98, 2.27, zc), (0.08, 2.74, 0.06), PAN2, 0, 0.005)
        for sd in (-1, 1): I.drape(f"krdr{zc}{sd}", (6.8, 4.4, zc + sd * 1.25), 0.7, 4.0, I.velvet("krvel", "#7a1a18"), R90, 5, 0.07)
    # wainscot panelling with framed panels all round
    for (c, s) in (((0, 1.1, 7.82), (14, 2.2, 0.06)), ((0, 1.1, -4.88), (14, 2.2, 0.06)), ((-6.92, 1.1, 1.5), (0.06, 2.2, 13))): K.box(c, s, PAN, 0, 0.005)
    for k in range(12):
        K.box((-6.5 + k * 1.18, 1.1, 7.78), (0.95, 1.6, 0.03), PAN2, 0, 0.01)
        K.box((-6.88, 1.1, -4.0 + k * 1.05), (0.03, 1.6, 0.85), PAN2, 0, 0.01)
    K.box((0, 2.24, 7.78), (14, 0.08, 0.1), PAN2, 0, 0.01)
    # the wall map with a frame and a pull-down curtain rod
    wall_quad("krmap", (0, 2.5, 7.8), 4.8, 3.2, img_mat("c06east", os.path.join(MAPS, "c06_east1941.png"), 0.55))
    for (c, s) in (((0, 4.14, 7.76), (5.0, 0.1, 0.06)), ((0, 0.86, 7.76), (5.0, 0.1, 0.06)), ((2.45, 2.5, 7.76), (0.1, 3.38, 0.06)), ((-2.45, 2.5, 7.76), (0.1, 3.38, 0.06))):
        K.box(c, s, PAN2, 0, 0.01)
    # portraits (dark oil paintings) on the back wall either side of the map, and a clock
    for k, x in enumerate((-4.4, 4.4)):
        I.framed(f"krport{k}", (x, 3.1, 7.8), 1.0, 1.3, I.img_mat(f"krpm{k}", I.portrait_img(seed=30 + k), 0.6), K_.gold(), 0, 0.08, 0.05)
    K.cyl((-6.7, 3.3, 5.5), 0.3, 0.08, PAN2, 28, "x"); K.cyl((-6.65, 3.3, 5.5), 0.25, 0.01, pm("#efe6cc", 0.5), 28, "x")
    # the conference table (green baize), chairs, ashtrays, water carafes, papers, pencils
    K.box((0, 0.74, -0.25), (2.4, 0.06, 6.6), PAN, 0, 0.02); K.box((0, 0.775, -0.25), (2.2, 0.01, 6.4), cloth("#2e5a3a"), 0, 0.0)
    for sx in (-1, 1):
        for sz in (-1, 1): K.box((sx * 1.05, 0.37, -0.25 + sz * 3.1), (0.12, 0.74, 0.12), PAN2, 0, 0.01)
        for k in range(6):
            z = -3.0 + k * 1.1; x = sx * 1.6
            K.box((x, 0.48, z), (0.5, 0.08, 0.5), cloth("#3a2a1e"), 0, 0.03); K.box((x + sx * 0.24, 0.95, z), (0.08, 0.9, 0.5), PAN2, 0, 0.02)
            for dx in (-0.2, 0.2):
                for dz in (-0.2, 0.2): K.cyl((x + dx, 0.22, z + dz), 0.025, 0.44, PAN2, 8)
            K.box((sx * 0.7, 0.785, z), (0.3, 0.004, 0.4), paper("#efe4c8"), 0.1 * k, 0.0)
            if k % 2: K.cyl((sx * 0.5, 0.86, z + 0.3), 0.05, 0.16, glassm(), 14)
    # Stalin's desk with the pile of ignored warnings, phones, lamp, pipe, an inkstand
    K.box((3.6, 0.76, 3.55), (2.0, 0.07, 1.1), PAN, 0, 0.02)
    for sx in (-1, 1): K.box((3.6 + sx * 0.75, 0.37, 3.55), (0.48, 0.74, 1.0), PAN, 0, 0.02)
    K.box((3.6, 0.8, 3.55), (1.2, 0.01, 0.7), cloth("#2a4a32"), 0, 0.0)
    for k in range(34):
        x = 3.15 + rnd.uniform(-0.25, 0.25); z = 3.4 + rnd.uniform(-0.25, 0.25); y = 0.81 + k * 0.012
        K.box((x, y, z), (0.24, 0.008, 0.16), paper(("#efe4c8", "#e8dcc0", "#f2ead6")[k % 3]), rnd.uniform(-0.6, 0.6), 0.0)
    for k in range(6):
        x = 3.15 + rnd.uniform(-0.2, 0.2); z = 3.4 + rnd.uniform(-0.15, 0.15); y = 0.81 + 34 * 0.012 + 0.004
        text("WARNING", (x, y + k * 0.002, z), 0.035, pm("#a81e22", 0.6), rnd.uniform(-0.5, 0.5), "sans", 0.0006, pitch=-R90)
    for k in range(12):                         # letters slid off onto the floor
        K.box((2.3 + rnd.uniform(-0.6, 0.6), 0.004, 3.0 + rnd.uniform(-0.6, 0.6)), (0.24, 0.006, 0.16), paper("#efe4c8"), rnd.uniform(0, 3), 0.0)
    for k, col in enumerate(("#1a1a1c", "#e8e0d0", "#1a1a1c")):
        x = 3.9 + k * 0.28; K.box((x, 0.85, 3.85), (0.18, 0.08, 0.22), pm(col, 0.2), 0, 0.02); K.box((x, 0.92, 3.83), (0.22, 0.04, 0.05), pm(col, 0.2), 0, 0.015)
    K.cyl((4.4, 0.81, 3.3), 0.09, 0.02, brass(), 18); K.cyl((4.4, 0.97, 3.3), 0.012, 0.3, brass(), 8); K.cyl((4.4, 1.12, 3.3), 0.08, 0.28, pm("#1e5a32", 0.15), 18, "x")
    point((4.4, 1.05, 3.3), 12, (1.0, 0.72, 0.42), 0.04)
    K.box((3.6, 0.86, 3.2), (0.4, 0.08, 0.2), pm("#1a1a1a", 0.3), 0, 0.01)
    K.cyl((3.0, 0.83, 3.85), 0.03, 0.04, pm("#3a2010", 0.5), 10); K.cyl((3.08, 0.84, 3.85), 0.008, 0.14, pm("#2a1a10", 0.5), 6, "x")
    K.box((3.6, 0.5, 4.5), (0.6, 0.1, 0.6), cloth("#3a2a1e"), 0, 0.04); K.box((3.6, 1.1, 4.82), (0.62, 1.1, 0.1), PAN2, 0, 0.03)
    # side furniture: bookcases, a globe, the samovar on a side table, a sofa with a white cover, a stove with tiles
    from .void import bookcase
    bookcase("krbc1", (-6.7, 0, -2.0), 2.4, 2.6, 0.45, 5, PAN, yaw=-R90, seed=6); bookcase("krbc2", (-6.7, 0, 1.6), 2.4, 2.6, 0.45, 5, PAN, yaw=-R90, seed=7)
    lathe("krglobe", [(0.0, 0.0), (0.3, 0.0), (0.06, 0.1), (0.05, 0.7), (0.0, 0.72)], (5.8, 0, 6.5), PAN, 20)
    K.sphere((5.8, 1.1, 6.5), 0.42, pm("#5a7a8a", 0.4), 20); K.torus((5.8, 1.1, 6.5), 0.45, 0.02, brass(), 30, 6, "z", 0.4)
    K.box((-5.5, 0.4, 6.8), (1.0, 0.8, 0.6), PAN, 0, 0.02)
    lathe("samovar", [(0.0, 0.0), (0.12, 0.0), (0.08, 0.06), (0.17, 0.2), (0.18, 0.4), (0.12, 0.48), (0.05, 0.55), (0.06, 0.62), (0.0, 0.64)], (-5.5, 0.8, 6.8), brass(), 24)
    for k in range(3): K.cyl((-5.2 + k * 0.1, 0.84, 6.6), 0.035, 0.08, glassm(), 12)
    K.box((-4.0, 0.3, -4.3), (2.4, 0.6, 0.9), cloth("#e8e0cc"), 0, 0.12); K.box((-4.0, 0.8, -4.65), (2.4, 0.6, 0.25), cloth("#e8e0cc"), 0, 0.1)
    K.box((5.9, 1.6, -4.4), (1.4, 3.2, 1.0), K_.brick("krstove", "#e8e0d0", "#d8d0c0", "#9a9080", 4.0, 0.5, 0.5, 0.2), 0, 0.03)
    # outside the windows: Kremlin wall and towers with red stars in the dawn
    TW = K_.brick("krtower", "#a8423a", "#8a3a32", "#5a2a26", 2.0)
    for k, (x, z, h) in enumerate(((40, -30, 50), (45, 25, 60), (60, 70, 44))):
        K.box((x, h / 2, z), (9, h, 9), TW, 0.3, 0.1); K.cyl((x, h + 8, z), 4.8, 16, pm("#3a5a4a", 0.5, 0.3), 8, "y", 0.3)
        lathe(f"star{k}", [(0.0, -1.5), (1.6, 0.0), (0.0, 1.5)], (x, h + 18, z), em("#ff3a2a", 6.0), 5, cap=True, tilt=__import__("mathutils").Matrix.Rotation(math.radians(90), 3, "X"))
    K.box((30, 9, 20), (4, 18, 140), TW, 0, 0.1)
    for k in range(30): K.box((27.8, 18.6, -45 + k * 4.6), (0.6, 1.4, 1.8), TW, 0, 0.05)
    K.build()
    # light: grey-pink dawn through the windows (cool), the desk lamp and a ceiling lamp warm, a soft fill
    for zc in (-2.0, 3.5): area((7.6, 2.3, zc), (0, 1.0, zc), 700, (0.75, 0.8, 1.0), 2.0, 2.8)
    area((0, 4.4, 2.0), (0, 0, 2.0), 600, (1.0, 0.75, 0.5), 6)
    area((-3, 2.6, -3.5), (1, 1.2, 4.5), 260, (1.0, 0.8, 0.6), 3)
    spot((0, 4.4, 4.5), (0, 2.5, 7.8), 900, (1.0, 0.82, 0.6), 60, 0.5, 0.3)
    lathe("chand", [(0.0, 0.0), (0.4, 0.1), (0.5, 0.25), (0.3, 0.4), (0.0, 0.45)], (0, 3.6, 0.5), brass(), 20)
    sm = smoke_mat("krsmoke", "#c0b8b0", 0.1)
    for k in range(3): o = lib.blob(f"krhaze{k}", T(rnd.uniform(-3, 4), 3.9, rnd.uniform(0, 5)), (1.6, 0.2, 1.0), sm, 0.08, k); o.visible_shadow = False
    return {}
