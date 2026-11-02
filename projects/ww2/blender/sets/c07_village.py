# A Chinese village in Zhejiang, April 1942 (chapter 7 shots 26-27): a B-25 crash-landed in the rice paddy, villagers lead
# the crew to hide in a barn (f < 3418); then the empty village at dusk with smoke rising (Japan's revenge; f >= 3418:
# serious, no people).
# three.js layout: the village street runs along x at z 0..3 (stone path, characters stand here, y 0.1); houses north of it
# at z 4..10 (the barn with open doors at (-5, 0, 5.5)); paddies south (z -30..-2, water y 0.02) with the B-25 nose-down
# at (14, 0, -16); bamboo hills behind (z 30+). Dusk sun low in the -x / -z sky (warm, behind the camera's left).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, crate, barrel
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK
from sets import ikit

SUN = (-0.8, 0.16, -0.45)
F_REVENGE = 3418
def gfn(x, z):
    if z > -1.5: return 0.1 + 0.6 * CK.smooth(14, 40, z) * (1 + 0.6 * math.sin(x * 0.07)) * CK.smooth(14, 40, z) * 8
    return -0.25 + 0.05 * math.sin(x * 0.3)

def roof(K, cx, cz, w, d, h, y0, tile, ridge, yaw=0.0):
    """grey tile roof: two curved slopes of tile rows with upturned eave ends, a ridge with end flicks"""
    ca, sa = math.cos(yaw), math.sin(yaw)
    P = lambda u, y, v: (cx + u * ca + v * sa, y, cz - u * sa + v * ca)
    for sd in (-1, 1):
        for r in range(7):
            f = r / 6; v = sd * (d / 2 + 0.35) * (1 - f); y = y0 + h * f - 0.12 * math.sin(f * math.pi)
            K.box(P(0, y, v), (w + 0.6 + 0.3 * (1 - f), 0.07, (d / 2 + 0.35) / 6 + 0.1), tile, yaw, 0.0, sd * -math.atan2(h, d / 2), 0.0)
    K.box(P(0, y0 + h + 0.06, 0), (w + 0.7, 0.16, 0.25), ridge, yaw, 0.02)
    for su in (-1, 1): K.box(P(su * (w / 2 + 0.4), y0 + h + 0.2, 0), (0.25, 0.3, 0.22), ridge, yaw, 0.02, 0.0, su * 0.5)

def build(M, D):
    rnd = random.Random(1804)
    S = bpy.context.scene
    CK.sky(S.world, SUN, [(0.0, (1.0, 0.5, 0.22)), (0.05, (0.9, 0.42, 0.28)), (0.15, (0.45, 0.32, 0.42)), (0.45, (0.14, 0.16, 0.32)), (1.0, (0.04, 0.06, 0.16))],
           sun_col=(26, 12, 4), cloud_dark=(0.18, 0.12, 0.18), cloud_lit=(1.3, 0.6, 0.3), cover=0.5, strength=0.9, glow_col=(1.0, 0.45, 0.15), glow=1.0)
    CK.sun_light(SUN, 3.2, (1.0, 0.6, 0.32), 2.0)
    dirt = mat_once("vdirt", lambda: CK.green_hill_mat("vdirt", "#6a5a34", "#4a3e24", "#7a6a4a"))
    CK.heightfield("vground", -80, 80, -1.6, 90, 1.0, gfn, dirt)
    hills = mat_once("vhill", lambda: CK.green_hill_mat("vhill", "#3a5a2a", "#22381a", "#4a4a34"))
    CK.heightfield("vhills", -600, 600, 60, 900, 12, CK.ridge_fn(60, 500, 0, 220, 7, 0.006), hills)
    # paddies: mirror water in dyke-bounded fields with rows of young rice
    water = CK.water_mat("vpad", "#2a3a3a", "#4a5a50", 4.0, 0.02, 0.05)
    mesh_obj("paddy", [(-80, 0.02, -60), (80, 0.02, -60), (80, 0.02, -1.6), (-80, 0.02, -1.6)], [(0, 1, 2, 3)], water)
    K = Kit("vil")
    dyke = pm("#5a4a2e", 0.9); rice = pm("#7aa83a", 0.7)
    for k in range(5): K.box((0, 0.1, -2 - k * 11), (160, 0.3, 0.8), dyke, 0.0, 0.05)
    for k in range(9): K.box((-60 + k * 15, 0.1, -25), (0.8, 0.3, 50), dyke, 0.0, 0.05)
    for r in range(70):
        for c in range(26):
            x, z = -36 + c * 1.6 + rnd.uniform(-0.2, 0.2), -3.2 - r * 0.62
            if abs(x - 14) < 6 and abs(z + 16) < 5: continue
            if (z + 2) % 11 > 10.2: continue
            K.box((x, 0.15, z), (0.06, 0.32, 0.06), rice, rnd.uniform(0, 3), 0.0, rnd.uniform(-0.3, 0.3))
    # houses: whitewashed walls over a stone plinth, dark timber, tiled roofs, doors, windows with lattice
    white = mat_once("vwhite", lambda: worn("vwhite", "#e8e0cc", "#8a8270", 0.9, 0.0, 1.5, 0.62, "#a89a80"))
    stone = mat_once("vstone", lambda: lib.brickmat("vstone", "#8a8270", "#6a645a", "#4a4640", 3.0, 0.6, 0.3, 0.9))
    timber = wood("#4a3020", "#2a1a10", 5.0, 0.7); tile = pm("#3a3c40", 0.6); ridge = pm("#2a2a2e", 0.6)
    houses = [(-12, 7, 7, 5), (-5, 6.5, 5, 4.5), (3, 7.5, 6, 5), (11, 7, 6, 5), (19, 8, 5, 4.5), (-20, 8, 6, 5), (6, 15, 7, 5), (-9, 15, 6, 5)]
    for k, (x, z, w, d) in enumerate(houses):
        K.box((x, 0.35, z), (w + 0.1, 0.5, d + 0.1), stone, 0.0, 0.02); K.box((x, 1.85, z), (w, 2.5, d), white, 0.0, 0.02)
        for sx in (-1, 1): K.box((x + sx * (w / 2 - 0.1), 1.85, z - d / 2 - 0.05), (0.2, 2.6, 0.12), timber, 0.0, 0.01)
        K.box((x, 3.05, z - d / 2 - 0.05), (w, 0.15, 0.12), timber, 0.0, 0.01)
        roof(K, x, z, w, d, 1.4, 3.1, tile, ridge)
        if k == 1:
            K.box((x, 1.3, z - d / 2 - 0.02), (2.0, 2.0, 0.04), pm("#0e0a08", 0.9), 0.0, 0.0)            # the barn: open doors
            for sd in (-1, 1): K.box((x + sd * 1.45, 1.3, z - d / 2 - 0.35), (0.9, 2.0, 0.06), timber, sd * 0.9, 0.01)
            for j in range(4): K.cyl((x - 1.0 + j * 0.6, 0.45, z), 0.35, 0.7, pm("#b89a52", 0.95), 12, "z")
        else:
            K.box((x - w * 0.2, 1.2, z - d / 2 - 0.03), (1.0, 1.8, 0.05), timber, 0.0, 0.01)
            K.box((x + w * 0.22, 1.9, z - d / 2 - 0.03), (1.1, 0.8, 0.05), pm("#1a1410", 0.8), 0.0, 0.0)
            for j in range(4): K.box((x + w * 0.22 - 0.4 + j * 0.27, 1.9, z - d / 2 - 0.06), (0.04, 0.8, 0.03), timber, 0.0, 0.0)
            for j in range(3): K.box((x + w * 0.22, 1.65 + j * 0.25, z - d / 2 - 0.06), (1.1, 0.04, 0.03), timber, 0.0, 0.0)
    # street: flagstones, a well, firewood stacks, baskets, a cart, haystacks, drying racks, a water buffalo yoke
    flag_ = mat_once("vflag", lambda: lib.brickmat("vflag", "#8a8478", "#76706a", "#4a4640", 1.5, 0.7, 0.45, 0.85))
    K.box((0, 0.08, 1.5), (60, 0.1, 3.4), flag_, 0.0, 0.0)
    K.cyl((-1.0, 0.45, 3.4), 0.6, 0.7, stone, 20); K.cyl((-1.0, 0.82, 3.4), 0.5, 0.05, pm("#0a0a0a", 0.2), 20)
    for sx in (-0.65, 0.65): K.box((-1.0 + sx, 1.3, 3.4), (0.1, 1.6, 0.1), timber, 0.0, 0.0)
    K.box((-1.0, 2.1, 3.4), (1.5, 0.1, 0.1), timber, 0.0, 0.0); K.cyl((-1.0, 1.9, 3.4), 0.15, 0.3, pm("#5a4a30", 0.7), 12)
    logs = wood("#8a6a44", "#5a4028", 4.0, 0.8)
    for k in range(18): K.cyl((7.5 + (k % 6) * 0.17, 0.25 + (k // 6) * 0.16, 4.4), 0.08, 1.0, logs, 8, "z")
    for k in range(14): K.cyl((-15 + (k % 7) * 0.17, 0.25 + (k // 7) * 0.16, 4.2), 0.08, 1.0, logs, 8, "z")
    bask = pm("#a8864a", 0.8)
    for k, (x, z) in enumerate(((2.0, 3.6), (2.6, 3.8), (-7.8, 3.6), (14.5, 3.9), (15.0, 3.5))):
        K.cyl((x, 0.32, z), 0.3, 0.45, bask, 16, "y", 0.24); K.torus((x, 0.56, z), 0.3, 0.02, bask, 16, 4)
    for k, (x, z) in enumerate(((-26, 3), (24, 4), (26, -0.5))):
        K.cyl((x, 1.0, z), 1.4, 1.8, pm("#b89a52", 0.95), 16, "y", 1.0); K.cyl((x, 2.2, z), 1.0, 0.8, pm("#a88a48", 0.95), 16, "y", 0.1)
    K.box((-3.0, 0.55, 2.8), (1.8, 0.1, 1.0), timber, 0.3, 0.01)
    for sd in (-1, 1): K.cyl((-3.0 + sd * 0.8, 0.45, 2.8 - sd * 0.25), 0.45, 0.06, timber, 16, "x", None, 0.3)
    for k in range(4): K.box((18 + k * 0.6, 1.4, 3.0), (0.04, 2.0, 0.04), timber, 0.0, 0.0)
    K.box((18.9, 2.3, 3.0), (2.0, 0.04, 0.04), timber, 0.0, 0.0)
    for k in range(5): K.box((18.2 + k * 0.38, 2.0, 3.0), (0.3, 0.55, 0.01), pm(["#c8a050", "#8a3a2a", "#3a5a8a", "#d8d0b8", "#6a8a3a"][k], 0.8), 0.0, 0.0)
    lantern = em("#ff8a3a", 4.0)
    for k, x in enumerate((-12, 3, 11)): K.sphere((x - 0.8, 2.6, 7 - 2.7), 0.18, lantern, 10, (1, 1.3, 1)); lib.light("POINT", T(x - 0.8, 2.6, 4.1), 15, (1.0, 0.5, 0.2), 0.1)
    K.build()
    # bamboo groves behind the houses
    bam = mat_once("vbam", lambda: worn("vbam", "#7a9a3a", "#a89a4a", 0.35, 0.0, 4, 0.55, "#5a7a2a"))
    bf = CK.jungle_srcs()["fr"]
    for g, (gx, gz) in enumerate(((-16, 13), (16, 14), (0, 20), (-28, 16), (26, 18))):
        for k in range(10):
            px, pz = gx + rnd.uniform(-2, 2), gz + rnd.uniform(-2, 2); h = rnd.uniform(7, 11); lean = rnd.uniform(-0.1, 0.1); y0 = gfn(px, pz)
            tube(f"bam{g}{k}", [(px, y0, pz), (px + lean * h * 0.5, y0 + h * 0.5, pz), (px + lean * h, y0 + h, pz)], 0.05, bam, res=4, bres=1)
            for j in range(3): CK._cp(bf[j % 3], f"bl{g}{k}{j}", (px + lean * h * (0.6 + j * 0.15), y0 + h * (0.6 + j * 0.15), pz), rnd.random() * 6.3, rnd.uniform(0.8, 1.2))
    # the crash-landed B-25 nose-down in the paddy, mud splashed around it
    b = CK.inst(CK.plane("b25", gear=False, spin=False), "crash"); CK.place(b, (15, 1.3, -17), (0.6, -0.22, -0.75), 0.25)
    mud = pm("#3a2e1e", 0.9)
    for k in range(8): CK.puff(f"mud{k}", (14 + rnd.uniform(-6, 6), 0.05, -16 + rnd.uniform(-5, 5)), (rnd.uniform(0.8, 1.6), 0.2, rnd.uniform(0.8, 1.6)), mud, k, True)
    # the revenge: a burning roof and smoke over the empty village
    burn = CK.fireball("vfire", (11, 4.0, 7.0), 1.6, 3, 900) + CK.fireball("vfire2", (19, 4.0, 8.0), 1.3, 4, 600)
    burn += CK.smoke("vsmk", (11, 5, 7), 60, 2.5, 14, "#1e1a18", 0.85, (-20, 8), 3, 10) + CK.smoke("vsmk2", (19, 5, 8), 50, 2, 12, "#2a2420", 0.8, (-18, 6), 6, 9)
    burn += CK.smoke("vsmk3", (-40, 2, 30), 70, 6, 18, "#3a3230", 0.6, (-15, 5), 9, 8)
    CK.area((6, 5, -12), (0, 1.5, 2), 1800, (1.0, 0.62, 0.35), 10)
    CK.area((-6, 4, 2), (-5, 1.0, 5.5), 120, (1.0, 0.55, 0.25), 2)
    def update(f): CK.show(burn, f >= F_REVENGE)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
