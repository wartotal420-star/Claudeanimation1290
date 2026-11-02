# The map room (chapter 11 + 14): a wood-panelled headquarters room with a big table map of Europe 1944
# (maps/c11_europe.png, lon -9..33, lat 43.5..59, equirectangular). Room x -7..7, z -5..6 (back wall z 6), ceiling 4.2.
# The table: centre (0, 1.0), top y 0.92; the MAP spans x -1.95..1.95, z -0.15..2.15 at y 0.925, west on screen left
# for a camera on the -z side (lon -> x = 1.95 - (lon + 9) / 42 * 3.9; lat -> z = -0.15 + (lat - 43.5) / 15.5 * 2.3).
# Map overlays (arrows, lines) are exported flat fx cards at y 0.93, rot pi (readable from -z).
# Keep clear: the map surface (no props on it except along the very edges); standing room round the table:
# z -1.4..-0.6 (camera side, x -2.6..2.6), x +-2.6..3.4 (the two ends), z 2.7..3.3 (far side).
# Light: three green-shaded lamps over the table (warm pools), blackout windows with cool daylight slits on the -x wall,
# desk lamps, a warm bounce from the camera end; the back wall has the big Channel wall map and flags.
import bpy, math, random, os
from mathutils import Vector
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, glassm
from sets import ikit as IK
from sets.void import map_mat, map_plane, toy_tank, pin_flag, unit_block, cup, compass, dividers, magnifier, inkwell, bookcase, book
from sets.warroom import phone, banker_lamp, typewriter, wall_clock, rake, letters, chair

def build(M, D):
    rnd = random.Random(611); C.SB.reset()
    S = bpy.context.scene; bg = S.world.node_tree.nodes.get("Background")
    if bg: bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1); bg.inputs[1].default_value = 0.2
    K = Kit("room")
    panel = C.SB.wood("#6a4428", "#3a2414", 4, 0.45); dark = C.SB.wood("#4a2c18", "#24140a", 5, 0.4)
    wallp = C.plaster("mr", "#c8b896"); fl = C.planks("mr_floor", "#7a4a2a", "#4a2a16", "X", 0.12, 1.4)
    # floor, carpet runner, ceiling with beams, walls with dado panelling
    K.box((0, -0.05, 0.5), (14.2, 0.1, 11.2), fl, 0, 0)
    IK.floor_quad("mr_rug", (0, 1.0), 5.6, 4.2, IK.img_mat("mr_rugm", IK.carpet_img(192, 256, "#5a1a1a", "#c8a24a", "#1e2a3a"), 0.9), 0, 0.006)
    K.box((0, 4.25, 0.5), (14.2, 0.1, 11.2), C.plaster("mrc", "#d8ccb4"), 0, 0)
    for k in range(5): K.box((-6 + k * 3, 4.05, 0.5), (0.3, 0.3, 11), dark, 0, 0.02)
    for (cx, cz, w, d) in ((0, 6.05, 14.2, 0.1), (0, -5.05, 14.2, 0.1), (-7.05, 0.5, 0.1, 11.2), (7.05, 0.5, 0.1, 11.2)):
        K.box((cx, 2.1, cz), (w, 4.2, d), wallp, 0, 0)
    for (cx, cz, w, d, yaw) in ((0, 5.95, 14, 0.12, 0), (0, -4.95, 14, 0.12, 0), (-6.95, 0.5, 0.12, 11, 0), (6.95, 0.5, 0.12, 11, 0)):
        K.box((cx, 0.6, cz), (w, 1.2, d), panel, 0, 0.005); K.box((cx, 1.22, cz), (w + 0.02, 0.06, d + 0.04), dark, 0, 0.005)
        K.box((cx, 0.06, cz), (w + 0.02, 0.12, d + 0.04), dark, 0, 0.005); K.box((cx, 3.95, cz), (w + 0.02, 0.12, d + 0.06), dark, 0, 0.01)
    # the map table: heavy oak, turned legs, a raised rim; the map
    oak = C.SB.wood("#7a4a26", "#3e2412", 5, 0.4)
    K.box((0, 0.88, 1.0), (4.3, 0.08, 2.7), oak, 0, 0.02)
    for sx in (-1, 1): K.box((sx * 2.13, 0.95, 1.0), (0.06, 0.06, 2.72), dark, 0, 0.01)
    for sz in (-1, 1): K.box((0, 0.95, 1.0 + sz * 1.33), (4.32, 0.06, 0.06), dark, 0, 0.01)
    K.box((0, 0.74, 1.0), (4.1, 0.22, 2.5), oak, 0, 0.01)
    for sx in (-1.85, 0, 1.85):
        for sz in (-1.05, 1.05): K.cyl((sx, 0.32, 1.0 + sz), 0.09, 0.64, dark, 12); K.cyl((sx, 0.45, 1.0 + sz), 0.12, 0.12, dark, 12)
    map_plane("map", -1.95, 1.95, -0.15, 2.15, 0.925, map_mat("mr_map", "c11_europe.png", 0.55))
    # props on the table rim only: phones, cups, an ashtray, dividers, a pointer, rakes, unit blocks waiting
    phone("ph1", (-2.0, 0.92, -0.2), 0.3); phone("ph2", (1.95, 0.92, 2.3), 2.6)
    cup("cup1", (1.98, 0.92, -0.22)); cup("cup2", (-1.98, 0.92, 2.25))
    K.cyl((2.02, 0.94, 0.4), 0.08, 0.03, glassm(), 16); K.cyl((2.02, 0.955, 0.4), 0.06, 0.01, pm("#5a5650", 0.9), 12)
    for k in range(3): K.cyl((2.0 + k * 0.01, 0.965, 0.38 + k * 0.03), 0.006, 0.07, pm("#f0ece0", 0.8), 6, "x", None, 0.5 * k)
    rake("rk1", (-2.0, 0.93, 1.7), 0.0, 1.2); rake("rk2", (2.0, 0.93, 1.2), math.pi, 1.1)
    for k in range(6): unit_block(f"ub{k}", (-2.04 + (k % 2) * 0.06, 0.92, 0.5 + k * 0.12), 0.1 * k, ["#2a4a8a", "#8a2a2a", "#2a6a3a"][k % 3])
    K.cyl((0, 0.95, -0.24), 0.012, 1.4, pm("#c8a060", 0.4), 8, "x")
    # three green-shaded hanging lamps over the table
    gm = C.mat_once("mr_greenglass", lambda: lib.principled("mr_gg", lib.hexc("#1a6a3a"), 0.15, 0.0, (0.2, 0.9, 0.45), 0.5))
    for x in (-1.4, 0, 1.4):
        K.cyl((x, 3.4, 1.0), 0.008, 1.6, pm("#1a1a1a", 0.6), 4)
        K.cyl((x, 2.55, 1.0), 0.32, 0.22, gm, 24, "y", 0.12); K.cyl((x, 2.43, 1.0), 0.07, 0.06, em("#fff0c8", 18), 12)
        C.lamp((x, 2.32, 1.0), 120, (1.0, 0.78, 0.5), 0.08)
    # the back wall: Channel wall map (crop of the table map), flags, a clock pair, a blackboard
    mw = IK.img_mat("mr_wallmap", bpy.data.images.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps", "c11_europe.png")), 0.6)
    IK.framed("wallmap", (0, 2.45, 5.9), 5.6, 3.3, mw, dark, 0, 0.1, 0.06)
    for x, kind in ((-4.1, "uk"), (-5.2, "us"), (4.1, "fr"), (5.2, "ca")):
        C.flagpole(f"fl{x}", x, 0.0, 5.5, 2.9, kind, 0.0, 0.95, 0.62, 0.05, brass())
        K.cyl((x, 0.06, 5.5), 0.2, 0.12, brass(), 16)
    wall_clock("clk1", (-1.8, 3.6, 5.88), "LONDON"); wall_clock("clk2", (1.8, 3.6, 5.88), "MOSCOW")
    # left wall (-x): blackout windows with daylight slits, a teleprinter desk, filing cabinets
    for z in (-2.5, 0.5, 3.5):
        K.box((-6.98, 2.2, z), (0.06, 2.0, 1.4), em("#a8c4ff", 1.5), 0, 0)
        for s in (-1, 1): K.box((-6.9, 2.2, z + s * 0.38), (0.06, 2.1, 0.66), C.SB.cloth("#1e1e24"), 0, 0.02)
        for k in range(3): K.box((-6.9, 1.35 + k * 0.72, z), (0.1, 0.06, 1.5), dark, 0, 0.005)
        C.fill((-6.8, 2.2, z), (0, 1.0, z), 90, (0.7, 0.82, 1.0), 0.3, 1.8)
    for k in range(3):
        z = -3.8 + k * 0.62
        K.box((-6.6, 0.7, z), (0.7, 1.4, 0.6), iron("#5a6050"), 0, 0.02)
        for j in range(3): K.box((-6.24, 0.32 + j * 0.42, z), (0.02, 0.36, 0.52), iron("#6a7060"), 0, 0.01); K.box((-6.22, 0.42 + j * 0.42, z), (0.03, 0.03, 0.14), brass(), 0, 0)
    K.box((-6.3, 0.75, 2.0), (1.2, 0.06, 2.0), oak, 0, 0.01)
    for sz in (-0.9, 0.9):
        for sx in (-0.5, 0.5): K.box((-6.3 + sx, 0.37, 2.0 + sz), (0.06, 0.74, 0.06), dark, 0, 0)
    typewriter("tw", (-6.3, 0.78, 1.6), -math.pi / 2); banker_lamp("bl1", (-6.4, 0.78, 2.6), -math.pi / 2, 20)
    letters("lt1", (-6.2, 0.78, 2.2), 0.3, 5, True)
    # right wall (+x): bookcase, a pinned-up board of photos and orders, a radio set with a lit dial
    bookcase("bc", (6.7, 0, -2.5), 2.4, 2.6, 0.4, 5, dark, -math.pi / 2, 4)
    K.box((6.9, 2.0, 1.0), (0.06, 1.6, 2.6), C.SB.cloth("#6a5a40"), 0, 0.01)
    for k in range(8):
        a = C.poster_img([(["ORDERS", "SECRET", "OVERLORD", "BOLERO", "FORTITUDE", "NEPTUNE", "TOP SECRET", "MAPS"][k], 0.14, "#8a1e1e" if k % 3 == 0 else "#2a2a2a")], "#f0e8d4", "#2a2a2a", 128, 96, seed=k)
        IK.panel(f"memo{k}", (6.86, 2.4 - (k // 4) * 0.62, 0.0 + (k % 4) * 0.62), 0.5, 0.38, IK.img_mat(f"mr_memo{k}", a, 0.8), -math.pi / 2 + rnd.uniform(-0.05, 0.05))
    K.box((6.6, 0.45, 3.6), (0.7, 0.9, 1.2), C.SB.wood("#5a3a22", "#2a1a0e", 6), 0, 0.02)
    K.box((6.6, 1.2, 3.6), (0.5, 0.6, 1.0), iron("#3a3a34"), 0, 0.02); K.box((6.33, 1.25, 3.6), (0.02, 0.18, 0.6), em("#ffb85a", 3), 0, 0)
    for k in range(4): K.cyl((6.33, 1.05, 3.3 + k * 0.2), 0.04, 0.03, pm("#d8d0c0", 0.4), 12, "x")
    # front wall (behind the cameras): a door, a coat stand
    K.box((3.5, 1.1, -4.98), (1.1, 2.2, 0.08), dark, 0, 0.01)
    # chairs round the table and against the walls
    vel = C.SB.cloth("#4a2a1e")
    for k, (x, z, yaw) in enumerate(((-2.9, 0.4, -math.pi / 2), (2.9, 1.6, math.pi / 2), (-1.2, 3.1, math.pi), (1.2, 3.1, math.pi), (-5.6, 4.6, math.pi), (5.6, 4.8, math.pi))):
        IK.chair(f"ch{k}", x, z, yaw, oak, vel, 0.48, True, None)
    C.fill((0, 3.2, -4.6), (0, 1.0, 1.0), 380, (1.0, 0.84, 0.66), 5, 2.5)
    C.fill((5.5, 3.0, -2.0), (0, 1.2, 1.5), 140, (1.0, 0.8, 0.6), 2.0)
    K.build()
    return {}
