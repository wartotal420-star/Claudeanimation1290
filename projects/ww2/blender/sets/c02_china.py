# China 1937 (chapter 2 shots 9-16). Three areas in one set (three coords, cameras mostly look +z):
#  A. outside the city: a dirt road along x 0 from z -30 to the gate (z 30), fields, willows, farmhouses; the Nanjing city
#     wall runs along x at z 30..36 (12 m high, battlements) with the gate (opening x -2.5..2.5, 7 m high) and a two-tier
#     gate tower on top. Keep the road (|x| < 3.2, z -20..29) clear for the column; a low rise with the general's field
#     post at (7.5, 0, 6) (map table, telephone, tent).
#  B. inside the wall: an empty street along x 0 from z 36 to 80 (|x| < 3 clear), shophouses both sides with signboards,
#     lanterns; dusk aftermath props: a single dropped shoe at (0.7, 0, 44), a suitcase, an overturned cart, papers.
#  C. the retreat road into the mountains at x 200: a road climbing from (200, 0, -5) up the valley to +z, terraces, pines,
#     mist, ridges. Keep |x - 200| < 2.5 for z -5..25 clear (soldiers march there).
# Light: D["light"] "dusk" = low orange sun behind the wall, smoke columns over the city, cool fill; otherwise day.
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached, set_world
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK
from sets.void import smoke_column, smoke_mat, tube, fire

def hip_roof(K, c, w, d, h, m, eave=0.6, up=0.35, ridge_m=None):
    """Chinese hipped roof with up-turned corners: four sloped faces + an eave fascia + ridge with end horns"""
    x, y, z = c; W2, D2 = w / 2 + eave, d / 2 + eave; r = min(w, d) * 0.12
    ring0 = [(x - W2, y + up, z - D2), (x, y, z - D2 - 0.05), (x + W2, y + up, z - D2), (x + W2 + 0.05, y, z), (x + W2, y + up, z + D2), (x, y, z + D2 + 0.05), (x - W2, y + up, z + D2), (x - W2 - 0.05, y, z)]
    top = [(x - w * 0.3, y + h, z), (x + w * 0.3, y + h, z)]
    for a, b, t in ((0, 1, 0), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 5, 1), (5, 6, 0), (6, 7, 0), (7, 0, 0)):
        K.quad([ring0[a], ring0[b], top[t]], m); K.quad([top[t], ring0[b], ring0[a]], m)
    K.quad([ring0[1], top[1], top[0]], m); K.quad([ring0[5], top[0], top[1]], m)
    K.quad([top[0], top[1], ring0[1]], m); K.quad([top[1], top[0], ring0[5]], m)
    rm = ridge_m or m
    K.box((x, y + h + 0.08, z), (w * 0.6 + 0.2, 0.18, 0.2), rm, 0, 0.02)
    for sd in (-1, 1): K.box((x + sd * (w * 0.3 + 0.12), y + h + 0.3, z), (0.15, 0.45, 0.2), rm, 0, 0.02, 0, -sd * 0.3)
    for p in ring0[::2]: K.sphere((p[0], p[1] + 0.02, p[2]), 0.12, rm, 6)

def gable_house(K, x, z, w, d, yaw, wall_m, roof_m, wood_m, rnd, h=2.6, door=True):
    xf = CK.X(x, 0, z, yaw)
    xf.box(K, (0, h / 2, 0), (w, h, d), wall_m, 0.03)
    for sd in (-1, 1):
        q = [xf.p(-w / 2 - 0.4, h - 0.05, sd * (d / 2 + 0.5)), xf.p(w / 2 + 0.4, h - 0.05, sd * (d / 2 + 0.5)), xf.p(w / 2 + 0.4, h + d * 0.42, 0), xf.p(-w / 2 - 0.4, h + d * 0.42, 0)]
        K.quad(q if sd < 0 else q[::-1], roof_m); K.quad(q[::-1] if sd < 0 else q, roof_m)
    for sd in (-1, 1): K.quad([xf.p(sd * w / 2, h, -d / 2), xf.p(sd * w / 2, h, d / 2), xf.p(sd * w / 2, h + d * 0.4, 0)], wall_m); K.quad([xf.p(sd * w / 2, h + d * 0.4, 0), xf.p(sd * w / 2, h, d / 2), xf.p(sd * w / 2, h, -d / 2)], wall_m)
    xf.box(K, (0, h + d * 0.42 + 0.05, 0), (w + 0.9, 0.12, 0.2), roof_m, 0.02)
    if door: xf.box(K, (0.0, 0.95, -d / 2 - 0.02), (0.9, 1.9, 0.06), wood_m, 0.01)
    for sd in (-1, 1): xf.box(K, (sd * w * 0.3, 1.5, -d / 2 - 0.02), (0.7, 0.6, 0.05), pm("#2a2420", 0.6), 0.01)
    return xf

LEAFD = None
def willow(K, x, z, h, leaf, bark, rnd, y=0.0):
    K.cyl((x, y + h * 0.3, z), h * 0.05, h * 0.6, bark, 8, "y", h * 0.03, roll=rnd.uniform(-0.1, 0.1))
    for k in range(5):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(0.2, h * 0.15)
        K.cyl((x + d * 0.5 * math.cos(a), y + h * 0.75, z + d * 0.5 * math.sin(a)), h * 0.012, h * 0.4, bark, 5, "y", None, 0, 0.4 * math.sin(a), -0.4 * math.cos(a))
    for k in range(16):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(0.2, h * 0.26); yy = y + h * rnd.uniform(0.55, 0.92)
        K.sphere((x + d * math.cos(a), yy, z + d * math.sin(a)), h * rnd.uniform(0.09, 0.13), leaf if k % 3 else LEAFD, 12, (1.0, 0.85, 1.0))

def build(M, D):
    random.seed(1937); KS.reset(); rnd = random.Random(1937)
    dusk = D.get("light") == "dusk"
    K = Kit("china")
    if dusk: set_world((0.12, 0.08, 0.12), (0.9, 0.42, 0.18), 0.8, (0.16, 0.1, 0.2), (1.0, 0.5, 0.22))
    else: set_world((0.3, 0.48, 0.8), (0.75, 0.82, 0.9), 1.0, (0.28, 0.46, 0.82), (0.8, 0.85, 0.9))
    BRK = KS.brick("cwall", "#7a7670", "#625e5a", "#3e3a36", 2.2, 0.5, 0.22, 0.9); BRK2 = grime("cwall2", "#6e6a64", 0.45)
    ROOF = KS.brick("croof", "#3a3c42", "#2e3036", "#1a1c20", 9, 0.12, 0.3, 0.6); RED = pm("#8a2a22", 0.55); GRN = pm("#2a5a4a", 0.5)
    DIRT = CK.ground_mat("cdirt", "#9a8460", "#6e5a3e", 0.3); FIELD = CK.ground_mat("cfield", "#6a7a3a", "#4a5a2a", 0.2)
    global LEAFD; LEAFD = pm("#4a6a2a", 0.75)
    LEAF = pm("#5a7a34", 0.7); LEAF2 = pm("#6a8a3a", 0.7); BARK = pm("#4a3a2a", 0.8); PLAST = grime("cplast", "#d8ccb0", 0.35); WD = wood("#6a4a2a", "#3a2614", 8, 0.6)
    COB = KS.wet_cobbles("ccob", "#7a7670", "#5a5650", 0.25, 3.5)
    # ======================= A. outside the wall =======================
    K.box((0, -0.05, -5), (140, 0.1, 75), FIELD, 0, 0)
    K.box((0, 0.004, 0), (7, 0.008, 62), DIRT, 0, 0)
    for k in range(60): K.box((rnd.choice((-1.6, 1.6)) + rnd.uniform(-0.15, 0.15), 0.01, rnd.uniform(-30, 29)), (0.25, 0.008, rnd.uniform(1, 3)), pm("#7a6648", 0.9), rnd.uniform(-0.05, 0.05), 0)
    for k in range(80): K.sphere((rnd.uniform(-3.4, 3.4), 0.0, rnd.uniform(-30, 29)), rnd.uniform(0.05, 0.14), DIRT, 6, (1.3, 0.4, 1.0))
    # rice / wheat fields with dykes, willows, farmhouses, haystacks, a well, carts
    for sd in (-1, 1):
        for k in range(6):
            zz = -28 + k * 9
            K.box((sd * 18, 0.12, zz), (24, 0.24, 0.5), DIRT, 0, 0.1)
            CK.grass_patch(K, 4.5 * sd if sd > 0 else -30, 30 if sd > 0 else -4.5, zz + 0.6, zz + 8.4, 160, [LEAF2, LEAF, pm("#8a9a4a", 0.7)], rnd, (0.3, 0.7))
    for k in range(14):
        sd = 1 if k % 2 else -1; willow(K, sd * rnd.uniform(4.2, 6.5), -26 + k * 3.8, rnd.uniform(5, 7.5), LEAF, BARK, rnd)
    houses = []
    for k, (x, z, yaw) in enumerate(((-9, -12, 0.1), (-12, 4, -0.15), (10, -20, 0.05), (13, 16, -0.1), (-15, 18, 0.2), (16, 0, 0.0))):
        gable_house(K, x, z, rnd.uniform(5, 7), rnd.uniform(3.5, 4.5), yaw, PLAST, ROOF, WD, rnd)
    for k in range(5): K.cyl((rnd.uniform(-14, -6) if k % 2 else rnd.uniform(6, 14), 0.9, rnd.uniform(-25, 20)), 1.0, 1.8, pm("#c8a860", 0.9), 10, "y", 0.3)
    cart = CK.X(-4.2, 0, -6, 0.3)
    cart.box(K, (0, 0.8, 0), (2.2, 0.12, 1.2), WD, 0.02)
    for sd in (-1, 1): cart.box(K, (0, 1.05, sd * 0.6), (2.2, 0.4, 0.06), WD, 0.01); cart.cyl(K, (0, 0.6, sd * 0.72), 0.6, 0.08, WD, 16, "z")
    cart.cyl(K, (1.9, 0.75, 0.3), 0.04, 1.8, WD, 6, "x"); cart.cyl(K, (1.9, 0.75, -0.3), 0.04, 1.8, WD, 6, "x")
    for k in range(9): CK.telegraph(K, 4.0, -28 + k * 7, 6.0, 0.0, R90)
    # the general's field post on a low rise (shots 10-11)
    K.sphere((8.5, -1.2, 6), 4.0, CK.ground_mat("crise", "#8a7a52", "#6a5a3a", 0.4), 16, (1.6, 0.33, 1.3))
    gx, gz, gy = 7.5, 6.0, 0.0
    K.box((gx + 1.2, 0.74, gz + 0.6), (1.4, 0.05, 0.9), WD, 0.2, 0.01)
    for dx in (-0.6, 0.6):
        for dz in (-0.35, 0.35): K.cyl((gx + 1.2 + dx, 0.37, gz + 0.6 + dz), 0.03, 0.74, WD, 6)
    CK.quad_uv("gmap", [(gx + 1.85, 0.77, gz + 0.25), (gx + 0.55, 0.77, gz + 0.25), (gx + 0.55, 0.77, gz + 0.95), (gx + 1.85, 0.77, gz + 0.95)],
               IK.img_mat("gmapi", IK.landscape_img(31, 384, 220, naive=True), 0.7))
    K.box((gx + 1.6, 0.82, gz + 0.5), (0.2, 0.1, 0.14), pm("#3a3a2a", 0.5), 0.3, 0.02)
    K.cyl((gx - 1.6, 1.4, gz + 1.6), 0.03, 2.8, WD, 6)
    tent = CK.X(gx + 2.5, 0, gz + 3.5, -0.3)
    for sd in (-1, 1):
        q = [tent.p(-1.6, 0, sd * 1.6), tent.p(1.6, 0, sd * 1.6), tent.p(1.6, 2.1, 0), tent.p(-1.6, 2.1, 0)]
        K.quad(q, cloth("#8a8458")); K.quad(q[::-1], cloth("#8a8458"))
    for k in range(4): K.box((gx - 0.8 + k * 0.5, 0.25, gz + 2.2), (0.45, 0.5, 0.35), pm("#5a5a3a", 0.6), 0.1 * k, 0.03)
    CK.sandbags(K, (gx - 0.2, 0, gz - 1.2), 0.2, 6, 2, CK.sack_mat(), rnd)
    # ======================= the wall and the gate =======================
    WZ0, WZ1, WH = 30.0, 36.0, 12.0
    for x0, x1 in ((-70, -2.5), (2.5, 70)):
        K.box(((x0 + x1) / 2, WH / 2, (WZ0 + WZ1) / 2), (x1 - x0, WH, WZ1 - WZ0), BRK, 0, 0.05)
    K.box((0, (WH + 7) / 2, (WZ0 + WZ1) / 2), (5.0, WH - 7, WZ1 - WZ0), BRK, 0, 0.05)
    K.box((0, 3.5, WZ1 - 0.5), (5.0, 7, 0.4), pm("#141210", 0.9), 0, 0)
    for k in range(17):
        a = math.pi * k / 16; K.box((2.7 * math.cos(a), 5.0 + 2.2 * math.sin(a), WZ0 - 0.05), (0.5, 0.35, 0.3), BRK2, 0, 0.02, 0, -(math.pi / 2 - a))
    for sd in (-1, 1):   # sloped plinth, buttress steps, weeds
        K.box((sd * 30, 0.6, WZ0 - 0.4), (55, 1.2, 0.8), BRK2, 0, 0.05)
        K.box((sd * 2.2, 3.4, WZ0 - 0.15), (0.6, 6.8, 0.3), BRK2, 0, 0.02)
        for sd2 in (0, 1): K.box((sd * (2.5 + 0.9 + sd2 * 0.1), 3.5, WZ0 + 0.6), (1.6, 7.0, 0.1), WD, 0.0, 0.02, 0, 0) if False else None
    for sd in (-1, 1):   # open gate leaves, iron studs
        K.box((sd * 2.3, 3.2, WZ0 + 1.4), (0.18, 6.2, 2.4), WD, sd * 0.15, 0.03)
        for j in range(5):
            for i in range(3): K.sphere((sd * 2.2, 0.9 + j * 1.1, WZ0 + 0.6 + i * 0.7), 0.05, iron(), 6)
    for k in range(94):   # battlements
        x = -70 + k * 1.5 + 0.4
        if -3.5 < x < 3.5: continue
        K.box((x, WH + 0.5, WZ0 + 0.2), (0.8, 1.0, 0.4), BRK, 0, 0.03)
    for k in range(40): K.cyl((rnd.uniform(-60, 60), 0.15, WZ0 - 0.9 + rnd.uniform(-0.3, 0.3)), 0.15, 0.3, LEAF if k % 2 else LEAF2, 5, "y", 0.25)
    # stains / repairs on the face
    for k in range(30): K.box((rnd.uniform(-60, 60), rnd.uniform(1.5, 11), WZ0 - 0.01), (rnd.uniform(1, 4), rnd.uniform(0.5, 3), 0.02), BRK2, 0, 0)
    # the gate tower: platform, red columns, lattice walls, two roofs
    tz = (WZ0 + WZ1) / 2; ty = WH
    K.box((0, ty + 0.3, tz), (16, 0.6, 6.5), BRK2, 0, 0.03)
    for i in range(6):
        for j in (-1, 1): K.cyl((-6.0 + i * 2.4, ty + 2.1, tz + j * 2.4), 0.22, 3.0, RED, 12)
    K.box((0, ty + 1.9, tz), (11.5, 2.8, 4.2), RED, 0, 0.02)
    for i in range(10):
        K.box((-5.0 + i * 1.1, ty + 2.0, tz - 2.12), (0.9, 1.6, 0.04), wood("#7a3a22", "#4a1e10", 14, 0.5), 0, 0.01)
        for j in range(5): K.box((-5.0 + i * 1.1, ty + 1.4 + j * 0.3, tz - 2.15), (0.85, 0.03, 0.02), GRN, 0, 0)
    K.box((0, ty + 3.45, tz), (13.5, 0.35, 5.6), GRN, 0, 0.02)
    hip_roof(K, (0, ty + 3.6, tz), 13.0, 5.0, 2.4, ROOF, 1.4, 0.6)
    K.box((0, ty + 4.9, tz), (9.0, 1.4, 3.2), RED, 0, 0.02)
    hip_roof(K, (0, ty + 5.6, tz), 9.5, 3.6, 2.0, ROOF, 1.1, 0.5)
    sign(K, (0, ty + 4.9, tz - 1.65), 2.2, 0.7, 0, "ZHONGHUA MEN", "#1e2a4a", gold(), "serif", gold())
    # ======================= B. inside the wall: the empty street =======================
    K.box((0, -0.03, 58), (9, 0.08, 46), lib.brickmat("cpave", "#8a8478", "#7a746a", "#4a4640", 1.2, 0.6, 0.4, 0.75), 0, 0)
    K.box((0, -0.05, 58), (140, 0.1, 46), DIRT, 0, 0)
    SH = [("CHA", "#8a1e1e"), ("MI", "#1e1e22"), ("BU", "#2a3a5a"), ("YAO", "#1e4a2a"), ("JIU", "#6a1a1a"), ("SHU", "#1e1e22"), ("DOU FU", "#4a1e2a"), ("XIE", "#1e3a3a")]
    SHOP_WALL = [grime("csw1", "#c8b898", 0.4), grime("csw2", "#a89878", 0.4), grime("csw3", "#d0c4a8", 0.4)]
    for sd in (-1, 1):
        for k in range(8):
            z = 38.5 + k * 5.0; x = sd * 6.2; w = 4.8; dpt = 6.0
            xf = CK.X(x, 0, z, -sd * R90)
            m = SHOP_WALL[(k + (sd > 0)) % 3]
            xf.box(K, (0, 3.2, 0), (w, 6.4, dpt), m, 0.03) if False else K.box((x + sd * 0.5, 3.2, z), (dpt, 6.4, w), m, 0, 0.03)
            fx_ = x - sd * 2.5   # street face x
            K.box((fx_, 1.4, z), (0.2, 2.8, w - 0.3), wood("#5a3a22", "#2e1e10", 8, 0.6), 0, 0.01)
            for j in range(6): K.box((fx_ - sd * 0.12, 1.3, z - 1.9 + j * 0.76), (0.04, 2.4, 0.66), wood("#6a4428", "#3a2414", 10, 0.6), 0, 0.01, 0, sd * 0.02 * (j % 2))
            K.box((fx_ - sd * 0.5, 3.0, z), (1.0, 0.12, w), ROOF, 0, 0.02, 0, sd * 0.25)
            for j in range(3): K.box((fx_ - sd * 0.02, 4.5, z - 1.4 + j * 1.4), (0.05, 1.1, 0.8), pm("#2a2420", 0.6), 0, 0.01)
            K.box((fx_ - sd * 0.15, 4.5, z), (0.06, 0.08, w - 0.4), WD, 0, 0.01)
            hip_roof(K, (x + sd * 0.5, 6.4, z), dpt, w, 1.5, ROOF, 0.5, 0.3) if k % 3 == 0 else None
            if k % 3 != 0:
                for s2 in (-1, 1):
                    q = [(x + sd * 0.5 + s2 * (dpt / 2 + 0.5), 6.35, z - w / 2 - 0.2), (x + sd * 0.5 + s2 * (dpt / 2 + 0.5), 6.35, z + w / 2 + 0.2), (x + sd * 0.5, 8.0, z + w / 2 + 0.2), (x + sd * 0.5, 8.0, z - w / 2 - 0.2)]
                    K.quad(q, ROOF); K.quad(q[::-1], ROOF)
            nm, col = SH[(k * 2 + (sd > 0)) % len(SH)]
            K.box((fx_ - sd * 0.8, 2.9, z + 1.6), (0.06, 1.9, 0.55), pm(col, 0.45), 0, 0.01)
            KS._frame(K, (fx_ - sd * 0.8, 2.9, z + 1.6), 0.55, 1.9, sd * R90, gold(), 0.03, 0.08)
            for s3 in (-1, 1):
                text("\n".join(nm.replace(" ", "")), (fx_ - sd * 0.8 + s3 * 0.035, 2.9, z + 1.6), 0.22, gold(), s3 * R90, "serif", 0.004)
            K.cyl((fx_ - sd * 0.8, 3.95, z + 1.6), 0.015, 0.3, iron(), 6)
            if rnd.random() < 0.7:
                lz = z - 1.2; K.cyl((fx_ - sd * 0.9, 3.5, lz), 0.22, 0.42, pm("#b8281e", 0.6), 12); K.cyl((fx_ - sd * 0.9, 3.75, lz), 0.12, 0.06, pm("#1a1a1a", 0.5), 10)
                K.cyl((fx_ - sd * 0.9, 3.25, lz), 0.12, 0.06, pm("#1a1a1a", 0.5), 10)
    # aftermath props (dusk): the dropped shoe, a suitcase, an overturned handcart, a fallen lantern, scattered papers, a hat
    SHOE = pm("#2a1e18", 0.5)
    sx_, sz_ = 0.7, 44.0
    K.box((sx_, 0.05, sz_), (0.12, 0.08, 0.26), SHOE, 0.4, 0.03); K.box((sx_ + 0.02, 0.1, sz_ - 0.06), (0.1, 0.06, 0.12), SHOE, 0.4, 0.03)
    K.box((sx_ + 0.05, 0.01, sz_ + 0.03), (0.13, 0.02, 0.28), pm("#3a2a20", 0.7), 0.4, 0.005)
    K.box((-1.2, 0.18, 48.5), (0.65, 0.36, 0.2), pm("#6a3a22", 0.5), 1.1, 0.03, 0, R90 * 0.98)
    K.cyl((-1.2, 0.4, 48.5), 0.015, 0.12, brass(), 6, "x", yaw=1.1)
    hc = CK.X(1.8, 0, 52, 0.6); hc.box(K, (0, 0.5, 0), (1.6, 0.1, 1.0), WD, 0.02, 0, 0, 1.2); hc.cyl(K, (0.3, 0.45, 0.6), 0.45, 0.06, WD, 14, "z"); hc.cyl(K, (-0.6, 0.12, -0.3), 0.04, 1.6, WD, 6, "x", yaw=0.4)
    K.cyl((-0.6, 0.2, 55.5), 0.2, 0.38, pm("#8a2018", 0.7), 12, "z", yaw=0.5); K.box((-0.6, 0.05, 56.2), (0.3, 0.02, 0.04), WD, 0.3, 0)
    for k in range(18): K.box((rnd.uniform(-2.5, 2.5), 0.005, rnd.uniform(41, 62)), (0.21, 0.003, 0.3), paper("#e8dfc8", 0.4), rnd.uniform(0, 3), 0)
    K.box((-0.5, 0.04, 46.0), (0.3, 0.06, 0.3), pm("#c8b070", 0.8), 0.2, 0.03)
    K.cyl((-0.5, 0.08, 46.0), 0.18, 0.02, pm("#c8b070", 0.8), 14)
    for k in range(12): K.box((rnd.uniform(-2.8, 2.8), 0.04, rnd.uniform(40, 70)), (rnd.uniform(0.2, 0.6), 0.08, rnd.uniform(0.05, 0.15)), WD, rnd.uniform(0, 3), 0.01)
    # ======================= C. the retreat road into the mountains (x ~ 200) =======================
    OX = 200.0
    def H(x, z):
        dx = x - OX; road = math.exp(-((dx - 1.2 * math.sin(z * 0.08)) / 4.0) ** 2)
        hill = 0.0 + 0.04 * dx * dx * 0.06 + 6 * (0.5 + 0.5 * math.sin(z * 0.05 + dx * 0.04)) * min(1.0, abs(dx) / 18)
        return max(0.0, z * 0.08) * (1 - 0.0) + hill * (1 - road)
    CK.terrain("cmount", OX - 70, OX + 70, -12, 120, 70, 66, H, CK.ground_mat("cmtn", "#6a7a44", "#4a5a30", 0.25))
    K.box((OX, 0.0, 0), (0.1, 0.1, 0.1), DIRT, 0, 0)
    for k in range(70):   # road surface strips following the valley
        z = -10 + k * 1.8; xx = OX + 1.2 * math.sin(z * 0.08); K.box((xx, H(xx, z) + 0.03, z), (4.4, 0.06, 1.9), DIRT, 0.08 * math.cos(z * 0.08), 0, -0.08)
    for k in range(260):
        x = OX + rnd.choice((-1, 1)) * rnd.uniform(5, 60); z = rnd.uniform(-8, 115)
        CK.pine(K, x, z, rnd.uniform(4, 9), pm("#2e4a2a", 0.8), BARK, H(x, z) - 0.2, rnd)
    for k in range(12):   # terraces
        z = 10 + k * 7; sd = 1 if k % 2 else -1
        for j in range(3): K.box((OX + sd * (14 + j * 4), H(OX + sd * (14 + j * 4), z) + 0.2, z), (3.6, 0.4, 6), FIELD, 0, 0.05)
    for k in range(6):   # distant ridges
        K.sphere((OX + rnd.uniform(-90, 90), -10, rnd.uniform(160, 260)), rnd.uniform(40, 70), pm("#5a6a7a" if not dusk else "#4a3a4a", 0.9), 14, (1.8, 0.8, 0.6))
    K.box((OX + 3.2, H(OX + 3.2, 6) + 0.6, 6), (0.4, 1.2, 0.4), grime("cstone", "#8a8478", 0.4), 0, 0.03)
    sign(K, (OX + 3.2, H(OX + 3.2, 6) + 1.5, 6), 1.4, 0.4, -0.4, "CHONGQING 900 LI", "#2a2a2a", pm("#e8e0c8", 0.5), "sans")
    # ======================= light =======================
    if dusk:
        sun = IK.sun((0.15, -0.18, -1.0), 2.4, (1.0, 0.5, 0.22), 2.0)
        sm_ = smoke_mat("csmoke", "#2a2422", 0.75)
        for k, (x, z) in enumerate(((-14, 48), (9, 60), (-4, 70), (18, 52), (-26, 64))):
            smoke_column(f"cs{k}", (x, 6, z), 30, 3, 9, sm_, (12, -4), k, 10)
        for k, (x, z) in enumerate(((9.5, 58), (-13, 47))): fire(f"cf{k}", (x, 6.2, z), 1.2, k, True, 2000)
        lib.light("AREA", T(0, 6, 20), 3000, (0.5, 0.6, 0.95), 20).rotation_euler = (math.radians(-50), 0, math.pi)
        lib.light("AREA", T(0, 4, 40), 900, (0.55, 0.62, 0.95), 10).rotation_euler = (math.radians(-60), 0, math.pi)
        lib.light("AREA", T(0, 11, 55), 5000, (1.0, 0.55, 0.3), 6, size_y=30)
        lib.light("AREA", T(0, 3, 36.5), 1200, (0.6, 0.66, 1.0), 5).rotation_euler = (math.radians(-80), 0, math.pi)
        for k, z in enumerate((41, 47, 53, 60, 67)): lib.light("POINT", T(-2.0 if k % 2 else 2.0, 2.5, z), 120, (1.0, 0.5, 0.25), 0.4)
        lib.light("AREA", T(OX, 8, -8), 1400, (0.6, 0.62, 0.9), 12).rotation_euler = (math.radians(-60), 0, math.pi)
    else:
        IK.sun((-0.45, -0.6, 0.65), 4.2, (1.0, 0.9, 0.74), 1.5)
    K.build()
    return {}
