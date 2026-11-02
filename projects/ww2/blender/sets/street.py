# A 1920s German street (shots 17, 19, 20, 24, 25, 27, 28) in the three.js layout of sets.ts buildStreet:
# road x -6..6 (cobbles), sidewalks |x| 6..10 (+0.15), houses |x| 10..16 every 7 m in z from -12, lamps at x +-5.6,
# the factory gate at x 6, z 24.5..27.5, the speaker's crate at (0, 0, 34.2), the balcony building at z 44.5..48.
# night = warm windows + lanterns + blue moon; gloom = overcast grey day.
# Keep clear (characters stand there): road |x| < 5 everywhere; right sidewalk x 6.5..8.3, z 11..24 (dole queue,
# shot 19); left sidewalk x -8.8..-6.3, z 14..23 (family, shot 27); square z 24..43, |x| < 5 (crowds, torches);
# balcony top (0, 6.3, 45.3); the end facade z 45.92 (shadow card, shot 28) -> facade relief there stays < 8 cm;
# the padlock card at (5.98, 1.45, 26) (shot 25) -> nothing in front of the gate.
import bpy, math, random
import lib
from lib import T
from . import kit_sbpw as K_
from .kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, stripes, paper, text, sign, poster, barrel, crate, R90

D90 = R90
LEFT = [("BÄCKEREI MÜLLER", "bread", "#5a2a1e"), ("APOTHEKE", "bottles", "#1e3a2a"), ("TANZ-CAFÉ ODEON", "cafe", "#3a1030"),
        ("UHRMACHER BRANDT", "clocks", "#1e2a4a"), ("BUCHHANDLUNG", "books", "#2a1e14"), ("SCHNEIDEREI", "cloth", "#1e3a3a"),
        ("METZGEREI HAHN", "meat", "#6a1e1e"), ("GASTHAUS ZUM LÖWEN", "beer", "#2a3a1e"), ("ZEITUNGEN · TABAK", "papers", "#1e1e2a")]
RIGHT = [("KOLONIALWAREN", "jars", "#2a4a3a"), ("HUTMACHER", "hats", "#3a1e1e"), ("KONDITOREI", "cafe", "#4a2a3a"),
         ("FAHRRÄDER", "wheels", "#1e2a3a"), ("PFANDLEIHE", "pawn", "#3a2a10"), None, None,
         ("KAFFEEHAUS", "cafe", "#1e3a2a"), ("BIERSTUBE", "beer", "#3a1e10")]
WALLC = ["#d89a5a", "#8aa8c0", "#e0c070", "#c87860", "#9ab878", "#d8b0a0", "#b8c8d0", "#e0a878", "#a8a0c8"]
POSTERS = [("#e8c84a", [("TANZ", 0.2), ("HEUTE ABEND", 0.09), ("JAZZ-KAPELLE", 0.07)], "#c8202a", "#1a1a1a"),
           ("#c8202a", [("KINO", 0.2), ("METROPOLIS", 0.1), ("UFA-PALAST", 0.07)], "#1a1a1a", "#f4ecd8"),
           ("#f0e6cc", [("ARBEIT", 0.14), ("UND BROT!", 0.12), ("VERSAMMLUNG 20 UHR", 0.055)], "#c8202a", "#1a1a1a"),
           ("#2a5aa8", [("ZIRKUS", 0.17), ("BUSCH", 0.12), ("TÄGLICH 8 UHR", 0.06)], "#e8c84a", "#f4ecd8"),
           ("#3a8a4a", [("KAFFEE", 0.16), ("HAG", 0.14), ("SCHONT DAS HERZ", 0.055)], "#f0e6cc", "#f4ecd8"),
           ("#e8e0c8", [("WÄHLT!", 0.18), ("LISTE 4", 0.11), ("FÜR FREIHEIT", 0.06)], "#2a5aa8", "#1a1a1a"),
           ("#d86a2a", [("SCHOKOLADE", 0.11), ("SARRASANI", 0.08), ("NUR 20 PF.", 0.07)], "#3a1e10", "#f4ecd8")]

def build(M, D):
    random.seed(1929); K_.reset()
    night = D["light"] == "night"; sid = D.get("id", 0)
    K = K_.Kit("street"); rnd = random.Random(7)
    # ---------------- materials ----------------
    COB = K_.wet_cobbles("cob", "#6e6a7a", "#4a4656", 0.9 if night else 0.55, 4.5)
    SLAB = lib.brickmat("slab", "#8e887e", "#7e786e", "#4a4640", 1.6, 0.5, 0.5, 0.6)
    GRAN = pm("#8a8680", 0.7); STONE = grime("stone", "#c8bca4", 0.3); STONE_D = grime("stoned", "#9a8e7c", 0.35)
    TRIM = grime("trim", "#f0e6d0", 0.18); ROOF = K_.brick("roof", "#7a3a30", "#5e2c26", "#2a1a18", 7, 0.3, 0.14, 0.7)
    SLATE = K_.brick("slate", "#3a4250", "#2e3440", "#1a1e26", 8, 0.35, 0.16, 0.6)
    BRK = K_.brick("stbrick", "#a0503a", "#7a3428", "#4a3a34", 5.0); IRONM = iron()
    if night:
        WINS = [K_.window_glow("w1", "#ffb060", 2.6), K_.window_glow("w2", "#ff9850", 1.8), K_.window_glow("w3", "#ffd090", 3.2), K_.window_glow("w4", "#ff8a6a", 1.5)]
        DARKW = pm("#141a28", 0.12, 0.2); SHOPG = K_.window_glow("shop", "#ffa850", 2.4); LANT = em("#ffc070", 14.0)
    else:
        WINS = [pm("#3a4a5e", 0.06, 0.3), pm("#4a5a6a", 0.08, 0.3), pm("#2e3a4a", 0.06, 0.3)]
        DARKW = pm("#2a3444", 0.08, 0.3); SHOPG = K_.window_glow("shopd", "#e08a40", 0.75); LANT = pm("#e8e4d8", 0.15)
    CURT = [cloth("#e8dcc0"), cloth("#a82a2a"), cloth("#3a6a4a"), cloth("#d8b860")]
    # ---------------- ground ----------------
    K.box((0, -0.05, 20), (12.2, 0.1, 92), COB, 0, 0)
    for sx in (-1, 1):
        K.box((sx * 8, 0.075, 20), (4, 0.15, 92), SLAB, 0, 0)
        K.box((sx * 6.08, 0.085, 20), (0.18, 0.17, 92), GRAN, 0, 0.01)
        K.box((sx * 5.85, 0.002, 20), (0.3, 0.004, 92), pm("#2a2830", 0.15), 0, 0)  # wet gutter
    for x in (-0.72, 0.72):  # tram rails catch the light
        K.box((x - 1.3, 0.005, 20), (0.07, 0.012, 92), pm("#9a9aa0", 0.2, 1.0), 0, 0)
    for z in (6, 21, 38):
        K.cyl((2.6, 0.004, z), 0.35, 0.01, IRONM, 20)
    # ---------------- houses ----------------
    for k in range(9):
        for sx in (-1, 1):
            spec = (RIGHT if sx > 0 else LEFT)[k]
            if spec is None: continue
            house(K, k, sx, spec, night, WINS, DARKW, SHOPG, CURT, TRIM, STONE, STONE_D, ROOF, SLATE, rnd)
    # posters pasted on the house fronts beside the shops, readable
    pi = 0
    for k in range(9):
        for sx in (-1, 1):
            if (RIGHT if sx > 0 else LEFT)[k] is None: continue
            z = -12 + k * 7 + 3.12; bg, lines, acc, ink = POSTERS[pi % len(POSTERS)]; pi += 1
            poster(K, (sx * 9.92, 1.75, z), 0.4, 0.6, sx * D90, bg, lines, ink, None, "sans")
    factory(K, BRK, TRIM, STONE, IRONM, night, rnd)
    endbuilding(K, TRIM, STONE, STONE_D, SLATE, IRONM, night, WINS, DARKW, CURT)
    # ---------------- street furniture ----------------
    lamp_mat = pm("#1e2a26", 0.4, 0.7); LAMPS = []
    for k in range(7):
        for sx in (-1, 1):
            z = -10 + k * 9
            if sx > 0 and z == 26: z = 23.0          # keep the gate clear (shot 25)
            if sx < 0 and z == 17: z = 12.5          # keep the family close-up clear (shot 27)
            LAMPS.append((sx * 5.6, z)); gaslamp(K, (sx * 5.6, 0.0, z), lamp_mat, LANT)
    litfass(K, (-7.7, 0.15, 3.2), 0)
    litfass(K, (7.9, 0.15, 37.5), 3)
    bicycle(K, (-9.55, 0.15, 9.6), pm("#1a1a1e", 0.4, 0.6), D90)
    bicycle(K, (9.55, 0.15, 3.0), pm("#5a1e1e", 0.4, 0.5), -D90)
    BW = wood("#8a5a32", "#4a2c18", 3); CW = wood("#b08a52", "#6a4a22", 12, 0.8)
    for (x, z) in ((7.4, -7), (-7.3, -4), (7.6, 7.0), (-7.4, 11.0), (-7.5, 27.0), (7.6, 40.5), (-7.8, 41.5)):
        barrel(K, (x, 0.55, z), 0.3, 0.8, BW, IRONM)
    for (x, y, z, s) in ((8.3, 0.37, 6.4, 0.55), (8.4, 0.35, 7.1, 0.5), (8.3, 0.79, 6.7, 0.45), (-8.8, 0.37, 12.0, 0.55), (-8.9, 0.39, 26.0, 0.6), (-8.9, 0.87, 26.1, 0.5)):
        crate(K, (x, y, z), s, CW, rnd.uniform(-0.3, 0.3))
    for (x, z) in ((-8.6, 11.2), (9.2, -5.0)):  # milk cans + dustbins
        K.cyl((x, 0.5, z), 0.17, 0.7, pm("#9a9a98", 0.35, 0.8), 16); K.cyl((x, 0.88, z), 0.12, 0.08, pm("#9a9a98", 0.35, 0.8), 16)
        K.cyl((x + 0.45, 0.55, z + 0.1), 0.28, 0.8, pm("#3a4a3e", 0.5, 0.5), 18); K.cyl((x + 0.45, 0.97, z + 0.1), 0.3, 0.05, pm("#3a4a3e", 0.5, 0.5), 18)
    handcart(K, (8.6, 0.15, -1.5), BW, IRONM, CW)
    for (x, z) in ((-8.4, 37.0), (8.4, 43.5)): bench(K, (x, 0.15, z), BW, IRONM, -1 if x < 0 else 1)
    for (x, z) in ((-8.6, 40.0), (8.7, 34.8)): tree(K, (x, 0.15, z))
    # tram / telegraph wires against the sky
    for z in range(-12, 46, 14): K.cyl((0, 7.2, z), 0.012, 20, IRONM, 4, "x")
    K.cyl((-1.3, 6.4, 17), 0.012, 60, IRONM, 4, "z")
    # the speaker's crate (shot 20) - a stencilled beer crate
    crate(K, (0, 0.27, 34.2), 0.6, wood("#a07a4a", "#5a3a1a", 12, 0.8), 0.0, wood("#7a5a32", "#3a2a12", 12, 0.8))
    text("BRAUEREI", (0, 0.3, 33.885), 0.08, pm("#2a1a10", 0.8), 0, "sans", 0.002)
    K.build()
    # ---------------- light ----------------
    if night:
        K_.set_world((0.004, 0.008, 0.03), (0.03, 0.04, 0.09), 1.0, (0.006, 0.012, 0.05), (0.06, 0.07, 0.16))
        lib.light("SUN", (0, 0, 10), 0.35, (0.55, 0.68, 1.0), math.radians(1.5), (math.radians(55), 0, math.radians(-150)))
        moon = K_.Kit("moon"); moon.sphere((-14, 62, 110), 3.2, em("#e8ecff", 6.0), 20); moon.build()
        for (x, z) in LAMPS: lib.light("POINT", T(x, 4.35, z), 160, (1.0, 0.7, 0.38), 0.15)
        if sid in (24, 28):  # torch glow from the crowd lights the square and the facade from below
            r = random.Random(33)
            for i in range(9):
                lib.light("POINT", T(r.uniform(-4, 4), 2.3, (31 if sid == 24 else 33) + r.uniform(0, 9)), 140, (1.0, 0.5, 0.18), 0.4)
            lib.light("SPOT", T(0, 0.3, 41), 900, (1.0, 0.55, 0.25), 0.5, (math.radians(147), 0, 0))
    else:
        K_.set_world((0.30, 0.35, 0.44), (0.50, 0.52, 0.56), 1.0, (0.30, 0.36, 0.46), (0.62, 0.62, 0.64))
        lib.light("SUN", (0, 0, 10), 2.6, (1.0, 0.86, 0.68), math.radians(10), (math.radians(52), 0, math.radians(30)))
    return {}


# ---------------- pieces ----------------
def house(K, k, sx, spec, night, WINS, DARKW, SHOPG, CURT, TRIM, STONE, STONE_D, ROOF, SLATE, rnd):
    name, kind, shopc = spec
    zc = -12 + k * 7; X = sx * 10; face = sx * D90
    h = 11 + ((k + (1 if sx > 0 else 0)) % 3) * 2
    def P(d, y, u): return (X - sx * d, y, zc + u)
    WALL = grime(f"hw{k}{sx}", WALLC[(k * 2 + (1 if sx > 0 else 0)) % len(WALLC)], 0.32)
    K.box((sx * 13, h / 2, zc), (6, h, 6.96), WALL, 0, 0.02)
    # rusticated ground floor, string course, pilaster strips, cornice + frieze + dentils
    K.box(P(0.03, 1.6, 0), (0.06, 3.2, 6.96), STONE, 0, 0.01)
    for j in range(5): K.box(P(0.065, 0.4 + j * 0.62, 0), (0.02, 0.025, 6.9), STONE_D, 0, 0)
    K.box(P(0.09, 3.32, 0), (0.18, 0.22, 7.0), TRIM, 0, 0.02)
    for u in (-3.33, 3.33): K.box(P(0.05, (3.4 + h) / 2, u), (0.1, h - 3.4, 0.3), TRIM, 0, 0.01)
    K.box(P(0.05, h - 0.8, 0), (0.1, 0.5, 7.0), grime("frieze", "#b89870", 0.3), 0, 0.01)
    K.box(P(0.18, h - 0.42, 0), (0.36, 0.26, 7.1), TRIM, 0, 0.03)
    K.box(P(0.1, h - 0.6, 0), (0.2, 0.1, 7.04), TRIM, 0, 0.01)
    for j in range(22): K.box(P(0.14, h - 0.62, -3.3 + j * 0.31), (0.08, 0.1, 0.12), TRIM, 0, 0)
    # roof: steep tiled slope facing the street, dormers, chimneys
    rm = ROOF if (k + sx) % 3 else SLATE
    K.quad([(X - sx * 0.3, h, zc - 3.55), (X - sx * 0.3, h, zc + 3.55), (sx * 13.5, h + 3.4, zc + 3.55), (sx * 13.5, h + 3.4, zc - 3.55)], rm)
    K.quad([(sx * 13.5, h + 3.4, zc - 3.55), (sx * 13.5, h + 3.4, zc + 3.55), (sx * 16, h, zc + 3.55), (sx * 16, h, zc - 3.55)], rm)
    for u in (-3.55, 3.55):
        K.quad([(X, h, zc + u), (sx * 13.5, h + 3.4, zc + u), (sx * 16, h, zc + u)], grime("gable", "#8a7a6a", 0.3))
    for u in ((-1.8, 1.8) if k % 2 else (0,)):
        dx = sx * 11.1
        K.box((dx, h + 1.1, zc + u), (1.1, 1.6, 1.0), TRIM, 0, 0.02)
        K.box((dx - sx * 0.56, h + 1.2, zc + u), (0.02, 0.85, 0.6), WINS[(k + int(u)) % len(WINS)] if (night and rnd.random() < 0.6) else DARKW, 0, 0)
        K.box((dx, h + 2.0, zc + u), (1.3, 0.12, 1.2), rm, 0, 0.01, 0, sx * -0.35)
    for u in (-2.4, 2.1):
        cx = sx * (13.2 + (u > 0) * 1.4)
        K.box((cx, h + 3.2, zc + u), (0.55, 2.0, 0.7), grime("chim", "#8a4a3a", 0.4), 0, 0.02)
        K.box((cx, h + 4.25, zc + u), (0.7, 0.1, 0.85), STONE_D, 0, 0.01)
        for dz in (-0.15, 0.15): K.cyl((cx, h + 4.45, zc + u + dz), 0.08, 0.3, pm("#7a4a3a", 0.8), 10)
    K.cyl(P(0.12, h / 2, 3.42), 0.055, h, iron("#2e3a34"), 10)  # drainpipe
    # upper floors: framed windows, sills, hoods / pediments, curtains, shutters, flower boxes, a balcony
    nfl = int((h - 4.2) // 2.7); shut = (k + sx) % 3 == 0; flow = (k + sx) % 2 == 0
    shutm = cloth(["#2e5a3a", "#7a2a24", "#2e3e6a", "#5a6a2a"][(k + (sx > 0)) % 4])
    for fl in range(nfl):
        y = 4.1 + fl * 2.7
        for j, u in enumerate((-2.1, 0.0, 2.1)):
            lit = night and rnd.random() < 0.62
            K.box(P(0.012, y + 0.8, u), (0.02, 1.55, 0.86), WINS[rnd.randrange(len(WINS))] if lit else DARKW, 0, 0)
            for uu in (-0.47, 0.47): K.box(P(0.05, y + 0.8, u + uu), (0.08, 1.72, 0.09), TRIM, 0, 0.01)
            K.box(P(0.05, y + 1.62, u), (0.08, 0.09, 1.03), TRIM, 0, 0.01)
            K.box(P(0.04, y + 1.12, u), (0.04, 0.05, 0.86), TRIM, 0, 0)
            K.box(P(0.04, y + 0.8, u), (0.04, 1.55, 0.04), TRIM, 0, 0)
            K.box(P(0.11, y - 0.03, u), (0.2, 0.08, 1.15), STONE, 0, 0.01)
            if fl % 2 == 0:
                K.box(P(0.1, y + 1.82, u), (0.2, 0.14, 1.25), TRIM, 0, 0.015); K.box(P(0.12, y + 1.75, u), (0.06, 0.22, 0.16), STONE, 0, 0.005)
            else:
                K.quad([P(0.08, y + 1.72, u - 0.62), P(0.08, y + 1.72, u + 0.62), P(0.08, y + 2.05, u)], TRIM)
                K.box(P(0.09, y + 1.72, u), (0.1, 0.06, 1.28), TRIM, 0, 0.01)
            if rnd.random() < 0.7:
                cm = CURT[rnd.randrange(len(CURT))]
                for uu in (-0.33, 0.33): K.box(P(0.026, y + 0.85, u + uu), (0.01, 1.45, 0.2), cm, 0, 0)
            if shut:
                for uu in (-0.73, 0.73): K.box(P(0.06, y + 0.8, u + uu), (0.04, 1.66, 0.46), shutm, 0, 0.01)
            if flow and fl < 2 and j != 1:
                K.box(P(0.28, y + 0.08, u), (0.24, 0.18, 0.92), wood("#5a3a1e", "#2e1a0c", 9), 0, 0.01)
                for q in range(7):
                    K.sphere(P(0.3 + rnd.uniform(-0.05, 0.05), y + 0.24 + rnd.uniform(0, 0.08), u - 0.4 + q * 0.13), 0.07, cloth("#3a6a2a"), 6)
                    K.sphere(P(0.34, y + 0.3 + rnd.uniform(0, 0.08), u - 0.38 + q * 0.13), 0.04, pm(["#d82030", "#f0a020", "#e8508a", "#f0f0e0"][(q + k) % 4], 0.6), 6)
        if fl == 0 and (k + sx) % 3 == 1:  # little iron balcony on the middle window
            K.box(P(0.45, y - 0.12, 0), (0.9, 0.12, 1.6), STONE, 0, 0.02)
            for q in range(11): K.cyl(P(0.86, y + 0.4, -0.75 + q * 0.15), 0.012, 0.9, iron(), 6)
            K.box(P(0.86, y + 0.88, 0), (0.05, 0.05, 1.6), iron(), 0, 0.005)
            for uu in (-0.78, 0.78): K.box(P(0.45, y + 0.88, uu), (0.85, 0.05, 0.05), iron(), 0, 0.005)
    # house number plate (blue enamel)
    K.box(P(0.02, 3.0, 3.0), (0.02, 0.2, 0.26), pm("#1e3a8a", 0.25), 0, 0.005)
    text(str(10 + k * 2 + (1 if sx > 0 else 0)), P(0.036, 3.0, 3.0), 0.14, pm("#f4f0e8", 0.4), face, "sans", 0.002)
    shopfront(K, P, sx, k, face, name, kind, shopc, night, SHOPG, rnd)

def shopfront(K, P, sx, k, face, name, kind, shopc, night, SHOPG, rnd):
    FR = pm(shopc, 0.35); GLD = gold()
    K.box(P(0.18, 1.2, -1.0), (0.36, 2.4, 4.3), FR, 0, 0.015)          # wooden shopfront surround
    K.box(P(0.37, 0.3, -1.0), (0.04, 0.6, 4.0), pm(shopc, 0.3), 0, 0.01)
    for j in range(4): K.box(P(0.39, 0.3, -2.6 + j * 1.07), (0.02, 0.4, 0.8), pm(shopc, 0.45), 0, 0.005)
    # the lit display: backdrop glow, goods on two glass shelves, mullions, gilt edge
    K.box(P(0.365, 1.5, -1.0), (0.02, 1.7, 3.8), SHOPG, 0, 0)
    goods(K, P, kind, rnd)
    K.box(P(0.62, 1.5, -1.0), (0.04, 1.74, 0.05), FR, 0, 0.005)
    for u in (-2.95, 0.95): K.box(P(0.5, 1.5, u), (0.28, 1.86, 0.1), FR, 0, 0.01)
    K.box(P(0.5, 2.42, -1.0), (0.28, 0.1, 4.0), FR, 0, 0.01); K.box(P(0.55, 0.62, -1.0), (0.18, 0.06, 4.0), GLD, 0, 0.005)
    K.box(P(0.6, 0.62, -1.0), (0.48, 0.05, 4.1), FR, 0, 0.005)
    # door between panelled jambs: lit glass, brass handle, transom, step
    for u in (1.3, 2.8): K.box(P(0.18, 1.2, u), (0.36, 2.4, 0.2), FR, 0, 0.01)
    K.box(P(0.03, 1.15, 2.05), (0.06, 2.3, 1.3), pm(shopc, 0.4), 0, 0.01)
    K.box(P(0.07, 1.5, 2.05), (0.02, 0.9, 0.7), SHOPG, 0, 0)
    K.box(P(0.07, 2.2, 2.05), (0.02, 0.22, 1.1), SHOPG, 0, 0)
    for v in (1.0, 1.97, 2.08): K.box(P(0.08, v, 2.05), (0.03, 0.05, 1.2), FR, 0, 0)
    K.cyl(P(0.11, 1.1, 1.75), 0.025, 0.12, brass(), 8, "x")
    K.box(P(0.2, 0.05, 2.05), (0.4, 0.1, 1.4), grime("step", "#a09888", 0.3), 0, 0.01)
    # fascia sign with gilt lettering
    sign(K, P(0.42, 2.72, -0.15), 6.3, 0.48, face, name, "#14181c" if k % 2 else shopc, None, "serif", "#c8963a", 0.07)
    # striped awning over the window + valance
    sa = ["#c8323a", "#2a6a4a", "#d8a83a", "#2a4a8a"][(k + (sx > 0)) % 4]
    AW = stripes(f"aw{sa}", sa, "#f0e8d4", 9.0, 1)
    if (k + sx) % 3 != 2:
        K.box(P(1.15, 2.33, -1.0), (1.55, 0.04, 4.3), AW, 0, 0.005, 0, sx * 0.32)
        K.box(P(1.9, 1.97, -1.0), (0.03, 0.26, 4.3), AW, 0, 0.004)
    # a hanging bracket sign every other shop (reads down the street)
    if (k + (sx > 0)) % 2 == 0:
        ir = iron()
        K.box(P(0.7, 3.75, -3.0), (1.3, 0.05, 0.05), ir, 0, 0.005)
        K.box(P(0.3, 3.5, -3.0), (0.05, 0.6, 0.05), ir, 0, 0.005, 0, sx * 0.8)
        K.box(P(0.85, 3.3, -3.0), (0.8, 0.55, 0.05), pm(shopc, 0.4), 0, 0.01)
        K_._frame(K, P(0.85, 3.3, -3.0), 0.8, 0.55, 0.0, gold(), 0.03, 0.07)
        for d in (0.55, 1.15): K.cyl(P(d, 3.65, -3.0), 0.008, 0.16, ir, 4)
        short = {"bread": "BROT", "bottles": "APOTHEKE", "cafe": "CAFÉ", "clocks": "UHREN", "books": "BÜCHER", "cloth": "MASS-\nSCHNEIDER", "meat": "WURST",
                 "beer": "BIER", "papers": "TABAK", "jars": "KAFFEE", "hats": "HÜTE", "wheels": "RÄDER", "pawn": "PFAND"}[kind]
        for yaw, dz in ((0.0, -0.03), (math.pi, 0.03)):
            text(short, P(0.85, 3.3, -3.0 + dz), 0.15, gold(), yaw, "serif", 0.004, fit=0.68)
        if kind == "bread": K.torus(P(0.85, 3.82, -3.0), 0.13, 0.03, gold(), 20, 8, "z")
        if kind == "clocks": K.cyl(P(0.85, 3.85, -3.0), 0.16, 0.06, gold(), 24, "z")
    # wall lantern beside the door
    K.box(P(0.2, 2.55, 3.05), (0.4, 0.04, 0.04), iron(), 0, 0)
    K.cyl(P(0.4, 2.45, 3.05), 0.07, 0.2, em("#ffc070", 10.0) if night else pm("#e8e4d8", 0.2), 6)
    K.cyl(P(0.4, 2.6, 3.05), 0.09, 0.08, iron(), 6, "y", 0.02)
    if night:
        lib.light("AREA", T(*P(0.95, 1.5, -1.0)), 70, (1.0, 0.72, 0.42), 1.6, (0, -sx * D90, 0), 3.6)

def goods(K, P, kind, rnd):
    n = 5 if kind in ("wheels", "hats") else 10
    for row, y in enumerate((0.72, 1.42)):
        K.box(P(0.48, y, -1.0), (0.24, 0.025, 3.7), pm("#d8e0e0", 0.05), 0, 0)
        for i in range(n):
            u = -2.7 + i * (3.5 / (n - 1)); b = y + 0.02
            if kind == "bread":
                if i % 3 == 2: K_.pretzel(K, P(0.48, b, u), bread_m(), 1.4)
                else: K.sphere(P(0.48, b + 0.07, u), 0.1, bread_m(), 10, (1.3, 0.7, 0.9))
            elif kind in ("bottles", "jars"):
                c = ["#2a6a4a", "#8a2a1e", "#d8a83a", "#2a3a8a", "#e8dcc0"][(i + row) % 5]
                K.cyl(P(0.48, b + 0.12, u), 0.06, 0.24, pm(c, 0.15), 10); K.cyl(P(0.48, b + 0.27, u), 0.025, 0.07, pm(c, 0.15), 8)
                K.box(P(0.545, b + 0.12, u), (0.005, 0.08, 0.08), pm("#f4ecd8", 0.7), 0, 0)
            elif kind == "cafe":
                if i % 2:
                    K.cyl(P(0.48, b + 0.06, u), 0.13, 0.12, pm(["#f0d8e0", "#6a3a1e", "#f4ecd8"][i % 3], 0.5), 16); K.sphere(P(0.48, b + 0.14, u), 0.025, pm("#c8102a", 0.3), 6)
                else:
                    K.cyl(P(0.48, b + 0.04, u), 0.045, 0.08, pm("#f4f0e8", 0.2), 12); K.cyl(P(0.48, b + 0.005, u), 0.08, 0.01, pm("#f4f0e8", 0.2), 12)
            elif kind == "clocks":
                K.cyl(P(0.48, b + 0.16, u), 0.12, 0.05, pm("#f4ecd8", 0.4), 20, "x"); K.torus(P(0.505, b + 0.16, u), 0.12, 0.015, brass(), 18, 6, "x")
            elif kind == "books":
                for q in range(4): K.box(P(0.48, b + 0.12, u - 0.12 + q * 0.07), (0.16, rnd.uniform(0.18, 0.26), 0.06), pm(rnd.choice(["#7a1e22", "#1e3a5a", "#2a4a2a", "#a8782a"]), 0.6), 0, 0.003)
            elif kind == "cloth":
                K.cyl(P(0.48, b + 0.15, u), 0.07, 0.3, cloth(["#2a3a6a", "#6a2a2a", "#3a5a3a", "#8a7a5a", "#4a4a4a"][i % 5]), 12)
            elif kind == "meat":
                K.cyl(P(0.48, b + 0.35, u), 0.035, 0.4, pm("#8a2a1e", 0.4), 10); K.sphere(P(0.48, b + 0.06, u), 0.08, pm("#c86a5a", 0.5), 8, (1.4, 0.6, 1))
            elif kind == "beer":
                K.cyl(P(0.48, b + 0.1, u), 0.05, 0.2, pm("#c88a2a", 0.15), 10); K.cyl(P(0.48, b + 0.215, u), 0.052, 0.03, pm("#fff8e8", 0.8), 10)
            elif kind == "papers":
                K.box(P(0.48, b + 0.15, u), (0.03, 0.3, 0.22), paper("#efe4c8"), 0, 0); K.box(P(0.5, b + 0.25, u), (0.01, 0.05, 0.2), pm("#1a1a1a", 0.7), 0, 0)
            elif kind == "hats":
                c = ["#2a2a2e", "#5a4a3a", "#3a3a4a", "#8a7a5a", "#1e1e22"][i % 5]
                K.cyl(P(0.48, b + 0.01, u), 0.17, 0.02, cloth(c), 16); K.cyl(P(0.48, b + 0.08, u), 0.1, 0.13, cloth(c), 16)
            elif kind == "wheels":
                K.torus(P(0.48, b + 0.3, u), 0.28, 0.02, pm("#1a1a1a", 0.6), 20, 6, "x")
            elif kind == "pawn":
                c = [gold(), brass(), pm("#c8c8d0", 0.2, 1.0), pm("#7a1e22", 0.4)][i % 4]
                if i % 2: K.cyl(P(0.48, b + 0.1, u), 0.07, 0.2, c, 12)
                else: K.box(P(0.48, b + 0.08, u), (0.15, 0.16, 0.2), c, 0, 0.01)

def bread_m(): return K_.cached("bread", lambda: lib.bread("kbread"))

def gaslamp(K, c, m, glow):
    x, y, z = c
    K.cyl((x, 0.25, z), 0.17, 0.5, m, 12); K.cyl((x, 0.55, z), 0.12, 0.1, m, 12)
    K.cyl((x, 2.3, z), 0.055, 3.6, m, 10, "y", 0.045)
    K.cyl((x, 3.95, z), 0.08, 0.1, m, 10)
    K.box((x, 3.85, z), (0.7, 0.04, 0.04), m, 0, 0.005)  # ladder bar
    K.cyl((x, 4.35, z), 0.2, 0.55, glow, 4, "y", 0.26, math.pi / 4)
    for a in range(4):
        aa = math.pi / 4 + a * math.pi / 2
        K.box((x + 0.23 * math.cos(aa), 4.35, z + 0.23 * math.sin(aa)), (0.025, 0.58, 0.025), m, -aa, 0)
    K.cyl((x, 4.72, z), 0.34, 0.22, m, 4, "y", 0.06, math.pi / 4)
    K.sphere((x, 4.88, z), 0.05, m, 8)
    K.cyl((x, 4.06, z), 0.17, 0.06, m, 4, "y", None, math.pi / 4)

def litfass(K, c, seed):
    """advertising column covered in readable bills"""
    x, y, z = c; G = pm("#24402e", 0.45, 0.4)
    K.cyl((x, y + 0.15, z), 0.66, 0.3, G, 24); K.cyl((x, y + 1.6, z), 0.58, 2.6, pm("#d8d0b8", 0.8), 24)
    K.cyl((x, y + 2.98, z), 0.68, 0.16, G, 24); K.cyl((x, y + 3.2, z), 0.6, 0.3, G, 24, "y", 0.25)
    K.sphere((x, y + 3.45, z), 0.12, G, 10)
    for i in range(8):
        a = i * math.pi / 4; bg, lines, acc, ink = POSTERS[(i + seed) % len(POSTERS)]
        px, pz = x + 0.6 * math.sin(a), z - 0.6 * math.cos(a)
        poster(K, (px, y + 1.65, pz), 0.44, 2.3 if i % 2 else 1.4, -a, bg, lines, ink, None, "sans")

def bicycle(K, c, m, yaw):
    x, y, z = c; ca, sa = math.cos(yaw), math.sin(yaw)
    def at(u, v): return (x + u * ca, y + v, z - u * sa)
    for u in (-0.5, 0.5): K.torus(at(u, 0.34), 0.32, 0.018, pm("#1a1a1a", 0.7), 22, 6, "z", yaw)
    K.box(at(0, 0.55), (0.75, 0.03, 0.03), m, yaw, 0, 0, 0.15); K.box(at(-0.05, 0.45), (0.03, 0.5, 0.03), m, yaw, 0, 0, 0.5)
    K.box(at(0.45, 0.55), (0.03, 0.45, 0.03), m, yaw, 0, 0, -0.3); K.box(at(-0.25, 0.42), (0.5, 0.03, 0.03), m, yaw, 0, 0, -0.5)
    K.box(at(-0.15, 0.78), (0.2, 0.05, 0.1), pm("#3a2418", 0.6), yaw, 0.01); K.box(at(0.5, 0.82), (0.04, 0.03, 0.45), m, yaw, 0.005)

def handcart(K, c, W, I, CW):
    x, y, z = c
    K.box((x, y + 0.6, z), (1.0, 0.08, 1.6), W, 0, 0.01)
    for dx in (-0.5, 0.5): K.box((x + dx, y + 0.78, z), (0.05, 0.3, 1.6), W, 0, 0.005)
    for dz in (-0.5, 0.5): K.torus((x - 0.56, y + 0.38, z + dz), 0.34, 0.03, I, 20, 6, "x")
    K.box((x + 0.1, y + 0.7, z - 1.2), (0.05, 0.05, 1.0), W, 0, 0.005, -0.4)
    for i in range(3): crate(K, (x, y + 0.82, z - 0.45 + i * 0.45), 0.36, CW, 0.1 * i)
    K.sphere((x + 0.2, y + 1.1, z + 0.1), 0.2, cloth("#c8b48a"), 10, (1, 0.8, 1.2))

def bench(K, c, W, I, side):
    x, y, z = c
    for dz in (-0.7, 0.7): K.box((x, y + 0.22, z + dz), (0.45, 0.44, 0.06), I, 0, 0.005)
    for j in range(3): K.box((x - 0.13 + j * 0.13, y + 0.46, z), (0.1, 0.035, 1.6), W, 0, 0.005)
    for j in range(2): K.box((x + side * 0.24, y + 0.62 + j * 0.15, z), (0.035, 0.1, 1.6), W, 0, 0.005)

def tree(K, c):
    x, y, z = c
    K.cyl((x, y + 1.6, z), 0.13, 3.2, wood("#4a3a2a", "#2a1e14", 2, 0.9), 10)
    K.cyl((x, y + 0.02, z), 0.6, 0.04, iron(), 16)
    r = random.Random(int(x * 10 + z))
    for i in range(9):
        K.sphere((x + r.uniform(-0.9, 0.9), y + 3.4 + r.uniform(-0.3, 1.0), z + r.uniform(-0.9, 0.9)), r.uniform(0.6, 0.9), cloth(["#2e5a24", "#3a6a2a", "#24481e"][i % 3]), 10)

def factory(K, BRK, TRIM, STONE, IRONM, night, rnd):
    """right side z 19.5..33.5: a brick engineering works, its compound wall on the sidewalk with the gate at x 6"""
    F = BRK; DK = pm("#22262e", 0.1, 0.3); B2 = K_.brick("brk2", "#8a4030", "#6a2e24", "#3a2a24", 5.0)
    K.box((13, 7.5, 26.5), (6, 15, 14), F, 0, 0.02)
    for j in range(5): K.box((9.95, 7.5, 20.6 + j * 2.95), (0.2, 15, 0.45), B2, 0, 0.01)
    for fl in range(2):
        for j in range(4):
            z = 22.05 + j * 2.95; y0 = 3.6 + fl * 5.0
            K.box((9.99, y0 + 1.7, z), (0.04, 3.4, 1.9), DK if not night or rnd.random() < 0.5 else K_.window_glow("fw", "#a8c0d8", 0.6), 0, 0)
            for q in range(5): K.box((9.96, y0 + 0.1 + q * 0.75, z), (0.03, 0.04, 1.9), IRONM, 0, 0)
            for q in range(3): K.box((9.96, y0 + 1.7, z - 0.95 + (q + 1) * 0.475), (0.03, 3.4, 0.04), IRONM, 0, 0)
            K.box((9.9, y0 - 0.06, z), (0.2, 0.12, 2.1), STONE, 0, 0.01)
            K.box((9.92, y0 + 3.5, z), (0.16, 0.22, 2.2), B2, 0, 0.01)
    K.box((9.85, 13.0, 26.5), (0.3, 1.4, 12.5), TRIM, 0, 0.02)
    text("MASCHINENFABRIK  KRAUSE & SÖHNE", (9.68, 13.0, 26.5), 0.8, pm("#1e2a3a", 0.5), D90, "serif", 0.03, fit=12.0)
    K.quad([(10, 15, 19.5), (10, 15, 33.5), (13, 17.5, 33.5), (13, 17.5, 19.5)], pm("#3a3e46", 0.6))
    # smokestack
    K.cyl((14.5, 14, 30.5), 0.95, 28, BRK, 20, "y", 0.75); K.cyl((14.5, 28.2, 30.5), 0.9, 0.6, pm("#2a2224", 0.8), 20)
    for y in (8, 18, 24): K.cyl((14.5, y, 30.5), 0.96 - (y / 28) * 0.2, 0.25, IRONM, 20)
    # compound wall along the street (x 6.1..6.4, z 24.2..33.5) with brick pillars and the gate; side wall back to x 10
    K.box((6.25, 1.3, 30.6), (0.3, 2.6, 5.8), F, 0, 0.01); K.box((6.25, 2.65, 30.6), (0.42, 0.12, 5.9), STONE, 0, 0.01)
    K.box((8.1, 1.3, 24.2), (3.8, 2.6, 0.3), F, 0, 0.01); K.box((8.1, 2.65, 24.2), (3.9, 0.12, 0.42), STONE, 0, 0.01)
    for z in (24.32, 27.68):
        K.box((6.25, 1.7, z), (0.55, 3.4, 0.55), F, 0, 0.02); K.box((6.25, 3.45, z), (0.68, 0.14, 0.68), STONE, 0, 0.02)
        K.sphere((6.25, 3.75, z), 0.2, em("#ffc890", 6.0) if night else pm("#e8e4d8", 0.2), 14)
    # the gate: double iron gate with spear-topped bars, rails, a sign plate, a chain (the padlock is a card in shot 25)
    G = pm("#1a1c22", 0.35, 0.8)
    for k in range(17):
        z = 24.7 + k * 0.1875; K.cyl((6.12, 1.6, z), 0.022, 3.0, G, 8)
        K.cyl((6.12, 3.18, z), 0.04, 0.16, G, 4, "y", 0.0)
    for y in (0.25, 1.15, 2.6): K.box((6.12, y, 26.0), (0.06, 0.07, 3.0), G, 0, 0.005)
    K.box((6.12, 1.6, 26.0), (0.07, 3.0, 0.07), G, 0, 0.005)
    for k in range(16): K.cyl((6.12, 2.9, 24.79 + k * 0.1875), 0.05, 0.02, G, 8, "y", None, 0.0)   # rosettes on the top rail
    K.box((6.1, 3.65, 26.0), (0.06, 0.45, 2.6), G, 0, 0.01)
    text("FABRIK", (6.065, 3.65, 26.0), 0.3, gold(), D90, "serif", 0.01)
    # notices: tied to the gate, pasted on the pillar and the wall
    poster(K, (6.07, 2.2, 27.1), 0.42, 0.56, D90, "#f2ead6", [("GESCHLOSSEN", 0.07), ("Keine Einstellungen", 0.045), ("Die Direktion", 0.04)], "#1a1a1a", None, "serif", "#1a1a1a")
    poster(K, (5.965, 1.8, 24.32), 0.46, 0.66, D90, "#e8c84a", [("ARBEIT", 0.13), ("UND BROT!", 0.1)], "#c8202a", None, "sans")
    poster(K, (6.095, 1.6, 28.6), 0.55, 0.75, D90, "#f0e6cc", [("BEKANNT-", 0.08), ("MACHUNG", 0.08), ("des Polizeipräsidenten", 0.035)], "#1a1a1a", None, "serif", "#1a1a1a")
    poster(K, (6.095, 1.5, 29.4), 0.5, 0.7, D90, "#c8202a", [("STREIK!", 0.14), ("ALLE MANN", 0.07)], "#f4ecd8", None, "sans")
    # the employment-office hatch in the side wall where the dole queue ends (faces -z)
    K.box((8.0, 1.5, 24.03), (1.2, 0.9, 0.05), K_.window_glow("hatch", "#ffc890", 2.5), 0, 0)
    K.box((8.0, 1.5, 24.02), (1.36, 1.06, 0.03), wood("#3a2a1a", "#1a120a", 8), 0, 0.01)
    K.box((8.0, 1.02, 23.93), (1.4, 0.06, 0.22), STONE, 0, 0.01)
    sign(K, (8.0, 2.3, 24.0), 1.8, 0.36, 0.0, "ARBEITSAMT", "#1e2a3a", pm("#f2ead6", 0.4), "sans", "#c8c0a8", 0.04)
    if night: lib.light("POINT", T(8.0, 1.6, 23.6), 30, (1.0, 0.8, 0.55), 0.3)

def endbuilding(K, TRIM, STONE, STONE_D, SLATE, IRONM, night, WINS, DARKW, CURT):
    """the grand building closing the square (facade z 46, x -12..12, 16 m), balcony x -3..3 at y 6..7.3"""
    WALL = grime("endw", "#d8c08e", 0.28); BASE = grime("endb", "#b8a888", 0.3)
    K.box((0, 8, 47), (24, 16, 2), WALL, 0, 0.02)
    K.box((0, 2.6, 45.98), (24, 5.2, 0.04), BASE, 0, 0.01)
    for j in range(8): K.box((0, 0.5 + j * 0.62, 45.95), (24, 0.03, 0.02), STONE_D, 0, 0)
    K.box((0, 5.35, 45.96), (24.2, 0.3, 0.08), TRIM, 0, 0.01)
    K.box((0, 14.6, 45.97), (24.4, 0.5, 0.06), TRIM, 0, 0.01)
    K.box((0, 15.6, 45.98), (24, 1.4, 0.04), grime("attic", "#c8b080", 0.3), 0, 0.01)
    for j in range(25): K.cyl((-11.5 + j * 0.96, 15.6, 46.02), 0.09, 0.9, TRIM, 10)
    K.box((0, 16.3, 46.0), (24.4, 0.2, 0.12), TRIM, 0, 0.02)
    # roof + central clock tower silhouette
    K.quad([(-12.2, 16, 46), (12.2, 16, 46), (12.2, 20, 49), (-12.2, 20, 49)], SLATE)
    K.box((0, 19, 47.5), (4, 6, 3), WALL, 0, 0.02); K.box((0, 22.2, 47.5), (4.4, 0.4, 3.4), TRIM, 0, 0.02)
    K.cyl((0, 19.6, 45.98), 1.1, 0.06, em("#ffe8c0", 2.0) if night else pm("#f4ecd8", 0.4), 32, "z")
    K.torus((0, 19.6, 45.95), 1.12, 0.06, gold(), 32, 8, "z")
    for a in range(12):
        aa = a * math.pi / 6; K.box((0.9 * math.sin(aa), 19.6 + 0.9 * math.cos(aa), 45.93), (0.05, 0.16, 0.02), pm("#1a1a1a", 0.5), 0, 0, 0, -aa)
    K.box((0.2, 19.85, 45.92), (0.04, 0.6, 0.02), pm("#1a1a1a", 0.5), 0, 0, 0, -0.6); K.box((-0.15, 19.5, 45.92), (0.05, 0.42, 0.02), pm("#1a1a1a", 0.5), 0, 0, 0, 1.2)
    K.quad([(-2.4, 22.4, 46.0), (2.4, 22.4, 46.0), (0, 24.6, 47.5)], SLATE); K.quad([(2.4, 22.4, 46.0), (2.4, 22.4, 49.0), (0, 24.6, 47.5)], SLATE)
    K.quad([(-2.4, 22.4, 49.0), (-2.4, 22.4, 46.0), (0, 24.6, 47.5)], SLATE)
    for x in (-11.4, 11.4): K.cyl((x, 18.6, 46.5), 0.04, 5, iron(), 6)
    # pilasters between bays, tall windows (lit at night), the balcony door
    for j in range(9): K.box((-12 + j * 3, 10.0, 45.96), (0.5, 9.2, 0.07), TRIM, 0, 0.01)
    for j in range(9): K.box((-12 + j * 3, 14.2, 45.97), (0.6, 0.3, 0.07), TRIM, 0, 0.01)
    rr = random.Random(46)
    for fl, (y0, hh) in enumerate(((6.3, 2.6), (9.6, 2.2), (12.2, 1.6))):
        for j in range(8):
            x = -10.5 + j * 3
            if fl == 0 and abs(x) < 3.2: continue
            lit = night and rr.random() < 0.7
            K.box((x, y0 + hh / 2, 45.985), (1.3, hh, 0.02), WINS[rr.randrange(len(WINS))] if lit else DARKW, 0, 0)
            K_._frame(K, (x, y0 + hh / 2, 45.97), 1.3, hh, 0.0, TRIM, 0.1, 0.05)
            K.box((x, y0 + hh / 2, 45.975), (0.05, hh, 0.03), TRIM, 0, 0)
            K.box((x, y0 - 0.06, 45.965), (1.6, 0.1, 0.06), TRIM, 0, 0.005)
            if fl == 0: K.box((x, y0 + hh + 0.22, 45.965), (1.7, 0.16, 0.06), TRIM, 0, 0.01)
            if lit and rr.random() < 0.6:
                for dx in (-0.48, 0.48): K.box((x + dx, y0 + hh / 2, 45.97), (0.3, hh - 0.1, 0.01), CURT[1], 0, 0)
    K.box((0, 7.6, 45.985), (2.0, 2.9, 0.02), K_.window_glow("bdoor", "#ffc070", 3.5 if night else 1.2), 0, 0)
    for dx in (-0.8, 0.8): K.box((dx, 7.6, 45.97), (0.45, 2.9, 0.01), cloth("#9a1e24"), 0, 0)
    K_._frame(K, (0, 7.6, 45.97), 2.0, 2.9, 0.0, TRIM, 0.14, 0.06)
    K.box((0, 9.3, 45.965), (2.6, 0.25, 0.06), TRIM, 0, 0.01)
    # ground floor: arched portal with a lit hall, barred side windows, lanterns
    K.box((0, 2.0, 45.99), (2.4, 4.0, 0.02), K_.window_glow("portal", "#ffb868", 2.4 if night else 0.8), 0, 0)
    K.torus((0, 4.0, 45.96), 1.25, 0.12, STONE, 24, 6, "z", 0, 0, 0, (1, 1, 0.4), math.pi)
    for dx in (-1.25, 1.25): K.box((dx, 2.0, 45.96), (0.26, 4.0, 0.08), STONE, 0, 0.01)
    for dx in (-0.55, 0.55): K.box((dx, 1.6, 45.97), (1.0, 3.2, 0.03), wood("#4a2a14", "#2a160a", 6), 0, 0.01)
    for j in range(8):
        x = -10.5 + j * 3
        if abs(x) < 2: continue
        K.box((x, 2.7, 45.99), (1.2, 1.8, 0.02), WINS[0] if night else DARKW, 0, 0)
        for q in range(5): K.cyl((x - 0.5 + q * 0.25, 2.7, 45.95), 0.02, 1.8, IRONM, 6)
        K_._frame(K, (x, 2.7, 45.96), 1.2, 1.8, 0.0, STONE, 0.12, 0.06)
    for dx in (-2.0, 2.0):
        K.box((dx, 3.4, 45.93), (0.08, 0.08, 0.1), iron(), 0, 0)
        K.cyl((dx, 3.6, 45.82), 0.12, 0.4, em("#ffc070", 12.0) if night else pm("#e8e4d8", 0.2), 6)
        K.cyl((dx, 3.86, 45.82), 0.15, 0.12, iron(), 6, "y", 0.03)
        if night: lib.light("POINT", T(dx, 3.6, 45.6), 80, (1.0, 0.7, 0.4), 0.1)
    # the balcony (keep: slab y 6..6.3, z 44.5..46; rail top y 7.3)
    K.box((0, 6.15, 45.2), (6, 0.3, 1.6), TRIM, 0, 0.03)
    K.box((0, 5.95, 45.25), (6.2, 0.12, 1.55), STONE, 0, 0.02)
    for dx in (-2.6, -1.3, 0, 1.3, 2.6): K.box((dx, 5.6, 45.75), (0.22, 0.6, 0.5), TRIM, 0, 0.02)
    for k in range(13): K.cyl((-2.8 + k * 0.47, 6.75, 44.6), 0.06, 0.9, TRIM, 10, "y", 0.045)
    for sxx in (-1, 1): K.box((sxx * 2.92, 6.75, 45.2), (0.16, 0.9, 1.4), TRIM, 0, 0.01)
    K.box((0, 7.25, 44.6), (6.1, 0.12, 0.22), TRIM, 0, 0.02)
    K.box((0, 6.35, 44.6), (6.0, 0.08, 0.18), TRIM, 0, 0.01)
    # plain red banners (no symbols) on gilt poles
    for k in range(4):
        x = -9 + k * 6
        K.box((x, 11, 45.955), (1.8, 4.5, 0.01), stripes("banr", "#a81e24", "#8a161c", 30.0, 0), 0, 0)
        K.cyl((x, 13.3, 45.95), 0.025, 2.0, gold(), 8, "x")
        K.box((x, 8.73, 45.95), (1.8, 0.06, 0.01), gold(), 0, 0)
