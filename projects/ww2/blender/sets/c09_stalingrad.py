# Stalingrad, winter 1942-43 (chapter 9). Snow, gutted blocks, factory chimneys, the grain elevator, the Volga beyond.
# Low pink winter sun from the south-west (behind-left of most cameras), blue snow shadows, fires in the ruins.
# Ground is flat (|y| < 0.04) on the street |x| < 7 (z -14..66), in the pocket |x| < 14 (z -46..-26) and on the road |x| < 6 (z < -62).
# Layout (three, y up; the street runs along +z):
#   street: road x -7..7, z -10..44 (snow, rubble, craters), ruined blocks both sides (facades at x = +-9, facing the road),
#           the Univermag store (Paulus' HQ) on the right at x 9, z 24..36 with its sign and the cellar steps at (8.0, 0, 30.5).
#   station square: z 46..64, fountain (children's ring dance round a crocodile) at (0, 0, 54); station facade at z 66
#           (x -16..16, facing -z), "STALINGRAD" letters over the entrance at y ~9.
#   skyline / establishing: factory district x 30..90, z 60..140 (chimneys, halls), grain elevator at (-40, 0, 95),
#           the Volga from z 150 (frozen edges, ice floes), the far bank z 400.
#   the pocket (trapped Sixth Army): open snow at z -20..-60, |x| < 30, a wrecked tank (-6, -32), a fire at (2, 0, -36),
#           ruins behind (+z); supply-drop zone round (0, 0, -45).
#   POW column: the open steppe south x -60..60, z -70..-220 (flat), road along x = 0.
#   interiors (sun leaks through holes): ROOM at x 200 (floor y 0, x 196..204, z -4..4, back wall z 4, bathtub (200, 0, 1.5));
#           STAIRS at x 240 (stair flight from (240, 0, -2) up +z to (240, 3.3, 4.6), landing; top floor y 3.3).
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, smoke_mat, smoke_column, text
from sets import c09_kit as K

bx, cy = K.bx, K.cy
CRATERS = [(-3, 12, 2.2), (4, 30, 1.8), (-2, 38, 1.5), (5, 5, 1.4), (-12, -40, 2.5), (14, -28, 2.0), (-22, -48, 3.0), (20, -55, 2.2), (6, 58, 1.2)]
def H(x, z):
    if x > 150: return 0.0
    flat = max(1 - K.sm(7, 11, abs(x)) if -14 < z < 66 else 0.0, (1 - K.sm(14, 20, abs(x))) * (1 - K.sm(-26, -22, z)) * K.sm(-50, -46, z), (1 - K.sm(6, 10, abs(x))) * (1 - K.sm(-62, -58, z)))
    h = (0.12 * noise.noise(Vector((x * 0.2, z * 0.2, 0.3))) + 0.35 * noise.noise(Vector((x * 0.05, z * 0.05, 1.3)))) * (1 - 0.92 * flat)
    for cx, cz, r in CRATERS:
        d = math.hypot(x - cx, z - cz)
        if d < r * 1.8: h += -0.5 * r * 0.3 * max(0.0, 1 - (d / r) ** 2) + 0.15 * math.exp(-((d - r) / (0.3 * r)) ** 2)
    h -= 3.0 * K.sm(140, 152, z)          # the bank drops to the river ice
    return h
def build(M, D):
    rnd = random.Random(1943)
    K.sky("#4a5878", "#e8a890", 0.8, "#3a4a72", "#f0b4a0")
    snow = K.snow_ground("c9snow", "#5a4a40")
    def dirt(x, z):
        v = 0.0
        if abs(x) < 6 and -10 < z < 64: v = 0.35 + 0.3 * noise.noise(Vector((x * 0.3, z * 0.3, 4)))
        if abs(x) < 3 and z < -60: v = 0.55
        for cx, cz, r in CRATERS:
            if math.hypot(x - cx, z - cz) < r * 1.3: v = max(v, 0.85)
        return max(0.0, min(1.0, v))
    K.heightfield("ground", H, -110, 140, -230, 160, 0.9, snow, dirt)
    ice = lib.principled("c9ice", lib.hexc("#9aaabb"), 0.15); bx("volga", (0, -2.9, 300), (900, 0.1, 300), ice, 0)
    water = lib.principled("c9water", lib.hexc("#1e2a34"), 0.05)
    for k in range(40):
        x_, z_ = rnd.uniform(-200, 250), rnd.uniform(160, 380)
        K.blob3(f"floe{k}", (x_, -2.85, z_), (rnd.uniform(3, 9), 0.15, rnd.uniform(2, 6)), K.mat_once("c9floe", lambda: lib.principled("c9floe", lib.hexc("#e4ecf4"), 0.4)), 0.3, k)
    bx("lead", (40, -2.84, 230), (500, 0.05, 18), water, 0)
    bx("farbank", (0, -1.0, 420), (1200, 4, 40), snow, 0)
    for k in range(30): lathe(f"fartree{k}", [(0.0, 0.0), (2.5, 2.0), (0.0, 7.0)], (-300 + k * 22 + rnd.uniform(-5, 5), 0.5, 430 + rnd.uniform(0, 20)), K.mat_once("c9fartree", lambda: lib.principled("c9fartree", lib.hexc("#3a3a48"), 0.9)), 8)
    PL = ["#b8a690", "#a8806a", "#8a8c90", "#c0a080", "#9a8a7a", "#a86a50", "#b8a888", "#7a8478"]
    RM = [K.ruin_mat_snow(f"c9ruin{k}", c) for k, c in enumerate(PL)]
    # ---------- the street: blocks on both sides, facades facing the road ----------
    signs = {1: ("АПТЕКА", "#2a3a2a", "#e8dcb8"), 4: ("ХЛЕБ", "#4a1a1a", "#efe2b8"), 7: ("ГАСТРОНОМ", "#1a2a4a", "#efe2b8")}
    zz = -12.0; k = 0
    while zz < 44:
        w = rnd.uniform(7, 10)
        if not (22 < zz + w / 2 < 38): K.ruin(f"rr{k}", 9.2, zz + w / 2, w, rnd.randint(3, 5), RM[k % 8], 50 + k, yaw=math.pi / 2, sign=signs.get(k))
        zz += w + rnd.uniform(0.5, 2.0); k += 1
    zz = -12.0; k = 0
    while zz < 44:
        w = rnd.uniform(7, 10)
        K.ruin(f"rl{k}", -9.2, zz + w / 2, w, rnd.randint(3, 5), RM[(k + 3) % 8], 90 + k, yaw=-math.pi / 2, sign=signs.get(k + 2))
        zz += w + rnd.uniform(0.5, 2.0); k += 1
    # the Univermag department store (right side): bigger, a long sign, cellar steps down to a door
    K.ruin("univer", 9.4, 30, 14, 4, RM[2], 777, yaw=math.pi / 2, glow_p=0.05)
    bx("usign", (8.95, 4.6, 30), (0.12, 0.9, 9.0), pmat("c9usign", "#2a2a2a", 0.6), 0.02)
    text("УНИВЕРМАГ", (8.86, 4.35, 30), 0.62, pmat("c9usignt", "#e8d8a8", 0.5), yaw=math.pi / 2, flat=False)
    for k in range(6): bx(f"ustep{k}", (8.2 + k * 0.32, -0.12 - k * 0.2, 30.5), (0.34, 0.2, 2.0), K.concrete(), 0.01)
    bx("udoor", (10.1, -0.5, 30.5), (0.08, 1.9, 1.3), wood_mat("c9door", "#4a3420", "#2a1a0c", 6, 0.7), 0.01)
    bx("udoorframe", (10.12, 0.55, 30.5), (0.12, 0.2, 1.6), K.concrete(), 0.01)
    for sz in (-1, 1): bx(f"uwall{sz}", (9.0, -0.4, 30.5 + sz * 1.1), (2.2, 1.0, 0.2), K.concrete(), 0.01)
    lib.light("POINT", T(9.9, 0.6, 30.5), 25, (1.0, 0.6, 0.3), 0.1).visible_camera = False
    # street furniture: craters, rubble heaps, bricks, burnt tram, lamp posts, a dead truck, barricades, signs, wires
    brick = K.mat_once("c9brick", lambda: K.add_snow(lib.brickmat("c9brick", "#8a4a36", "#6a3424", "#5a4a40", 30), 0.6))
    rub = K.mat_once("c9rubble", lambda: K.add_snow(__import__("sets.front", fromlist=["ruin_mat"]).ruin_mat("c9rubble", "#7a6a5a", "#7a3e2c"), 0.7))
    for k in range(26):
        sd = -1 if k % 2 else 1; z_ = -10 + k * 2.1 + rnd.uniform(-1, 1)
        K.rubble(f"rb{k}", (sd * rnd.uniform(5.5, 8.5), H(sd * 7, z_), z_), (rnd.uniform(1.5, 3.0), rnd.uniform(0.6, 1.4), rnd.uniform(1.5, 2.6)), rub, k, 4)
    K.bricks("bricks", (0, 0, 18), 18, 500, brick, 3, H)
    K.bricks("bricks2", (0, 0, -30), 18, 260, brick, 4, H)
    tram = K.mat_once("c9tram", lambda: K.add_snow(worn("c9tram", "#8a2a22", "#2a1a14", 0.6, 0.4, 5, 0.55, "#1a1210"), 0.5))
    bx("tram", (-3.6, 1.6, 40), (2.4, 2.2, 9.0), tram, 0.15, 0.25)
    for k in range(5): bx(f"tramwin{k}", (-3.6 + 1.22 * math.sin(0.25) * 0 - 1.2, 2.1, 37.2 + k * 1.5), (0.05, 0.8, 1.0), K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0)), 0.0, 0.25)
    for k, (x_, z_, lean) in enumerate(((-6.2, 4, 0.0), (6.3, 16, 0.25), (-6.4, 28, -0.4), (6.2, 42, 0.1))):
        top = (x_ + math.sin(lean) * 5, 5 * math.cos(lean), z_)
        tube(f"lp{k}", [(x_, 0, z_), ((x_ + top[0]) / 2, 2.6, z_), top, (top[0] + (0.8 if x_ < 0 else -0.8), top[1] + 0.2, z_)], 0.08, pmat("c9iron", "#2a2a28", 0.6, 0.5), res=4, bres=1)
    for k in range(6):
        z_ = -8 + k * 9; tube(f"tw{k}", [(-6.2, 6, z_), (0, 5.2, z_ + 4.5), (6.2, 6, z_ + 9)], 0.015, pmat("fwire", "#1a1a1a", 0.5, 0.8), res=8, bres=0)
    K.truck("dtruck", 4.0, 9.0, 2.2, "#4a4a3e", "#5a5a48"); fire("dtf", (4.2, 1.6, 9.0), 0.7, seed=4, energy=500)
    for k, (x_, z_, yw) in enumerate(((-2.0, 22, 0.2), (2.5, 34, -0.3))):
        for j in range(3): K.wire(f"bw{k}{j}", (x_, 0, z_ + j * 0.01), 4.0, yw, 0.45)
    from sets.front import hedgehog
    steel = K.mat_once("frust", lambda: worn("frust", "#4a3a30", "#7a3a1a", 0.7, 0.5, 6, 0.55, "#2a1a10"))
    for k, (x_, z_) in enumerate(((-5, 14), (5.5, 21), (-4.5, 45), (4.8, 47))): hedgehog(f"hh{k}", (x_, H(x_, z_) - 0.1, z_), k * 0.7, steel)
    K.bathtub("tubst", (-4.4, H(-4.4, 25), 25), 0.4)
    for k in range(4): K.sandbags(f"sbs{k}", (-5.5 + (k % 2) * 11, H(0, 6 + k * 10), 6 + k * 10), (1 if k % 2 else -1) * 0.3, 5, 2, k)
    # ---------- station square: the fountain, the station facade with its name ----------
    sto = K.mat_once("c9stone", lambda: K.add_snow(worn("c9stone", "#c8bca8", "#7a7064", 0.8, 0.0, 2, 0.55, "#8a8070"), 0.6))
    lathe("basin", [(0.0, 0.0), (4.2, 0.0), (4.2, 0.55), (3.9, 0.55), (3.9, 0.15), (0.0, 0.15)], (0, H(0, 54), 54), sto, 48)
    lathe("bice", [(0.0, 0.3), (3.9, 0.3), (0.0, 0.3)], (0, H(0, 54), 54), K.mat_once("c9floe", lambda: lib.principled("c9floe", lib.hexc("#e4ecf4"), 0.4)), 40)
    stat = K.mat_once("c9statue", lambda: K.add_snow(worn("c9statue", "#d8d0c0", "#8a8478", 0.5, 0.1, 3, 0.6, "#a8a090"), 0.35))
    y0 = H(0, 54) + 0.3
    lathe("croc", [(0.0, 0.0), (0.35, 0.05), (0.45, 0.3), (0.3, 0.6), (0.0, 0.65)], (0, y0, 54), stat, 16, sx=2.6, sz=0.8)
    for k in range(6):   # six children dancing in a ring, holding hands (the famous Barmaley fountain)
        a = k / 6 * math.tau; px, pz = 1.6 * math.cos(a), 54 + 1.6 * math.sin(a)
        lathe(f"kid{k}", [(0.0, 0.0), (0.08, 0.0), (0.09, 0.45), (0.2, 0.5), (0.24, 0.8), (0.16, 1.05), (0.08, 1.12), (0.0, 1.12)], (px, y0, pz), stat, 14)
        K.blob3(f"kidh{k}", (px, y0 + 1.25, pz), (0.14, 0.15, 0.14), stat, 0.01, k)
        b = (k + 1) / 6 * math.tau; qx, qz = 1.6 * math.cos(b), 54 + 1.6 * math.sin(b)
        tube(f"arm{k}", [(px, y0 + 0.95, pz), ((px + qx) / 2 * 1.08, y0 + 0.85, 54 + (pz + qz - 108) / 2 * 1.08), (qx, y0 + 0.95, qz)], 0.04, stat, res=4, bres=1)
    # station: a long neoclassical front with columns, a central tower stump, everything blasted and black inside
    stm = K.ruin_mat_snow("c9station", "#d8c8a0", "#9a5a3a", 0.5)
    K.ruin("stL", -11, 68, 12, 2, stm, 901, yaw=0.0, glow_p=0.15, fh=4.0)
    K.ruin("stR", 11, 68, 12, 2, stm, 902, yaw=0.0, glow_p=0.15, fh=4.0)
    bx("stC", (0, 4.5, 67.5), (10, 9, 1.0), stm, 0.05)
    bx("stCdoor", (0, 2.4, 66.95), (3.2, 4.8, 0.2), K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0)), 0)
    for k in range(6): cy(f"col{k}", (-4.2 + k * 1.68, 3.4, 66.6), 0.32, 6.8, stm, 20)
    bx("pedim", (0, 7.2, 66.5), (10.6, 0.7, 0.6), stm, 0.04)
    bx("nameb", (0, 8.25, 66.6), (9.4, 1.2, 0.2), pmat("c9nameb", "#2a2a2e", 0.6), 0.02)
    text("СТАЛИНГРАД", (0, 8.25, 66.48), 0.95, pmat("c9namet", "#f0e0b0", 0.4, 0.3), flat=False)
    bx("tower", (0, 11, 68.5), (5, 5, 3), stm, 0.05)
    bx("tclk", (0, 11.5, 66.95), (1.6, 1.6, 0.05), pmat("c9clock", "#e8dcc0", 0.6), 0)
    cy("clockf", (0, 11.5, 66.9), 0.7, 0.05, pmat("c9clockf", "#d8c8a0", 0.6), 24, rot=(math.radians(90), 0, 0))
    for a_, ln in ((math.radians(30), 0.45), (math.radians(-100), 0.6)):
        o = bx(f"chand{ln}", (0.0 + ln / 2 * math.sin(a_), 11.5 + ln / 2 * math.cos(a_), 66.86), (0.06, ln, 0.02), pmat("kink2", "#1a1a1a", 0.6), 0); o.rotation_euler[1] = a_
    for k in range(3): fire(f"stf{k}", (-12 + k * 12, 1.2, 69), 1.4, seed=20 + k, energy=2500)
    sm_ = K.mat_once("c9smoke", lambda: smoke_mat("c9smoke", "#2a2422", 0.42))
    for k in range(3): smoke_column(f"sts{k}", (-12 + k * 12, 6, 70), 26, 1.5, 6, sm_, drift=(-14, 10), seed=k + 40, puffs=12)
    # ---------- skyline: factory halls with saw-tooth roofs, chimneys, the grain elevator ----------
    fac = K.ruin_mat_snow("c9fac", "#8a5a46", "#8a4632", 0.5)
    for k in range(6):
        x_, z_ = 32 + (k % 3) * 20, 70 + (k // 3) * 26
        K.ruin(f"hall{k}", x_, z_, 18, 3, fac, 300 + k, yaw=0.0, depth=14, glow_p=0.25, fh=4.0)
    for k, (x_, z_, h_) in enumerate(((40, 98, 34), (52, 102, 30), (64, 96, 38), (76, 110, 28), (88, 92, 32), (30, 120, 26))):
        lathe(f"chim{k}", [(0.0, 0.0), (1.4, 0.0), (1.0, h_ * 0.9), (1.05, h_ * 0.92), (1.05, h_ * (0.75 + 0.25 * (k % 2))), (0.0, h_ * (0.75 + 0.25 * (k % 2)))], (x_, 0, z_), fac, 16)
    elev = K.ruin_mat_snow("c9elev", "#b8b0a0", "#6a6460", 0.4)
    bx("elevT", (-40, 20, 98), (12, 40, 9), elev, 0.1)
    for k in range(5): cy(f"silo{k}", (-46 + k * 3, 12, 92), 1.5, 24, elev, 20)
    bx("elevgap", (-38, 26, 93.4), (4, 10, 0.3), K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0)), 0)
    xs = -100.0
    while xs < 120:   # far rows of shells against the river light
        w = rnd.uniform(8, 14)
        if not (-50 < xs < -30): K.ruin(f"far{int(xs)}", xs, 128 + rnd.uniform(-6, 6), w, rnd.randint(3, 6), RM[int(abs(xs)) % 8], 500 + int(xs), yaw=0.0, glow_p=0.15)
        xs += w + rnd.uniform(1, 5)
    for k in range(8):
        x_, z_ = rnd.uniform(-90, 100), rnd.uniform(75, 130)
        fire(f"ff{k}", (x_, 1.0, z_), 2.0, seed=k + 60, energy=5000)
        smoke_column(f"fs{k}", (x_, 8, z_), 40, 2.5, 9, sm_, drift=(-30, 14), seed=k + 70, puffs=12)
    # ---------- the pocket: trapped soldiers' camp at the city edge ----------
    K.panzer("pkwreck", -6, -32, 0.6, "#5e6658", burnt=False, y0=H(-6, -32) - 0.15, tilt=0.08)
    K.blob3("pksnowcap", (-6.3, 2.4, -32), (2.2, 0.25, 1.6), snow, 0.1, 3)
    fire("pkfire", (2, H(2, -36), -36), 0.45, seed=13, energy=380)
    for k in range(8):
        a = k / 8 * math.tau; K.blob3(f"pkstone{k}", (2 + 0.55 * math.cos(a), H(2, -36), -36 + 0.55 * math.sin(a)), (0.16, 0.1, 0.14), sto, 0.03, k)
    for k in range(7): tube(f"pklog{k}", [(2 + 0.3 * math.cos(k), H(2, -36) + 0.05, -36 + 0.3 * math.sin(k)), (2 - 0.2 * math.cos(k), H(2, -36) + 0.25, -36 - 0.2 * math.sin(k))], 0.04, wood_mat("fbeam", "#2a1c14", "#100a08", 6, 0.9), res=2, bres=1)
    for k in range(4): K.blanket_roll(f"pkbl{k}", (-1 + k * 1.2, H(0, -38) + 0.1, -38.5 + (k % 2) * 0.6), 0.3 * k, ["#5a5a50", "#6a5a46", "#4a4e46"][k % 3])
    for k in range(6): K.helmet_ground(f"pkh{k}", (rnd.uniform(-8, 8), H(0, -40), rnd.uniform(-44, -34)), rnd.uniform(0, 6))
    for k in range(4): K.jerrycan(f"pkjc{k}", (4.5 + k * 0.36, H(4.5, -35), -35.5), 0.3 * k, "#5e6658")
    for k in range(3): K.sandbags(f"pksb{k}", (-12 + k * 9, H(-12 + k * 9, -28), -28), 0.1 * k, 6, 2, k + 30, K.mat_once("c9sbag", lambda: K.add_snow(__import__("sets.front", fromlist=["sandmat"]).sandmat(), 0.6)))
    for k in range(5):
        x_, z_ = -20 + k * 10, rnd.uniform(-58, -46)
        from sets.front import dead_tree
        dead_tree(f"pktree{k}", (x_, H(x_, z_), z_), rnd.uniform(5, 8), K.mat_once("c9bark", lambda: K.add_snow(worn("c9bark", "#2a221c", "#4a3a2a", 0.9, 0.0, 3, 0.6, "#1a1410"), 0.3)), k + 5)
    tube("supchute", [(9.0, H(9, -42) + 0.05, -42), (9.6, H(9, -42) + 0.2, -42.6), (10.4, H(9, -42) + 0.1, -43.2)], 0.25, K.mat_once("c9chute", lambda: lib.cloth("c9chute", "#e8e4d8")), taper=lambda f: 0.4 + f)
    # ---------- the steppe south: the long road the prisoners walk ----------
    for k in range(20):
        z_ = -70 - k * 8; tube(f"rpole{k}", [(4.0, H(4, z_), z_), (4.05, H(4, z_) + 1.6, z_)], 0.05, wood_mat("fpole", "#4a3a2a", "#2a1e14", 4, 0.9), res=2, bres=1)
    for k in range(12):
        x_, z_ = rnd.uniform(-60, 60), rnd.uniform(-200, -80)
        if abs(x_) < 8: continue
        from sets.front import dead_tree
        dead_tree(f"stree{k}", (x_, H(x_, z_), z_), rnd.uniform(4, 7), K.mat_once("c9bark", lambda: K.add_snow(worn("c9bark", "#2a221c", "#4a3a2a", 0.9, 0.0, 3, 0.6, "#1a1410"), 0.3)), k + 50)
    K.truck("swreck", -14, -110, 1.0, "#5e6658", "#6a6a5a")
    K.t34("st34", 12, -95, 2.2, y0=H(12, -95))
    # ---------- interiors ----------
    room(rnd); stairs(rnd)
    # ---------- light: low pink sun from the south-west, cold sky fill, warm bounce ----------
    K.sun((-0.45, 0.22, -0.85), 3.2, (1.0, 0.66, 0.5), 2.0)
    K.area((0, 30, -40), (0, 0, 20), 9000, (0.55, 0.65, 1.0), 60)
    K.area((0, 6, -14), (0, 1.5, 10), 1200, (1.0, 0.72, 0.55), 14)
    K.area((0, 5, 40), (0, 1.5, 55), 1200, (1.0, 0.6, 0.4), 12)
    return {}

def room(rnd):
    """a gutted flat at x 196..204, z -4..4 (camera side z -4 open), y 0..3.2: peeling wallpaper, a shell hole, the bathtub,
    a piano, broken chairs, a picture askew, snow blown in; light: sun through the hole + a cold window"""
    X = 200.0
    wp = K.mat_once("c9wp", lambda: K.add_snow(lib.wallpaper("c9wp", "#8a9a7a", "#6a7a5a"), 0.2))
    fl = lib.parquet("c9rfloor", "#6a4a32", "#4a3020")
    bx("rfloor", (X, -0.05, 0), (9, 0.1, 9), fl, 0)
    for sd in (-1, 1): bx(f"rside{sd}", (X + sd * 4.1, 1.6, 0), (0.25, 3.2, 8.4), wp, 0)
    # back wall with a blasted hole (sun comes through) and a window
    for (x0, x1, y0, y1) in ((-4.2, -1.2, 0, 3.2), (1.8, 4.2, 0, 3.2), (-1.2, 1.8, 0, 0.6), (-1.2, 1.8, 2.7, 3.2)):
        bx(f"rb{x0}{y0}", (X + (x0 + x1) / 2, (y0 + y1) / 2, 4.1), (x1 - x0, y1 - y0, 0.3), wp, 0)
    K.rubble("rhole", (X + 0.3, 0, 3.4), (2.4, 0.7, 1.4), K.mat_once("c9rubble2", lambda: K.add_snow(__import__("sets.front", fromlist=["ruin_mat"]).ruin_mat("c9rubble2", "#8a7a6a", "#8a4632"), 0.5)), 5, 5)
    bx("rceil", (X + 1.5, 3.25, -0.5), (6, 0.15, 7), K.concrete("c9ceil", "#9a948a"), 0)
    for k in range(5): bx(f"rlath{k}", (X - 2.5 + k * 0.25, 3.0, 1.5 + k * 0.3), (0.05, 0.05, 2.0), wood_mat("fbeam", "#2a1c14", "#100a08", 6, 0.9), 0.0, 0.3 * k)
    K.bathtub("rtub", (X - 1.6, 0, 1.6), 0.15)
    pn = wood_mat("c9piano", "#2a120a", "#120604", 8, 0.25)
    bx("piano", (X + 2.9, 0.65, 2.9), (1.6, 1.3, 0.6), pn, 0.03, -0.2); bx("pkeys", (X + 2.85, 0.75, 2.55), (1.4, 0.04, 0.22), pmat("c9keys", "#f2ecd8", 0.3), 0.005, -0.2)
    for k, (x_, z_, yw) in enumerate(((1.2, -0.5, 0.8), (-0.4, -1.8, 2.3))): __import__("sets.warroom", fromlist=["chair"]).chair(f"rch{k}", (X + x_, 0, z_), yw, pn, K.mat_once("c9seat2", lambda: lib.cloth("c9seat2", "#5a2a2a")))
    bx("rchairbroken", (X + 0.4, 0.2, 1.0), (0.45, 0.06, 0.45), pn, 0.01, 0.6)
    bx("rpic", (X - 4.0, 1.9, -1.0), (0.05, 0.6, 0.8), wood_mat("c9frame", "#6a4a1a", "#3a2a0a", 9, 0.4), 0.01, 0.0).rotation_euler[0] = 0.15
    bx("rpicin", (X - 3.97, 1.9, -1.0), (0.02, 0.48, 0.66), pmat("c9pic", "#6a7a5a", 0.6), 0.0).rotation_euler[0] = 0.15
    for k in range(40): bx(f"rdeb{k}", (X + rnd.uniform(-3.5, 3.5), 0.03, rnd.uniform(-3.5, 3.5)), (rnd.uniform(0.05, 0.3), 0.04, rnd.uniform(0.05, 0.2)), [fl, wp, pn][k % 3], 0.0, rnd.random() * 3)
    K.blob3("rsnow", (X + 0.5, 0, 3.0), (1.6, 0.25, 1.0), K.snow_ground("c9snow2"), 0.1, 7)
    K.area((X + 0.3, 2.0, 6.5), (X - 0.5, 0.8, 0), 600, (1.0, 0.68, 0.5), 2.5)
    K.area((X, 2.8, -6), (X, 1.2, 1), 220, (0.6, 0.7, 1.0), 6)
def stairs(rnd):
    """a stairwell at x 236..244: flight up +z from (240, 0, -2) to (240, 3.3, 4.6), landing, top floor y 3.3 (z 4.6..8),
    blasted side wall (light), iron banister; the camera looks from z < -3 or from the side x < 236 opening"""
    X = 240.0; st = K.concrete("c9stair", "#9a948a", "#4a4640")
    wall = K.mat_once("c9swall", lambda: K.add_snow(lib.plaster("c9swall", "#a8a090"), 0.3))
    bx("sfloor", (X, -0.05, 2), (9, 0.1, 14), st, 0)
    n = 12
    n = 12
    for k in range(n): bx(f"step{k}", (X, (k + 1) * 0.1375, -2 + k * 0.55 + 0.275), (2.0, (k + 1) * 0.275, 0.55), st, 0.005)
    bx("slanding", (X, 3.2, 6.3), (6, 0.2, 3.4), st, 0.01)
    bx("sback", (X, 3.3, 8.1), (8, 6.6, 0.25), wall, 0)
    bx("sright", (X + 3.9, 3.3, 2), (0.25, 6.6, 12), wall, 0)
    for (z0, z1, y0, y1) in ((-4, 0.5, 0, 6.6), (3.5, 8, 0, 6.6), (0.5, 3.5, 4.8, 6.6)): bx(f"sleft{z0}{y0}", (X - 3.9, (y0 + y1) / 2, (z0 + z1) / 2), (0.25, y1 - y0, z1 - z0), wall, 0)
    for k in range(n):
        tube(f"bal{k}", [(X - 1.0, (k + 1) * 0.275, -2 + k * 0.55 + 0.275), (X - 1.0, (k + 1) * 0.275 + 0.9, -2 + k * 0.55 + 0.275)], 0.012, pmat("c9iron", "#2a2a28", 0.6, 0.5), res=2, bres=0) if k % 2 == 0 else None
    tube("rail", [(X - 1.0, 1.2, -1.7), (X - 1.0, 4.2, 4.3), (X - 1.0, 4.2, 6.0)], 0.03, wood_mat("c9rail", "#4a2a14", "#2a140a", 8, 0.4), res=4, bres=1)
    K.rubble("srub", (X + 1.5, 0, -1.2), (2.0, 0.5, 1.4), K.mat_once("c9rubble2", lambda: K.add_snow(__import__("sets.front", fromlist=["ruin_mat"]).ruin_mat("c9rubble2", "#8a7a6a", "#8a4632"), 0.5)), 9, 4)
    K.area((X - 6, 2.5, 2), (X, 1.5, 2), 500, (1.0, 0.68, 0.5), 3)
    K.area((X, 6, 2), (X, 0, 2), 200, (0.6, 0.7, 1.0), 4)
    lib.light("POINT", T(X + 2, 4.5, 6.5), 60, (1.0, 0.5, 0.2), 0.1).visible_camera = False
