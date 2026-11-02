# December 1944, the Battle of the Bulge (chapter 11). Three areas:
#  A. The Ardennes forest (origin): deep snow, dense snowy spruce, a forest road along x 0 (z -20..120); German tanks in
#     winter whitewash burst out of the fog at (0, 0, 22) and (-4.5, 0, 40) facing the camera (-z), a halftrack behind.
#     An American foxhole line across the near side at z 2..5 (pits at x -9, -4, 5, 10, y 0 rim; GIs stand in them at
#     y -0.9). Keep clear: the road |x| < 3.5, z 6..60.
#  B. Bastogne at x 200: a snowy crossroads square x 190..210, z 0..40 (flat y 0) with stone houses, the church at
#     (214, 0, 46), the town sign "BASTOGNE" at (195.5, 0, 2) facing the camera, sandbagged positions and a jeep; the road
#     out of town runs +z (the German parley party walks in along x 200, z 60..30 under a white flag).
#  C. The HQ cellar at x -200: brick vaults x -203.5..-196.5, z 0..5.5 (back wall z 5.5), floor y 0, ceiling 2.6;
#     the general's desk at (-200, 0, 3.4) (he sits/stands behind it at z 4.2), maps on the walls, field phones.
# Light: snow (overcast dawn; cool, soft) outside, with fog cards from the staging; interior = lamps + candles.
import bpy, math, random
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, glassm
from sets import ikit as IK
from sets.void import fire, smoke_mat, smoke_column, candle, cup, mat_once
from sets.warroom import phone, typewriter

def H(x, z):
    if abs(x) < 4 or (abs(x - 200) < 40 and z < 70): return 0.0
    return 0.5 * C.nz2(x, z, 0.06, 5.0) * min(1.0, (abs(x) - 4) / 6) if x < 100 else 0.3 * C.nz2(x, z, 0.06, 6.0)

def build(M, D):
    rnd = random.Random(1216); C.SB.reset()
    sd = (0.4, 0.35, 0.8); C.sky("snow", sd, 0.8); C.sun(sd, 1.6, (1.0, 0.92, 0.82), 6.0)
    K = Kit("ardennes"); PM = C.pine_mats(True); snow = C.snow_mat()
    C.ground("ar_g", -120, 260, -40, 160, 0.9, H, snow, skip=lambda x, z: any(math.hypot(x - fx, z - 3.4) < 0.8 for fx in (-9, -4, 5, 10)) and x < 50)
    # ================= A. the forest =================
    K.box((0, 0.012, 50), (6.5, 0.02, 150), C.mat_once("ar_ruts", lambda: C._mixmat("ar_ruts", [(0.3, "#6a6058"), (0.5, "#c8ccd4"), (0.7, "#e8ecf2")], 0.4, 6, 0.6, 0.4)), 0, 0)
    for k in range(700):
        x, z = rnd.uniform(-118, 95), rnd.uniform(-38, 158)
        if abs(x) < 6 and z > -10: continue
        if abs(x) < 16 and -6 < z < 8: continue
        C.pine(K, x, H(x, z) - 0.2, z, rnd.uniform(10, 20), rnd, PM, snow=True)
    for k in range(30):
        x, z = rnd.uniform(-16, 16), rnd.uniform(-8, 10)
        if abs(x) < 4: continue
        K.sphere((x, 0, z), rnd.uniform(0.5, 1.1), snow, 10, (1.4, 0.5, 1.2))
    # German armour in winter white + a halftrack
    C.tank_at("pz1", 0, 0, 22, math.pi / 2, "#8a8a70", None, whitewash=True)
    C.tank_at("pz2", -4.5, 0, 40, math.pi / 2 - 0.15, "#8a8a70", None, whitewash=True)
    HT = dict(body=C.worn("ar_ht", "#d0d0c4", "#5a5e50", 0.7, 0.2, 5, 0.66), dark=pm("#3a3a34", 0.7), tyre=pm("#1a1a1a", 0.85), canvas=C.SB.cloth("#c8c8bc"))
    C.truck(K, 3.0, 58, math.pi / 2, HT, canvas=False)
    # American foxholes: log rims, sandbags, a .30 cal, ammo boxes, a stove can, blankets
    logm = C.bark_mat("ar_log", "#4a3a2a", "#2a2018")
    for fx in (-9, -4, 5, 10):
        K.cyl((fx, -0.8, 3.4), 0.75, 1.6, pm("#2a2420", 0.95), 16)
        for k in range(3): K.cyl((fx + rnd.uniform(-0.2, 0.2), 0.12 + k * 0.05, 2.5 - k * 0.02), 0.12, 2.0, logm, 8, "x", None, rnd.uniform(-0.2, 0.2))
        C.sandbags(K, fx, 0.0, 2.3, 0.0, 3, 1, C.sandbag_m(), rnd, 0.1)
        K.sphere((fx - 1.0, 0.1, 3.8), 0.5, snow, 10, (1.2, 0.4, 1.0))
    K.cyl((5.2, 0.55, 2.2), 0.03, 0.9, iron("#1a1a1a"), 8, "z"); K.box((5.2, 0.48, 2.7), (0.12, 0.16, 0.5), iron("#2a2a2a"), 0, 0.01)
    for k in range(4): K.box((-6.5 + k * 0.4, 0.15, 1.6), (0.3, 0.2, 0.16), C.worn("ar_ammo", "#4a5236", "#2a2a22", 0.6, 0.3, 20, 0.6), 0.3 * k, 0.01)
    K.cyl((-2.0, 0.12, 2.0), 0.1, 0.22, iron("#5a5a54"), 10); fire("ar_can", (-2.0, 0.24, 2.0), 0.12, seed=3, energy=60)
    C.fill((0, 10, -20), (0, 1, 20), 6000, (0.85, 0.9, 1.0), 30)
    # ================= B. Bastogne =================
    BX = 200.0
    K.box((BX, 0.01, 30), (14, 0.02, 120), C.mat_once("ar_ruts", lambda: None), 0, 0)
    stone = C.SB.grime("ar_stone", "#a8a090", 0.35, 3.0); slate = C.SB.stripes("ar_slate", "#3a3e46", "#30343a", 7, 2); trim = pm("#e8e2d4", 0.6)
    winw = C.SB.window_glow("arw", "#ffc070", 1.6)
    for side in (-1, 1):
        z = -10.0
        while z < 70:
            w = rnd.uniform(7, 10)
            if 20 < z < 34 and side > 0: z += 16; continue
            C.house(K, BX + side * 12, z + w / 2, w, 8, rnd.randint(2, 3), side * math.pi / 2, stone, trim, slate, winw, rnd, 3.0, shutters=pm("#4a3a2a", 0.6),
                    snow=snow, sill_snow=True, lit=0.25, base=C.concrete("ar_base", "#7a766e"), ruin=0.35 if rnd.random() < 0.2 else 0.0)
            z += w + 0.2
    K.box((BX + 16, 9, 48), (8, 18, 8), stone, 0, 0.05); K.cyl((BX + 16, 21, 48), 4.4, 6, slate, 4, "y", 0.0, math.pi / 4)
    K.cyl((BX + 16, 24.5, 48), 0.25, 2, iron(), 6)
    for s in (-1, 1): K.box((BX - 4.5 + s * 0.9, 1.1, 2), (0.1, 2.2, 0.1), iron("#2a2a2a"), 0, 0)
    sign(K, (BX - 4.5, 2.0, 1.95), 2.2, 0.5, 0.0, "BASTOGNE", board="#f2f0e8", ink=pm("#1a1a1a", 0.6), kind="sans", trim="#1a1a1a")
    sign(K, (BX - 4.5, 1.45, 1.95), 1.6, 0.3, 0.0, "LIÈGE 87", board="#f2f0e8", ink=pm("#1a1a1a", 0.6), kind="sans")
    for k, (x, z, yw) in enumerate(((BX - 5, 10, 0.2), (BX + 5, 14, -0.3), (BX + 3, 40, 0.0), (BX - 4, 44, 0.1))):
        C.sandbags(K, x, 0, z, yw, 6, 3, C.sandbag_m(), rnd, 0.06)
        K.box((x, 0.75, z + 0.05), (3.4, 0.15, 0.5), snow, yw, 0.06)
    JM = dict(body=C.worn("ar_jeep", "#5a603e", "#3a3a2a", 0.6, 0.2, 6, 0.65), tyre=pm("#1a1a1a", 0.85), seat=C.SB.cloth("#4a4a32"))
    C.jeep(K, BX + 6.5, 4, 0.5, JM)
    K.box((BX + 6.5, 1.15, 4), (2.6, 0.06, 1.3), snow, 0.5, 0.03)
    for k in range(40):
        x, z = BX + rnd.uniform(-60, 60), rnd.uniform(70, 150)
        C.pine(K, x, H(x, z), z, rnd.uniform(9, 16), rnd, PM, snow=True)
    for k in range(20):
        x, z = BX + rnd.uniform(-12, 12), rnd.uniform(-5, 60)
        if abs(x - BX) < 6: continue
        K.sphere((x, 0, z), rnd.uniform(0.3, 0.8), snow, 8, (1.4, 0.4, 1.2))
    K.box((BX + 4, 3.3, 30), (0.12, 6.6, 0.12), iron("#2a2a2a"), 0, 0); K.box((BX - 4, 3.3, 30), (0.12, 6.6, 0.12), iron("#2a2a2a"), 0, 0)
    K.box((BX, 6.4, 30), (8, 0.02, 0.02), iron("#1a1a1a"), 0, 0)
    C.fill((BX, 12, -20), (BX, 1, 20), 6000, (0.88, 0.9, 1.0), 30)
    C.fill((BX, 6, 10), (BX, 1, 30), 1500, (1.0, 0.8, 0.6), 10)
    # ================= C. the HQ cellar =================
    CX = -200.0
    brick = C.brickm("ar_cbrick", "#8a5a42", "#6a4232")
    K.box((CX, -0.05, 2.5), (7.2, 0.1, 6.2), C.concrete("ar_cfl", "#6a645a"), 0, 0)
    for s in (-1, 1): K.box((CX + s * 3.55, 1.0, 2.5), (0.2, 2.0, 6.2), brick, 0, 0)
    K.box((CX, 1.3, 5.6), (7.2, 2.6, 0.2), brick, 0, 0); K.box((CX, 1.3, -0.65), (7.2, 2.6, 0.2), brick, 0, 0)
    for k in range(16):
        a = math.pi * k / 15
        K.box((CX + 3.5 * math.cos(a), 2.0 + 0.8 * math.sin(a), 2.5), (0.5, 0.25, 6.2), brick, 0, 0.0, 0, a + math.pi / 2)
    oak = C.SB.wood("#6a4a2a", "#3a2614", 6)
    K.box((CX, 0.76, 3.4), (1.8, 0.06, 0.9), oak, 0, 0.01)
    for sx in (-0.8, 0.8):
        for sz in (-0.38, 0.38): K.box((CX + sx, 0.38, 3.4 + sz), (0.06, 0.76, 0.06), oak, 0, 0)
    phone("ar_ph", (CX + 0.65, 0.79, 3.2), 0.4); typewriter("ar_tw", (CX - 0.5, 0.79, 3.5), 0.0)
    for k in range(3):
        a = C.poster_img([(["G-2", "MESSAGE", "SITREP"][k], 0.14), (["SECRET", "101 ABN", "22 DEC"][k], 0.1, "#8a1e1e")], "#f0e8d4", "#1e1e1e", 100, 130, seed=60 + k)
        IK.floor_quad(f"ar_doc{k}", (CX + 0.0 + k * 0.25, 3.25), 0.21, 0.28, IK.img_mat(f"ar_docm{k}", a, 0.8), rnd.uniform(-0.3, 0.3), 0.792 + k * 0.001)
    candle("ar_cand", (CX - 0.8, 0.79, 3.15), 0.12, 2, 1.5)
    K.cyl((CX + 0.0, 2.25, 3.0), 0.01, 0.6, pm("#1a1a1a", 0.6), 4); K.cyl((CX, 1.95, 3.0), 0.16, 0.12, pm("#3a4a3a", 0.5, 0.4), 16, "y", 0.06)
    K.cyl((CX, 1.9, 3.0), 0.05, 0.05, em("#ffe2b0", 15), 10); C.lamp((CX, 1.8, 3.0), 45, (1.0, 0.72, 0.42), 0.05)
    mm = IK.img_mat("ar_map", bpy.data.images.load(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "maps", "c11_channel.png")), 0.7)
    IK.framed("ar_wmap", (CX, 1.55, 5.45), 2.2, 1.35, mm, oak, 0, 0.05, 0.03)
    for k in range(6): K.box((CX - 3.2, 0.2 + (k // 3) * 0.32, 1.0 + (k % 3) * 0.4), (0.4, 0.3, 0.35), C.worn("ar_ammo", "#4a5236", "#2a2a22", 0.6, 0.3, 20, 0.6), 0.1 * k, 0.01)
    K.box((CX + 3.1, 0.9, 1.4), (0.6, 0.06, 1.8), oak, 0, 0.01); K.box((CX + 3.1, 1.15, 1.4), (0.5, 0.4, 0.6), iron("#3a4a32"), 0, 0.02)
    K.box((CX + 2.8, 1.18, 1.4), (0.02, 0.1, 0.4), em("#ffb85a", 2.5), 0, 0)
    for k in range(3): K.sphere((CX + 3.35, 1.7, 0.2 + k * 0.4), 0.15, C.mat_once("ar_helm", lambda: C.worn("ar_helm", "#5a603e", "#3a3a2a", 0.5, 0.2, 10, 0.6)), 12, (1.1, 0.7, 1.1))
    C.fill((CX, 1.9, -0.3), (CX, 1.0, 3.5), 70, (1.0, 0.82, 0.6), 2.0)
    K.build()
    return {}
