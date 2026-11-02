# Chapter 5: a deep Underground platform used as an air-raid shelter, autumn 1940 (Aldwych). Families sleep on the
# platform under the curved tiled tunnel; bunks, blankets, a tea trolley, posters and roundels.
# Layout (three coords): the tunnel runs along z (-30..40); its circle centre (0, 1.0), radius 3.8 (x -3.8..3.8);
# the platform top y 0 for x -3.7..0.9 (edge x 0.9, white line); the track pit x 0.9..3.6 at y -1.05 with rails.
# The curved back wall rises behind the platform from x -3.7. Keep clear: platform x -3.0..0.6, z -6..14 (people on
# blankets, sitting, lying); bunks stand at x -3.1 at z -10, 16, 22.
import bpy, math, random
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, crate, barrel, stripes, R90
from .c05_kit import (area, point, spot, lathe, tube, worn, mat_once, cached)

def tiles():
    return K_.brick("c5tile", "#e8e0c8", "#e0d8bc", "#9a9280", 6.0, 0.5, 0.5, 0.25)

def build(M, D):
    random.seed(1940); K_.reset(); rnd = random.Random(14)
    K = Kit("tube"); TL = tiles(); BAND = K_.brick("c5band", "#2a5a3a", "#24503a", "#1a2a20", 6.0, 0.5, 0.5, 0.25)
    TRIM = pm("#5a2a1e", 0.4)
    R, cy0, L, zc = 3.8, 1.0, 72.0, 5.0
    for k in range(40):                                  # the tunnel shell (tiles), with a green band on the platform side
        a0 = math.radians(-60 + k * 6.0); a1 = a0 + math.radians(6.0); a = (a0 + a1) / 2
        x, y = -R * math.cos(a), cy0 + R * math.sin(a)
        if y < -1.0 or (x > 1.0 and y < 0.5): continue
        w = 2 * R * math.sin(math.radians(3.0)) + 0.02
        m = BAND if (x < 0 and 2.35 < y < 2.75) else TL
        K.box((x * 1.02, y, zc), (0.12, w, L), m, 0, 0.0, 0.0, -a)
    K.box((-1.4, -0.05, zc), (4.8, 0.1, L), K_.brick("c5plat", "#7a7468", "#6e685e", "#4a4640", 1.8, 0.5, 0.5, 0.6), 0, 0.0)
    K.box((0.86, 0.006, zc), (0.12, 0.012, L), pm("#e8e4d8", 0.6), 0, 0.0)
    K.box((0.95, -0.5, zc), (0.1, 1.0, L), pm("#4a4640", 0.8), 0, 0.0)
    K.box((2.3, -1.1, zc), (3.0, 0.1, L), pm("#2a2622", 0.9), 0, 0.0)
    for x in (1.7, 3.15): K.box((x, -0.98, zc), (0.08, 0.12, L), pm("#8a8a90", 0.25, 1.0), 0, 0.005)
    K.box((2.42, -0.98, zc), (0.12, 0.08, L), pm("#6a5a4a", 0.6, 0.6), 0, 0.005)
    for k in range(int(L / 0.7)): K.box((2.42, -1.04, zc - L / 2 + k * 0.7), (2.4, 0.06, 0.25), wood("#3a2a1e", "#1e1610", 6, 0.9), 0, 0.0)
    # roundels, posters in frames, an exit sign, benches, bunks, the tea trolley
    def roundel(z, label):
        x = -3.56; y = 1.65
        K.cyl((x, y, z), 0.55, 0.04, pm("#c81e22", 0.35), 32, "x"); K.cyl((x + 0.02, y, z), 0.37, 0.04, pm("#f0ece0", 0.4), 32, "x")
        K.box((x + 0.05, y, z), (0.04, 0.22, 1.5), pm("#1e2a6a", 0.4), 0, 0.005)
        text(label, (x + 0.08, y, z), 0.14, pm("#f0ece0", 0.4), -R90, "sans", 0.002, fit=1.3)
    for z in (-8, 6, 20): roundel(z, "ALDWYCH")
    PST = [("#2a4a8a", [("TRAVEL", 0.12), ("BY TUBE", 0.12), ("IT'S QUICKER", 0.07)], "#f4ecd8"), ("#e8c030", [("HOLIDAYS", 0.1), ("AT HOME", 0.12), ("1940", 0.08)], "#1a1a1a"),
           ("#c81e22", [("KEEP", 0.14), ("CALM", 0.14), ("CARRY ON", 0.1)], "#f4ecd8"), ("#3a6a3a", [("DIG FOR", 0.12), ("VICTORY", 0.12)], "#f4ecd8"),
           ("#f0e8d0", [("BOVRIL", 0.16), ("PREVENTS THAT", 0.06), ("SINKING FEELING", 0.06)], "#a81e22"), ("#5a2a6a", [("PICCADILLY", 0.09), ("CIRCUS", 0.1), ("THEATRES", 0.07)], "#f4ecd8")]
    for k in range(9):
        z = -12 + k * 4.0
        if k in (1, 5): continue
        bg, lines, ink = PST[k % len(PST)]
        K.box((-3.56, 1.6, z), (0.05, 1.0, 0.75), wood("#3a2214", "#1a0e06", 8, 0.4), 0, 0.01)
        poster(K, (-3.52, 1.6, z), 0.66, 0.9, -R90, bg, lines, ink, None, "sans")
    sign(K, (-3.4, 2.1, 12), 1.4, 0.3, -R90, "WAY OUT", "#1e2a6a", pm("#f0ece0", 0.4), "sans", None, 0.03)
    BW = wood("#6a4428", "#3a2414", 6, 0.5); ST = pm("#3a4a3a", 0.5, 0.4)
    for z in (-10, 16, 22):                               # three-tier bunks (steel frame, canvas)
        for sd in (-0.95, 0.95):
            K.box((-3.1, 1.1, z + sd), (0.06, 2.2, 0.06), ST, 0, 0.005); K.box((-2.3, 1.1, z + sd), (0.06, 2.2, 0.06), ST, 0, 0.005)
        for t in range(3):
            K.box((-2.7, 0.35 + t * 0.75, z), (0.8, 0.06, 1.95), cloth(("#6a5a4a", "#4a5a6a", "#7a4a3a")[t]), 0, 0.02)
            K.box((-2.75, 0.43 + t * 0.75, z + 0.1), (0.65, 0.12, 1.5), cloth(("#a83a2a", "#3a5a8a", "#8a7a5a", "#5a7a4a")[(t + z) % 4]), 0.03, 0.05)
    for k, z in enumerate((-14, 26)):
        K.box((-3.1, 0.45, z), (0.5, 0.06, 2.0), BW, 0, 0.01); K.box((-3.32, 0.75, z), (0.06, 0.6, 2.0), BW, 0, 0.01)
    # blankets, pillows, suitcases, bags, thermos flasks, a birdcage, gas mask boxes scattered along the platform
    BLK = ["#8a3a2a", "#3a5a7a", "#7a6a4a", "#4a6a4a", "#9a7a5a", "#5a3a5a", "#a8584a", "#2a4a6a"]
    for k in range(24):
        z = -14 + k * 1.6 + rnd.uniform(-0.3, 0.3); x = rnd.uniform(-2.8, -0.6)
        K.box((x, 0.03, z), (rnd.uniform(1.2, 1.8), 0.06, rnd.uniform(0.8, 1.2)), stripes(f"blk{k % 4}", BLK[k % 8], BLK[(k + 3) % 8], 18, 0) if k % 3 == 0 else cloth(BLK[k % 8]), rnd.uniform(-0.3, 0.3), 0.04)
        if k % 2: K.box((x - 0.4, 0.1, z + rnd.uniform(-0.3, 0.3)), (0.4, 0.12, 0.3), cloth("#e8e0d0"), rnd.uniform(-0.3, 0.3), 0.06)
        if k % 3 == 1: K.box((-3.35, 0.22, z), (0.25, 0.42, 0.6), pm(("#6a3a1e", "#3a2a1e", "#7a5a3a")[k % 3], 0.6), 0, 0.03)
        if k % 4 == 2: K.box((-3.4, 0.12, z + 0.5), (0.15, 0.22, 0.2), pm("#8a7a5a", 0.8), 0.2, 0.01)
        if k % 5 == 3: K.cyl((x + 0.5, 0.15, z - 0.4), 0.05, 0.3, pm(("#2a4a7a", "#7a2a22")[k % 2], 0.3, 0.3), 12)
    lathe("cage", [(0.0, 0.0), (0.15, 0.0), (0.15, 0.3), (0.08, 0.42), (0.0, 0.45)], (-3.3, 0.45, -14), brass(), 12, cap=False)
    K.box((-2.0, 0.5, -3.5), (1.0, 0.06, 0.6), pm("#6a6a60", 0.5, 0.4), 0, 0.01)              # tea trolley with urn and cups
    K.box((-2.0, 0.2, -3.5), (1.0, 0.04, 0.6), pm("#6a6a60", 0.5, 0.4), 0, 0.01)
    for dx in (-0.45, 0.45):
        for dz in (-0.25, 0.25): K.cyl((-2.0 + dx, 0.35, -3.5 + dz), 0.02, 0.7, pm("#6a6a60", 0.5, 0.4), 6)
    K.cyl((-2.2, 0.75, -3.5), 0.18, 0.45, pm("#b8b8bc", 0.2, 1.0), 20); K.sphere((-2.2, 0.98, -3.5), 0.06, brass(), 10)
    for k in range(6): K.cyl((-1.75 + (k % 3) * 0.12, 0.57, -3.65 + (k // 3) * 0.15), 0.035, 0.07, pm("#f2ece0", 0.3), 12)
    text("W.V.S. TEA", (-2.0, 0.42, -3.81), 0.07, pm("#f0ece0", 0.5), 0, "sans", 0.001)
    K.box((-2.0, 0.42, -3.8), (0.9, 0.12, 0.01), pm("#2a4a2a", 0.6), 0, 0.0)
    # ceiling lamps and conduits
    for k in range(10):
        z = -15 + k * 5.5
        K.cyl((-0.5, 4.1, z), 0.008, 0.6, pm("#1a1a1a", 0.6), 6); K.cyl((-0.5, 3.75, z), 0.22, 0.12, pm("#e8e4d8", 0.3, 0.3), 16, "y", 0.04)
        K.sphere((-0.5, 3.65, z), 0.07, em("#ffd8a0", 18.0), 10)
        point((-0.5, 3.55, z), 70, (1.0, 0.72, 0.42), 0.06)
    for x in (-2.2, 1.6): K.cyl((x, 4.4 if x < 0 else 4.45, zc), 0.05, L, pm("#3a3a3a", 0.5, 0.5), 8, "z")
    K.build()
    area((3.5, 1.2, -32), (0, 1.0, 0), 300, (0.5, 0.65, 1.0), 4)           # cool light down the tunnel mouth
    area((2.8, 1.6, 5), (-3, 0.6, 5), 180, (1.0, 0.75, 0.5), 6, 2)          # warm fill across the platform
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.01, 0.012, 1)
    return {}
