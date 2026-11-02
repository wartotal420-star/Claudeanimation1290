# Yalta, February 1945 (chapter 12): the Livadia Palace terrace above the Black Sea - white limestone arcades, cypresses,
# a balustrade over the sea, the three Allied flags - and a round table with a cake shaped like Germany (outline from
# Natural Earth), cut into the four occupation zones (the pieces part in update() during ZONE_SHOTS).
# Late-winter sun from the sea side (screen left), cool sky, warm bounce off the stone.
# Layout (three, y up): terrace floor y 0, x -12..12, z -6..9; round table at (0, 0, 3) r 1.35, top y 0.76; the cake
#   centred (0, 0.78, 3.0), ~0.45 x 0.6 m, north = +z, east = -x (reads correctly from cameras at z < 3);
#   seats: Churchill (-1.15, 0, 3.75), Roosevelt (0, 0, 4.25), Stalin (1.15, 0, 3.75) (characters in mode "chair");
#   the arcade at z 9.2 (facing -z); balustrade along x 8.5 (sea beyond, x > 9); flagpoles at (-4, 7.5) (-2.2, 7.8) (2.2, 7.8).
import bpy, math, random, json, os
from mathutils import Vector, Matrix, noise
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text, cup
from sets.front import sea_mat, flag as wave_flag
from sets import c09_kit as K
from sets import ikit
import numpy as np

bx, cy = K.bx, K.cy
ZONE_SHOTS = (5,)
CAKE = (0.0, 0.78, 3.0)
S_ = 0.078
def su_flag_img(w=384, h=256):
    a = ikit.canvas(h, w, "#c8202c")
    ikit.poly(a, [(60 + 22 * math.cos(math.pi / 2 + k * math.pi * 4 / 5), 60 - 22 * math.sin(math.pi / 2 + k * math.pi * 4 / 5)) for k in range(5)], "#f2d040")
    ikit.ellipse(a, 52, 92, 20, 20, "#f2d040", ring=0.25)
    ikit.rect(a, 40, 84, 70, 92, "#f2d040")
    ikit.shade(a, 0.06, 7, 16); return a
def flagm(kind):
    return K.mat_once("c12flag" + kind, lambda: ikit.img_mat("c12flag" + kind, su_flag_img() if kind == "su" else ikit.flag_img(kind), 0.75, sheen=0.4))
def clip(poly, f):
    """Sutherland-Hodgman: keep the part where f(p) >= 0 (f linear)"""
    out = []
    for i in range(len(poly)):
        a, b = poly[i - 1], poly[i]; fa, fb = f(a), f(b)
        if fb >= 0:
            if fa < 0: t = fa / (fa - fb); out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            out.append(b)
        elif fa >= 0: t = fa / (fa - fb); out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out
def germany():
    G = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps", "ne_50m_countries.geojson")))
    for f in G["features"]:
        if f["properties"]["ADM0_A3"] == "DEU":
            g = f["geometry"]; parts = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            return max((p[0] for p in parts), key=len)
def build(M, D):
    rnd = random.Random(1945)
    K.sky("#6a9ad0", "#e8e0d0", 1.0, "#5a8ac8", "#f0e8d8")
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(400, -40, 0)); o = bpy.context.object; o.scale = (900, 900, 1); bpy.ops.object.transform_apply(scale=True); o.data.materials.append(sea_mat())
    stone = K.mat_once("c12lime", lambda: worn("c12lime", "#ece6d8", "#a89e8c", 0.75, 0.0, 1.0, 0.6, "#d8cfbc"))
    floor = K.mat_once("c12flagst", lambda: lib.tiles("c12flagst", "#d8d0c0", "#c8bea8", "#8a8070", 1.0))
    bx("terrace", (0, -0.1, 1.5), (26, 0.2, 17), floor, 0)
    bx("cliff", (20, -21, 1.5), (16, 42, 60), K.mat_once("c12rock", lambda: worn("c12rock", "#8a8070", "#5a5048", 0.9, 0.0, 0.3, 0.55)), 0)
    # the arcade: two storeys of round arches, windows behind, a cornice; ivy patches
    dark = K.mat_once("c12shade", lambda: lib.principled("c12shade", lib.hexc("#3a3430"), 0.9))
    for k in range(9):
        x_ = -12 + k * 3
        cy(f"acol{k}", (x_, 2.0, 9.0), 0.28, 4.0, stone, 20)
        cy(f"acap{k}", (x_, 4.05, 9.0), 0.4, 0.2, stone, 20)
        if k < 8:
            for j in range(9):
                a = math.pi * j / 8; bx(f"aarc{k}{j}", (x_ + 1.5 + 1.25 * math.cos(a), 4.3 + 1.0 * math.sin(a), 9.0), (0.4, 0.25, 0.5), stone, 0.01)
    bx("aback", (0, 3.2, 11.5), (26, 6.4, 0.3), K.mat_once("c12wall", lambda: lib.plaster("c12wall", "#e4dccb")), 0)
    for k in range(8):
        bx(f"awin{k}", (-10.5 + k * 3, 2.4, 11.3), (1.1, 2.4, 0.06), K.mat_once("c12win", lambda: lib.principled("c12win", lib.hexc("#2a3440"), 0.1, 0.2)), 0.0)
        bx(f"awf{k}", (-10.5 + k * 3, 2.4, 11.28), (1.3, 2.6, 0.04), stone, 0.01)
    bx("aupper", (0, 7.2, 9.6), (26, 3.0, 1.4), stone, 0.02); bx("acorn", (0, 8.85, 9.4), (26.6, 0.4, 1.8), stone, 0.02)
    for k in range(12): bx(f"auw{k}", (-11 + k * 2, 7.2, 8.88), (0.8, 1.4, 0.06), K.mat_once("c12win", lambda: None), 0.0)
    bx("aroof", (0, 5.0, 10.3), (26, 0.3, 2.6), stone, 0.01)
    ivy = K.mat_once("c12ivy", lambda: lib.principled("c12ivy", lib.hexc("#2e4a26"), 0.8))
    for k in range(10): K.blob3(f"ivy{k}", (-12 + rnd.uniform(0, 24), rnd.uniform(1, 7), 8.6), (rnd.uniform(0.6, 1.4), rnd.uniform(0.8, 2.0), 0.25), ivy, 0.2, k)
    # balustrade over the sea, cypresses, urns with box shrubs, flagpoles with the three flags
    for k in range(30):
        z_ = -6 + k * 0.5; lathe(f"bal{k}", [(0.0, 0.0), (0.1, 0.0), (0.06, 0.2), (0.12, 0.5), (0.06, 0.75), (0.1, 0.85), (0.0, 0.85)], (8.5, 0, z_), stone, 12)
    bx("balrail", (8.5, 0.92, 1.4), (0.35, 0.14, 15), stone, 0.02); bx("balbase", (8.5, 0.05, 1.4), (0.4, 0.1, 15), stone, 0.01)
    cyp = K.mat_once("c12cyp", lambda: lib.principled("c12cyp", lib.hexc("#1e3a22"), 0.85))
    for k, (x_, z_) in enumerate(((-11, 6), (-9.5, 7.2), (10.5, 10), (12, 7), (11, 4), (-13, 2))):
        lathe(f"cyp{k}", [(0.0, 0.0), (0.7, 0.5), (0.9, 2.5), (0.7, 5.5), (0.3, 7.8), (0.0, 8.6)], (x_, 0, z_), cyp, 14)
    for k, x_ in enumerate((-6, 6)):
        lathe(f"urn{k}", [(0.0, 0.0), (0.3, 0.0), (0.25, 0.25), (0.5, 0.6), (0.45, 0.9), (0.0, 0.9)], (x_, 0, 7.0), stone, 20)
        K.blob3(f"box{k}", (x_, 1.2, 7.0), (0.55, 0.5, 0.55), ivy, 0.08, k)
    for k, (x_, z_, kind) in enumerate(((-4.0, 7.6, "uk"), (-2.2, 7.9, "us"), (2.2, 7.9, "su"))):
        tube(f"fpole{k}", [(x_, 0, z_), (x_, 6.5, z_)], 0.05, pmat("c12pole", "#e8e4d8", 0.4), res=2, bres=1)
        wave_flag(f"flag{k}", (x_, 6.4, z_), 1.6, 1.05, (1, 0.25), flagm(kind), 0.1)
    # ---------- the table and the cake ----------
    cloth = K.mat_once("c12cloth", lambda: lib.cloth("c12cloth", "#f4f0e6"))
    lathe("tcloth", [(0.0, 0.76), (1.38, 0.76), (1.42, 0.72), (1.44, 0.3), (1.4, 0.28), (0.0, 0.28)], (0, 0, 3), cloth, 48)
    for k in range(3): cup(f"tcup{k}", (-0.95 + k * 0.95, 0.765, 2.35 + (k % 2) * 0.1), "#f2ece0", True)
    for k in range(3): lathe(f"tglass{k}", [(0.0, 0.0), (0.03, 0.0), (0.01, 0.01), (0.008, 0.12), (0.04, 0.16), (0.045, 0.24), (0.0, 0.24)], (-0.7 + k * 0.7, 0.765, 3.7), lib.glass("c12glass"), 16)
    lathe("cakeplate", [(0.0, 0.0), (0.45, 0.0), (0.47, 0.012), (0.0, 0.012)], (0, 0.765, 3.0), K.mat_once("c12plate", lambda: lib.principled("c12plate", lib.hexc("#f4f2ee"), 0.2)), 40)
    tube("knife", [(0.38, 0.79, 2.6), (0.62, 0.79, 2.5)], 0.008, pmat("c12silver", "#d8d8dc", 0.2, 1.0), res=2, bres=0)
    bx("knifeh", (0.7, 0.79, 2.47), (0.14, 0.02, 0.03), wood_mat("c12kh", "#3a2414", "#1e120a", 8, 0.4), 0.005, 0.4)
    pieces = cake()
    for k, (x_, z_) in enumerate(((-3.2, 1.0), (3.2, 1.0), (-2.0, -1.0), (2.0, -1.0), (0.0, 5.6))):
        cy(f"stool{k}", (x_, 0.25, z_), 0.25, 0.5, stone, 16)
    K.sun((0.9, 0.45, -0.2), 4.0, (1.0, 0.88, 0.72), 1.5)
    K.area((-6, 20, -20), (0, 0, 5), 12000, (0.65, 0.78, 1.0), 40)
    K.area((0, 3, -4), (0, 1.0, 3.5), 900, (1.0, 0.86, 0.7), 6)
    def update(f):
        on = D.get("id") in ZONE_SHOTS and D.get("set") == "c12_yalta"
        u = 0.0
        if on: u = max(0.0, min(1.0, (f - D["a"] - 12) / 22.0)); u = u * u * (3 - 2 * u)
        for o, (dx, dz) in pieces: o.location = T(CAKE[0] + dx * 0.09 * u, 0, CAKE[2] + dz * 0.09 * u)
    update(D.get("a", 0))
    return {"update": update}
def cake():
    ring = [(lo, la) for lo, la in germany()]
    zones = {
        "su": clip(ring, lambda p: p[0] - 10.9),
        "uk": clip(clip(ring, lambda p: 10.9 - p[0]), lambda p: p[1] - 51.5),
        "us": clip(clip(clip(ring, lambda p: 10.9 - p[0]), lambda p: 51.5 - p[1]), lambda p: p[0] - 8.1),
        "fr": clip(clip(ring, lambda p: 51.5 - p[1]), lambda p: 8.1 - p[0]),
    }
    sponge = K.mat_once("c12sponge", lambda: worn("c12sponge", "#d8a868", "#a8743a", 0.8, 0.0, 30, 0.5, "#c8945a"))
    icing = K.mat_once("c12icing", lambda: lib.principled("c12icing", lib.hexc("#f6f0e4"), 0.35))
    jam = K.mat_once("c12jam", lambda: lib.principled("c12jam", lib.hexc("#9a1e2a"), 0.3))
    cl, cb = 10.4, 51.2
    out = []
    for name, poly in zones.items():
        if len(poly) < 3: continue
        pts = [(-(lo - cl) * 0.63 * S_, (la - cb) * S_) for lo, la in poly]
        cx = sum(p[0] for p in pts) / len(pts); cz = sum(p[1] for p in pts) / len(pts)
        n = len(pts); objs = []
        for (y0, y1, m) in ((0.0, 0.05, sponge), (0.05, 0.06, jam), (0.06, 0.11, sponge), (0.11, 0.125, icing)):
            vs = [(x, CAKE[1] + y0, z) for x, z in pts] + [(x, CAKE[1] + y1, z) for x, z in pts]
            fs = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
            objs.append(mesh_obj(f"cake{name}{y0}", vs, fs, m))
        root = bpy.data.objects.new(f"cake{name}", None); link(root)
        for o in objs: o.parent = root
        # a toothpick flag on each zone
        fx, fz = cx * 0.85, cz * 0.85
        tube(f"pick{name}", [(fx, CAKE[1] + 0.12, fz), (fx, CAKE[1] + 0.28, fz)], 0.003, pmat("c12pick", "#e8d8b0", 0.6), res=2, bres=0).parent = root
        o = K.img_plane(f"pflag{name}", (fx - 0.045, CAKE[1] + 0.25, fz), 0.08, 0.055, flagm(name)); o.parent = root
        L = math.hypot(cx, cz) or 1.0
        out.append((root, (cx / L, cz / L)))
    return out
