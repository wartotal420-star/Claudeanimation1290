# Chapter 10: the lakeside villa outside Berlin, January 1942 - shown empty and cold. Exterior: a grand stucco villa with
# a columned porch and steep roof above a snowy garden sloping to a grey frozen lake, bare trees, black iron railings.
# Interior (x 100): the dining room - a long table set with papers, pens, ashtrays and cups before fifteen empty chairs,
# panelled walls, tall windows on the lake, a dead fireplace, a chandelier. Grey winter daylight only.
# Layout (three, y up): EXTERIOR villa body x -14..14, z 20..34 (front at z 20 facing -z), porch steps at (0, 0, 18);
#   garden y 0 for z -20..18 sloping to the lake at z < -24; the camera stands in the garden (z -18..0).
#   INTERIOR room x 94..106, z -3..9 (windows on x 106), table x 98.6..101.4, z 0..8 (top y 0.78), chairs along both sides;
#   the camera enters from z -3 looking +z.
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text, cup
from sets.warroom import chair
from sets import c09_kit as K

bx, cy = K.bx, K.cy
def H(x, z):
    if x > 60: return 0.0
    return 0.1 * noise.noise(Vector((x * 0.2, z * 0.2, 0.4))) - 2.5 * K.sm(-14, -26, z)
def build(M, D):
    rnd = random.Random(1942)
    K.sky("#8a929c", "#d0d0cc", 1.0, "#7a8490", "#c8c8c4")
    K.heightfield("ground", H, -70, 60, -60, 60, 0.8, K.snow_ground("c10snow", "#7a7068"), lambda x, z: 0.5 if abs(x) < 1.6 and -20 < z < 18 else 0.0)
    bx("lake", (0, -2.4, -90), (300, 0.1, 120), lib.principled("c10ice", lib.hexc("#9aa4ac"), 0.2), 0)
    stucco = K.mat_once("c10stucco", lambda: K.add_snow(lib.plaster("c10stucco", "#d8d0bc"), 0.4))
    roof = K.mat_once("c10vroof", lambda: K.add_snow(worn("c10vroof", "#5a4038", "#3a2a24", 0.7, 0.0, 6, 0.6), 0.85))
    win = K.mat_once("c10vwin", lambda: lib.principled("c10vwin", lib.hexc("#2a3038"), 0.1, 0.2))
    bx("vbody", (0, 6, 27), (28, 12, 14), stucco, 0.03)
    K.loft2("vroof", [(14.6, -7.6), (14.6, 7.6), (-14.6, 7.6), (-14.6, -7.6)], 12.0, [(12, -1.0), (12, 1.0), (-12, 1.0), (-12, -1.0)], 17.5, K.P_of(0, 27, 0, 0), roof)
    for k in range(4): bx(f"dorm{k}", (-9 + k * 6, 14.0, 21.2), (1.6, 2.0, 1.4), stucco, 0.02)
    for fl in range(2):
        for k in range(9):
            x_ = -12 + k * 3
            if fl == 0 and abs(x_) < 2: continue
            bx(f"vw{fl}{k}", (x_, 2.8 + fl * 5, 19.97), (1.3, 2.6, 0.06), win, 0.0)
            bx(f"vwc{fl}{k}", (x_, 4.25 + fl * 5, 19.92), (1.7, 0.3, 0.12), stucco, 0.01)
    for k in range(4): cy(f"pcol{k}", (-3 + k * 2, 2.7, 17.6), 0.28, 5.4, stucco, 20)
    bx("porchroof", (0, 5.6, 18.2), (7.6, 0.5, 3.6), stucco, 0.02)
    for k in range(4): bx(f"pstep{k}", (0, 0.12 + k * 0.24, 16.0 + k * 0.4), (6.0, 0.24, 1.6 - k * 0.3), stucco, 0.01)
    bx("vdoor", (0, 1.8, 19.98), (1.8, 3.2, 0.06), wood_mat("c10vdoor", "#3a2414", "#1e120a", 6, 0.4), 0.01)
    iron = pmat("c10iron", "#1e1e1e", 0.5, 0.6)
    for sd in (-1, 1):
        for k in range(26): tube(f"rail{sd}{k}", [(sd * (4 + k * 1.0), H(sd * (4 + k), 10), 10), (sd * (4 + k * 1.0), 1.2, 10)], 0.02, iron, res=2, bres=0)
        tube(f"railt{sd}", [(sd * 4, 1.2, 10), (sd * 30, 1.2, 10)], 0.03, iron, res=2, bres=0)
    from sets.front import dead_tree
    bark = K.mat_once("c10vbark", lambda: K.add_snow(worn("c10vbark", "#2e2822", "#4a3e32", 0.9, 0.0, 3, 0.6, "#1a1612"), 0.3))
    for k, (x_, z_, h_) in enumerate(((-12, 6, 11), (13, 4, 12), (-20, -8, 10), (22, -10, 9), (-6, -14, 8), (30, 12, 13), (-30, 14, 12))):
        dead_tree(f"vt{k}", (x_, H(x_, z_), z_), h_, bark, seed=k + 3)
    for k in range(8): lathe(f"hedge{k}", [(0.0, 0.0), (0.9, 0.0), (0.8, 1.0), (0.0, 1.2)], (-14 + k * 4, 0, 14), K.mat_once("c10hedge", lambda: K.add_snow(lib.principled("c10hedge", lib.hexc("#2a3a2a"), 0.9), 0.7)), 10) if abs(-14 + k * 4) > 3 else None
    room(rnd)
    K.sun((0.3, 0.3, -1.0), 1.2, (0.92, 0.9, 0.86), 8.0)
    K.area((0, 30, -40), (0, 4, 20), 14000, (0.72, 0.78, 0.88), 60)
    return {}
def room(rnd):
    X = 100.0
    pan = wood_mat("c10pan", "#4a3022", "#2a1a10", 3, 0.5)
    bx("rfloor", (X, -0.05, 3), (13, 0.1, 13), lib.parquet("c10parq", "#6a4a30", "#4a3020"), 0)
    bx("rceil", (X, 3.85, 3), (13, 0.1, 13), lib.plaster("c10rceil", "#d8d0c0"), 0)
    for (cx, cz, w, d) in ((X - 6.1, 3, 0.2, 13), (X, 9.6, 13, 0.2), (X, -3.6, 13, 0.2)): bx(f"rw{cx}{cz}", (cx, 1.95, cz), (w, 3.9, d), lib.plaster("c10rwall", "#c8bca8"), 0)
    for sd in (-1,):
        bx("rpan", (X - 5.98, 0.6, 3), (0.06, 1.2, 12.6), pan, 0.01)
    # window wall (x 106): three tall windows on the grey lake
    for k in range(3):
        z_ = 0 + k * 3.3
        bx(f"rwin{k}", (X + 6.1, 1.9, z_), (0.05, 2.6, 1.5), lib.emit("c10lakelight", (0.78, 0.82, 0.88), 1.4), 0)
        for sd in (-1, 1): bx(f"rcur{k}{sd}", (X + 5.95, 1.95, z_ + sd * 1.05), (0.1, 3.0, 0.5), K.mat_once("c10curt", lambda: lib.cloth("c10curt", "#6a5a4a")), 0.02)
        K.area((X + 6.6, 1.9, z_), (X, 0.8, z_), 220, (0.75, 0.82, 0.95), 1.4, 2.4)
    for (z0, z1) in ((-3.5, -0.8), (0.8, 2.5), (4.1, 5.8), (7.4, 9.5)): bx(f"rwall2{z0}", (X + 6.1, 1.95, (z0 + z1) / 2), (0.2, 3.9, z1 - z0), lib.plaster("c10rwall", "#c8bca8"), 0)
    for (y0, y1) in ((0, 0.6), (3.2, 3.9)): bx(f"rwall3{y0}", (X + 6.1, (y0 + y1) / 2, 3), (0.2, y1 - y0, 13), lib.plaster("c10rwall", "#c8bca8"), 0)
    # the table, papers, pens, cups, ashtrays; empty chairs
    WD = wood_mat("c10table", "#3a2214", "#1e1008", 5, 0.3)
    bx("rtable", (X, 0.76, 4), (2.6, 0.06, 8.0), WD, 0.02)
    for sx in (-1, 1):
        for sz in (-1, 0, 1): bx(f"rtl{sx}{sz}", (X + sx * 1.1, 0.37, 4 + sz * 3.6), (0.1, 0.74, 0.1), WD, 0.01)
    bx("rcloth", (X, 0.795, 4), (1.0, 0.004, 7.4), lib.cloth("c10runner", "#e8e0d0"), 0)
    seat = K.mat_once("c10seat", lambda: lib.cloth("c10seat", "#5a2a24"))
    for k in range(7):
        z_ = 0.8 + k * 1.1
        for sd in (-1, 1):
            if not (sd < 0 and k == 0): chair(f"rch{k}{sd}", (X + sd * 1.75, 0, z_), sd * math.pi / 2 + math.pi, WD, seat)
            px = X + sd * 0.8
            bx(f"rpap{k}{sd}", (px, 0.8, z_), (0.32, 0.004, 0.42), pmat("kpaper", "#f0e6cc", 0.8), 0, rnd.uniform(-0.2, 0.2))
            if k % 2: cup(f"rcup{k}{sd}", (px + sd * 0.25, 0.79, z_ + 0.25), "#f2ece0", True)
            tube(f"rpen{k}{sd}", [(px - 0.1, 0.81, z_ - 0.25), (px + 0.08, 0.81, z_ - 0.3)], 0.006, pmat("kblack", "#141414", 0.4), res=2, bres=0)
    chair("rchh", (X, 0, 8.5), math.pi, WD, seat)
    for k in range(3): lathe(f"rash{k}", [(0.0, 0.0), (0.07, 0.0), (0.08, 0.025), (0.065, 0.025), (0.055, 0.008), (0.0, 0.008)], (X, 0.8, 1.5 + k * 2.5), lib.glass("c10ashg"), 24)
    bx("fire", (X - 5.85, 0.6, 7.0), (0.4, 1.2, 1.8), K.mat_once("c10marb", lambda: lib.marble("c10marb")), 0.02)
    bx("firein", (X - 5.65, 0.45, 7.0), (0.05, 0.7, 1.0), K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0)), 0)
    cy("chand", (X, 3.3, 4), 0.5, 0.2, pmat("c10brass", "#a88a4a", 0.3, 1.0), 20)
    for k in range(8):
        a = k / 8 * math.tau; cy(f"chc{k}", (X + 0.6 * math.cos(a), 3.15, 4 + 0.6 * math.sin(a)), 0.02, 0.12, pmat("c10wax", "#efe6d2", 0.4), 8)
    K.area((X, 3.6, 4), (X, 0, 4), 90, (0.85, 0.85, 0.9), 3)
