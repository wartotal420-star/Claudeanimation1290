# The money printing press (shots 13, 26), sets.ts buildPress layout: room x -8..8, z -6..8 (brick back wall z 8),
# the press at x 0, z 2..4 (rollers at y 1.3/1.8/2.3, z 3; flywheel x 1.7), table at (3.8, 2), cash piles at
# x -2.5..-1.6, z 0.3..0.9 growing in shot 13, the official at (2.3, 1.7), the worker at (-2.6, 1.6).
# Shot 26: the newspaper card lies on the table top (y 0.915) at x 3.55..4.05, z 1.67..2.33 - keep that spot clear.
# Look: a sooty state print works - brick, green cast-iron press, an overhead line shaft with leather belts, sheets
# of fresh banknotes drying on lines, warm green-shaded lamps against cool window light.
import bpy, math, random
import lib
from lib import T, hexc, nodes, ramp
from . import kit_sbpw as K_
from .kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, stripes, paper, text, flat_text, sign, poster, barrel, crate, R90

def banknote(name="note", a="#a8b48a", b2="#6a7a5a"):
    """a printed note: pale paper with fine guilloche waves and a darker border tint"""
    def mk():
        m = lib.principled(name, hexc(a), 0.8); t, n, l = nodes(m)
        tc = n.new("ShaderNodeTexCoord"); wv = n.new("ShaderNodeTexWave"); wv.wave_type = "RINGS"; wv.inputs["Scale"].default_value = 40; wv.inputs["Distortion"].default_value = 2
        l.new(tc.outputs["Object"], wv.inputs["Vector"])
        r = ramp(n, l, wv.outputs["Fac"], [(0.4, hexc(a)), (0.6, hexc(b2))])
        l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"]); return m
    return K_.cached("bn" + name + a, mk)

PILES = []
def build(M, D):
    random.seed(1923); K_.reset(); rnd = random.Random(13)
    K = K_.Kit("press")
    FL = lib.brickmat("prfloor", "#6a4a32", "#5a3e28", "#20140c", 1.2, 0.18, 3.0, 0.6)   # long floor boards
    BRK = K_.brick("prbrick", "#a85a40", "#7e3e2a", "#4a3a34", 4.5)
    IRONM = iron("#2a2e34"); GREEN = pm("#2a5a42", 0.35, 0.5); GREEND = pm("#1e3e2e", 0.4, 0.5); RED = pm("#9a2a20", 0.35, 0.4)
    PAPER = paper("#efe6d0"); NOTE = banknote(); NOTE2 = banknote("note2", "#c8a8b8", "#8a6a7a"); NOTE3 = banknote("note3", "#d8c08a", "#a07a4a")
    BAND = pm("#e8dcb8", 0.8); TABW = wood("#7a4a2a", "#4a2614", 14, 0.4)
    # ---------------- shell ----------------
    K.box((0, -0.05, 1), (17, 0.1, 15), FL, 0, 0)
    for (x, z, r) in ((-1.2, 1.2, 0.5), (0.8, 4.8, 0.7), (-3.5, 5.5, 0.4), (2.6, 0.2, 0.35)):   # ink stains
        K.cyl((x, 0.003, z), r, 0.004, pm("#14141c", 0.25), 20, "y", None, rnd.uniform(0, 3))
    K.box((0, 5.05, 1), (17, 0.1, 15), grime("prceil", "#c8b898", 0.35), 0, 0)
    for k in range(5): K.box((0, 4.78, -4 + k * 3), (16, 0.34, 0.26), wood("#4a2c18", "#2a160a", 3), 0, 0.02)
    K.box((0, 2.5, 8.15), (17, 5, 0.3), BRK, 0, 0)
    K.box((0, 2.5, -6.15), (17, 5, 0.3), BRK, 0, 0)
    for sx in (-1, 1): K.box((sx * 8.15, 2.5, 1), (0.3, 5, 15), BRK, 0, 0)
    for (x, z, w, d) in ((0, 7.97, 16, 0.06),):
        K.box((x, 0.5, z), (w, 1.0, d), grime("dado", "#3a4a3e", 0.3), 0, 0)
    for sx in (-1, 1): K.box((sx * 7.97, 0.5, 1), (0.06, 1.0, 14), grime("dado", "#3a4a3e", 0.3), 0, 0)
    for k in range(5): K.box((-7.85, 2.5, -4 + k * 3), (0.3, 5, 0.3), BRK, 0, 0.02)
    # ---------------- the press ----------------
    K.box((0, 0.45, 3), (3.4, 0.9, 2.2), GREEN, 0, 0.04)
    K.box((0, 0.06, 3), (3.7, 0.12, 2.5), GREEND, 0, 0.02)
    for sx in (-1, 1):
        K.box((sx * 1.3, 1.75, 3), (0.28, 1.8, 1.8), GREEN, 0, 0.05)
        K.box((sx * 1.3, 2.7, 3), (0.34, 0.12, 1.9), IRONM, 0, 0.02)
        for y in (1.3, 1.8, 2.3): K.cyl((sx * 1.48, y, 3), 0.12, 0.08, brass(), 16, "x")
        for (y, z) in ((1.1, 2.3), (1.1, 3.7), (2.45, 2.3), (2.45, 3.7)): K.cyl((sx * 1.46, y, z), 0.04, 0.05, brass(), 8, "x")
        K.box((sx * 1.46, 1.75, 3), (0.02, 0.06, 1.6), gold(), 0, 0)
    for y in (1.3, 1.8, 2.3): K.cyl((0, y, 3), 0.22, 2.5, IRONM, 32, "x")
    for y in (1.55, 2.05): K.cyl((0, y, 3.32), 0.09, 2.4, pm("#202024", 0.15, 0.2), 20, "x")   # inked rollers (glossy)
    K.box((0, 2.55, 3.6), (2.4, 0.2, 0.3), RED, 0, 0.02)
    K.box((0, 2.68, 3.6), (2.3, 0.04, 0.24), pm("#1a1a6a", 0.1), 0, 0)
    # brass maker's plate
    K.box((0, 0.6, 1.89), (1.2, 0.26, 0.02), brass(), 0, 0.005)
    text("SCHNELLPRESSE  1921", (0, 0.6, 1.875), 0.09, pm("#1a1410", 0.5), 0, "serif", 0.002, fit=1.1)
    # feed board with blank sheets, delivery tray with printed sheets
    K.box((0, 1.05, 1.6), (2.2, 0.06, 1.1), PAPER, 0, 0.01, 0.12)
    for k in range(12): K.box((rnd.uniform(-0.05, 0.05), 1.1 + k * 0.006, 1.6), (1.6, 0.004, 0.9), PAPER, rnd.uniform(-0.03, 0.03), 0, 0.12)
    K.box((0, 0.95, 4.5), (2.2, 0.06, 0.9), IRONM, 0, 0.01)
    for k in range(30): K.box((rnd.uniform(-0.6, 0.6), 1.0 + k * 0.006, 4.5 + rnd.uniform(-0.15, 0.15)), (0.9, 0.004, 0.45), [NOTE, NOTE2][k % 2], rnd.uniform(-0.15, 0.15), 0)
    # flywheel with spokes, gears, crank
    K.torus((1.75, 1.3, 3), 0.9, 0.07, RED, 40, 10, "x")
    for k in range(6):
        a = k * math.pi / 3; K.box((1.75, 1.3 + 0.45 * math.sin(a), 3 + 0.45 * math.cos(a)), (0.06, 0.9, 0.06), RED, 0, 0.005, -a + R90)
    K.cyl((1.75, 1.3, 3), 0.14, 0.18, RED, 16, "x")
    gear(K, (-1.62, 1.3, 3), 0.5, IRONM); gear(K, (-1.62, 2.1, 3.5), 0.28, IRONM)
    K.cyl((1.95, 1.3, 3), 0.05, 0.6, IRONM, 12, "x")
    # ---------------- overhead line shaft with pulleys and belts ----------------
    K.cyl((0, 4.3, 3), 0.06, 15.5, IRONM, 12, "x")
    for x in (-6, -2, 2, 6): K.box((x, 4.5, 3), (0.12, 0.4, 0.12), IRONM, 0, 0.01)
    K.cyl((1.75, 4.3, 3), 0.35, 0.18, wood("#6a4a2a", "#3a2412", 6), 20, "x")
    for dz in (-0.33, 0.33):
        top, bot = (4.3, 3 + dz), (1.3, 3 + dz * 0.25)
        K.box((1.82, (top[0] + bot[0]) / 2, (top[1] + bot[1]) / 2), (0.14, 3.0, 0.012), pm("#5a3018", 0.55), 0, 0, math.atan2(top[1] - bot[1], 3.0) * 0.0 + (0.08 if dz > 0 else -0.08))
    for x in (-5.0, 5.5): K.cyl((x, 4.3, 3), 0.25, 0.12, IRONM, 16, "x")
    # ---------------- drying lines with fresh sheets of banknotes ----------------
    for z in (5.4, 6.4, -0.8):
        K.cyl((0, 3.6, z), 0.006, 15, pm("#2a2a2a", 0.7), 4, "x")
        for i in range(16):
            x = -6.8 + i * 0.85 + rnd.uniform(-0.05, 0.05)
            if abs(x - 1.75) < 0.6 and z < 0: continue
            K.box((x, 3.27, z), (0.7, 0.6, 0.004), [NOTE, NOTE2, NOTE3][i % 3], rnd.uniform(-0.05, 0.05), 0)
            for dx in (-0.28, 0.28): K.box((x + dx, 3.6, z), (0.03, 0.07, 0.03), wood("#c8a87a", "#8a6a4a", 20), 0, 0)
    # ---------------- left side: paper rolls, the worker's growing cash piles, crates of notes ----------------
    for k in range(4): K.cyl((-5.5, 0.38 + (0.7 if k > 1 else 0), 3 + (k % 2) * 0.85 + (0.4 if k > 1 else 0)), 0.36, 1.3, paper("#efe6d0", 0.15), 32, "x")
    K.box((-5.5, 0.04, 3.4), (1.6, 0.08, 1.8), wood("#8a6a4a", "#4a3020", 10), 0, 0.01)
    for k in range(4):
        x = -6 + k * 0.7; crate(K, (x, 0.3, 7), 0.6, wood("#b08a52", "#6a4a22", 12, 0.8), k * 0.3)
        text("REICHSBANK", (x - 0.0, 0.32, 6.69), 0.06, pm("#2a1a10", 0.8), k * 0.3, "sans", 0.002, fit=0.5) if k % 2 == 0 else None
        for q in range(3): K_.cash_bundle(K, (x - 0.15 + q * 0.15, 0.55, 7), NOTE, BAND, k * 0.3 + R90)
    for i in range(10):   # loose bundles spilling on the floor
        K_.cash_bundle(K, (-3.2 + rnd.uniform(-0.6, 0.9), 0.0, -0.2 + rnd.uniform(-0.5, 0.6)), [NOTE, NOTE2, NOTE3][i % 3], BAND, rnd.uniform(0, 3))
    wheelbarrow(K, (-4.3, 0, 0.6), NOTE, NOTE3, BAND, rnd)
    for k in range(3): barrel(K, (5 + k * 0.85, 0.45, 6.5), 0.33, 0.9, pm(["#1e2a4a", "#3a1e1e", "#1e1e22"][k], 0.4, 0.3), IRONM)
    for k in range(3): sign_flat = text(["TINTE", "TINTE", "FIRNIS"][k], (5 + k * 0.85, 0.55, 6.16), 0.07, pm("#f0e8d0", 0.6), 0, "sans", 0.002)
    # ---------------- right side: type cases, shelves, the censor's work table ----------------
    for row in range(3):
        K.box((5.5, 1.2 + row * 0.6, 7.75), (3.0, 0.04, 0.35), wood("#5a3018", "#2a140a", 9), 0, 0.005)
        for k in range(8): K.box((4.2 + k * 0.36, 1.35 + row * 0.6, 7.75), (0.25, 0.26, 0.25), pm(["#c8b48a", "#8a6a4a", "#5a6a7a"][(row + k) % 3], 0.6), 0, 0.01)
    K.box((7.5, 0.7, 3.5), (0.9, 1.4, 2.4), wood("#6a3a1e", "#341a0c", 7), 0, 0.02)   # type case cabinet
    for r in range(7):
        for c in range(2):
            K.box((7.04, 0.15 + r * 0.18, 2.9 + c * 1.2), (0.02, 0.14, 1.1), wood("#7a4a24", "#3e2210", 7), 0, 0.005)
            K.cyl((7.02, 0.22 + r * 0.18, 2.9 + c * 1.2), 0.03, 0.03, brass(), 8, "x")
    K.box((7.5, 1.42, 3.5), (1.0, 0.04, 2.5), wood("#5a3018", "#2a140a", 9), 0, 0.01)
    K.box((7.5, 1.47, 3.5), (0.7, 0.05, 1.6), pm("#4a4a4e", 0.3, 0.6), 0, 0.005)   # composing stone with a forme
    for q in range(60): K.box((7.25 + (q % 10) * 0.05, 1.505, 3.0 + (q // 10) * 0.2), (0.04, 0.02, 0.16), pm("#6a6a6e", 0.3, 0.9), 0, 0)
    table(K, TABW, PAPER, rnd)
    # ---------------- walls: signs, posters, clock, calendar, windows ----------------
    sign(K, (2.0, 4.05, 7.97), 4.6, 0.55, 0.0, "REICHSDRUCKEREI", "#1e2a3a", gold(), "serif", gold(), 0.06)
    sign(K, (-0.9, 2.45, 7.97), 1.3, 0.34, 0.0, "RAUCHEN VERBOTEN", "#b01e1e", pm("#f4f0e8", 0.4), "sans", pm("#f4f0e8", 0.4), 0.02)
    K.cyl((-0.9, 3.4, 7.96), 0.33, 0.05, brass(), 32, "z"); K.cyl((-0.9, 3.4, 7.93), 0.3, 0.02, pm("#f4ecd8", 0.4), 32, "z")
    for a in range(12): K.box((-0.9 + 0.25 * math.sin(a * 0.5236), 3.4 + 0.25 * math.cos(a * 0.5236), 7.915), (0.02, 0.06, 0.01), pm("#1a1a1a", 0.5), 0, 0, 0, -a * 0.5236)
    K.box((-0.85, 3.48, 7.91), (0.02, 0.18, 0.01), pm("#1a1a1a", 0.5), 0, 0, 0, -0.5); K.box((-0.98, 3.38, 7.91), (0.02, 0.15, 0.01), pm("#1a1a1a", 0.5), 0, 0, 0, 1.4)
    poster(K, (-5.6, 2.3, 7.96), 0.8, 1.1, 0.0, "#e8c84a", [("100", 0.2), ("BILLIONEN", 0.08), ("MARK", 0.1)], "#3a1e10", None, "serif", "#3a1e10")
    poster(K, (-4.5, 2.4, 7.96), 0.7, 0.95, 0.0, "#c8202a", [("ARBEITER!", 0.09), ("SCHICHT", 0.08), ("6 UHR", 0.1)], "#f4ecd8", None, "sans")
    poster(K, (5.9, 3.2, 7.96), 0.55, 0.75, 0.0, "#f0e6cc", [("NOVEMBER", 0.07), ("1923", 0.18)], "#1a1a1a", None, "serif", "#1a1a1a")
    for sx in (-1, 1):
        x = -3.2
        if sx > 0: continue
        K.box((x, 2.6, 8.0), (1.4, 2.2, 0.03), K_.window_glow("prwin", "#b8d0f0", 3.2), 0, 0)
        K_._frame(K, (x, 2.6, 7.96), 1.4, 2.2, 0.0, pm("#3a3a3a", 0.5, 0.5), 0.1, 0.06)
        for q in range(1, 4): K.box((x, 1.5 + q * 0.55, 7.95), (1.4, 0.03, 0.03), pm("#3a3a3a", 0.5, 0.5), 0, 0)
        for q in range(1, 3): K.box((x - 0.7 + q * 0.467, 2.6, 7.95), (0.03, 2.2, 0.03), pm("#3a3a3a", 0.5, 0.5), 0, 0)
        lib.light("AREA", T(x, 2.6, 7.7), 220, (0.7, 0.82, 1.0), 1.4, (math.radians(90), 0, math.radians(180)), 2.2)
    # big side window on the left wall: cool shaft of daylight across the press
    K.box((-7.99, 2.7, 1.0), (0.03, 2.4, 2.4), K_.window_glow("prwin2", "#c0d8ff", 3.0), 0, 0)
    K_._frame(K, (-7.95, 2.7, 1.0), 2.4, 2.4, -R90, pm("#3a3a3a", 0.5, 0.5), 0.1, 0.06)
    for q in range(1, 4): K.box((-7.95, 1.5 + q * 0.6, 1.0), (0.03, 0.03, 2.4), pm("#3a3a3a", 0.5, 0.5), 0, 0)
    for q in range(1, 4): K.box((-7.95, 2.7, -0.2 + q * 0.6), (0.03, 2.4, 0.03), pm("#3a3a3a", 0.5, 0.5), 0, 0)
    lib.light("AREA", T(-7.6, 2.7, 1.0), 450, (0.7, 0.82, 1.0), 2.4, (0, math.radians(-90), 0), 2.4)
    # ---------------- lamps ----------------
    for x, z in ((0, 2.5), (-4, 4), (4, 4), (3.8, 1.6)):
        y = 3.35 if (x, z) != (3.8, 1.6) else 2.3
        K.cyl((x, (y + 5) / 2, z), 0.008, 5 - y, pm("#1a1a1a", 0.6), 4)
        K.cyl((x, y + 0.1, z), 0.34, 0.24, GREEND, 20, "y", 0.08); K.cyl((x, y - 0.02, z), 0.33, 0.01, pm("#f0ece0", 0.4), 20)
        K.sphere((x, y - 0.03, z), 0.07, em("#ffd090", 30), 10)
        lib.light("POINT", T(x, y - 0.12, z), 160 if y > 3 else 70, (1.0, 0.72, 0.42), 0.1)
    lib.light("AREA", T(0, 3.5, -5.5), 250, (1.0, 0.8, 0.6), 6, (math.radians(75), 0, 0))
    K.build()
    W = bpy.context.scene.world; bg = W.node_tree.nodes.get("Background")
    if bg: bg.inputs[0].default_value = (0.03, 0.025, 0.02, 1); bg.inputs[1].default_value = 0.3
    # ---------------- the growing cash piles: layers of bundles shown one by one (shot 13) ----------------
    PILES.clear()
    for k in range(9):
        px, pz = -2.5 + (k % 3) * 0.45, 0.3 + (k // 3) * 0.3
        for layer in range(14):
            L = K_.Kit(f"pile{k}_{layer}"); y = layer * 0.062
            for j in (-1, 1):
                if layer % 2: L.box((j * 0.04 + rnd.uniform(-0.01, 0.01), y + 0.03, 0), (0.08, 0.06, 0.32), [NOTE, NOTE2, NOTE3][(k + layer) % 3], rnd.uniform(-0.06, 0.06), 0.003)
                else: L.box((rnd.uniform(-0.01, 0.01), y + 0.03, j * 0.04), (0.32, 0.06, 0.08), [NOTE, NOTE2, NOTE3][(k + layer) % 3], rnd.uniform(-0.06, 0.06), 0.003)
            L.box((0, y + 0.03, 0), (0.035, 0.064, 0.035), BAND, 0, 0.003)
            for o in L.build(): o.location = T(px, 0, pz); PILES.append((k, layer, o))
    sm = lambda u: (lambda x: x * x * (3 - 2 * x))(max(0.0, min(1.0, u)))
    def update(f):
        g = 0.4 + 3.6 * sm((f - 1560) / 110) if D["id"] == 13 else 2.0
        for k, layer, o in PILES:
            n = int(round(g / 4.0 * 14 * (0.6 + 0.4 * ((k * 7) % 5) / 4)))
            o.hide_render = layer >= max(1, n)
    return {"update": update}

def gear(K, c, r, m):
    x, y, z = c
    K.cyl(c, r, 0.12, m, 32, "x"); K.cyl(c, r * 0.3, 0.2, brass(), 16, "x")
    n = int(r * 40)
    for i in range(n):
        a = i * 2 * math.pi / n
        K.box((x, y + (r + 0.03) * math.sin(a), z + (r + 0.03) * math.cos(a)), (0.12, 0.06, 0.05), m, 0, 0, -a)

def wheelbarrow(K, c, N1, N2, BAND, rnd):
    x, y, z = c; W = wood("#7a5a3a", "#3a2a1a", 8)
    K.box((x, 0.55, z), (0.7, 0.35, 0.9), pm("#5a6a5a", 0.5, 0.4), 0, 0.02)
    K.torus((x, 0.25, z - 0.65), 0.22, 0.04, pm("#1a1a1a", 0.6), 18, 6, "x")
    for dx in (-0.25, 0.25): K.box((x + dx, 0.5, z + 0.75), (0.05, 0.05, 1.0), W, 0, 0.005, -0.25); K.box((x + dx, 0.22, z + 0.3), (0.05, 0.44, 0.05), W, 0, 0.005)
    for i in range(14): K_.cash_bundle(K, (x + rnd.uniform(-0.22, 0.22), 0.66 + (i // 7) * 0.07, z + rnd.uniform(-0.3, 0.3)), [N1, N2][i % 2], BAND, rnd.uniform(0, 3))

def table(K, TABW, PAPER, rnd):
    """the censor's work table at (3.8, 2): top y 0.91; the newspaper card lands on x 3.55..4.05, z 1.67..2.33"""
    K.box((3.8, 0.88, 2), (2.2, 0.06, 1.0), TABW, 0, 0.01)
    for dx in (-1, 1):
        for dz in (-0.4, 0.4): K.box((3.8 + dx, 0.43, 2 + dz), (0.07, 0.86, 0.07), wood("#5a3018", "#2a140a", 9), 0, 0)
    K.box((3.8, 0.8, 2), (2.0, 0.1, 0.9), TABW, 0, 0.005)
    K.box((3.8, 0.912, 2.0), (0.9, 0.003, 0.75), pm("#2a4a32", 0.8), 0, 0)   # green blotter under the paper
    for dx in (-0.45, 0.45): K.box((3.8 + dx, 0.914, 2.0), (0.08, 0.006, 0.77), pm("#5a2a14", 0.45), 0, 0.002)
    INK = pm("#1a1a1a", 0.7); RED = pm("#b01e1e", 0.5)
    # stack of other papers (left), with readable mastheads
    for i, (name, head) in enumerate((("VOLKSZEITUNG", "STREIK IN BERLIN"), ("BERLINER TAGESPOST", "REICHSTAG BRENNT"), ("DER ABEND", "NOTVERORDNUNG"))):
        x, z, yaw = 3.05 + i * 0.03, 1.95 + i * 0.05, 0.12 - i * 0.1; y = 0.915 + i * 0.008
        K.box((x, y, z), (0.42, 0.006, 0.56), paper("#ece2c8", 0.35), yaw, 0)
        flat_text(name, (x, y + 0.004, z + 0.2), 0.05, INK, yaw, "serif", fit=0.38)
        flat_text(head, (x, y + 0.004, z + 0.13), 0.032, INK, yaw, "sans", fit=0.36)
        for c in range(3):
            for r in range(6): K.box((x - 0.13 + c * 0.13, y + 0.0035, z + 0.06 - r * 0.05), (0.11, 0.001, 0.012), pm("#5a5650", 0.8), yaw, 0)
    # rubber stamp + ink pad, red pencil, scissors, glasses, coffee, ashtray with a smouldering cigarette, a desk lamp
    K.box((4.45, 0.93, 1.75), (0.16, 0.03, 0.1), pm("#2a2a2e", 0.5, 0.5), 0.2, 0.005); K.box((4.45, 0.947, 1.75), (0.13, 0.004, 0.075), pm("#7a1018", 0.5), 0.2, 0)
    K.box((4.5, 0.93, 2.05), (0.1, 0.03, 0.06), RED, -0.3, 0.005); K.cyl((4.5, 1.0, 2.05), 0.025, 0.12, wood("#6a3a1e", "#341a0c", 9), 10); K.sphere((4.5, 1.08, 2.05), 0.035, wood("#6a3a1e", "#341a0c", 9), 10)
    flat_text("ZENSIERT", (4.47, 0.9132, 2.25), 0.04, RED, 0.25, "sans")
    K.cyl((4.25, 0.92, 1.6), 0.006, 0.18, RED, 6, "x", None, 0.7)
    for s in (-1, 1): K.box((4.32, 0.917, 2.4 + s * 0.02), (0.13, 0.004, 0.012), pm("#b0b0b8", 0.2, 1.0), 0.3 * s, 0); K.torus((4.24, 0.918, 2.4 + s * 0.04), 0.022, 0.005, pm("#1a1a1a", 0.5), 10, 4, "y")
    K.cyl((3.2, 0.96, 2.35), 0.045, 0.09, pm("#f4f0e6", 0.2), 14); K.cyl((3.2, 0.915, 2.35), 0.08, 0.008, pm("#f4f0e6", 0.2), 14); K.cyl((3.2, 0.995, 2.35), 0.04, 0.005, pm("#3a1e0e", 0.1), 12)
    K.cyl((4.65, 0.925, 2.3), 0.08, 0.025, pm("#8a8a90", 0.3, 0.8), 16)
    K.cyl((4.62, 0.945, 2.3), 0.006, 0.08, pm("#f4f0e8", 0.6), 6, "x", None, 0.5); K.sphere((4.585, 0.945, 2.32), 0.007, em("#ff6020", 20), 6)
    for s in (-1, 1): K.torus((3.3 + s * 0.04, 0.917, 1.6), 0.03, 0.004, pm("#2a2a2a", 0.4, 0.5), 12, 4, "y")
    K.cyl((2.95, 0.925, 1.65), 0.09, 0.03, brass(), 16); K.cyl((2.95, 1.15, 1.65), 0.012, 0.45, brass(), 8)
    K.cyl((2.95, 1.37, 1.75), 0.12, 0.12, pm("#1e6a3a", 0.15), 16, "y", 0.06); K.sphere((2.95, 1.31, 1.75), 0.035, em("#ffd090", 25), 8)
    lib.light("POINT", T(2.95, 1.28, 1.8), 18, (1.0, 0.75, 0.45), 0.04)
    for i in range(5): K.box((4.6 + rnd.uniform(-0.1, 0.1), 0.92 + i * 0.006, 1.65), (0.2, 0.004, 0.28), paper("#efe4c8", 0.3), rnd.uniform(-0.3, 0.3), 0)
