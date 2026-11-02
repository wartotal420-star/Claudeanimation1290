# Map room (chapter 9: Axis high tide 1942, Torch, Stalingrad encirclement, Hitler and Stalin's tug-of-war; chapter 12:
# the 1945 squeeze). A timbered field-HQ map room at night: room x -7..7, z -6..6.5 (back wall z 6.5 with two windows
# on a dark pine forest), oak map table centred (0, 1) 4.3 x 2.5, top y 0.95; the Europe map (maps/c09_europe.png,
# lon -14..58, lat 63..24) spans x +1.95 (west) .. -1.95 (east), z -0.0565 (south) .. 2.0565 (north): 18.46 deg / m.
#   three x = 1.95 - (lon + 14) / 18.4615 ; three z = -0.0565 + (lat - 24) / 18.4615
# Keep clear: the map surface (overlay fx cards lie flat on it at y 0.952..0.96, rot pi); around Stalingrad (x -1.6, z 1.3),
# North Africa (z 0.2..0.8) and Germany (x 0.6, z 1.4) no props stand on the map. Characters stand behind the table at
# z 2.6..3.2 (|x| < 2) and at its ends x +-2.7; the camera works from z < 0.
import bpy, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, TS
from sets.void import (map_mat, map_plane, lathe, tube, worn, pmat, wood_mat, brass, glassm, gold, ink, text, mat_once, link,
                       toy_tank, pin_flag, unit_block, book, cup, compass, dividers, magnifier, candle, bookcase, window, sconce, smoke_mat)
from sets.warroom import phone, banker_lamp, typewriter, wall_clock, chair, rake
from sets import c09_kit as K

bx, cy = K.bx, K.cy
Y = 0.952
def mx(lon): return 1.95 - (lon + 14) / 18.4615
def mz(lat): return -0.0565 + (lat - 24) / 18.4615

def build(M, D):
    random.seed(1942); rnd = random.Random(42)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.01, 0.012, 0.02, 1); bg.inputs[1].default_value = 1.0
    FL = lib.parquet("c9floor", "#5a3a22", "#3e2614")
    PINE = K.mat_once("c9pine", lambda: lib.wood("c9pine", "#8a5a30", "#5a3418", 3, 0.5))
    OAK = K.mat_once("c9oak", lambda: lib.wood("c9oak", "#5a3018", "#2a140a", 5, 0.35))
    PN = K.mat_once("c9pan", lambda: lib.wood("c9pan", "#6a4024", "#3a1e0c", 2.5, 0.5))
    bx("floor", (0, -0.05, 0), (15, 0.1, 14), FL, 0)
    bx("rug", (0, 0.004, 1), (6.4, 0.012, 4.6), lib.carpet("c9rug", "#3a2a20", "#8a6a3a"), 0.003)
    bx("ceil", (0, 3.75, 0), (15, 0.1, 14), PN, 0)
    for k in range(6): bx(f"beam{k}", (0, 3.6, -5 + k * 2.2), (15, 0.22, 0.26), OAK, 0.02)
    # timbered walls: vertical boards, horizontal rails
    for z_, w_, yaw in ((6.55, 15, 0.0),):
        bx("back", (0, 1.9, z_), (w_, 3.8, 0.2), PN, 0)
    for sx in (-1, 1): bx(f"side{sx}", (sx * 7.1, 1.9, 0), (0.2, 3.8, 14), PN, 0)
    bx("front", (0, 1.9, -6.6), (15, 3.8, 0.2), PN, 0)
    for k in range(30): bx(f"board{k}", (-7 + k * 0.48, 1.9, 6.42), (0.04, 3.8, 0.05), OAK, 0.005)
    for sx in (-1, 1):
        for k in range(26): bx(f"sboard{sx}{k}", (sx * 6.98, 1.9, -6 + k * 0.48), (0.05, 3.8, 0.04), OAK, 0.005)
    for y_ in (0.9, 2.6):
        bx(f"rail{y_}", (0, y_, 6.38), (14, 0.1, 0.08), OAK, 0.01)
        for sx in (-1, 1): bx(f"srail{sx}{y_}", (sx * 6.94, y_, 0), (0.08, 0.1, 13), OAK, 0.01)
    # ---------- the oak map table ----------
    bx("ttop", (0, 0.92, 1), (4.3, 0.06, 2.5), OAK, 0.02)
    bx("tapron", (0, 0.78, 1), (4.1, 0.22, 2.3), OAK, 0.02)
    for sx in (-1, 1):
        for sz in (-1, 1): lathe(f"tleg{sx}{sz}", [(0.0, 0.0), (0.12, 0.0), (0.08, 0.1), (0.06, 0.3), (0.1, 0.45), (0.07, 0.55), (0.09, 0.68), (0.0, 0.68)], (sx * 1.9, 0, 1 + sz * 1.0), OAK, 20)
    map_plane("map", -1.95, 1.95, mz(24), mz(63), Y, map_mat("c9map", "c09_europe.png", 0.5))
    for sx in (-1, 1):
        for sz in (mz(24), mz(63)): bx(f"corner{sx}{sz}", (sx * 1.95, Y + 0.004, sz), (0.1, 0.01, 0.1), brass(), 0.003)
    # map furniture off the action areas: pins on capitals, unit blocks in the Atlantic, ships, dividers, papers
    for k, (lon, lat, col) in enumerate(((37.6, 55.75, "#b02a2a"), (30.3, 59.94, "#b02a2a"), (-0.1, 51.5, "#2a4a9a"), (12.5, 41.9, "#2a7a3a"), (2.35, 48.86, "#4a4a4a"), (31.24, 30.04, "#2a4a9a"))):
        pin_flag(f"pf{k}", (mx(lon), Y, mz(lat)), col, 0.11)
    for k, (lon, lat, yw) in enumerate(((-11, 47, 0.3), (-12, 38, 1.2), (-9, 56, 2.0))): toy_tank(f"tt{k}", (mx(lon), Y, mz(lat)), yw, "#6a6e64", 0.9)
    from sets.void import toy_ship
    for k, (lon, lat, yw) in enumerate(((-8, 44, 0.5), (-12.5, 42, 1.0), (-6, 50, 2.6), (4, 55, 0.4))): toy_ship(f"ts{k}", (mx(lon), Y, mz(lat)), yw, 0.2, "#6a7280")
    for k, (lon, lat, yw, col) in enumerate(((50, 60, 0.1, "#8a3a2a"), (54, 56, 0.4, "#8a3a2a"), (-12, 61, 0.2, "#3a4a8a"))): unit_block(f"ub{k}", (mx(lon), Y, mz(lat)), yw, col)
    for k in range(5): bx(f"pap{k}", (1.62 + k * 0.03, Y + 0.002 + k * 0.002, -0.35 + k * 0.01), (0.24, 0.002, 0.32), pmat("kpaper", "#f0e6cc", 0.8), 0, 0.15 * k - 0.2)
    text("GEHEIM", (1.6, Y + 0.013, -0.38), 0.04, pmat("kred", "#a81e22", 0.5), yaw=0.2)
    dividers("div", (-1.2, Y, -0.25), 0.4, 0.2); magnifier("mag", (0.4, Y, -0.32), 2.6); compass("comp", (-0.5, Y, -0.38), 0.06)
    rake("rake1", (1.0, Y, -0.3), 0.6, 1.0)
    cup("cup", (-1.85, Y, -0.35)); cup("cup2", (1.88, Y, 2.3), "#e8e0d0")
    lathe("ash", [(0.0, 0.0), (0.07, 0.0), (0.08, 0.025), (0.065, 0.025), (0.055, 0.008), (0.0, 0.008)], (-2.0, Y, 2.25), glassm(), 32)
    phone("phone", (2.0, Y + 0.004, 2.15), 0.4)
    book("bk1", (-1.95, Y, 0.1), (0.26, 0.06, 0.2), "#3a2a1a", 0.3); book("bk2", (-1.9, Y + 0.06, 0.12), (0.24, 0.05, 0.18), "#6a1e1e", 0.5)
    # ---------- the room ----------
    bookcase("shelfL", (-4.6, 0, 6.15), 3.0, 2.7, 0.4, 5, OAK, seed=7); bookcase("shelfR", (4.6, 0, 6.15), 3.0, 2.7, 0.4, 5, OAK, seed=8)
    # wall maps: the eastern front pinned to boards, framed
    wm = map_mat("c9wall", "c09_europe.png", 0.6)
    me = bpy.data.meshes.new("wallmap"); me.from_pydata([T(1.3, 1.5, 6.3), T(-1.3, 1.5, 6.3), T(-1.3, 2.9, 6.3), T(1.3, 2.9, 6.3)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for k, cc in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = cc
    link(bpy.data.objects.new("wallmap", me)); me.materials.append(wm)
    bx("wmframe", (0, 2.2, 6.34), (2.8, 1.6, 0.05), OAK, 0.02)
    for k, (x_, y_) in enumerate(((1.15, 2.8), (-1.15, 2.8), (1.15, 1.6), (-1.15, 1.6))): cy(f"tack{k}", (x_, y_, 6.28), 0.02, 0.02, pmat("kred", "#a81e22", 0.5), 8, rot=(math.radians(90), 0, 0))
    for sx in (-1, 1): window(f"win{sx}", (sx * 2.6, 1.2, 6.42), 0.9, 1.8, (0.22, 0.32, 0.55), 1.2, curtain="#3a3424", wood=OAK)
    for x_, lab in ((-1.6, "BERLIN"), (1.6, "MOSKAU")): wall_clock(f"clk{lab}", (x_, 3.25, 6.38), lab)
    for x_ in (-3.6, 3.6, -6.2, 6.2): sconce(f"sc{x_}", (x_, 2.3, 6.38), 55)
    # side walls: a radio desk (left), a teleprinter and coat hooks (right), filing cabinets, a stove
    bx("desk", (-6.2, 0.76, 2.5), (0.9, 0.06, 1.8), OAK, 0.02)
    for sz in (-1, 1): bx(f"deskped{sz}", (-6.2, 0.37, 2.5 + sz * 0.7), (0.86, 0.74, 0.4), OAK, 0.02)
    bx("radio", (-6.3, 1.05, 2.6), (0.5, 0.5, 0.8), K.mat_once("c9radio", lambda: worn("c9radio", "#4a4e44", "#2a2a24", 0.5, 0.4, 30, 0.7)), 0.02)
    for k in range(4): cy(f"rknob{k}", (-6.04, 1.0 + (k % 2) * 0.15, 2.35 + (k // 2) * 0.35), 0.03, 0.03, pmat("kblack", "#141414", 0.4), 12, rot=(0, math.radians(90), 0))
    bx("rdial", (-6.04, 1.18, 2.6), (0.01, 0.12, 0.3), lib.emit("c9dial", (1.0, 0.65, 0.25), 5), 0.004)
    banker_lamp("blamp", (-6.1, 0.79, 1.8), 1.6, 18); typewriter("tw", (-6.2, 0.79, 3.1), 1.57)
    for k in range(2):
        z_ = -2.5 + k * 0.75
        bx(f"file{k}", (6.6, 0.7, z_), (0.6, 1.4, 0.7), worn(f"c9filecab{k}", "#5a6050", "#2a2a26", 0.5, 0.5, 30, 0.7), 0.01)
        for d_ in range(4):
            bx(f"fd{k}{d_}", (6.29, 0.25 + d_ * 0.33, z_), (0.02, 0.28, 0.6), pmat("kfiledr", "#646a58", 0.45, 0.5), 0.005)
            bx(f"fh{k}{d_}", (6.27, 0.33 + d_ * 0.33, z_), (0.02, 0.025, 0.14), brass(), 0.003)
    for k in range(4):
        z_ = 1.5 + k * 0.5; cy(f"hook{k}", (6.95, 1.85, z_), 0.015, 0.15, brass(), 8, rot=(0, math.radians(90), 0))
        tube(f"coat{k}", [(6.85, 1.82, z_), (6.8, 1.5, z_ + 0.02), (6.82, 0.9, z_), (6.84, 0.55, z_ - 0.02)], 0.16, K.mat_once(f"c9coat{k % 2}", lambda: lib.cloth(f"c9coat{k % 2}", ["#4a4e46", "#5a5a50"][k % 2])), taper=lambda f: 0.6 + f * 0.6)
        lathe(f"cap{k}", [(0.0, 0.0), (0.15, 0.0), (0.16, 0.03), (0.13, 0.1), (0.0, 0.11)], (6.82, 1.95, z_), K.mat_once("c9capc", lambda: lib.cloth("c9capc", "#4a4e46")), 20)
    lathe("stove", [(0.0, 0.0), (0.35, 0.0), (0.38, 0.1), (0.35, 0.2), (0.33, 1.0), (0.36, 1.05), (0.2, 1.1), (0.0, 1.1)], (-5.8, 0, -3.5), pmat("c9stove", "#2a2622", 0.6, 0.6), 24)
    cy("stovepipe", (-5.8, 2.4, -3.5), 0.08, 2.6, pmat("c9stove", "#2a2622", 0.6, 0.6), 12)
    bx("stoveglow", (-5.8, 0.4, -3.85), (0.25, 0.18, 0.02), lib.emit("c9ember", (1.0, 0.35, 0.08), 6), 0.01)
    K.lamp_glow("stovel", (-5.8, 0.5, -4.1), 30, (1.0, 0.45, 0.15), 0.1)
    seat = K.mat_once("c9seat", lambda: lib.cloth("c9seat", "#3a2a1e"))
    for k, (x_, z_, yw) in enumerate(((-3.2, 0.2, 1.4), (3.2, 0.4, -1.5), (-5.6, 1.6, 1.57), (2.9, 3.3, 0.6), (-2.9, 3.4, -0.5))): chair(f"ch{k}", (x_, 0, z_), yw, OAK, seat)
    # forest outside the windows (dark firs against a deep blue night)
    fir = K.mat_once("c9fir", lambda: lib.principled("c9fir", lib.hexc("#0e1a14"), 0.9))
    for k in range(18):
        x_ = -8 + k * 0.95 + rnd.uniform(-0.3, 0.3); z_ = 8 + rnd.uniform(0, 4); h_ = rnd.uniform(5, 9)
        lathe(f"fir{k}", [(0.0, 0.0), (1.2, 1.0), (0.4, 1.2), (0.95, 2.4), (0.3, 2.6), (0.65, 3.8), (0.0, h_ * 0.6)], (x_, 0, z_), fir, 10)
    bx("night", (0, 4, 14), (30, 12, 0.1), lib.emit("c9night", (0.06, 0.09, 0.2), 1.0), 0)
    # ---------- light: hanging green-shaded lamp over the map (warm key), sconces, desk lamp, stove, cold moon rim ----------
    cy("cord", (0, 3.2, 1), 0.008, 1.0, M["dark"], 6)
    lathe("lshade", [(0.07, 0.25), (0.55, 0.0), (0.57, -0.02), (0.08, 0.23)], (0, 2.45, 1), K.mat_once("klshade", lambda: worn("klshade", "#2a5a3a", "#1a2a1e", 0.35, 0.6, 20, 0.75)), 40, cap=False)
    lathe("lshadein", [(0.068, 0.248), (0.545, 0.0)], (0, 2.45, 1), lib.principled("c9lshin", lib.hexc("#f2ead0"), 0.6, 0.0, (1.0, 0.85, 0.6), 1.5), 40, cap=False)
    lathe("bulb", [(0.0, 0.18), (0.05, 0.13), (0.045, 0.08), (0.0, 0.06)], (0, 2.45, 1), M["bulb"], 20)
    sp = lib.light("SPOT", T(0, 2.55, 1), 1500, (1.0, 0.76, 0.48), 0.25); lib.look_at(sp, T(0, 0.9, 1)); sp.data.spot_size = math.radians(120); sp.data.spot_blend = 0.6
    lib.light("POINT", T(0, 2.85, 1), 40, (1.0, 0.75, 0.45), 0.2)
    K.area((0, 3.5, -3), (0, 1.4, 2.5), 260, (1.0, 0.72, 0.5), 5)                      # warm fill on the faces behind the table
    for sx in (-1, 1): K.area((sx * 2.6, 2.0, 7.5), (sx * 1.0, 1.2, 2.5), 160, (0.45, 0.6, 1.0), 1.2, 2.0)   # moonlight rim through the windows
    K.area((5, 3, -5), (0, 1, 1), 120, (0.55, 0.65, 1.0), 4)
    return {}
