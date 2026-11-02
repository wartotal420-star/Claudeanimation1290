# Hiroshima (chapter 13, the atomic bomb shots). SERIOUS: no jokes, no victims shown, no destruction shown.
#   f < F_MEMORIAL: the city on a clear summer morning: the Motoyasu river, the domed Industrial Promotion Hall on the far
#     bank, tiled wooden houses, a tram, a lone bomber high overhead with its contrail; at F_FLASH the light fills
#     everything (white-out), nothing else.
#   f >= F_MEMORIAL: the same riverbank at dusk years later: the bare skeleton dome, empty ground with young trees, paper
#     lanterns floating on the river, candles on the embankment, a stopped watch (11:02, Nagasaki) on a stone.
# three.js layout: the river runs along x between the near embankment (z 6) and the far one (z 34); water y -1.4.
#   The dome building centred (0, 0, 46), dome top y ~25. Near bank promenade y 0, z -10..6 (camera side): stone lantern
#   at (-4, 0, 2), willow at (6, 0, 1); the watch on a stone at (1.2, 0.62, 3.2); candles along the edge z 5.4.
#   The bomber: high at y 1800 crossing +x (contrail), visible with a narrow lens looking up.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj, candle, pocket_watch
from sets import c07_kit as CK
from sets import ikit

F_FLASH = 3016
F_MEMORIAL = 3062
SUN_AM = (0.6, 0.55, -0.6)
SUN_DUSK = (-0.9, 0.08, 0.3)

def roofs(K, x, z, w, d, h, y0, tile, rnd):
    for sd in (-1, 1):
        K.box((x, y0 + h / 2, z + sd * d / 4), (w + 0.6, 0.12, d / 2 + 0.6), tile, 0.0, 0.0, -sd * math.atan2(h, d / 2))
    K.box((x, y0 + h + 0.05, z), (w + 0.7, 0.18, 0.3), pm("#2a2a2e", 0.6), 0.0, 0.02)

def build(M, D):
    rnd = random.Random(806)
    S = bpy.context.scene
    W_am = S.world
    CK.sky(W_am, SUN_AM, [(0.0, (0.82, 0.86, 0.9)), (0.06, (0.5, 0.66, 0.86)), (0.35, (0.2, 0.42, 0.76)), (1.0, (0.06, 0.18, 0.52))],
           sun_col=(30, 28, 22), cloud_dark=(0.5, 0.52, 0.58), cloud_lit=(1.3, 1.25, 1.15), cover=0.3, strength=0.8, glow_col=(1.0, 0.95, 0.85), glow=0.35)
    W_dusk = bpy.data.worlds.new("wdusk"); W_dusk.use_nodes = True
    CK.sky(W_dusk, SUN_DUSK, [(0.0, (0.95, 0.5, 0.3)), (0.05, (0.7, 0.4, 0.42)), (0.18, (0.28, 0.24, 0.4)), (0.5, (0.07, 0.08, 0.2)), (1.0, (0.02, 0.025, 0.08))],
           sun_col=(14, 7, 3), cloud_dark=(0.1, 0.08, 0.14), cloud_lit=(1.0, 0.5, 0.35), cover=0.45, strength=0.8, glow_col=(1.0, 0.5, 0.3), glow=0.8)
    bg_am = W_am.node_tree.nodes["Background"]
    sun = CK.sun_light(SUN_AM, 4.6, (1.0, 0.95, 0.85), 1.2); dusk = CK.sun_light(SUN_DUSK, 1.6, (1.0, 0.55, 0.3), 2.0)
    stone = mat_once("hstone", lambda: lib.brickmat("hstone", "#8a8478", "#76706a", "#4a4640", 1.4, 0.8, 0.35, 0.85))
    ground = mat_once("hgr", lambda: CK.green_hill_mat("hgr", "#7a7258", "#5a5440", "#8a8268"))
    CK.heightfield("near", -200, 200, -120, 6, 2.0, lambda x, z: 0.0, ground)
    CK.heightfield("far", -200, 200, 34, 220, 2.0, lambda x, z: 0.0, ground)
    CK.sea("river", -400, 400, 4, 36, -1.4, CK.water_mat("hriver", "#1e3a3a", "#3a5a52", 2.0, 0.03, 0.15))
    K = Kit("hc")
    for zz in (6.0, 34.0): K.box((0, -0.7, zz), (400, 1.5, 0.6), stone, 0.0, 0.02)
    for k in range(5): K.box((-12 + k * 0.9, -0.4 - k * 0.22, 5.2 - k * 0.3), (0.85, 0.2, 2.0), stone, 0.0, 0.01)      # river steps
    # stone lantern, benches, a willow, the stone with the watch
    lath = mat_once("hlant", lambda: lib.plaster("hlant", "#9a948a"))
    lathe("slant", [(0.0, 0.0), (0.35, 0.0), (0.35, 0.15), (0.12, 0.2), (0.1, 0.9), (0.3, 0.95), (0.32, 1.25), (0.45, 1.3), (0.1, 1.55), (0.06, 1.7), (0.0, 1.75)], (-4, 0, 2), lath, 6)
    K.box((-4, 1.1, 2), (0.42, 0.25, 0.42), em("#ffc070", 0.0), 0.0, 0.0)
    K.box((1.2, 0.3, 3.2), (0.9, 0.6, 0.7), stone, 0.3, 0.06)
    wood_b = wood("#6a5034", "#3a2a1a", 4.0, 0.7)
    for k, x in enumerate((-9, 9)):
        K.box((x, 0.45, -2), (1.8, 0.08, 0.45), wood_b, 0.0, 0.01)
        for sx in (-0.7, 0.7): K.box((x + sx, 0.22, -2), (0.08, 0.45, 0.4), stone, 0.0, 0.0)
    K.build()
    bark = mat_once("hbark", lambda: worn("hbark", "#4a3a2a", "#2a1e14", 0.9, 0.0, 3, 0.55, "#3a3a2a"))
    tube("willow", [(6, 0, 1), (6.2, 2.5, 1.1), (5.6, 5, 1.6)], 0.3, bark, res=4, bres=2, taper=lambda f: 1 - 0.5 * f)
    leaf = mat_once("hleaf", lambda: CK.leaf_mat("hleaf", "#6a9a3a", "#3a6a1e"))
    for k in range(26):
        a = rnd.uniform(0, math.tau); r = rnd.uniform(0.5, 3.0); top = (5.6 + r * math.cos(a), rnd.uniform(4.2, 5.4), 1.6 + r * math.sin(a))
        tube(f"wbr{k}", [top, (top[0] + 0.2, top[1] - 1.5, top[2]), (top[0] + 0.3, top[1] - rnd.uniform(2.6, 3.8), top[2] + 0.1)], 0.05, leaf, res=6, bres=1)
    # ---------- morning state: the domed hall, houses, a tram, the bomber ----------
    before = set(bpy.data.objects.keys())
    H = Kit("hall"); brick = mat_once("hbrick", lambda: lib.brickmat("hbrick", "#a8846a", "#8a6a54", "#5a4a40", 3.0, 0.5, 0.25, 0.85))
    win = pm("#2a3038", 0.2); copper = pm("#4a8a72", 0.4, 0.6); trim = pm("#d8d0bc", 0.6)
    H.box((0, 6.5, 46), (36, 13, 14), brick, 0.0, 0.05)
    for fl in range(3):
        for k in range(14): H.box((-16 + k * 2.45, 2.5 + fl * 4, 38.95), (1.1, 2.2, 0.1), win, 0.0, 0.0)
        H.box((0, 4.5 + fl * 4, 38.9), (36.2, 0.25, 0.2), trim, 0.0, 0.0)
    H.box((0, 9.5, 46), (11, 19, 11), brick, 0.0, 0.05)
    for fl in range(5):
        for k in range(4): H.box((-3.6 + k * 2.4, 2.5 + fl * 3.6, 40.4), (1.0, 2.2, 0.1), win, 0.0, 0.0)
    H.cyl((0, 19.5, 46), 5.6, 1.2, trim, 32)
    H.build()
    dome = lathe("dome", [(5.4, 20.0), (5.3, 21.5), (4.6, 23.2), (3.2, 24.6), (1.6, 25.4), (0.4, 25.7), (0.0, 25.75)], (0, 0, 46), copper, 32)
    houses = Kit("houses"); tile = pm("#3a3c42", 0.6); wl = mat_once("hwall", lambda: worn("hwall", "#c8b898", "#8a7a60", 0.9, 0.0, 2, 0.6, "#a89878"))
    for k in range(120):
        x, z = rnd.uniform(-180, 180), rnd.uniform(38, 200)
        if abs(x) < 24 and z < 58: continue
        w, d, h = rnd.uniform(5, 9), rnd.uniform(4, 7), rnd.uniform(3, 6)
        houses.box((x, h / 2, z), (w, h, d), wl, 0.0, 0.02); roofs(houses, x, z, w, d, 1.6, h, tile, rnd)
    for k in range(60):
        x, z = rnd.uniform(-180, 180), rnd.uniform(-110, -14)
        w, d, h = rnd.uniform(5, 9), rnd.uniform(4, 7), rnd.uniform(3, 6)
        houses.box((x, h / 2, z), (w, h, d), wl, 0.0, 0.02); roofs(houses, x, z, w, d, 1.6, h, tile, rnd)
    for k in range(9):                                                   # the T-shaped bridge, a tram on it
        houses.box((-60, -0.2, 6 + k * 3.5), (14, 0.5, 3.6), stone, 0.0, 0.02)
    houses.box((-60, 0.4, 20), (0.3, 0.8, 30), stone, 0.0, 0.0)
    houses.box((-58, 1.8, 18), (2.4, 2.6, 9), pm("#3a6a4a", 0.5, 0.2), 0.0, 0.1); houses.box((-58, 3.2, 18), (2.0, 0.2, 8.6), pm("#2a2a2a", 0.5), 0.0, 0.0)
    for k in range(6): houses.box((-56.75, 2.2, 14.2 + k * 1.4), (0.05, 1.0, 1.0), pm("#cfe0e8", 0.1), 0.0, 0.0)
    houses.build()
    morning = [bpy.data.objects[k] for k in set(bpy.data.objects.keys()) - before]
    b29 = CK.inst(CK.plane("b29", gear=False, spin=True), "enola")
    con = mat_once("hcon", lambda: CK.smoke_mat("hcon", "#f4f6f8", 0.8))
    trail = [tube(f"trail{k}", [(-3000, 1800 + k * 6, 300 + k * 30), (0, 1800 + k * 6, 300 + k * 30)], 6 + k * 3, con, res=2, bres=3) for k in range(2)]
    flash = lib.light("SUN", (0, 0, 0), 0.0, (1.0, 0.96, 0.9), math.radians(30)); flash.rotation_euler = (math.radians(10), 0, 0)
    # ---------- memorial state: the skeleton dome, bare ground, lanterns on the river, candles, the stopped watch ----------
    before = set(bpy.data.objects.keys())
    R = Kit("ruin"); rb = mat_once("hruin", lambda: worn("hruin", "#8a7a6a", "#4a3e36", 0.9, 0.0, 1.5, 0.5, "#5a4a40"))
    for k in range(5): R.box((-4.0 + k * 2.0, 6 + (k % 2) * 3, 40.5), (1.2, 12 + (k % 2) * 6, 0.8), rb, 0.0, 0.03)
    for sd in (-1, 1):
        R.box((sd * 5.4, 7.5, 46), (0.8, 15, 11), rb, 0.0, 0.03)
        for k in range(3): R.box((sd * (8 + k * 3.5), 2.5 + (k % 2) * 2.5, 39.5), (2.4, 5 + (k % 2) * 5, 0.9), rb, 0.0, 0.03)
    R.cyl((0, 19.5, 46), 5.6, 1.0, rb, 32)
    steel = pm("#3a3634", 0.6, 0.6)
    R.torus((0, 22.5, 46), 4.9, 0.12, steel, 40, 6); R.torus((0, 24.6, 46), 3.1, 0.1, steel, 32, 6)
    R.build()
    for k in range(12):
        a = k / 12 * math.tau
        tube(f"rib{k}", [(5.3 * math.cos(a), 20.0, 46 + 5.3 * math.sin(a)), (4.6 * math.cos(a), 23.2, 46 + 4.6 * math.sin(a)), (1.6 * math.cos(a), 25.4, 46 + 1.6 * math.sin(a)), (0.3 * math.cos(a), 25.7, 46 + 0.3 * math.sin(a))], 0.12, steel, res=4, bres=1)
    for k in range(10): CK.puff(f"ytree{k}", (rnd.uniform(-60, 60), 3.5, rnd.uniform(60, 140)), (2.2, 2.6, 2.2), leaf, k, True)
    lan = []
    lp = mat_once("hlantern", lambda: lib.principled("hlantern", hexc("#f2e2c0"), 0.8, 0.0, (1.0, 0.62, 0.3), 3.0))
    L = Kit("lanterns")
    for k in range(34):
        x, z = rnd.uniform(-34, 34), rnd.uniform(9, 30)
        L.box((x, -1.25, z), (0.36, 0.36, 0.36), lp, rnd.uniform(0, 1), 0.01); L.box((x, -1.41, z), (0.44, 0.06, 0.44), wood_b, 0.0, 0.0)
        if k % 5 == 0: lan.append(lib.light("POINT", T(x, -0.9, z), 8, (1.0, 0.6, 0.3), 0.15))
    L.build()
    for k in range(9): candle(f"hc{k}", (-6 + k * 1.5, 0.0, 5.4), 0.18, k, 0.6)
    pocket_watch("watch", (1.2, 0.6, 3.15), 0.6)
    memorial = [bpy.data.objects[k] for k in set(bpy.data.objects.keys()) - before]
    fill = CK.area((0, 4, -12), (0, 1, 4), 400, (1.0, 0.8, 0.6), 8)
    def update(f):
        mem = f >= F_MEMORIAL
        S.world = W_dusk if mem else W_am
        CK.show(morning + [dome] + trail, not mem); CK.show(memorial, mem); sun.hide_render = mem; dusk.hide_render = not mem
        u = (f - 2850) / 30.0
        b29.hide_render = mem or u < 0
        CK.place(b29, (-400 + 105 * u, 1800, 300), (1, 0, 0), 0.0, 1.0)
        for tr in trail: tr.location = T(-400 + 105 * u - 30, 0, 0)
        w = (f - F_FLASH) / 4.0
        if not mem and w >= 0:
            k = min(1.0, w)
            flash.data.energy = 2000 * k; bg_am.inputs[1].default_value = 0.8 + 400 * k
        else:
            flash.data.energy = 0; bg_am.inputs[1].default_value = 0.8
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
