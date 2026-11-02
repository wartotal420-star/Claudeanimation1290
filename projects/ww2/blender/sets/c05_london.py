# Chapter 5: a London street in the Blitz, 1940. Night (light "night": blackout, fires, searchlights, barrage balloons,
# St Paul's dome in the smoke at the end of the street) or the morning after (any other light: smoke haze, smouldering
# rubble, "BUSINESS AS USUAL").
# Layout (three coords): the road x -5..5 along z (-10..130), pavements |x| 5..7.5 (+0.14), terraces of brick
# houses (fronts at |x| 7.5) every 6 m in z from -6; one bombed gap at x -7.5..-13, z 16..28 (rubble, a burning room);
# the Underground entrance in the house front at x 7.5, z 10..14 (stairs down, roundel sign); a crashed bus nose-down
# in a crater at (1.5, 0, 46); a fire engine at (-3, 0, 34). St Paul's at (0, 0, 330) (dome top y ~111).
# Keep clear: road |x| < 4.5 for z 0..30 (firemen, Londoners), pavement x 5.5..7.2, z 4..20 (people out of the tube).
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, brick, paper, text, sign, poster, glassm, crate, barrel, stripes, R90
from .c05_kit import (sky, ground_mat, sun_light, area, point, spot, truck, lathe, tube, worn, mat_once, cached, searchlight, aim, fire, smoke_column, smoke_mat, empty)
from .front import sandbag_wall, sandmat, boxes

SHOPS = [("TOBACCONIST", "#1e2a3a"), ("J. HARRIS & SON  BUTCHERS", "#6a1e1e"), ("TEA ROOMS", "#1e3a2a"), ("GREENGROCER", "#3a4a1e"), None,
         ("THE ROSE & CROWN", "#3a1e10"), ("CHEMIST", "#1e2a4a"), ("IRONMONGER", "#2a2a2a"), ("BAKER", "#5a3a1e"), ("NEWSAGENT", "#2a1e3a"),
         ("DRAPER", "#1e3a3a"), ("BOOKSELLER", "#3a2a1e")]

def terrace(K, k, sx, spec, night, rnd, BR, BR2, TRIM, WIN, WINLIT, STONE, TAPE):
    zc = -6 + k * 6.0; X = sx * 7.5; face = sx * R90; h = 10.0 + (k % 3) * 1.6
    P = lambda d, y, u: (X - sx * d, y, zc + u)        # d = out from the facade toward the road
    W = BR if (k + (sx > 0)) % 3 else BR2
    K.box((sx * 11, h / 2, zc), (7, h, 6.0), W, 0, 0.0)
    K.box(P(0.08, h - 0.3, 0), (0.16, 0.25, 6.0), TRIM, 0, 0.01); K.box(P(0.05, h + 0.4, 0), (0.1, 0.9, 6.0), W, 0, 0.0)
    for u in (-1.6, 1.6):                                 # chimney stacks with pots
        K.box((sx * 9.0, h + 1.6, zc + u), (0.7, 1.6, 1.2), BR2, 0, 0.01)
        for j in range(3): K.cyl((sx * 9.0, h + 2.6, zc + u - 0.35 + j * 0.35), 0.09, 0.4, pm("#8a4a32", 0.8), 10)
    K.quad([(sx * 7.6, h + 0.85, zc - 3), (sx * 7.6, h + 0.85, zc + 3), (sx * 10.5, h + 3.0, zc + 3), (sx * 10.5, h + 3.0, zc - 3)], pm("#3a3e46", 0.6))
    for fl in range(int((h - 3.6) // 2.6)):
        y = 3.9 + fl * 2.6
        for u in (-1.7, 0.0, 1.7):
            lit = night and rnd.random() < 0.06
            K.box(P(0.01, y + 0.85, u), (0.02, 1.5, 0.9), WINLIT if lit else WIN, 0, 0)
            for uu in (-0.48, 0.48): K.box(P(0.05, y + 0.85, u + uu), (0.08, 1.62, 0.08), TRIM, 0, 0.005)
            K.box(P(0.05, y + 1.62, u), (0.08, 0.1, 1.04), TRIM, 0, 0.005); K.box(P(0.05, y + 0.85, u), (0.06, 0.06, 0.9), TRIM, 0, 0)
            K.box(P(0.1, y + 0.05, u), (0.2, 0.08, 1.1), STONE, 0, 0.005); K.box(P(0.05, y + 1.75, u), (0.1, 0.14, 1.1), STONE, 0, 0.005)
            for half in (0.42, 1.28):                   # anti-blast tape crosses on the panes
                for a in (0.62, -0.62): K.box(P(0.025, y + half, u), (0.006, 0.82, 0.035), TAPE, 0, 0.0, a, 0)
    if spec is None: return
    name, col = spec; FR = pm(col, 0.35)
    K.box(P(0.15, 1.5, 0), (0.3, 3.0, 6.0), FR, 0, 0.01)
    K.box(P(0.31, 1.45, -0.8), (0.02, 1.8, 3.6), WIN, 0, 0)
    for a in (0.45, -0.45): K.box(P(0.325, 1.45, -0.8), (0.006, 3.9, 0.05), TAPE, 0, 0.0, a, 0)
    K.box(P(0.33, 0.35, -0.8), (0.06, 0.7, 3.7), FR, 0, 0.005)
    K.box(P(0.05, 1.15, 1.9), (0.08, 2.3, 1.1), pm(col, 0.45), 0, 0.01)
    sign(K, P(0.36, 2.7, 0), 5.6, 0.5, face, name, col, K_.gold(), "serif", "#c8963a", 0.06)
    if (k + sx) % 2: sandbag_wall(f"lsb{k}{sx}", P(0.75, 0.0, -0.8), face, 6, 3, sandmat_c(), seed=k)

def sandmat_c(): return cached("lsand", sandmat)

def st_pauls(K, c, m, lead):
    x, y, z = c
    K.box((x, 15, z + 30), (60, 30, 120), m, 0, 0.1)                      # nave and choir
    K.box((x, 15, z), (110, 30, 36), m, 0, 0.1)                            # transepts
    for sd in (-1, 1):                                                     # the west towers
        K.box((x + sd * 20, 30, z - 30), (13, 60, 13), m, 0, 0.1)
        K.cyl((x + sd * 20, 66, z - 30), 5.5, 12, m, 16); K.cyl((x + sd * 20, 76, z - 30), 3.0, 10, lead, 12, "y", 0.4)
    K.cyl((x, 38, z), 26, 16, m, 40)                                      # the drum with its colonnade
    for k in range(32):
        a = k / 32 * math.tau; K.cyl((x + 27.5 * math.cos(a), 38, z + 27.5 * math.sin(a)), 0.9, 14, m, 8)
    K.cyl((x, 46.5, z + 0), 28.5, 1.6, m, 40)
    K.cyl((x, 51, z), 22, 8, m, 40)
    lathe_k(K, (x, 55, z), [(22.5, 0), (22, 8), (19, 18), (13, 26), (6, 30), (0, 31)], lead)
    K.cyl((x, 90, z), 3.2, 8, m, 16); K.cyl((x, 96, z), 1.5, 5, lead, 12, "y", 0.5); K.sphere((x, 100, z), 1.5, K_.gold(), 12)
def lathe_k(K, c, prof, m, seg=40):
    rings = []
    for r, h in prof:
        rings.append([(c[0] + r * math.cos(a / seg * math.tau), c[1] + h, c[2] + r * math.sin(a / seg * math.tau)) for a in range(seg)])
    from .c05_kit import loft_k
    loft_k(K, rings, m, 0.0, False, True)

def bus(K, c, yaw, pitch):
    """a red double-decker (front), nose-down in a bomb crater"""
    x, y, z = c; R = mat_once("lbusred", lambda: worn("lbusred", "#a81e1a", "#3a2a22", 0.45, 0.2, 6, 0.7, "#5a1a14"))
    cw, sw = math.cos(yaw), math.sin(yaw); cp, sp_ = math.cos(pitch), math.sin(pitch)
    def P(lx, ly, lz):
        ly2, lz2 = ly * cp - lz * sp_, ly * sp_ + lz * cp
        return (x + lx * cw + lz2 * sw, y + ly2, z - lx * sw + lz2 * cw)
    K.box(P(0, 2.2, 0), (2.4, 4.2, 8.0), R, yaw, 0.12, -pitch)
    for fl in (1.6, 3.3):
        for sd in (-1, 1): K.box(P(sd * 1.21, fl + 0.1, 0.4), (0.02, 0.8, 6.4), pm("#1a2230", 0.08), yaw, 0.0, -pitch)
    K.box(P(0, 3.95, 0), (2.42, 0.25, 8.02), pm("#e8e0c8", 0.6), yaw, 0.02, -pitch)
    K.box(P(0, 2.6, -4.01), (2.0, 0.6, 0.02), pm("#1a1a1a", 0.6), yaw, 0.0, -pitch)
    for sd in (-1, 1): K.cyl(P(sd * 0.95, 0.6, -2.6), 0.5, 0.3, pm("#141414", 0.85), 18, "x", None, yaw, -pitch)

def build(M, D):
    random.seed(1940); K_.reset(); rnd = random.Random(40); sid = D.get("id", 0)
    night = D["light"] == "night"
    if night:
        sky((0.01, 0.015, 0.04), (0.05, 0.04, 0.07), (0.32, 0.12, 0.05), sun_dir=(0.0, 0.08, 1.0), sun_col=(0.9, 0.3, 0.05), glow=0.9, strength=1.0)
    else:
        sky((0.36, 0.42, 0.52), (0.62, 0.6, 0.58), (0.86, 0.74, 0.6), sun_dir=(-0.6, 0.25, 0.75), sun_col=(1.0, 0.75, 0.45), glow=0.9, strength=1.0, clouds=0.5)
    K = Kit("ldn")
    ROAD = K_.wet_cobbles("lroad", "#3a3a40", "#2a2a30", 0.85 if night else 0.5, 1.4)
    SLAB = lib.brickmat("lslab", "#8a867e", "#7a766e", "#4a4640", 1.4, 0.5, 0.5, 0.6)
    BR = K_.brick("lbrick", "#b89a6a", "#a8885a", "#6a5e50", 4.0); BR2 = K_.brick("lbrick2", "#8a4a36", "#7a3e2e", "#5a4a42", 4.0)
    TRIM = grime("ltrim", "#e8e0cc", 0.3); STONE = grime("lstone", "#c8bca4", 0.35); TAPE = pm("#efe6c8", 0.8)
    WIN = pm("#10141c", 0.08, 0.2); WINLIT = K_.window_glow("lwin", "#ff9a50", 1.2)
    K.box((0, -0.05, 60), (10.2, 0.1, 160), ROAD, 0, 0)
    for sx in (-1, 1):
        K.box((sx * 6.25, 0.07, 60), (2.5, 0.14, 160), SLAB, 0, 0); K.box((sx * 5.05, 0.08, 60), (0.12, 0.16, 160), pm("#8a8680", 0.7), 0, 0.01)
        for k in range(26):  # white blackout kerb stripes
            K.box((sx * 5.08, 0.165, -6 + k * 5), (0.13, 0.01, 1.2), pm("#e8e4d8", 0.7), 0, 0.0)
    for k in range(22):
        for sx in (-1, 1):
            if sx < 0 and 2 <= k <= 3: continue        # the bombed gap
            spec = SHOPS[(k * 2 + (sx > 0)) % len(SHOPS)] if k < 12 else None
            terrace(K, k, sx, spec, night, rnd, BR, BR2, TRIM, WIN, WINLIT, STONE, TAPE)
    # ---------------- the bombed gap: party walls, a hanging fireplace, wallpaper, rubble, a burning room ----------------
    WP = stripes("lwallp", "#c8a8a0", "#a87a7a", 30, 1)
    for z in (15.0, 27.0): K.box((-11, 5.5, z), (7, 11, 0.4), BR2, 0, 0.0)
    for fl, y in enumerate((3.2, 5.8, 8.4)):
        K.box((-11, y + 1.2, 26.78), (6.6, 2.4, 0.02), WP if fl != 1 else stripes("lwallp2", "#a8c0a0", "#88a080", 24, 0), 0, 0.0)
        K.box((-11 + rnd.uniform(-1, 1), y, 26.6), (2.5 + rnd.uniform(0, 2), 0.25, 0.4), wood("#6a4a2a", "#3a2a1a", 8, 0.8), 0, 0.01)
    K.box((-10.5, 6.2, 26.6), (1.4, 0.12, 0.25), STONE, 0, 0.01); K.box((-10.5, 5.6, 26.68), (0.8, 1.1, 0.06), pm("#1a1410", 0.9), 0, 0.0)
    K.box((-11.8, 6.8, 26.7), (0.5, 0.65, 0.04), wood("#8a6a2a", "#4a3a1a", 9, 0.4), 0, 0.01, 0, 0.2)     # a picture still hanging, askew
    rub = []; brick_m = BR2
    for j in range(380):
        x, z = rnd.uniform(-13.5, -5.0), rnd.uniform(15.5, 27.5); top = 2.6 * max(0, 1 - ((x + 10) / 4.5) ** 2) * max(0, 1 - ((z - 21.5) / 7) ** 2)
        rub.append(((x, rnd.uniform(0, top) + 0.08, z), (0.24, 0.08, 0.12), rnd.uniform(0, 3), rnd.uniform(-0.6, 0.6)))
    boxes("lbricks", rub, brick_m, 0.0)
    for j in range(9): lib.blob(f"lrub{j}", T(-10 + rnd.uniform(-2.5, 2.5), 0.3, 21.5 + rnd.uniform(-4.5, 4.5)), (rnd.uniform(1.2, 2.4), rnd.uniform(0.5, 1.3), rnd.uniform(1.0, 2.0)), BR2, 0.4, j)
    for j in range(12): K.box((-9 + rnd.uniform(-3, 3), 0.8 + rnd.uniform(0, 1.5), 21 + rnd.uniform(-5, 5)), (rnd.uniform(1.5, 3.5), 0.15, 0.2), wood("#4a3a2a", "#2a1a10", 6, 0.9), rnd.uniform(0, 3), 0.01, rnd.uniform(-0.6, 0.6))
    K.box((-7.0, 1.0, 19.0), (0.8, 0.9, 1.4), cloth("#6a5a7a"), 0.3, 0.12, 0.3)             # an armchair in the rubble
    sign(K, (-5.3, 1.2, 25.4), 1.6, 0.5, -R90, "BUSINESS AS USUAL", "#f2ece0", pm("#1a1a1a", 0.6), "sans", None, 0.03)
    # ---------------- the Underground entrance (right side, z 10..14) ----------------
    K.box((7.45, 1.6, 12), (0.3, 3.2, 4.6), pm("#5a1e1a", 0.3), 0, 0.01)
    K.box((7.3, 1.2, 12), (0.4, 2.4, 3.0), pm("#0a0a0c", 0.9), 0, 0.0)
    for k in range(8): K.box((7.0 + k * 0.28, 0.05 - k * 0.18, 12), (0.3, 0.1, 2.8), pm("#6a6660", 0.7), 0, 0.005)
    K.box((7.3, 2.8, 12), (0.42, 0.6, 3.6), pm("#f0ece0", 0.4), 0, 0.01)
    text("UNDERGROUND", (7.07, 2.8, 12), 0.36, pm("#1e2a6a", 0.4), R90, "sans", 0.004, fit=3.2)
    K.cyl((6.7, 3.6, 12), 0.5, 0.06, pm("#c81e22", 0.35), 32, "x"); K.cyl((6.66, 3.6, 12), 0.33, 0.06, pm("#f0ece0", 0.4), 32, "x")
    K.box((6.62, 3.6, 12), (0.04, 0.2, 1.3), pm("#1e2a6a", 0.4), 0, 0.005); text("ALDWYCH", (6.59, 3.6, 12), 0.13, pm("#f0ece0", 0.4), R90, "sans", 0.002, fit=1.1)
    K.cyl((6.7, 2.0, 12), 0.05, 4.0, pm("#2a2a2a", 0.5, 0.5), 8)
    sign(K, (6.9, 2.2, 15.2), 1.2, 0.4, R90, "SHELTER", "#f0ece0", pm("#1a1a1a", 0.6), "sans", None, 0.03)
    # street furniture: a red phone box, a pillar box, lamp posts (hooded), an ARP post, a static water tank, bins
    RED = pm("#b81e1a", 0.35)
    K.box((5.9, 1.25, 4.5), (1.0, 2.5, 1.0), RED, 0, 0.03); K.box((5.9, 2.55, 4.5), (1.1, 0.2, 1.1), RED, 0, 0.05)
    for sd in (-1, 1):
        for k in range(6): K.box((5.9 + sd * 0.51, 0.7 + k * 0.28, 4.5), (0.02, 0.22, 0.75), pm("#2a2a30", 0.05), 0, 0.0)
    K.box((5.39, 2.35, 4.5), (0.03, 0.16, 0.7), pm("#f0ece0", 0.4), 0, 0.0); text("TELEPHONE", (5.37, 2.35, 4.5), 0.09, pm("#1a1a1a", 0.6), R90, "sans", 0.001, fit=0.66)
    K.cyl((-6.2, 0.75, 9), 0.28, 1.5, RED, 20); K.sphere((-6.2, 1.5, 9), 0.29, RED, 16, (1, 0.5, 1))
    K.box((-5.95, 1.15, 9), (0.04, 0.05, 0.25), pm("#1a1a1a", 0.8), 0, 0.0)
    for k in range(10):
        for sx in (-1, 1):
            z = -2 + k * 13 + (6 if sx > 0 else 0)
            if sx < 0 and 15 < z < 29: continue
            K.cyl((sx * 5.4, 2.4, z), 0.07, 4.8, pm("#2a3a2e", 0.5, 0.5), 10); K.box((sx * 5.0, 4.75, z), (0.9, 0.06, 0.06), pm("#2a3a2e", 0.5, 0.5), 0, 0.005)
            K.cyl((sx * 4.6, 4.65, z), 0.18, 0.2, pm("#1a1a1a", 0.5, 0.3), 12, "y", 0.12)
            K.box((sx * 5.4, 0.9, z), (0.16, 0.5, 0.16), pm("#e8e4d8", 0.7), 0, 0.0)          # white blackout bands
    K.box((-6.3, 0.8, 34), (2.0, 1.6, 3.0), mat_once("lewtank", lambda: worn("lewtank", "#4a5a4a", "#2a2a2a", 0.6, 0.4, 6, 0.6)), 0, 0.03)
    text("E.W.S.", (-5.29, 1.0, 34), 0.3, pm("#f0e8d0", 0.6), R90, "sans", 0.002)
    sign(K, (6.4, 2.3, 22), 1.0, 0.45, R90, "A.R.P.", "#1a1a1a", pm("#f0e8d0", 0.6), "sans", None, 0.04)
    for k, (x, z) in enumerate(((6.9, 2), (6.8, 18), (-6.9, 6))): barrel(K, (x, 0.55, z), 0.28, 0.75, pm("#3a3a3a", 0.5, 0.5), pm("#2a2a2a", 0.5, 0.5))
    # crater with the bus, the fire engine with ladders and hoses (night), sandbags, debris on the road
    for j in range(40):
        a = j / 40 * math.tau; K.box((1.5 + 5.2 * math.cos(a), 0.25, 46 + 4.2 * math.sin(a)), (1.4, 0.5 + rnd.random() * 0.4, 0.8), pm("#3a3634", 0.9), -a, 0.15, rnd.uniform(-0.3, 0.3))
    K.cyl((1.5, -0.05, 46), 5.0, 0.12, pm("#0e0c0c", 0.9), 30, "y", None, 0, 0, 0)
    bus(K, (1.5, -1.6, 46), 0.25, -0.45)
    if night:
        def ladder(K2, P, yaw):
            for sd in (-1, 1): K2.box(P(-1.0, 2.0, sd * 0.35), (5.0, 0.08, 0.08), pm("#c8b890", 0.6), yaw, 0.01, 0, 0.12)
            for k in range(12): K2.box(P(-3.2 + k * 0.4, 1.75 + k * 0.045, 0), (0.05, 0.05, 0.7), pm("#c8b890", 0.6), yaw, 0.0)
            K2.box(P(-1.45, 1.4, 0), (3.0, 0.6, 2.0), mat_once("lfirered", lambda: worn("lfirered", "#b81e1a", "#3a2a22", 0.4, 0.2, 9, 0.75)), yaw, 0.04)
            K2.cyl(P(-0.3, 1.9, 0.8), 0.25, 0.4, brass(), 14, "x", None, yaw)
        truck("fengine", (-2.5, 0, 34), R90 * 1.1, "#b81e1a", lights=True, load=ladder)
        for k, pts in enumerate((((-2.2, 1.0, 33), (-3.5, 0.05, 30), (-5.5, 0.05, 27), (-7.5, 1.0, 24)), ((-2.8, 1.0, 33.5), (-1.0, 0.05, 29), (0.5, 0.05, 24), (2.0, 0.05, 20)))):
            tube(f"hose{k}", list(pts), 0.06, pm("#c8b890", 0.7))
    sand = sandmat_c()
    sandbag_wall("lsb_a", (6.6, 0.14, 9.0), R90, 4, 4, sand, 2); sandbag_wall("lsb_b", (6.6, 0.14, 15.0), R90, 4, 4, sand, 3)
    for j in range(60): K.box((rnd.uniform(-4.5, 4.5), 0.04, rnd.uniform(-5, 60)), (rnd.uniform(0.1, 0.35), 0.06, rnd.uniform(0.08, 0.2)), BR2 if j % 2 else pm("#3a3634", 0.8), rnd.uniform(0, 3), 0.0)
    # ---------------- far away: more roofs, St Paul's, barrage balloons ----------------
    PORT = grime("lportland", "#b8b0a0", 0.3); LEAD = pm("#5a6a70", 0.5, 0.4)
    st_pauls(K, (0, 0, 330), PORT, LEAD)
    for j in range(70):
        x, z = rnd.uniform(-160, 160), rnd.uniform(140, 520)
        if abs(x) < 60 and 260 < z < 400: continue
        hh_ = rnd.uniform(10, 26); K.box((x, hh_ / 2, z), (rnd.uniform(12, 30), hh_, rnd.uniform(12, 30)), BR if j % 2 else BR2, rnd.uniform(-0.2, 0.2), 0.0)
        for c in range(2): K.box((x + rnd.uniform(-5, 5), hh_ + 1.5, z + rnd.uniform(-5, 5)), (0.8, 3, 0.8), BR2, 0, 0.0)
    K.box((0, -0.05, 330), (600, 0.1, 500), pm("#2a2a2e", 0.8), 0, 0.0)
    BAL = pm("#9aa0a4" if not night else "#4a5056", 0.5)
    for j, (x, y, z) in enumerate(((-90, 140, 260), (60, 160, 300), (130, 120, 420), (-30, 180, 470), (-180, 150, 380))):
        K.sphere((x, y, z), 9, BAL, 18, (1, 1, 2.2));
        for sd in (-1, 1): K.box((x + sd * 4, y, z + 18), (0.4, 6, 6), BAL, 0, 0.5)
        K.box((x, y + 5, z + 18), (6, 0.4, 6), BAL, 0, 0.5)
        tube(f"cable{j}", [(x, y - 8, z), (x + 3, 0, z - 5)], 0.08, pm("#2a2a2a", 0.5), 2, 0)
    K.build()
    # ---------------- light, fire and smoke ----------------
    smm = smoke_mat("lsmoke", "#1e1a1a" if night else "#6a625e", 0.55)
    if night:
        lib.light("SUN", (0, 0, 10), 0.25, (0.5, 0.62, 1.0), math.radians(1), (math.radians(60), 0, math.radians(-150)))
        for k, (c, s) in enumerate((((-10.5, 0.4, 24.0), 1.2), ((-11.5, 3.2, 26.2), 0.8), ((-9.0, 0.3, 18.5), 0.9), ((-14, 10.2, 40), 1.6), ((12, 10.5, 64), 1.8), ((-30, 18, 200), 6), ((40, 15, 240), 7), ((-50, 20, 300), 8))):
            fire(f"lfire{k}", c, s, seed=k + 3, energy=900 * s * s if k < 5 else 30000)
        area((-9, 6, 22), (0, 1.5, 12), 1800, (1.0, 0.45, 0.15), 6)                         # fire glow onto the street
        area((0, 12, -10), (0, 1.5, 15), 1600, (0.45, 0.55, 1.0), 10)                         # cool moon fill from behind the camera
        area((0, 60, 360), (0, 40, 330), 90000, (1.0, 0.45, 0.15), 120)                      # the burning City lights St Paul's from behind
        for k, (x, z, h, r) in enumerate(((-10, 22, 24, 2.5), (-14, 42, 40, 4), (12, 66, 50, 5), (-35, 210, 180, 30), (45, 250, 200, 35), (-60, 310, 220, 40))):
            smoke_column(f"lsm{k}", (x, 4 if k < 3 else 30, z), h, r, r * 3, smm, drift=(25, 30), seed=k + 2, puffs=10)
        beams = []
        for k, (x, z) in enumerate(((-120, 260), (40, 300), (160, 420), (-40, 520), (230, 360))):
            beams.append((searchlight(f"sl{k}", (x, 0, z), 0, 1.0, 900, 0.8, 16, 5.0), (x, z), k))
        def update(f):
            for o, (x, z), k in beams:
                aim(o, (x, 0, z), -0.6 + 0.9 * math.sin(f * 0.012 + k * 1.7), 0.9 + 0.25 * math.sin(f * 0.009 + k * 2.3))
        update(1188)
        return {"update": update}
    else:
        sun_light((0.55, -0.35, 0.75), 4.5, (1.0, 0.78, 0.55), 2.0)
        area((0, 15, -12), (0, 1.5, 15), 2800, (0.75, 0.8, 0.95), 14)
        for k, (x, z, h, r) in enumerate(((-10, 22, 20, 1.5), (-14, 42, 30, 3), (-35, 210, 120, 25), (45, 250, 140, 30))):
            smoke_column(f"lsm{k}", (x, 2 if k < 2 else 30, z), h, r, r * 3, smm, drift=(15, 20), seed=k + 2, puffs=9)
        fire("lember", (-10.5, 0.4, 24.0), 0.4, seed=2, energy=150)
        return {}
