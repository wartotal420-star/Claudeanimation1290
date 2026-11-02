# The beer hall (shots 22-23), sets.ts buildBeerhall layout: hall x -10..10, z -6..12 (back wall z 12), three rows of
# long tables at z 1 / 4.6 / 8.2 (x +-3.5), the speaker's crate at (0, 0, 10.6), podium at z 11.5, banners at z 11.9.
# Characters stand among the tables (x -6..6, z 0.5..9), Hitler walks in from (-5, 0, 6) and climbs the crate.
# Look: a smoky Bavarian beer cellar - wood panelling, stencilled plaster, a vaulted beamed ceiling, wagon-wheel
# chandeliers (warm key), cool leaded windows on the back wall (rim), blue-white bunting, a bar with taps on the left.
import bpy, math, random
import lib
from lib import T
from . import kit_sbpw as K_
from .kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, stripes, paper, text, sign, poster, barrel, crate, stein, pretzel, R90

def build(M, D):
    random.seed(1920); K_.reset(); rnd = random.Random(22)
    K = K_.Kit("beerhall")
    FL = lib.parquet("bhfloor", "#7a4a2a", "#5e3a1e"); PL = grime("bhplaster", "#d8a868", 0.4, 3.0)
    PLANK = lib.brickmat("bhplank", "#6a3a1c", "#5a2e14", "#22100a", 1.0, 0.22, 8.0, 0.5)
    WD = wood("#5a3418", "#2a160a", 6); WDL = wood("#7a4a24", "#3e2210", 5); TB = wood("#9a6a3a", "#5a3a1a", 4, 0.45)
    BEER = pm("#e8a030", 0.15); FOAM = pm("#fff6e0", 0.9); GL = pm("#d8e0d8", 0.05); HOOP = iron("#2a2a2e")
    STEINC = [pm("#c8b48a", 0.4), pm("#8a6a4a", 0.45), pm("#d8d0c0", 0.3), pm("#5a6a8a", 0.35)]
    BREZ = K_.cached("brez", lambda: lib.bread("kbrez", "#a85a22"))
    # ---------------- room shell ----------------
    K.box((0, -0.05, 3), (21, 0.1, 19), FL, 0, 0)
    K.box((0, 5.05, 3), (21, 0.1, 19), grime("bhceil", "#d8bc88", 0.3), 0, 0)
    K.box((0, 2.5, 12.15), (21, 5, 0.3), PL, 0, 0)
    K.box((0, 2.5, -6.15), (21, 5, 0.3), PL, 0, 0)
    for sx in (-1, 1): K.box((sx * 10.15, 2.5, 3), (0.3, 5, 19), PL, 0, 0)
    # vaulted bays: heavy beams across + arched ribs along the side walls
    for k in range(7):
        z = -5 + k * 2.8
        K.box((0, 4.72, z), (20, 0.4, 0.34), WD, 0, 0.03)
        for sx in (-1, 1):
            K.box((sx * 9.8, 4.3, z), (0.5, 0.5, 0.34), WD, 0, 0.02, 0, sx * 0.785)  # knee brace
            K.box((sx * 9.88, 2.5, z), (0.24, 5, 0.3), WD, 0, 0.02)                 # wall post
    K.box((0, 4.6, 3), (0.3, 0.3, 19), WD, 0, 0.03)
    for sx in (-1, 1): K.box((sx * 6.5, 4.6, 3), (0.24, 0.24, 19), WD, 0, 0.02)
    # panelling to 1.6 m with raised panels, a painted stencil frieze, a plate shelf
    for (x, z, w, yaw) in ((0, 11.96, 20, 0.0), (-9.96, 3, 18, R90), (9.96, 3, 18, -R90)):
        ca, sa = math.cos(yaw), math.sin(yaw)
        if yaw == 0: K.box((x, 0.8, z), (w, 1.6, 0.08), PLANK, 0, 0.01)
        else: K.box((x, 0.8, z), (0.08, 1.6, w), PLANK, 0, 0.01)
        n = int(w / 1.0)
        for j in range(n):
            u = -w / 2 + 0.5 + j
            p = (x + u * ca, 0.85, z - u * sa)
            p = (p[0] - (0.05 if x > 5 else -0.05 if x < -5 else 0), 0.85, p[2] - (0.05 if yaw == 0 else 0))
            K.box(p, (0.8, 1.1, 0.03) if yaw == 0 else (0.03, 1.1, 0.8), WDL, 0, 0.012)
        if yaw == 0:
            K.box((x, 1.65, z - 0.08), (w, 0.08, 0.16), WD, 0, 0.01); K.box((x, 3.55, z - 0.04), (w, 0.35, 0.02), stripes("frz", "#9a2a1e", "#2a5a3a", 18, 0), 0, 0)
        else:
            K.box((x - math.copysign(0.08, x), 1.65, z), (0.16, 0.08, w), WD, 0, 0.01); K.box((x - math.copysign(0.04, x), 3.55, z), (0.02, 0.35, w), stripes("frz2", "#9a2a1e", "#2a5a3a", 18, 1), 0, 0)
    # ---------------- back wall: stage end ----------------
    for sx in (-1, 1): K.box((sx * 6.2, 2.3, 11.85), (5.6, 0.05, 0.28), WD, 0, 0.01)       # stein shelves
    for k in range(30):
        x = -8.6 + k * 0.6
        if abs(x) < 3.5: continue
        m = STEINC[k % 4]; K.cyl((x, 2.43, 11.85), 0.07, 0.22, m, 12); K.cyl((x, 2.56, 11.85), 0.075, 0.04, pewter(), 12)
        K.torus((x + 0.08, 2.44, 11.85), 0.05, 0.012, m, 10, 5, "z")
    K.box((0, 0.55, 11.5), (2.4, 1.1, 0.6), WD, 0, 0.02)              # podium
    K.box((0, 1.12, 11.5), (2.6, 0.06, 0.7), WDL, 0, 0.01)
    K.box((0, 0.6, 11.18), (2.42, 0.9, 0.02), cloth("#8a1a1e"), 0, 0)
    K.box((0, 1.3, 11.6), (0.7, 0.4, 0.35), WDL, 0, 0.01, -0.0)       # lectern on the podium
    K.box((0, 1.52, 11.55), (0.8, 0.04, 0.45), WD, 0, 0.005, 0.25)
    for k, x in enumerate((-2.6, 2.6)):
        K.box((x, 2.75, 11.92), (1.4, 2.3, 0.03), stripes("bhban", "#b0202a", "#8a1820", 26, 0), 0, 0)
        K.cyl((x, 3.92, 11.88), 0.03, 1.6, gold(), 8, "x"); K.box((x, 1.62, 11.9), (1.4, 0.05, 0.03), gold(), 0, 0)
    # the brewery's carved name board over the stage
    sign(K, (0, 4.15, 11.92), 4.6, 0.5, 0.0, "BÜRGERBRÄU", "#3a1e10", gold(), "serif", gold(), 0.08)
    for x in (-2.75, 2.75):  # carved crests
        K.cyl((x, 4.15, 11.9), 0.26, 0.06, pm("#2a5aa8", 0.4), 24, "z"); K.torus((x, 4.15, 11.86), 0.26, 0.03, gold(), 24, 6, "z")
        K.box((x, 4.15, 11.85), (0.42, 0.06, 0.02), pm("#f0ece0", 0.4), 0, 0, 0, 0.6)
    # Bavarian lozenge crest centred behind the speaker, flanked by two lantern sconces (back light on the stage)
    K.cyl((0, 2.75, 11.94), 0.66, 0.06, WD, 40, "z"); K.torus((0, 2.75, 11.9), 0.66, 0.04, gold(), 40, 8, "z")
    K.cyl((0, 2.75, 11.9), 0.58, 0.02, pm("#f2f0ea", 0.5), 40, "z")
    for i in range(-5, 6):
        for j in range(-5, 6):
            u, v = (i + j) * 0.075, (i - j) * 0.075
            if (i + j) % 2 == 0 and u * u + v * v < 0.5 ** 2: K.box((u, 2.75 + v, 11.885), (0.1, 0.1, 0.01), pm("#2a5ab0", 0.45), 0, 0, 0, math.pi / 4)
    text("GEGRÜNDET 1885", (0, 1.95, 11.92), 0.11, gold(), 0, "serif", 0.004)
    for x in (-1.25, 1.25):
        K.box((x, 2.55, 11.9), (0.1, 0.1, 0.1), brass(), 0, 0.01); K.box((x, 2.62, 11.75), (0.04, 0.04, 0.3), brass(), 0, 0)
        K.cyl((x, 2.75, 11.62), 0.1, 0.26, em("#ffb860", 9.0), 6, "y", 0.12); K.cyl((x, 2.93, 11.62), 0.14, 0.1, brass(), 6, "y", 0.03)
        lib.light("POINT", T(x, 2.75, 11.45), 60, (1.0, 0.62, 0.3), 0.08)
    # leaded windows (cool light from the street) with deep reveals and sills
    for sx in (-1, 1):
        x = sx * 6.6
        K.box((x, 2.75, 12.0), (1.5, 1.9, 0.04), K_.window_glow("bhwin", "#a8c4e8", 3.0), 0, 0)
        for q in range(6): K.box((x, 1.95 + q * 0.32, 11.97), (1.5, 0.02, 0.02), pm("#2a2a2a", 0.6), 0, 0)
        for q in range(4): K.box((x - 0.56 + q * 0.375, 2.75, 11.97), (0.02, 1.9, 0.02), pm("#2a2a2a", 0.6), 0, 0)
        K_._frame(K, (x, 2.75, 11.95), 1.5, 1.9, 0.0, WD, 0.14, 0.12)
        K.box((x, 1.72, 11.86), (1.8, 0.08, 0.3), WD, 0, 0.01)
        for dx in (-0.95, 0.95): K.box((x + dx, 2.75, 11.88), (0.35, 2.1, 0.04), cloth("#6a1e1e"), 0, 0.005)
        lib.light("AREA", T(x, 2.75, 11.7), 120, (0.65, 0.78, 1.0), 1.5, (math.radians(90), 0, math.radians(180)), 1.9)
    # antler trophies and framed paintings
    for x in (-8.6, -4.6, 4.6, 8.6):
        antlers(K, (x, 3.05, 11.95), WD)
    # ---------------- left wall: the bar ----------------
    K.box((-8.6, 0.55, 3.5), (0.8, 1.1, 7.0), WD, 0, 0.02)
    K.box((-8.55, 1.13, 3.5), (1.0, 0.06, 7.2), WDL, 0, 0.01)
    for j in range(7): K.box((-8.18, 0.55, 0.5 + j), (0.03, 0.8, 0.8), WDL, 0, 0.01)
    K.box((-8.2, 0.08, 3.5), (0.08, 0.06, 7.0), brass(), 0, 0.005)     # foot rail
    for j in range(6):   # taps on the counter + steins waiting
        z = 0.6 + j * 1.15
        K.cyl((-8.75, 1.35, z), 0.04, 0.4, brass(), 10); K.cyl((-8.6, 1.5, z), 0.025, 0.3, brass(), 8, "x"); K.cyl((-8.45, 1.42, z), 0.02, 0.12, brass(), 8)
        stein(K, (-8.35, 1.16, z + 0.35), BEER, GL, FOAM, GL)
    for j in range(4):   # barrels racked behind the bar with spigots
        z = 0.8 + j * 1.6
        barrel(K, (-9.55, 0.45, z), 0.42, 0.95, wood("#8a5a32", "#4a2c18", 3), HOOP, "x")
        barrel(K, (-9.55, 1.32, z + 0.8 if j < 3 else z), 0.36, 0.8, wood("#8a5a32", "#4a2c18", 3), HOOP, "x")
        K.cyl((-9.05, 0.45, z), 0.03, 0.12, brass(), 8, "x")
    K.box((-9.9, 2.3, 4.8), (0.1, 0.9, 1.6), pm("#1e2420", 0.9), 0, 0.01)   # chalk board
    K_._frame(K, (-9.83, 2.3, 4.8), 1.6, 0.9, -R90, WDL, 0.06, 0.05)
    for i, (s, sz) in enumerate((("HEUTE", 0.13), ("Weißwurst · Brezn", 0.075), ("1 Maß Bier", 0.09))):
        text(s, (-9.83, 2.55 - i * 0.22, 4.8), sz, pm("#efece4", 0.9), -R90, "serif", 0.001, fit=1.4)
    for j, zc in enumerate((-0.8, 2.0, 7.6)):   # shelves of steins and bottles over the bar
        K.box((-9.85, 2.9, zc), (0.3, 0.04, 1.6), WD, 0, 0.005)
        for q in range(6): K.cyl((-9.85, 3.02, zc - 0.625 + q * 0.25), 0.05, 0.2, STEINC[(q + j) % 4] if q % 2 else pm(["#2a5a2a", "#6a2a1a"][j % 2], 0.15), 10)
    # ---------------- right wall: barrels, coat rack, a side door ----------------
    for k in range(3):
        for j in range(2): barrel(K, (9.3, 0.42 + j * 0.8, -2 + k * 1.4), 0.38, 0.95, wood("#8a5a32", "#4a2c18", 3), HOOP, "x")
    K.box((9.9, 1.9, 5.0), (0.06, 0.06, 2.4), WD, 0, 0.005)
    for q in range(7):
        z = 3.9 + q * 0.36; K.cyl((9.85, 1.85, z), 0.015, 0.2, brass(), 6, "x")
        if q % 2 == 0: K.cyl((9.78, 2.02, z), 0.17, 0.04, cloth(["#3a3a3e", "#5a4a3a", "#2a2a2e"][q % 3]), 14); K.cyl((9.78, 2.1, z), 0.1, 0.13, cloth(["#3a3a3e", "#5a4a3a", "#2a2a2e"][q % 3]), 14)
        else: K.box((9.8, 1.35, z), (0.1, 0.95, 0.3), cloth(["#4a3a2a", "#2a3a4a", "#3a3a2a"][q % 3]), 0, 0.03)
    K.box((9.86, 1.1, 10.4), (0.06, 2.2, 1.1), WDL, 0, 0.01); K.box((9.9, 1.15, 10.4), (0.06, 2.35, 1.25), WD, 0, 0.01)
    K.cyl((9.82, 1.05, 10.0), 0.03, 0.06, brass(), 8, "x")
    sign(K, (9.86, 2.55, 10.4), 1.0, 0.26, R90, "AUSGANG", "#1e2a1e", None, "sans", None, 0.03)
    for (z, c1, c2) in ((2.0, "#c87a4a", "#4a6a3a"), (7.6, "#6a8ab0", "#8a6a4a")):
        painting(K, (9.94, 2.5, z), 1.0, 0.75, c1, c2, R90)
    poster(K, (9.94, 2.35, -4.0), 0.6, 0.85, R90, "#e8c84a", [("BOCKBIER", 0.12), ("FEST", 0.12), ("SAMSTAG", 0.06)], "#3a1e10", None, "sans")
    poster(K, (-9.9, 2.35, 7.6), 0.6, 0.85, -R90, "#f0e6cc", [("VERSAMM-", 0.08), ("LUNG", 0.1), ("HEUTE 20 UHR", 0.055)], "#c8202a", None, "sans")
    # ---------------- long tables loaded with beer and food ----------------
    for row in range(3):
        for sx in (-1, 1):
            x, z = sx * 3.5, 1 + row * 3.6
            K.box((x, 0.78, z), (3.4, 0.07, 1.05), TB, 0, 0.02)
            for dx in (-1.35, 1.35):
                K.box((x + dx, 0.38, z), (0.1, 0.76, 0.7), WD, 0, 0.01); K.box((x + dx, 0.06, z), (0.14, 0.12, 0.9), WD, 0, 0.01)
            K.box((x, 0.25, z), (2.6, 0.08, 0.06), WD, 0, 0.005)
            for dz in (-0.85, 0.85):
                K.box((x, 0.45, z + dz), (3.3, 0.06, 0.32), TB, 0, 0.01)
                for dx in (-1.35, 1.35): K.box((x + dx, 0.21, z + dz), (0.06, 0.42, 0.26), WD, 0, 0)
            for k in range(7):
                px, pz = x - 1.45 + k * 0.48 + rnd.uniform(-0.06, 0.06), z + (0.27 if k % 2 else -0.27)
                if rnd.random() < 0.75: stein(K, (px, 0.815, pz), BEER, GL, FOAM, GL)
                else:
                    K.cyl((px, 0.815 + 0.11, pz), 0.07, 0.22, STEINC[k % 4], 12); K.cyl((px, 0.815 + 0.235, pz), 0.073, 0.03, pewter(), 12)
                    K.torus((px + 0.08, 0.93, pz), 0.05, 0.013, STEINC[k % 4], 10, 5, "z")
            for k in range(3):   # plates with pretzels, radish, sausages
                px = x - 1.0 + k * 1.0; pz = z + rnd.uniform(-0.08, 0.08)
                K.cyl((px, 0.82, pz), 0.14, 0.012, pm("#f4f0e6", 0.25), 20)
                if k == 1: pretzel(K, (px, 0.826, pz), BREZ, 1.4, rnd.uniform(0, 3))
                elif k == 0:
                    for q in range(2): K.cyl((px - 0.04 + q * 0.08, 0.84, pz), 0.025, 0.16, pm("#e8d8c0", 0.5), 10, "x", None, rnd.uniform(-0.3, 0.3))
                else:
                    for q in range(4): K.sphere((px + rnd.uniform(-0.06, 0.06), 0.85, pz + rnd.uniform(-0.06, 0.06)), 0.028, pm("#c82040", 0.3), 8)
            K.cyl((x + 0.5, 0.86, z), 0.04, 0.1, pm("#3a5a2a", 0.1), 10)      # candle in a bottle
            K.cyl((x + 0.5, 0.97, z), 0.02, 0.12, pm("#f4ecd8", 0.6), 8); K.sphere((x + 0.5, 1.05, z), 0.015, em("#ffb050", 30), 6)
            K.cyl((x - 0.5, 0.82, z + 0.1), 0.07, 0.015, pm("#8a8a90", 0.3, 0.8), 12)   # ashtray + cigar
            K.cyl((x - 0.46, 0.835, z + 0.1), 0.012, 0.11, pm("#5a3018", 0.7), 6, "x", None, 0.4)
            for q in range(4): K.cyl((x - 1.2 + q * 0.8, 0.818, z - 0.3), 0.05, 0.004, pm(["#f0ece0", "#2a5aa8"][q % 2], 0.6), 12)  # coasters
            if (row + sx) % 2: K.cyl((x + 1.2, 0.82, z + 0.25), 0.17, 0.02, cloth("#3a3a3e"), 14); K.cyl((x + 1.2, 0.89, z + 0.25), 0.1, 0.12, cloth("#3a3a3e"), 14)
    # the speaker's beer crate, stencilled
    crate(K, (0, 0.27, 10.6), 0.6, wood("#a07a4a", "#5a3a1a", 12, 0.8), 0.0, wood("#7a5a32", "#3a2a12", 12, 0.8))
    text("BÜRGERBRÄU", (0, 0.29, 10.285), 0.07, pm("#2a1a10", 0.8), 0, "sans", 0.002)
    for i in range(4): K.cyl((0.45 + i * 0.13, 0.13, 10.2 + (i % 2) * 0.1), 0.035, 0.26, pm("#3a5a2a", 0.1), 10)   # empty bottles
    # ---------------- blue-white bunting and wagon-wheel chandeliers ----------------
    for z in (2.6, 6.4):
        n = 30
        for i in range(n):
            t0, t1 = i / n, (i + 0.8) / n
            x0, x1 = -9.6 + 19.2 * t0, -9.6 + 19.2 * t1
            y0 = 4.35 - 0.6 * math.sin(math.pi * t0); y1 = 4.35 - 0.6 * math.sin(math.pi * t1)
            K.quad([(x0, y0, z), (x1, y1, z), ((x0 + x1) / 2, (y0 + y1) / 2 - 0.32, z)], pm("#2a5ab0" if i % 2 else "#f2f0ea", 0.8))
        K.cyl((0, 4.35 - 0.3, z), 0.006, 19.2, pm("#3a3a3a", 0.8), 4, "x")
    for row in range(3):
        for sx in (-1, 1):
            x, z = sx * 3.5, 1 + row * 3.6
            chandelier(K, (x, 3.45, z), WD)
            lib.light("POINT", T(x, 3.3, z), 170, (1.0, 0.66, 0.36), 0.35)
    # wall sconces on the posts: a ring of small warm sources
    for k in range(1, 7):
        z = -5 + k * 2.8
        for sx in (-1, 1):
            if sx < 0 and 0 < z < 7.5: continue
            x = sx * 9.7
            K.box((x, 2.55, z), (0.12, 0.2, 0.08), brass(), 0, 0.01)
            K.cyl((x - sx * 0.12, 2.75, z), 0.08, 0.16, em("#ffc070", 8.0), 10, "y", 0.11)
            lib.light("POINT", T(x - sx * 0.2, 2.75, z), 30, (1.0, 0.65, 0.35), 0.08)
    # a green tiled stove in the back-left corner, an upright piano back-right, round tables by the walls
    TILE = K_.brick("bhtile", "#2a6a4a", "#24604a", "#1a2a20", 7.0, 0.5, 0.5, 0.25)
    K.box((-8.9, 1.1, 10.9), (1.2, 2.2, 1.2), TILE, 0, 0.03); K.box((-8.9, 2.28, 10.9), (1.35, 0.16, 1.35), TILE, 0, 0.03)
    K.box((-8.9, 0.06, 10.9), (1.4, 0.12, 1.4), pm("#3a3a3a", 0.5), 0, 0.01); K.box((-8.28, 0.75, 10.9), (0.04, 0.4, 0.45), brass(), 0, 0.01)
    K.cyl((-8.9, 3.6, 11.4), 0.1, 2.6, iron(), 12)
    K.box((8.3, 0.65, 11.55), (1.5, 1.3, 0.6), wood("#2a160c", "#120804", 8, 0.25), 0, 0.02)
    K.box((8.3, 0.86, 11.15), (1.4, 0.06, 0.25), pm("#f4f0e6", 0.3), 0, 0.005)
    for q in range(20): K.box((7.66 + q * 0.07, 0.9, 11.12), (0.025, 0.03, 0.14), pm("#141414", 0.3), 0, 0)
    K.box((8.3, 1.32, 11.6), (1.55, 0.05, 0.65), wood("#2a160c", "#120804", 8, 0.25), 0, 0.01)
    for q in range(2): K.cyl((7.9 + q * 0.8, 1.36, 11.6), 0.06, 0.12, brass(), 10); K.sphere((7.9 + q * 0.8, 1.46, 11.6), 0.02, em("#ffb050", 30), 6)
    K.box((8.3, 1.15, 11.22), (0.5, 0.35, 0.02), paper("#efe4c8"), 0, 0, 0.2)
    K.cyl((8.3, 0.25, 10.75), 0.22, 0.05, cloth("#6a1e1e"), 16); K.cyl((8.3, 0.12, 10.75), 0.03, 0.22, wood("#2a160c", "#120804", 8, 0.25), 8)
    for (x, z) in ((-6.5, 10.6), (6.2, 10.4), (-8.2, -3.8), (8.0, 4.4)):
        K.cyl((x, 0.75, z), 0.5, 0.05, TB, 24); K.cyl((x, 0.38, z), 0.06, 0.72, WD, 10); K.cyl((x, 0.03, z), 0.3, 0.05, WD, 16)
        for a in range(3):
            aa = a * 2.1 + x; cx, cz = x + 0.75 * math.cos(aa), z + 0.75 * math.sin(aa)
            K.box((cx, 0.45, cz), (0.38, 0.05, 0.38), WDL, -aa, 0.01)
            for dx in (-0.15, 0.15):
                for dz in (-0.15, 0.15): K.box((cx + dx, 0.22, cz + dz), (0.04, 0.44, 0.04), WD, 0, 0)
            K.box((cx + 0.2 * math.cos(aa), 0.75, cz + 0.2 * math.sin(aa)), (0.05, 0.6, 0.38), WDL, -aa, 0.01)
        stein(K, (x + 0.15, 0.775, z), BEER, GL, FOAM, GL); stein(K, (x - 0.2, 0.775, z + 0.1), BEER, GL, FOAM, GL)
    for i in range(6):   # crates of empties beside the podium
        crate(K, (-1.9 - (i % 2) * 0.62, 0.22 + (i // 2) * 0.42, 11.4), 0.55, wood("#a07a4a", "#5a3a1a", 12, 0.8), 0.05 * i)
    # warm fill from the bar and the front, a cool rim from the windows (above)
    lib.light("AREA", T(-8.4, 3.3, 3.5), 220, (1.0, 0.62, 0.32), 1.2, (0, 0, 0), 6.0)
    lib.light("AREA", T(0, 4.0, -5.0), 200, (1.0, 0.72, 0.5), 6, (math.radians(70), 0, 0))
    lib.light("SPOT", T(0, 4.6, 6.5), 700, (1.0, 0.75, 0.45), 0.4, (math.radians(35), 0, 0))   # stage key onto the crate
    K.build()
    W = bpy.context.scene.world; bg = W.node_tree.nodes.get("Background")
    if bg: bg.inputs[0].default_value = (0.03, 0.02, 0.015, 1); bg.inputs[1].default_value = 0.3
    return {}

def pewter(): return K_.cached("pewter", lambda: lib.principled("kpewter", (0.55, 0.55, 0.56), 0.3, 0.9))

def chandelier(K, c, WD):
    x, y, z = c; I = iron("#1e1a18")
    K.torus((x, y, z), 0.62, 0.05, WD, 28, 8, "y")
    for a in range(8):
        aa = a * math.pi / 4; K.box((x + 0.31 * math.cos(aa), y, z + 0.31 * math.sin(aa)), (0.62, 0.04, 0.04), WD, -aa, 0)
    K.cyl((x, y, z), 0.09, 0.14, WD, 12)
    for a in range(3):
        aa = a * 2 * math.pi / 3; K.box((x + 0.3 * math.cos(aa), y + 0.75, z + 0.3 * math.sin(aa)), (0.012, 1.55, 0.012), I, 0, 0, 0.0, 0.0)
    K.cyl((x, 4.6, z), 0.012, 0.6, I, 4)
    for a in range(8):
        aa = a * math.pi / 4 + 0.39; px, pz = x + 0.62 * math.cos(aa), z + 0.62 * math.sin(aa)
        K.cyl((px, y + 0.07, pz), 0.045, 0.04, brass(), 10)
        K.cyl((px, y + 0.15, pz), 0.02, 0.12, pm("#f4ecd8", 0.5), 8)
        K.sphere((px, y + 0.24, pz), 0.035, em("#ffb860", 25), 8, (1, 1.6, 1))

def antlers(K, c, WD):
    x, y, z = c; BONE = pm("#e8dcc0", 0.5)
    K.box((x, y - 0.1, z - 0.02), (0.36, 0.48, 0.04), WD, 0, 0.02)
    K.sphere((x, y - 0.05, z - 0.08), 0.08, pm("#d8ccb0", 0.5), 10, (1.3, 0.8, 0.8))
    for s in (-1, 1):
        K.box((x + s * 0.2, y + 0.18, z - 0.1), (0.035, 0.5, 0.035), BONE, 0, 0.0, 0, -s * 0.5)
        K.box((x + s * 0.38, y + 0.42, z - 0.1), (0.03, 0.35, 0.03), BONE, 0, 0.0, 0, -s * 0.15)
        for t in range(3):
            K.box((x + s * (0.22 + t * 0.08), y + 0.2 + t * 0.12, z - 0.1), (0.025, 0.2, 0.025), BONE, 0, 0.0, 0, s * 0.5)

def painting(K, c, w, h, c1, c2, yaw=0.0):
    """a framed oil landscape: sky, hills, a field, a little house"""
    x, y, z = c; ca, sa = math.cos(yaw), math.sin(yaw); nrm = (-sa, 0, -ca)
    def at(u, v, d): return (x + u * ca + nrm[0] * d, y + v, z - u * sa + nrm[2] * d)
    K.box(at(0, 0, 0), (w, h, 0.03), pm(c1, 0.6), yaw, 0)
    K.box(at(0, -h * 0.22, 0.017), (w, h * 0.56, 0.005), pm(c2, 0.7), yaw, 0)
    K.box(at(-w * 0.18, -h * 0.05, 0.02), (w * 0.4, h * 0.22, 0.005), pm("#3a5a3a", 0.7), yaw, 0, 0, 0.2)
    K.box(at(w * 0.2, -h * 0.08, 0.023), (w * 0.12, h * 0.14, 0.005), pm("#e8e0d0", 0.6), yaw, 0)
    K.box(at(w * 0.2, h * 0.01, 0.024), (w * 0.15, h * 0.06, 0.005), pm("#8a2a1e", 0.6), yaw, 0)
    K.sphere(at(w * 0.3, h * 0.3, 0.02), w * 0.06, pm("#f0d890", 0.5), 8, (1, 1, 0.2))
    K_._frame(K, at(0, 0, 0.02), w, h, yaw, gold(), 0.08, 0.06)
