# Ethiopian highlands, October 1935 (chapter 2 shot 20). Three coords, the camera looks +z down a dusty road (x 0,
# |x| < 3 clear, z -10..60) that the Italian column drives along toward the camera (tankettes and lorries are built
# here at z 18..45; soldiers are staged in front at z 4..14). A rocky outcrop at (-7, 0, 7) (top y ~1.2) where the
# Emperor and his warriors stand; a village of round thatched tukuls at x 7..18, z 6..22 with stone walls and a well;
# flat-topped ambas and acacias on golden grass, a sign ADDIS ABEBA. Light: hot high sun from -x/-z, warm bounce.
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached, set_world
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK

def tukul(K, x, z, r, rnd, wall, thatch, door):
    K.cyl((x, 1.1, z), r, 2.2, wall, 20, "y", None, 0, 0.0)
    K.cyl((x, 2.2 + r * 0.75, z), r + 0.5, r * 1.5, thatch, 20, "y", 0.08, rnd.uniform(0, 6))
    K.cyl((x, 2.25, z), r + 0.55, 0.12, thatch, 20)
    K.cyl((x, 2.2 + r * 1.55, z), 0.05, 0.6, pm("#3a2a1a", 0.6), 6); K.sphere((x, 2.2 + r * 1.85, z), 0.09, pm("#c8a040", 0.4, 0.6), 8)
    a = rnd.uniform(-0.6, 0.6); K.box((x - r * math.sin(a), 0.85, z - r * math.cos(a)), (0.8, 1.7, 0.1), door, a, 0.02)

def build(M, D):
    random.seed(1935); KS.reset(); rnd = random.Random(35)
    K = Kit("ethiopia")
    set_world((0.3, 0.5, 0.85), (0.86, 0.82, 0.74), 1.0, (0.26, 0.48, 0.86), (0.9, 0.84, 0.72))
    GR = CK.ground_mat("egrass", "#b89a52", "#8a7038", 0.25); DUST = CK.ground_mat("edust", "#b88a5a", "#946a40", 0.4); ROCK = grime("erock", "#8a7a6a", 0.45, 2.5)
    def H(x, z): return 0.0 if abs(x) < 5 and z < 70 else 0.25 * math.sin(x * 0.11) * math.sin(z * 0.07) * min(1.0, (abs(x) - 5) / 10 if abs(x) >= 5 else 0) + max(0, (abs(x) - 30)) * 0.08
    CK.terrain("eground", -90, 90, -20, 160, 60, 60, H, GR)
    K.box((0, 0.01, 30), (6.5, 0.02, 100), DUST, 0, 0)
    for k in range(90): K.sphere((rnd.uniform(-3.4, 3.4), 0.0, rnd.uniform(-10, 70)), rnd.uniform(0.05, 0.15), DUST, 6, (1.4, 0.35, 1.0))
    for k in range(40): K.box((rnd.choice((-1.3, 1.3)) + rnd.uniform(-0.1, 0.1), 0.022, rnd.uniform(-10, 70)), (0.3, 0.006, rnd.uniform(1, 4)), pm("#8a6440", 0.9), 0, 0)
    CK.grass_patch(K, -30, -3.5, -12, 60, 900, [pm("#c8a860", 0.8), pm("#a88a48", 0.8), pm("#d8b870", 0.8)], rnd, (0.25, 0.65), hfn=H)
    CK.grass_patch(K, 3.5, 30, -12, 60, 900, [pm("#c8a860", 0.8), pm("#a88a48", 0.8), pm("#d8b870", 0.8)], rnd, (0.25, 0.65), hfn=H)
    LEAF = pm("#5a6a2a", 0.75); BARK = pm("#4a3a28", 0.8)
    for k in range(26):
        x = rnd.choice((-1, 1)) * rnd.uniform(6, 60); z = rnd.uniform(-5, 120)
        if 6 < x < 19 and 4 < z < 24: continue
        CK.acacia(K, x, z, rnd.uniform(4, 7), LEAF, BARK, H(x, z), rnd)
    # ambas: flat-topped mountains on the horizon
    for k in range(7):
        x = rnd.uniform(-150, 150); z = rnd.uniform(170, 260); r = rnd.uniform(20, 45)
        K.cyl((x, r * 0.35, z), r, r * 0.7, grime("eamba", "#8a6a4a", 0.4), 16, "y", r * 0.82)
        K.cyl((x, r * 0.72, z), r * 0.82, 0.6, pm("#6a7a3a", 0.8), 16)
    # the outcrop
    for k in range(9):
        K.sphere((-7 + rnd.uniform(-1.5, 1.5), rnd.uniform(0.0, 0.6), 7 + rnd.uniform(-1.2, 1.2)), rnd.uniform(0.8, 1.5), ROCK, 10, (1.3, 0.55, 1.0))
    K.box((-7, 0.6, 7.2), (3.2, 1.2, 2.2), ROCK, 0.2, 0.4)
    for k in range(6): K.sphere((-7 + rnd.uniform(-4, 4), 0.1, 7 + rnd.uniform(-3, 3)), rnd.uniform(0.2, 0.5), ROCK, 8, (1.2, 0.6, 1.0))
    # Ethiopian banner (green-yellow-red tricolour) on a spear-pole by the outcrop
    a = IK.canvas(256, 384, "#2a8a3a"); IK.rect(a, 0, 1 / 3, 1, 2 / 3, "#f2d040"); IK.rect(a, 0, 2 / 3, 1, 1, "#c8202a")
    CK.flagpole(K, (-8.4, 1.1, 7.6), 3.6, IK.img_mat("eflag", a, 0.7, sheen=0.3), 1.5, 1.0, wood("#6a4a2a", "#3a2614", 10))
    # the village
    WALL = grime("ewall", "#a8805a", 0.4, 3.0); TH = pm("#b89a5a", 0.95); DOOR = wood("#5a3a1e", "#2e1e10", 8)
    for k, (x, z, r) in enumerate(((9, 8, 2.2), (14, 10, 2.6), (11, 15, 2.0), (17, 17, 2.4), (8, 20, 1.8))): tukul(K, x, z, r, rnd, WALL, TH, DOOR)
    for k in range(40):
        t = k / 40; x = 6.5 + 12 * t; z = 4.5 + 2 * math.sin(t * 9)
        K.sphere((x, 0.25, z), rnd.uniform(0.25, 0.4), ROCK, 7, (1.2, 0.8, 1.0))
    K.cyl((12, 0.45, 4.8), 0.8, 0.9, ROCK, 14); K.box((12, 1.6, 4.8), (2.0, 0.08, 0.08), wood("#5a4030", "#2e2016", 6), 0, 0.01)
    for sd in (-1, 1): K.cyl((12 + sd * 0.9, 0.8, 4.8), 0.05, 1.6, wood("#5a4030", "#2e2016", 6), 6)
    for k in range(5): K.cyl((rnd.uniform(7, 18), 0.35, rnd.uniform(6, 22)), 0.25, 0.7, pm("#a8582a", 0.6), 10, "y", 0.15)
    # the Italian column (tankettes, lorries) coming down the road toward the camera
    for k, z in enumerate((20.0, 26.0, 31.5)): CK.tankette(K, 0.6 * (-1) ** k, z, R90 + rnd.uniform(-0.05, 0.05))
    for k, z in enumerate((38.0, 46.0, 54.0)): CK.lorry(K, 0.0, z, R90, "#8a7a52", "#a89868")
    sign(K, (3.8, 1.9, 2.0), 1.6, 0.45, -0.3, "ADDIS ABEBA 300", "#f2ead6", pm("#1a1a1a", 0.5), "sans", "#1a1a1a")
    K.cyl((3.8, 0.85, 2.04), 0.05, 1.7, wood("#6a4a2a", "#3a2614", 10), 6)
    IK.sun((0.35, -0.85, 0.4), 4.0, (1.0, 0.92, 0.78), 1.2)
    lib.light("AREA", T(0, 6, -12), 1800, (1.0, 0.88, 0.72), 14).rotation_euler = (math.radians(-75), 0, math.pi)
    K.build()
    return {}
