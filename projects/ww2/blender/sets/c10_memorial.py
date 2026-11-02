# The memorial hall (chapter 10): a dim, quiet museum room. Behind low glass, a mound of thousands of worn shoes; a heap
# of suitcases with painted names; a tall wall of family photographs (sepia portraits in plain frames); rows of memorial
# candles on a dark stone ledge; a single stem of white flowers. Warm candlelight against cool, faint skylight.
# Layout (three, y up): hall x -8..8, z -4..12, floor y 0, ceiling 4.5. Shoe mound x -6.5..-1.2, z 3..9 (behind a glass
# barrier at z 2.6, x -6.6..-1.0); suitcases x 1.2..6.5, z 3.5..8.5; the photograph wall on the back wall z 11.8, x -7..7,
# y 0.6..4.2; the candle ledge x -2.5..2.5, z 0.6..1.2 (top y 0.42); the flower lies on the ledge at (0.3, 0.43, 0.9).
import bpy, math, random
import numpy as np
from mathutils import Vector, Matrix
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text, candle
from sets import c09_kit as K
from sets import ikit

bx, cy = K.bx, K.cy
def build(M, D):
    rnd = random.Random(10)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.005, 0.005, 0.008, 1); bg.inputs[1].default_value = 1.0
    stone = K.mat_once("c10stone", lambda: worn("c10stone", "#4a4644", "#2a2826", 0.7, 0.0, 2, 0.6, "#3a3634"))
    wall = K.mat_once("c10wall", lambda: lib.plaster("c10wall", "#3a3836"))
    bx("floor", (0, -0.05, 4), (17, 0.1, 17), K.mat_once("c10floor", lambda: lib.tiles("c10floor", "#3a3836", "#34322f", "#1e1c1a", 1.2)), 0)
    bx("ceil", (0, 4.55, 4), (17, 0.1, 17), wall, 0)
    for sd in (-1, 1): bx(f"side{sd}", (sd * 8.1, 2.25, 4), (0.2, 4.5, 17), wall, 0)
    bx("back", (0, 2.25, 12.1), (17, 4.5, 0.2), wall, 0); bx("front", (0, 2.25, -4.6), (17, 4.5, 0.2), wall, 0)
    for k in range(5): bx(f"slit{k}", (-6 + k * 3, 4.49, 4), (0.4, 0.02, 14), lib.emit("c10sky", (0.55, 0.62, 0.75), 0.6), 0)
    # ---------- the shoe mound behind glass ----------
    bx("glass", (-3.8, 0.55, 2.6), (5.6, 1.1, 0.02), lib.glass("c10glass"), 0)
    bx("glrail", (-3.8, 1.11, 2.6), (5.7, 0.04, 0.06), pmat("c10steel", "#2a2a2a", 0.4, 0.8), 0.003)
    bx("plinth", (-3.8, 0.06, 6), (5.8, 0.12, 6.8), stone, 0.01)
    leathers = ["#3a2a20", "#2a2220", "#4a3428", "#1e1c1c", "#5a4030", "#3a3434", "#6a4a34", "#2e2a26", "#5a3a2a", "#4a4a44", "#7a5a3a", "#8a3a2a"]
    mats = [K.mat_once(f"c10lea{k}", lambda c=c: worn(f"c10lea{k}", c, "#1a1612", 0.65, 0.0, 12, 0.62, "#2a2018")) for k, c in enumerate(leathers)]
    shoes(mats, rnd)
    # ---------- the suitcase heap ----------
    from sets.kit_sbpw import Kit
    KC = Kit("cases"); cases = ["#6a4a2e", "#4a3a2e", "#7a5a3a", "#3a3a3a", "#5a4030", "#8a6a4a", "#5a2a22", "#3a4a3a"]
    cm = [K.mat_once(f"c10case{k}", lambda c=c: worn(f"c10case{k}", c, "#2a1e14", 0.6, 0.1, 6, 0.62, "#2a1e14")) for k, c in enumerate(cases)]
    for k in range(110):
        r = rnd.random() ** 0.6; a = rnd.random() * math.tau
        x_, z_ = 3.9 + 2.4 * r * math.cos(a), 6.0 + 2.2 * r * math.sin(a)
        y_ = 0.12 + (1.0 - r) * 1.5 * rnd.uniform(0.6, 1.0)
        w, h, d = rnd.uniform(0.5, 0.8), rnd.uniform(0.14, 0.24), rnd.uniform(0.32, 0.46)
        KC.box((x_, y_, z_), (w, h, d), cm[k % 8], rnd.uniform(0, 3), 0.025, rnd.uniform(-0.4, 0.4), rnd.uniform(-0.3, 0.3))
    KC.build()
    names = ["Hanna Fischer\nWien", "Max Rosenberg\nFrankfurt", "Eva Klein\nBudapest", "Josef Levi\nPrag", "Ruth Weiss\nAmsterdam", "Samuel Kahn\nBerlin", "Lea Goldmann\nKöln", "Isaak Baum\nWarschau"]
    for k, nm in enumerate(names):
        x_, z_ = 1.7 + (k % 4) * 1.15, 3.55 + (k // 4) * 0.25; yaw = rnd.uniform(-0.15, 0.15)
        y_ = 0.2 + (k // 4) * 0.42
        bx(f"ncase{k}", (x_, y_, z_), (0.95, 0.42, 0.26), cm[k], 0.03, yaw)
        bx(f"nhandle{k}", (x_, y_ + 0.24, z_), (0.2, 0.04, 0.05), pmat("c10handle", "#2a1e14", 0.5), 0.005, yaw)
        text(nm, (x_, y_ + 0.04, z_ - 0.135), 0.065, pmat("c10paint", "#e8e4d8", 0.7), yaw=yaw, flat=False)
    # ---------- the photograph wall ----------
    pics = []
    for k in range(24):
        a = ikit.portrait_img(100 + k)
        lum = a[..., :3].mean(axis=2, keepdims=True); sep = np.concatenate([lum * 1.08, lum * 0.92, lum * 0.72], axis=2)
        a2 = a.copy(); a2[..., :3] = np.clip(sep * 0.95 + 0.04, 0, 1)
        pics.append(ikit.img_mat(f"c10ph{k}", a2, 0.6))
    frame = wood_mat("c10frame", "#2a1e16", "#140e0a", 8, 0.5)
    for r in range(6):
        for k in range(16):
            x_ = -7.0 + k * 0.93 + (r % 2) * 0.15; y_ = 0.85 + r * 0.6
            w_, h_ = 0.5 + (k * 7 + r * 3) % 3 * 0.06, 0.58
            bx(f"pf{r}{k}", (x_, y_, 11.96), (w_ + 0.06, h_ + 0.06, 0.04), frame, 0.004)
            K.img_plane(f"pp{r}{k}", (x_, y_, 11.93), w_, h_ * 0.95, pics[(r * 5 + k * 3) % 24])
    for k in range(9): bx(f"plight{k}", (-6.4 + k * 1.6, 4.35, 11.6), (0.5, 0.06, 0.12), pmat("c10steel", "#2a2a2a", 0.4, 0.8), 0.003)
    # ---------- the candle ledge and a white flower ----------
    bx("ledge", (0, 0.21, 0.9), (5.4, 0.42, 0.75), stone, 0.01)
    for k in range(13):
        x_ = -2.4 + k * 0.4 + rnd.uniform(-0.05, 0.05); z_ = 0.75 + (k % 2) * 0.28
        glassc = K.mat_once("c10votive", lambda: lib.principled("c10votive", lib.hexc("#e8dcc8"), 0.2, 0.0))
        lathe(f"vot{k}", [(0.0, 0.0), (0.05, 0.0), (0.055, 0.1), (0.0, 0.1)], (x_, 0.42, z_), glassc, 14)
        from sets.void import flame, flame_mat
        flame(f"vfl{k}", (x_, 0.53, z_), 0.06, 0.012, K.mat_once("flamemat", lambda: flame_mat("flame")), seed=k)
        lib.light("POINT", T(x_, 0.6, z_), 6, (1.0, 0.6, 0.28), 0.02).visible_camera = False
    for k in range(3): candle(f"tall{k}", (-1.8 + k * 1.8, 0.42, 1.1), 0.28, k + 20, 2.5)
    stem = K.mat_once("c10stem", lambda: lib.principled("c10stem", lib.hexc("#3a5a2a"), 0.6))
    tube("fstem", [(0.0, 0.43, 0.95), (0.3, 0.44, 0.88), (0.6, 0.435, 0.8)], 0.007, stem, res=4, bres=0)
    for k in range(6):
        a = k / 6 * math.tau; K.blob3(f"petal{k}", (0.63 + 0.035 * math.cos(a), 0.45, 0.8 + 0.035 * math.sin(a)), (0.04, 0.02, 0.03), K.mat_once("c10petal", lambda: lib.principled("c10petal", lib.hexc("#f4f2ec"), 0.5)), 0.005, k)
    # quiet lights: candle warmth on the ledge, picture lights on the wall, a soft cool skylight
    K.area((0, 0.9, 0.2), (0, 0.4, 1.0), 25, (1.0, 0.62, 0.3), 2.0)
    for k in range(9): K.spot((-6.4 + k * 1.6, 4.3, 11.4), (-6.4 + k * 1.6, 1.8, 11.9), 60, (1.0, 0.8, 0.6), 50, 0.7)
    K.area((-3.8, 4.3, 6), (-3.8, 0, 6), 160, (0.7, 0.78, 0.95), 4)
    K.area((3.9, 4.3, 6), (3.9, 0, 6), 120, (0.8, 0.8, 0.9), 4)
    K.area((0, 3.0, -4.0), (0, 1, 6), 60, (0.9, 0.75, 0.6), 6)
    return {}
def shoes(mats, rnd):
    """a mound of ~1600 worn shoes: each a low lathed body with toe-cap, heel and opening, scattered and tilted"""
    import bmesh
    groups = {}
    for k in range(1600):
        r = rnd.random() ** 0.55; a = rnd.random() * math.tau
        x_, z_ = -3.8 + 2.6 * r * math.cos(a), 6.0 + 2.9 * r * math.sin(a)
        y_ = 0.12 + (1 - r) ** 1.3 * 1.25 + rnd.uniform(0, 0.06)
        L = rnd.uniform(0.22, 0.3) * (0.7 if rnd.random() < 0.15 else 1.0)
        bm = groups.setdefault(k % len(mats), bmesh.new())
        M = Matrix.Translation(T(x_, y_, z_)) @ Matrix.Rotation(rnd.uniform(0, math.tau), 4, "Z") @ Matrix.Rotation(rnd.uniform(-0.8, 0.8), 4, "X") @ Matrix.Rotation(rnd.uniform(-0.5, 0.5), 4, "Y")
        # sole + upper as a squashed sphere, the heel block, the dark opening
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0, matrix=M @ Matrix.Diagonal((L / 2, L * 0.2, L * 0.24, 1.0)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=M @ Matrix.Translation((-L * 0.38, 0, -L * 0.12)) @ Matrix.Diagonal((L * 0.18, L * 0.32, L * 0.12, 1.0)))
    for i, bm in groups.items():
        me = bpy.data.meshes.new(f"shoes{i}"); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        me.materials.append(mats[i]); link(bpy.data.objects.new(f"shoes{i}", me))
