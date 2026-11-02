# Wall Street 1929 (shot 18), sets.ts buildWallst layout: office x -8..8, z -6..10, back wall z 7 with the big chart
# board (x -3.2..3.2, y 1.2..4.3, the chart line itself is an exported effect card), four desks at x -4.5 + 3k, z 2.5.
# The chart card sits at z 6.72 (x -2.8..2.8, y 1.35..4.15): nothing between it and the board. Brokers stand at
# z 1.4 in front of the desks and at z 0.4. Look: a mahogany-and-marble brokerage - green damask walls, gilt trim,
# quotation boards in chalk, banker's lamps, candlestick phones, ticker tape everywhere, a skyline in the windows.
import bpy, math, random
import lib
from lib import T
from . import kit_sbpw as K_
from .kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, stripes, paper, text, flat_text, sign, poster, R90

QUOTES = [("U.S. STEEL", "261", "204"), ("GEN. MOTORS", "72", "40"), ("RADIO CORP", "114", "44"), ("AT & T", "304", "230"),
          ("GEN. ELECTRIC", "396", "283"), ("ANACONDA", "131", "70"), ("CHRYSLER", "135", "52"), ("WESTINGHOUSE", "289", "160")]

def build(M, D):
    random.seed(1929); K_.reset(); rnd = random.Random(18)
    K = K_.Kit("wallst")
    FL = lib.tiles("wsfloor", "#e8e0cc", "#2a3a32", "#1a1a18", 2.0); RUN = lib.carpet("wsrun", "#7a1a1e", "#c8a24a")
    DAM = lib.wallpaper("wsdamask", "#2a5a42", "#1e4a34"); MAH = wood("#5a2414", "#2a0e06", 6, 0.35); MAHL = wood("#7a3a1e", "#3a160a", 6, 0.3)
    DESK = wood("#6a2e18", "#2e1008", 7, 0.3); GREEN = pm("#2a5a3a", 0.6); BOARD = pm("#141e1a", 0.85)
    CHALK = pm("#efece2", 0.9); CHR = pm("#e85a4a", 0.9); TAPE = paper("#f4ecd6", 0.15); INK = pm("#1a1a1a", 0.7)
    # ---------------- shell ----------------
    K.box((0, -0.05, 2), (17, 0.1, 17), FL, 0, 0)
    K.box((0, 0.006, 1.0), (2.2, 0.012, 9), RUN, 0, 0)
    K.box((0, 5.05, 2), (17, 0.1, 17), grime("wsceil", "#c8b898", 0.2), 0, 0)
    for k in range(7): K.box((0, 4.9, -5 + k * 2.4), (16, 0.22, 0.22), gold(), 0, 0.01)
    for k in range(7): K.box((-7.2 + k * 2.4, 4.9, 2), (0.22, 0.22, 16), wood("#e8dcc0", "#d0c4a8", 4), 0, 0.01)
    K.box((0, 2.5, 7.15), (17, 5, 0.3), DAM, 0, 0)
    K.box((0, 2.5, -6.15), (17, 5, 0.3), DAM, 0, 0)
    for sx in (-1, 1): K.box((sx * 8.15, 2.5, 2), (0.3, 5, 17), DAM, 0, 0)
    # mahogany wainscot with raised panels, chair rail, gilt picture rail, cornice
    K.box((0, 0.6, 6.96), (16, 1.2, 0.08), MAH, 0, 0.01)
    for j in range(16): K.box((-7.5 + j, 0.62, 6.91), (0.8, 0.85, 0.03), MAHL, 0, 0.012)
    K.box((0, 1.24, 6.9), (16, 0.08, 0.12), MAH, 0, 0.01)
    for sx in (-1, 1):
        K.box((sx * 7.96, 0.6, 2), (0.08, 1.2, 16), MAH, 0, 0.01); K.box((sx * 7.9, 1.24, 2), (0.12, 0.08, 16), MAH, 0, 0.01)
        for j in range(15): K.box((sx * 7.91, 0.62, -5 + j), (0.03, 0.85, 0.8), MAHL, 0, 0.012)
    K.box((0, 4.65, 6.95), (16, 0.3, 0.1), gold(), 0, 0.02)
    # ---------------- the chart board (card at z 6.72 sits in front of it) ----------------
    K.box((0, 2.75, 6.92), (6.2, 3.0, 0.06), BOARD, 0, 0.01)
    K_._frame(K, (0, 2.75, 6.88), 6.2, 3.0, 0.0, gold(), 0.16, 0.1)
    for k in range(11): K.box((-2.8 + k * 0.56, 2.75, 6.885), (0.012, 2.8, 0.004), pm("#3a5a4a", 0.8), 0, 0)
    for k in range(6): K.box((0, 1.5 + k * 0.5, 6.885), (5.9, 0.012, 0.004), pm("#3a5a4a", 0.8), 0, 0)
    sign(K, (0, 1.0, 6.86), 3.4, 0.22, 0.0, "DOW JONES INDUSTRIAL AVERAGE", "#2a1208", gold(), "serif", None, 0.04)
    sign(K, (0, 4.47, 6.86), 3.0, 0.24, 0.0, "NEW YORK  ·  OCTOBER 1929", "#2a1208", gold(), "serif", None, 0.04)
    for sx in (-1, 1):   # brass picture lamps over the board
        K.cyl((sx * 1.6, 4.3, 6.6), 0.07, 0.9, brass(), 14, "x"); K.box((sx * 1.6, 4.35, 6.8), (0.04, 0.04, 0.3), brass(), 0, 0)
        K.box((sx * 1.6, 4.27, 6.6), (0.8, 0.02, 0.06), em("#ffd8a0", 10), 0, 0)
    # ---------------- quotation boards in chalk ----------------
    for sx in (-1, 1):
        x = sx * 4.75
        K.box((x, 2.9, 6.92), (2.2, 2.6, 0.05), BOARD, 0, 0.01)
        K_._frame(K, (x, 2.9, 6.89), 2.2, 2.6, 0.0, MAH, 0.1, 0.07)
        text("QUOTATIONS", (x, 4.0, 6.885), 0.12, gold(), 0, "serif", 0.002)
        for i in range(4):
            name, hi, lo = QUOTES[i + (0 if sx < 0 else 4)]; y = 3.6 - i * 0.5
            text(name, (x + 1.0, y, 6.885), 0.125, CHALK, 0, "mono", 0.001, "LEFT")
            text(hi, (x - 0.42, y, 6.885), 0.15, CHALK, 0, "mono", 0.001)
            text(lo, (x - 0.82, y - 0.02, 6.885), 0.15, CHR, 0, "mono", 0.001)
            K.box((x - 0.42, y + 0.0, 6.884), (0.32, 0.012, 0.002), CHALK, 0, 0, 0, -0.35)   # struck-through high
            K.box((x, y - 0.22, 6.886), (2.0, 0.006, 0.002), pm("#5a6a60", 0.8), 0, 0)
        K.box((x, 1.55, 6.82), (2.0, 0.04, 0.1), MAH, 0, 0.005)
        for q in range(3): K.box((x - 0.4 + q * 0.2, 1.585, 6.82), (0.08, 0.02, 0.02), CHALK, q, 0)
    # ---------------- windows with the Manhattan skyline beyond ----------------
    for sx in (-1, 1):
        x = sx * 6.85
        K_._frame(K, (x, 2.75, 6.92), 1.3, 2.6, 0.0, MAH, 0.14, 0.12)
        for q in range(1, 3): K.box((x, 1.45 + q * 0.87, 6.95), (1.3, 0.04, 0.04), MAH, 0, 0)
        K.box((x, 2.75, 6.95), (0.04, 2.6, 0.04), MAH, 0, 0)
        for dx in (-0.85, 0.85): K.box((x + dx, 2.8, 6.85), (0.4, 3.1, 0.05), cloth("#7a1e22"), 0, 0.01)
        K.box((x, 4.4, 6.84), (1.9, 0.25, 0.08), cloth("#7a1e22"), 0, 0.01)
    # the view out: a glowing autumn sky with the skyline painted in front of it, tiny lit office windows
    r2 = random.Random(5)
    for sx in (-1, 1):
        x = sx * 6.85
        K.box((x, 3.35, 6.995), (1.3, 1.4, 0.01), em("#e8b888", 2.4), 0, 0)
        K.box((x, 2.05, 6.995), (1.3, 1.2, 0.01), em("#9ab4d8", 2.0), 0, 0)
        u = -0.62
        while u < 0.6:
            w = r2.uniform(0.12, 0.26); h = r2.uniform(0.5, 1.9); w = min(w, 0.65 - u)
            K.box((x + u + w / 2, 1.45 + h / 2, 6.985), (w, h, 0.005), pm("#3a4258", 0.8), 0, 0)
            if h > 1.4: K.box((x + u + w / 2, 1.45 + h + 0.12, 6.985), (0.03, 0.25, 0.005), pm("#3a4258", 0.8), 0, 0)
            for q in range(int(h * 6)):
                if r2.random() < 0.35: K.box((x + u + r2.uniform(0.02, w - 0.02), 1.5 + q * 0.15, 6.982), (0.015, 0.025, 0.002), em("#ffd890", 4), 0, 0)
            u += w + 0.01
    # ---------------- desks: blotters, banker's lamps, candlestick phones, ledgers, ticker, tape ----------------
    for k in range(4):
        x = -4.5 + k * 3
        K.box((x, 0.76, 2.5), (2.2, 0.06, 1.0), DESK, 0, 0.02)
        for dx in (-0.75, 0.75):
            K.box((x + dx, 0.38, 2.5), (0.6, 0.76, 0.9), DESK, 0, 0.02)
            for j in range(3):
                K.box((x + dx, 0.15 + j * 0.22, 2.04), (0.5, 0.18, 0.02), MAHL, 0, 0.005)
                K.cyl((x + dx, 0.24 + j * 0.22, 2.02), 0.015, 0.02, brass(), 8, "z")
        K.box((x, 0.6, 2.06), (0.9, 0.3, 0.04), MAH, 0, 0.005)
        K.box((x, 0.795, 2.45), (1.0, 0.01, 0.6), GREEN, 0, 0)
        for dx in (-0.5, 0.5): K.box((x + dx, 0.8, 2.45), (0.06, 0.016, 0.62), pm("#3a1a0e", 0.45), 0, 0.002)
        # banker's lamp
        K.cyl((x - 0.75, 0.8, 2.75), 0.08, 0.03, brass(), 16); K.cyl((x - 0.75, 0.97, 2.75), 0.012, 0.32, brass(), 8)
        K.cyl((x - 0.75, 1.14, 2.66), 0.09, 0.42, pm("#1e7a3e", 0.1), 16, "x", None, 0, 0, 0)
        K.cyl((x - 0.75, 1.1, 2.66), 0.04, 0.3, em("#ffe0a8", 12), 8, "x")
        lib.light("POINT", T(x - 0.75, 1.02, 2.62), 22, (1.0, 0.78, 0.5), 0.05)
        # candlestick telephone
        K.cyl((x + 0.6, 0.81, 2.75), 0.07, 0.03, INK, 16); K.cyl((x + 0.6, 0.98, 2.75), 0.015, 0.33, INK, 8)
        K.cyl((x + 0.6, 1.15, 2.72), 0.035, 0.05, INK, 12, "z"); K.cyl((x + 0.6, 1.16, 2.69), 0.02, 0.03, brass(), 10, "z")
        K.cyl((x + 0.66, 1.05, 2.75), 0.022, 0.12, INK, 10); K.box((x + 0.64, 1.1, 2.75), (0.04, 0.012, 0.012), brass(), 0, 0)
        # ledger, inkwell + pen, scattered papers, cigar ashtray
        K.box((x + 0.15, 0.82, 2.75), (0.32, 0.05, 0.24), pm("#6a1e22", 0.55), 0.1, 0.01)
        K.box((x - 0.2, 0.81, 2.35), (0.38, 0.02, 0.27), paper("#f2ead8", 0.2), -0.15, 0)
        flat_text("SELL", (x - 0.2, 0.822, 2.3), 0.07, pm("#b01e1e", 0.6), -0.15, "sans")
        K.cyl((x + 0.45, 0.83, 2.35), 0.04, 0.05, pm("#1a1a2a", 0.05), 12); K.cyl((x + 0.47, 0.88, 2.35), 0.005, 0.15, gold(), 6, "y", None, 0, 0.4)
        for j in range(5): K.box((x + rnd.uniform(-0.6, 0.4), 0.8 + j * 0.003, 2.45 + rnd.uniform(-0.25, 0.2)), (0.21, 0.003, 0.28), paper(["#f2ead8", "#e8f0f0", "#f4e4c8"][j % 3], 0.2), rnd.uniform(-0.6, 0.6), 0)
        K.cyl((x - 0.35, 0.81, 2.8), 0.06, 0.02, pm("#c8c0b0", 0.2, 0.6), 14); K.cyl((x - 0.31, 0.83, 2.8), 0.012, 0.12, pm("#4a2412", 0.7), 8, "x", None, 0.6)
        # small ticker under a glass dome on every other desk, spitting tape onto the floor
        if k % 2 == 0:
            K.cyl((x + 0.2, 0.86, 2.3), 0.09, 0.08, brass(), 14); K.sphere((x + 0.2, 0.98, 2.3), 0.1, lib.glass("kdome"), 14)
        tape(K, [(x + 0.2, 0.83, 2.1), (x + 0.3, 0.78, 1.95), (x + 0.45, 0.45, 1.92), (x + 0.35, 0.02, 1.7), (x + 0.0, 0.004, 1.2), (x - 0.4, 0.004, 1.3)], TAPE, rnd)
        # chair (leather, brass studs) behind the desk
        L = cloth("#5a1e12")
        K.box((x, 0.46, 3.3), (0.52, 0.08, 0.5), L, 0, 0.03); K.box((x, 0.88, 3.55), (0.52, 0.8, 0.08), L, 0, 0.03)
        for dx in (-0.27, 0.27): K.box((x + dx, 0.62, 3.3), (0.06, 0.06, 0.5), MAH, 0, 0.01)
        K.cyl((x, 0.22, 3.3), 0.03, 0.4, iron(), 8)
        for a in range(5): K.box((x + 0.2 * math.cos(a * 1.257), 0.04, 3.3 + 0.2 * math.sin(a * 1.257)), (0.4, 0.03, 0.04), iron(), -a * 1.257, 0)
    # ---------------- the big ticker on its pedestal, tape heaps, a waste basket, safe, coat stand, palms ----------------
    K.cyl((5.5, 0.5, 0.5), 0.15, 1.0, MAH, 16); K.cyl((5.5, 0.05, 0.5), 0.3, 0.1, MAH, 16); K.cyl((5.5, 1.02, 0.5), 0.2, 0.06, brass(), 16)
    K.sphere((5.5, 1.2, 0.5), 0.2, lib.glass("kdome2"), 18); K.cyl((5.5, 1.12, 0.5), 0.1, 0.1, brass(), 12)
    tape(K, [(5.5, 1.1, 0.3), (5.4, 0.9, 0.15), (5.3, 0.4, 0.0), (5.1, 0.004, -0.3), (4.4, 0.004, -0.5), (4.0, 0.004, 0.0), (4.6, 0.004, 0.3)], TAPE, rnd)
    for i in range(10):   # curled tape scattered on the floor
        tape(K, [(rnd.uniform(-6.5, 6.5), 0.004, rnd.uniform(-1.5, 4.0))] + [None] * 4, TAPE, rnd)
    K.cyl((-6.0, 0.25, 3.4), 0.2, 0.5, wood("#b8905a", "#6a4a22", 30, 0.8), 14, "y", 0.24)
    for i in range(5): K.sphere((-6.0 + rnd.uniform(-0.12, 0.12), 0.52, 3.4 + rnd.uniform(-0.12, 0.12)), 0.07, paper("#f2ead8", 0.2), 8)
    K.box((-6.9, 0.65, 5.0), (1.0, 1.3, 1.0), pm("#2a2e34", 0.3, 0.8), 0, 0.04)
    K.cyl((-6.9, 0.8, 4.48), 0.1, 0.04, brass(), 24, "z"); K.box((-6.9, 1.15, 4.49), (0.6, 0.08, 0.02), gold(), 0, 0)
    text("SAFE CO.", (-6.9, 1.15, 4.475), 0.05, pm("#2a1a10", 0.6), 0, "serif", 0.001)
    K.cyl((-6.8, 0.9, 1.0), 0.03, 1.8, MAH, 8); K.cyl((-6.8, 0.03, 1.0), 0.25, 0.04, MAH, 14)
    for a in range(4):
        aa = a * R90; K.box((-6.8 + 0.12 * math.cos(aa), 1.75, 1.0 + 0.12 * math.sin(aa)), (0.25, 0.03, 0.03), brass(), -aa, 0, 0, 0.5)
    K.cyl((-6.65, 1.82, 1.0), 0.17, 0.02, cloth("#2a2a2e"), 14); K.cyl((-6.65, 1.9, 1.0), 0.1, 0.14, cloth("#2a2a2e"), 14)
    K.box((-6.95, 1.3, 1.0), (0.12, 0.85, 0.35), cloth("#3a3a44"), 0, 0.03)
    for k in range(2):
        px = k * 13.6 - 6.8
        K.cyl((px, 0.22, 6.2), 0.25, 0.44, pm("#8a4a2a", 0.5), 16, "y", 0.3)
        r3 = random.Random(k)
        for i in range(9):
            a = i * 0.7; K.box((px + 0.35 * math.cos(a), 0.9 + r3.uniform(0, 0.4), 6.2 + 0.35 * math.sin(a)), (0.6, 0.02, 0.16), cloth("#2e6a2a"), -a, 0, 0, 0.5)
        K.cyl((px, 0.7, 6.2), 0.03, 0.6, wood("#5a4a2a", "#3a2a1a", 4), 8)
    # brass gallery rail in front of the boards
    for j in range(9): K.cyl((-6 + j * 1.5, 0.5, 6.0), 0.025, 1.0, brass(), 10); K.sphere((-6 + j * 1.5, 1.02, 6.0), 0.04, brass(), 10)
    K.cyl((0, 0.98, 6.0), 0.02, 12.2, brass(), 10, "x")
    # ---------------- light ----------------
    for sx in (-1, 1):
        for z in (-0.5, 3.5):
            K.cyl((sx * 3, 4.4, z), 0.01, 0.9, brass(), 6)
            K.sphere((sx * 3, 3.85, z), 0.22, em("#ffe2b0", 6.0), 18)
            K.cyl((sx * 3, 4.05, z), 0.1, 0.08, brass(), 12)
            lib.light("POINT", T(sx * 3, 3.6, z), 140, (1.0, 0.78, 0.5), 0.2)
    for sx in (-1, 1): lib.light("AREA", T(sx * 6.85, 2.75, 6.6), 160, (0.7, 0.82, 1.0), 1.3, (math.radians(90), 0, math.radians(180)), 2.6)
    lib.light("AREA", T(0, 4.2, 5.8), 160, (1.0, 0.85, 0.65), 6.0, (math.radians(30), 0, 0), 1.0)    # wash on the boards
    lib.light("AREA", T(0, 3.5, -5.5), 300, (1.0, 0.82, 0.62), 7, (math.radians(75), 0, 0))
    K.build()
    W = bpy.context.scene.world; bg = W.node_tree.nodes.get("Background")
    if bg: bg.inputs[0].default_value = (0.03, 0.025, 0.02, 1); bg.inputs[1].default_value = 0.3
    return {}

def tape(K, pts, m, rnd):
    """a paper ticker tape ribbon through the given points (None = random curl continuing on the floor)"""
    P = [pts[0]]
    for p in pts[1:]:
        if p is None:
            x, y, z = P[-1]; a = rnd.uniform(0, 6.28); P.append((x + 0.3 * math.cos(a), 0.004, z + 0.3 * math.sin(a)))
        else: P.append(p)
    for (x0, y0, z0), (x1, y1, z1) in zip(P, P[1:]):
        n = 6
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            a = (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0, z0 + (z1 - z0) * t0); b = (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1, z0 + (z1 - z0) * t1)
            w = 0.018 + 0.01 * math.sin(i)
            dx, dz = b[0] - a[0], b[2] - a[2]; L = math.hypot(dx, dz) or 1e-4; nx, nz = -dz / L * w, dx / L * w
            if L < 0.02: nx, nz = w, 0.0
            K.quad([(a[0] - nx, a[1] + 0.002 * i, a[2] - nz), (a[0] + nx, a[1] + 0.002 * i, a[2] + nz), (b[0] + nx, b[1] + 0.002 * i, b[2] + nz), (b[0] - nx, b[1] + 0.002 * i, b[2] - nz)], m)
