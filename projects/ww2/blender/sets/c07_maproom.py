# The Pacific map room (chapter 7 shots 1-6, 15-16, 50; c13_maproom reuses it with its own pins), three.js layout:
#   room x -6..6, z -6..5.5 (back wall z 5.5, window wall x 6), floor y 0.
#   map table centred (0, 1.2), 4.4 x 2.4, top y 0.95; the Pacific map (maps/c07_pacific.png, lon 92..250 E,
#   lat 56..-22) lies on it at x +2.0 (west) .. -2.0 (east), z 0.215 (south) .. 2.185 (north), y 0.952:
#   mx(lon) = 2 - (lon - 92) / 158 * 4,  mz(lat) = 0.215 + (lat + 22) / 78 * 1.97   (Japan ~ (0.78, 1.64), Hawaii ~ (-0.81, 1.31))
#   Characters stand behind the table at z ~2.8 (general at x ~0.9, the US official at the valve x ~ -0.5), or at its
#   front edge z ~ -0.4. Keep clear: table top above the map (only low props, < 0.25 m, sit on it).
#   Oil pipeline (brass) along lat ~36 from San Francisco to Tokyo with the valve wheel at (VX, 1.08, VZ); the oil gauge
#   stands on the map at (GX, 0.95, GZ) facing -z. update(f): valve turns, needle drops, flags pop up (cfg).
import bpy, math, random, os
from mathutils import Vector, Matrix
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, flat_text, sign, poster, books, paper, brass
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj, map_mat, map_plane, cup, toy_ship, magnifier, dividers, inkwell
from sets import c07_kit as CK
from sets import ikit

def mx(lon): return 2.0 - (lon - 92.0) / 158.0 * 4.0
def mz(lat): return 0.215 + (lat + 22.0) / 78.0 * 1.97
TOP = 0.952
VX, VZ = mx(186), mz(35.5)
GX, GZ = mx(146), mz(46)
CHINA = [(121.5, 31.2), (116.4, 39.9), (118.8, 32.1), (125.5, 44.0), (113.3, 23.1), (123.4, 41.8), (112.9, 28.2)]
CONQ7 = [(166.6, 19.3, 1852), (144.8, 13.4, 1866), (104.0, 15.0, 1884), (114.2, 22.3, 1945), (121.0, 14.6, 1969), (125.0, 8.0, 1976),
         (102.0, 4.0, 1991), (103.8, 1.35, 2000), (114.0, 0.5, 2017), (110.0, -7.3, 2027), (101.5, -0.5, 2037), (143.0, -5.0, 2050), (96.5, 20.0, 2058)]

def pin(K, name, lon, lat, m, h=0.13, w=0.075):
    """a map pin flag: steel pin + a small cloth flag (own object so update() can pop it up); returns the object"""
    x, z = mx(lon), mz(lat)
    me = mesh_obj(f"{name}p", [(x - 0.003, TOP, z), (x + 0.003, TOP, z), (x + 0.003, TOP + h, z), (x - 0.003, TOP + h, z)], [(0, 1, 2, 3)], pmat("kpin", "#d8d0c0", 0.2, 1.0))
    fv = []; NX = 6
    for j in range(2):
        for i in range(NX + 1):
            u = i / NX; fv.append((x - u * w, TOP + h - 0.002 - j * w * 0.66, z + 0.006 * math.sin(u * 6)))
    fo = mesh_obj(f"{name}f", fv, [(i, i + 1, NX + 2 + i, NX + 1 + i) for i in range(NX)], m)
    uv = fo.data.uv_layers.new()
    for p in fo.data.polygons:
        for li in p.loop_indices:
            vi = fo.data.loops[li].vertex_index; uv.data[li].uv = ((vi % (NX + 1)) / NX, 1 - (vi // (NX + 1)))
    for ob in (me, fo):
        ob.data.transform(Matrix.Translation(-T(x, TOP, z))); ob.location = T(x, TOP, z)
    return [me, fo]

def build_room(M, D, cfg):
    rnd = random.Random(1941)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.05, 0.05, 0.06, 1); bg.inputs[1].default_value = 0.2
    K = Kit("room")
    floor = wood("#6a4428", "#3a2414", 4.0, 0.45); panel_w = wood("#5a3a22", "#2e1c10", 6.0, 0.4)
    wallm = mat_once("mrwall", lambda: lib.plaster("mrwall", "#c8b48a"))
    K.box((0, -0.05, 0), (12.4, 0.1, 12), floor, 0.0, 0.0)
    for k in range(24): K.box((-6 + k * 0.5 + 0.25, 0.002, 0), (0.008, 0.004, 12), pm("#2a1a10", 0.6), 0.0, 0.0)
    K.box((0, 2.0, 5.55), (12.4, 4.0, 0.1), wallm, 0.0, 0.0); K.box((6.05, 2.0, 0), (0.1, 4.0, 12), wallm, 0.0, 0.0); K.box((-6.05, 2.0, 0), (0.1, 4.0, 12), wallm, 0.0, 0.0)
    K.box((0, 0.55, 5.45), (12.2, 1.1, 0.12), panel_w, 0.0, 0.01)
    for sx in (-6.0, 6.0): K.box((sx - math.copysign(0.06, sx), 0.55, 0), (0.12, 1.1, 12), panel_w, 0.0, 0.01)
    K.box((0, 1.12, 5.38), (12.2, 0.06, 0.06), panel_w, 0.0, 0.005); K.box((0, 3.95, 5.4), (12.2, 0.12, 0.2), panel_w, 0.0, 0.01)
    K.box((0, 4.05, 0), (12.4, 0.1, 12), pm("#d8ccb0", 0.9), 0.0, 0.0)
    for k in range(5): K.box((0, 3.9, -4.5 + k * 2.4), (12.2, 0.25, 0.25), panel_w, 0.0, 0.01)
    # ---- the map table: thick top, apron, turned legs, brass corner guards ----
    K.box((0, 0.92, 1.2), (4.4, 0.06, 2.4), floor, 0.0, 0.01); K.box((0, 0.84, 1.2), (4.2, 0.12, 2.2), panel_w, 0.0, 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1):
            K.cyl((sx * 2.0, 0.42, 1.2 + sz * 1.0), 0.08, 0.84, panel_w, 12); K.cyl((sx * 2.0, 0.2, 1.2 + sz * 1.0), 0.11, 0.12, panel_w, 12)
            K.box((sx * 2.18, 0.955, 1.2 + sz * 1.18), (0.08, 0.012, 0.08), brass(), 0.0, 0.0)
    mm = mat_once("pacmap", lambda: map_mat("pacmap", "c07_pacific.png", 0.55))
    map_plane("pmap", -2.0, 2.0, 0.215, 2.185, TOP, mm)
    # ---- desk clutter on the table rim (outside the map) ----
    cup("mcup", (2.1, 0.95, 0.1)); cup("mcup2", (-2.05, 0.95, 2.3), "#e8e0d0")
    magnifier("mmag", (1.8, 0.95, 2.28), 0.4); dividers("mdiv", (-1.7, 0.95, 0.08), 2.8); inkwell("mink", (-2.12, 0.95, 0.45))
    for k in range(3): K.box((1.4 + k * 0.03, 0.952 + k * 0.004, 0.12), (0.22, 0.003, 0.3), paper("#efe4c8", 0.3), 0.1 * k, 0.0)
    for k in range(5): K.cyl((-0.6 + k * 0.035, 0.957, 0.05), 0.005, 0.18, pm(["#c8302a", "#2a4a8a", "#e8c040", "#2a2a2a", "#3a7a3a"][k], 0.5), 8, "z")
    K.cyl((0.7, 0.96, 0.06), 0.06, 0.015, pm("#c8c0b0", 0.2, 0.6), 18)                                   # ashtray
    tube("cig", [(0.7, 0.975, 0.06), (0.76, 0.98, 0.04)], 0.004, pmat("kcig", "#f2ece0", 0.8), res=2, bres=0)
    # ---- back wall: clocks TOKYO / WASHINGTON, blackboard, wall map, filing cabinets, teleprinter, coat stand ----
    clockface = ikit.canvas(256, 256, "#f2ead6")
    for k in range(12):
        a = k / 12 * math.tau; ikit.ellipse(clockface, 0.5 + 0.38 * math.sin(a), 0.5 - 0.38 * math.cos(a), 0.03, 0.03, "#1a1a1a")
    ikit.ellipse(clockface, 0.5, 0.5, 0.48, 0.48, "#2a2a2a", ring=0.06)
    cm = ikit.img_mat("mclockf", clockface, 0.3)
    for k, (x, lab, hr) in enumerate(((-3.2, "TOKYO", 3.0), (-1.8, "WASHINGTON", 1.0))):
        ikit.panel(f"clk{k}", (x, 3.1, 5.44), 0.6, 0.6, cm, 0.0)
        K.cyl((x, 3.1, 5.48), 0.33, 0.06, brass(), 28, "z")
        for j, (L, a) in enumerate(((0.16, hr / 12 * math.tau), (0.24, 0.5))):
            K.box((x - math.sin(a) * L / 2, 3.1 + math.cos(a) * L / 2, 5.43), (0.018, L, 0.01), pm("#141414", 0.4), 0.0, 0.0, 0.0, a)
        sign(K, (x, 2.62, 5.46), 1.1, 0.2, 0.0, lab, board="#2a1e14", ink=brass(), kind="sans")
    K.box((1.8, 2.3, 5.47), (2.6, 1.5, 0.05), pm("#1e2a24", 0.9), 0.0, 0.0)
    for k, (dx, dy, ln) in enumerate(((-0.9, 0.5, 1.2), (-0.9, 0.25, 0.9), (-0.9, 0.0, 1.5), (-0.9, -0.25, 1.0))):
        K.box((1.8 + dx + ln / 2 - 0.0, 2.3 + dy, 5.44), (ln, 0.02, 0.005), pm("#d8d4c8", 0.9), 0.0, 0.0)
    ktext("OIL RESERVES:\n18 MONTHS", (1.8, 2.25, 5.43), 0.2, pm("#e8e4d8", 0.9), 0.0, "sans", 0.002)
    K.box((1.8, 1.52, 5.42), (2.7, 0.06, 0.12), panel_w, 0.0, 0.0)
    for k in range(3):
        x = 4.0 + k * 0.62
        K.box((x, 0.7, 5.1), (0.58, 1.4, 0.6), pm("#5a6250", 0.45, 0.3), 0.0, 0.01)
        for j in range(3): K.box((x, 0.3 + j * 0.45, 4.79), (0.5, 0.36, 0.02), pm("#6a7260", 0.45, 0.3), 0.0, 0.0); K.box((x, 0.42 + j * 0.45, 4.77), (0.14, 0.03, 0.03), brass(), 0.0, 0.0)
    for k in range(6): K.box((4.0 + (k % 3) * 0.62 + rnd.uniform(-0.1, 0.1), 1.42 + (k // 3) * 0.05, 5.1), (0.32, 0.04, 0.42), paper("#efe4c8", 0.3), rnd.uniform(-0.3, 0.3), 0.0)
    K.box((-4.5, 0.5, 5.0), (1.2, 1.0, 0.7), panel_w, 0.0, 0.01); K.box((-4.5, 1.15, 5.0), (0.8, 0.3, 0.5), pm("#2a2a2a", 0.4, 0.5), 0.0, 0.01)
    K.box((-4.5, 1.32, 4.85), (0.5, 0.004, 0.25), paper("#f2ead0", 0.2), 0.0, 0.0, 0.0)
    for k in range(8): K.box((-4.5, 1.33 + k * 0.03, 4.98 + 0.02 * math.sin(k)), (0.4, 0.004, 0.06), paper("#f2ead0", 0.2), 0.0, 0.0)
    K.cyl((-5.4, 0.9, 4.7), 0.03, 1.8, panel_w, 8); K.cyl((-5.4, 0.02, 4.7), 0.25, 0.04, panel_w, 16)
    for k in range(3): K.sphere((-5.4 + 0.18 * math.cos(k * 2.1), 1.65, 4.7 + 0.18 * math.sin(k * 2.1)), 0.13, pm(["#4a5a3a", "#2a2a2a", "#7a6a4a"][k], 0.8), 8, (1, 1.4, 1))
    # big world map on the back wall
    wm = mat_once("wallmap", lambda: map_mat("wallmap", "map_world.png", 0.6))
    ikit.panel("wmap", (4.2, 2.9, 5.43), 2.6, 1.3, wm, 0.0)
    for k, (dx, dy, sw, sh) in enumerate(((0, 0.68, 2.72, 0.06), (0, -0.68, 2.72, 0.06), (1.33, 0, 0.06, 1.42), (-1.33, 0, 0.06, 1.42))): K.box((4.2 + dx, 2.9 + dy, 5.44), (sw, sh, 0.04), panel_w, 0.0, 0.0)
    # posters / notices, a telephone and a radio on a side desk at the window wall
    poster(K, (-0.4, 2.6, 5.48), 0.7, 0.95, 0.0, "#e8dcc0", [("NOTICE", 0.14), ("SECRET", 0.12), ("NO ENTRY", 0.09)], "#7a1e1a", border="#7a1e1a")
    K.box((5.4, 0.78, 2.6), (0.9, 0.06, 1.8), floor, 0.0, 0.01)
    for sz in (-1, 1): K.box((5.4, 0.38, 2.6 + sz * 0.8), (0.8, 0.76, 0.06), panel_w, 0.0, 0.0)
    K.box((5.4, 1.0, 2.0), (0.5, 0.4, 0.35), wood("#7a4a24", "#3a2010", 8.0, 0.35), 0.0, 0.01); K.cyl((5.18, 1.02, 2.0), 0.1, 0.01, pm("#d8c89a", 0.6), 16, "x")
    K.box((5.4, 0.86, 3.1), (0.25, 0.1, 0.18), pm("#141414", 0.3, 0.2), 0.0, 0.01); K.cyl((5.4, 0.95, 3.1), 0.025, 0.24, pm("#141414", 0.3, 0.2), 8, "z")
    # window on the right wall (x 6): mullions, glowing day sky, curtains
    win_m = lib.emit("mwin", (0.55, 0.7, 1.0), 3.0)
    K.box((5.98, 2.3, 1.0), (0.02, 2.0, 2.4), win_m, 0.0, 0.0)
    for k in range(4): K.box((5.95, 2.3, -0.2 + k * 0.8), (0.06, 2.0, 0.06), panel_w, 0.0, 0.0)
    for k in range(3): K.box((5.95, 1.3 + k * 1.0, 1.0), (0.06, 0.06, 2.4), panel_w, 0.0, 0.0)
    K.build()
    cur = mat_once("mcurt", lambda: lib.cloth("mcurt", "#6a1e1a"))
    for sd in (-1, 1): ikit.drape(f"mcur{sd}", (5.85, 3.7, 1.0 + sd * 1.5), 0.8, 3.6, cur, math.pi / 2, 5, 0.06)
    # ---- lights: two green-shaded lamps over the table, daylight from the window, a warm desk lamp ----
    shade_m = mat_once("mshade", lambda: lib.principled("mshade", hexc("#1e5a3a"), 0.35, 0.3))
    for k, x in enumerate((-1.1, 1.1)):
        lathe(f"lshade{k}", [(0.05, 0.0), (0.12, -0.05), (0.32, -0.25), (0.34, -0.27)], (x, 2.2, 1.2), shade_m, 32, cap=False)
        tube(f"lcord{k}", [(x, 2.2, 1.2), (x, 4.0, 1.2)], 0.008, pmat("kcord", "#1a1a1a", 0.6), res=2, bres=0)
        lathe(f"lbulb{k}", [(0.0, -0.12), (0.05, -0.15), (0.0, -0.21)], (x, 2.2, 1.2), lib.emit("mbulb", (1.0, 0.8, 0.5), 20), 16)
        L = lib.light("SPOT", T(x, 2.0, 1.2), 260, (1.0, 0.78, 0.5), 0.12); L.data.spot_size = math.radians(110); L.data.spot_blend = 0.6; L.rotation_euler = (0, 0, 0)
    CK.area((5.5, 2.4, 1.0), (0, 1.0, 1.2), 160, (0.6, 0.75, 1.0), 2.2, 1.8)
    CK.area((-2.5, 2.6, -3.5), (0, 1.2, 1.5), 90, (1.0, 0.75, 0.5), 3.0)
    CK.area((0, 3.0, 4.8), (0, 1.5, 2.5), 60, (1.0, 0.65, 0.4), 4.0)                    # back rim on the characters
    lib.light("POINT", T(-4.5, 1.9, 4.6), 25, (1.0, 0.6, 0.3), 0.1)
    # ---- toys on the map: Japanese tanks and flags in China, the US fleet at Pearl Harbor ----
    jpf = CK.jp_flag_mat(); usf = CK.us_flag_mat()
    ukf = mat_once("ukflag", lambda: ikit.img_mat("ukflag", ikit.flag_img("uk"), 0.8))
    nlf = mat_once("nlflag", lambda: ikit.img_mat("nlflag", (lambda a: (ikit.put(a, ikit.grid(a)[1] < 1 / 3, "#b8202c"), ikit.put(a, ikit.grid(a)[1] > 2 / 3, "#1e3a8a"), a)[-1])(ikit.canvas(128, 192, "#f4f1ea")), 0.8))
    pops = []
    for k, (lo, la) in enumerate(cfg.get("china", [])): pin(None, f"cn{k}", lo, la, jpf)
    from sets.void import toy_tank
    for k, (lo, la, yw) in enumerate(cfg.get("tanks", [])): toy_tank(f"tt{k}", (mx(lo), TOP, mz(la)), yw, "#7a6a3a", 0.8)
    for k, (lo, la) in enumerate(cfg.get("fleet", [])): toy_ship(f"ts{k}", (mx(lo), TOP, mz(la)), math.pi / 2 + 0.2, 0.2, "#6a7480")
    for k, (lo, la, f0) in enumerate(cfg.get("conquest", [])): pops.append((f0, pin(None, f"cq{k}", lo, la, jpf, 0.15, 0.085)))
    for k, (lo, la, f0) in enumerate(cfg.get("usflags", [])): pops.append((f0, pin(None, f"us{k}", lo, la, usf, 0.15, 0.085)))
    drops = [(f0, pin(None, f"jx{k}", lo, la, jpf)) for k, (lo, la, f0) in enumerate(cfg.get("jpdrop", []))]
    B = Kit("bar"); barrel_m = pm("#2a2a26", 0.4, 0.6); band = pm("#c8a24a", 0.4, 0.6)
    for k, (lo, la, fl) in enumerate(cfg.get("barrels", [])):
        x, z = mx(lo), mz(la)
        for j in range(3):
            bx_, bz_ = x + (j % 2) * 0.05 - 0.02, z + (j // 2) * 0.05
            B.cyl((bx_, TOP + 0.032, bz_), 0.022, 0.064, barrel_m, 14); B.cyl((bx_, TOP + 0.05, bz_), 0.0225, 0.006, band, 14)
        pin(None, f"bf{k}", lo + 1.5, la + 1.5, ukf if fl == "uk" else nlf, 0.11, 0.06)
    if cfg.get("barrels"): B.build()
    # ---- the oil pipeline and its valve, the oil gauge ----
    valve, needle = None, None
    if cfg.get("pipeline"):
        cu = pm("#b8863a", 0.3, 1.0); P = Kit("pipe")
        pts = [(237.6, 37.8), (215, 36.5), (186, 35.5), (160, 35.4), (141.5, 35.5)]
        for k in range(len(pts) - 1):
            a, b = Vector((mx(pts[k][0]), TOP + 0.05, mz(pts[k][1]))), Vector((mx(pts[k + 1][0]), TOP + 0.05, mz(pts[k + 1][1])))
            d = b - a; L = d.length; yaw = math.atan2(-d.z, d.x)
            P.cyl(tuple((a + b) / 2), 0.018, L, cu, 14, "x", None, yaw)
            P.cyl(tuple(a), 0.026, 0.03, cu, 14, "x", None, yaw)
        for k in range(14):
            f = k / 13; lo = 237.6 + (141.5 - 237.6) * f; la = 37.8 + (35.5 - 37.8) * f
            P.box((mx(lo), TOP + 0.022, mz(la)), (0.012, 0.044, 0.04), pm("#3a3a3a", 0.5, 0.6), 0.0, 0.0)
        P.cyl((VX, TOP + 0.05, VZ), 0.04, 0.08, cu, 16, "x"); P.cyl((VX, TOP + 0.1, VZ), 0.012, 0.1, cu, 10)
        sign(P, (mx(238), TOP + 0.16, mz(39)), 0.32, 0.09, 0.0, "U.S. OIL", board="#1e2a5a", ink=pm("#f2efe6", 0.5), kind="sans")
        P.cyl((mx(238), TOP + 0.06, mz(39)), 0.008, 0.12, pm("#3a3a3a", 0.5, 0.6), 8)
        P.build()
        V = Kit("valve"); red = pm("#b8202a", 0.4, 0.3)
        V.torus((0, 0, 0), 0.11, 0.012, red, 32, 8, "y")
        for k in range(4): V.box((0, 0, 0), (0.22, 0.012, 0.014), red, k * math.pi / 4, 0.0)
        V.cyl((0, 0, 0), 0.025, 0.03, red, 12)
        valve = V.build()[0]; valve.location = T(VX, TOP + 0.155, VZ)
        # gauge: brass case, painted dial (EMPTY / FULL), glass, needle on its own object
        dial = ikit.canvas(256, 256, "#f2ead6"); xg, yg = ikit.grid(dial)
        ang = __import__("numpy").arctan2(xg - 0.5, 0.62 - yg); rr = ((xg - 0.5) ** 2 + (yg - 0.62) ** 2) ** 0.5
        ikit.put(dial, (rr > 0.34) & (rr < 0.42) & (ang < -0.6) & (ang > -1.3), "#c8202a")
        ikit.put(dial, (rr > 0.34) & (rr < 0.42) & (ang > 0.6) & (ang < 1.3), "#2a8a3a")
        for k in range(9):
            a = -1.3 + k * 2.6 / 8; ikit.put(dial, (abs(ang - a) < 0.02) & (rr > 0.3) & (rr < 0.42), "#1a1a1a")
        ikit.stamp(dial, "E", 0.17, 0.44, 0.1, "#a8181e", bold=0.15); ikit.stamp(dial, "F", 0.76, 0.44, 0.1, "#1e6a2a", bold=0.15)
        ikit.stamp(dial, "OIL", 0.5, 0.7, 0.11, "#1a1a1a", bold=0.2, align="center")
        rr2 = ((xg - 0.5) ** 2 + (yg - 0.5) ** 2) ** 0.5; ikit.put(dial, rr2 > 0.5, "#b8863a"); ikit.put(dial, (rr2 > 0.47) & (rr2 <= 0.5), "#3a2a1a")
        G = Kit("gauge")
        G.cyl((GX, TOP + 0.24, GZ + 0.02), 0.25, 0.06, brass(), 32, "z"); G.box((GX, TOP + 0.05, GZ + 0.02), (0.12, 0.1, 0.08), brass(), 0.0, 0.01)
        G.build()
        ikit.panel("gdial", (GX, TOP + 0.24, GZ - 0.012), 0.34, 0.34, ikit.img_mat("gdialm", dial, 0.35), 0.0)
        N = Kit("needle"); N.box((0, 0.06, 0), (0.012, 0.14, 0.006), pm("#1a1a1a", 0.4, 0.3), 0.0, 0.0); N.cyl((0, 0, 0), 0.016, 0.01, pm("#8a1a1a", 0.4, 0.4), 12, "z")
        needle = N.build()[0]; needle.location = T(GX, TOP + 0.22, GZ - 0.02)
    hop = None
    def update(f):
        if valve is not None:
            u = min(1.0, max(0.0, (f - cfg["valve"][0]) / (cfg["valve"][1] - cfg["valve"][0])))
            valve.rotation_euler = (0, 0, u * u * (3 - 2 * u) * 3.0 * math.pi)
        if needle is not None:
            u = min(1.0, max(0.0, (f - cfg["gauge"][0]) / (cfg["gauge"][1] - cfg["gauge"][0])))
            a = 1.05 - 2.1 * (u * u * (3 - 2 * u)) - (0.06 * math.sin(f * 1.7) if u >= 1 else 0)
            needle.rotation_euler = (0, a, 0)
        for f0, objs in pops:
            u = (f - f0) / 6.0
            s = 0.0 if u < 0 else (min(1.15, u * 1.15) if u < 1 else 1.0 + 0.15 * math.exp(-(u - 1) * 1.5) * math.cos((u - 1) * 3))
            for o in objs: o.scale = (max(1e-3, s),) * 3; o.hide_render = s < 0.01
        for f0, objs in drops:
            u = (f - f0) / 8.0
            for o in objs: o.rotation_euler = (0, 0, 0) if u < 0 else (min(1.0, u) * 1.4, 0, 0); o.hide_render = u > 1.6
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}

CFG7 = dict(china=CHINA, tanks=[(117, 35, 2.4), (114, 31, 2.8), (119.5, 37, 2.2), (110.5, 33, 3.0)], fleet=[(201.2, 21.6), (202.4, 21.9), (203.3, 21.4), (201.8, 20.9), (203.0, 20.6)],
            conquest=CONQ7, barrels=[(114.5, 1.5, "nl"), (102.5, -1.0, "nl"), (110.0, -7.0, "nl"), (101.8, 4.2, "uk")], pipeline=True, valve=(203, 236), gauge=(262, 318))
def build(M, D): return build_room(M, D, CFG7)
