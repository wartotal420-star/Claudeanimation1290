# Iwo Jima, February 1945 (chapter 13): the black volcanic-sand beach terraces under Mount Suribachi, wrecked amtracs and
# landing craft, shell craters, smoke, marines dug into the sand.
# three.js layout: the beach slopes up from the surf (z 30, y -0.25) to the first terrace (z 0, y 1.2) and the second
#   terrace (z -25, y 3.5); Suribachi (170 m) rises at (-420, 0, 260) to the left of a camera looking +z (out to sea, the
#   fleet on the horizon) or to the right of one looking -z (inland). Marines lie / crouch in the shell holes at
#   (-3, y, 6), (2, y, 9), (6, y, 4) on the slope (y = sand(x, z), see SAND below); keep x -8..8, z 2..14 clear.
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, crate, barrel
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK
from sets import front as FR

CRATERS = [(-3, 6, 1.6), (2, 9, 1.4), (6, 4, 1.8), (-9, 13, 2.0), (12, 10, 2.2), (-14, 2, 1.8), (9, -6, 2.4), (-6, -10, 2.0), (18, -2, 2.0), (-20, 16, 2.4)]
def sand(x, z):
    h = 1.2 * CK.smooth(32, 0, z) + 2.3 * CK.smooth(-12, -28, z) - 0.25 - 0.9 * CK.smooth(30, 46, z)
    h += 0.15 * noise.noise(Vector((x * 0.2, z * 0.2, 1.0)))
    for cx, cz, r in CRATERS:
        d = math.hypot(x - cx, z - cz)
        if d < r * 1.6: h += -0.55 * r * max(0.0, 1 - (d / r) ** 2) + 0.25 * r * math.exp(-((d - r) / (0.3 * r)) ** 2)
    return h

def build(M, D):
    rnd = random.Random(219)
    S = bpy.context.scene
    CK.sky(S.world, (0.5, 0.45, 0.75), [(0.0, (0.7, 0.68, 0.64)), (0.08, (0.48, 0.52, 0.6)), (0.4, (0.24, 0.32, 0.48)), (1.0, (0.1, 0.14, 0.26))],
           sun_col=(20, 18, 14), cloud_dark=(0.3, 0.3, 0.32), cloud_lit=(1.0, 0.95, 0.88), cover=0.8, strength=0.75, glow_col=(1.0, 0.9, 0.75), glow=0.3)
    CK.sun_light((0.5, 0.45, 0.75), 4.0, (1.0, 0.9, 0.78), 2.0)
    black = mat_once("isand", lambda: CK.green_hill_mat("isand", "#2a2826", "#1a1816", "#4a4440"))
    CK.heightfield("iwo", -160, 160, -140, 48, 0.8, sand, black)
    CK.heightfield("suri", -900, 0, -100, 700, 12, lambda x, z: -2 + 175 * max(0.0, 1 - math.hypot(x + 420, z - 260) / 300) ** 1.4 + 4 * noise.noise(Vector((x * 0.04, z * 0.04, 3))), black)
    CK.sea("isea", -3000, 3000, 30, 5000, -0.25, CK.water_mat("iwater", "#1a3a4a", "#3a5a62", 1.0, 0.07, 0.6))
    CK.whitecaps("isurf", -160, 160, 30, 36, 220, rnd, -0.21, (3, 9))
    K = Kit("iw")
    steel = mat_once("iamtr", lambda: worn("iamtr", "#4e5642", "#2e2a24", 0.6, 0.3, 1.5, 0.55, "#3a3a2e"))
    burnt = mat_once("iburnt", lambda: worn("iburnt", "#2a2622", "#5a3a20", 0.8, 0.3, 2.0, 0.5, "#1a1612"))
    # wrecked amtracs (LVT): box hull, track sponsons, tilted in the sand; a broken LCVP in the surf
    for k, (x, z, yw, tilt, m) in enumerate(((-12, 20, 0.4, 0.15, steel), (14, 24, -0.6, -0.1, burnt), (-26, 26, 1.2, 0.2, burnt), (22, 6, 0.3, 0.08, steel))):
        y = sand(x, z)
        K.box((x, y + 1.0, z), (3.2, 1.8, 7.8), m, yw, 0.1, tilt, 0.05)
        for sd in (-1, 1): K.box((x + sd * 1.75 * math.cos(yw), y + 0.6, z - sd * 1.75 * math.sin(yw)), (0.6, 1.1, 7.4), pm("#1a1a18", 0.8), yw, 0.05, tilt, 0.0)
        K.box((x, y + 2.1, z), (2.6, 0.5, 2.0), m, yw, 0.05, tilt, 0.0)
    K.box((4, -0.1, 34), (3.2, 1.2, 9.5), pm("#4e5a4a", 0.6), 0.9, 0.1, 0.0, 0.3)
    # debris: crates, drums, a jeep stuck to its axles, broken palm stumps (Suribachi side), barbed wire, a pillbox
    for k in range(10):
        x, z = rnd.uniform(-30, 30), rnd.uniform(-5, 26)
        if -8 < x < 8 and 2 < z < 14: continue
        crate(K, (x, sand(x, z) + 0.3, z), 0.7, wood("#7a5a34", "#4a3420", 5.0, 0.8), rnd.uniform(0, 3))
    for k in range(8):
        x, z = rnd.uniform(-30, 30), rnd.uniform(-5, 26)
        if -8 < x < 8 and 2 < z < 14: continue
        barrel(K, (x, sand(x, z) + 0.3, z), 0.3, 0.9, pm("#4a4a36", 0.5, 0.4), pm("#2a2a26", 0.5, 0.5), "x" if k % 2 else "y", rnd.uniform(0, 3))
    K.box((-4, sand(-4, -18) + 0.6, -18), (1.6, 0.9, 3.0), pm("#5a5a3a", 0.6), 0.3, 0.06, 0.25)
    for sd in (-1, 1):
        for e in (-1.0, 1.0): K.cyl((-4 + sd * 0.8, sand(-4, -18) + 0.2, -18 + e), 0.35, 0.25, pm("#141414", 0.8), 12, "x", None, 0.3)
    conc = mat_once("ipill", lambda: worn("ipill", "#6a6660", "#3a3632", 0.9, 0.0, 1.5, 0.55, "#4a4640"))
    K.box((-24, sand(-24, -22) + 1.0, -22), (6, 2.4, 5), conc, 0.2, 0.3); K.box((-24, sand(-24, -22) + 1.2, -24.6), (3.0, 0.4, 0.3), pm("#0a0a0a", 0.8), 0.2, 0.0)
    wire = pmat("iwire", "#3a3430", 0.6, 0.5)
    for k in range(3):
        for j in range(16): K.torus((-30 + k * 22 + j * 0.45, sand(-30 + k * 22 + j * 0.45, -12) + 0.35, -12), 0.35, 0.012, wire, 14, 3, "x")
    K.build()
    for k in range(6):
        x, z = rnd.uniform(-60, -20), rnd.uniform(-60, -20)
        tube(f"istump{k}", [(x, sand(x, z), z), (x + 0.2, sand(x, z) + rnd.uniform(1.5, 3.5), z)], 0.2, burnt, res=2, bres=1)
    # smoke over the beach and from Suribachi, the invasion fleet on the horizon
    for k, (x, z) in enumerate(((-14, 2), (20, -10), (-40, -30), (-300, 220), (40, 20))):
        CK.smoke(f"ism{k}", (x, sand(x, z) if abs(x) < 160 else 30, z), 60, 3, 18, "#3a3634" if k % 2 else "#24201e", 0.75, (40, 20), k, 9)
    ship = CK.us_battleship("ibb", 600, 1800, 2.6, 180, 30, 0.0)
    for k, (x, z) in enumerate(((-900, 2300), (1500, 2600), (-2200, 3000))): CK.clone(ship, x - 600, z - 1800, f"ic{k}")
    lcs = Kit("ilc")
    for k in range(30):
        x, z = rnd.uniform(-900, 900), rnd.uniform(200, 900)
        lcs.box((x, 0.3, z), (3.2, 1.2, 9.0), pm("#4e5a4a", 0.6), 0.0, 0.1); lcs.box((x, 0.4, z - 6), (2.0, 0.1, 6), mat_once("ffoam", FR.foam_mat), 0.0, 0.0)
    lcs.build()
    CK.area((0, 8, -14), (0, 1.5, 8), 2400, (1.0, 0.86, 0.7), 14)
    return {}
