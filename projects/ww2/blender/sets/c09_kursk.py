# Kursk, July 1943 (chapter 9): the steppe in high summer - ripe wheat, sunflowers, a white-washed village - cut by the
# Soviet trench lines, minefields and gun pits, with the German tank wave rolling in from the north in its own dust.
# Golden afternoon sun from the west (screen right for cameras looking +z), hazy blue sky, smoke from burning tanks.
# Layout (three, y up; the Germans come from +z toward -z):
#   first trench: centre line z 0, |x| < 40, floor y -1.5 (soldiers stand at y -1.3; parapet at y +0.4 on the z+ side);
#           AT guns dug in at (-12, 0, 2.6) (6, 0, 2.6) (22, 0, 2.6) muzzles +z; a dugout entrance at (-4, -1.5, -0.9).
#   rear trenches z -22, -45, -70 (same profile), gun pits behind each; telegraph line along x = -30.
#   minefield: z 6..30 (signs at z 6), wire on pickets at z 5.
#   German wave: Tigers / Panzers on z 60..260 (|x| < 120) facing -z; a burning Tiger stuck in a crater at (8, 0, 26)
#           (shot "the attack fails": crew at (11, 0, 23)); burnt wrecks scattered z 30..60.
#   Soviet counter-attack: T-34s at x 40..90, z -16..4 facing +z; infantry runs among them; the camera for it sits ~ (60, 1, -26).
#   flat ground (y 0 outside the crater) round the stuck Tiger (r 6 about (9, 22)), the T-34 field x 36..95, z -28..8, and round (-6, -8).
#   village: white khatas with thatched roofs round (-55, 0, -10), sunflowers between the village and the trench.
import bpy, math, random
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, smoke_mat, smoke_column, text
from sets import c09_kit as K

bx, cy = K.bx, K.cy
TRENCHES = (0.0, -22.0, -45.0, -70.0)
def trench_d(x, z):
    d = 9.0
    for tz in TRENCHES:
        zz = tz + 1.2 * math.sin(x * 0.12 + tz)
        d = min(d, abs(z - zz))
    return d
def H(x, z):
    h = 1.6 * noise.noise(Vector((x * 0.012, z * 0.012, 0.4))) + 0.25 * noise.noise(Vector((x * 0.07, z * 0.07, 2.1)))
    h *= K.sm(4, 30, math.hypot(x - 8, z - 4)) * 0.7 + 0.3
    flat = max(1 - K.sm(6, 10, math.hypot(x - 9, z - 22)), (1 - K.sm(36, 100, x) if x > 30 else K.sm(30, 36, x)) * (1 - K.sm(8, 14, z)) * K.sm(-34, -28, z), 1 - K.sm(3, 8, math.hypot(x + 6, z + 8)))
    h *= 1 - flat
    if abs(x) < 46:
        d = trench_d(x, z)
        if d < 0.75: h = -1.5
        elif d < 1.6: h = max(h, 0.4 * (1 - (d - 0.75) / 0.85))
    if math.hypot(x - 8, z - 26) < 3.2: h -= 1.0 * (1 - (math.hypot(x - 8, z - 26) / 3.2) ** 2)
    return h
def build(M, D):
    rnd = random.Random(1943)
    K.sky("#4a7ac0", "#e8d0a0", 1.0, "#3a6ab8", "#f0d8a8")
    gm = K.steppe_ground("c9steppe", "#5a4a30")
    def mask(x, z):
        if abs(x) < 46 and trench_d(x, z) < 1.7: return 0.9
        if 4 < z < 32 and abs(x) < 45: return 0.35
        return 0.0
    K.heightfield("ground", H, -160, 160, -110, 280, 1.0, gm, mask)
    # wheat / grass cover: instanced tufts (dense near the cameras)
    wheat = K.mat_once("c9wheat", lambda: worn("c9wheat", "#c8a858", "#8a7a3a", 0.85, 0.0, 6, 0.5, "#a88a40"))
    from sets.front import grass_tuft_src, scatter
    src = grass_tuft_src(wheat, 3); pts = []
    while len(pts) < 2600:
        x_, z_ = rnd.uniform(-90, 120), rnd.uniform(-90, 120)
        if abs(x_) < 46 and trench_d(x_, z_) < 2.0: continue
        if math.hypot(x_ - 8, z_ - 26) < 4: continue
        pts.append((x_, H(x_, z_) - 0.03, z_))
    scatter(src, "wh", pts, s=(1.2, 2.6), seed=4); src.location = T(0, -50, 0)
    # trenches: log revetments, duckboards, sandbag parapets, firing steps
    logm = wood_mat("c9log", "#6a5a3a", "#3a2a18", 4, 0.8)
    duck = wood_mat("c9duck", "#7a6040", "#4a3420", 8, 0.8)
    for ti, tz in enumerate(TRENCHES):
        for k in range(46 if ti == 0 else 24):
            x_ = -44 + k * (2.0 if ti == 0 else 3.8)
            zz = tz + 1.2 * math.sin(x_ * 0.12 + tz)
            for sd in (-1, 1):
                tube(f"rev{ti}{k}{sd}", [(x_ - 1.0, -0.9, zz + sd * 0.72), (x_ + 1.0, -0.9, zz + sd * 0.72)], 0.11, logm, res=2, bres=1)
                if ti == 0: tube(f"rev2{ti}{k}{sd}", [(x_ - 1.0, -0.6, zz + sd * 0.74), (x_ + 1.0, -0.6, zz + sd * 0.74)], 0.1, logm, res=2, bres=1)
            if ti == 0: bx(f"duck{k}", (x_, -1.45, zz), (1.9, 0.05, 0.6), duck, 0.005, 0.0)
            if k % 3 == 0: tube(f"post{ti}{k}", [(x_, -1.5, zz + 0.75), (x_, 0.0, zz + 0.75)], 0.07, logm, res=2, bres=1)
        if ti == 0:
            for k in range(14): K.sandbags(f"tsb{k}", (-40 + k * 6, H(-40 + k * 6, 1.4), 1.2 + 1.2 * math.sin((-40 + k * 6) * 0.12)), 0.0, 5, 2, k + 40)
    # dugout entrance
    bx("dugr", (-4, -0.3, -1.6), (2.4, 0.2, 1.6), logm, 0.02)
    bx("dugd", (-4, -1.0, -1.25), (1.0, 1.1, 0.05), K.mat_once("finterior", lambda: lib.principled("finterior", lib.hexc("#0c0908"), 1.0)), 0)
    # AT guns dug in front of the first trench, and gun pits behind the rear lines
    for k, x_ in enumerate((-12, 6, 22, -28, 34)):
        z_ = 2.8 + 1.2 * math.sin(x_ * 0.12)
        K.at_gun(f"atg{k}", x_, z_, -math.pi / 2, y0=H(x_, z_) - 0.25)
        for a_ in (-1, 1): K.sandbags(f"ats{k}{a_}", (x_ + a_ * 1.6, H(x_ + a_ * 1.6, z_ + 1.2), z_ + 1.0), math.pi / 2 + a_ * 0.6, 3, 2, k * 5 + a_)
        for j in range(3): K.ammo_box(f"atb{k}{j}", (x_ - 1.2 + j * 0.35, H(x_, z_ - 1.5), z_ - 1.5), 0.2 * j, "", "#4e5a32")
    for ti, tz in enumerate(TRENCHES[1:]):
        for k in range(6):
            x_ = -40 + k * 16 + rnd.uniform(-3, 3); z_ = tz - 4
            K.field_gun(f"rg{ti}{k}", x_, z_, -math.pi / 2, "#4e5a32", y0=H(x_, z_))
    # minefield: wire on pickets, warning signs, half-buried mines
    for k in range(8):
        x0 = -42 + k * 11
        K.wire(f"mw{k}", (x0, H(x0, 5), 5.0), 10, 0.0, 0.4)
        for e in (-5, 0, 5): tube(f"mp{k}{e}", [(x0 + e, H(x0 + e, 5) - 0.2, 5.0), (x0 + e, H(x0 + e, 5) + 1.0, 5.0)], 0.04, logm, res=2, bres=1)
    for k, x_ in enumerate((-30, -8, 15, 37)):
        bx(f"ms{k}", (x_, H(x_, 6.5) + 0.9, 6.5), (0.7, 0.45, 0.03), pmat("c9msign", "#e8dcc0", 0.6), 0.01, rnd.uniform(-0.1, 0.1))
        tube(f"msp{k}", [(x_, H(x_, 6.5) - 0.2, 6.52), (x_, H(x_, 6.5) + 0.7, 6.52)], 0.03, logm, res=2, bres=1)
        text("МИНЫ!", (x_, H(x_, 6.5) + 0.9, 6.47), 0.14, pmat("c9mink", "#a81e1e", 0.6), flat=False)
    minem = K.mat_once("c9mine", lambda: worn("c9mine", "#4a4e3a", "#2a2a22", 0.6, 0.5, 20, 0.6))
    for k in range(70):
        x_, z_ = rnd.uniform(-42, 44), rnd.uniform(8, 30)
        if math.hypot(x_ - 8, z_ - 26) < 4: continue
        lathe(f"mine{k}", [(0.0, 0.0), (0.16, 0.0), (0.16, 0.05), (0.06, 0.07), (0.0, 0.09)], (x_, H(x_, z_) - 0.02, z_), minem, 12)
    # ---------- the German wave ----------
    for k in range(34):
        x_ = rnd.uniform(-120, 120); z_ = 60 + (k % 6) * 35 + rnd.uniform(-10, 10)
        (K.tiger if k % 3 == 0 else K.panzer)(f"gw{k}", x_, z_, math.pi / 2 + rnd.uniform(-0.15, 0.15), *(("#8a7a4a", "#4e5a3a") if k % 3 == 0 else ("#6a6a58",)), y0=H(x_, z_))
    dust = K.mat_once("c9dust", lambda: smoke_mat("c9dust", "#b8a07a", 0.32))
    for k in range(18):
        x_ = rnd.uniform(-110, 110); z_ = 70 + rnd.uniform(0, 160)
        smoke_column(f"dust{k}", (x_, H(x_, z_) + 1.5, z_ + 4), 6, 3.5, 7, dust, drift=(8, 6), seed=k + 100, puffs=6)
    K.tiger("stuck", 8, 26, math.pi / 2 + 0.35, y0=H(8, 26) + 0.2, tilt=-0.18)
    fire("stuckf", (7.6, H(8, 26) + 2.6, 25.5), 1.0, seed=3, energy=1800)
    sm = K.mat_once("c9smoke", lambda: smoke_mat("c9smoke", "#1e1a18", 0.4))
    smoke_column("stucks", (7.6, H(8, 26) + 3.5, 26), 26, 1.0, 6, sm, drift=(-14, 10), seed=8, puffs=12)
    for k in range(6):
        x_, z_ = rnd.uniform(-60, 70), rnd.uniform(32, 62)
        K.panzer(f"wr{k}", x_, z_, rnd.uniform(0, 6), burnt=True, y0=H(x_, z_), tilt=rnd.uniform(-0.08, 0.08))
        if k % 2 == 0:
            fire(f"wrf{k}", (x_, H(x_, z_) + 1.6, z_), 1.2, seed=k + 20, energy=2400)
            smoke_column(f"wrs{k}", (x_, H(x_, z_) + 3, z_), 30, 1.4, 7, sm, drift=(-16, 12), seed=k + 30, puffs=12)
    # ---------- the Soviet counter-attack: T-34s with infantry ----------
    for k in range(9):
        x_ = 40 + (k % 5) * 11 + rnd.uniform(-2, 2); z_ = -14 + (k // 5) * 12 + rnd.uniform(-2, 2)
        K.t34(f"t34_{k}", x_, z_, -math.pi / 2 + rnd.uniform(-0.1, 0.1), y0=H(x_, z_))
    for k in range(4): smoke_column(f"tdust{k}", (45 + k * 12, H(45 + k * 12, -18) + 1, -18), 5, 3, 6, dust, drift=(4, -4), seed=k + 140, puffs=5)
    # ---------- the village and sunflowers ----------
    thatch = K.mat_once("c9thatch", lambda: worn("c9thatch", "#a88a52", "#6a5430", 0.95, 0.0, 8, 0.5, "#7a643a"))
    wash = K.mat_once("c9wash", lambda: worn("c9wash", "#eee8dc", "#a89a88", 0.85, 0.0, 3, 0.62, "#c8bca8"))
    blue = pmat("c9blue", "#3a6aa8", 0.5)
    for k in range(7):
        x_, z_ = -62 + (k % 4) * 9 + rnd.uniform(-2, 2), -18 + (k // 4) * 13 + rnd.uniform(-2, 2); yw = rnd.uniform(-0.3, 0.3)
        y0 = H(x_, z_)
        bx(f"khw{k}", (x_, y0 + 1.25, z_), (6.0, 2.5, 4.0), wash, 0.08, yw)
        K.loft2(f"khr{k}", [(3.6, -2.6), (3.6, 2.6), (-3.6, 2.6), (-3.6, -2.6)], 2.4, [(2.2, -0.2), (2.2, 0.2), (-2.2, 0.2), (-2.2, -0.2)], 4.9, K.P_of(x_, z_, yw, y0), thatch)
        for sd in (-1, 1): bx(f"khwin{k}{sd}", (x_ + sd * 1.5 * math.cos(yw), y0 + 1.4, z_ - 2.01 + sd * 1.5 * math.sin(yw)), (0.8, 0.8, 0.05), blue, 0.01, yw)
        bx(f"khdoor{k}", (x_, y0 + 1.0, z_ - 2.02), (0.9, 1.9, 0.05), wood_mat("c9door", "#4a3420", "#2a1a0c", 6, 0.7), 0.01, yw)
    sunfl = K.mat_once("c9sunfl", lambda: lib.principled("c9sunfl", lib.hexc("#e8b81a"), 0.6))
    stem = K.mat_once("c9stem", lambda: lib.principled("c9stem", lib.hexc("#3a5a1e"), 0.7))
    cen = K.mat_once("c9sunc", lambda: lib.principled("c9sunc", lib.hexc("#3a2410"), 0.8))
    for k in range(160):
        x_, z_ = rnd.uniform(-48, -26), rnd.uniform(-28, -4)
        if trench_d(x_, z_) < 2.2: continue
        y0 = H(x_, z_); h_ = rnd.uniform(1.4, 2.0)
        tube(f"sfs{k}", [(x_, y0, z_), (x_ + 0.05, y0 + h_, z_)], 0.025, stem, res=2, bres=0)
        cy(f"sfh{k}", (x_ + 0.06, y0 + h_, z_ - 0.05), 0.22, 0.04, sunfl, 12, rot=(math.radians(70), 0, rnd.uniform(-0.3, 0.3)))
        cy(f"sfc{k}", (x_ + 0.06, y0 + h_ + 0.01, z_ - 0.08), 0.12, 0.05, cen, 10, rot=(math.radians(70), 0, rnd.uniform(-0.3, 0.3)))
    # telegraph line
    for k in range(8):
        z_ = -90 + k * 14; tube(f"tpole{k}", [(-30, H(-30, z_) - 0.2, z_), (-30, H(-30, z_) + 6, z_)], 0.1, logm, res=2, bres=1)
    # light: golden afternoon sun from the west, blue sky fill, warm bounce off the wheat
    K.sun((-0.85, 0.42, 0.3), 4.5, (1.0, 0.8, 0.55), 1.5)
    K.area((0, 40, -60), (0, 0, 20), 30000, (0.55, 0.7, 1.0), 100)
    K.area((0, 4, -10), (0, 0, 4), 900, (1.0, 0.85, 0.6), 20)
    return {}
