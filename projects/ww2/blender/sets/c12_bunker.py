# The bunker under Berlin, 30 April 1945 (chapter 12), handled soberly: a long low concrete corridor with pipes and
# cables, caged bulbs, a field telephone, a bench, maps pinned up, water on the floor; at its end a small room with a
# sofa, seen through a heavy steel door that slowly swings shut in update() during DOOR_SHOTS.
# Layout (three, y up): corridor x -1.4..1.4, z -6..10, floor y 0, ceiling 2.3; the doorway at z 10 (x -0.55..0.55,
#   2.0 high), the door hinged at x +0.55 swinging into the corridor; the room beyond z 10.2..14 (x -2.5..2.5) with the
#   sofa against the back wall (z 13.6); the seated figure goes at (0.2, 0, 13.0) (mode "chair", chair: false).
import bpy, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text
from sets.warroom import phone, chair
from sets import c09_kit as K

bx, cy = K.bx, K.cy
DOOR_SHOTS = (11,)
def build(M, D):
    rnd = random.Random(1945)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.0, 0.0, 0.0, 1); bg.inputs[1].default_value = 1.0
    conc = K.mat_once("c12conc", lambda: worn("c12conc", "#8a867c", "#4a4640", 0.85, 0.0, 1.5, 0.58, "#6a665e"))
    conc2 = K.mat_once("c12conc2", lambda: worn("c12conc2", "#6a6660", "#3a3632", 0.85, 0.0, 2.5, 0.55, "#5a564e"))
    bx("floor", (0, -0.05, 4), (6, 0.1, 22), K.mat_once("c12wetfl", lambda: worn("c12wetfl", "#4a4640", "#2a2826", 0.25, 0.0, 1.2, 0.5, "#3a3834")), 0)
    for sd in (-1, 1): bx(f"wall{sd}", (sd * 1.55, 1.15, 2), (0.3, 2.3, 16), conc, 0.01)
    bx("ceil", (0, 2.4, 2), (3.4, 0.2, 16), conc2, 0)
    bx("back0", (0, 1.15, -6.1), (3.4, 2.3, 0.2), conc, 0)
    for sd in (-1, 1): bx(f"endw{sd}", (sd * 1.0, 1.15, 10.0), (0.9, 2.3, 0.3), conc, 0.01)
    bx("lintel", (0, 2.15, 10.0), (1.2, 0.3, 0.3), conc, 0.01)
    # pipes and cables along the ceiling and walls, caged bulbs
    for k, (x_, y_, r) in enumerate(((-1.25, 2.15, 0.07), (-1.05, 2.2, 0.05), (1.2, 2.1, 0.09), (1.32, 1.8, 0.03), (1.32, 1.7, 0.03))):
        tube(f"pipe{k}", [(x_, y_, -6), (x_, y_, 9.8)], r, pmat(f"c12pipe{k % 2}", ["#5a5e58", "#6a4a3a"][k % 2], 0.5, 0.6), res=2, bres=1)
    for k in range(5):
        z_ = -4 + k * 3.2
        lathe(f"cage{k}", [(0.0, 0.0), (0.08, -0.05), (0.09, -0.18), (0.0, -0.22)], (0, 2.3, z_), pmat("c12cage", "#2a2a28", 0.5, 0.6), 8, cap=False)
        lathe(f"bulb{k}", [(0.0, -0.04), (0.05, -0.08), (0.04, -0.16), (0.0, -0.18)], (0, 2.3, z_), lib.emit("c12bulb", (1.0, 0.72, 0.42), 14 if k != 2 else 2), 12)
        if k != 2: lib.light("POINT", T(0, 2.05, z_), 28, (1.0, 0.7, 0.42), 0.05).visible_camera = False
    # furniture: bench, phone on a shelf, maps pinned up, a stack of crates, a gas mask hanging, papers on the floor
    WD = wood_mat("c12wood", "#5a4430", "#2e2218", 6, 0.6)
    bx("bench", (-1.15, 0.45, 2.0), (0.4, 0.06, 2.4), WD, 0.01)
    for sz in (-1, 1): bx(f"benchl{sz}", (-1.15, 0.22, 2.0 + sz * 1.1), (0.36, 0.44, 0.06), WD, 0.005)
    bx("shelf", (1.25, 1.05, 4.5), (0.3, 0.04, 0.8), WD, 0.005); phone("bphone", (1.22, 1.07, 4.5), -1.57)
    for k in range(3):
        bx(f"bmap{k}", (1.39, 1.5, -1.5 + k * 1.3), (0.01, 0.6, 0.85), K.mat_once(f"c12bmap{k}", lambda: lib.principled(f"c12bmap{k}", lib.hexc(["#d8cca8", "#c8d0b0", "#e0d4b8"][k]), 0.8)), 0.0)
        for j in range(3): tube(f"bmapl{k}{j}", [(1.38, 1.3 + j * 0.15, -1.8 + k * 1.3), (1.38, 1.4 + j * 0.12, -1.3 + k * 1.3)], 0.006, pmat("kred", "#a81e22", 0.5), res=2, bres=0)
    for k in range(4): bx(f"crate{k}", (1.1, 0.25 + (k // 2) * 0.48, 7.6 + (k % 2) * 0.55), (0.5, 0.46, 0.5), wood_mat("c9crate", "#8a7a52", "#5a4a2a", 10, 0.7), 0.01)
    for k in range(14): bx(f"pap{k}", (rnd.uniform(-1.1, 1.1), 0.004, rnd.uniform(-3, 9)), (0.21, 0.002, 0.29), pmat("kpaper", "#f0e6cc", 0.8), 0, rnd.uniform(0, 3))
    lathe("bucket", [(0.0, 0.0), (0.13, 0.0), (0.16, 0.28), (0.0, 0.28)], (-1.1, 0, 6.5), pmat("c12tin", "#6a6a64", 0.5, 0.6), 16)
    # the room: sofa, side table with a lamp, a framed picture (a landscape), a rug; dim lamp light
    bx("rfloor", (0, -0.04, 12.1), (5, 0.1, 4), K.mat_once("c12rfl", lambda: lib.parquet("c12rfl", "#5a3a22", "#3a2414")), 0)
    for sd in (-1, 1): bx(f"rwall{sd}", (sd * 2.6, 1.15, 12.1), (0.2, 2.3, 4), conc, 0)
    bx("rback", (0, 1.15, 14.1), (5.2, 2.3, 0.2), K.mat_once("c12rwall", lambda: lib.wallpaper("c12rwall", "#6a6a5a", "#5a5a4a")), 0)
    bx("rceil", (0, 2.4, 12.1), (5.2, 0.2, 4), conc2, 0)
    sofa = K.mat_once("c12sofa", lambda: lib.cloth("c12sofa", "#3a4a5a"))
    bx("sofab", (0.2, 0.25, 13.3), (2.0, 0.5, 0.8), sofa, 0.06); bx("sofaback", (0.2, 0.75, 13.7), (2.0, 0.6, 0.25), sofa, 0.06)
    for sd in (-1, 1): bx(f"sofaarm{sd}", (0.2 + sd * 1.05, 0.5, 13.35), (0.2, 0.55, 0.85), sofa, 0.06)
    bx("rtable", (-1.6, 0.55, 13.2), (0.5, 0.05, 0.5), WD, 0.01); bx("rtablel", (-1.6, 0.27, 13.2), (0.06, 0.54, 0.06), WD, 0)
    lathe("rlamp", [(0.0, 0.0), (0.08, 0.0), (0.02, 0.05), (0.02, 0.3), (0.0, 0.3)], (-1.6, 0.58, 13.2), pmat("c12brass", "#a88a4a", 0.3, 1.0), 12)
    lathe("rlampsh", [(0.06, 0.28), (0.16, 0.12), (0.17, 0.11), (0.07, 0.27)], (-1.6, 0.58, 13.2), lib.principled("c12shade", lib.hexc("#e8d8b0"), 0.7, 0.0, (1.0, 0.75, 0.45), 2.0), 20, cap=False)
    lib.light("POINT", T(-1.6, 0.85, 13.2), 18, (1.0, 0.65, 0.35), 0.05).visible_camera = False
    from sets import ikit
    K.img_plane("rpic", (0.2, 1.6, 13.98), 1.0, 0.7, ikit.img_mat("c12pic", ikit.landscape_img(77), 0.6))
    bx("rpicf", (0.2, 1.6, 14.0), (1.1, 0.8, 0.04), wood_mat("c9frame", "#6a4a1a", "#3a2a0a", 9, 0.4), 0.01)
    bx("rrug", (0.2, 0.005, 12.4), (2.4, 0.01, 1.6), lib.carpet("c12rug", "#5a1e1e", "#a88a4a"), 0)
    # the steel door, hinged at x +0.55, z 10.15
    door = K.mat_once("c12door", lambda: worn("c12door", "#4a4e4a", "#2a2c2a", 0.5, 0.6, 6, 0.65, "#3a3a38"))
    hinge = bpy.data.objects.new("hinge", None); link(hinge); hinge.location = T(0.55, 0, 9.85)
    parts = [bx("door", (0.55 - 0.55, 1.0, 9.85), (1.1, 2.0, 0.1), door, 0.01), bx("dwheel", (0.55 - 0.55, 1.1, 9.78), (0.06, 0.06, 0.04), door, 0.0)]
    parts.append(K.wheel("dhand", K.P_of(0.0, 9.77, 0, 0), 0, 1.1, 0, 0.18, 0.03, pmat("c12handle", "#2a2a2a", 0.4, 0.8), math.pi / 2, 16))
    for k in range(4): parts.append(bx(f"drivet{k}", (0.55 - 0.55 + (k % 2 - 0.5) * 0.9, 0.2 + (k // 2) * 1.6, 9.79), (0.05, 0.05, 0.03), door, 0.0))
    for o in parts:
        o.parent = hinge
    bpy.context.view_layer.update()
    for o in parts: o.matrix_parent_inverse = hinge.matrix_world.inverted()
    K.area((0, 1.6, -5.5), (0, 1.0, 6), 30, (0.7, 0.75, 0.85), 2)
    def update(f):
        if D.get("id") in DOOR_SHOTS and D.get("set") == "c12_bunker":
            u = max(0.0, min(1.0, (f - D["a"] - 100) / 90.0)); u = u * u * (3 - 2 * u)
        else: u = 0.0
        hinge.rotation_euler = (0, 0, math.radians(-100) * (1 - u))
    update(D.get("a", 0))
    return {"update": update}
