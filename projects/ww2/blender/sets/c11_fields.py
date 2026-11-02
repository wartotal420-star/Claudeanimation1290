# Two stretches of countryside for chapter 11:
#  A. Kent, spring 1944 (origin): the FAKE ARMY (FUSAG) in a hedged field near Dover. Rubber dummy Shermans at
#     HERO (0, 0, 8) (side to the camera, update() pumps it up over ch11 frames 1512..1572 from flat), (-10, 16), (9, 18),
#     (-3, 27), (15, 30); the "lifted" dummy (four men carry it) floats at (-7.5, 1.95, 6.5); a bicycle pump + hose at
#     (-3.4, 0, 6.2). Dummy landing craft of canvas on the creek z 44..60. The radio truck with tall aerials at (10, 0, 4).
#     Keep clear (characters): x -9..8, z 1..7 and the pump spot; the field is flat (y 0) for |x| < 30, z < 40.
#     Signs: "FIRST U.S. ARMY GROUP" HQ board at (-8, 0, 1.5) facing the camera, a fingerpost DOVER 5 at (6.5, 0, 0.5).
#  B. Holland, September 1944 (x 300): flat polder with ditches, a windmill at (318, 0, 40), farms, poplar rows; the small
#     canal bridge (road along z) at (300, ~1.6, 26..34) where paratroopers stand (deck y 1.6, x 298.6..301.4);
#     the ARNHEM ROAD BRIDGE far away: a steel tied arch over the Rhine at z 230 (span x 200..400, arch top y 34) with the
#     town and its church tower beyond. Camera on the polder looks +z.
# Light: day (A, bright spring) / golden (B, late afternoon).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, glassm
from sets import ikit as IK
from sets.void import lathe, tube, worn, mat_once
from sets import front as FR

PUMP = None
def HA(x, z):
    if abs(x) < 32 and z < 42: return 0.0
    return 0.6 * C.nz2(x, z, 0.03, 2.0) * min(1.0, (abs(x) - 32 if abs(x) >= 32 else 0) / 10 + max(0, z - 42) / 10)
def build(M, D):
    global PUMP
    light = D.get("light", "day"); rnd = random.Random(44); C.SB.reset()
    kind = "golden" if light == "golden" else "day"
    sd = (0.6, 0.55, 0.6) if kind == "day" else (-0.7, 0.2, 0.7)
    C.sky(kind, sd, 0.9); C.sun(sd, 4.2 if kind == "day" else 3.6, C.SKIES[kind]["sun"], 2.0)
    K = Kit("fields"); TM = C.tree_mats("summer"); gm = C.grass_mat("fd_grass", "#4e7a2a", "#7a9a38", "#a8a050")
    # ================= A. Kent =================
    C.ground("fd_ka", -90, 90, -40, 110, 1.0, HA, gm)
    water = C.water_mat("fd_creek", "#1e3a3a", "#4a6a5a", 0.05)
    K.box((0, -0.1, 60), (220, 0.05, 30), water, 0, 0)
    K.box((0, -0.35, 45.5), (220, 0.6, 2.0), C.mud_mat("fd_mud"), 0, 0.2)
    for x0, x1, z0, z1 in ((-90, -14, 36, 38), (14, 90, 36, 38), (-34, -32, -40, 36), (32, 34, -40, 36)):
        C.hedge(K, x0, z0, x1, z1, 2.0, rnd, TM)
    for x, z in ((-24, 33), (26, 34), (-36, 10), (38, -6), (-30, -18), (44, 20)): C.leafy(K, x, HA(x, z), z, rnd.uniform(11, 15), rnd, TM)
    # farm track with ruts
    K.box((0, 0.01, -3), (180, 0.02, 3.6), C.sand_mat("fd_track", "#9a8a68", "#7a6a50"), 0, 0)
    # the dummy Shermans: a rubber skin over the US-style tank, stars kept; one is being pumped up
    rubber = mat_once("fd_rubber", lambda: lib.principled("fd_rubber", lib.hexc("#5a6236"), 0.38, 0.0))
    def dummy(n, x, z, yaw, sag=1.0):
        objs = C.tank_at(n, x, 0, z, yaw, "#58603c", "white")
        C.recolor(objs, "tank#58603c", rubber); C.recolor(objs, "tanksteel", rubber); C.recolor(objs, "tankmud", rubber)
        r = C.rig(objs, (x, 0, z)); r.scale = (1.0, 1.0, sag); return r
    PUMP = dummy("hero", 0, 8, 0.0)
    for k, (x, z, yw, sg) in enumerate(((-10, 16, 0.3, 1.0), (9, 18, -0.2, 1.0), (-3, 27, 0.1, 0.92), (15, 30, 0.5, 1.0), (-18, 28, -0.3, 0.7))): dummy(f"dm{k}", x, z, yw, sg)
    lr = dummy("lift", -7.5, 6.5, 0.15, 0.95); lr.location.z += 1.95; lr.scale = (0.78, 0.78, 0.74)
    # pump + hose, a valve, an inflation compressor, spare rolled dummies
    K.cyl((-3.4, 0.45, 6.2), 0.04, 0.9, pm("#3a4a3a", 0.4, 0.6), 10); K.box((-3.4, 0.92, 6.2), (0.36, 0.04, 0.04), pm("#2a2a2a", 0.6), 0, 0.005)
    K.box((-3.4, 0.03, 6.2), (0.3, 0.04, 0.12), pm("#3a4a3a", 0.4, 0.6), 0, 0.005)
    tube("fd_hose", [(-3.35, 0.1, 6.2), (-2.7, 0.04, 6.5), (-2.0, 0.05, 6.8), (-1.5, 0.6, 6.9)], 0.025, pm("#1e1e1e", 0.6))
    for k in range(4): K.cyl((-6 + k * 1.1, 0.25, -0.6), 0.25, 1.6, rubber, 14, "z", None, 0.2 * k)
    # crates the dummies came in (stencilled), and grass tufts + wild flowers over the field
    crm = C.SB.wood("#8a7a4e", "#5a4a2a", 10)
    for k, (x, z, yw) in enumerate(((-5.4, 4.4, 0.15), (-5.1, 3.3, -0.1), (4.4, 6.6, 0.3))):
        K.box((x, 0.35, z), (1.4, 0.7, 0.9), crm, yw, 0.02)
        text("DUMMY TANK M4\nHANDLE WITH CARE", (x - 0.46 * math.sin(yw), 0.4, z - 0.46 * math.cos(yw)), 0.09, pm("#1e1e1e", 0.7), yw, "sans", 0.001, fit=1.25)
    src = FR.grass_tuft_src(C.foliage_mat("fd_tuft", "#5a8a2a", "#3a5a1a"), 3); pts = []
    while len(pts) < 900:
        x, z = rnd.uniform(-30, 30), rnd.uniform(-6, 40)
        if abs(z + 3) < 2.0: continue
        pts.append((x, 0.0, z))
    FR.scatter(src, "fd_tf", pts, s=(0.8, 1.8), seed=4); src.location = T(0, -50, 0)
    for k in range(120):
        x, z = rnd.uniform(-30, 30), rnd.uniform(-6, 40)
        K.sphere((x, 0.12, z), 0.05, pm(rnd.choice(["#f4f0e0", "#e8c840", "#c84a6a"]), 0.6), 6)
    # dummy landing craft: scaffold-pole frames with canvas skins, moored along the creek
    pole = iron("#6a6a62"); canv = C.SB.cloth("#8a8466")
    for k in range(5):
        x = -40 + k * 18; z = 50 + (k % 2) * 4
        K.box((x, 0.5, z), (14, 1.2, 4.0), canv, 0.05 * k, 0.1)
        K.box((x - 4.5, 2.0, z), (3.0, 2.0, 2.4), canv, 0.05 * k, 0.05)
        for j in range(8): K.cyl((x - 6.5 + j * 1.85, 1.2, z - 2.0), 0.04, 2.4, pole, 6)
        K.box((x, 2.4, z - 2.0), (14, 0.06, 0.06), pole, 0.05 * k, 0)
        if k == 2: K.box((x + 4, 0.9, z), (5, 0.8, 4.2), canv, 0.05 * k, 0.1, 0, 0.12)
    # the radio truck with its aerials and a generator; tents; the HQ board; a fingerpost; jerricans; a motorbike
    TRM = dict(body=worn("fd_truck", "#5a603e", "#3a3a2a", 0.6, 0.2, 6, 0.65), dark=pm("#2a2a24", 0.6), tyre=pm("#1a1a1a", 0.85),
               canvas=C.SB.cloth("#6a6a4a"), wood=C.SB.wood("#6a5a3a", "#3a2e1a", 8))
    C.truck(K, 10, 4.5, -0.5, TRM)
    for k, h in enumerate((10, 8, 12)):
        x = 12 + k * 1.8; K.cyl((x, h / 2, 9 + k * 0.7), 0.05, h, pole, 6)
        for s in (-1, 1): K.cyl((x + s * 1.2, h * 0.4, 9 + k * 0.7), 0.008, h * 0.85, pm("#1a1a1a", 0.6), 4, "y", None, 0, 0, s * 0.28)
    K.box((13.5, 9.0, 9.7), (5.0, 0.01, 0.01), pm("#1a1a1a", 0.6), 0.3, 0)
    K.box((7.5, 0.45, 9.5), (1.2, 0.9, 0.8), worn("fd_gen", "#4a5236", "#2a2a22", 0.6, 0.3, 20, 0.6), 0.2, 0.03)
    tent = C.SB.cloth("#7a7452")
    for k in range(6):
        x, z = -24 + k * 4.2, 22 if k % 2 else 20
        K.quad([(x - 1.5, 0, z - 1.4), (x + 1.5, 0, z - 1.4), (x + 1.5, 1.6, z), (x - 1.5, 1.6, z)], tent)
        K.quad([(x + 1.5, 0, z + 1.4), (x - 1.5, 0, z + 1.4), (x - 1.5, 1.6, z), (x + 1.5, 1.6, z)], tent)
        for s in (-1, 1): K.quad([(x + s * 1.5, 0, z - 1.4), (x + s * 1.5, 0, z + 1.4), (x + s * 1.5, 1.6, z)], C.SB.cloth("#6a6446"))
    hq = C.SB.wood("#6a4a2a", "#3a2614", 6)
    for s in (-1, 1): K.box((-8 + s * 1.3, 1.1, 1.5), (0.12, 2.2, 0.12), hq, 0, 0.01)
    sign(K, (-8, 1.75, 1.45), 3.0, 0.5, 0.0, "FIRST U.S. ARMY GROUP", board="#1e3a2a", ink=pm("#f2e8c8", 0.6), kind="sans", trim="#e8c45a")
    sign(K, (-8, 1.25, 1.45), 2.2, 0.32, 0.0, "HEADQUARTERS", board="#e8dcb0", ink=pm("#1e1e1e", 0.6), kind="sans")
    K.box((6.5, 1.2, 0.5), (0.12, 2.4, 0.12), C.SB.wood("#e8e4dc", "#c8c4bc", 6), 0, 0.01)
    for k, (s, txt, yw) in enumerate(((1.95, "DOVER  5", 0.0), (1.6, "FOLKESTONE  8", math.pi), (1.25, "LONDON  71", 0.5))):
        K.box((6.5 + 0.55 * math.cos(yw), s, 0.5 - 0.55 * math.sin(yw)), (1.2, 0.24, 0.05), pm("#f0ece0", 0.6), yw, 0.01)
        text(txt, (6.5 + 0.55 * math.cos(yw) - 0.03 * math.sin(yw), s, 0.5 - 0.55 * math.sin(yw) - 0.03 * math.cos(yw)), 0.11, pm("#1e1e1e", 0.6), yw, "sans", 0.002, fit=1.1)
    for k in range(6): K.box((4.2 + (k % 3) * 0.24, 0.23 + (k // 3) * 0.46, 2.8), (0.18, 0.46, 0.34), worn("fd_jerry", "#4a5236", "#2a2a22", 0.6, 0.3, 20, 0.6), 0.1 * k, 0.03)
    for k in range(5): K.box((-12 + k * 0.7, 0.25, 4.0), (0.6, 0.5, 0.45), C.SB.wood("#7a6a42", "#4a3a22", 10), 0.2 * k, 0.02)
    # the oast house (Kent!) and a farmhouse behind the hedge
    brk = C.brickm("fd_brick", "#9a4a32", "#7a3424"); wht = pm("#f2efe6", 0.5)
    K.cyl((-46, 4.0, 62), 3.0, 8.0, brk, 24); K.cyl((-46, 10.0, 62), 3.1, 4.0, pm("#6a3a2a", 0.8), 24, "y", 0.4)
    K.cyl((-46, 12.6, 62), 0.6, 1.4, wht, 12, "y", 0.4); K.box((-46.3, 12.7, 61.6), (0.1, 0.9, 1.1), wht, 0.4, 0.01)
    C.house(K, -36, 64, 9, 6, 2, 0.1, C.plaster("fdh", "#efe6d0"), pm("#3a2a1e", 0.6), C.SB.stripes("fd_tile", "#8a4a32", "#7a3e28", 7, 2), C.SB.window_glow("fdw", "#ffc070", 1.2), rnd, 2.8, shutters=None)
    C.fill((0, 10, -20), (0, 1, 12), 9000, (1.0, 0.92, 0.8), 30)
    # ================= B. Holland =================
    BX = 300.0
    def HB(x, z): return 0.0 if z < 220 else (0.0 if z > 240 else -2.0)
    C.ground("fd_nl", BX - 160, BX + 160, -30, 330, 2.0, lambda x, z: 0.0 if z < 214 or z > 246 else -3.0, gm)
    for k in range(9):
        z = 8 + k * 22
        if abs(z - 30) < 6: continue
        K.box((BX, -0.05, z), (320, 0.04, 1.4), C.water_mat("fd_ditch", "#1a3036", "#4a6a62", 0.04), 0, 0)
    K.box((BX, -0.2, 30), (320, 0.04, 6.0), C.water_mat("fd_canal", "#1a3036", "#3a5a58", 0.04), 0, 0)
    for s in (-1, 1): K.box((BX, -0.6, 30 + s * 3.2), (320, 1.2, 0.6), C.brickm("fd_quay", "#7a4a3a", "#5a3428"), 0, 0.01)
    K.box((BX, -0.5, 230), (320, 0.04, 30), C.water_mat("fd_rhine", "#22383e", "#4a6a6a", 0.05), 0, 0)
    # the small canal bridge: a steel girder truss on brick abutments, the road on dykes
    road = C.sand_mat("fd_road", "#8a8070", "#6a6458")
    K.box((BX, 0.8, 30), (3.0, 0.2, 7.2), C.concrete("fd_deck", "#8a847a"), 0, 0.02)
    for s in (-1, 1):
        K.box((BX + s * 1.55, 1.2, 30), (0.12, 0.8, 7.2), iron("#4a5048"), 0, 0.01)
        for k in range(7): K.box((BX + s * 1.55, 1.25, 26.6 + k * 1.15), (0.08, 0.9, 0.08), iron("#4a5048"), 0, 0, 0.7 if k % 2 else -0.7)
        K.box((BX + s * 1.55, 1.68, 30), (0.14, 0.1, 7.3), iron("#4a5048"), 0, 0.01)
    for e in (-1, 1): K.box((BX, 0.2, 30 + e * 4.4), (3.6, 1.4, 1.6), C.brickm("fd_quay", "#7a4a3a", "#5a3428"), 0, 0.02)
    K.box((BX, 0.35, 12), (3.2, 0.7, 30), road, 0, 0.3); K.box((BX, 0.35, 58), (3.2, 0.7, 40), road, 0, 0.3)
    sign(K, (BX + 2.3, 1.6, 23.0), 1.6, 0.4, 0.0, "ARNHEM 11", board="#f0f0f0", ink=pm("#1e3a8a", 0.6), kind="sans", trim="#1e3a8a")
    K.box((BX + 2.3, 0.8, 23.0), (0.08, 1.6, 0.08), iron("#f0f0f0"), 0, 0)
    # windmill
    mx, mz = BX + 18, 40
    K.cyl((mx, 6, mz), 3.2, 12, C.brickm("fd_mill", "#5a4a42", "#4a3a34"), 8, "y", 2.4)
    K.cyl((mx, 12.6, mz), 2.5, 1.6, C.SB.stripes("fd_thatch", "#6a5a3a", "#5a4a2e", 9, 2), 8, "y", 1.0)
    K.box((mx, 4.2, mz - 2.8), (5.6, 0.12, 0.8), C.SB.wood("#6a4a2a", "#3a2614", 6), 0, 0.01)
    for k in range(4):
        a = k * math.pi / 2 + 0.35
        K.box((mx + 4.5 * math.cos(a), 12.8 + 4.5 * math.sin(a), mz - 3.1), (9.0, 0.25, 0.15), C.SB.wood("#5a3a22", "#2a1a0e", 6), 0, 0.01, 0, a)
        K.box((mx + 4.8 * math.cos(a) - 0.6 * math.sin(a), 12.8 + 4.8 * math.sin(a) + 0.6 * math.cos(a), mz - 3.15), (7.0, 1.2, 0.04), C.SB.cloth("#e8e0cc"), 0, 0.0, 0, a)
    K.cyl((mx, 12.8, mz - 3.0), 0.35, 0.6, iron(), 10, "z")
    for k, (x, z) in enumerate(((BX - 30, 55), (BX + 40, 80), (BX - 60, 110), (BX + 70, 140))):
        C.house(K, x, z, 9, 7, 1, rnd.uniform(-0.3, 0.3), C.brickm("fd_hb", "#8a4a36", "#6a3424"), pm("#f0ece0", 0.5), C.SB.stripes("fd_rt", "#a84a2a", "#8a3a22", 8, 2), C.SB.window_glow("fdw", "#ffc070", 1.2), rnd, 2.8, shutters=pm("#2a6a3a", 0.6))
    for k in range(70):
        z = 12 + k * 3.0; x = BX - 8 if k % 2 else BX + 8
        if abs(z - 30) < 6 or z > 210: continue
        K.cyl((x, 4, z), 0.15, 8, TM["bark"], 6); K.sphere((x, 11, z), 1.6, TM["leaf"] if k % 3 else TM["leaf2"], 10, (0.6, 2.4, 0.6))
    for k in range(40):
        x, z = rnd.uniform(BX - 150, BX + 150), rnd.uniform(60, 210)
        C.leafy(K, x, 0, z, rnd.uniform(8, 13), rnd, TM)
    # the Arnhem road bridge: approach viaducts, piers, the steel tied arch, hangers; the town beyond
    st = iron("#4e5a5a"); cc = C.concrete("fd_pier", "#9a948a")
    K.box((BX, 9.2, 230), (420, 0.8, 12), cc, 0, 0.05)
    for k in range(13):
        x = BX - 210 + k * 35
        if abs(x - BX) < 100 and abs(x - BX) > 5: continue
        K.box((x, 4.4, 230), (3.0, 9.0, 10), cc, 0, 0.05)
    for s in (-1, 1):
        K.box((BX + s * 100, 4.4, 230), (6, 9.0, 14), cc, 0, 0.05)
        for k in range(41):
            u = k / 40; x = BX - 100 + 200 * u; y = 10 + 24 * 4 * u * (1 - u)
            K.box((x, y, 230 + s * 5.5), (5.4, 1.6, 1.0), st, 0, 0.0, 0, math.atan(24 * 4 * (1 - 2 * u) / 200))
            if 0 < k < 40 and k % 2 == 0: K.box((x, (y + 10) / 2, 230 + s * 5.5), (0.25, y - 10, 0.25), st, 0, 0)
        K.box((BX, 10.2, 230 + s * 5.5), (200, 1.2, 0.8), st, 0, 0)
    for k in range(15):
        u = (k + 0.5) / 15; x = BX - 100 + 200 * u; y = 10 + 24 * 4 * u * (1 - u)
        K.box((x, y + 0.2, 230), (0.6, 0.6, 11), st, 0, 0)
    for k in range(26):
        x = BX - 150 + k * 12 + rnd.uniform(-2, 2); z = 262 + rnd.uniform(0, 20)
        C.house(K, x, z, rnd.uniform(7, 11), 8, rnd.randint(2, 4), rnd.uniform(-0.1, 0.1), C.brickm("fd_hb", "#8a4a36", "#6a3424"), pm("#f0ece0", 0.5), C.SB.stripes("fd_rt", "#a84a2a", "#8a3a22", 8, 2), C.SB.window_glow("fdw", "#ffc070", 1.2), rnd, 3.0)
    K.box((BX + 20, 20, 285), (10, 40, 10), C.brickm("fd_church", "#7a5a46", "#5a4034"), 0, 0.1)
    K.box((BX + 20, 44, 285), (7, 8, 7), C.brickm("fd_church", "#7a5a46", "#5a4034"), 0, 0.1)
    K.cyl((BX + 20, 52, 285), 3.8, 8, iron("#3a5a52"), 8, "y", 0.4)
    C.fill((BX, 12, -30), (BX, 1, 40), 12000, (1.0, 0.82, 0.6), 40)
    K.build()
    def update(f):
        if PUMP is None: return
        u = max(0.0, min(1.0, (f - 1512) / 60.0)); w = 0.06 * math.sin(f * 1.3) * (1 - u) * (u > 0)
        PUMP.scale = (1.0 + 0.04 * (1 - u), 1.0, max(0.08, 0.08 + 0.92 * u * u * (3 - 2 * u) + w)) if f >= 1490 else (1.0, 1.0, 1.0)
    return {"update": update}
