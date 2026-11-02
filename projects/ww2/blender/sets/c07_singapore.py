# Singapore, February 1942 (chapter 7 shots 17-19): the fortress's huge coastal gun points out to sea; the Japanese come
# out of the jungle behind it on bicycles; the garrison surrenders.
# three.js layout: the 15-inch gun pit centred at the origin (concrete ring r 7, wall top y 1.2), shield at z -1..5,
# barrel pointing +z (seaward) to z ~20 at y ~6. Sea from z 42 (y -0.25), beach z 30..42. Ground y 0 elsewhere.
#   The British stand on the seaward apron at x -6..6, z 7..10 (facing +z) and around the pit; the officer with the
#   rangefinder at (6.5, 0, 5). A dirt road runs from the jungle edge (z -44) to the pit (z -8) along x -4..4.
#   Riders: bicycles (Blender) and riders (cast) share BIKES / bike_pos(k, f): six riders, f 2195..2305.
#   Surrender ground (shot 19): the road at x -6..6, z -24..-12 (keep clear of props).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, poster, crate, barrel
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK
from sets import ikit

SUN = (0.75, 0.55, 0.35)
BIKES = [(-4.5, 0.0), (-1.5, 1.6), (1.5, 0.4), (4.2, 2.2), (-3.0, 4.5), (0.4, 5.2)]   # (x, z lag)
def bike_pos(k, f):
    x, lag = BIKES[k]
    return (x + 0.3 * math.sin(f * 0.05 + k), 0.0, -40.0 - lag + 4.0 * (f - 2195) / 30.0)
def ground(x, z):
    return -0.25 - 1.6 * CK.smooth(30, 42, z) + 0.15 * math.sin(x * 0.2) * math.sin(z * 0.15) * (1 - CK.smooth(-12, -8, z) * CK.smooth(12, 8, abs(x)))

def build(M, D):
    rnd = random.Random(1942)
    S = bpy.context.scene
    CK.sky(S.world, SUN, [(0.0, (0.86, 0.84, 0.78)), (0.06, (0.55, 0.68, 0.84)), (0.35, (0.2, 0.42, 0.74)), (1.0, (0.06, 0.18, 0.5))],
           sun_col=(30, 26, 18), cloud_dark=(0.45, 0.46, 0.52), cloud_lit=(1.35, 1.25, 1.1), cover=0.6, strength=0.75, glow_col=(1.0, 0.9, 0.7), glow=0.4)
    CK.sun_light(SUN, 5.0, (1.0, 0.9, 0.75), 1.5)
    grass = mat_once("sgrass", lambda: CK.green_hill_mat("sgrass", "#6a8a2a", "#4a6a1e", "#9a6a3a"))
    CK.heightfield("sground", -120, 120, -120, 60, 1.5, lambda x, z: ground(x, z) + 0.25, grass)
    road = mat_once("sroad", lambda: lib.plaster("sroad", "#a8683a"))
    mesh_obj("road", [(-4, 0.27, -46), (4, 0.27, -46), (4, 0.27, -7), (-4, 0.27, -7)], [(0, 1, 2, 3)], road)
    CK.sea("ssea", -3000, 3000, 38, 4000, -0.25, CK.water_mat("swater", "#0e4a5a", "#2a8a8a", 0.8, 0.05, 0.4))
    CK.heightfield("sbeach", -120, 120, 26, 46, 2, lambda x, z: 0.0 - 1.4 * CK.smooth(28, 44, z), mat_once("ssand", lambda: lib.plaster("ssand", "#d8c48a")))
    for k in range(4): CK.heightfield(f"isl{k}", -300 + k * 380, -60 + k * 380, 700 + k * 150, 900 + k * 150, 20, (lambda kk: lambda x, z: -5 + 40 * max(0, 1 - ((x - (-180 + kk * 380)) / 120) ** 2 - ((z - (800 + kk * 150)) / 100) ** 2))(k), grass)
    K = Kit("bat")
    conc = mat_once("sconc", lambda: worn("sconc", "#a8a49a", "#6a665e", 0.85, 0.0, 2.0, 0.55, "#7a766a"))
    gun = mat_once("sgun", lambda: worn("sgun", "#5a6450", "#3a3e34", 0.5, 0.3, 1.5, 0.6, "#4a5242"))
    dk = pm("#2a2c2a", 0.5, 0.5)
    # concrete pit: ring wall in segments, floor, steps, ready-use lockers
    K.cyl((0, 0.27, 0), 7.2, 0.06, conc, 40)
    for k in range(28):
        a = k / 28 * math.tau
        if abs(math.cos(a) + 1) < 0.15: continue
        K.box((7.3 * math.sin(a), 0.85, 7.3 * math.cos(a)), (1.7, 1.2, 0.8), conc, a, 0.04)
    # gun: turntable, open-backed shield, cradle, the long barrel
    K.cyl((0, 0.45, 0.8), 5.0, 0.4, gun, 40)
    K.box((0, 2.9, 2.2), (6.4, 4.4, 5.6), gun, 0.0, 0.25); K.box((0, 5.15, 1.4), (6.0, 0.25, 4.6), gun, 0.0, 0.1)
    K.box((0, 2.9, -0.8), (5.6, 3.6, 0.2), dk, 0.0, 0.0)
    for k in range(6): K.box((-2.8 + k * 1.12, 2.5, 5.05), (0.25, 0.25, 0.25), dk, 0.0, 0.02)
    K.cyl((0, 3.4, 6.2), 1.0, 2.8, gun, 24, "z", None, 0.0, 0.0, 0.0)
    L = 16.0; el = math.radians(9)
    for i in range(8):
        f0 = i / 8; r = 0.75 - 0.3 * f0
        K.cyl((0, 3.4 + math.sin(el) * (7.6 + L * (f0 + 0.0625)), 7.6 + math.cos(el) * L * (f0 + 0.0625)), r, L / 8 + 0.02, gun, 24, "z", r - 0.04, 0.0, 0.0, -el)
    K.cyl((0, 3.4 + math.sin(el) * (7.6 + L), 7.6 + math.cos(el) * L), 0.5, 0.6, dk, 24, "z", None, 0.0, 0.0, -el)
    # shells on a rack, a hoist, ammunition lockers, sandbags, rangefinder, searchlight
    brassm = pm("#c8963a", 0.3, 1.0); shellm = pm("#4a4a3a", 0.5, 0.5)
    for k in range(6):
        x = -6.2 + (k % 3) * 0.55; z = -2.5 - (k // 3) * 0.6
        K.cyl((x, 1.1, z), 0.19, 1.3, shellm, 16); K.cyl((x, 1.85, z), 0.19, 0.2, shellm, 16, "y", 0.02); K.cyl((x, 0.55, z), 0.2, 0.12, brassm, 16)
    K.box((-6.2, 0.35, -2.8), (2.0, 0.15, 1.6), wood("#6a4a2a", "#3a2414", 6.0, 0.7), 0.0, 0.01)
    K.box((-3.0, 2.5, -3.0), (0.25, 4.6, 0.25), dk, 0.0, 0.0); K.box((-3.0, 4.8, -2.0), (0.25, 0.25, 2.3), dk, 0.0, 0.0)
    tube("hoistc", [(-3.0, 4.8, -1.0), (-3.0, 2.2, -1.0)], 0.03, pmat("scab", "#1a1a1a", 0.6), res=2, bres=0)
    for k in range(3): K.box((5.0 + k * 1.1, 0.75, -3.4), (1.0, 1.0, 0.7), pm("#4a5a3a", 0.6), 0.0, 0.03)
    for k in range(3): ktext("15 IN", (5.0 + k * 1.1, 0.85, -3.76), 0.18, pm("#e8e4d8", 0.8), 0.0, "sans", 0.001)
    sand = mat_once("ssandbag", lambda: lib.cloth("ssandbag", "#b8a878"))
    for row in range(3):
        for k in range(12):
            a = -0.9 + k * 0.16; x, z = 9.0 * math.sin(a) + 2, -9.0 * math.cos(a) * 0.4 - 8
            K.box((x + (row % 2) * 0.2, 0.42 + row * 0.3, z), (0.6, 0.3, 0.38), sand, a, 0.08)
    K.cyl((6.5, 0.9, 5.4), 0.06, 1.3, dk, 8); K.box((6.5, 1.65, 5.4), (1.6, 0.18, 0.2), pm("#3a3e34", 0.4, 0.4), 0.0, 0.02)
    for sd in (-1, 1): K.cyl((6.5 + sd * 0.8, 1.65, 5.4), 0.1, 0.25, dk, 12, "z")
    K.cyl((-8.5, 1.0, 4.0), 0.12, 2.0, dk, 8); K.cyl((-8.5, 2.2, 4.0), 0.6, 0.7, pm("#3a3e34", 0.4, 0.4), 24, "z"); K.cyl((-8.5, 2.2, 4.38), 0.52, 0.04, em("#f2ecd8", 0.4), 24, "z")
    # barracks huts with attap roofs, a flagpole with the Union flag, notice board, signpost
    att = mat_once("satap", lambda: lib.brickmat("satap", "#8a7a4a", "#6a5a34", "#4a3e26", 6.0, 3.0, 0.06, 0.95))
    for k, (x, z) in enumerate(((-17, -10), (17, -12), (-24, 2))):
        K.box((x, 1.4, z), (8, 2.8, 5), wood("#9a7a52", "#6a4a2a", 3.0, 0.8), 0.0, 0.02)
        for sd in (-1, 1): K.box((x, 3.55, z + sd * 1.55), (8.6, 0.12, 3.6), att, 0.0, 0.0, sd * 0.6)
        for j in range(4): K.box((x - 3 + j * 2, 1.6, z - 2.52), (0.9, 0.8, 0.05), pm("#1e2420", 0.3), 0.0, 0.0)
    K.cyl((9.5, 4.5, -4.5), 0.07, 9.0, pm("#e8e4dc", 0.5), 10); K.sphere((9.5, 9.05, -4.5), 0.12, pm("#c8a24a", 0.3, 0.8), 10)
    sign(K, (2.0, 1.6, -9.5), 2.6, 0.7, 0.0, "JOHORE BATTERY", board="#1e2a1e", ink=pm("#f2efe6", 0.5), kind="sans", trim="#c8a24a")
    for sx in (-1.0, 1.0): K.cyl((2.0 + sx, 0.9, -9.48), 0.06, 1.8, wood("#6a4a2a", "#3a2414", 6.0, 0.7), 8)
    sign(K, (-6.8, 2.0, -12), 1.6, 0.4, 0.3, "SEA FRONT  >", board="#e8e4dc", ink=pm("#1a1a1a", 0.5), kind="sans")
    K.cyl((-6.8, 1.0, -12), 0.05, 2.2, wood("#6a4a2a", "#3a2414", 6.0, 0.7), 8)
    K.build()
    ikit.flag("ukflag", (9.45, 8.9, -4.5), 2.2, 1.3, mat_once("ukflag", lambda: ikit.img_mat("ukflag", ikit.flag_img("uk"), 0.8)), math.pi, 0.08)
    # palms and the jungle wall behind the fortress
    pf = CK.palm_srcs(rnd); trunk = CK.palm_trunk()
    gf = lambda x, z: ground(x, z) + 0.25
    for k, (x, z) in enumerate(((-12, 14), (14, 16), (-20, 24), (22, 26), (-9, -18), (11, -22), (-30, -6), (28, -4), (-14, 30), (16, 33), (-40, 18), (40, 20))):
        CK.palm(f"sp{k}", x, gf(x, z), z, rnd.uniform(9, 14), 0.15, rnd.uniform(0, 6), pf, trunk, rnd, 1.2)
    CK.jungle_wall("jw", -60, 60, -70, -45, gf, rnd, 120, 24, pf, trunk)
    CK.jungle_wall("jw2", -60, -5, -47, -40, gf, rnd, 70, 6, pf, trunk)
    CK.jungle_wall("jw3", 5, 60, -47, -40, gf, rnd, 70, 6, pf, trunk)
    CK.jungle_wall("jw4", -5, 5, -60, -48, gf, rnd, 20, 3)
    # the bicycles
    bikes = [CK.inst(CK.bicycle(), f"bk{k}") for k in range(len(BIKES))]
    CK.area((-6, 4, -14), (0, 1.5, 3), 1500, (1.0, 0.85, 0.7), 8)
    def update(f):
        on = 2150 <= f < 2310
        for k, o in enumerate(bikes):
            o.hide_render = not on
            if on: x, y, z = bike_pos(k, f); CK.place(o, (x, gf(x, z), z), (0, 0, 1))
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
