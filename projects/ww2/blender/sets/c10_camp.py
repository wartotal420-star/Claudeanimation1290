# The camp (chapter 10, the Holocaust): serious, empty, still. A railway line runs through a long brick gatehouse with a
# central tower and an arch over the track; concrete fence posts bent inward carry barbed wire; watchtowers; rows of
# wooden barracks; birch trees; a siding with freight wagons, one door open; on the ramp, abandoned suitcases and bundles.
# Cold grey morning, low haze (light world volume), muted colour; nothing moves. No symbols anywhere.
# Layout (three, y up): the main track along x 0 from z -60 to z 150 (rails at x +-0.72, top y 0.17); the gatehouse spans
# x -34..34 at z 40..50 with the arch over the track (x -2.6..2.6, height 5); the tower above it (x -4..4) to y 17.
# Fences run along z 38 (outside the gatehouse) and along x +-36 inward; watchtowers at (+-36, 38) and every 40 m.
# Inside: the ramp (concrete platform) x -6.5..-1.6, z 60..120 (top y 0.9); freight wagons on the siding x 0, z 64..112;
# barracks at x +-(14..60), z 58..170. The camera stays outside the inner area except along the ramp (x -9..-6).
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text
from sets import c09_kit as K

bx, cy = K.bx, K.cy
def H(x, z): return 0.08 * noise.noise(Vector((x * 0.2, z * 0.2, 0.3))) + 0.25 * noise.noise(Vector((x * 0.03, z * 0.03, 1.1))) * K.sm(3, 10, abs(x))
def build(M, D):
    rnd = random.Random(1945)
    K.sky("#8a9098", "#c4c4c0", 0.9, "#7a828c", "#b8b8b4")
    gm = K._ground("c10ground", [(0.25, lib.hexc("#4a4a3a")), (0.45, lib.hexc("#5e5c48")), (0.6, lib.hexc("#6e6a54")), (0.8, lib.hexc("#585a4a"))], 0.9, 0.05, 4.0, 0.6, "#5a5650", 0.8)[0]
    K.heightfield("ground", H, -160, 160, -80, 200, 1.0, gm, lambda x, z: 0.9 if abs(x) < 3 or (abs(x - 0) < 3.5) else 0.0)
    # ---------- the track: ballast, sleepers, rails (main line + siding) ----------
    ball = K.mat_once("c10ballast", lambda: worn("c10ballast", "#6a6660", "#3a3834", 0.9, 0.0, 40, 0.5, "#4a4844"))
    sleeper = wood_mat("c10sleeper", "#3a3026", "#1e1812", 6, 0.9)
    rail = K.mat_once("c10rail", lambda: worn("c10rail", "#5a4a40", "#8a8a88", 0.4, 0.8, 40, 0.5, "#3a2a20"))
    from sets.kit_sbpw import Kit
    KT = Kit("track")
    for x0 in (0.0,):
        KT.box((x0, 0.06, 45), (3.4, 0.16, 210), ball, 0, 0.0)
        for k in range(300): KT.box((x0, 0.14, -60 + k * 0.7), (2.5, 0.12, 0.24), sleeper, 0.0, 0.004)
        for sd in (-1, 1):
            KT.box((x0 + sd * 0.72, 0.22, 45), (0.07, 0.06, 210), rail, 0, 0.003); KT.box((x0 + sd * 0.72, 0.18, 45), (0.14, 0.03, 210), rail, 0, 0.0)
    KT.build()
    # weeds between the sleepers outside the gate
    weed = K.mat_once("c10weed", lambda: worn("c10weed", "#6a6a3a", "#4a4a2a", 0.85, 0.0, 6, 0.5, "#5a5a34"))
    from sets.front import grass_tuft_src, scatter
    src = grass_tuft_src(weed, 7); pts = []
    while len(pts) < 700:
        x_, z_ = rnd.uniform(-40, 40), rnd.uniform(-60, 37)
        if abs(x_) < 1.9 and rnd.random() < 0.7: continue
        pts.append((x_, H(x_, z_) - 0.02, z_))
    scatter(src, "wd", pts, s=(0.8, 1.8), seed=3); src.location = T(0, -50, 0)
    # ---------- the gatehouse ----------
    brick = K.mat_once("c10brick", lambda: lib.brickmat("c10brick", "#7a4a3a", "#6a3e30", "#6a6058", 3.5))
    roof = K.mat_once("c10roof", lambda: worn("c10roof", "#3a3634", "#2a2624", 0.8, 0.1, 3, 0.6, "#2a2a28"))
    dark = K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0))
    for sd in (-1, 1):
        bx(f"gwing{sd}", (sd * 18.3, 3.0, 45), (31.4, 6.0, 9.0), brick, 0.02)
        K.loft2(f"groof{sd}", [(15.9, -4.8), (15.9, 4.8), (-15.9, 4.8), (-15.9, -4.8)], 6.0, [(15.9, -0.2), (15.9, 0.2), (-15.9, 0.2), (-15.9, -0.2)], 8.2, K.P_of(sd * 18.3, 45, 0, 0), roof)
        for k in range(12):
            x_ = sd * (5 + k * 2.4)
            bx(f"gwin{sd}{k}", (x_, 3.8, 40.45), (0.9, 0.7, 0.1), dark, 0.0)
            for j in range(2): bx(f"gwb{sd}{k}{j}", (x_, 3.8 + (j - 0.5) * 0.35, 40.4), (0.95, 0.04, 0.05), K.concrete("c10frame", "#8a8478"), 0.0)
    bx("gcenterL", (-3.6, 3.5, 45), (2.0, 7.0, 9.4), brick, 0.02); bx("gcenterR", (3.6, 3.5, 45), (2.0, 7.0, 9.4), brick, 0.02)
    bx("garchtop", (0, 6.0, 45), (5.4, 2.0, 9.4), brick, 0.02)
    for k in range(11):
        a = math.pi * k / 10; bx(f"garc{k}", (2.6 * math.cos(a), 4.2 + 1.0 * math.sin(a), 40.3), (0.5, 0.3, 0.2), brick, 0.01)
    bx("gtower", (0, 11.0, 44.5), (7.0, 8.0, 6.0), brick, 0.02)
    for sd in (-1, 1):
        for k in range(3): bx(f"gtw{sd}{k}", (-2.2 + k * 2.2, 13.2, 41.45), (1.2, 2.2, 0.1), K.mat_once("c10glass", lambda: lib.principled("c10glass", lib.hexc("#2a3038"), 0.15, 0.2)), 0.0) if sd < 0 else None
    K.loft2("gtroof", [(4.0, -3.5), (4.0, 3.5), (-4.0, 3.5), (-4.0, -3.5)], 15.0, [(0.2, -0.2), (0.2, 0.2), (-0.2, 0.2), (-0.2, -0.2)], 17.4, K.P_of(0, 44.5, 0, 0), roof)
    # ---------- fences and watchtowers ----------
    post = K.concrete("c10post", "#9a968c", "#5a5650")
    wire_m = K.mat_once("c10wire", lambda: lib.principled("c10wire", lib.hexc("#3a3a3c"), 0.5, 0.8))
    KF = Kit("fence")
    def fence_line(p0, p1, step=3.2):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); n = int(L / step); dx, dz = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
        for k in range(n + 1):
            x_, z_ = p0[0] + dx * k * step, p0[1] + dz * k * step
            KF.box((x_, 1.5, z_), (0.18, 3.0, 0.18), post, math.atan2(dx, dz), 0.01)
            KF.box((x_ - dz * 0.25, 3.15, z_ + dx * 0.25), (0.15, 0.6, 0.15), post, math.atan2(dx, dz), 0.0, pitch=0.6)
            lathe(f"ins{x_}{z_}", [(0.0, 0.0), (0.05, 0.0), (0.05, 0.1), (0.0, 0.12)], (x_, 2.6, z_), pmat("c10ins", "#e8e4dc", 0.3), 6) if k % 4 == 0 else None
        for h in (0.4, 0.9, 1.4, 1.9, 2.4, 2.8):
            tube(f"fw{p0}{h}", [(p0[0], h, p0[1]), (p1[0], h - 0.02, p1[1])], 0.008, wire_m, res=2, bres=0)
    for sd in (-1, 1):
        fence_line((sd * 34.5, 39.0), (sd * 150, 39.0))
        fence_line((sd * 36.0, 50.0), (sd * 36.0, 170.0))
    KF.build()
    for k, (x_, z_) in enumerate(((-38, 37), (38, 37), (-80, 37), (80, 37), (-122, 37), (122, 37), (-38, 90), (38, 90), (-38, 140), (38, 140))):
        tower(f"wt{k}", x_, z_, rnd)
    # ---------- barracks rows, chimneys ----------
    bw = wood_mat("c10barr", "#5a4a3a", "#3a2e24", 2.0, 0.85)
    KB = Kit("barr")
    for sd in (-1, 1):
        for r in range(4):
            for k in range(5):
                x_ = sd * (16 + r * 12); z_ = 60 + k * 22
                KB.box((x_, 1.4, z_), (8.5, 2.8, 16), bw, 0.0, 0.02)
                KB.box((x_, 3.05, z_), (9.0, 0.3, 16.6), roof, 0.0, 0.01, roll=0.0)
                KB.box((x_, 3.2, z_ + 5), (0.6, 1.4, 0.6), brick, 0.0, 0.01)
                for j in range(6): KB.box((x_ - sd * 4.27, 2.0, z_ - 6.5 + j * 2.6), (0.05, 0.6, 0.9), dark, 0.0, 0.0)
    KB.build()
    # ---------- freight wagons on the siding, the ramp with abandoned luggage ----------
    car = K.mat_once("c10car", lambda: worn("c10car", "#6a3a2a", "#3a2a22", 0.85, 0.1, 3, 0.55, "#4a2a1e"))
    for k in range(5): wagon(f"wg{k}", 0.0, 66 + k * 10.6, car, open_=(k == 1), rnd=rnd)
    conc = K.concrete("c10ramp", "#8a867c", "#5a5650")
    bx("ramp", (-4.05, 0.45, 90), (4.9, 0.9, 60), conc, 0.02)
    leather = [K.mat_once(f"c10case{k}", lambda: worn(f"c10case{k}", c, "#3a2a1e", 0.6, 0.1, 6, 0.6, "#2a1e14")) for k, c in enumerate(("#6a4a2e", "#4a3a2e", "#7a5a3a", "#3a3a3a", "#5a4030", "#8a6a4a"))]
    from sets.kit_sbpw import Kit as Kit2
    KC = Kit2("cases")
    for k in range(70):
        x_, z_ = rnd.uniform(-6.2, -2.2), rnd.uniform(64, 84) if k < 50 else rnd.uniform(88, 110)
        w, h, d = rnd.uniform(0.45, 0.75), rnd.uniform(0.12, 0.2), rnd.uniform(0.3, 0.45)
        stack = 0.9 + h / 2 + (0.18 if rnd.random() < 0.3 else 0.0)
        KC.box((x_, stack, z_), (w, h, d), leather[k % 6], rnd.uniform(0, 3), 0.02)
        KC.box((x_, stack + h / 2 + 0.02, z_), (0.12, 0.03, 0.03), pmat("c10handle", "#2a1e14", 0.5), rnd.uniform(0, 3), 0.0)
    for k in range(18):
        x_, z_ = rnd.uniform(-6.0, -2.4), rnd.uniform(64, 110)
        KC.sphere((x_, 1.05, z_), 0.25, K.mat_once(f"c10bund{k % 3}", lambda: lib.cloth(f"c10bund{k % 3}", ["#6a6458", "#5a4a4a", "#7a7060"][k % 3])), 10, (1.2, 0.7, 1.0))
    KC.build()
    for k, (x_, z_, nm) in enumerate(((-3.0, 66.2, "H. KLEIN\nBERLIN"), (-4.6, 67.0, "R. LÖWY\nPRAG"), (-3.8, 70.4, "S. COHEN\nAMSTERDAM"))):
        bx(f"case{k}", (x_, 1.1, z_), (0.7, 0.4, 0.2), leather[k], 0.03, 0.1 * k)
        text(nm, (x_, 1.12, z_ - 0.105), 0.07, pmat("c10paint", "#e8e4d8", 0.7), yaw=0.1 * k, flat=False)
    # ---------- birches, lamps, mud puddles ----------
    bark = K.mat_once("c10birch", lambda: worn("c10birch", "#e8e4dc", "#2a2a28", 0.7, 0.0, 3, 0.55, "#c8c4bc"))
    leaves = K.mat_once("c10leaf", lambda: lib.principled("c10leaf", lib.hexc("#8a7a3a"), 0.8))
    for k in range(26):
        x_, z_ = rnd.choice((-1, 1)) * rnd.uniform(8, 60), rnd.uniform(-50, 30)
        h_ = rnd.uniform(8, 13)
        tube(f"bir{k}", [(x_, 0, z_), (x_ + 0.3, h_ * 0.5, z_), (x_ + 0.1, h_, z_ + 0.2)], 0.14, bark, res=3, bres=1, taper=lambda f: 1 - 0.6 * f)
        K.blob3(f"birc{k}", (x_ + 0.1, h_ * 0.85, z_ + 0.2), (1.8, 2.6, 1.8), leaves, 0.6, k)
    for k in range(10):
        z_ = 52 + k * 12; tube(f"lp{k}", [(-8.5, 0, z_), (-8.5, 5, z_), (-7.6, 5.3, z_)], 0.06, post, res=2, bres=1)
        lathe(f"lps{k}", [(0.0, 0.0), (0.3, -0.18), (0.0, -0.08)], (-7.6, 5.3, z_), pmat("c10lamp", "#2a2a28", 0.5, 0.5), 10)
    water = lib.principled("c10pud", lib.hexc("#2a2c30"), 0.04)
    for k in range(12):
        x_, z_ = rnd.uniform(-10, 10), rnd.uniform(-40, 36)
        if abs(x_) < 2.2: continue
        lathe(f"pud{k}", [(0.0, 0.0), (rnd.uniform(0.6, 1.6), 0.0)], (x_, H(x_, z_) + 0.02, z_), water, 18, cap=False, sx=1.4, sz=0.8)
    # ---------- light: overcast morning, cold sky, a faint warm break low on the horizon behind the gate ----------
    K.sun((0.1, 0.25, 1.0), 1.4, (1.0, 0.82, 0.66), 8.0)
    K.area((0, 40, -40), (0, 0, 30), 22000, (0.7, 0.76, 0.85), 90)
    vol = bpy.data.materials.new("c10haze"); vol.use_nodes = True; nt = vol.node_tree
    for x in list(nt.nodes): nt.nodes.remove(x)
    o_ = nt.nodes.new("ShaderNodeOutputMaterial"); pv = nt.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Density"].default_value = 0.008
    pv.inputs["Color"].default_value = (0.82, 0.84, 0.86, 1); nt.links.new(pv.outputs[0], o_.inputs["Volume"])
    hz = bx("haze", (0, 12, 60), (320, 28, 300), vol, 0); hz.visible_shadow = False
    return {}
def tower(name, x, z, rnd):
    wd = wood_mat("c10tower", "#4a3c30", "#2a2018", 3, 0.85); roof = K.mat_once("c10roof", lambda: None)
    for sx in (-1, 1):
        for sz in (-1, 1): tube(f"{name}l{sx}{sz}", [(x + sx * 1.6, 0, z + sz * 1.6), (x + sx * 1.1, 6.0, z + sz * 1.1)], 0.12, wd, res=2, bres=1)
    for h in (2.0, 4.0):
        for sd in (-1, 1):
            tube(f"{name}bx{h}{sd}", [(x - 1.5, h, z + sd * 1.45), (x + 1.5, h + 0.8, z + sd * 1.45)], 0.06, wd, res=2, bres=0)
            tube(f"{name}bz{h}{sd}", [(x + sd * 1.45, h, z - 1.5), (x + sd * 1.45, h + 0.8, z + 1.5)], 0.06, wd, res=2, bres=0)
    bx(f"{name}cab", (x, 6.9, z), (2.8, 1.8, 2.8), wd, 0.02)
    for sd in (-1, 1): bx(f"{name}win{sd}", (x, 7.2, z + sd * 1.41), (2.2, 0.7, 0.05), K.mat_once("finterior", lambda: None), 0.0)
    K.loft2(f"{name}roof", [(2.0, -2.0), (2.0, 2.0), (-2.0, 2.0), (-2.0, -2.0)], 7.8, [(0.1, -0.1), (0.1, 0.1), (-0.1, 0.1), (-0.1, -0.1)], 9.2, K.P_of(x, z, 0, 0), K.mat_once("c10roof", lambda: None))
def wagon(name, x, z, m, open_=False, rnd=None):
    """covered goods wagon (10.6 m), bow along z, plank sides, sliding door (one open, black inside), four wheels"""
    steel = K.mat_once("c9steel", lambda: worn("c9steel", "#3a3c34", "#5a5a50", 0.5, 0.5, 30, 0.7))
    bx(f"{name}body", (x, 2.35, z), (2.9, 2.5, 9.6), m, 0.03)
    K.loft2(f"{name}roof", [(1.55, -4.85), (1.55, 4.85), (-1.55, 4.85), (-1.55, -4.85)], 3.6, [(0.4, -4.85), (0.4, 4.85), (-0.4, 4.85), (-0.4, -4.85)], 3.95, K.P_of(x, z, 0, 0), K.mat_once("c10roof", lambda: None))
    for k in range(9):
        for sd in (-1, 1): bx(f"{name}pl{k}{sd}", (x + sd * 1.46, 2.35, z - 4.4 + k * 1.1), (0.03, 2.45, 0.05), K.mat_once("c10car2", lambda: worn("c10car2", "#5a3226", "#2a1a14", 0.85, 0.1, 3, 0.55)), 0.0)
    for sd in (-1, 1):
        bx(f"{name}door{sd}", (x + sd * 1.49, 2.25, z + (1.6 if (open_ and sd < 0) else 0.0)), (0.06, 2.1, 1.7), m, 0.01)
        bx(f"{name}rail{sd}", (x + sd * 1.52, 3.35, z), (0.05, 0.08, 4.0), steel, 0.0)
    if open_: bx(f"{name}in", (x - 1.47, 2.25, z), (0.03, 2.0, 1.6), K.mat_once("finterior", lambda: None), 0.0)
    bx(f"{name}win", (x - 1.48, 3.1, z - 3.3), (0.04, 0.35, 0.6), K.mat_once("finterior", lambda: None), 0.0)
    bx(f"{name}frame", (x, 0.95, z), (2.6, 0.3, 10.2), steel, 0.01)
    for sz in (-1, 1):
        for sd in (-1, 1):
            o = cy(f"{name}wh{sz}{sd}", (x + sd * 0.72, 0.5, z + sz * 3.2), 0.48, 0.12, steel, 16); o.rotation_euler = (0, math.radians(90), 0)
        cy(f"{name}buf{sz}", (x + 0.8, 1.0, z + sz * 5.15), 0.15, 0.3, steel, 12, rot=(math.radians(90), 0, 0))
        cy(f"{name}buf2{sz}", (x - 0.8, 1.0, z + sz * 5.15), 0.15, 0.3, steel, 12, rot=(math.radians(90), 0, 0))
