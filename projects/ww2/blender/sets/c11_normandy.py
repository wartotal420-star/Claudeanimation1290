# Normandy, June 1944 (chapter 11: the Atlantic Wall before D-Day, the invasion fleet, Omaha beach, the end of the day).
# Layout (three coords, the sea toward -z, the beach facing north = -z):
#  - sea level y 0 for z < 0; the beach rises y = 0.04 z (z 0..36, keep it exactly so: characters stand on it),
#    a shingle bank z 33..38, the bluffs z 40..72 up to y ~24, the plateau z > 72 (hedgerows, farmhouses, a church).
#  - Keep clear (soldiers): the beach x -12..14, z 3..30 apart from the hedgehogs listed in HOG (stand behind them,
#    i.e. at z + 0.8); the draw path up the bluff x 2..8, z 38..70 (small groups climbing; y = H(x, z)).
#  - The hero Higgins boat (LCVP) at (3, 0, -30), bow +z, deck y 0.15, ramp hinge z -24.9 (update() drops the ramp at
#    ch11 frames 2546..2560); troops stand in it at x 1.8..4.2, z -34..-26.
#  - The sinking DD tank at (13, -1.3, -16), a burning landing craft at (-13, 0, 1).
#  - The bunker (casemate "WN 62") on the bluff at (-20, 24, 62): its room inside x -22.5..-17.5, z 62..66, floor y 24,
#    ceiling 26.4, the embrasure (x -21.1..-18.9, y 25.0..25.55) looks out to sea; officer stands at (-20, 24, 62.9),
#    the camera can sit at (-18.4, 25.5, 65.6). The wall map of the Channel hangs on the room's right wall (x -17.55).
#  - The invasion fleet (z -60..-1400) only exists from ch11 frame 1975 on (update hides it before D-Day).
# Light: day (before), golden = D-Day dawn (low sun from the east, +x), dusk = end of the day (sun west), interior.
import bpy, math, random, os
from mathutils import Vector, Matrix
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, glassm
from sets import ikit as IK
from sets import front as FR
from sets.void import lathe, tube, worn, mat_once, fire, smoke_mat, smoke_column
from sets.warroom import phone

HOG = [(-9, 9), (-4.5, 11), (0.5, 9.5), (5.5, 12), (10, 9), (-7, 16), (2.5, 17), (8, 18.5), (-11, 21), (12.5, 15), (-2, 22), (6, 25)]
BX, BY, BZ = -20.0, 24.0, 62.0
FLEET = []; RAMP = None

def H(x, z):
    if z < 36: return max(-4.0, 0.04 * z) if z > -100 else -4.0
    b = 1.44 + (z - 36) * 0.06
    if z > 38:
        u = min(1.0, (z - 40) / 32.0); u = max(0.0, u)
        draw = math.exp(-((x - 5) / 6.0) ** 2) * 0.35 + math.exp(-((x + 42) / 9.0) ** 2) * 0.5
        b = 1.56 + 23.0 * (u * u * (3 - 2 * u)) * (1 - draw * (1 - u)) + 1.2 * C.nz2(x, z, 0.08, 4.0) * u
        if z > 72: b = 24.6 + 0.8 * C.nz2(x, z, 0.05, 7.0)
    if abs(x - BX) < 5.5 and 57 < z < 70: b = min(b, BY - 0.05) if z > 61 else b
    return b

def build(M, D):
    global RAMP
    light = D.get("light", "golden"); rnd = random.Random(66); C.SB.reset()
    kind = {"golden": "dawn", "dusk": "dusk", "day": "day", "interior": "day", "grey": "grey"}.get(light, "dawn")
    sun_dir = {"dawn": (1.0, 0.16, -0.35), "dusk": (-1.0, 0.12, -0.4), "day": (0.6, 0.6, -0.5), "grey": (0.4, 0.7, -0.4)}[kind]
    C.sky(kind, sun_dir, 0.9)
    C.sun(sun_dir, {"dawn": 3.2, "dusk": 3.0, "day": 3.6, "grey": 1.8}[kind], C.SKIES[kind]["sun"], 2.0)
    # ---------- terrain: sea bed, beach, shingle, bluffs, plateau ----------
    gm = C.grass_mat("nm_grass", "#5a7a2c", "#8a9a3e", "#b8a868")
    sand = C.sand_mat("nm_sand", "#c8b086", "#a8906a")
    def tm():
        m = lib.principled("nm_ground", lib.hexc("#c8b086"), 0.8); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); sp = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sp.inputs[0])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.15; nz.inputs["Detail"].default_value = 6; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        hv = n.new("ShaderNodeMath"); hv.operation = "MULTIPLY_ADD"; hv.inputs[1].default_value = 0.6; l.new(nz.outputs["Fac"], hv.inputs[0]); l.new(sp.outputs[2], hv.inputs[2])
        r = lib.ramp(n, l, hv.outputs[0], [(0.0, lib.hexc("#4a4436")), (0.3, lib.hexc("#8a7a5a")), (0.55, lib.hexc("#c2aa80")), (1.5, lib.hexc("#d4c09a")),
                                             (1.75, lib.hexc("#7a7466")), (2.1, lib.hexc("#8a8a58")), (3.0, lib.hexc("#6a8a34")), (6.0, lib.hexc("#5a7a2c"))])
        fine = n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 4; fine.inputs["Detail"].default_value = 8; l.new(tc.outputs["Object"], fine.inputs["Vector"])
        mu = n.new("ShaderNodeMix"); mu.data_type = "RGBA"; mu.blend_type = "MULTIPLY"; mu.inputs[0].default_value = 0.3; l.new(r.outputs["Color"], mu.inputs[6]); l.new(fine.outputs["Color"], mu.inputs[7])
        l.new(mu.outputs[2], b.inputs["Base Color"])
        vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 9; l.new(tc.outputs["Object"], vo.inputs["Vector"])
        lib.bump(n, l, vo.outputs["Distance"], 0.25, 0.04)
        wet = lib.ramp(n, l, hv.outputs[0], [(0.25, (0.2, 0.2, 0.2)), (0.6, (0.85, 0.85, 0.85))], (-200, -300)); l.new(wet.outputs["Color"], b.inputs["Roughness"])
        return m
    C.ground("ground", -110, 110, -40, 160, 0.9, H, mat_once("nm_ground", tm))
    sea = C.water_mat("nm_sea", "#14303c", "#3a6670", 0.06)
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, 0.0, -1000)); so = bpy.context.object; so.scale = (4000, 2000, 1); bpy.ops.object.transform_apply(scale=True); so.data.materials.append(sea)
    foam = mat_once("nm_foam", FR.foam_mat)
    for k in range(5):
        bpy.ops.mesh.primitive_plane_add(size=1, location=T(rnd.uniform(-3, 3), 0.02, -0.8 - k * 3.2)); fo = bpy.context.object; fo.scale = (240, 0.9 + k * 0.2, 1); bpy.ops.object.transform_apply(scale=True); fo.data.materials.append(foam)
    K = Kit("beach")
    # ---------- beach obstacles: hedgehogs, log ramps with mines, wire, craters, wreckage ----------
    steel = mat_once("nm_steel", lambda: worn("nm_steel", "#4a3a30", "#7a3a1a", 0.7, 0.5, 6, 0.55, "#2a1a10"))
    for k, (x, z) in enumerate(HOG): FR.hedgehog(f"hog{k}", (x, H(x, z) - 0.15, z), k * 0.7 + 0.3, steel)
    for k in range(40):
        x, z = rnd.uniform(-100, 100), rnd.uniform(-6, 30)
        if -13 < x < 15 and 2 < z < 31: continue
        FR.hedgehog(f"hogx{k}", (x, H(x, z) - 0.15, z), rnd.random() * 3, steel)
    logm = C.bark_mat("nm_log", "#5a4a36", "#2a2018"); mine = iron("#3a3a34")
    for k in range(26):
        x, z = rnd.uniform(-100, 100), rnd.uniform(-10, 4)
        if abs(x - 3) < 3 and z < 0: continue
        K.cyl((x, H(x, z) + 1.3, z), 0.13, 3.2, logm, 8, "y", None, 0, 0, -0.65)
        K.cyl((x, H(x, z) + 2.5, z - 1.0), 0.18, 0.12, mine, 12, "y", None, 0, -0.65)
    wire = iron("#3a3634")
    for k in range(6): C.coil(K, -100 + k * 34, 38.6, -80 + k * 34, 38.6, 0.45, wire, 2.0, H(0, 38.6) - 0.05)
    # the shingle bank with a low sea wall stretch
    for k in range(260):
        x, z = rnd.uniform(-100, 100), rnd.uniform(33, 38)
        K.sphere((x, H(x, z), z), rnd.uniform(0.08, 0.2), pm(rnd.choice(["#8a8478", "#6a665e", "#a49c8c", "#5a564e"]), 0.6), 6, (1, 0.6, 1))
    # wreckage on the sand: a burning landing craft, a stranded jeep, crates, life vests, an abandoned helmet line
    LM = dict(hull=worn("nm_hull", "#5a6a5e", "#3a4038", 0.7, 0.1, 3, 0.62, "#3a3a2a"), inside=C.planks("nm_deck", "#7a6a50", "#4a3e2e", "Y"),
              steel=mat_once("nm_lsteel", lambda: worn("nm_lsteel", "#5a5e5a", "#3a3a36", 0.5, 0.6, 12, 0.6)), ramp_in=pm("#4a4e48", 0.6))
    C.lcvp(K, -13, 0.0, 1.0, 0.3, 1.0, LM, rnd, "PA 13-21")
    fire("lcfire", (-13.5, 1.2, 0.0), 1.4, seed=4, energy=2200)
    smm = mat_once("nm_smoke", lambda: smoke_mat("nm_smoke", "#2a2420", 0.42))
    smoke_column("lcsmoke", (-13.5, 3.0, 0.5), 22, 1.0, 4.0, smm, drift=(-14, 6), seed=6, puffs=12)
    JM = dict(body=worn("nm_jeep", "#5a603e", "#3a3a2a", 0.6, 0.2, 6, 0.65), tyre=pm("#1a1a1a", 0.85), seat=C.SB.cloth("#4a4a32"))
    C.jeep(K, 15.5, 7.5, -0.6, JM)
    for k in range(10):
        x, z = rnd.uniform(-12, 15), rnd.uniform(2, 30)
        if any(math.hypot(x - hx, z - hz) < 1.6 for hx, hz in HOG): continue
        K.box((x, H(x, z) + 0.15, z), (0.6, 0.3, 0.4), C.SB.wood("#7a6a42", "#4a3a22", 10), rnd.random() * 3, 0.02)
    for k in range(14):
        x, z = rnd.uniform(-12, 15), rnd.uniform(2, 30)
        K.sphere((x, H(x, z) + 0.06, z), 0.17, pm("#5a5e3e", 0.4, 0.3), 10, (1, 0.5, 1))
    for k in range(8):
        x, z = rnd.uniform(-40, 40), rnd.uniform(6, 32)
        K.cyl((x, H(x, z) - 0.05, z), rnd.uniform(1.0, 1.8), 0.14, pm("#3a3428", 0.9), 16)
    # the DD tank going down, its canvas screen collapsing, bubbles
    tk = C.tank_at("dd", 13, -1.25, -16, math.pi / 2 + 0.25, "#58603c", "white", tilt=-0.18)
    K.cyl((13, 0.3, -16), 2.0, 1.6, C.SB.cloth("#7a7458"), 20, "y", 1.6)
    for k in range(9): K.sphere((13 + rnd.uniform(-2, 2), 0.02, -16 + rnd.uniform(-2, 2)), rnd.uniform(0.1, 0.3), foam, 8, (1, 0.4, 1))
    # ---------- the hero LCVP (ramp rigged) + a wave of boats behind it ----------
    HK = Kit("hero"); P = C.lcvp(HK, 3, 0.0, -30, 0.0, None, LM, rnd, "PA 26-17"); HK.build()
    RK = Kit("ramp"); Lh, Hs = 10.4, 1.65
    hr = Hs + 0.25; hz = -30 + Lh / 2 - 0.1
    RK.box((3, -0.1 + hr / 2, hz), (3.05, hr, 0.14), LM["steel"], 0, 0.02)
    for k in range(5): RK.box((3 - 0.9 + k * 0.45, -0.1 + hr / 2, hz - 0.08), (0.08, hr * 0.95, 0.06), LM["ramp_in"], 0, 0.0)
    RAMP = C.rig(RK.build(), (3, -0.1, hz))
    for k in range(14):
        x, z = -60 + k * 9 + rnd.uniform(-3, 3), -60 - rnd.uniform(0, 140)
        C.lcvp(K, x, 0.0, z, rnd.uniform(-0.15, 0.15), 0.0, LM, rnd, "")
        K.quad([(x - 1.2, 0.03, z - 5.0), (x + 1.2, 0.03, z - 5.0), (x + 3.0, 0.03, z - 22), (x - 3.0, 0.03, z - 22)], foam)
    for k in range(6):
        x, z = [(-7, -12), (8, -20), (-20, -26), (18, -36), (-3, -48), (11, -44)][k]
        C.lcvp(K, x, 0.0, z, rnd.uniform(-0.2, 0.2), 0.0, LM, rnd, "")
        K.quad([(x - 1.2, 0.03, z - 5.0), (x + 1.2, 0.03, z - 5.0), (x + 2.4, 0.03, z - 16), (x - 2.4, 0.03, z - 16)], foam)
    # ---------- the bluff defences: the casemate with its room, trenches, an MG nest, wire, mine signs ----------
    conc = C.concrete("nm_conc", "#8e887a")
    B = Kit("bunker")
    x0, x1, z0, z1, y0, y1 = BX - 2.5, BX + 2.5, BZ, BZ + 4.0, BY, BY + 2.4
    B.box((BX, y0 - 0.15, BZ + 2), (6.8, 0.3, 5.8), conc, 0, 0.02)
    B.box((BX, y1 + 0.45, BZ + 2), (7.0, 0.9, 6.0), conc, 0, 0.08)
    B.box((x0 - 0.4, (y0 + y1) / 2, BZ + 2), (0.8, y1 - y0, 5.6), conc, 0, 0.0); B.box((x1 + 0.4, (y0 + y1) / 2, BZ + 2), (0.8, y1 - y0, 5.6), conc, 0, 0.0)
    B.box((BX, (y0 + y1) / 2, z1 + 0.4), (6.6, y1 - y0, 0.8), conc, 0, 0.0)
    sx0, sx1, sy0, sy1 = BX - 1.1, BX + 1.1, BY + 1.0, BY + 1.55
    B.box((BX, (y0 + sy0) / 2, BZ - 0.4), (6.6, sy0 - y0, 0.8), conc, 0, 0.0); B.box((BX, (sy1 + y1) / 2, BZ - 0.4), (6.6, y1 - sy1, 0.8), conc, 0, 0.0)
    B.box(((x0 - 0.8 + sx0) / 2, (sy0 + sy1) / 2, BZ - 0.4), (sx0 - x0 + 0.8, sy1 - sy0, 0.8), conc, 0, 0.0)
    B.box(((sx1 + x1 + 0.8) / 2, (sy0 + sy1) / 2, BZ - 0.4), (x1 + 0.8 - sx1, sy1 - sy0, 0.8), conc, 0, 0.0)
    for s in (-1, 1): B.box((BX + s * 1.6, BY + 1.27, BZ - 1.0), (0.3, 1.1, 0.6), conc, s * 0.5, 0.02)
    B.box((BX, BY + 2.9, BZ - 0.95), (5.0, 0.3, 0.7), conc, 0, 0.03)
    text("WN 62", (BX + 2.2, BY + 2.0, BZ - 0.81), 0.3, pm("#e8e0c8", 0.8), 0, "sans", 0.002)
    net = C.SB.cloth("#4a4a2a")
    for k in range(8): B.sphere((BX + rnd.uniform(-3, 3), BY + 3.4, BZ + rnd.uniform(0, 4)), rnd.uniform(0.6, 1.1), net if k % 2 else C.foliage_mat("nm_bush", "#4a6a2a", "#24401a"), 10, (1.4, 0.5, 1.2))
    # room inside: floor boards, caged bulb, MG on its mount at the slit, field phone, periscope, ammo, bunks, helmets
    B.box((BX, y0 + 0.02, BZ + 2), (5.0, 0.04, 4.0), C.planks("nm_bfl", "#6a5a44", "#3a3024", "X"), 0, 0)
    B.box((BX, y1 - 0.05, BZ + 2), (5.0, 0.04, 4.0), C.plaster("nmb", "#a8a294"), 0, 0)
    B.cyl((BX + 0.6, y1 - 0.25, BZ + 2.0), 0.06, 0.12, em("#ffe2b0", 22), 12)
    for k in range(3): B.torus((BX + 0.6, y1 - 0.25, BZ + 2.0), 0.08, 0.008, iron(), 12, 4, "x", k * 1.0)
    C.lamp((BX + 0.6, y1 - 0.4, BZ + 2.0), 90, (1.0, 0.72, 0.42), 0.05)
    mgm = iron("#2a2a2a")
    B.box((BX + 0.7, y0 + 0.55, BZ + 0.5), (0.5, 1.1, 0.5), conc, 0, 0.02)
    B.cyl((BX + 0.7, y0 + 1.2, BZ + 0.2), 0.03, 1.0, mgm, 8, "z"); B.box((BX + 0.7, y0 + 1.2, BZ + 0.75), (0.1, 0.14, 0.4), mgm, 0, 0.01)
    B.box((BX + 0.7, y0 + 1.12, BZ + 1.0), (0.06, 0.1, 0.3), C.SB.wood("#6a4a2a", "#3a2614", 8), 0, 0.01)
    B.box((BX + 2.3, y0 + 1.0, BZ + 2.6), (0.3, 0.04, 1.4), C.SB.wood("#6a4a2a", "#3a2614", 8), 0, 0.01)
    B.box((BX + 2.25, y0 + 1.15, BZ + 2.2), (0.22, 0.26, 0.32), pm("#3a4a32", 0.6), 0, 0.02)
    B.cyl((BX + 2.25, y0 + 1.33, BZ + 2.1), 0.04, 0.08, pm("#141414", 0.3), 10, "z")
    B.cyl((BX - 0.9, y0 + 1.4, BZ + 0.3), 0.05, 1.8, iron("#4a4e48"), 10); B.box((BX - 0.9, y0 + 2.3, BZ + 0.3), (0.12, 0.14, 0.12), iron("#4a4e48"), 0, 0.01)
    for k in range(5): B.box((BX - 2.1 + (k % 3) * 0.32, y0 + 0.13 + (k // 3) * 0.27, BZ + 0.6), (0.3, 0.26, 0.18), pm("#4a5236", 0.7), 0, 0.02)
    for t in range(2):
        B.box((BX - 1.9, y0 + 0.5 + t * 0.9, BZ + 3.2), (1.0, 0.06, 1.6), C.SB.wood("#7a5a3a", "#4a3020", 6), 0, 0.01)
        B.box((BX - 1.9, y0 + 0.58 + t * 0.9, BZ + 3.2), (0.9, 0.1, 1.5), pm("#5a5a4a", 0.95), 0, 0.03)
    for k in range(3): B.sphere((BX - 2.38, y0 + 1.7, BZ + 1.2 + k * 0.35), 0.14, mat_once("nm_helm", lambda: worn("nm_helm", "#4c5448", "#2a2e28", 0.5, 0.2, 10, 0.6)), 12, (1, 0.7, 1.1))
    cal = C.poster_img([("JUNI", 0.14, "#8a1e1e"), ("1944", 0.14), ("1 2 3 4 5", 0.07), ("6 7 8 9", 0.07)], "#f0e8d4", "#2a2a2a", 120, 160, seed=5)
    IK.panel("cal", (BX - 2.47, y0 + 1.6, BZ + 2.4), 0.3, 0.4, IK.img_mat("nm_cal", cal, 0.8), -math.pi / 2)
    cm = IK.img_mat("nm_chmap", bpy.data.images.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps", "c11_channel.png")), 0.7)
    IK.framed("bmap", (BX + 2.45, y0 + 1.5, BZ + 2.2), 1.9, 1.15, cm, C.SB.wood("#4a2c18", "#24140a", 5), math.pi / 2, 0.05, 0.03)
    B.box((BX + 2.47, y0 + 1.5, BZ + 2.2), (0.04, 1.25, 2.0), C.SB.cloth("#5a4a32"), 0, 0.0)
    # clutter: shelf with mess tins and a radio, rifle rack, coats on hooks, a stool, a card table, a stove, sandbags at the slit
    wd = C.SB.wood("#6a4a2a", "#3a2614", 8)
    B.box((BX - 2.38, y0 + 1.25, BZ + 3.0), (0.24, 0.04, 1.6), wd, 0, 0.005)
    for k in range(5): B.cyl((BX - 2.38, y0 + 1.33, BZ + 2.4 + k * 0.28), 0.07, 0.12, pm(["#6a6e5e", "#8a8a80", "#5a5e50"][k % 3], 0.4, 0.6), 12)
    B.box((BX - 2.3, y0 + 0.9, BZ + 1.95), (0.3, 0.06, 0.8), wd, 0, 0.005)
    for k in range(4): B.box((BX - 2.3, y0 + 0.62, BZ + 1.7 + k * 0.17), (0.04, 1.25, 0.06), wd, 0, 0.0, 0, 0.05)
    for k in range(3): B.box((BX + 1.5 + k * 0.32, y0 + 1.5, BZ + 3.88), (0.28, 0.75, 0.12), pm(["#5e6658", "#4c5448", "#5a6054"][k], 0.9), 0, 0.04)
    B.box((BX + 0.2, y0 + 0.72, BZ + 2.6), (0.9, 0.05, 0.6), wd, 0, 0.01)
    for sx in (-0.4, 0.4):
        for sz in (-0.25, 0.25): B.box((BX + 0.2 + sx, y0 + 0.36, BZ + 2.6 + sz), (0.05, 0.72, 0.05), wd, 0, 0)
    for k in range(5): B.box((BX + 0.05 + k * 0.08, y0 + 0.755, BZ + 2.55 + (k % 2) * 0.1), (0.06, 0.004, 0.09), pm("#f0ece0", 0.6), 0.3 * k, 0)
    B.cyl((BX + 0.5, y0 + 0.8, BZ + 2.75), 0.04, 0.1, pm("#4a5a3a", 0.4, 0.4), 10)
    B.cyl((BX - 0.5, y0 + 0.3, BZ + 3.3), 0.2, 0.06, wd, 12); B.cyl((BX - 0.5, y0 + 0.15, BZ + 3.3), 0.03, 0.3, wd, 6)
    B.box((BX + 1.9, y0 + 0.4, BZ + 3.5), (0.5, 0.8, 0.5), iron("#2a2a2a"), 0, 0.02); B.cyl((BX + 1.9, y0 + 1.6, BZ + 3.6), 0.06, 1.6, iron("#2a2a2a"), 8)
    C.sandbags(B, BX - 0.6, y0, BZ + 0.3, 0.0, 3, 2, C.sandbag_m(), rnd)
    sg2 = C.poster_img([("FEIND", 0.14, "#8a1e1e"), ("HÖRT", 0.14, "#8a1e1e"), ("MIT!", 0.14, "#8a1e1e")], "#e8dcc0", "#1e1e1e", 120, 160, seed=12)
    IK.panel("nm_post", (BX - 1.4, y0 + 1.6, BZ + 3.88), 0.45, 0.6, IK.img_mat("nm_postm", sg2, 0.8), 0.0)
    C.fill((BX, BY + 1.3, BZ + 3.6), (BX, BY + 1.0, BZ), 50, (1.0, 0.82, 0.6), 2.0)
    C.fill((BX, BY + 1.3, BZ - 1.4), (BX, BY + 1.2, BZ + 3.0), 60, (0.8, 0.88, 1.0), 2.0, 0.5)
    B.build()
    # trench line + sandbags + the MG nest on the bluff top; tobruks; mine signs; wire along the bluff foot
    sb = C.sandbag_m()
    for k in range(9):
        x = -50 + k * 12; z = 70 + 2 * math.sin(k)
        C.sandbags(K, x, H(x, z) - 0.1, z - 0.6, 0.1 * math.sin(k * 2), 6, 2, sb, rnd)
    C.sandbags(K, 9, H(9, 66) - 0.1, 65.4, 0.0, 6, 3, sb, rnd, 0.15)
    K.cyl((9.2, H(9, 66) + 0.75, 64.6), 0.03, 1.1, iron("#1a1a1a"), 8, "z")
    for k, x in enumerate((-60, -34, 22, 40, 58)):
        z = 41.5 + (k % 2); y = H(x, z)
        K.box((x, y + 0.8, z), (0.08, 1.6, 0.08), C.SB.wood("#6a4a2a", "#3a2614", 8), 0, 0)
        sign(K, (x, y + 1.45, z - 0.05), 0.9, 0.45, 0.1, "ACHTUNG\nMINEN", board="#e8dcb0", ink=pm("#8a1e1e", 0.6), kind="sans")
    # the plateau: Normandy farmhouses, a church tower, hedgerow trees, telegraph poles
    stone = C.SB.grime("nm_stone", "#c8b89a", 0.35, 3.0); slate = C.SB.stripes("nm_slate", "#4a4e56", "#3a3e46", 6.0, 2)
    TM = C.tree_mats("summer")
    for k, (x, z, w, fl_) in enumerate(((-36, 86, 9, 2), (-22, 96, 7, 2), (18, 88, 10, 2), (34, 100, 8, 1), (52, 90, 7, 2), (-58, 92, 8, 2))):
        C.house(K, x, z, w, 6, fl_, rnd.uniform(-0.2, 0.2), stone, pm("#e8e0cc", 0.6), slate, C.SB.window_glow("nmw", "#ffc070", 1.5), rnd, 2.8, shutters=pm("#4a6a8a", 0.6), base=stone)
    K.box((44, H(44, 112) + 9, 112), (5, 18, 5), stone, 0, 0.05); K.cyl((44, H(44, 112) + 24, 112), 3.2, 12, slate, 4, "y", 0.0, math.pi / 4)
    for k in range(70):
        x, z = rnd.uniform(-105, 105), rnd.uniform(76, 150)
        if abs(x - BX) < 6 and z < 70: continue
        C.leafy(K, x, H(x, z), z, rnd.uniform(7, 12), rnd, TM)
    for k in range(4): C.hedge(K, -100, 80 + k * 18, 100, 83 + k * 18, 1.6, rnd, TM)
    for k in range(40):
        x, z = rnd.uniform(-100, 100), rnd.uniform(44, 72)
        if abs(x - 5) < 5 or abs(x - BX) < 6: continue
        K.sphere((x, H(x, z), z), rnd.uniform(0.5, 1.2), C.foliage_mat("nm_scrub", "#5a7a2a", "#2a4a1a"), 8, (1.3, 0.6, 1.2))
    K.build()
    # smoke on the bluffs (naval shelling) + fires
    for k, (x, z, h) in enumerate(((-30, 74, 26), (14, 76, 30), (40, 70, 22), (-62, 78, 28))):
        smoke_column(f"bsm{k}", (x, H(x, z) + 2, z), h, 2.0, 7, smm, drift=(-20, 14), seed=40 + k, puffs=12)
        fire(f"bfire{k}", (x, H(x, z), z - 1), 1.6, seed=50 + k, energy=2600)
    # ---------- the fleet ----------
    fleet = []
    def add(fn, *a, **k): fleet.extend(C.grab(fn, *a, **k))
    for i, (x, z, yw, L, Bm, kd) in enumerate(((-180, -420, 0.15, 150, 22, "battleship"), (120, -380, -0.1, 110, 15, "cruiser"), (320, -600, 0.2, 110, 15, "cruiser"),
                                               (-40, -260, 0.05, 90, 10, "destroyer"), (210, -240, -0.2, 90, 10, "destroyer"), (-320, -700, 0.1, 150, 22, "battleship"))):
        add(FR.warship, f"ws{i}", x, z, yw, L, Bm, kd, 0.3)
    FK = Kit("fleet"); grey = mat_once("shipgrey", lambda: worn("shipgrey", "#7a8590", "#4a525a", 0.55, 0.2, 0.5, 0.68, "#565e66"))
    dk = pm("#3a3e44", 0.5); bal = pm("#a8aca4", 0.5)
    for k in range(70):
        x, z = rnd.uniform(-900, 900), rnd.uniform(-160, -1400)
        if abs(x) < 70 and z > -300: continue
        L = rnd.uniform(60, 120); yw = rnd.uniform(-0.3, 0.3); P_ = C._P(x, z, yw)
        FK.box(P_(0, 1.8, 0), (L, 6.0, L * 0.14), grey, yw, 0.4)
        FK.box(P_(-L * 0.18, 7.0, 0), (L * 0.22, 6.0, L * 0.1), grey, yw, 0.2); FK.box(P_(-L * 0.18, 11, 0), (L * 0.12, 2.6, L * 0.08), dk, yw, 0.1)
        FK.cyl(P_(-L * 0.05, 9.5, 0), L * 0.025, 8, dk, 10)
        FK.cyl(P_(L * 0.3, 10, 0), 0.3, 14, dk, 6); FK.cyl(P_(-L * 0.38, 9, 0), 0.3, 12, dk, 6)
        if k % 3 == 0:
            by = rnd.uniform(70, 110); FK.sphere(P_(0, by, 0), 5.0, bal, 12, (2.4, 1.0, 1.0))
            for s in (-1, 1): FK.box(P_(-11, by + s * 2.2, 0), (4, 3, 0.4), bal, yw, 0.0, 0, s * 0.5)
            FK.cyl(P_(0, by / 2 + 4, 0), 0.08, by - 8, dk, 4)
    fleet.extend(FK.build())
    FLEET.extend(fleet)
    # ---------- fills ----------
    if kind != "dusk":
        C.fill((0, 30, -60), (0, 2, 20), 60000, (1.0, 0.82, 0.62), 60)
    else:
        C.fill((0, 30, -60), (0, 2, 20), 45000, (1.0, 0.6, 0.4), 60)
    C.fill((3, 6, -42), (3, 1.4, -28), 900, (1.0, 0.86, 0.7), 6)
    C.fill((0, 40, 140), (0, 10, 40), 30000, (0.7, 0.8, 1.0), 60)
    def update(f):
        on = f >= 1975
        for o in FLEET:
            try: o.hide_render = not on
            except ReferenceError: pass
        u = max(0.0, min(1.0, (f - 2546) / 14.0)); u = u * u
        if RAMP: RAMP.rotation_euler = (-u * math.radians(84), 0, 0)
    return {"update": update}
