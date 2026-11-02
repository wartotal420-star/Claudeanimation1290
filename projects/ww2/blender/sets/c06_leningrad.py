# Chapter 6: besieged Leningrad, winter 1941-42.
# Street (three coords): a snowed-in avenue along z (x -6..6, snow drifts), classical pastel facades at |x| 7.5 (yellow,
# pink, green, with white columns and pediments, windows taped and dark), a frozen trolleybus abandoned at (3, 0, 30),
# a bakery with a queue spot at the right facade (x 7.5, z 8..12, sign "ХЛЕБ"), a water hole spot, tram wires sagging.
# Keep clear: x -4..4, z 0..20 (the woman pulling the sled, the queue at x 5.5..7, z 6..16).
# Apartment interior (x 40..46, z 0..5, floor y 0, ceiling 3.2): a table under the window with the bread ration on a plate
# with a scale (125 g), a pot on a little iron stove (burzhuika) with a belt boiling in it, wallpaper peeling off the
# wall, frost on the window, a candle, blankets; the table top is at y 0.78, plate centre (43, 0.79, 3.6).
# A wall calendar "1942" and a metronome on the shelf (the city radio's heartbeat).
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, stripes, R90
from .c05_kit import (sky, ground_mat, height_mesh, sun_light, area, point, spot, lathe, tube, worn, mat_once, cached, snow_mat, fsphere, smoke_mat, fire)

FAC = ["#e8c870", "#d8a8a0", "#a8c0a0", "#e0d0b0", "#c8b0d0", "#e8b880"]

def facade(K, k, sx, rnd, SNOW, TAPE, DARKW):
    zc = -10 + k * 9.0; X = sx * 7.5; h = 16 + (k % 2) * 2
    P = lambda d, y, u: (X - sx * d, y, zc + u)
    W = grime(f"lnf{k}{sx}", FAC[(k * 2 + (sx > 0)) % len(FAC)], 0.25); WH = grime("lnwhite", "#f0ece0", 0.2)
    K.box((sx * 11.5, h / 2, zc), (8, h, 9.0), W, 0, 0.0)
    K.box(P(0.05, 1.8, 0), (0.1, 3.6, 9.0), grime("lnrust", "#b8a888", 0.3), 0, 0.0)
    for j in range(6): K.box(P(0.08, 0.4 + j * 0.6, 0), (0.04, 0.04, 9.0), WH, 0, 0.0)
    K.box(P(0.2, h - 0.4, 0), (0.4, 0.5, 9.2), WH, 0, 0.02); K.box(P(0.12, 3.8, 0), (0.24, 0.2, 9.0), WH, 0, 0.01)
    K.box(P(0.25, h + 0.1, 0), (0.6, 0.4, 9.2), SNOW, 0, 0.1)
    for u in (-3.4, 3.4): K.cyl(P(0.3, (4 + h - 0.6) / 2, u), 0.22, h - 4.6, WH, 14)
    for fl in range(3):
        y = 4.6 + fl * 3.6
        for u in (-2.2, 0.0, 2.2):
            K.box(P(0.01, y + 1.0, u), (0.02, 1.8, 1.0), DARKW, 0, 0.0)
            for a in (0.55, -0.55): K.box(P(0.02, y + 1.0, u), (0.006, 2.0, 0.04), TAPE, 0, 0.0, a, 0)
            K.box(P(0.08, y + 2.05, u), (0.16, 0.12, 1.3), WH, 0, 0.01); K.box(P(0.1, y - 0.02, u), (0.2, 0.08, 1.2), WH, 0, 0.01)
            K.box(P(0.14, y + 0.06, u), (0.16, 0.08, 1.15), SNOW, 0, 0.03)
            if fl == 0 and (k + sx) % 2 == 0: K.quad([P(0.1, y + 2.12, u - 0.65), P(0.1, y + 2.12, u + 0.65), P(0.1, y + 2.5, u)], WH)

def build(M, D):
    random.seed(1942); K_.reset(); rnd = random.Random(42); sid = D.get("id", 0)
    sky((0.36, 0.42, 0.52), (0.62, 0.64, 0.68), (0.82, 0.8, 0.8), sun_dir=(-0.5, 0.2, 0.8), sun_col=(1.0, 0.85, 0.7), glow=0.3, clouds=0.4, cloud_shade=(0.6, 0.62, 0.68))
    SNOW = snow_mat("lnsnow"); TAPE = pm("#efe6c8", 0.8); DARKW = pm("#1a1e26", 0.1, 0.2)
    def H(x, z): return 0.25 + 0.35 * max(0, (abs(x) - 4) / 3.5) ** 2 + 0.12 * noise.noise(Vector((x * 0.3, z * 0.3, 1.0)))
    height_mesh("lnsnowg", -7.5, 7.5, -20, 140, 0.5, H, SNOW)
    K = Kit("lnd")
    for k in range(15):
        for sx in (-1, 1): facade(K, k, sx, rnd, SNOW, TAPE, DARKW)
    # bakery front with the ration queue: a dark doorway, sign, an iron lamp
    K.box((7.42, 1.3, 10), (0.2, 2.6, 2.0), pm("#2a1e16", 0.6), 0, 0.01)
    sign(K, (7.3, 3.1, 10), 2.4, 0.5, R90, "ХЛЕБ", "#2a3a2a", pm("#f0e8d0", 0.5), "serif", None, 0.05)
    K.box((7.35, 2.0, 12.2), (0.1, 0.8, 0.6), paper("#efe4c8"), 0, 0.0)
    text("ХЛЕБ 125 г", (7.29, 2.1, 12.2), 0.08, pm("#1a1a1a", 0.6), R90, "sans", 0.001, fit=0.5)
    # trolleybus frozen in the snow, tram wires, lamp posts, a poster "DEFEND LENINGRAD"
    TB = mat_once("lntb", lambda: worn("lntb", "#8a3a2a", "#3a2a22", 0.5, 0.2, 6, 0.7, "#5a2a1e"))
    K.box((3.2, 1.9, 30), (2.6, 2.8, 10), TB, 0, 0.3); K.box((3.2, 3.35, 30), (2.62, 0.4, 10.0), SNOW, 0, 0.15)
    for sd in (-1, 1):
        for k in range(6): K.box((3.2 + sd * 1.31, 2.3, 26 + k * 1.6), (0.02, 1.0, 1.3), pm("#c8d0d8", 0.1), 0, 0.0)
    for sd in (-0.5, 0.5): K.box((3.2 + sd, 5.0, 31), (0.04, 0.04, 3.0), pm("#2a2a2a", 0.5, 0.5), 0, 0.0, 0.45)
    for k in range(6):
        z = -5 + k * 18
        for sx in (-1, 1): K.cyl((sx * 6.6, 3.5, z), 0.1, 7, pm("#2a2a2a", 0.5, 0.5), 8)
        for x in (-2.0, 2.0): tube(f"wire{k}{x}", [(-6.6, 6.6, z), (x, 6.2, z), (6.6, 6.6, z)], 0.015, pm("#1a1a1a", 0.5), 6, 0) if x < 0 else None
        K.box((0, 6.5, z + 9), (0.02, 0.02, 18), pm("#1a1a1a", 0.5, 0.5), 0, 0.0)
    poster(K, (-7.42, 2.4, 6), 1.0, 1.4, -R90, "#c81e22", [("ЗАЩИТИМ", 0.12), ("ЛЕНИНГРАД", 0.11)], "#f4ecd8", None, "sans")
    poster(K, (-7.42, 2.4, 22), 1.0, 1.4, -R90, "#f0e8d0", [("ВСЕ", 0.14), ("НА ЗАЩИТУ", 0.09), ("РОДИНЫ", 0.11)], "#a81e22", None, "sans")
    # snow-covered rubble, a sled with a bundle, buckets by a water hole, firewood from a broken fence
    for k in range(20): fsphere(K, (rnd.choice((-1, 1)) * rnd.uniform(4.5, 7), 0.3, rnd.uniform(-5, 60)), rnd.uniform(0.4, 1.0), SNOW, 10, (1.6, 0.6, 1.2))
    K.box((-3.5, 0.45, 18), (0.5, 0.12, 1.1), wood("#7a5a3a", "#4a3a24", 8, 0.7), 0.2, 0.01); K.box((-3.5, 0.62, 18), (0.45, 0.25, 0.9), cloth("#5a4a3a"), 0.2, 0.08)
    for k in range(3): K.cyl((-1.5 + k * 0.4, 0.45, 26), 0.14, 0.3, pm("#5a5a60", 0.4, 0.6), 12)
    K.cyl((-1.0, 0.27, 27), 0.6, 0.06, pm("#1a2a3a", 0.05), 20)
    for k in range(10): K.box((5.8 + rnd.uniform(-0.3, 0.3), 0.4 + k * 0.04, 30 + rnd.uniform(-1, 1)), (1.4, 0.06, 0.12), wood("#6a5a42", "#3a3020", 8, 0.8), rnd.uniform(0, 3), 0.0)
    K.build()
    # ---------------- the apartment ----------------
    A = Kit("lnapt"); X0 = 40.0
    WP = stripes("lnwp", "#b8a888", "#9a8a6a", 26, 0); PL = grime("lnplaster", "#c8bca4", 0.35)
    A.box((X0 + 3, -0.05, 2.5), (6.2, 0.1, 5.4), wood("#5a4030", "#3a2618", 4, 0.6), 0, 0)
    A.box((X0 + 3, 3.25, 2.5), (6.2, 0.1, 5.4), grime("lnceil", "#c8c0b0", 0.3), 0, 0)
    A.box((X0 + 3, 1.6, 5.05), (6.2, 3.2, 0.1), WP, 0, 0.0); A.box((X0 - 0.05, 1.6, 2.5), (0.1, 3.2, 5.4), WP, 0, 0.0); A.box((X0 + 6.05, 1.6, 2.5), (0.1, 3.2, 5.4), WP, 0, 0.0)
    A.box((X0 + 3, 1.6, -0.05), (6.2, 3.2, 0.1), WP, 0, 0.0)
    for k in range(6):                            # wallpaper scraped off in patches (bare plaster), curling strips
        A.box((X0 + 0.6 + k * 0.9, 1.2 + rnd.uniform(0, 1.0), 4.99), (rnd.uniform(0.4, 0.8), rnd.uniform(0.5, 1.2), 0.01), PL, 0, 0.0)
        A.box((X0 + 0.8 + k * 0.9, 1.6, 4.95), (0.3, 0.8, 0.02), WP, 0, 0.0, 0.5, 0.2)
    A.box((X0 + 3, 1.75, 5.0), (1.4, 1.5, 0.12), pm("#c8d8e8", 0.3), 0, 0.0)                     # frosted window
    for k in range(3): A.box((X0 + 3, 1.0 + k * 0.75, 4.95), (1.5, 0.06, 0.08), wood("#e8e0d0", "#c8c0b0", 8, 0.6), 0, 0.005)
    A.box((X0 + 3, 1.75, 4.95), (0.06, 1.5, 0.08), wood("#e8e0d0", "#c8c0b0", 8, 0.6), 0, 0.005)
    for a in (0.7, -0.7): A.box((X0 + 3, 1.75, 4.92), (0.04, 2.0, 0.005), TAPE, 0, 0.0, 0, a)
    TW = wood("#6a4428", "#3a2414", 6, 0.5)
    A.box((X0 + 3, 0.76, 3.7), (1.6, 0.05, 1.0), TW, 0, 0.01)
    for dx in (-0.72, 0.72):
        for dz in (-0.42, 0.42): A.box((X0 + 3 + dx, 0.38, 3.7 + dz), (0.05, 0.76, 0.05), TW, 0, 0.005)
    A.box((X0 + 3, 0.785, 3.7), (1.5, 0.004, 0.9), cloth("#e8e0d0"), 0, 0.0)
    A.cyl((X0 + 3, 0.795, 3.6), 0.15, 0.012, pm("#f2ece0", 0.3), 28); A.torus((X0 + 3, 0.80, 3.6), 0.14, 0.006, pm("#2a5a9a", 0.3), 28, 6, "y")
    A.box((X0 + 3.0, 0.82, 3.6), (0.09, 0.04, 0.07), lib.bread("lnbread", "#5a3a22"), 0.2, 0.012)        # the 125 g ration
    A.box((X0 + 3.12, 0.82, 3.63), (0.09, 0.035, 0.07), lib.bread("lnbread2", "#4a3020"), -0.3, 0.012)
    A.box((X0 + 2.5, 0.8, 3.7), (0.22, 0.04, 0.14), brass(), 0, 0.01); A.cyl((X0 + 2.5, 0.86, 3.7), 0.08, 0.01, brass(), 18)  # letter scale
    A.box((X0 + 2.5, 0.84, 3.62), (0.12, 0.05, 0.005), pm("#efe6cc", 0.5), 0, 0.0)
    lathe("lncandle", [(0.0, 0.0), (0.025, 0.0), (0.025, 0.12), (0.0, 0.12)], (X0 + 3.55, 0.79, 3.9), pm("#efe2c4", 0.45), 12)
    from .void import flame, flame_mat
    flame("lnfl", (X0 + 3.55, 0.92, 3.9), 0.05, 0.01, mat_once("lnflm", lambda: flame_mat("lnflm")))
    point((X0 + 3.55, 0.98, 3.9), 8, (1.0, 0.6, 0.28), 0.02)
    # the little iron stove with a pot, a leather belt boiling in it; firewood made of chair legs and books
    A.box((X0 + 1.0, 0.35, 2.0), (0.5, 0.5, 0.6), pm("#2a2a2a", 0.5, 0.6), 0, 0.03)
    A.box((X0 + 1.0, 0.04, 2.0), (0.5, 0.08, 0.6), pm("#2a2a2a", 0.5, 0.6), 0, 0.01)
    A.box((X0 + 1.0, 0.3, 1.68), (0.2, 0.15, 0.02), em("#ff7a2a", 6.0), 0, 0.0)
    tube("lnpipe", [(X0 + 1.0, 0.6, 2.2), (X0 + 1.0, 2.4, 2.2), (X0 + 1.0, 2.6, 4.9)], 0.06, pm("#2a2a2a", 0.5, 0.6), 4, 1)
    A.cyl((X0 + 1.0, 0.72, 2.0), 0.16, 0.2, pm("#6a6a6a", 0.4, 0.7), 18)
    A.cyl((X0 + 1.0, 0.8, 2.0), 0.15, 0.02, pm("#5a4a32", 0.3), 18)
    tube("lnbelt", [(X0 + 0.95, 0.81, 1.95), (X0 + 1.05, 0.81, 2.05), (X0 + 1.1, 0.95, 2.0), (X0 + 1.2, 1.05, 1.9)], 0.012, pm("#4a2a14", 0.5))
    point((X0 + 1.0, 0.3, 1.5), 18, (1.0, 0.5, 0.2), 0.1)
    for k in range(5): A.box((X0 + 0.6 + k * 0.1, 0.05, 1.3), (0.06, 0.06, 0.5), TW, 0.1 * k, 0.005)
    for k in range(4): A.box((X0 + 1.6, 0.06 + k * 0.05, 1.4), (0.25, 0.05, 0.18), pm(("#7a1e22", "#1e3a5a", "#2a4a2a", "#6a4a1e")[k], 0.6), 0.2 * k, 0.003)
    A.box((X0 + 5.2, 0.4, 2.2), (1.4, 0.4, 2.0), cloth("#5a4a3a"), 0, 0.06); A.box((X0 + 5.2, 0.65, 2.2), (1.3, 0.12, 1.9), stripes("lnblk", "#7a3a2a", "#c8b88a", 16, 0), 0, 0.05)
    A.box((X0 + 5.6, 1.9, 4.95), (1.2, 0.04, 0.3), TW, 0, 0.005)
    lathe("lnmetro", [(0.0, 0.0), (0.08, 0.0), (0.02, 0.25), (0.0, 0.25)], (X0 + 5.3, 1.92, 4.85), wood("#3a2214", "#1a0e06", 8, 0.4), 4)
    A.box((X0 + 0.5, 1.9, 4.97), (0.4, 0.5, 0.01), paper("#efe4c8"), 0, 0.0); text("1942", (X0 + 0.5, 2.05, 4.955), 0.08, pm("#a81e22", 0.6), math.pi, "sans", 0.001)
    A.build()
    # the sled the mother pulls (shots 18 / 27): moves toward the camera along x -1.5
    from .c05_kit import empty
    SL = empty("sled"); sk = Kit("sledk"); W8 = wood("#7a5a3a", "#4a3a24", 8, 0.7)
    sk.box((0, 0.2, 0), (0.55, 0.06, 1.2), W8, 0, 0.01)
    for sd in (-1, 1): sk.box((sd * 0.25, 0.08, 0), (0.04, 0.06, 1.3), pm("#5a5a5a", 0.4, 0.6), 0, 0.01); sk.box((sd * 0.25, 0.14, 0.4), (0.04, 0.12, 0.04), W8, 0, 0.0)
    sk.box((0, 0.3, 0.2), (0.5, 0.18, 0.5), cloth("#7a3a2a"), 0, 0.06)
    for o in sk.build(): o.parent = SL
    rope = tube("sledrope", [(0, 0.25, -0.6), (0, 0.6, -1.2), (0, 0.95, -1.75)], 0.012, pm("#c8b890", 0.8)); rope.parent = SL
    def update(f):
        z = 20 - 0.075 * max(0, min(f, 2050) - 1937) if f < 2900 else 11.0
        SL.location = T(-1.5, H(-1.5, z) - 0.05, z)
    update(1937)
    # light: overcast winter daylight (cold), snow bounce; inside: grey window light, the candle and stove glow
    sun_light((0.5, -0.35, -0.8), 1.6, (0.85, 0.9, 1.0), 6)
    area((0, 25, -15), (0, 0, 20), 5000, (0.75, 0.8, 0.95), 30)
    area((X0 + 3, 1.8, 5.6), (X0 + 3, 1.0, 2.0), 260, (0.75, 0.85, 1.0), 1.4, 1.5)
    area((X0 + 3, 2.6, 0.5), (X0 + 3, 0.8, 3.0), 50, (1.0, 0.75, 0.5), 2)
    return {"update": update}
