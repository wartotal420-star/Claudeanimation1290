# Tokyo interiors (chapter 7 shots 28-30: the war cabinet after the Doolittle Raid; c13_radio reuses build_home for the
# family listening to the Emperor's broadcast, chapter 13).
# HQ (build_hq), three.js layout: room x -6..6, z -4..6; the conference table centred (0, 0, 1.6), 4.0 x 1.6, top y 0.78
#   (Tojo stands at its head (0, 0, 2.9), officers along x = +-1.4 at z 0.6..2.4); back wall z 6 with the Pacific wall map
#   at (-2.2, 2.2, 5.9) and a tall window at (2.8, 2.2, 6) looking onto Tokyo rooftops with smoke rising (Doolittle).
#   A toy fleet sits on a small table map at (0, 0.79, 1.4). update(f): a B-25 flashes past the window f 3590..3640.
# Home (build_home): tatami room x -3..3, z -1..4; the radio on a chest at (0, 0.55, 3.2) facing -z; the family kneels on
#   the tatami at z 1.2..2.4 facing +z (toward the radio); shoji at the back (z 4) lit by morning sun; tokonoma on the left.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, poster, paper, brass
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj, map_mat, cup, toy_ship
from sets import c07_kit as CK
from sets import ikit

def calligraphy_img(seed=0, w=128, h=384):
    a = ikit.canvas(h, w, "#efe6cc"); rs = random.Random(seed)
    for col in range(2):
        y = 0.08
        while y < 0.86:
            cx = 0.35 + col * 0.32; s_ = rs.uniform(0.04, 0.07)
            for k in range(rs.randint(3, 5)):
                x0 = cx + rs.uniform(-0.12, 0.08); y0 = y + rs.uniform(0, s_)
                if rs.random() < 0.5: ikit.rect(a, x0, y0, x0 + rs.uniform(0.06, 0.18), y0 + 0.008, "#1a1410")
                else: ikit.rect(a, x0, y0, x0 + 0.025, y0 + rs.uniform(0.02, 0.05), "#1a1410")
            y += s_ + 0.03
    ikit.rect(a, 0.62, 0.88, 0.72, 0.92, "#b8202a")
    return a
def shoji(K, cx, cy, cz, w, h, frame, glow_m, yaw=0.0, nx=4, ny=6):
    ca, sa = math.cos(yaw), math.sin(yaw); P = lambda u, v: (cx + u * ca, cy + v, cz - u * sa)
    K.box(P(0, 0), (w, h, 0.01), glow_m, yaw, 0.0)
    for i in range(nx + 1): K.box(P(-w / 2 + i * w / nx, 0), (0.035, h, 0.04), frame, yaw, 0.0)
    for j in range(ny + 1): K.box(P(0, -h / 2 + j * h / ny), (w, 0.035, 0.04), frame, yaw, 0.0)

def build_hq(M, D):
    rnd = random.Random(1804)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.5, 0.55, 0.65, 1); bg.inputs[1].default_value = 0.5
    K = Kit("hq"); dark = wood("#4a2a18", "#24140a", 5.0, 0.35); light_w = wood("#8a6a44", "#5a4028", 6.0, 0.5)
    wall = mat_once("hqwall", lambda: lib.plaster("hqwall", "#c8bca0"))
    K.box((0, -0.05, 1), (12.2, 0.1, 10.2), mat_once("hqfloor", lambda: lib.parquet("hqfloor", "#7a5030", "#5a3820")), 0.0, 0.0)
    K.box((0, 3.5, 6.05), (12.2, 7, 0.1), wall, 0.0, 0.0); K.box((-6.05, 3.5, 1), (0.1, 7, 10.2), wall, 0.0, 0.0); K.box((6.05, 3.5, 1), (0.1, 7, 10.2), wall, 0.0, 0.0)
    K.box((0, 0.6, 5.95), (12, 1.2, 0.1), dark, 0.0, 0.01); K.box((0, 4.3, 1), (12.2, 0.1, 10.2), pm("#d8ccb0", 0.8), 0.0, 0.0)
    for i in range(5): K.box((-4.8 + i * 2.4, 4.15, 1), (0.25, 0.25, 10), dark, 0.0, 0.0)
    # conference table with green baize, chairs, papers, tea cups, the toy fleet on a table map, an ashtray
    K.box((0, 0.74, 1.6), (4.0, 0.08, 1.6), dark, 0.0, 0.01); K.box((0, 0.785, 1.6), (3.8, 0.01, 1.4), pm("#2a4a2a", 0.85), 0.0, 0.0)
    for sx in (-1.8, 1.8):
        for sz in (0.95, 2.25): K.cyl((sx, 0.36, sz), 0.06, 0.72, dark, 10)
    for k in range(4):
        for sd in (-1, 1):
            cx, cz = sd * 1.35, 0.7 + k * 0.6
            K.box((cx, 0.45, cz), (0.45, 0.07, 0.45), pm("#5a1e1a", 0.8), 0.0, 0.02); K.box((cx + sd * 0.22, 0.85, cz), (0.06, 0.8, 0.45), dark, 0.0, 0.01)
            K.box((cx - sd * 0.45, 0.795, cz), (0.24, 0.003, 0.32), paper("#efe4c8", 0.3), rnd.uniform(-0.2, 0.2), 0.0)
    mm = mat_once("hqmap", lambda: map_mat("hqmap", "c07_pacific.png", 0.6))
    from sets.void import map_plane
    map_plane("hqtmap", -0.9, 0.9, 0.95, 1.85, 0.792, mm)
    for k in range(5): toy_ship(f"hqts{k}", (-0.45 + (k % 3) * 0.12, 0.79, 1.3 + (k // 3) * 0.12), math.pi / 2, 0.12, "#5a6470")
    for k in range(4): cup(f"hqcup{k}", (-1.3 + k * 0.8, 0.79, 0.95 + (k % 2) * 1.3), "#f2ece0", True)
    # back wall: the Pacific map, a plain national flag on a stand, a calligraphy scroll, a clock; the window onto Tokyo
    ikit.panel("hqwmap", (-2.2, 2.3, 5.94), 3.0, 1.48, mm, 0.0)
    for dx, dy, sw, sh in ((0, 0.78, 3.12, 0.06), (0, -0.78, 3.12, 0.06), (1.53, 0, 0.06, 1.6), (-1.53, 0, 0.06, 1.6)): K.box((-2.2 + dx, 2.3 + dy, 5.92), (sw, sh, 0.04), dark, 0.0, 0.0)
    K.cyl((-4.6, 1.2, 5.3), 0.03, 2.4, brass(), 8); K.sphere((-4.6, 2.45, 5.3), 0.06, brass(), 10)
    ikit.flag("hqflag", (-4.62, 2.35, 5.28), 1.1, 0.75, CK.jp_flag_mat(), 0.0, 0.05)
    ikit.panel("hqscroll", (-5.94, 2.2, 3.4), 0.6, 1.8, ikit.img_mat("hqscm", calligraphy_img(3), 0.7), -math.pi / 2)
    win = lib.emit("hqwin", (0.75, 0.82, 0.95), 1.0)
    K.box((2.8, 2.3, 6.0), (2.4, 2.8, 0.02), mat_once("hqglass", lambda: lib.glass("hqglass")), 0.0, 0.0)
    for i in range(4): K.box((1.6 + i * 0.8, 2.3, 5.97), (0.06, 2.8, 0.08), dark, 0.0, 0.0)
    for j in range(5): K.box((2.8, 0.9 + j * 0.7, 5.97), (2.4, 0.06, 0.08), dark, 0.0, 0.0)
    K.build()
    # outside: Tokyo rooftops, a smoke column, sky backdrop
    X = Kit("tokyo"); tile = pm("#3a3c42", 0.6); wl = pm("#b8aa90", 0.8)
    for k in range(60):
        x, z = rnd.uniform(-30, 40), rnd.uniform(14, 90); w, d, h = rnd.uniform(4, 9), rnd.uniform(4, 8), rnd.uniform(2, 8)
        X.box((x, h / 2 - 3, z), (w, h, d), wl, rnd.uniform(-0.2, 0.2), 0.0); X.box((x, h - 2.6, z), (w + 0.8, 0.5, d + 0.8), tile, rnd.uniform(-0.2, 0.2), 0.0)
    X.box((12, 6, 60), (6, 18, 6), pm("#a8a090", 0.8), 0.0, 0.0)
    X.build()
    mesh_obj("tsky", [(-200, -20, 160), (200, -20, 160), (200, 120, 160), (-200, 120, 160)], [(0, 1, 2, 3)], lib.emit("tskym", (0.62, 0.72, 0.88), 1.2))
    CK.smoke("tsmk", (18, 0, 70), 60, 4, 16, "#2a2624", 0.85, (-12, 0), 3, 10)
    b25 = CK.inst(CK.plane("b25", gear=False, spin=True), "hqb25")
    CK.area((2.8, 2.3, 5.5), (0, 1.2, 1.6), 400, (0.75, 0.82, 1.0), 2.4, 2.8)
    CK.area((-2, 3.0, -3), (0, 1.2, 1.6), 260, (1.0, 0.78, 0.55), 4)
    L = lib.light("SPOT", T(0, 4.0, 1.6), 400, (1.0, 0.8, 0.55), 0.2); L.data.spot_size = math.radians(80)
    lathe("hqlamp", [(0.05, 0.0), (0.12, -0.05), (0.5, -0.3), (0.52, -0.32)], (0, 3.6, 1.6), pm("#2a2a2a", 0.4, 0.5), 32, cap=False)
    tube("hqcord", [(0, 3.6, 1.6), (0, 4.3, 1.6)], 0.01, pmat("kcord", "#1a1a1a", 0.6), res=2, bres=0)
    def update(f):
        u = (f - 3590) / 50.0
        b25.hide_render = not (0 <= u <= 1)
        CK.place(b25, (-40 + 90 * u, 24 - 4 * u, 30), (1, -0.05, 0), -0.25, 1.0)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}

def build_home(M, D):
    rnd = random.Random(815)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.9, 0.85, 0.75, 1); bg.inputs[1].default_value = 0.3
    K = Kit("home"); cedar = wood("#8a6a44", "#5a4028", 6.0, 0.6); dark = wood("#4a3220", "#2a1a10", 5.0, 0.5)
    tat = mat_once("tatami", lambda: lib.brickmat("tatami", "#b8a868", "#a89858", "#3a3020", 1.1, 1.8, 0.9, 0.9))
    K.box((0, -0.05, 1.5), (6.2, 0.1, 5.2), tat, 0.0, 0.0)
    plaster = mat_once("hmwall", lambda: lib.plaster("hmwall", "#c8b48a"))
    K.box((-3.05, 1.3, 1.5), (0.1, 2.6, 5.2), plaster, 0.0, 0.0); K.box((3.05, 1.3, 1.5), (0.1, 2.6, 5.2), plaster, 0.0, 0.0)
    K.box((0, 2.65, 1.5), (6.2, 0.1, 5.2), cedar, 0.0, 0.0)
    for x in (-3.0, -1.0, 1.0, 3.0): K.box((x, 1.3, 4.0), (0.12, 2.6, 0.12), dark, 0.0, 0.0)
    K.box((0, 2.0, 4.0), (6.0, 0.12, 0.14), dark, 0.0, 0.0)
    glow = lib.emit("shojiglow", (1.0, 0.92, 0.78), 2.2)
    for k, x in enumerate((-2.0, 0.0, 2.0)): shoji(K, x, 1.0, 4.02, 1.85, 1.9, cedar, glow)
    K.box((0, 2.33, 4.02), (6.0, 0.6, 0.02), plaster, 0.0, 0.0)
    # tokonoma alcove on the left: scroll, an ikebana vase; a chest with the radio; a low table with tea; cushions
    K.box((-2.98, 0.08, 2.0), (0.04, 0.16, 1.8), dark, 0.0, 0.0)
    ikit.panel("hmscroll", (-2.98, 1.4, 2.0), 0.5, 1.4, ikit.img_mat("hmscm", calligraphy_img(7), 0.7), -math.pi / 2)
    lathe("vase", [(0.0, 0.0), (0.08, 0.0), (0.1, 0.12), (0.05, 0.3), (0.06, 0.34), (0.0, 0.34)], (-2.6, 0.16, 1.4), pm("#3a5a6a", 0.2), 18)
    for k in range(5): tube(f"stem{k}", [(-2.6, 0.45, 1.4), (-2.6 + 0.1 * math.cos(k), 0.75 + 0.06 * k, 1.4 + 0.1 * math.sin(k))], 0.006, pm("#3a5a2a", 0.6), res=2, bres=0)
    K.box((0, 0.3, 3.3), (1.4, 0.6, 0.6), dark, 0.0, 0.02)
    for j in range(2): K.box((0, 0.18 + j * 0.25, 2.99), (1.3, 0.2, 0.02), cedar, 0.0, 0.0)
    rad = wood("#7a4a24", "#3a2010", 8.0, 0.35)
    K.box((0, 0.85, 3.25), (0.62, 0.5, 0.36), rad, 0.0, 0.03); K.cyl((-0.12, 0.88, 3.06), 0.14, 0.02, pm("#d8c89a", 0.7), 20, "z")
    for k in range(6): K.box((-0.12, 0.88 - 0.1 + k * 0.04, 3.05), (0.26, 0.01, 0.01), rad, 0.0, 0.0)
    K.box((0.18, 0.92, 3.06), (0.16, 0.08, 0.02), em("#ffb860", 2.0), 0.0, 0.0)
    for k in range(2): K.cyl((0.1 + k * 0.12, 0.72, 3.06), 0.03, 0.03, pm("#2a2a2a", 0.3), 12, "z")
    K.box((0, 0.17, 0.8), (1.2, 0.06, 0.7), dark, 0.0, 0.01)
    for sx in (-0.5, 0.5):
        for sz in (0.5, 1.1): K.box((sx, 0.08, sz), (0.06, 0.16, 0.06), dark, 0.0, 0.0)
    for k in range(3): cup(f"hmcup{k}", (-0.3 + k * 0.3, 0.2, 0.8), "#c8c0a8", True)
    for k, (x, z, col) in enumerate(((-1.2, 1.6, "#6a2a3a"), (-0.4, 1.8, "#2a4a6a"), (0.4, 1.8, "#6a5a2a"), (1.2, 1.6, "#3a5a3a"))): K.box((x, 0.05, z), (0.6, 0.1, 0.6), pm(col, 0.9), 0.0, 0.04)
    # a family photograph on the wall, an alarm clock, folded futon, a kitchen doorway with a noren curtain on the right
    ikit.panel("hmphoto", (2.98, 1.6, 2.5), 0.35, 0.25, ikit.img_mat("hmph", ikit.portrait_img(3, 128, 96), 0.6), math.pi / 2)
    K.box((2.5, 0.25, 0.4), (0.9, 0.5, 0.7), pm("#e8e0cc", 0.9), 0.0, 0.05)
    K.box((-2.98, 1.0, -0.2), (0.02, 2.0, 0.9), pm("#2a3a5a", 0.9), 0.0, 0.0)
    K.build()
    CK.area((0, 1.2, 4.6), (0, 0.8, 1.5), 400, (1.0, 0.9, 0.72), 5, 2)
    CK.area((0, 2.2, -2.5), (0, 0.7, 2.0), 90, (0.85, 0.85, 1.0), 4)
    lib.light("POINT", T(0.1, 1.1, 2.9), 6, (1.0, 0.65, 0.3), 0.05)
    return {}

def build(M, D): return build_hq(M, D)
