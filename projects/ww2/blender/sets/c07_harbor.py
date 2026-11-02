# Pearl Harbor, 7 December 1941 (chapter 7 shots 8-10), three.js layout (y up, metres, real scale):
#   the camera-side Navy Yard pier: x -6..6, z -40..0, deck top y 1.6 (sailors stand at z -6..-1); quay edge z -40.
#   Battleship Row: US battleships moored bow -x along z 120 (outboard) / 158 (inboard) at x -520, -320, -110, 100, 300.
#   Ford Island: flat land z 200..900 (y 0.8), quays along z 200, hangars, tower, palms. Koolau ridge z 2600..5000.
#   The empty carrier berth (shot 10): a quay on the near shore at x -330..-270, z -26 with its sign at (-296, 1.6, -27);
#   the camera looks +z / -x from about (-288, 2.2, -36) over empty water.
# Sun: early morning, low in the east (+x, slightly toward the camera). Attack state (planes, fires, smoke, splashes,
# flak) switches on per frame in update(f): F_ATTACK (chapter-local frame 905).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, poster, barrel, crate
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK

SUN = (0.75, 0.32, -0.25)
F_ATTACK = 905
SHIPS = [(-520, 70), (-320, 70), (-110, 70), (-110, 104), (100, 70), (100, 104), (300, 70)]

def plane_path(k, f):
    """k < 12: attack planes crossing the row (z 60) at frame 925 + 17k, diving toward the pier side; k >= 12: a high
    formation of level bombers crossing the sky (-x)"""
    rs = random.Random(k * 31 + 7)
    if k < 12:
        fp = 925 + 17 * k; s_ = (f - fp) / 30.0
        x = rs.uniform(-110, 60); yr = rs.uniform(30, 60); vx = rs.uniform(-12, 12); vy = -rs.uniform(10, 25)
        p = Vector((x + vx * s_, max(22.0, yr + vy * s_), 60 - 90 * s_))
        return p, Vector((vx, vy if p.y > 22.5 else 0.0, -90)), 0.3 * math.sin(k * 1.7)
    j = k - 12; row, col = divmod(j, 3)
    p = Vector((700 - 70 * (f - 860) / 30.0 + col * 18 + row * 30, 420 + col * 6, 520 + (col - 1) * 22 + row * 60))
    return p, Vector((-1, 0, 0)), 0.0

def build(M, D):
    rnd = random.Random(1207)
    S = bpy.context.scene
    CK.sky(S.world, SUN, [(0.0, (0.95, 0.62, 0.38)), (0.05, (0.55, 0.58, 0.72)), (0.25, (0.18, 0.34, 0.66)), (1.0, (0.04, 0.12, 0.38))],
           sun_col=(40, 30, 16), cloud_dark=(0.32, 0.3, 0.38), cloud_lit=(1.3, 0.95, 0.7), cover=0.5, strength=0.62, glow_col=(1.0, 0.55, 0.25), glow=0.8)
    CK.sun_light(SUN, 5.5, (1.0, 0.78, 0.55), 1.2)
    # ---------- water, shores, Ford Island, hills ----------
    CK.sea("harbour", -4000, 4000, -900, 6000, -0.25, CK.water_mat("hwater", "#0e3a44", "#2a6a6a", 1.0, 0.05, 0.35))
    sand = mat_once("hsand", lambda: lib.plaster("hsand", "#b8a888"))
    grass = mat_once("hgrass", lambda: CK.green_hill_mat("hgrass", "#5a7a2a", "#3a5a1e", "#8a7a52"))
    concrete = mat_once("hconc", lambda: lib.plaster("hconc", "#a8a49a"))
    CK.heightfield("nearshore", -1500, 900, -420, -40, 6, lambda x, z: 0.9 + 0.6 * max(0, (-z - 80) / 300) * 20, grass)
    bx = CK.bx
    bx("quay", (-300, 0.4, -46), (2400, 1.4, 14), concrete, 0.05)
    CK.heightfield("ford", -760, 560, 146, 900, 8, lambda x, z: 0.8 + 0.4 * math.sin(x * 0.01) * min(1, (z - 146) / 40), grass)
    bx("fordquay", (-100, 0.5, 150), (1300, 1.6, 10), concrete, 0.05)
    CK.heightfield("koolau", -6000, 6000, 2400, 6000, 60, CK.ridge_fn(2400, 4200, -20, 750, 4, 0.0015), mat_once("hkoolau", lambda: CK.green_hill_mat("hkoolau", "#3e6a3a", "#22422a", "#5a6a5a")))
    CK.heightfield("westshore", -4000, -1500, -900, 2400, 40, lambda x, z: -6 + 60 * max(0, (-x - 1200) / 2800) + 8 * math.sin(z * 0.004), grass)
    CK.heightfield("eastshore", 900, 4000, -900, 2400, 40, lambda x, z: -6 + 80 * max(0, (x - 1300) / 2700) + 8 * math.sin(z * 0.005), grass)
    # ---------- battleship row ----------
    ship = CK.us_battleship("bb", SHIPS[0][0], SHIPS[0][1], math.pi, 180, 30, 0.0)
    for k, (x, z) in enumerate(SHIPS[1:]): CK.clone(ship, x - SHIPS[0][0], z - SHIPS[0][1], f"c{k}")
    # quays (mooring blocks) between the pairs
    for k, (x, z) in enumerate(SHIPS):
        if z == 70: bx(f"moor{k}", (x + 70, 0.8, 130), (14, 2.6, 8), concrete, 0.1)
    # ---------- Ford Island buildings ----------
    K = Kit("ford")
    roof = pm("#6a7480", 0.5, 0.4); wall = pm("#d8d0bc", 0.8); red = pm("#a8322a", 0.7); white = pm("#f2efe6", 0.6); dark = pm("#2a2c30", 0.6)
    for k in range(4):
        hx = -420 + k * 120; hz = 380
        K.box((hx, 9, hz), (90, 18, 60), wall, 0.0, 0.3)
        K.cyl((hx, 18, hz), 31, 90, roof, 24, "x")
        K.box((hx, 7, hz - 30.2), (70, 14, 0.4), dark, 0.0, 0.0)
    for k in range(10): K.box((-650 + k * 110, 5, 240), (40, 10, 18), wall, 0.0, 0.3); K.box((-650 + k * 110, 10.5, 240), (42, 1.2, 20), red, 0.0, 0.3)
    K.box((-180, 20, 330), (10, 40, 10), wall, 0.0, 0.0); K.box((-180, 42, 330), (14, 5, 14), pm("#24343a", 0.2, 0.3), 0.0, 0.0); K.box((-180, 45.5, 330), (16, 1, 16), red, 0.0, 0.0)
    for k in range(6):   # checkered water tower
        K.box((60, 30 + k * 2.5, 330), (14, 2.5, 14), red if k % 2 else white, 0.0, 0.0)
    for sd in ((-1, -1), (1, -1), (1, 1), (-1, 1)): K.box((60 + sd[0] * 6, 15, 330 + sd[1] * 6), (0.8, 30, 0.8), dark, 0.0, 0.0)
    # navy yard on the near shore: sheds, cranes, the tank farm to the east
    for k in range(7):
        x = -820 + k * 110
        if abs(x) < 60: continue
        K.box((x, 7, -90), (60, 14, 30), wall if k % 2 else pm("#c8b89a", 0.8), 0.0, 0.3); K.box((x, 14.6, -90), (62, 1.4, 32), roof, 0.0, 0.3)
        for w in range(8): K.box((x - 26 + w * 7.4, 8, -74.9), (3.5, 3, 0.3), pm("#1e2428", 0.2), 0.0, 0.0)
    for k in range(9):
        tx, tz = 520 + (k % 3) * 70, -160 + (k // 3) * 70
        K.cyl((tx, 9, tz), 26, 18, pm("#c8c4b8", 0.5, 0.2), 32, "y"); K.cyl((tx, 18.5, tz), 26.5, 1.2, pm("#8a8a84", 0.5, 0.2), 32, "y", r2=10)
    for k, x in enumerate((-160, 160)):
        K.box((x, 18, -60), (2, 36, 2), pm("#3a3a36", 0.5, 0.6), 0.0, 0.0); K.box((x + 12, 36, -60), (34, 2, 2), pm("#3a3a36", 0.5, 0.6), 0.0, 0.0)
        tube(f"cranec{k}", [(x + 24, 36, -60), (x + 24, 20, -60)], 0.08, pmat("hcable", "#1a1a1a", 0.6), res=2, bres=0)
    K.build()
    # ---------- the pier (close shots): planks on pilings, bollards, ropes, crates, drums, life rings, lamp, signs ----------
    P = Kit("pier")
    plank = wood("#8a6a48", "#4a3622", 3.0, 0.75); pile = wood("#5a4632", "#2a1e14", 2.0, 0.8); iron = pm("#2a2a2e", 0.5, 0.7)
    for k in range(40):
        P.box((0, 1.5, -40 + k + 0.5), (12, 0.12, 0.92), plank, rnd.uniform(-0.01, 0.01), 0.008)
    for sx in (-5.6, -2, 2, 5.6):
        for k in range(9): P.cyl((sx, 0.2, -38 + k * 4.7), 0.22, 2.9, pile, 10)
    for sd in (-1, 1):
        P.box((sd * 6.05, 1.35, -20), (0.25, 0.35, 40), plank, 0.0, 0.01)
        for k in range(8):
            z = -37 + k * 5; P.cyl((sd * 5.6, 1.85, z), 0.16, 0.5, iron, 14); P.cyl((sd * 5.6, 2.14, z), 0.22, 0.1, iron, 14)
    mrope = pmat("hrope", "#b89a62", 0.9)
    for k, (x, z) in enumerate(((-4.2, -3.2), (4.0, -9.0), (-4.5, -15))):
        for j in range(4): P.torus((x, 1.6 + j * 0.06, z), 0.42 - j * 0.03, 0.05, mrope, 20, 6)
    tube("mline", [(-5.6, 2.1, -2.0), (-7, 1.2, 2), (-12, 0.0, 30), (-60, 2, 110), (-108, 6, 115)], 0.05, mrope, res=20, bres=1)
    cr = wood("#a07a4a", "#6a4a2a", 5.0, 0.8)
    for k, (x, z, s, yw) in enumerate(((3.6, -4.8, 0.8, 0.2), (4.4, -5.6, 0.6, -0.3), (3.6, -4.8, 0.55, 0.5), (-3.8, -11, 0.9, 0.1), (-4.4, -10.0, 0.6, 0.6))):
        crate(P, (x, 1.56 + (0.64 if k == 2 else 0) + s * 0.4, z), s, cr, yw)
    drum = pm("#4a5a3a", 0.5, 0.4)
    for k, (x, z) in enumerate(((-4.6, -6.2), (-4.0, -6.8), (-4.8, -7.4), (4.6, -13), (4.1, -13.6))): barrel(P, (x, 1.56 + 0.45, z), 0.3, 0.9, drum, pm("#2a2a26", 0.5, 0.5))
    lr = pm("#e8e4dc", 0.6); lrr = pm("#c8302a", 0.6)
    for k, (x, z) in enumerate(((-5.9, -8.5), (5.9, -17))):
        for j in range(8): P.torus((x - 0.05 * (1 if x > 0 else -1), 2.45, z), 0.36, 0.07, lr if j % 2 == 0 else lrr, 4, 8, "x", arc=math.pi / 4, roll=j * math.pi / 4)
        P.box((x, 1.9, z), (0.1, 1.3, 0.1), pile, 0.0, 0.0)
    # lamp post, sentry box, mail sacks, a bicycle, tool box, signal flags on a staff
    P.cyl((5.2, 3.2, -20), 0.07, 3.3, iron, 10); P.box((5.2, 4.9, -20), (0.35, 0.4, 0.35), pm("#ffe0a0", 0.3), 0.0, 0.0)
    P.box((-4.0, 2.7, -26), (1.6, 2.3, 1.6), pm("#e8e2d2", 0.7), 0.2, 0.02); P.box((-4.0, 3.95, -26), (1.9, 0.2, 1.9), red, 0.2, 0.02)
    P.box((-3.25, 2.9, -26.2), (0.05, 0.9, 0.8), pm("#1a2026", 0.2), 0.2, 0.0)
    sack = mat_once("hsack", lambda: lib.cloth("hsack", "#c8b890"))
    for k in range(4): lib.blob(f"sack{k}", T(2.6 + k * 0.45, 1.85, -24 + (k % 2) * 0.4), (0.3, 0.32, 0.4), sack, 0.05, k)
    P.box((2.8, 1.75, -9.5), (0.7, 0.35, 0.35), pm("#8a2a22", 0.5, 0.3), 0.3, 0.02)
    P.cyl((-5.4, 4.0, -1.0), 0.05, 4.8, pile, 8)
    for j, col in enumerate(("#c8202a", "#f2d040", "#1e3a8a", "#f2efe6")):
        P.box((-5.4, 6.0 - j * 0.65, -0.35), (0.04, 0.55, 1.0), pm(col, 0.8), 0.0, 0.0)
    P.build()
    SG = Kit("signs")
    sign(SG, (0, 3.4, -38.6), 4.6, 0.9, 0.0, "PIER 1  -  NAVY YARD PEARL HARBOR", board="#1e3a5a", ink=pm("#f2efe6", 0.5), kind="sans", trim="#c8a24a")
    for sx in (-2.2, 2.2): SG.cyl((sx, 2.5, -38.6), 0.06, 1.9, iron, 8)
    sign(SG, (4.6, 2.4, -6.3), 1.2, 0.5, math.pi / 2, "NO SMOKING", board="#c8302a", ink=pm("#f2efe6", 0.5), kind="sans")
    poster(SG, (-3.2, 3.0, -26.0 - 0.81), 0.9, 1.1, 0.0, "#e8dcc0", [("ENLIST", 0.2), ("U.S. NAVY", 0.15), ("1941", 0.12)], "#1e2a5a", accent="#c8302a")
    SG.build()
    # ---------- the empty carrier berth (shot 10): west of the row, nothing moored, the sign says where the carrier is ----------
    B = Kit("berth"); BX = -900
    B.box((BX, 0.6, -30), (70, 2.0, 12), concrete, 0.0, 0.05)
    for k in range(6): B.cyl((BX - 30 + k * 12, 1.95, -24.6), 0.25, 0.7, iron, 14); B.cyl((BX - 30 + k * 12, 2.3, -24.6), 0.33, 0.1, iron, 14)
    sign(B, (BX + 4, 3.2, -29.0), 4.4, 1.1, 0.0, "CARRIER BERTH  F-9", board="#e8e2d2", ink=pm("#1e2a3a", 0.5), kind="sans", trim="#2a2a2a")
    sign(B, (BX + 4, 2.35, -29.0), 4.4, 0.5, 0.0, "USS ENTERPRISE - AT SEA", board="#e8e2d2", ink=pm("#a8282a", 0.5), kind="sans")
    for sx in (-2.0, 2.0): B.cyl((BX + 4 + sx, 2.2, -28.95), 0.06, 3.0, iron, 8)
    for k in range(5): crate(B, (BX - 20 + k * 1.1, 1.6 + 0.28, -32 + (k % 2) * 0.5), 0.7, cr, k * 0.3)
    for k in range(4): barrel(B, (BX + 12 + (k % 2) * 0.7, 1.6 + 0.45, -33 + k * 0.6), 0.3, 0.9, drum, pm("#2a2a26", 0.5, 0.5))
    for j in range(5): B.torus((BX - 8, 1.62 + j * 0.06, -27), 0.5 - j * 0.04, 0.06, mrope, 20, 6)
    for k in range(6): crate(B, (BX - 3 + (k % 3) * 0.8, 1.6 + 0.28 + (k // 3) * 0.56, -33.5), 0.7, cr, 0.1 * k)
    for j in range(8): B.torus((BX + 7.5, 2.1, -24.3), 0.36, 0.07, lr if j % 2 == 0 else lrr, 4, 8, "z", arc=math.pi / 4, roll=j * math.pi / 4)
    B.box((BX + 1.0, 1.75, -23.0), (1.2, 0.3, 4.0), plank, 0.0, 0.02)
    B.build()
    # ---------- palms along both shores ----------
    pf = CK.palm_srcs(rnd); trunk = CK.palm_trunk()
    for k in range(26):
        x = -880 + k * 68 + rnd.uniform(-15, 15)
        if abs(x) < 40 or -340 < x < -250: continue
        CK.palm(f"pn{k}", x, 1.0, -60 - rnd.uniform(0, 30), rnd.uniform(11, 16), 0.12, rnd.uniform(0, 6), pf, trunk, rnd, 1.3)
    for k, (x, z) in enumerate(((-14, -44), (13, -45), (-22, -50), (24, -48))): CK.palm(f"pp{k}", x, 1.0, z, rnd.uniform(9, 12), 0.15, rnd.uniform(0, 6), pf, trunk, rnd, 1.1)
    for k in range(30): CK.palm(f"pf{k}", -720 + k * 42 + rnd.uniform(-10, 10), 0.8, 180 + rnd.uniform(0, 30), rnd.uniform(11, 15), 0.1, rnd.uniform(0, 6), pf, trunk, rnd, 1.3, nuts=False)
    # small craft: a motor launch and a whaleboat in the water, a buoy
    L = Kit("boats")
    for k, (x, z, yw) in enumerate(((-40, 50, 0.4), (60, 70, -0.8))):
        L.box((x, 0.2, z), (9, 1.2, 2.6), pm("#5a6a78", 0.5, 0.2), yw, 0.3); L.box((x - 1, 1.2, z), (3.5, 1.0, 2.0), pm("#e8e4dc", 0.6), yw, 0.1)
    L.cyl((25, 0.4, 30), 0.9, 1.6, pm("#c8302a", 0.6), 16); L.cyl((25, 1.6, 30), 0.3, 1.0, pm("#2a2a2a", 0.6), 10)
    L.build()
    # ---------- the attack: planes, fires, smoke, splashes, flak ----------
    kinds = ["kate", "val", "zero", "val", "kate", "zero", "val", "kate", "zero", "val", "kate", "zero"] + ["kate"] * 9
    planes = [CK.inst(CK.plane(k_), f"atk{i}") for i, k_ in enumerate(kinds)]
    attack = []
    for k, (x, z) in enumerate(SHIPS):
        for j in range(3): attack += CK.fireball(f"fire{k}{j}", (x + rnd.uniform(-60, 50), 8.0, z + rnd.uniform(-8, 8)), rnd.uniform(1.8, 3.2), k * 5 + j, 2500)
        attack += CK.smoke(f"smb{k}", (x + rnd.uniform(-20, 20), 9, z), 14, 7, 12, "#7a3410", 0.75, (0, 0), k + 60, 4)
        attack += CK.smoke(f"smk{k}", (x + rnd.uniform(-30, 30), 10, z), 260 if k == 1 else 170, 10, 70, "#141210", 0.9, (-160, 120), k, 12)
        if k % 2 == 0: attack += CK.smoke(f"smw{k}", (x - 50, 6, z - 10), 90, 6, 30, "#5a524a", 0.7, (-90, 60), k + 20, 8)
    attack += CK.fireball("arizona", (-300, 10, 70), 6, 99, 40000)
    splashes = []
    for k in range(9):
        x = (-560 + k * 70 if k < 6 else 120 + (k - 6) * 80) + rnd.uniform(-15, 15); z = rnd.uniform(30, 55)
        splashes.append((935 + k * 17, CK.splash(f"spl{k}", (x, -0.25, z), rnd.uniform(18, 28), rnd.uniform(2.0, 3.0))))
    flak = []
    for k in range(26):
        flak.append((F_ATTACK + rnd.randrange(0, 200), CK.smoke(f"flak{k}", (rnd.uniform(-700, 600), rnd.uniform(120, 420), rnd.uniform(-100, 700)), 1, rnd.uniform(4, 7), 7, "#1a1816", 0.92, seed=k + 40, puffs=2)))
    haze = CK.smoke("haze", (-200, 30, 260), 120, 80, 160, "#3a3634", 0.45, (-200, 0), 7, 6)
    # warm rim from the burning row on the pier side (only in the attack)
    glow = [CK.area((-100, 30, 60), (0, 2, -10), 120000, (1.0, 0.45, 0.15), 120)]
    bounce = CK.area((10, 6, -20), (0, 2, -3), 2500, (0.9, 0.8, 0.7), 12)
    def update(f):
        on = f >= F_ATTACK
        CK.show(attack + glow + haze, on)
        for f0, objs in splashes:
            u = (f - f0) / 30.0; CK.show(objs, 0 <= u < 2.2)
            for o in objs: o.scale = (1, 1, max(0.05, min(1.0, u * 2.0))) if u >= 0 else (1, 1, 1)
        for f0, objs in flak: CK.show(objs, f >= f0)
        for i, o in enumerate(planes):
            p, v, roll = plane_path(i, f)
            vis = f >= 845 and -1500 < p.x < 1500 and -400 < p.z < 2500
            o.hide_render = not vis
            if vis: CK.place(o, tuple(p), tuple(v), roll, 1.5)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
