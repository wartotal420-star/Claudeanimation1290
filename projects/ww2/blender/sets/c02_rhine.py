# Cologne, 7 March 1936: the Hohenzollern bridge over the Rhine (chapter 2 shots 25-27). Three coords: the bridge deck runs
# along z from the west-bank bridgehead (z 0) to the east bank (z 380), deck y 0, roadway |x| < 6 (keep |x| < 4.5 clear
# for the marching column), footways |x| 6..8 behind railings. Three steel tied-arch spans on each side (x +-8.4), each
# 120 m, hangers and lattice; the stone bridgehead towers stand at z -2 (x +-10). Behind the bridgehead (z < 0) the old
# town: a cobbled square z -40..0 with crowds, flags on houses, and the cathedral's twin spires at (-30, 0, -70). The
# generals' spot: by the left tower at (-4.5, 0, -3.5). The river below (y -9) with barges. Light: low golden morning sun
# from the east (+z, slightly +x), cool sky fill; the camera end gets a warm bounce.
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached, set_world
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK

def build(M, D):
    random.seed(1936); KS.reset(); rnd = random.Random(36)
    K = Kit("rhine")
    set_world((0.35, 0.5, 0.8), (0.95, 0.78, 0.6), 1.0, (0.3, 0.48, 0.82), (1.0, 0.8, 0.6))
    STEEL = CK.wm("rsteel", "#4a5a5a", "#2a3030", 0.5, 0.6, 14, 0.75, "#3a3a34"); COB = lib.cobbles("rhcob", "#7a7470", "#5a5650")
    STONE = grime("rhstone", "#8a7e70", 0.4, 2.5); STONE2 = grime("rhstone2", "#a89a86", 0.35, 2.5); DARK = grime("rhdark", "#3a3634", 0.5, 2.0)
    WATER = lib.principled("rhwater", hexc("#3a5a6a"), 0.08, 0.0)
    # river + deck
    K.box((0, -9, 150), (900, 0.1, 900), WATER, 0, 0)
    K.box((0, -0.3, 190), (17, 0.6, 400), DARK, 0, 0.02)
    K.box((0, 0.01, 190), (12, 0.02, 400), COB, 0, 0)
    for sd in (-1, 1):
        K.box((sd * 7, 0.12, 190), (2.0, 0.24, 400), STONE2, 0, 0.02)
        for k in range(200): K.cyl((sd * 8.0, 0.65, -5 + k * 2.0), 0.03, 0.9, STEEL, 6)
        K.box((sd * 8.0, 1.12, 190), (0.1, 0.08, 400), STEEL, 0, 0.01)
        for k in range(27): K.cyl((sd * 8.05, 3.0, 2 + k * 14), 0.06, 6.0, IR_ if False else STEEL, 6) if False else None
    for k in range(3):   # piers
        K.box((0, -5, 120 * (k + 1) - 2), (18, 9, 6), STONE, 0, 0.05)
    # arches: tied arch, top chord + hangers + diagonals, per span per side
    for sp in range(3):
        z0 = sp * 120.0 + 2; L = 116.0
        for sd in (-1, 1):
            x = sd * 8.6; prev = None
            for k in range(41):
                t = k / 40; z = z0 + L * t; y = 1.0 + 19.0 * math.sin(math.pi * t)
                if prev:
                    pz, py = prev; mz, my = (z + pz) / 2, (y + py) / 2; ln = math.hypot(z - pz, y - py)
                    K.box((x, my, mz), (0.7, 0.9, ln + 0.1), STEEL, 0, 0.02, -math.atan2(y - py, z - pz))
                prev = (z, y)
                if k % 2 == 0 and 0 < k < 40:
                    K.box((x, (1.0 + y) / 2, z), (0.25, y - 1.0, 0.25), STEEL, 0, 0.0)
                    if k < 39:
                        z2 = z0 + L * (k + 2) / 40; y2 = 1.0 + 19.0 * math.sin(math.pi * (k + 2) / 40)
                        dz, dy = z2 - z, (y2 + 1.0) / 2 - (y + 1.0) / 2
                        K.box((x, (1.0 + y) / 2 + dy / 2, (z + z2) / 2), (0.14, 0.14, math.hypot(dz, (y - 1.0) / 2) + 0.2), STEEL, 0, 0.0, math.atan2((y - 1.0) / 2, dz) * (1 if k % 4 else -1))
            K.box((x, 1.0, z0 + L / 2), (0.8, 1.2, L), STEEL, 0, 0.02)
        for k in range(0, 41, 4):   # wind bracing between the arches
            t = k / 40; z = z0 + L * t; y = 1.0 + 19.0 * math.sin(math.pi * t)
            if y > 8: K.box((0, y, z), (17.2, 0.3, 0.3), STEEL, 0, 0.0)
    # bridgehead towers
    for sd in (-1, 1):
        x = sd * 10.5
        K.box((x, 7, -2), (5, 14, 5), STONE, 0, 0.05)
        for j in range(3): K.box((x, 3 + j * 4, -4.55), (1.2, 2.0, 0.1), pm("#1e1e22", 0.4), 0, 0.01)
        K.cyl((x, 16.5, -2), 3.3, 5.0, pm("#3a4a4a", 0.5, 0.3), 4, "y", 0.2, math.pi / 4)
        for k in range(6): K.box((x - 2.2 + k * 0.88, 14.4, -4.6), (0.5, 0.8, 0.4), STONE, 0, 0.02)
        K.box((x - sd * 1.6, 15.4, -2), (0.15, 2.0, 0.15), pm("#2a2a2a", 0.5), 0, 0)
    # the town square behind the bridgehead: houses with steep roofs, flags, lamp posts, a tram, the cathedral
    K.box((0, -0.05, -40), (120, 0.1, 80), COB, 0, 0)
    WALLS = [grime(f"rhw{k}", c, 0.3) for k, c in enumerate(("#d8c8a8", "#c8a888", "#e0d4bc", "#b89a7a", "#d0b898"))]
    ROOF = KS.brick("rhroof", "#5a3a34", "#4a2e28", "#2a1a18", 8, 0.3, 0.12, 0.7)
    for sd in (-1, 1):
        for k in range(7):
            z = -10 - k * 7; x = sd * 16; w = 6.8; h = rnd.uniform(11, 15)
            K.box((x, h / 2, z), (8, h, w), WALLS[(k + (sd > 0)) % 5], 0, 0.03)
            for s2 in (-1, 1):
                q = [(x - sd * 4 * 1.0 * s2 * 0 + (-4.2), h, z + s2 * (w / 2 + 0.2)), (x + 4.2, h, z + s2 * (w / 2 + 0.2)), (x + 4.2, h + 4.5, z), (x - 4.2, h + 4.5, z)]
                K.quad(q, ROOF); K.quad(q[::-1], ROOF)
            for r in range(3):
                for c in range(3):
                    K.box((x - sd * 4.02, 3 + r * 3.4, z - 2.2 + c * 2.2), (0.05, 1.6, 0.9), pm("#1e2430", 0.1, 0.3), 0, 0)
                    KS._frame(K, (x - sd * 4.04, 3 + r * 3.4, z - 2.2 + c * 2.2), 1.0, 1.7, sd * R90, pm("#f2ead8", 0.5), 0.1, 0.06)
            if k % 2 == 0: IK.drape(f"rhf{sd}{k}", (x - sd * 4.15, h - 1.0, z), 1.2, 5.5, pm("#b8202a", 0.7), sd * R90, 3, 0.04)
            poster(K, (x - sd * 4.05, 1.4, z + 2.4), 0.6, 0.85, sd * R90, ["#e8c84a", "#f0e6cc", "#3a8a4a"][k % 3], [("4711", 0.18), ("KÖLNISCH", 0.08), ("WASSER", 0.08)] if k % 3 == 0 else [("STOLLWERCK", 0.1), ("SCHOKOLADE", 0.08)] if k % 3 == 1 else [("KÖLN", 0.16), ("RHEIN", 0.1)], "#1a1a1a")
    for k, (x, z) in enumerate(((-7, -6), (7, -6), (-7, -18), (7, -18), (-7, -30), (7, -30))):
        K.cyl((x, 2.4, z), 0.08, 4.8, iron("#1e2420"), 8); K.cyl((x, 4.9, z), 0.22, 0.4, pm("#f2ead0", 0.2), 8, "y", 0.12)
    # the cathedral: twin open-work spires, buttresses, the nave
    CATH = grime("rhcath", "#5a5650", 0.55, 2.0)
    cx, cz = -4.0, -100.0
    for sd in (-1, 1):
        x = cx + sd * 9
        K.box((x, 25, cz), (12, 50, 12), CATH, 0, 0.05)
        for j in range(5): K.box((x, 52 + j * 6, cz), (10 - j * 1.8, 6, 10 - j * 1.8), CATH, 0, 0.05)
        K.cyl((x, 95, cz), 3.5, 30, CATH, 8, "y", 0.2)
        for k in range(10):
            for s2 in (-1, 1): K.box((x + s2 * 6.2, 6 + k * 4.5, cz - 6.2), (0.8, 3.0, 0.8), CATH, 0, 0.02)
        for r in range(4): K.box((x, 12 + r * 10, cz - 6.05), (2.2, 6.5, 0.1), pm("#1e1e24", 0.4), 0, 0.01)
    K.box((cx, 20, cz - 20 * 0), (10, 40, 12), CATH, 0, 0.05); K.box((cx, 14, cz - 6.1), (4.5, 12, 0.2), pm("#1e1e24", 0.4), 0, 0)
    K.box((cx, 22, cz + 40), (20, 44, 70), CATH, 0, 0.05)
    # barges on the river, the far bank (Deutz) with factory chimneys
    for k, (x, z) in enumerate(((-40, 60), (35, 150), (-60, 230))):
        CK.boat(K, x, z, 0.1 * k, "barge", 1.3, -9.0)
    for k in range(12):
        x = rnd.uniform(-160, 160); K.box((x, 6, 420 + rnd.uniform(0, 30)), (rnd.uniform(15, 40), rnd.uniform(10, 25), 12), grime("rhfar", "#8a7a70", 0.4), 0, 0.1)
    for k in range(4): K.cyl((rnd.uniform(-120, 120), 20, 440), 1.6, 40, KS.brick("rhchim", "#8a4a3a", "#6a3a2a"), 12)
    # square dressing: tram rails, a flower stall, kiosk, bicycles, benches
    for x in (-1.5, 1.5): K.box((x, 0.012, -40), (0.08, 0.02, 80), pm("#9a9aa0", 0.2, 1.0), 0, 0)
    for k, (x, z) in enumerate(((-9.5, -14), (9.5, -22), (-9.5, -34))):
        K.box((x, 0.5, z), (1.6, 1.0, 1.0), wood("#5a3a22", "#2e1e10", 8), 0, 0.02)
        for j in range(8): K.sphere((x - 0.6 + (j % 4) * 0.4, 1.08, z - 0.25 + (j // 4) * 0.5), 0.17, pm(["#d8304a", "#f2d040", "#f2ece0", "#a83a8a"][j % 4], 0.7), 8)
        K.cyl((x, 2.0, z), 0.03, 2.0, wood("#5a3a22", "#2e1e10", 8), 6); K.cyl((x, 2.4, z), 1.1, 0.25, cloth("#2a5a3a" if k % 2 else "#a82a2a"), 10, "y", 0.05)
    K.cyl((8.5, 1.5, -10), 0.9, 3.0, pm("#2a4a3a", 0.5), 12); K.cyl((8.5, 3.2, -10), 1.1, 0.4, pm("#2a4a3a", 0.5), 12, "y", 0.2)
    for j in range(3): poster(K, (8.5 + 0.92 * math.sin(j * 1.2 + 3.5), 1.6, -10 + 0.92 * math.cos(j * 1.2 + 3.5)), 0.6, 0.9, j * 1.2 + 3.5 + math.pi, ["#e8c84a", "#f0e6cc", "#c8202a"][j], [("KINO", 0.16), ("UFA", 0.1)], "#1a1a1a")
    for k in range(3): K.box((-9.6, 0.45, -6 - k * 2), (0.5, 0.06, 1.6), wood("#5a3a22", "#2e1e10", 8), 0, 0.01)
    IK.sun((-0.4, -0.3, -0.85), 5.0, (1.0, 0.74, 0.46), 1.5)
    lib.light("AREA", T(0, 8, -14), 900, (0.9, 0.85, 1.0), 14).rotation_euler = (math.radians(-70), 0, math.pi)
    lib.light("AREA", T(0, 6, 10), 900, (1.0, 0.85, 0.65), 10).rotation_euler = (math.radians(-70), 0, 0)
    K.build()
    return {}
