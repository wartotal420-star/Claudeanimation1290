# Italy 1943-45 (chapter 9: Sicily landings, Mussolini's arrest at Villa Savoia, "Italy switches sides", the long climb up
# the mountains to the monastery; chapter 12: Mussolini stopped on the road by Lake Como). Hard Mediterranean sun.
# Layout (three, y up):
#   BEACH (Sicily, July 1943) round the origin: sea for z > 14 (surface y -0.25), sand rising to dunes at z < -10,
#         landing craft (LCVP) beached at (-8, 14) (0, 15) (9, 13.5) bows -z with ramps down; ships offshore z 80..300;
#         soldiers wade at z 10..16 and cross the sand z 0..10; a stone farmhouse and prickly pears at x -20..-30, z -14.
#   VILLA (Rome, 25 July 1943) at x 200: villa facade at z 12 (x 188..212) facing -z, steps down from the door (200, 1.6, 10)
#         to the gravel at z 8; umbrella pines, an ambulance at (205, 0, 4) (nose +x); the King stands at (196.5, 1.6, 10.2).
#   MOUNTAIN (Cassino) at x -300: slope rising toward +z from (-300, 0, 0) to the monastery on the summit (-300, 46, 120);
#         terraces, olive trees, stone walls, a mule track zig-zagging up; climbers on the track z 6..30.
#   the mule track: x = -300 + 3 sin(0.25 z), its ground y = max(0, 0.28 z) exactly for z -12..60 (|dx| < 2.5).
#   ROAD (Lake Como, April 1945) at x -300, z -60: a lakeside road along x with the lake at z < -70, a stopped German
#         truck at (-296, 0, -62) (nose +x), a partisan road block at (-288, 0, -62).
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, smoke_mat, smoke_column, text
from sets.front import warship, sea_mat, foam_mat, flag as wave_flag
from sets import c09_kit as K

bx, cy = K.bx, K.cy
def Hb(x, z):
    """beach: sand sloping into the sea at z 14, dunes behind"""
    h = 0.6 - 0.07 * z + 0.25 * noise.noise(Vector((x * 0.08, z * 0.08, 0.3))) * K.sm(18, 26, abs(x))
    h += 3.0 * K.sm(-8, -30, z) * (0.6 + 0.4 * noise.noise(Vector((x * 0.05, 1.0, 0.2))))
    return max(-1.2, h)
def Hm(x, z):
    """mountain at x -300: a long ridge climbing to the summit at z 120, terraces; the lake road at z -60"""
    lx = x + 300
    base = 46 * K.sm(-10, 125, z) * math.exp(-(lx / 70) ** 2 * K.sm(0, 120, z)) + 6 * noise.noise(Vector((lx * 0.03, z * 0.03, 1.1))) * K.sm(0, 40, z)
    base += 0.3 * noise.noise(Vector((lx * 0.3, z * 0.3, 2.2)))
    base += 0.6 * math.sin(z * 0.9) * K.sm(8, 20, z) * 0.3                 # terraces
    side = 18 * K.sm(40, 110, abs(lx)) * (1 + 0.3 * noise.noise(Vector((lx * 0.02, z * 0.02, 3.0))))
    road = -60.0
    if z < -40: base = 0.4 * noise.noise(Vector((lx * 0.1, z * 0.1, 0.7))) + 14 * K.sm(-55, -20, z)
    if abs(z - road) < 4: base = 0.0
    if z < -66: base = -2.0
    pd = abs(lx - 3 * math.sin(z * 0.25))
    if -12 < z < 60 and pd < 5: b = 1 - K.sm(2.5, 5, pd); return (base + side) * (1 - b) + max(0.0, 0.28 * z) * b
    return base + side
def build(M, D):
    rnd = random.Random(1943)
    K.sky("#3a7ad0", "#d8e8f0", 1.0, "#2a6ad0", "#e8f0f0")
    sea = sea_mat()
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, -0.25, 600)); o = bpy.context.object; o.scale = (3000, 1200, 1); bpy.ops.object.transform_apply(scale=True); o.data.materials.append(sea)
    foam = mat_once("ffoam", foam_mat)
    sand = K.sand_ground("c9isand", "#6a5a44")
    K.heightfield("beach", Hb, -80, 80, -60, 40, 0.8, sand, lambda x, z: 0.8 if 10 < z < 15 else 0.0)
    for k in range(8): mesh_obj(f"surf{k}", [(-80, -0.22, 13.4 + k * 0.4 + 0.3 * math.sin(k)), (80, -0.22, 13.4 + k * 0.4), (80, -0.22, 13.7 + k * 0.4), (-80, -0.22, 13.7 + k * 0.4 + 0.3 * math.sin(k))], [(0, 1, 2, 3)], foam) if k % 2 == 0 else None
    # landing craft (LCVP): plywood hull, ramp down, coxswain's station, wake foam
    ply = K.mat_once("c9ply", lambda: worn("c9ply", "#7a8288", "#4a4a44", 0.6, 0.1, 3, 0.62, "#5a6064"))
    steel = K.mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    for k, (x_, z_, yw) in enumerate(((-8, 15.5, 0.08), (0, 16.5, -0.05), (9, 15.0, 0.12), (-18, 22, 0.0), (16, 26, 0.2))):
        P = K.P_of(x_, z_, yw + math.pi / 2, -0.4)
        K.prism(f"lc{k}", [(-5.5, 0.0), (4.6, 0.0), (5.0, 1.9), (-5.3, 1.9), (-5.6, 0.8)], -1.6, 1.6, P, ply)
        bx(f"lcin{k}", P(0, 1.0, 0), (8.8, 1.8, 2.7), K.mat_once("c9lcin", lambda: lib.principled("c9lcin", lib.hexc("#3a3e40"), 0.8)), 0.0, yw + math.pi / 2)
        if k < 3:
            K.prism(f"ramp{k}", [(4.9, 0.0), (5.05, 0.0), (7.2, -0.35), (7.1, -0.45)], -1.4, 1.4, P, steel)
        else:
            K.prism(f"ramp{k}", [(4.6, 0.1), (4.8, 0.1), (5.1, 1.9), (4.9, 1.9)], -1.4, 1.4, P, steel)
            mesh_obj(f"lcw{k}", [P(-6, -0.2, -2.5), P(-6, -0.2, 2.5), P(-30, -0.2, 6), P(-30, -0.2, -6)], [(0, 1, 2, 3)], foam)
        bx(f"cox{k}", P(-4.6, 2.3, 0.9), (0.8, 0.8, 0.8), ply, 0.03, yw + math.pi / 2)
        for sd in (-1, 1): tube(f"lcmg{k}{sd}", [P(-3.8, 2.3, sd * 1.3), P(-2.6, 2.4, sd * 1.3)], 0.04, steel, res=2, bres=0)
    warship("lst", -60, 120, 0.2, 100, 15, "destroyer", 0.0)
    warship("cru", 90, 220, -0.1, 160, 18, "cruiser", 0.4)
    for k in range(5): warship(f"tr{k}", -200 + k * 110, 320 + (k % 2) * 60, rnd.uniform(-0.2, 0.2), 120, 16, "destroyer", 0.0)
    for k in range(6): smoke_column(f"bsm{k}", (rnd.uniform(-50, 50), 0.5, rnd.uniform(-40, -20)), 18, 1.5, 6, K.mat_once("c9smokeL", lambda: smoke_mat("c9smokeL", "#5a524a", 0.35)), drift=(12, -6), seed=k, puffs=8)
    # beach clutter: hedgehogs, wire, crates, jerrycans, a jeep, the farmhouse and prickly pears
    from sets.front import hedgehog
    rust = K.mat_once("frust", lambda: worn("frust", "#4a3a30", "#7a3a1a", 0.7, 0.5, 6, 0.55, "#2a1a10"))
    for k, x_ in enumerate((-22, -14, 5, 18, 26)): hedgehog(f"bh{k}", (x_, Hb(x_, 9) - 0.1, 9 + (k % 2)), k * 0.6, rust)
    for k in range(6): K.ammo_box(f"bab{k}", (3 + (k % 3) * 0.4, Hb(3, 4), 4 + (k // 3) * 0.3), 0.3 * k, "", "#5a5a3a")
    for k in range(5): K.jerrycan(f"bjc{k}", (-4 + k * 0.38, Hb(-4, 3), 3), 0.2 * k, "#5a5e3a")
    K.wire("bw1", (-30, Hb(-30, 6), 6), 16, 0.1, 0.45); K.wire("bw2", (30, Hb(30, 6), 6), 14, -0.1, 0.45)
    stone = K.mat_once("c9istone", lambda: worn("c9istone", "#d8c8a0", "#9a8a6a", 0.85, 0.0, 2, 0.58, "#b8a882"))
    roof = K.mat_once("c9tile", lambda: lib.brickmat("c9tile", "#b8603a", "#9a4a2a", "#6a3a2a", 6, 0.3, 0.15, 0.7))
    for k, (x_, z_) in enumerate(((-26, -16), (24, -20))):
        y0 = Hb(x_, z_); bx(f"farm{k}", (x_, y0 + 2.0, z_), (8, 4, 6), stone, 0.05, 0.2 * k)
        K.loft2(f"froof{k}", [(4.4, -3.4), (4.4, 3.4), (-4.4, 3.4), (-4.4, -3.4)], 4.0, [(4.4, -0.1), (4.4, 0.1), (-4.4, 0.1), (-4.4, -0.1)], 5.6, K.P_of(x_, z_, 0.2 * k, y0), roof)
        for j in range(3): bx(f"fwin{k}{j}", (x_ - 2.5 + j * 2.5, y0 + 2.4, z_ - 3.01), (0.8, 1.0, 0.05), wood_mat("c9shut", "#3a6a4a", "#2a4a34", 6, 0.6), 0.01)
    cact = K.mat_once("c9cact", lambda: lib.principled("c9cact", lib.hexc("#4a7a3a"), 0.7))
    for k in range(14):
        x_, z_ = rnd.uniform(-40, 40), rnd.uniform(-28, -6)
        y0 = Hb(x_, z_)
        for j in range(5): K.blob3(f"pp{k}{j}", (x_ + rnd.uniform(-0.4, 0.4), y0 + 0.3 + j * 0.25, z_ + rnd.uniform(-0.4, 0.4)), (0.25, 0.3, 0.06), cact, 0.02, k * 5 + j)
    flagm = K.mat_once("c9usflag", lambda: K_flag("us"))
    tube("bflagp", [(-2, Hb(-2, 2), 2), (-2, Hb(-2, 2) + 4.5, 2)], 0.04, wood_mat("ftool", "#6a4a2a", "#3a2614", 12, 0.7), res=2, bres=1)
    wave_flag("bflag", (-2, Hb(-2, 2) + 4.45, 2), 1.5, 0.9, (1, 0.2), flagm, 0.1)
    villa(rnd); mountain(rnd)
    K.sun((0.4, 0.75, -0.5), 5.5, (1.0, 0.92, 0.78), 1.0)
    K.area((0, 40, -60), (0, 0, 20), 30000, (0.6, 0.75, 1.0), 100)
    K.area((200, 10, -20), (200, 2, 10), 6000, (0.75, 0.85, 1.0), 30)
    K.area((-300, 20, -30), (-300, 8, 20), 9000, (0.75, 0.85, 1.0), 40)
    return {}

def K_flag(kind):
    from sets import ikit
    return ikit.img_mat("c9flag" + kind, ikit.flag_img(kind), 0.75, sheen=0.4)
def villa(rnd):
    X = 200.0
    gravel = K.mat_once("c9gravel", lambda: worn("c9gravel", "#c8b898", "#8a7a60", 0.9, 0.0, 30, 0.5, "#a89878"))
    bx("vground", (X, -0.05, 0), (120, 0.1, 80), gravel, 0)
    plaster = K.mat_once("c9vpl", lambda: lib.plaster("c9vpl", "#e8c890"))
    trim = K.mat_once("c9vtrim", lambda: lib.plaster("c9vtrim", "#f4ecd8"))
    roof = K.mat_once("c9tile", lambda: lib.brickmat("c9tile", "#b8603a", "#9a4a2a", "#6a3a2a", 6, 0.3, 0.15, 0.7))
    bx("vbody", (X, 5.5, 16), (24, 11, 8), plaster, 0.03)
    K.loft2("vroof", [(12.6, -4.4), (12.6, 4.4), (-12.6, 4.4), (-12.6, -4.4)], 11.0, [(10.5, -1.0), (10.5, 1.0), (-10.5, 1.0), (-10.5, -1.0)], 13.2, K.P_of(X, 16, 0, 0), roof)
    bx("vcorn", (X, 11.0, 11.9), (24.6, 0.4, 0.4), trim, 0.02); bx("vband", (X, 5.6, 11.95), (24.2, 0.25, 0.25), trim, 0.02)
    win = K.mat_once("c9vwin", lambda: lib.principled("c9vwin", lib.hexc("#1a2028"), 0.1))
    shut = wood_mat("c9shut", "#3a6a4a", "#2a4a34", 6, 0.6)
    for fl in range(2):
        for k in range(7):
            x_ = X - 9.6 + k * 3.2
            if fl == 0 and k == 3: continue
            y_ = 2.6 + fl * 5.0
            bx(f"vw{fl}{k}", (x_, y_, 11.98), (1.1, 2.0, 0.05), win, 0.0)
            for sd in (-1, 1): bx(f"vs{fl}{k}{sd}", (x_ + sd * 0.85, y_, 11.95), (0.55, 2.0, 0.06), shut, 0.01)
            bx(f"vp{fl}{k}", (x_, y_ + 1.25, 11.93), (1.5, 0.3, 0.15), trim, 0.01)
    # portico: four columns, pediment, the door, the steps
    for k in range(4): cy(f"vcol{k}", (X - 3 + k * 2, 2.8, 10.6), 0.3, 4.4, trim, 20)
    bx("vent", (X, 5.2, 10.6), (7.6, 0.6, 1.4), trim, 0.03)
    K.prism("vped", [(-4.0, 5.5), (4.0, 5.5), (0.0, 7.0)], 9.9, 11.2, lambda a, b, c: (X + a, b, c), trim)
    bx("vdoor", (X, 2.4, 11.96), (1.8, 3.2, 0.06), wood_mat("c9vdoor", "#4a2a14", "#2a140a", 6, 0.4), 0.01)
    for k in range(5): bx(f"vstep{k}", (X, 0.16 + k * 0.32, 8.6 + k * 0.38), (8.0 - k * 0.2, 0.32, 0.38 * (5 - k) + 0.6), trim, 0.01)
    bx("vplat", (X, 1.55, 10.4), (7.6, 0.1, 2.2), trim, 0.01)
    for sd in (-1, 1):
        lathe(f"vurn{sd}", [(0.0, 0.0), (0.3, 0.0), (0.22, 0.3), (0.45, 0.7), (0.4, 0.95), (0.0, 0.95)], (X + sd * 4.3, 0, 8.4), trim, 20)
        for j in range(6): K.blob3(f"vbush{sd}{j}", (X + sd * (6 + j * 1.6), 0.6, 11.0), (0.8, 0.7, 0.6), K.mat_once("c9hedge", lambda: lib.principled("c9hedge", lib.hexc("#2a5a26"), 0.8)), 0.15, j)
    # umbrella pines
    bark = wood_mat("c9pbark", "#6a4a32", "#3a2618", 3, 0.9); crown = K.mat_once("c9pcrown", lambda: lib.principled("c9pcrown", lib.hexc("#2e5228"), 0.8))
    for k, (x_, z_) in enumerate(((-16, 6), (17, 3), (-24, 18), (26, 20), (-30, -10), (32, -8))):
        h_ = rnd.uniform(9, 13)
        tube(f"pine{k}", [(X + x_, 0, z_), (X + x_ + 0.6, h_ * 0.6, z_), (X + x_ + 1.2, h_, z_ + 0.3)], 0.35, bark, res=4, bres=1, taper=lambda f: 1 - 0.5 * f)
        K.blob3(f"pinec{k}", (X + x_ + 1.2, h_ + 0.6, z_ + 0.3), (4.5, 1.4, 4.0), crown, 0.6, k)
    # the ambulance (Mussolini was driven away in one)
    am = K.mat_once("c9amb", lambda: worn("c9amb", "#d8d4c8", "#6a6a60", 0.5, 0.2, 6, 0.66, "#a8a498"))
    P = K.P_of(X + 5, 4, 0.0, 0.0)
    bx("ambody", P(-0.6, 1.6, 0), (3.8, 2.2, 2.0), am, 0.12, 0.0)
    K.prism("ambon", [(1.3, 0.6), (2.6, 0.6), (2.6, 1.3), (1.3, 1.5)], -0.8, 0.8, P, am)
    for sd in (-1, 1):
        for lx in (-1.6, 1.9): K.wheel(f"amw{lx}{sd}", P, lx, 0.42, sd * 0.95, 0.42, 0.24, pmat("ftyre", "#141414", 0.8), 0.0, 18)
        bx(f"amcross{sd}", P(-1.0, 1.9, sd * 1.01), (0.7, 0.7, 0.01), pmat("c9white", "#f2f0e8", 0.6), 0.0, 0.0)
        for j in range(2): bx(f"amx{sd}{j}", P(-1.0, 1.9, sd * 1.02), (0.6 if j else 0.18, 0.18 if j else 0.6, 0.01), pmat("c9redx", "#c81e1e", 0.6), 0.0, 0.0)
    bx("amws", P(1.25, 2.0, 0), (0.04, 0.6, 1.7), win, 0.0, 0.0)
    for k in range(4): lathe(f"vlamp{k}", [(0.0, 0.0), (0.08, 0.0), (0.05, 2.8), (0.2, 3.0), (0.15, 3.4), (0.0, 3.5)], (X - 12 + k * 8, 0, 6.5), pmat("c9iron", "#2a2a28", 0.6, 0.5), 12)
def mountain(rnd):
    X = -300.0
    rock = K.mat_once("c9mrock", lambda: worn("c9mrock", "#a89a80", "#6a6050", 0.9, 0.0, 0.6, 0.52, "#8a7a62"))
    gm = K._ground("c9mgrass", [(0.25, lib.hexc("#6a6a3a")), (0.5, lib.hexc("#8a845a")), (0.7, lib.hexc("#a89a70")), (0.85, lib.hexc("#b8ab8a"))], 0.9, 0.05, 4.0, 0.8, "#c8b898", 0.8)[0]
    K.heightfield("mtn", lambda x, z: Hm(x, z), X - 160, X + 160, -110, 200, 1.2, gm, lambda x, z: 1.0 if abs(z + 60) < 3.5 else (0.6 if abs(x - X - 3 * math.sin(z * 0.25)) < 1.2 and 0 < z < 100 else 0.0))
    lake = lib.principled("c9lake", lib.hexc("#2a5a6a"), 0.05)
    bx("lake", (X, -1.0, -150), (600, 0.1, 160), lake, 0)
    olive = K.mat_once("c9olive", lambda: lib.principled("c9olive", lib.hexc("#6a7a4a"), 0.8)); obark = wood_mat("c9obark", "#5a4a3a", "#3a2a1e", 4, 0.9)
    for k in range(70):
        x_, z_ = X + rnd.uniform(-70, 70), rnd.uniform(4, 90)
        if abs(x_ - X - 3 * math.sin(z_ * 0.25)) < 3: continue
        y0 = Hm(x_, z_)
        tube(f"olt{k}", [(x_, y0, z_), (x_ + 0.3, y0 + 1.2, z_), (x_ - 0.2, y0 + 2.0, z_ + 0.2)], 0.14, obark, res=4, bres=1)
        K.blob3(f"olc{k}", (x_, y0 + 2.6, z_), (1.6, 1.0, 1.5), olive, 0.35, k)
    for k in range(40):
        x_, z_ = X + rnd.uniform(-60, 60), rnd.uniform(2, 100)
        K.blob3(f"mr{k}", (x_, Hm(x_, z_), z_), (rnd.uniform(0.6, 2.2), rnd.uniform(0.4, 1.4), rnd.uniform(0.6, 2.0)), rock, 0.3, k + 500)
    from sets.front import boxes
    walls = []
    for t in range(6):
        z0 = 8 + t * 12
        for k in range(30):
            x_ = X - 30 + k * 2.0; z_ = z0 + 2 * math.sin(k * 0.4 + t)
            walls.append(((x_, Hm(x_, z_) + 0.35, z_), (2.0, 0.7, 0.5), 0.2 * math.sin(k + t), rnd.uniform(-0.05, 0.05)))
    boxes("swalls", walls, rock, 0.08)
    # the monastery on the summit: long white walls, rows of small windows, a dome and bell tower (shell-scarred)
    mon = K.mat_once("c9mon", lambda: worn("c9mon", "#e8e0cc", "#8a8070", 0.85, 0.0, 1.0, 0.58, "#c8bca8"))
    sy = Hm(X, 120)
    bx("monA", (X, sy + 8, 120), (60, 16, 26), mon, 0.1); bx("monB", (X + 10, sy + 12, 132), (30, 24, 14), mon, 0.1)
    lathe("dome", [(0.0, 0.0), (5.0, 0.0), (5.0, 2.5), (4.0, 5.0), (2.0, 6.5), (0.0, 7.0)], (X - 4, sy + 16, 122), K.mat_once("c9dome", lambda: worn("c9dome", "#8a9a9a", "#4a5050", 0.6, 0.2, 2, 0.6)), 24)
    bx("tower", (X + 14, sy + 22, 118), (5, 16, 5), mon, 0.05)
    dark = K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0))
    for r in range(3):
        for k in range(18): bx(f"mw{r}{k}", (X - 27 + k * 3.2, sy + 4 + r * 4, 106.95), (0.8, 1.4, 0.1), dark, 0.0)
    for k in range(3): smoke_column(f"msm{k}", (X - 15 + k * 14, sy + 14, 112), 22, 3, 8, K.mat_once("c9smokeL", lambda: smoke_mat("c9smokeL", "#5a524a", 0.35)), drift=(10, -4), seed=k + 60, puffs=9)
    # the lake road (1945): a German truck stopped at a partisan road block, stone parapet, poplars
    K.truck("ctruck", X + 4, -62, 0.0, "#5e6658", "#6a6a5a")
    bx("rblock", (X + 13, 0.5, -62), (0.3, 0.12, 6.5), wood_mat("c9pole", "#c8c0b0", "#8a8070", 6, 0.6), 0.01)
    for sd in (-1, 1): tube(f"rbp{sd}", [(X + 13, 0, -62 + sd * 3.2), (X + 13, 1.1, -62 + sd * 3.2)], 0.06, wood_mat("fpole", "#4a3a2a", "#2a1e14", 4, 0.9), res=2, bres=1)
    for k in range(4): bx(f"rbs{k}", (X + 13, 0.06 + 0.12, -62 - 2.7 + k * 1.8), (0.28, 0.24, 1.2), pmat(f"c9stripe{k % 2}", ["#c81e1e", "#f2ece0"][k % 2], 0.6), 0.0)
    for k in range(20): bx(f"parap{k}", (X - 40 + k * 4, 0.45, -65.2), (3.9, 0.9, 0.5), rock, 0.05)
    for k in range(10):
        x_ = X - 40 + k * 9; tube(f"popl{k}", [(x_, 0, -57), (x_, 3, -57)], 0.18, obark, res=2, bres=1)
        lathe(f"poplc{k}", [(0.0, 2.0), (1.4, 4.0), (1.3, 8.0), (0.6, 11.0), (0.0, 12.5)], (x_, 0, -57), K.mat_once("c9popl", lambda: lib.principled("c9popl", lib.hexc("#4a6a2e"), 0.8)), 12)
    for k in range(5): lathe(f"farhill{k}", [(0.0, 0.0), (60, 0.0), (30, 26 + k * 4), (0.0, 34 + k * 4)], (X - 200 + k * 100, -2, -300 - (k % 2) * 40), K.mat_once("c9farhill", lambda: lib.principled("c9farhill", lib.hexc("#6a7a8a"), 0.9)), 16)
