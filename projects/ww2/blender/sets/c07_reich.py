# Hitler's study, December 1941 (chapter 7 shots 13-14): he reads the news at his desk, stands, spins the big globe to
# America and declares war on it; his generals behind him count his new enemies.
# three.js layout: room x -7..7, z -4..7 (back wall z 7 with three tall windows, fireplace on the left wall x -7).
#   desk centred (0.6, 0, 2.6), 2.6 x 1.2, top y 0.8 (Hitler stands behind it at (0.6, 0, 3.5) or sits in the chair);
#   the globe (radius 0.55, centre y 1.15) on its stand at (-1.5, 0, 2.2); generals stand at (2.6, 0, 3.4) and (3.4, 0, 2.6).
#   update(f): the globe turns from Europe to the Americas between f 1560 and 1600 (chapter-local).
# No emblems anywhere: plain red curtains, plain flags are not used.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, poster, gold, brass, paper, books
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj, map_mat, inkwell, cup, candle
from sets import c07_kit as CK
from sets import ikit

GLOBE = (-1.5, 1.15, 2.2)
G_EUROPE, G_AMERICA = -1.6, 0.3     # globe yaw (rad) showing Europe / the Americas to the camera (tuned by test render)
def build(M, D):
    rnd = random.Random(1211)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.3, 0.36, 0.5, 1); bg.inputs[1].default_value = 0.4
    K = Kit("rk")
    dark = wood("#3a2214", "#1a0e08", 5.0, 0.3); oak = wood("#6a4a2a", "#3a2414", 6.0, 0.4)
    marble = mat_once("rmarble", lambda: lib.principled("rmarble", hexc("#6a3a34"), 0.2)); goldm = gold()
    K.box((0, -0.05, 1.5), (14.4, 0.1, 11.4), mat_once("rfloor", lambda: lib.parquet("rfloor", "#6a3e22", "#4a2814")), 0.0, 0.0)
    K.box((0.6, 0.006, 2.4), (6.5, 0.012, 4.2), mat_once("rrug", lambda: lib.carpet("rrug", "#5a1e1a", "#b8902a")), 0.0, 0.0)
    wall = mat_once("rwall", lambda: lib.plaster("rwall", "#a89478"))
    K.box((0, 3.0, 7.05), (14.4, 6, 0.1), wall, 0.0, 0.0); K.box((-7.05, 3.0, 1.5), (0.1, 6, 11.4), wall, 0.0, 0.0); K.box((7.05, 3.0, 1.5), (0.1, 6, 11.4), wall, 0.0, 0.0)
    K.box((0, 0.7, 6.95), (14.2, 1.4, 0.12), dark, 0.0, 0.01); K.box((-6.95, 0.7, 1.5), (0.12, 1.4, 11.2), dark, 0.0, 0.01); K.box((6.95, 0.7, 1.5), (0.12, 1.4, 11.2), dark, 0.0, 0.01)
    K.box((0, 6.05, 1.5), (14.4, 0.1, 11.4), pm("#c8b898", 0.8), 0.0, 0.0)
    for i in range(6): K.box((-6 + i * 2.4, 5.85, 1.5), (0.3, 0.3, 11.2), dark, 0.0, 0.01)
    # three tall windows in the back wall: cold December daylight, heavy plain red curtains
    winm = lib.emit("rwin", (0.62, 0.72, 0.95), 2.5)
    for k, x in enumerate((-3.6, 0.6, 4.8)):
        K.box((x, 3.0, 7.0), (1.8, 3.8, 0.02), winm, 0.0, 0.0)
        for j in range(3): K.box((x - 0.9 + j * 0.9, 3.0, 6.96), (0.08, 3.8, 0.08), dark, 0.0, 0.0)
        for j in range(5): K.box((x, 1.1 + j * 0.95, 6.96), (1.8, 0.08, 0.08), dark, 0.0, 0.0)
        cur = mat_once("rcurt", lambda: ikit.velvet("rcurt", "#7a1414"))
        for sd in (-1, 1): ikit.drape(f"rc{k}{sd}", (x + sd * 1.25, 5.5, 6.85), 0.9, 5.2, cur, 0.0, 6, 0.08, 0.0)
    # fireplace with a real fire, mantel clock, candlesticks, portrait frames (dim landscapes), bookcases
    K.box((-6.7, 0.7, 2.5), (0.6, 1.4, 2.4), marble, 0.0, 0.02); K.box((-6.6, 1.45, 2.5), (0.8, 0.1, 2.7), marble, 0.0, 0.02)
    K.box((-6.45, 0.45, 2.5), (0.2, 0.8, 1.3), pm("#0e0a08", 0.8), 0.0, 0.0)
    CK.fireball("rfire", (-6.45, 0.12, 2.5), 0.32, 5, 120)
    K.box((-6.55, 1.68, 2.5), (0.2, 0.35, 0.4), goldm, 0.0, 0.01)
    for d in (-1.0, 1.0): candle(f"rcand{d}", (-6.55, 1.5, 2.5 + d), 0.2, int(d + 2), 0.6)
    land = ikit.landscape_img(4, 384, 288)
    ikit.framed("rpaint", (-6.95, 3.3, 2.5), 2.2, 1.6, ikit.img_mat("rpaintm", land, 0.6), goldm, math.pi / 2, 0.1)
    for k, z in enumerate((-1.5, 5.0)): K.box((6.7, 1.6, z), (0.5, 3.2, 2.0), dark, 0.0, 0.02)
    for k, z in enumerate((-1.5, 5.0)):
        for j in range(5):
            y = 0.25 + j * 0.6; K.box((6.5, y, z), (0.45, 0.04, 1.9), dark, 0.0, 0.0)
            zz = z - 0.9
            while zz < z + 0.88:
                w = rnd.uniform(0.04, 0.08); h = rnd.uniform(0.3, 0.48)
                K.box((6.5, y + 0.02 + h / 2, zz + w / 2), (0.3, h, w), pm(rnd.choice(["#5a1e1a", "#1e2a3a", "#3a3a1e", "#6a4a1e", "#2a1e14"]), 0.6), 0.0, 0.003); zz += w + 0.005
    # the desk: carved front, leather top, papers, the newspaper, inkwell, a telephone, a lamp; a heavy chair
    K.box((0.6, 0.4, 2.6), (2.6, 0.8, 1.2), dark, 0.0, 0.02); K.box((0.6, 0.82, 2.6), (2.75, 0.05, 1.3), dark, 0.0, 0.01)
    K.box((0.6, 0.85, 2.6), (2.2, 0.01, 0.9), pm("#2a3a24", 0.6), 0.0, 0.0)
    for k in range(4): K.box((-0.4 + k * 0.67, 0.4, 1.98), (0.5, 0.6, 0.02), oak, 0.0, 0.01)
    for k in range(5): K.box((0.2 + rnd.uniform(-0.2, 0.2), 0.86 + k * 0.003, 2.7 + rnd.uniform(-0.1, 0.1)), (0.24, 0.002, 0.32), paper("#efe4c8", 0.3), rnd.uniform(-0.3, 0.3), 0.0)
    inkwell("rink", (1.4, 0.85, 2.4)); cup("rcup", (1.75, 0.85, 2.85), "#f2ece0")
    K.box((1.2, 0.9, 2.95), (0.24, 0.1, 0.18), pm("#141414", 0.3, 0.2), 0.0, 0.01); K.cyl((1.2, 1.0, 2.95), 0.025, 0.26, pm("#141414", 0.3, 0.2), 8, "z")
    lathe("rlamp", [(0.0, 0.0), (0.08, 0.0), (0.03, 0.02), (0.015, 0.4), (0.0, 0.4)], (-0.4, 0.85, 3.0), brass(), 18)
    lathe("rlsh", [(0.08, 0.4), (0.2, 0.3), (0.21, 0.29)], (-0.4, 0.85, 3.0), mat_once("rlshm", lambda: lib.principled("rlshm", hexc("#2a5a3a"), 0.3, 0.3)), 24, cap=False)
    lib.light("POINT", T(-0.4, 1.12, 3.0), 30, (1.0, 0.7, 0.4), 0.05)
    K.box((0.6, 0.5, 3.6), (0.75, 0.08, 0.7), pm("#5a1e1a", 0.8), 0.0, 0.03); K.box((0.6, 1.1, 3.95), (0.75, 1.2, 0.1), dark, 0.0, 0.02)
    for sx in (-0.33, 0.33):
        for sz in (3.3, 3.9): K.cyl((0.6 + sx, 0.25, sz), 0.035, 0.5, dark, 8)
    # the globe: brass meridian, wooden stand, the world map turning
    K.cyl((GLOBE[0], 0.3, GLOBE[2]), 0.32, 0.06, dark, 24); K.cyl((GLOBE[0], 0.4, GLOBE[2]), 0.05, 0.6, dark, 12)
    for j in range(3):
        a = j / 3 * math.tau; tube(f"gleg{j}", [(GLOBE[0] + 0.4 * math.cos(a), 0, GLOBE[2] + 0.4 * math.sin(a)), (GLOBE[0] + 0.22 * math.cos(a), 0.33, GLOBE[2] + 0.22 * math.sin(a))], 0.03, dark, res=2, bres=1)
    K.torus((GLOBE[0], GLOBE[1], GLOBE[2]), 0.62, 0.025, dark, 40, 8, "y")
    K.build()
    tube("gmerid", [(GLOBE[0] + 0.58 * math.sin(a / 20 * math.pi), GLOBE[1] + 0.58 * math.cos(a / 20 * math.pi), GLOBE[2]) for a in range(21)], 0.015, brass(), res=2, bres=1)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.55, location=T(*GLOBE)); globe = bpy.context.object
    bpy.ops.object.shade_smooth(); globe.data.materials.append(map_mat("rglobe", "map_world.png", 0.35))
    globe.rotation_mode = "XYZ"
    # generals' side: a map stand with a map of Europe and Russia, a side table with a cognac decanter
    K2 = Kit("rk2")
    K2.box((4.6, 1.6, 4.4), (2.0, 1.3, 0.04), pm("#e8dcc0", 0.8), -0.5, 0.0)
    K2.box((4.6, 0.9, 4.4), (0.06, 1.8, 0.06), dark, -0.5, 0.0)
    K2.box((-3.4, 0.4, 5.5), (1.2, 0.8, 0.7), dark, 0.0, 0.02)
    K2.build()
    wm = mat_once("rwmap", lambda: map_mat("rwmap", "map_table.png", 0.6))
    ikit.panel("rmapp", (4.6 - 0.02 * math.sin(-0.5), 1.6, 4.4 - 0.025), 1.9, 1.2, wm, -0.5)
    lathe("rdec", [(0.0, 0.0), (0.08, 0.0), (0.1, 0.1), (0.04, 0.22), (0.03, 0.3), (0.0, 0.3)], (-3.6, 0.8, 5.5), CK.mat_once("rdecm", lambda: lib.principled("rdecm", hexc("#8a4a14"), 0.05)), 20)
    # light: cold window daylight from behind, the desk lamp, the fire, a warm fill from the camera side
    CK.area((0.6, 3.2, 6.6), (0.6, 1.0, 2.5), 900, (0.7, 0.8, 1.0), 9, 3)
    CK.area((-1.0, 3.0, -2.5), (0, 1.2, 2.6), 280, (1.0, 0.78, 0.55), 4)
    CK.area((5.5, 3.0, 0.5), (1.5, 1.2, 3.0), 120, (1.0, 0.7, 0.45), 2)
    def update(f):
        u = min(1.0, max(0.0, (f - 1560) / 40.0)); u = u * u * (3 - 2 * u)
        globe.rotation_euler = (0, math.radians(-23.4) * 0, G_EUROPE + (G_AMERICA - G_EUROPE) * u)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
