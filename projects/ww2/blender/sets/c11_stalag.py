# Stalag Luft III, March 1944 (chapter 11, the Great Escape). Three areas in one set:
#  A. the compound (origin): huts on brick piers at (-24,4) (24,4) (-24,19) (24,19) (-22,33) (22,33) and hut 104 at
#     (2,33); the yard / prisoners' circuit x -9..9, z -2..17 (keep clear, flat y 0); the warning wire z 44; the double
#     fence z 46.5 / 49 with a wire coil between; goon boxes at (-18, 51.5) and (16, 51.5) (platform y 5); the cleared
#     strip z 50..58; THE EXIT HOLE at (6, 55.5) r 0.45 (a man can stand in it: y -1.2 at the bottom); pines from z 58.5.
#     The camp sign at (-9.5, 0, -3.5) faces the camera. Gate + sign at z -30.
#  B. hut 104 inside, x -103.5..-96.5, z 0..4.6 (floor y 0, ceiling 2.6): the stove on its tiled plinth at (-100, 3.7);
#     under it the shaft (0.7 m square) -> update() lifts the stove aside at frames 252..276 (ch11 local frames).
#     Keep clear: x -102..-98, z 0.8..3.0 (two prisoners stand there).
#  C. the cutaway diorama at x 100..176: an earth block (surface y 0, front cut face z 0, camera at z < 0) with the three
#     tunnels as open bores: TOM y -3.0 (x 104..131), DICK y -5.0 (x 111..126), HARRY y -7.4 (x 119..158) and HARRY's exit
#     shaft at x 158 just short of the pines (x 161+). Bores are 1.4 m tall, z 0..1.6, floor at the given y.
#     Chambers "PICCADILLY" (x 132) and "LEICESTER SQ." (x 145) on Harry, air pump at x 121.
# Lights: day = cool overcast + low warm sun; night = moon, perimeter lamps, two searchlights (one sweeps to the hole).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, glassm
from sets import ikit as IK

HX, HZ = 6.0, 55.5
DX = 100.0      # diorama x0
STOVE = None

def H(x, z):
    if abs(x) < 47 and z < 51 and z > -31: return 0.0
    h = 0.25 * C.nz2(x, z, 0.07, 1.3) + 0.08 * C.nz2(x, z, 0.4, 2.1)
    d = min(abs(abs(x) - 47), abs(z - 51), abs(z + 31))
    return h * min(1.0, d / 4.0)

def terrain_mat(night):
    def mk():
        m = lib.principled("stg_ground", lib.hexc("#e8ecf2"), 0.7); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord")
        big = n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 0.12; big.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], big.inputs["Vector"])
        fine = n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 3.0; fine.inputs["Detail"].default_value = 8; l.new(tc.outputs["Object"], fine.inputs["Vector"])
        cov = 0.38 if night else 0.56
        r = lib.ramp(n, l, big.outputs["Fac"], [(cov - 0.06, lib.hexc("#8a7a58")), (cov - 0.02, lib.hexc("#a89874")), (cov + 0.02, lib.hexc("#d8dde6")), (cov + 0.1, lib.hexc("#f2f5fa"))])
        mu = n.new("ShaderNodeMix"); mu.data_type = "RGBA"; mu.blend_type = "MULTIPLY"; mu.inputs[0].default_value = 0.22; l.new(r.outputs["Color"], mu.inputs[6]); l.new(fine.outputs["Color"], mu.inputs[7])
        l.new(mu.outputs[2], b.inputs["Base Color"]); lib.bump(n, l, fine.outputs["Fac"], 0.35, 0.05)
        return m
    return C.mat_once("stg_ground" + str(night), mk)

def hut(K, x, z, yaw, M, rnd, label="", night=False, L=12.0, Dp=7.0):
    P = C._P(x, z, yaw); B = lambda c, s, m, bev=0.01: K.box(P(*c), s, m, yaw, bev)
    fy = 0.6; Hw = 2.6
    for i in range(5):
        for s in (-1, 1): B((-L / 2 + 0.4 + i * (L - 0.8) / 4, fy / 2, s * (Dp / 2 - 0.4)), (0.42, fy, 0.42), M["brick"], 0.01)
    B((0, fy + 0.08, 0), (L + 0.1, 0.16, Dp + 0.1), M["plank"], 0.01)
    B((0, fy + 0.16 + Hw / 2, 0), (L, Hw, Dp), M["boards"], 0.0)
    for s in (-1, 1):
        for k in range(5):
            lx = -L / 2 + 1.2 + k * (L - 2.4) / 4
            if s < 0 and k == 2: continue
            wy = fy + 1.5; fz = s * (Dp / 2 + 0.02)
            B((lx, wy, fz), (1.0, 1.0, 0.04), M["winl"] if night and rnd.random() < 0.6 else M["glass"], 0.0)
            for d in (-0.5, 0.5): B((lx + d, wy, fz + s * 0.03), (0.07, 1.1, 0.06), M["trim"], 0.005)
            for d in (-0.5, 0.5): B((lx, wy + d, fz + s * 0.03), (1.1, 0.07, 0.06), M["trim"], 0.005)
            B((lx, wy, fz + s * 0.03), (0.04, 1.0, 0.05), M["trim"], 0.0); B((lx, wy, fz + s * 0.03), (1.0, 0.04, 0.05), M["trim"], 0.0)
            for d in (-1, 1): B((lx + d * 0.8, wy, fz + s * 0.06), (0.5, 1.05, 0.04), M["shutter"], 0.006)
    # door, steps, number board, lamp
    fz = -Dp / 2
    B((0, fy + 1.2, fz - 0.02), (1.0, 2.0, 0.06), M["door"], 0.01); B((0.35, fy + 1.15, fz - 0.07), (0.05, 0.05, 0.05), brass(), 0)
    for k in range(3): B((0, fy - 0.1 - k * 0.2 + 0.1, fz - 0.3 - k * 0.3), (1.6, 0.18, 0.32), M["plank"], 0.01)
    if label:
        B((0, fy + 2.4, fz - 0.05), (0.9, 0.36, 0.04), pm("#1e2a22", 0.6), 0.005)
        text(label, P(0, fy + 2.4, fz - 0.08), 0.22, pm("#f0ead8", 0.7), yaw, "sans", 0.003)
    B((-0.8, fy + 2.3, fz - 0.15), (0.14, 0.1, 0.3), iron(), 0.01)
    # roof: tar paper with battens, overhang, ridge cap; chimney + stove pipe
    rh = 1.6; y0 = fy + 0.16 + Hw; ov = 0.45
    K.quad([P(-L / 2 - ov, y0 - 0.1, -Dp / 2 - ov), P(L / 2 + ov, y0 - 0.1, -Dp / 2 - ov), P(L / 2 + ov, y0 + rh, 0), P(-L / 2 - ov, y0 + rh, 0)], M["roof"])
    K.quad([P(L / 2 + ov, y0 - 0.1, Dp / 2 + ov), P(-L / 2 - ov, y0 - 0.1, Dp / 2 + ov), P(-L / 2 - ov, y0 + rh, 0), P(L / 2 + ov, y0 + rh, 0)], M["roof"])
    for s in (-1, 1): K.quad([P(s * L / 2, y0, -Dp / 2), P(s * L / 2, y0, Dp / 2), P(s * L / 2, y0 + rh, 0)], M["boards"])
    B((0, y0 + rh + 0.03, 0), (L + 2 * ov, 0.08, 0.3), M["roof2"], 0.01)
    if M.get("snowroof"):
        K.quad([P(-L / 2 - ov, y0 - 0.06, -Dp / 2 - ov), P(L / 2 + ov, y0 - 0.06, -Dp / 2 - ov), P(L / 2 + ov, y0 + rh + 0.04, 0), P(-L / 2 - ov, y0 + rh + 0.04, 0)], M["snowroof"])
    B((L / 4, y0 + rh * 0.7, Dp / 6), (0.5, rh * 1.2, 0.5), M["brick"], 0.01); B((-L / 4, y0 + rh + 0.4, -Dp / 8), (0.12, 1.4, 0.12), iron(), 0.0)
    # props: rain barrel, firewood, bench, bucket, washing line
    K.cyl(P(L / 2 - 0.4, 0.5, -Dp / 2 - 0.5), 0.35, 1.0, M["barrel"], 14, "y", None, yaw)
    for k in range(10): K.cyl(P(-L / 2 + 0.6 + (k % 5) * 0.32, 0.15 + (k // 5) * 0.28, -Dp / 2 - 0.5), 0.13, 1.1, M["log"], 8, "z", None, yaw + 0.05 * k)
    B((-2.5, 0.45, -Dp / 2 - 0.9), (1.8, 0.07, 0.35), M["plank"], 0.01)
    for d in (-0.8, 0.8): B((-2.5 + d, 0.22, -Dp / 2 - 0.9), (0.08, 0.44, 0.3), M["plank"], 0.0)

def build(M, D):
    global STOVE
    night = bool(D.get("night")) or D.get("light") == "night"
    rnd = random.Random(1944); SB = C.SB; SB.reset()
    sun_dir = (0.35, 0.22, 1.0) if not night else (-0.4, 0.55, 0.8)
    C.sky("night" if night else "snow", sun_dir, 0.6 if night else 0.9)
    if night: C.sun(sun_dir, 0.35, (0.6, 0.72, 1.0), 1.0)
    else: C.sun(sun_dir, 2.2, (1.0, 0.86, 0.68), 3.0)
    snow = C.snow_mat()
    MAT = dict(brick=C.brickm("stg_brick", "#8a4a3a", "#6a3424"), plank=C.planks("stg_plank", "#7a6248", "#4a3828", "Y"),
               boards=C.boards("stg_boards", "#6a5440", "#4a3a2a", 0.22, 2.8), winl=SB.window_glow("stgw", "#ffb866", 2.2), glass=pm("#26303a", 0.08),
               trim=pm("#c8c0a8", 0.6), shutter=pm("#4a5a3a", 0.6), door=pm("#5a3e28", 0.55), roof=SB.stripes("stg_roof", "#2a2a2c", "#3a3a3c", 4.0, 0),
               roof2=pm("#1e1e20", 0.7), barrel=SB.wood("#6a4a2a", "#3a2614", 6), log=C.bark_mat("stg_log", "#6a5034", "#3a2a1a"),
               snowroof=snow if night else None)
    # ================= A. the compound =================
    C.ground("ground", -72, 72, -42, 112, 0.8, H, terrain_mat(night), skip=lambda x, z: math.hypot(x - HX, z - HZ) < 0.55)
    K = Kit("camp")
    huts = [(-24, 4, "61"), (24, 4, "62"), (-24, 19, "63"), (24, 19, "103"), (-22, 33, "105"), (22, 33, "122"), (2, 33, "104")]
    for x, z, lab in huts: hut(K, x, z, 0.0, MAT, rnd, lab, night)
    # the exit hole: boarded rim, a ladder top, dark shaft
    K.cyl((HX, -1.6, HZ), 0.5, 3.2, pm("#0a0806", 1.0), 16)
    K.cyl((HX, -0.02, HZ), 0.62, 0.06, pm("#3a2e22", 0.9), 16)
    for s in (-1, 1): K.box((HX + s * 0.2, -0.3, HZ + 0.35), (0.05, 1.0, 0.05), MAT["plank"], 0, 0.005, 0.15)
    for k in range(3): K.box((HX, -0.15 - k * 0.3, HZ + 0.38 - k * 0.04), (0.42, 0.04, 0.04), MAT["plank"], 0, 0.0)
    for k in range(14):   # trampled snow + spoil around it
        a = rnd.random() * math.tau; d = rnd.uniform(0.7, 1.6)
        K.sphere((HX + d * math.cos(a), 0.0, HZ + d * math.sin(a)), rnd.uniform(0.15, 0.35), snow if k % 3 else pm("#8a7a5a", 0.9), 8, (1.0, 0.35, 1.0))
    # warning wire, double fence, coil, side fences, back fence + gate
    post = C.SB.wood("#5a4632", "#2e2218", 5, 0.8); wire = iron("#3a3634")
    for k in range(35):
        x = -45 + k * 2.65; K.box((x, 0.3, 44), (0.1, 0.6, 0.1), post, 0, 0.0)
    K.box((0, 0.55, 44), (92, 0.06, 0.06), post, 0, 0.0)
    C.wire_fence(K, [(-46, 46.5), (46, 46.5)], 2.9, post, wire, rnd, barbs=True)
    C.wire_fence(K, [(-46, 49), (46, 49)], 2.9, post, wire, rnd, barbs=False)
    C.coil(K, -45, 47.75, 45, 47.75, 0.42, wire, 2.2)
    for sx in (-1, 1): C.wire_fence(K, [(sx * 46.5, -30), (sx * 46.5, 49)], 2.9, post, wire, rnd, step=3.0, barbs=False)
    C.wire_fence(K, [(-46.5, -30), (-3, -30)], 2.9, post, wire, rnd, step=3.0, barbs=False); C.wire_fence(K, [(3, -30), (46.5, -30)], 2.9, post, wire, rnd, step=3.0, barbs=False)
    for s in (-1, 1): K.box((s * 3, 1.8, -30), (0.3, 3.6, 0.3), post, 0, 0.01)
    K.box((0, 3.7, -30), (6.6, 0.3, 0.3), post, 0, 0.01)
    TM = dict(wood=post, board=C.boards("stg_tb", "#7a6248", "#4a3828", 0.18, 1.0), roof=MAT["roof2"], snow=snow if night else None)
    sp1 = C.tower(K, -18, 51.5, 0.0, 5.0, TM, rnd); sp2 = C.tower(K, 16, 51.5, 0.0, 5.0, TM, rnd)
    C.tower(K, -40, -33, math.pi, 5.0, TM, rnd)
    # perimeter lamp poles (inside the fence), lamps lit at night
    lampg = em("#ffd8a0", 12 if night else 0.6)
    for k in range(9):
        x = -40 + k * 10; K.box((x, 2.4, 45.6), (0.12, 4.8, 0.12), post, 0, 0.0); K.box((x, 4.8, 45.35), (0.08, 0.08, 0.6), post, 0, 0)
        K.cyl((x, 4.72, 45.1), 0.22, 0.16, iron("#2a2a2a"), 12, "y", 0.05); K.cyl((x, 4.62, 45.1), 0.1, 0.06, lampg, 10)
        if night and abs(x - HX) < 26: C.lamp((x, 4.4, 45.1), 160, (1.0, 0.78, 0.5), 0.08)
    # the camp sign in the camera's foreground + a notice board
    sp = C.SB.wood("#4a3626", "#2a1c12", 5, 0.8)
    for s in (-1, 1): K.box((-9.5 + s * 1.4, 1.2, -3.5), (0.14, 2.4, 0.14), sp, 0.1, 0.01)
    sign(K, (-9.5, 2.0, -3.5), 3.2, 0.62, 0.1, "STALAG LUFT III", board="#e8e0c8", ink=pm("#1e1e22", 0.6), kind="sans", trim="#2a2a2a")
    sign(K, (-9.5, 1.45, -3.5), 3.0, 0.32, 0.1, "KRIEGSGEFANGENENLAGER", board="#e8e0c8", ink=pm("#8a1e1e", 0.6), kind="sans")
    K.box((9.5, 1.5, -2.5), (2.0, 1.3, 0.08), C.SB.wood("#6a4a2a", "#3a2614", 5), -0.15, 0.01)
    for s in (-1, 1): K.box((9.5 + s * 0.9, 0.9, -2.45), (0.1, 1.8, 0.1), sp, -0.15, 0.0)
    for k, (lines, bg) in enumerate(((["CAMP", "THEATRE", "TONIGHT"], "#e8d8b0"), (["NO", "DIGGING"], "#f0e8d8"), (["FOOTBALL", "SAT 2PM"], "#d8e0c8"))):
        a = C.poster_img([(s, 0.12) for s in lines], bg, "#2a1a14", 160, 220, seed=k)
        C.img_panel(f"notice{k}", (9.0 + k * 0.5 * math.cos(0.15), 1.55, -2.58 + k * 0.5 * math.sin(0.15)), 0.42, 0.58, a, -0.15)
    # fire pool, firewood stacks, carts, buckets, a stove-pipe smoke at night, washing lines with shirts
    K.box((-13, 0.35, 12), (5, 0.7, 3), C.concrete(), 0, 0.03); K.box((-13, 0.6, 12), (4.6, 0.04, 2.6), C.water_mat("stg_pool", "#1a2a34", "#3a4a54"), 0, 0)
    sign(K, (-13, 1.2, 10.4), 1.6, 0.4, 0.0, "FEUERLÖSCHTEICH", board="#c8202c", ink=pm("#f0ead8", 0.6), kind="sans")
    K.box((-13, 0.6, 10.42), (0.08, 1.2, 0.08), post, 0, 0)
    shirt = [pm(c, 0.9) for c in ("#c8c0b0", "#6a7a9a", "#8a6a4a", "#e8e4dc", "#4a5a7a")]
    for hx, hz in ((-24, -0.4), (24, -0.4), (-22, 28.6)):
        K.box((hx - 4, 1.0, hz), (0.08, 2.0, 0.08), post, 0, 0); K.box((hx + 4, 1.0, hz), (0.08, 2.0, 0.08), post, 0, 0)
        K.box((hx, 1.95, hz), (8, 0.015, 0.015), wire, 0, 0)
        for k in range(9): K.box((hx - 3.4 + k * 0.85 + rnd.uniform(-0.1, 0.1), 1.6, hz), (0.5, 0.65, 0.04), shirt[k % 5], rnd.uniform(-0.1, 0.1), 0.02)
    for k in range(6):
        x, z = rnd.choice([(-16, 2), (16, 2), (-16, 26), (12, 26), (-8, 30), (12, 40)]); x += rnd.uniform(-1, 1); z += rnd.uniform(-1, 1)
        K.cyl((x, 0.2, z), 0.17, 0.4, iron("#5a5a5a"), 12)
    for k in range(4):
        x, z = [(-14, 24), (14, 10), (-6, 40), (30, 26)][k]
        for j in range(12): K.cyl((x + (j % 4) * 0.3, 0.15 + (j // 4) * 0.27, z), 0.13, 1.2, MAT["log"], 8, "z", None, 0.3 * k)
    K.build()
    # pine forest all round (thick behind the north fence)
    PM = C.pine_mats(night)
    PK = Kit("pines")
    pts = []
    for k in range(560):
        x, z = rnd.uniform(-72, 72), rnd.uniform(58.5, 110)
        pts.append((x, z))
    for k in range(240):
        sx = rnd.choice((-1, 1)); pts.append((sx * rnd.uniform(52, 72), rnd.uniform(-40, 58)))
    for k in range(120): pts.append((rnd.uniform(-72, 72), rnd.uniform(-42, -34)))
    for x, z in pts:
        if abs(x - HX) < 2.5 and z < 61: continue
        h = rnd.uniform(11, 19) if z > 64 or abs(x) > 55 else rnd.uniform(7, 13)
        C.pine(PK, x, H(x, z), z, h, rnd, PM, snow=night or rnd.random() < 0.4)
    # stumps in the cleared strip + young pines at the edge
    for k in range(18):
        x, z = rnd.uniform(-44, 44), rnd.uniform(51, 58)
        if math.hypot(x - HX, z - HZ) < 2.5: continue
        PK.cyl((x, 0.2, z), rnd.uniform(0.2, 0.35), 0.4, MAT["log"], 10)
    PK.build()
    # ================= B. inside hut 104 =================
    RX = -100.0
    R = Kit("room"); fl = C.planks("stg_floor", "#8a6a48", "#5a4430", "X", 0.14, 2.0); wl = C.boards("stg_inwall", "#9a7a56", "#6a5238", 0.2, 2.6)
    for s, (x0, x1) in enumerate(((-103.5, -100.4), (-99.6, -96.5))): R.box(((x0 + x1) / 2, -0.05, 2.3), (x1 - x0, 0.1, 4.6), fl, 0, 0.0)
    R.box((RX, -0.05, 1.67), (0.8, 0.1, 3.34), fl, 0, 0.0); R.box((RX, -0.05, 4.25), (0.8, 0.1, 0.7), fl, 0, 0.0)
    R.box((RX, -1.4, 3.7), (0.9, 0.1, 0.9), pm("#2a1e14", 0.9), 0, 0.0)
    for s in (-1, 1): R.box((RX + s * 0.4, -0.7, 3.7), (0.06, 1.4, 0.8), C.planks("stg_shore", "#8a7a5a", "#5a4a30", "Z"), 0, 0)
    for k in range(5): R.box((RX, -0.2 - k * 0.25, 3.35), (0.4, 0.04, 0.05), MAT["plank"], 0, 0)
    for s in (-1, 1): R.box((RX + s * 0.22, -0.65, 3.35), (0.05, 1.3, 0.05), MAT["plank"], 0, 0)
    for (a_, b_) in ((-103.6, -102.75), (-101.65, -98.35), (-97.25, -96.4)): R.box(((a_ + b_) / 2, 1.3, 4.65), (b_ - a_, 2.8, 0.1), wl, 0, 0)
    for wx_ in (-102.2, -97.8): R.box((wx_, 0.5, 4.65), (1.1, 1.0, 0.1), wl, 0, 0); R.box((wx_, 2.35, 4.65), (1.1, 0.6, 0.1), wl, 0, 0)
    R.box((RX, 1.3, -0.1), (7.2, 2.8, 0.1), wl, 0, 0)
    R.box((-103.55, 1.3, 2.3), (0.1, 2.8, 4.8), wl, 0, 0); R.box((-96.45, 1.3, 2.3), (0.1, 2.8, 4.8), wl, 0, 0)
    R.box((RX, 2.65, 2.3), (7.2, 0.1, 4.8), C.boards("stg_ceil", "#b8a07a", "#8a7454", 0.25, 7.0), 0, 0)
    for k in range(4): R.box((RX - 3 + k * 2, 2.52, 2.3), (0.16, 0.16, 4.7), MAT["plank"], 0, 0.01)
    # windows either side of the stove (camp view beyond), blackout boards, sill clutter
    out = IK.img_mat("stg_view", IK.landscape_img(1944, 256, 192), 0.8, emit=1.2 if not night else 0.05)
    for wx in (-102.2, -97.8):
        R.box((wx, 1.55, 4.58), (1.1, 1.0, 0.03), glassm(), 0, 0)
        IK.panel(f"view{wx}", (wx, 1.55, 4.75), 1.2, 1.1, out)
        for d in (-0.55, 0.55): R.box((wx + d, 1.55, 4.55), (0.07, 1.1, 0.08), MAT["trim"], 0, 0.005)
        for d in (-0.5, 0.5): R.box((wx, 1.55 + d, 4.55), (1.15, 0.07, 0.08), MAT["trim"], 0, 0.005)
        R.box((wx, 1.55, 4.55), (0.04, 1.0, 0.05), MAT["trim"], 0, 0)
        R.box((wx, 1.02, 4.45), (1.2, 0.05, 0.2), MAT["plank"], 0, 0.005)
        for k in range(3): R.cyl((wx - 0.3 + k * 0.3, 1.1, 4.45), 0.05, 0.12, pm(["#c8a040", "#8a2a2a", "#3a5a8a"][k], 0.4, 0.5), 12)
    if not night: C.fill((RX, 1.6, 5.6), (RX, 1.0, 1.0), 260, (0.75, 0.85, 1.0), 2.5)
    # three-tier bunks on the left, straw palliasses, blankets, kit bags
    blank = [pm(c, 0.95) for c in ("#5a5a6a", "#6a4a3a", "#4a5a4a", "#7a6a5a")]
    for bz in (1.2, 3.2):
        for s in (-1, 1):
            for e in (-0.5, 0.5): R.box((-102.9 + e * 0.9, 1.15, bz + s * 0.9), (0.07, 2.3, 0.07), MAT["plank"], 0, 0)
        for t in range(3):
            y = 0.35 + t * 0.75
            R.box((-102.9, y, bz), (0.95, 0.06, 1.9), MAT["plank"], 0, 0.005); R.box((-102.9, y + 0.08, bz), (0.85, 0.12, 1.8), pm("#c8b07a", 0.95), 0, 0.03)
            R.box((-102.75, y + 0.16, bz + rnd.uniform(-0.3, 0.3)), (0.6, 0.08, 1.2), blank[(t + int(bz)) % 4], rnd.uniform(-0.1, 0.1), 0.03)
            if rnd.random() < 0.6: R.sphere((-102.6, y + 0.32, bz - 0.6), 0.16, pm("#8a7a5a", 0.9), 10, (1, 0.7, 1.4))
    # the table, benches, mugs, tins, cards, a chess board
    R.box((-100.6, 0.75, 1.6), (1.6, 0.06, 0.8), MAT["plank"], 0.05, 0.01)
    for sx in (-0.7, 0.7):
        for sz in (-0.32, 0.32): R.box((-100.6 + sx, 0.37, 1.6 + sz), (0.06, 0.74, 0.06), MAT["plank"], 0, 0)
    for sz in (-0.7, 0.7): R.box((-100.6, 0.45, 1.6 + sz), (1.6, 0.05, 0.3), MAT["plank"], 0, 0.01)
    for k in range(5): R.cyl((-101.2 + k * 0.3, 0.83, 1.5 + (k % 2) * 0.2), 0.045, 0.1, pm(["#e8e4dc", "#c8202c", "#4a6a8a", "#e8e4dc", "#c8a040"][k], 0.4, 0.4), 12)
    ck = IK.canvas(64, 64, "#f0e8d8"); x_, y_ = IK.grid(ck); IK.put(ck, ((x_ * 8).astype(int) + (y_ * 8).astype(int)) % 2 == 0, "#2a1e14")
    IK.floor_quad("chess", (-100.1, 1.75), 0.3, 0.3, IK.img_mat("stg_chess", ck, 0.4), 0.2, 0.785)
    # the right wall: shelves of Red Cross parcels and Klim tins, coats on hooks, photos and a map
    for k in range(2): R.box((-96.7, 1.3 + k * 0.5, 2.6), (0.3, 0.04, 2.0), MAT["plank"], 0, 0.005)
    rc = C.poster_img([("RED", 0.22, "#c8202c"), ("CROSS", 0.22, "#c8202c")], "#d8c8a0", "#2a1a14", 96, 72, seed=3)
    rcm = IK.img_mat("stg_rc", rc, 0.8)
    for k in range(6):
        IK.panel(f"rc{k}", (-96.86, 1.47 + (k // 3) * 0.5, 1.9 + (k % 3) * 0.5), 0.4, 0.28, rcm, -math.pi / 2)
        R.box((-96.7, 1.47 + (k // 3) * 0.5, 1.9 + (k % 3) * 0.5), (0.3, 0.28, 0.4), pm("#c8b890", 0.9), 0, 0.005)
    for k in range(4): R.cyl((-96.7, 1.38 + 0.5, 3.4 + k * 0.12), 0.05, 0.14, pm("#d8d8d0", 0.3, 0.6), 12)
    for k in range(4):
        z = 0.6 + k * 0.32; R.box((-96.55, 1.9, z), (0.08, 0.04, 0.04), brass(), 0, 0)
        R.box((-96.62, 1.45, z), (0.16, 0.85, 0.3), pm(["#4a5a7a", "#5a4a32", "#6a6a6a", "#3a4a6a"][k], 0.9), 0, 0.05)
    for k in range(3):
        IK.panel(f"photo{k}", (-101.2 + k * 0.35, 2.0, 4.58), 0.22, 0.28, IK.img_mat(f"stg_ph{k}", IK.portrait_img(70 + k, 96, 120), 0.5), 0)
    mp_ = C.poster_img([("ESCAPE", 0.1), ("COMMITTEE", 0.08), ("X", 0.25, "#8a1e1e")], "#e8dcc0", "#2a2a2a", 200, 160, seed=9)
    IK.panel("xposter", (-103.48, 1.7, 3.0), 0.7, 0.56, IK.img_mat("stg_x", mp_, 0.7), math.pi / 2)
    # the stove (rigged): tiled plinth, iron stove, kettle, pipe to the ceiling
    S = Kit("stove"); tile = C.SB.brick("stg_tile", "#c8b8a0", "#b8a890", "#6a6058", 3.0, 0.15, 0.15, 0.4)
    S.box((RX, 0.15, 3.7), (0.95, 0.3, 0.95), tile, 0, 0.01)
    S.box((RX, 0.62, 3.7), (0.6, 0.65, 0.5), iron("#2a2626"), 0, 0.02); S.box((RX, 0.96, 3.7), (0.66, 0.05, 0.56), iron("#3a3434"), 0, 0.01)
    S.box((RX, 0.55, 3.44), (0.3, 0.25, 0.02), em("#ff7a2a", 3.0), 0, 0)
    S.cyl((RX + 0.12, 1.04, 3.62), 0.1, 0.13, pm("#8a8a86", 0.3, 0.7), 14)
    S.cyl((RX, 1.8, 3.82), 0.06, 1.6, iron("#2a2626"), 12)
    so = S.build(); STOVE = C.rig(so, (RX, 0, 3.7))
    C.lamp((RX, 0.7, 3.3), 25, (1.0, 0.5, 0.2), 0.1)
    R.cyl((RX - 0.5, 2.2, 2.0), 0.012, 0.6, pm("#1a1a1a", 0.6), 4); R.cyl((RX - 0.5, 1.88, 2.0), 0.05, 0.08, em("#ffe0b0", 20), 10)
    C.lamp((RX - 0.5, 1.8, 2.0), 70 if not night else 110, (1.0, 0.72, 0.42), 0.05)
    C.fill((RX + 1.0, 1.8, -0.0), (RX, 1.0, 3.0), 60, (1.0, 0.86, 0.7), 2.0)
    R.build()
    # ================= C. the cutaway diorama =================
    bpy.ops.mesh.primitive_cube_add(location=T(DX + 38, -5.0, 6.0)); E = bpy.context.object; E.name = "earth"
    E.scale = (39, 6, 5.0); bpy.ops.object.transform_apply(scale=True)
    em_ = lib.principled("stg_earth", lib.hexc("#b08a50"), 0.95); t, n, l = lib.nodes(em_)
    tc = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sep.inputs[0])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.8; nz.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    zr = n.new("ShaderNodeMapRange"); zr.inputs["From Min"].default_value = -5.0; zr.inputs["From Max"].default_value = 5.0; l.new(sep.outputs["Z"], zr.inputs["Value"])
    ad = n.new("ShaderNodeMath"); ad.operation = "MULTIPLY_ADD"; ad.inputs[1].default_value = 0.07; l.new(nz.outputs["Fac"], ad.inputs[0]); l.new(zr.outputs["Result"], ad.inputs[2])
    rr = lib.ramp(n, l, ad.outputs[0], [(0.0, lib.hexc("#a8804a")), (0.2, lib.hexc("#b8925a")), (0.24, lib.hexc("#7a5a34")), (0.3, lib.hexc("#c8a060")), (0.5, lib.hexc("#9a7444")), (0.56, lib.hexc("#b08a52")), (0.8, lib.hexc("#8a6a40"))])
    ga = n.new("ShaderNodeMapRange"); ga.inputs["From Min"].default_value = 3.6; ga.inputs["From Max"].default_value = 4.2; l.new(sep.outputs["Z"], ga.inputs["Value"])
    top = n.new("ShaderNodeMix"); top.data_type = "RGBA"; l.new(ga.outputs["Result"], top.inputs[0]); l.new(rr.outputs["Color"], top.inputs[6]); top.inputs[7].default_value = (*lib.hexc("#3a2e22"), 1)
    fine = n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 18; l.new(tc.outputs["Object"], fine.inputs["Vector"])
    mu = n.new("ShaderNodeMix"); mu.data_type = "RGBA"; mu.blend_type = "MULTIPLY"; mu.inputs[0].default_value = 0.3; l.new(top.outputs[2], mu.inputs[6]); l.new(fine.outputs["Color"], mu.inputs[7])
    l.new(mu.outputs[2], n["Principled BSDF"].inputs["Base Color"]); lib.bump(n, l, fine.outputs["Fac"], 0.5, 0.03)
    E.data.materials.append(em_)
    TUN = [("TOM", -3.0, DX + 4, DX + 31), ("DICK", -5.0, DX + 11, DX + 26), ("HARRY", -7.4, DX + 19, DX + 58)]
    cutters = []
    def cut(c, s):
        bpy.ops.mesh.primitive_cube_add(location=T(*c)); o = bpy.context.object; o.scale = (s[0] / 2, s[2] / 2, s[1] / 2); bpy.ops.object.transform_apply(scale=True)
        cutters.append(o); return o
    for name, y, x0, x1 in TUN:
        cut(((x0 + x1) / 2, y + 0.7, 0.3), (x1 - x0, 1.4, 2.6))
        cut((x0 + 0.5, y / 2 + 0.7, 0.3), (1.0, -y + 1.6, 2.6))
    cut((DX + 58.5, -3.7, 0.3), (1.0, 7.6, 2.6))
    for cx in (DX + 32, DX + 45): cut((cx, -7.4 + 1.0, 0.3), (2.4, 2.0, 2.6))
    cut((DX + 21, -7.4 + 1.0, 0.3), (2.6, 2.0, 2.6))
    un = cutters[0]
    for o in cutters[1:]:
        md = un.modifiers.new("u", "BOOLEAN"); md.operation = "UNION"; md.object = o
    bpy.context.view_layer.objects.active = un
    for md in list(un.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)
    for o in cutters[1:]: bpy.data.objects.remove(o, do_unlink=True)
    md = E.modifiers.new("cut", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = un
    bpy.context.view_layer.objects.active = E; bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(un, do_unlink=True)
    U = Kit("tunnels"); shore = C.planks("stg_bedb", "#a88a5a", "#6a5434", "Z", 0.12, 1.0); rail = iron("#4a4a4a")
    bulb = em("#ffe2a8", 30); cab = pm("#1a1a1a", 0.6)
    for name, y, x0, x1 in TUN:
        x = x0 + 1.2
        while x < x1 - 0.3:
            for zz in (0.12, 1.55): U.box((x, y + 0.7, zz), (0.1, 1.4, 0.1), shore, 0, 0.005)
            U.box((x, y + 1.35, 0.85), (0.12, 0.1, 1.6), shore, 0, 0.005)
            x += 0.9
        U.box(((x0 + x1) / 2, y + 0.04, 0.85), (x1 - x0, 0.06, 1.5), shore, 0, 0)
        U.box(((x0 + x1) / 2, y + 1.38, 1.0), (x1 - x0 - 1, 0.012, 0.012), cab, 0, 0)
        x = x0 + 2
        while x < x1:
            U.cyl((x, y + 1.28, 1.0), 0.045, 0.09, bulb, 10); x += 3.0
        for k in range(int((x1 - x0 - 1) / 6)): C.lamp((x0 + 3 + k * 6, y + 1.1, 0.8), 25, (1.0, 0.75, 0.45), 0.05)
        # rails + sleepers
        for zz in (0.6, 1.1): U.box(((x0 + x1) / 2 + 0.5, y + 0.12, zz), (x1 - x0 - 1.2, 0.04, 0.03), rail, 0, 0)
        for k in range(int((x1 - x0 - 1.2) / 0.5)): U.box((x0 + 1.0 + k * 0.5, y + 0.09, 0.85), (0.08, 0.03, 0.75), shore, 0, 0)
        # ladder up the shaft + the name board at the foot
        for k in range(int(-y / 0.35)): U.box((x0 + 0.5, y + 0.3 + k * 0.35, 0.5), (0.5, 0.04, 0.05), shore, 0, 0)
        for s in (-1, 1): U.box((x0 + 0.5 + s * 0.24, y / 2 + 0.6, 0.5), (0.05, -y + 1.2, 0.05), shore, 0, 0)
        sign(U, (x0 + 2.2, y + 1.0, 0.02), 1.4, 0.42, 0.0, name, board="#2a1e14", ink=pm("#f2e8c8", 0.6), kind="sans", trim="#8a6a3a")
    # trolleys on HARRY, chambers PICCADILLY / LEICESTER SQ., the air pump with its tin-can pipe
    y = -7.4
    for tx in (DX + 27.0, DX + 39.5, DX + 52.0):
        U.box((tx, y + 0.26, 0.85), (1.1, 0.08, 0.6), shore, 0, 0.01)
        for e in (-0.4, 0.4):
            for zz in (0.6, 1.1): U.cyl((tx + e, y + 0.2, zz), 0.08, 0.04, rail, 10, "z")
        U.box((tx + 0.5, y + 0.4, 0.85), (0.04, 0.25, 0.6), shore, 0, 0)
        U.cyl((tx + 0.6, y + 0.32, 0.85), 0.015, 3.0, pm("#c8b890", 0.9), 4, "x")
    for cx, nm in ((DX + 32, "PICCADILLY"), (DX + 45, "LEICESTER SQ.")):
        sign(U, (cx, y + 1.75, 0.02), 2.2, 0.36, 0.0, nm, board="#c8202c", ink=pm("#f8f0e0", 0.6), kind="sans", trim="#f0e8d8")
        for k in range(5): U.box((cx - 0.9 + k * 0.45, y + 0.3, 1.4), (0.35, 0.5, 0.3), pm("#8a7a5a", 0.95), 0.1 * k, 0.06)
    px = DX + 21
    U.box((px, y + 0.35, 1.2), (1.2, 0.5, 0.6), pm("#5a4a3a", 0.9), 0, 0.02)
    for k in range(4): U.box((px - 0.1 + k * 0.08, y + 0.55, 1.2), (0.05, 0.5, 0.62), pm("#3a3028", 0.9), 0, 0.01)
    U.box((px - 0.9, y + 0.35, 1.0), (0.5, 0.06, 0.4), shore, 0, 0)
    U.cyl((px - 0.3, y + 0.9, 1.0), 0.025, 0.9, shore, 6, "x")
    for k in range(int((DX + 57 - px) / 0.22)): U.cyl((px + 0.8 + k * 0.22, y + 0.12, 1.48), 0.07, 0.21, pm("#c8c8c0", 0.3, 0.6), 10, "x")
    sign(U, (px, y + 1.15, 1.48), 0.9, 0.24, 0.0, "AIR PUMP", board="#e8e0c8", ink=pm("#2a2a2a", 0.6), kind="sans")
    U.build()
    # the surface above the diorama: snowy strip, huts (cut), fence, tower, pines
    D2 = Kit("dtop")
    for x, lab in ((DX + 4.5, "123"), (DX + 11.5, "122"), (DX + 19.5, "104")): hut(D2, x, 4.6, 0.0, MAT, rnd, lab, night, 6.0, 4.0)
    C.wire_fence(D2, [(DX + 49, 0.5), (DX + 49, 12)], 2.9, post, wire, rnd, barbs=True)
    C.wire_fence(D2, [(DX + 51.5, 0.5), (DX + 51.5, 12)], 2.9, post, wire, rnd, barbs=False)
    C.coil(D2, DX + 50.25, 0.6, DX + 50.25, 11, 0.42, wire, 2.2)
    C.tower(D2, DX + 54, 8, -math.pi / 2, 5.0, TM, rnd)
    for k in range(40):
        x = DX + 61 + rnd.uniform(0, 16); z = rnd.uniform(0.6, 12)
        C.pine(D2, x, 0, z, rnd.uniform(8, 14), rnd, PM, snow=night or rnd.random() < 0.4)
    D2.box((DX + 58.5, 0.03, 0.5), (1.2, 0.06, 1.2), pm("#3a2e22", 0.9), 0, 0.01)
    D2.build()
    C.fill((DX + 30, -2, -12), (DX + 30, -5, 0), 700, (0.8, 0.86, 1.0), 30, 8)
    # fills for the compound: warm bounce from the camera side, cool sky fill; night: searchlights
    if not night:
        C.fill((0, 12, -24), (2, 1, 20), 9000, (1.0, 0.9, 0.78), 30)
        C.fill((HX, 6, HZ - 14), (HX, 0, HZ), 1200, (0.8, 0.88, 1.0), 10)
    else:
        C.fill((0, 14, -20), (2, 1, 30), 1500, (0.55, 0.65, 1.0), 40)
        for k, (sp_, tgt) in enumerate(((sp1, (-6, 0, 24)), (sp2, (HX + 0.3, 0, HZ - 0.3)))):
            o = IK.spot(sp_, tgt, 60000, (1.0, 0.96, 0.85), 7, 0.4, 0.15)
            C.beam_cone(f"sbeam{k}", sp_, tgt, 2.6, (1.0, 0.95, 0.82), 0.06, 48)
        C.lamp((HX, 1.0, HZ - 1.5), 60, (0.75, 0.85, 1.0), 0.3)
    def update(f):
        if STOVE is None: return
        u = max(0.0, min(1.0, (f - 252) / 24.0)); u = u * u * (3 - 2 * u)
        STOVE.location = T(RX + 0.95 * u, 0.42 * math.sin(math.pi * min(1.0, u * 1.2)) * 1.0, 3.7 - 0.25 * u)
    return {"update": update}
