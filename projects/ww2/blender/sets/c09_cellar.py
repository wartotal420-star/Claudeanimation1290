# Paulus' headquarters in the Univermag cellar, January 1943 (chapter 9). A brick-vaulted basement lit by candles in
# bottles, a hurricane lamp and a small iron stove; cold daylight from a sandbagged light-well at the back left.
# Layout (three, y up): cellar x -5..5, z -4..7, floor y 0, vault springs at y 2.2, crown y 3.1 (arches every 2 m along z);
# the general's table at (0, 0, 2.2) 2.2 x 1.1 (top y 0.78) - Paulus stands behind it at (0, 0, 3.1) or beside at (1.6, 0, 2.6);
# a staff officer's spot at (-1.9, 0, 3.0); the door (stairs up) at the back right (3.6, 0, 6.8); the light-well (-3.4, 2.4, 6.9).
# Keep clear: the telegram fx card is held at ~(0.15, 1.25, 1.5) / lies on the table at (0.3, 0.79, 1.9).
import bpy, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, fire, flame, flame_mat, smoke_mat, text, candle, cup, book
from sets.warroom import phone, chair, typewriter
from sets import c09_kit as K

bx, cy = K.bx, K.cy
def bottle_candle(name, c, h=0.16, seed=0, light=1.0):
    gl = K.mat_once("c9bottle", lambda: lib.principled("c9bottle", lib.hexc("#1e3a22"), 0.1, 0.0))
    lathe(name, [(0.0, 0.0), (0.04, 0.0), (0.042, 0.02), (0.04, 0.17), (0.015, 0.22), (0.013, 0.27), (0.0, 0.27)], c, gl, 18)
    wax = pmat("kwax", "#efe2c4", 0.45)
    lathe(f"{name}w", [(0.0, 0.25), (0.016, 0.25), (0.014, 0.25 + h), (0.0, 0.26 + h)], c, wax, 12)
    rnd = random.Random(seed)
    for k in range(5):
        a = rnd.random() * math.tau
        tube(f"{name}d{k}", [(c[0] + 0.017 * math.cos(a), c[1] + 0.25 + h * 0.8, c[2] + 0.017 * math.sin(a)), (c[0] + 0.03 * math.cos(a), c[1] + 0.2, c[2] + 0.03 * math.sin(a)), (c[0] + 0.042 * math.cos(a), c[1] + 0.05 + rnd.random() * 0.1, c[2] + 0.042 * math.sin(a))], 0.006, wax, res=4, bres=1)
    flame(f"{name}fl", (c[0], c[1] + 0.265 + h, c[2]), 0.055, 0.011, K.mat_once("flamemat", lambda: flame_mat("flame")), seed=seed)
    if light: lib.light("POINT", T(c[0], c[1] + 0.31 + h, c[2]), 7 * light, (1.0, 0.58, 0.26), 0.02).visible_camera = False
def build(M, D):
    rnd = random.Random(431)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.01, 0.01, 0.015, 1); bg.inputs[1].default_value = 1.0
    BR = K.mat_once("c9cbrick", lambda: lib.brickmat("c9cbrick", "#7a3a28", "#5a2a1c", "#6a5a4a", 4.5))
    BR2 = K.mat_once("c9cbrick2", lambda: lib.brickmat("c9cbrick2", "#8a4a32", "#6a3424", "#7a6a5a", 4.5))
    FLR = K.mat_once("c9cfloor", lambda: lib.tiles("c9cfloor", "#6a6058", "#4a4038", "#2a2420", 2.0))
    WD = wood_mat("c9cwood", "#5a3a20", "#2a1a0c", 6, 0.5)
    bx("floor", (0, -0.05, 1.5), (11, 0.1, 12), FLR, 0)
    for sd in (-1, 1): bx(f"wall{sd}", (sd * 5.15, 1.6, 1.5), (0.3, 3.2, 12), BR, 0)
    bx("back", (0, 1.6, 7.15), (11, 3.2, 0.3), BR, 0); bx("front", (0, 1.6, -4.3), (11, 3.2, 0.3), BR, 0)
    # barrel vault built from brick arches (ribs) with infill shells
    for k in range(7):
        z_ = -3.5 + k * 1.8; pts = []
        for j in range(17):
            a = math.pi * j / 16; pts.append((5.0 * math.cos(a), 2.2 + 0.9 * math.sin(a), z_))
        tube(f"rib{k}", pts, 0.16, BR2, res=2, bres=1)
    for j in range(16):
        a0, a1 = math.pi * j / 16, math.pi * (j + 1) / 16
        p0 = (5.05 * math.cos(a0), 2.2 + 0.95 * math.sin(a0)); p1 = (5.05 * math.cos(a1), 2.2 + 0.95 * math.sin(a1))
        vs = [(p0[0], p0[1], -4.2), (p1[0], p1[1], -4.2), (p1[0], p1[1], 7.2), (p0[0], p0[1], 7.2)]
        mesh_obj(f"vault{j}", vs, [(0, 1, 2, 3)], BR)
    for sd in (-1, 1):
        for k in range(6): bx(f"pier{sd}{k}", (sd * 4.85, 1.1, -3.5 + k * 1.8 + 0.9 * 0), (0.35, 2.2, 0.35), BR2, 0.02)
    # light-well at the back left: sandbagged slit, snow on the sill, cold daylight
    bx("lwell", (-3.4, 2.5, 7.0), (1.4, 0.6, 0.1), lib.emit("c9day", (0.7, 0.8, 1.0), 2.5), 0)
    K.sandbags("lwsb", (-3.4, 2.15, 6.85), 0.0, 3, 1, 3)
    K.blob3("lwsnow", (-3.4, 2.25, 6.8), (0.7, 0.08, 0.2), K.snow_ground("c9snow3"), 0.02, 1)
    K.area((-3.4, 2.6, 7.6), (-0.5, 0.8, 2.0), 260, (0.55, 0.68, 1.0), 1.2, 0.5)
    # door and stairs up (back right)
    bx("door", (3.6, 1.05, 7.0), (1.1, 2.1, 0.08), WD, 0.01)
    for k in range(4): bx(f"dplank{k}", (3.6, 0.4 + k * 0.45, 6.95), (1.1, 0.06, 0.03), wood_mat("c9cwood2", "#3a2614", "#1a0e06", 6, 0.6), 0.005)
    lathe("dknob", [(0.0, 0.0), (0.03, 0.0), (0.03, 0.04), (0.0, 0.05)], (3.25, 1.0, 6.94), pmat("c9iron", "#2a2a28", 0.6, 0.5), 10, tilt=Matrix.Rotation(math.radians(90), 3, "X"))
    # ---------- the general's table: maps, telegrams, field phone, candles, coffee, bread crust, pistol holster ----------
    bx("ttop", (0, 0.76, 2.2), (2.2, 0.05, 1.1), WD, 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1): bx(f"tleg{sx}{sz}", (sx * 1.0, 0.37, 2.2 + sz * 0.45), (0.07, 0.74, 0.07), WD, 0.005)
    for k in range(3):
        bx(f"tmap{k}", (-0.3 + k * 0.25, 0.79 + k * 0.002, 2.25 + (k - 1) * 0.08), (0.9, 0.003, 0.7), K.mat_once(f"c9tmap{k}", lambda: lib.principled(f"c9tmap{k}", lib.hexc(["#d8cca8", "#c8d0b0", "#e0d4b8"][k]), 0.8)), 0, 0.1 * (k - 1))
    for k in range(9):
        a = k / 9 * math.tau; tube(f"ring{k}", [(-0.3 + 0.18 * math.cos(a), 0.796, 2.3 + 0.12 * math.sin(a)), (-0.3 + 0.18 * math.cos(a + 0.7), 0.796, 2.3 + 0.12 * math.sin(a + 0.7))], 0.006, pmat("kred", "#a81e22", 0.5), res=2, bres=0)
    for k, (x_, z_) in enumerate(((-0.9, 1.8), (0.85, 2.55), (-0.85, 2.6))): bottle_candle(f"bc{k}", (x_, 0.785, z_), 0.12 + 0.05 * k, k, 1.2)
    phone("fphone", (0.8, 0.785, 2.0), -0.4)
    cup("cup", (-0.65, 0.785, 1.85), "#c8c0b0"); K.helmet_ground("thelm", (0.55, 0.785, 2.75), 0.6, "#4c5448", "stahl")
    for k in range(3): bx(f"tgram{k}", (0.45 + k * 0.05, 0.79 + k * 0.002, 1.85 + k * 0.03), (0.2, 0.002, 0.14), pmat("c9tgram", "#f0e8c8", 0.8), 0, 0.3 * k)
    lathe("lamp", [(0.0, 0.0), (0.08, 0.0), (0.08, 0.1), (0.04, 0.12), (0.06, 0.18), (0.06, 0.3), (0.03, 0.34), (0.0, 0.34)], (-0.95, 0.785, 2.55), pmat("c9lampm", "#4a4a30", 0.5, 0.6), 16)
    lathe("lampg", [(0.0, 0.12), (0.055, 0.14), (0.055, 0.28), (0.0, 0.3)], (-0.95, 0.785, 2.55), lib.emit("c9lampg", (1.0, 0.7, 0.35), 4), 16)
    lib.light("POINT", T(-0.95, 1.05, 2.55), 45, (1.0, 0.65, 0.32), 0.05).visible_camera = False
    # ---------- around the room: cots with grey blankets, department-store crates, shelves of boxes, stove, radio, coats ----------
    for k, z_ in enumerate((-2.6, -0.8)):
        bx(f"cot{k}", (-4.1, 0.38, z_), (0.8, 0.08, 1.9), K.mat_once("c9cot", lambda: lib.cloth("c9cot", "#5a5a50")), 0.03)
        for sx in (-1, 1):
            for sz in (-1, 1): bx(f"cotl{k}{sx}{sz}", (-4.1 + sx * 0.35, 0.19, z_ + sz * 0.85), (0.04, 0.38, 0.04), WD, 0.004)
        K.blob3(f"cotbl{k}", (-4.1, 0.48, z_ + 0.2), (0.38, 0.1, 0.7), K.mat_once("c9blanket", lambda: lib.cloth("c9blanket", "#4a4a44")), 0.06, k)
    crate = wood_mat("c9crate", "#8a7a52", "#5a4a2a", 10, 0.7)
    for k in range(9):
        x_, z_ = 3.6 + (k % 3) * 0.55 - 0.6, 4.6 + (k // 3) * 0.0 + (k % 2) * 0.1
        bx(f"cr{k}", (x_ + (k // 3) * 0.08, 0.25 + (k // 3) * 0.5, z_ - 1.0), (0.5, 0.48, 0.5), crate, 0.01, rnd.uniform(-0.1, 0.1))
    text("UNIVERMAG", (3.5, 0.3, 3.34), 0.08, pmat("c9sten", "#2a2018", 0.8), flat=False)
    for y_ in (0.5, 1.2, 1.9):
        bx(f"shelf{y_}", (4.75, y_, 1.0), (0.45, 0.04, 3.0), WD, 0.005)
        for k in range(7): bx(f"box{y_}{k}", (4.75, y_ + 0.14, -0.3 + k * 0.42), (0.36, 0.26, 0.34), K.mat_once(f"c9box{k % 3}", lambda: lib.principled(f"c9box{k % 3}", lib.hexc(["#b8a07a", "#8a7a5a", "#c8b48a"][k % 3]), 0.8)), 0.01, rnd.uniform(-0.1, 0.1))
    lathe("stove", [(0.0, 0.0), (0.3, 0.0), (0.32, 0.08), (0.3, 0.16), (0.28, 0.8), (0.3, 0.84), (0.16, 0.9), (0.0, 0.9)], (-3.4, 0, 4.4), pmat("c9stove", "#2a2622", 0.6, 0.6), 24)
    tube("stpipe", [(-3.4, 0.9, 4.4), (-3.4, 2.3, 4.4), (-3.4, 2.6, 6.9)], 0.07, pmat("c9stove", "#2a2622", 0.6, 0.6), res=4, bres=1)
    bx("stglow", (-3.4, 0.35, 4.11), (0.2, 0.14, 0.02), lib.emit("c9ember", (1.0, 0.35, 0.08), 8), 0.01)
    K.lamp_glow("stl", (-3.4, 0.45, 3.9), 40, (1.0, 0.45, 0.15), 0.1)
    bx("radio", (-4.5, 0.95, 2.6), (0.45, 0.45, 0.7), K.mat_once("c9radio", lambda: worn("c9radio", "#4a4e44", "#2a2a24", 0.5, 0.4, 30, 0.7)), 0.02)
    bx("radiot", (-4.5, 0.5, 2.6), (0.5, 0.06, 0.8), WD, 0.01)
    bx("rdial", (-4.27, 1.05, 2.6), (0.01, 0.1, 0.25), lib.emit("c9dial", (1.0, 0.65, 0.25), 5), 0.004)
    for k in range(3):
        tube(f"coat{k}", [(4.9, 1.9, -2.5 + k * 0.5), (4.8, 1.5, -2.48 + k * 0.5), (4.82, 0.8, -2.5 + k * 0.5)], 0.15, K.mat_once("c9coat0", lambda: lib.cloth("c9coat0", "#4a4e46")), taper=lambda f: 0.6 + f * 0.6)
        lathe(f"cap{k}", [(0.0, 0.0), (0.15, 0.0), (0.16, 0.03), (0.13, 0.1), (0.0, 0.11)], (4.82, 2.0, -2.5 + k * 0.5), K.mat_once("c9capc", lambda: lib.cloth("c9capc", "#4a4e46")), 20)
    for k, (x_, z_, yw) in enumerate(((-1.6, 2.0, 1.2), (1.5, 1.6, -1.8))): chair(f"ch{k}", (x_, 0, z_), yw, WD, K.mat_once("c9seat3", lambda: lib.cloth("c9seat3", "#3a2a1e")))
    typewriter("tw", (-4.45, 0.53, 1.6), 1.57)
    for k in range(6): bottle_candle(f"wc{k}", (rnd.uniform(-3.5, 3.5), 0, rnd.choice((-3.6, 6.6))), 0.1, k + 10, 0.8)
    for k in range(25): bx(f"paper{k}", (rnd.uniform(-3, 3), 0.003, rnd.uniform(-2, 5)), (0.2, 0.003, 0.28), pmat("kpaper", "#f0e6cc", 0.8), 0, rnd.random() * 3)
    for k in range(6): K.ammo_box(f"amb{k}", (2.2 + (k % 3) * 0.36, 0, -3.4 + (k // 3) * 0.2), 0.1 * k)
    # hanging bare bulb (dead) and a warm low fill from the candles' side, cold rim from the light-well
    tube("wire", [(0, 3.1, 2.2), (0, 2.5, 2.2)], 0.006, pmat("kblack", "#141414", 0.4), res=2, bres=0)
    lathe("deadbulb", [(0.0, 0.0), (0.04, 0.03), (0.035, 0.08), (0.0, 0.1)], (0, 2.4, 2.2), pmat("c9dead", "#8a8070", 0.2), 12)
    K.area((0.5, 2.0, -2.0), (0, 1.2, 2.6), 160, (1.0, 0.62, 0.35), 3)
    K.area((3.5, 2.4, 6.0), (0, 1.2, 2.4), 60, (0.6, 0.7, 1.0), 2)
    return {}
