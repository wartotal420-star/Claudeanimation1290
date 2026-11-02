# Guadalcanal, August 1942 - February 1943 (chapter 7 shots 42-47, 49): the beach landing, Henderson Field, the foxhole,
# night shelling, rain, and the Japanese night evacuation. One module, state by chapter-local frame:
#   day (landing, airfield, planes overhead), NIGHT ranges (shelling 5330..5465, evacuation 5772..5885), RAIN 5550..5678.
# three.js layout (y up): sea z > 32 (y -0.25), beach sand z 12..34, palm grove z -12..12, the foxhole pit centred
#   (4, 0, 2) (r 1.6, floor y -0.95, sandbag rim y 0..0.5; marines stand in it at y -0.95), Henderson Field z -45..-75
#   (runway along x, y 0.05), the pagoda tower at (-18, 0, -40), the flag pole at (-6, 0, -36), Wildcats parked at z -50.
#   Landing craft (LCVP) run in from z 140 to the beach (z 30) during f 5045..5200 at x -24..24; then stay beached.
#   Keep clear for characters: beach x -20..20, z 16..28; the airfield apron x -12..6, z -40..-32; the foxhole.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, crate, barrel
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK
from sets import front as FR

SUN = (0.6, 0.62, 0.45)
NIGHT = [(5300, 5470), (5740, 5900)]
RAIN = (5540, 5700)
LCVP_X = [-24, -12, 0, 12, 24]
def night(f): return any(a <= f < b for a, b in NIGHT)
def rain(f): return RAIN[0] <= f < RAIN[1]
def gfn(x, z):
    h = 0.12 * math.sin(x * 0.15) * math.cos(z * 0.11)
    if z > 12: h += -0.4 * CK.smooth(12, 36, z) * 1.0 - 0.9 * CK.smooth(28, 40, z)
    if math.hypot(x - 4, z - 2) < 1.6: h = -0.95
    return h
def lcvp_pos(k, f):
    u = min(1.0, max(0.0, (f - 5045 - k * 6) / 150.0)); u = 1 - (1 - u) ** 2
    return (LCVP_X[k] + 0.5 * math.sin(k), -0.05, 140 - 108 * u)

def build(M, D):
    rnd = random.Random(1942)
    S = bpy.context.scene
    W_day = S.world
    CK.sky(W_day, SUN, [(0.0, (0.82, 0.84, 0.82)), (0.06, (0.5, 0.66, 0.84)), (0.35, (0.18, 0.4, 0.72)), (1.0, (0.06, 0.18, 0.5))],
           sun_col=(30, 26, 18), cloud_dark=(0.4, 0.42, 0.5), cloud_lit=(1.35, 1.25, 1.1), cover=0.65, strength=0.75, glow_col=(1.0, 0.9, 0.7), glow=0.35)
    W_night = bpy.data.worlds.new("wnight"); W_night.use_nodes = True
    CK.sky(W_night, (-0.3, 0.5, 0.8), [(0.0, (0.07, 0.09, 0.16)), (0.2, (0.035, 0.045, 0.1)), (1.0, (0.01, 0.014, 0.04))],
           sun_col=(4, 4, 5), cloud_dark=(0.005, 0.006, 0.012), cloud_lit=(0.08, 0.09, 0.14), cover=0.5, strength=1.0, glow_col=(0.3, 0.35, 0.5), glow=0.1)
    W_rain = bpy.data.worlds.new("wrain"); W_rain.use_nodes = True
    CK.sky(W_rain, (0.3, 0.5, -0.8), [(0.0, (0.36, 0.4, 0.4)), (0.15, (0.26, 0.3, 0.32)), (1.0, (0.12, 0.14, 0.17))],
           sun_col=(2, 2, 2), cloud_dark=(0.14, 0.16, 0.18), cloud_lit=(0.36, 0.38, 0.4), cover=1.0, strength=0.9, glow=0.1, band=(0.0, 0.4), fade=(1.0, 0.7))
    sun = CK.sun_light(SUN, 5.0, (1.0, 0.9, 0.75), 1.5)
    moon = CK.sun_light((-0.3, 0.5, 0.8), 0.9, (0.55, 0.65, 1.0), 1.0)
    grey = CK.sun_light((0.2, 0.8, -0.4), 1.3, (0.8, 0.86, 0.92), 15)
    soil = mat_once("gsoil", lambda: CK.green_hill_mat("gsoil", "#5a5a2a", "#3e3a1e", "#6a5236"))
    CK.heightfield("gground", -120, 120, -130, 12, 1.0, gfn, soil)
    sand = mat_once("gsand", lambda: CK.green_hill_mat("gsand", "#c8b07a", "#a8946a", "#8a7a5a"))
    CK.heightfield("gbeach", -120, 120, 11, 46, 1.0, gfn, sand)
    CK.sea("gsea", -3000, 3000, 30, 4000, -0.25, CK.water_mat("gwater", "#0e4050", "#2a7a7a", 0.8, 0.05, 0.4))
    CK.whitecaps("gcaps", -200, 200, 32, 400, 300, rnd, -0.22, (2, 6))
    foam = mat_once("ffoam", FR.foam_mat); CK.whitecaps("surf", -120, 120, 31.2, 33.5, 160, rnd, -0.21, (3, 8))
    # far islands (Savo, Tulagi) across the sound
    hill = mat_once("ghill", lambda: CK.green_hill_mat("ghill", "#2e5a2a", "#1a3a1a", "#4a4a3a"))
    CK.heightfield("savo", -900, -300, 1800, 2400, 30, lambda x, z: -10 + 260 * max(0, 1 - ((x + 600) / 300) ** 2 - ((z - 2100) / 300) ** 2), hill)
    CK.heightfield("tulagi", 400, 1600, 2600, 3400, 40, lambda x, z: -10 + 180 * max(0, 1 - ((x - 1000) / 600) ** 2 - ((z - 3000) / 400) ** 2), hill)
    K = Kit("gd")
    olive = pm("#4a4a30", 0.7); olive2 = pm("#5a5a38", 0.6, 0.2); drum = pm("#5a5a3a", 0.5, 0.4); hoop = pm("#2a2a26", 0.5, 0.5)
    sb = mat_once("gsb", lambda: lib.cloth("gsb", "#8a7a52")); logm = wood("#5a4630", "#3a2a1a", 3.0, 0.9)
    # the foxhole: sandbag ring, log cover, poncho, helmets, ammo boxes, a field telephone, ration tins, a rifle against the rim
    for row in range(2):
        for k in range(14):
            a = k / 14 * math.tau + row * 0.2
            K.box((4 + 1.85 * math.cos(a), 0.15 + row * 0.28, 2 + 1.85 * math.sin(a)), (0.6, 0.28, 0.36), sb, -a + math.pi / 2, 0.08)
    for k in range(3): K.cyl((2.6 + k * 0.5, 0.75, 3.6), 0.14, 2.2, logm, 10, "x")
    K.box((5.6, 0.55, 3.4), (1.2, 0.04, 1.0), pm("#3e4a2a", 0.9), 0.0, 0.0, 0.0, 0.2)
    for k in range(3): K.box((6.2 + k * 0.42, 0.18, 0.4), (0.38, 0.3, 0.22), olive2, 0.2, 0.02)
    K.box((2.0, 0.6, 0.8), (0.25, 0.2, 0.18), pm("#3a3a2a", 0.5), 0.3, 0.02)
    for k in range(5): K.cyl((6.0 + k * 0.16, 0.1, 1.2), 0.05, 0.1, pm("#8a8a7a", 0.4, 0.6), 10)
    K.sphere((2.3, 0.62, 2.2), 0.17, pm("#4a5034", 0.6), 12, (1, 0.6, 1))
    # the beachhead: supply dumps, crates, drums, a jeep, barbed wire, a beach-party sign, life jackets, a wrecked boat
    for k in range(10): crate(K, (-28 + (k % 5) * 1.0, 0.36 + (k // 5) * 0.62, 18 + (k % 2) * 0.4), 0.8, wood("#8a6a3a", "#5a4020", 5.0, 0.8), 0.15 * k)
    for k in range(9): barrel(K, (22 + (k % 3) * 0.7, 0.45, 16 + (k // 3) * 0.7), 0.3, 0.9, drum, hoop)
    for k in range(6): K.box((26 + (k % 3) * 0.9, 0.2 + (k // 3) * 0.35, 21), (0.8, 0.35, 0.55), olive2, 0.2, 0.03)
    K.box((-18, 0.9, 22), (1.6, 0.6, 3.2), olive, 0.1, 0.08); K.box((-18, 1.35, 22.6), (1.5, 0.5, 0.06), pm("#8a9aa8", 0.1), 0.1, 0.0)
    for sd in (-1, 1):
        for e in (-1.1, 1.1): K.cyl((-18 + sd * 0.8, 0.4, 22 + e), 0.4, 0.25, pm("#141414", 0.8), 14, "x", None, 0.1)
    sign(K, (14, 1.6, 24), 2.0, 0.6, math.pi, "RED BEACH", board="#a82a22", ink=pm("#f2efe6", 0.5), kind="sans")
    K.cyl((14, 0.8, 24.05), 0.06, 1.6, wood("#6a5034", "#3a2a1a", 4.0, 0.8), 8)
    wire = pmat("gwire", "#3a3430", 0.6, 0.5)
    for k in range(3):
        for j in range(14): K.torus((-40 + k * 30 + j * 0.45, 0.35, 28), 0.35, 0.012, wire, 14, 3, "x")
    K.box((34, 0.4, 30), (3.0, 1.0, 8), pm("#4e5a4a", 0.6), 0.6, 0.1, 0.0, 0.25)
    # palm grove (many palms are shot up), wrecked trunks, jungle walls at the sides and back
    K.build()
    pf = CK.palm_srcs(rnd); trunk = CK.palm_trunk()
    for k in range(40):
        x, z = rnd.uniform(-60, 60), rnd.uniform(-28, 12)
        if math.hypot(x - 4, z - 2) < 4 or (-20 < x < 20 and z > 10): continue
        CK.palm(f"gp{k}", x, gfn(x, z), z, rnd.uniform(9, 16), 0.18, rnd.uniform(0, 6), pf, trunk, rnd, 1.2, nuts=k % 2 == 0)
    for k in range(6):
        x, z = rnd.uniform(-40, 40), rnd.uniform(-25, 8)
        tube(f"stump{k}", [(x, 0, z), (x + 0.1, rnd.uniform(2, 4), z)], 0.22, trunk, res=2, bres=1)
    gf = gfn
    CK.jungle_wall("jwl", -110, -62, -120, 10, gf, rnd, 60, 14, pf, trunk)
    CK.jungle_wall("jwr", 62, 110, -120, 10, gf, rnd, 60, 14, pf, trunk)
    CK.jungle_wall("jwb", -62, 62, -125, -95, gf, rnd, 70, 16, pf, trunk)
    # Henderson Field: runway, Marston-mat apron, the pagoda tower, a hangar, Wildcats, fuel drums, the flag pole, signs
    A = Kit("air")
    coral = mat_once("gcoral", lambda: lib.plaster("gcoral", "#b8a888"))
    A.box((0, 0.05, -60), (220, 0.1, 30), coral, 0.0, 0.0)
    mat = pm("#5a5e50", 0.6, 0.4)
    for k in range(20): A.box((-12 + k * 0.9, 0.06, -36), (0.6, 0.02, 8), mat, 0.0, 0.0)
    tw = wood("#6a5034", "#3a2a1a", 4.0, 0.8)
    for lv in range(3):
        y = lv * 3.0; w = 6 - lv * 1.4
        for sx in (-1, 1):
            for sz in (-1, 1): A.box((-18 + sx * w / 2, y + 1.5, -40 + sz * w / 2), (0.3, 3.0, 0.3), tw, 0.0, 0.0)
        A.box((-18, y + 3.0, -40), (w + 0.6, 0.2, w + 0.6), tw, 0.0, 0.0)
        for sd in (-1, 1): A.box((-18, y + 3.4, -40 + sd * (w / 2 + 0.6) * 0.6), (w + 1.6, 0.1, (w / 2 + 0.6) * 1.3), pm("#5a3a24", 0.8), 0.0, 0.0, -sd * 0.35)
    A.box((-18, 10, -40), (2.0, 1.4, 2.0), tw, 0.0, 0.0); A.box((-18, 11.2, -40), (3.0, 0.1, 3.0), pm("#5a3a24", 0.8), 0.0, 0.0)
    A.box((22, 4, -86), (26, 8, 18), pm("#6a6a5a", 0.6, 0.4), 0.0, 0.0); A.cyl((22, 8, -86), 9.2, 26, pm("#5a5e5a", 0.6, 0.4), 20, "x")
    A.box((22, 3.5, -76.9), (18, 7, 0.2), pm("#141414", 0.8), 0.0, 0.0)
    for k in range(12): barrel(A, (8 + (k % 4) * 0.7, 0.5, -33 - (k // 4) * 0.7), 0.3, 0.9, drum, hoop)
    for k in range(6): crate(A, (-9 + (k % 3) * 0.9, 0.36 + (k // 3) * 0.6, -31.5), 0.75, wood("#8a6a3a", "#5a4020", 5.0, 0.8), 0.1 * k)
    sign(A, (-2.0, 2.2, -31.0), 3.6, 0.8, math.pi, "HENDERSON FIELD", board="#e8e2d2", ink=pm("#1e2a3a", 0.5), kind="sans", trim="#4a3a2a")
    for sx in (-1.6, 1.6): A.cyl((-2.0 + sx, 1.1, -30.98), 0.07, 2.2, tw, 8)
    A.cyl((-6, 5, -36), 0.07, 10, pm("#d8d4c8", 0.5), 10)
    A.build()
    import sets.ikit as ikit
    flag = ikit.flag("gflag", (-6.04, 9.8, -36), 2.0, 1.1, CK.us_flag_mat(), math.pi, 0.08)
    for k in range(5):
        o = CK.inst(CK.plane("wildcat", gear=True, spin=False), f"gw{k}"); CK.place(o, (-30 + k * 14, 1.4, -52), (0, 0.14, 1))
    # landing craft (LCVP): plywood hull, steel bow ramp, coxswain's position; they run in, then sit on the beach
    L = Kit("lcvp"); ply = pm("#4e5a4a", 0.6); steel = pm("#3e4446", 0.5, 0.5)
    L.box((0, 0.5, 0), (3.2, 1.2, 9.5), ply, 0.0, 0.1); L.box((0, 0.95, 4.9), (3.1, 1.6, 0.3), steel, 0.0, 0.05, -0.12)
    L.box((0, 0.2, 0.0), (2.8, 0.1, 8.8), pm("#2a2a26", 0.8), 0.0, 0.0)
    for sd in (-1, 1): L.box((sd * 1.45, 1.2, -0.6), (0.2, 0.35, 8.0), ply, 0.0, 0.02)
    L.box((0, 1.4, -4.2), (1.4, 0.8, 0.8), steel, 0.0, 0.03)
    src = L.build()[0]; src.location = T(0, -500, 0)
    boats = [CK.inst(src, f"lc{k}") for k in range(5)]
    jboats = [CK.inst(src, f"jb{k}") for k in range(3)]
    for k, o in enumerate(jboats): CK.place(o, (-14 + k * 10, -0.05, 31.5), (0.1 * (k - 1), 0, -1))
    # night: Japanese destroyers offshore with gun flashes; shells bursting on the airfield
    before = set(bpy.data.objects.keys())
    for k, (x, z) in enumerate(((-300, 700), (100, 800), (450, 650))): FR.warship(f"jdd{k}", x, z, math.pi * 0.95, 110, 11, "destroyer", 0.6)
    for k in list(bpy.data.objects.keys()):
        if k.startswith("jdd") and "smk" in k: bpy.data.objects.remove(bpy.data.objects[k])
        elif k.startswith("jdd") and "ensign" in k: bpy.data.objects[k].data.materials[0] = CK.jp_flag_mat()
    dds = [bpy.data.objects[k] for k in set(bpy.data.objects.keys()) - before if k in bpy.data.objects]
    flashes, bursts = [], []
    for k, (x, z) in enumerate(((-280, 700), (120, 800), (470, 650))):
        flashes.append((k, [CK.puff(f"gfl{k}", (x, 8, z - 20), (14, 6, 14), lib.emit(f"gflm{k}", (1.0, 0.75, 0.4), 30), k)] + [lib.light("POINT", T(x, 20, z - 40), 4e6, (1.0, 0.7, 0.4), 4)]))
    for k, (x, z) in enumerate(((-30, -62), (12, -55), (40, -66), (-8, -20), (25, -10))):
        bursts.append((5350 + k * 22, CK.fireball(f"gb{k}", (x, 0.3, z), 3.0, k, 60000) + CK.smoke(f"gbs{k}", (x, 3, z), 30, 3, 9, "#2a2420", 0.8, (0, 0), k + 7, 5)))
    # rain: streaks around the foxhole and the grove (only in the rain frames), puddles
    R = Kit("rain"); rm = mat_once("grain", lambda: CK.smoke_mat("grain", "#d8e4ec", 0.5))
    for k in range(1600):
        x, z = rnd.uniform(-14, 22), rnd.uniform(-10, 18); y = rnd.uniform(0, 9)
        R.box((x, y, z), (0.012, rnd.uniform(0.5, 0.9), 0.012), rm, 0.0, 0.0, 0.08, 0.05)
    rainobj = R.build()
    pud = lib.principled("gpud", hexc("#2a2a20"), 0.03)
    puds = [mesh_obj(f"pud{k}", [(x - r, 0.04, z - r * 0.7), (x + r, 0.04, z - r * 0.7), (x + r, 0.04, z + r * 0.7), (x - r, 0.04, z + r * 0.7)], [(0, 1, 2, 3)], pud)
            for k, (x, z, r) in enumerate(((1.0, -1.0, 0.9), (7.5, 4.5, 0.7), (-3, 6, 1.2), (10, -4, 1.0)))]
    # planes overhead in the day (Wildcats chasing), a lantern in the foxhole at night
    fly = [CK.inst(CK.plane("wildcat", gear=False, spin=True), f"gfly{k}") for k in range(3)]
    lan = [lib.light("POINT", T(3.4, -0.4, 1.6), 6, (1.0, 0.6, 0.3), 0.05)]
    fill = CK.area((0, 8, 40), (0, 1, 0), 3000, (1.0, 0.85, 0.7), 20)
    def update(f):
        n, r = night(f), rain(f)
        S.world = W_night if n else (W_rain if r else W_day)
        sun.hide_render = n or r; moon.hide_render = not n; grey.hide_render = not r; fill.hide_render = n
        CK.show(rainobj + puds, r); CK.show(lan, n)
        for k, o in enumerate(boats): CK.place(o, lcvp_pos(k, f), (0, 0, -1)); o.hide_render = f > 5400
        CK.show(jboats, f >= 5740); CK.show(dds, n)
        for k, objs in flashes: CK.show(objs, 5300 <= f < 5470 and (f + k * 7) % 23 < 4)
        for f0, objs in bursts: CK.show(objs, 5300 <= f < 5470 and 0 <= f - f0 < 40)
        for k, o in enumerate(fly):
            u = (f - 5468 - k * 8) / 30.0
            o.hide_render = not (0 <= u < 4)
            CK.place(o, (-200 + 120 * u + k * 10, 45 + k * 6, 6 - k * 10), (1, 0.05, 0), -0.3)
        flag.hide_render = f < 5220
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
