# Chapter 5: Churchill's Cabinet War Rooms, the Map Room under Whitehall, summer 1940.
# Layout (three coords, y up): room x -6.5..6.5, z -6..5.6, ceiling y 3.3 held up by red-painted steel girders and
# stanchions; the big wall map of Europe 1940 (maps/c05_europe1940.png) on the back wall, x -1.95..1.95, y 0.5..3.1,
# z 5.48 (lon -14..46 left->right, lat 66..26 top->bottom). Two long desks along z at x +-3.6 (top y 0.76) with the
# coloured telephones, lamps, papers; a weather board, clocks, posters. Keep clear: Churchill at (0, 0, 4.3) and the
# floor |x| < 2.3, z -4..4.8 (staff stand there); desks seat staff at x +-2.9 / +-4.3.
import bpy, math, random
import lib
from lib import T
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, brick, paper, text, sign, poster, crate, glassm, R90
from .c05_kit import img_mat, wall_quad, point, area, spot, lathe, tube, worn, mat_once, smoke_mat
import os
MAPS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps")

def lamp(K, x, y, z, shade_m, cord_m, energy=60):
    K.cyl((x, (3.3 + y) / 2, z), 0.008, 3.3 - y, cord_m, 6)
    K.cyl((x, y, z), 0.32, 0.18, shade_m, 24, "y", 0.06)
    K.cyl((x, y + 0.12, z), 0.07, 0.08, shade_m, 12)
    K.sphere((x, y - 0.1, z), 0.06, em("#ffd8a0", 20.0), 10)
    point((x, y - 0.14, z), energy, (1.0, 0.72, 0.42), 0.06)

def phone(K, c, col):
    x, y, z = c; m = pm(col, 0.18)
    K.box((x, y + 0.04, z), (0.2, 0.08, 0.24), m, 0, 0.03)
    K.cyl((x, y + 0.085, z + 0.03), 0.05, 0.03, pm("#e8e0d0", 0.3), 16)
    K.box((x, y + 0.13, z - 0.02), (0.24, 0.04, 0.05), m, 0, 0.015)
    for sd in (-1, 1): K.sphere((x + sd * 0.11, y + 0.13, z - 0.02), 0.035, m, 10)
    tube("cord", [(x + 0.08, y + 0.03, z + 0.1), (x + 0.2, y + 0.005, z + 0.2), (x + 0.15, y + 0.005, z + 0.35)], 0.006, m)

def desk(K, x0, x1, z0, z1, top_m, leg_m, baize):
    K.box(((x0 + x1) / 2, 0.75, (z0 + z1) / 2), (x1 - x0, 0.05, z1 - z0), top_m, 0, 0.01)
    K.box(((x0 + x1) / 2, 0.778, (z0 + z1) / 2), (x1 - x0 - 0.12, 0.006, z1 - z0 - 0.12), baize, 0, 0.0)
    for x in (x0 + 0.08, x1 - 0.08):
        for z in (z0 + 0.08, z1 - 0.08): K.box((x, 0.37, z), (0.07, 0.74, 0.07), leg_m, 0, 0.01)

def build(M, D):
    random.seed(1940); K_.reset(); K = Kit("cab"); rnd = random.Random(5)
    sid = D.get("id", 0)
    # ---------------- shell ----------------
    LINO = lib.brickmat("cablino", "#4a3a2e", "#42342a", "#2a201a", 1.2, 0.5, 0.5, 0.35)
    WALL = grime("cabwall", "#e4d8bc", 0.3); WALLB = grime("cabwallb", "#5a6a4e", 0.35)
    CEIL = grime("cabceil", "#d8d0bc", 0.35); RED = mat_once("cabred", lambda: worn("cabred", "#9a2a22", "#4a3a30", 0.6, 0.3, 6, 0.7, "#5a2018"))
    K.box((0, -0.05, -0.3), (13.2, 0.1, 12.2), LINO, 0, 0)
    K.box((0, 3.35, -0.3), (13.2, 0.1, 12.2), CEIL, 0, 0)
    K.box((0, 1.65, 5.7), (13.2, 3.4, 0.3), WALL, 0, 0)
    K.box((0, 0.5, 5.53), (13.0, 1.0, 0.04), WALLB, 0, 0)            # dark green dado
    K.box((0, 1.02, 5.5), (13.0, 0.04, 0.05), pm("#2a3424", 0.5), 0, 0.005)
    for sx in (-1, 1):
        K.box((sx * 6.75, 1.65, -0.3), (0.3, 3.4, 12.2), WALL, 0, 0)
        K.box((sx * 6.58, 0.5, -0.3), (0.04, 1.0, 12.0), WALLB, 0, 0)
    K.box((0, 1.65, -6.45), (13.2, 3.4, 0.3), WALL, 0, 0)
    # steel girders (I-beams) across the room, stanchions, timber packing, an air duct and conduits
    for z in (-4.2, -1.6, 1.0, 3.6):
        K.box((0, 3.1, z), (13.0, 0.4, 0.06), RED, 0, 0.005)
        for dy in (-0.19, 0.19): K.box((0, 3.1 + dy, z), (13.0, 0.03, 0.26), RED, 0, 0.004)
        for sx in (-1, 1):
            K.box((sx * 3.2, 1.45, z), (0.06, 2.9, 0.22), RED, 0, 0.004)
            for dx in (-0.1, 0.1): K.box((sx * 3.2 + dx, 1.45, z), (0.02, 2.9, 0.22), RED, 0, 0.003)
            K.box((sx * 3.2, 0.03, z), (0.36, 0.06, 0.36), RED, 0, 0.005)
    K.cyl((-4.8, 2.95, -0.3), 0.26, 12.0, pm("#8a8c88", 0.45, 0.6), 20, "z")
    for z in (-5, -2, 1, 4): K.cyl((-4.8, 2.95, z), 0.29, 0.06, pm("#6a6c68", 0.45, 0.6), 20, "z")
    for k, x in enumerate((-5.9, -5.7, 5.8)): K.cyl((x, 2.75 + k * 0.05, -0.3), 0.025, 12.0, pm("#3a3a3a", 0.5, 0.5), 8, "z")
    # ---------------- the map wall ----------------
    mapm = img_mat("c05map", os.path.join(MAPS, "c05_europe1940.png"), 0.55)
    wall_quad("wallmap", (0, 1.8, 5.5), 3.9, 2.6, mapm)
    WD = wood("#5a3a22", "#2a1a0e", 6, 0.45)
    for (c, s) in (((0, 3.13, 5.48), (4.05, 0.08, 0.06)), ((0, 0.47, 5.48), (4.05, 0.08, 0.06)), ((2.0, 1.8, 5.48), (0.08, 2.74, 0.06)), ((-2.0, 1.8, 5.48), (0.08, 2.74, 0.06))):
        K.box(c, s, WD, 0, 0.01)
    # pins and string on the map: Britain's defences, the coast of France, the convoy routes
    PIN = [("#c81e22", -0.1, 51.5), ("#c81e22", -1.9, 52.5), ("#c81e22", -3.2, 55.9), ("#c81e22", 1.3, 51.1), ("#2a3a8a", -5.0, 50.1),
           ("#202020", 2.3, 48.9), ("#202020", 4.4, 50.8), ("#202020", 10.0, 53.5), ("#202020", 13.4, 52.5), ("#202020", -1.6, 49.6),
           ("#2a3a8a", -9.0, 54.0), ("#2a3a8a", -12.0, 57.0), ("#e8c030", 14.5, 35.9), ("#c81e22", 31.2, 30.0), ("#202020", 12.5, 41.9)]
    def MP(lon, lat): return (1.95 - (lon + 14) / 60 * 3.9, 3.1 - (66 - lat) / 40 * 2.6, 5.47)
    for k, (col, lo, la) in enumerate(PIN):
        x, y, z = MP(lo, la); K.cyl((x, y, z - 0.03), 0.004, 0.06, pm("#c8c8c8", 0.3, 1.0), 6, "z"); K.sphere((x, y, z - 0.065), 0.018, pm(col, 0.3), 10)
    for a, b in ((0, 1), (1, 2), (0, 3), (10, 11), (4, 10)):
        p, q = MP(*PIN[a][1:]), MP(*PIN[b][1:]); tube(f"str{a}{b}", [(p[0], p[1], 5.42), (q[0], q[1], 5.42)], 0.003, pm("#c01e22", 0.6))
    # weather board (WINDY = an air raid on), clocks, posters, notice boards
    K.box((3.8, 1.75, 5.52), (1.3, 0.55, 0.05), pm("#1e2a22", 0.5), 0, 0.01)
    text("WEATHER", (3.8, 1.92, 5.49), 0.11, pm("#e8dcb8", 0.6), 0, "sans", 0.002, fit=1.1)
    K.box((3.8, 1.67, 5.49), (1.0, 0.2, 0.02), pm("#f0e8d0", 0.6), 0, 0.003)
    text("WINDY", (3.8, 1.67, 5.475), 0.15, pm("#1a1a1a", 0.6), 0, "sans", 0.002, fit=0.9)
    # the world map above the posters, framed, with convoy pins in the Atlantic
    wall_quad("worldmap", (-3.75, 2.55, 5.5), 2.3, 1.15, img_mat("c05world", os.path.join(MAPS, "map_world.png"), 0.55))
    for (c, s_) in (((-3.75, 3.16, 5.48), (2.42, 0.07, 0.05)), ((-3.75, 1.94, 5.48), (2.42, 0.07, 0.05)), ((-2.57, 2.55, 5.48), (0.07, 1.29, 0.05)), ((-4.93, 2.55, 5.48), (0.07, 1.29, 0.05))):
        K.box(c, s_, WD, 0, 0.01)
    for k in range(9): K.sphere((-3.75 + 0.35 - k * 0.07, 2.62 + 0.1 * math.sin(k), 5.46), 0.014, pm("#c81e22" if k % 3 else "#2a3a8a", 0.3), 8)
    # box files on shelves along the right wall, labelled
    for r in range(4):
        K.box((6.38, 0.5 + r * 0.45, 0.6), (0.36, 0.03, 2.6), WD, 0, 0.005)
        for k in range(16):
            K.box((6.36, 0.67 + r * 0.45, -0.6 + k * 0.155), (0.3, 0.32, 0.12), pm(("#2a3a5a", "#5a2a22", "#3a4a2a", "#6a5a3a")[(k + r) % 4], 0.7), 0, 0.006)
            K.box((6.2, 0.7 + r * 0.45, -0.6 + k * 0.155), (0.01, 0.07, 0.07), paper("#f0e8d0"), 0, 0.0)
    for x, lab in ((3.2, "LONDON"), (4.4, "WASHINGTON")):
        K.cyl((x, 2.6, 5.52), 0.24, 0.06, wood("#3a2212", "#1a0a04", 8, 0.35), 28, "z")
        K.cyl((x, 2.6, 5.48), 0.2, 0.01, pm("#efe6cc", 0.5), 28, "z")
        for k in range(12):
            a = k / 12 * math.tau; K.box((x + 0.16 * math.sin(a), 2.6 + 0.16 * math.cos(a), 5.47), (0.012, 0.035, 0.004), pm("#1a1a1a", 0.6), 0, 0, 0, a)
        h = rnd.random() * math.tau
        K.box((x + 0.05 * math.sin(h), 2.6 + 0.05 * math.cos(h), 5.465), (0.014, 0.11, 0.004), pm("#1a1a1a", 0.6), 0, 0, 0, -h)
        K.box((x + 0.07 * math.sin(h * 3), 2.6 + 0.07 * math.cos(h * 3), 5.462), (0.009, 0.16, 0.004), pm("#1a1a1a", 0.6), 0, 0, 0, -h * 3)
        K.box((x, 2.26, 5.5), (0.42, 0.08, 0.02), brass(), 0, 0.003); text(lab, (x, 2.26, 5.485), 0.045, pm("#1a1a1a", 0.6), 0, "sans", 0.001, fit=0.32)
    poster(K, (-3.0, 1.45, 5.53), 0.5, 0.7, 0, "#e8d8b0", [("CARELESS", 0.13), ("TALK", 0.13), ("COSTS LIVES", 0.1)], "#a81e22", None, "sans", "#a81e22")
    poster(K, (5.5, 1.6, 5.53), 0.6, 0.84, 0, "#c8202a", [("KEEP", 0.14), ("MUM", 0.14), ("SHE'S NOT SO DUMB", 0.05)], "#f4ecd8", None, "sans")
    poster(K, (-4.6, 1.45, 5.53), 0.5, 0.7, 0, "#2a4a8a", [("BRITAIN", 0.12), ("SHALL NOT", 0.1), ("BURN", 0.13)], "#f4ecd8", None, "sans", "#e8c030")
    poster(K, (6.58, 1.7, 2.6), 0.6, 0.84, R90, "#3a6a3a", [("DIG", 0.15), ("FOR", 0.1), ("VICTORY", 0.12)], "#f4ecd8", None, "sans")
    poster(K, (-6.58, 1.7, 1.5), 0.6, 0.84, -R90, "#e8c030", [("WE'RE", 0.1), ("GOING TO", 0.09), ("SEE IT", 0.12), ("THROUGH", 0.1)], "#1a1a1a", None, "sans")
    sign(K, (0, 3.0, -6.28), 1.6, 0.26, math.pi, "MAP ROOM", "#f0e8d0", pm("#1a1a1a", 0.6), "sans", None, 0.03)
    for sx in (-1, 1):  # cork notice boards with pinned papers along the side walls
        z0 = -2.6
        K.box((sx * 6.57, 1.75, z0), (0.04, 1.0, 1.6), pm("#a8784a", 0.85), 0, 0.01)
        for k in range(7):
            K.box((sx * 6.54, 1.45 + (k % 3) * 0.28, z0 - 0.6 + k * 0.2), (0.01, 0.24, 0.18), paper("#f0e8d0" if k % 2 else "#e8e0a8"), 0, 0.0, rnd.uniform(-0.1, 0.1))
    # ---------------- furniture ----------------
    TOP = wood("#6a4428", "#3a2414", 5, 0.4); LEG = wood("#4a2e18", "#22140a", 5, 0.5); BAIZE = cloth("#2e5a3a")
    for sx in (-1, 1):
        desk(K, sx * 3.6 - 0.55, sx * 3.6 + 0.55, -3.5, 3.5, TOP, LEG, BAIZE)
        for k, z in enumerate((-2.8, -1.2, 0.4, 2.0)):  # phones in a row: white, green, red, black (the "beauty chorus")
            phone(K, (sx * 3.6 - sx * 0.25, 0.78, z), ("#f2ece0", "#2e6a3a", "#b82a22", "#1a1a1c")[(k + (sx > 0)) % 4])
            K.box((sx * 3.6 + sx * 0.1, 0.785, z + 0.45), (0.36, 0.01, 0.46), paper("#f2ead6"), 0.2 * k, 0.0)
            K.box((sx * 3.6 + sx * 0.12, 0.79, z + 0.48), (0.3, 0.004, 0.36), paper("#e8dcb8"), 0.4 * k + 0.2, 0.0)
        for z in (-2.0, 1.2):  # green-shaded desk lamps
            K.cyl((sx * 3.85, 0.79, z), 0.1, 0.03, brass(), 20)
            K.cyl((sx * 3.85, 0.95, z), 0.012, 0.32, brass(), 8)
            K.cyl((sx * 3.85, 1.12, z), 0.07, 0.3, pm("#1e5a32", 0.15), 20, "x"); point((sx * 3.85, 1.05, z), 6, (1.0, 0.76, 0.45), 0.04)
        for z in (-0.4, 2.8):  # ashtray with a cigar, in-trays, inkstand, teacup
            K.cyl((sx * 3.4, 0.79, z), 0.07, 0.02, glassm(), 20)
            K.box((sx * 3.95, 0.83, z - 0.4), (0.34, 0.1, 0.26), wood("#3a2212", "#1a0a04", 8, 0.35), 0, 0.01)
            K.cyl((sx * 3.3, 0.82, z + 0.6), 0.045, 0.07, pm("#f2ece0", 0.2), 16)
        K.box((sx * 3.6, 0.83, -3.3), (0.42, 0.1, 0.3), pm("#141214", 0.2), 0, 0.03)             # typewriter
        K.box((sx * 3.6, 0.92, -3.2), (0.3, 0.14, 0.004), paper("#f2ead6"), 0, 0.0)
        for k, z in enumerate((-3.0, -1.4, 0.2, 1.8, 3.2)):  # bentwood chairs
            for xx in (sx * 2.85, sx * 4.35):
                K.box((xx, 0.46, z), (0.42, 0.05, 0.42), LEG, 0, 0.02)
                for dx in (-0.17, 0.17):
                    for dz in (-0.17, 0.17): K.cyl((xx + dx, 0.23, z + dz), 0.018, 0.46, LEG, 8)
                bz = xx + (0.2 if xx * sx > 3.6 * abs(sx) else -0.2) * sx
                K.box((bz, 0.75, z), (0.03, 0.55, 0.38), LEG, 0, 0.01)
    for sx in (-1, 1):
        K.cyl((sx * 3.5, 0.9, -3.0), 0.07, 0.2, glassm(), 16); K.cyl((sx * 3.5, 0.86, -3.0), 0.06, 0.1, pm("#8a4a14", 0.1), 16)
        K.box((sx * 3.8, 0.8, -2.6), (0.26, 0.05, 0.18), wood("#6a3a1a", "#3a1a08", 10, 0.3), 0.3, 0.005)
        for k in range(3): K.box((sx * 3.4, 0.79 + k * 0.012, -2.3 + k * 0.02), (0.3, 0.01, 0.4), pm("#c8a060" if k % 2 else "#d86a3a", 0.8), 0.15 * k, 0.002)
        text("MOST SECRET", (sx * 3.4, 0.83, -2.3), 0.035, pm("#a81e22", 0.6), 0.3, "sans", 0.001, pitch=-R90)
    # filing cabinets, a safe, coat stand with a bowler, fire buckets, stirrup pump, sandbag, waste basket
    for k, z in enumerate((-5.6, -4.9, -4.2)):
        K.box((6.25, 0.65, z), (0.6, 1.3, 0.66), worn("cabfile", "#5a6050", "#2a2a26", 0.5, 0.5, 30, 0.7), 0, 0.01)
        for d in range(4):
            K.box((5.94, 0.22 + d * 0.3, z), (0.02, 0.26, 0.58), pm("#646a58", 0.45, 0.5), 0, 0.004); K.box((5.92, 0.3 + d * 0.3, z), (0.02, 0.025, 0.14), brass(), 0, 0.002)
    K.box((-6.1, 0.55, -5.4), (0.8, 1.1, 0.8), pm("#2a3a2e", 0.35, 0.4), 0, 0.03)
    K.cyl((-5.69, 0.6, -5.4), 0.1, 0.03, brass(), 20, "x")
    lathe("coatst", [(0.0, 0.0), (0.25, 0.0), (0.03, 0.05), (0.025, 1.85), (0.04, 1.9), (0.0, 1.92)], (-5.9, 0, 3.8), LEG, 16)
    lathe("bowler", [(0.0, 0.0), (0.2, 0.0), (0.22, 0.02), (0.14, 0.04), (0.13, 0.14), (0.08, 0.18), (0.0, 0.19)], (-5.75, 1.88, 3.8), pm("#1a1a1e", 0.4), 24)
    tube("coat", [(-5.9, 1.78, 3.8), (-5.72, 1.5, 3.72), (-5.7, 0.9, 3.75), (-5.8, 0.5, 3.7)], 0.17, cloth("#2a2a32"), taper=lambda f: 0.6 + f * 0.6)
    for k in range(3):
        K.cyl((5.9 - k * 0.38, 0.17, 4.9), 0.15, 0.34, pm("#c81e22", 0.4, 0.3), 18); K.cyl((5.9 - k * 0.38, 0.33, 4.9), 0.13, 0.02, pm("#d8c8a0", 0.9), 18)
    text("FIRE", (5.52, 0.62, 4.88), 0.11, pm("#f0e8d0", 0.6), 0, "sans", 0.002)
    K.box((5.52, 0.62, 4.94), (1.1, 0.16, 0.02), pm("#c81e22", 0.5), 0, 0.005)
    K.cyl((-6.1, 0.2, 4.6), 0.18, 0.4, wood("#9a7a4a", "#5a4428", 20, 0.8), 16)
    # ---------------- lights: green enamel pendants (warm), the map lit from above, cool fill from the door ----------------
    SH = pm("#1e4a2e", 0.3, 0.3); CORD = pm("#1a1a1a", 0.6)
    for x, z in ((-3.6, -2.0), (-3.6, 1.6), (3.6, -2.0), (3.6, 1.6), (0, -4.6), (0, 2.6)):
        lamp(K, x, 2.55, z, SH, CORD, 140)
    K.build()
    sp = spot((0, 3.2, 3.2), (0, 1.8, 5.5), 1600, (1.0, 0.8, 0.55), 70, 0.5, 0.3)
    area((0, 3.1, 1.2), (0, 0, 1.2), 300, (1.0, 0.72, 0.45), 4.0)
    area((0, 2.2, -5.8), (0, 1.4, 3), 260, (0.6, 0.72, 1.0), 3.0)              # cool fill from the doorway
    area((2.5, 3.0, 5.2), (0, 1.5, 4.0), 140, (0.75, 0.82, 1.0), 1.0)           # rim on Churchill from behind-right
    bg = bpy.context.scene.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1); bg.inputs[1].default_value = 0.3
    # cigar smoke hanging under the girders
    sm = smoke_mat("cabsmoke", "#b8b0a8", 0.05)
    for k in range(5):
        o = lib.blob(f"haze{k}", T(rnd.uniform(-4, 4), 2.85, rnd.uniform(-3, 4)), (rnd.uniform(1.0, 1.8), 0.18, rnd.uniform(0.6, 1.0)), sm, 0.08, k); o.visible_shadow = False
    return {}
