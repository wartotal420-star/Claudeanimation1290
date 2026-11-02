# Station HYPO, the codebreakers' basement at Pearl Harbor, May 1942 (chapter 7 shots 31-37).
# three.js layout: basement x -5..5, z -3..6, ceiling y 2.8 with pipes and bare bulbs; floor y 0.
#   Rochefort's desk centred (0, 0, 2.0) (top y 0.76, facing -z): he sits/stands behind it at (0, 0, 2.6).
#   Chalkboard on the back wall centred (-2.2, 1.6, 5.9) with "AF = ?" (and "AF = MIDWAY ?" from f 4120);
#   Pacific wall map centred (2.3, 1.6, 5.92), 2.4 x 1.18 (Midway at about (2.25, 1.75)); a red ring marks Midway from f 4140.
#   IBM tabulators along the left wall (x -4.3), teleprinters on a bench at the right (x 4.2, z 1..3) whose tape reads
#   "WATER MACHINE BROKEN" (f 4270+) then "AF IS SHORT OF WATER" (f 4380+). Other desks at (-2.4, 0, 0.8), (2.4, 0, 0.6).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, flat_text, sign, poster, paper, brass, books
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj, map_mat, cup
from sets import c07_kit as CK
from sets import ikit

def desk(K, x, z, top, metal, rnd, papers=14):
    K.box((x, 0.74, z), (1.6, 0.05, 0.8), top, 0.0, 0.01)
    for sx in (-0.7, 0.7): K.box((x + sx, 0.37, z), (0.08, 0.74, 0.7), metal, 0.0, 0.01)
    K.box((x + 0.45, 0.45, z), (0.6, 0.55, 0.7), metal, 0.0, 0.01)
    for j in range(3): K.box((x + 0.45, 0.25 + j * 0.18, z - 0.36), (0.5, 0.14, 0.02), pm("#5a6250", 0.45, 0.3), 0.0, 0.0)
    for k in range(papers):
        K.box((x + rnd.uniform(-0.65, 0.65), 0.767 + k * 0.0025, z + rnd.uniform(-0.3, 0.3)), (0.21, 0.002, 0.29), paper(rnd.choice(["#efe4c8", "#f4efe0", "#e8dcc0"]), 0.3), rnd.uniform(-0.8, 0.8), 0.0)

def build(M, D):
    rnd = random.Random(1942)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.03, 0.03, 0.035, 1); bg.inputs[1].default_value = 0.2
    K = Kit("hypo")
    conc = mat_once("hconc", lambda: worn("hconc", "#8a8a80", "#5a5a52", 0.9, 0.0, 1.0, 0.6, "#6a6a5e"))
    green = mat_once("hgreen", lambda: worn("hgreen", "#6a7a62", "#4a5246", 0.85, 0.0, 1.5, 0.6, "#56604e"))
    floor = mat_once("hfloor", lambda: lib.tiles("hfloor", "#5a5a52", "#3e3e38", "#2a2a26", 2.0))
    K.box((0, -0.05, 1.5), (10.2, 0.1, 9.2), floor, 0.0, 0.0)
    K.box((0, 1.4, 6.05), (10.2, 2.8, 0.1), conc, 0.0, 0.0); K.box((-5.05, 1.4, 1.5), (0.1, 2.8, 9.2), conc, 0.0, 0.0); K.box((5.05, 1.4, 1.5), (0.1, 2.8, 9.2), conc, 0.0, 0.0)
    K.box((0, 0.6, 5.98), (10.0, 1.2, 0.05), green, 0.0, 0.0); K.box((-4.98, 0.6, 1.5), (0.05, 1.2, 9.0), green, 0.0, 0.0); K.box((4.98, 0.6, 1.5), (0.05, 1.2, 9.0), green, 0.0, 0.0)
    K.box((0, 2.85, 1.5), (10.2, 0.1, 9.2), conc, 0.0, 0.0)
    for k in range(4): K.box((-3.6 + k * 2.4, 2.65, 1.5), (0.3, 0.35, 9.0), conc, 0.0, 0.0)
    pipe = pm("#6a5a4a", 0.5, 0.6); pipe2 = pm("#8a3a2a", 0.5, 0.5)
    for k, (y, z, r, m) in enumerate(((2.5, 5.6, 0.09, pipe), (2.55, 5.3, 0.06, pipe2), (2.45, 0.0, 0.07, pipe), (2.6, 2.5, 0.05, pipe2))):
        K.cyl((0, y, z), r, 10.0, m, 12, "x")
        for j in range(5): K.cyl((-4 + j * 2, y, z), r * 1.3, 0.08, m, 12, "x")
    K.cyl((4.6, 1.4, 5.6), 0.08, 2.8, pipe, 12); K.cyl((4.6, 1.2, 5.6), 0.14, 0.12, pm("#b8202a", 0.5, 0.3), 12, "z")
    # desks with paper storms, Rochefort's desk with coffee, ashtray, typewriter, the cardboard box files
    top = wood("#6a4a2a", "#3a2414", 6.0, 0.5); metal = pm("#4e5648", 0.45, 0.3)
    desk(K, 0, 2.0, top, metal, rnd, 24); desk(K, -2.4, 0.8, top, metal, rnd); desk(K, 2.4, 0.6, top, metal, rnd)
    for (x, z) in ((0.55, 2.2), (-0.6, 1.8), (-2.9, 0.9), (2.0, 0.4), (2.9, 0.8)): cup(f"cc{x}{z}", (x, 0.765, z), rnd.choice(["#f2ece0", "#e8dcc8", "#d8e0e8"]))
    for k in range(5): cup(f"cs{k}", (-0.2 + k * 0.05, 0.767, 2.3 + 0.03 * k), "#e8dcc8", k == 0)
    K.cyl((-0.3, 0.775, 1.75), 0.08, 0.02, pm("#b8b8b0", 0.2, 0.7), 18)
    for k in range(6): tube(f"butt{k}", [(-0.3 + 0.04 * math.cos(k), 0.79, 1.75 + 0.04 * math.sin(k)), (-0.3 + 0.07 * math.cos(k), 0.792, 1.75 + 0.07 * math.sin(k))], 0.005, pmat("kcig", "#f2ece0", 0.8), res=2, bres=0)
    tw = pm("#1e1e20", 0.3, 0.3)
    for (x, z) in ((-2.4, 0.7), (0.0, 1.85)):
        K.box((x, 0.83, z), (0.45, 0.12, 0.35), tw, 0.0, 0.01); K.box((x, 0.93, z + 0.12), (0.45, 0.12, 0.1), tw, 0.0, 0.01)
        K.cyl((x, 0.99, z + 0.14), 0.035, 0.5, tw, 12, "x"); K.box((x, 1.05, z + 0.18), (0.2, 0.14, 0.003), paper("#f2ead6", 0.2), 0.0, 0.0, -0.1)
    for k in range(10): K.box((-4.4 + (k % 2) * 0.32, 0.18 + (k // 2) * 0.32, 4.6), (0.3, 0.3, 0.42), pm("#a8865a", 0.85), rnd.uniform(-0.1, 0.1), 0.01)
    # IBM tabulators and sorters on the left wall
    for k in range(3):
        z = 0.0 + k * 1.6
        K.box((-4.35, 0.6, z), (0.9, 1.2, 1.3), pm("#3a4048", 0.45, 0.4), 0.0, 0.03); K.box((-4.35, 1.25, z - 0.3), (0.6, 0.1, 0.5), pm("#c8c8c0", 0.3, 0.6), 0.0, 0.01)
        K.box((-3.88, 0.8, z), (0.02, 0.3, 0.9), pm("#1a1a1a", 0.3), 0.0, 0.0)
        for j in range(8): K.cyl((-3.88, 1.0, z - 0.35 + j * 0.1), 0.02, 0.02, em("#ffb040" if j % 3 else "#40ff60", 3.0), 8, "x")
        for j in range(6): K.box((-4.35, 1.32 + j * 0.01, z - 0.3), (0.2, 0.008, 0.35), pm("#e8d8b0", 0.6), 0.0, 0.0)
        ktext("IBM", (-3.87, 0.5, z), 0.12, pm("#e8e4d8", 0.6), -math.pi / 2, "sans", 0.002)
    # teleprinters on a bench (right)
    K.box((4.3, 0.7, 2.0), (0.9, 0.06, 2.4), top, 0.0, 0.01); K.box((4.3, 0.35, 2.0), (0.8, 0.7, 0.06), metal, 0.0, 0.0)
    for k, z in enumerate((1.4, 2.6)):
        K.box((4.3, 0.95, z), (0.5, 0.45, 0.6), pm("#3a3e3a", 0.4, 0.4), 0.0, 0.03); K.box((4.3, 1.2, z - 0.1), (0.4, 0.12, 0.4), pm("#3a3e3a", 0.4, 0.4), 0.0, 0.03)
        K.cyl((4.1, 1.12, z + 0.32), 0.07, 0.3, pm("#f2ead6", 0.5), 12, "x")
    K.build()
    # paper tape ribbons hanging from the teleprinters, with the two intercepts (shown at their frames)
    tape = paper("#f2ead6", 0.2)
    def tape_text(name, body, z):
        o = ktext(body, (4.2, 0.62, z), 0.07, pm("#1a1a1a", 0.6), -math.pi / 2, "mono", 0.0005); return o
    for k, z in enumerate((1.4, 2.6)): mesh_obj(f"tape{k}", [(3.95, 1.1, z - 0.06), (3.95, 1.1, z + 0.06), (3.9, 0.2, z + 0.06), (3.9, 0.2, z - 0.06)], [(0, 1, 2, 3)], tape)
    t1 = ktext("WATER MACHINE\nBROKEN", (3.89, 0.65, 1.4), 0.05, pm("#1a1a1a", 0.6), math.pi / 2, "mono", 0.0005)
    t2 = ktext("AF IS SHORT\nOF WATER", (3.89, 0.65, 2.6), 0.05, pm("#1a1a1a", 0.6), math.pi / 2, "mono", 0.0005)
    # chalkboard with the riddle, the Pacific wall map with Midway, notices, a clock
    B = Kit("board")
    B.box((-2.2, 1.6, 5.96), (3.0, 1.5, 0.04), pm("#1e2a24", 0.9), 0.0, 0.0)
    for dx, dy, sw, sh in ((0, 0.78, 3.1, 0.07), (0, -0.78, 3.1, 0.07), (1.53, 0, 0.07, 1.6), (-1.53, 0, 0.07, 1.6)): B.box((-2.2 + dx, 1.6 + dy, 5.93), (sw, sh, 0.05), top, 0.0, 0.0)
    B.box((-2.2, 0.82, 5.88), (3.0, 0.04, 0.14), top, 0.0, 0.0)
    for k in range(4): B.box((-3.2 + k * 0.2, 0.86, 5.86), (0.07, 0.025, 0.025), pm("#f2efe6", 0.9), 0.0, 0.0)
    B.build()
    chalk = pm("#ecebe2", 0.9)
    ktext("AF = ?", (-2.2, 1.95, 5.93), 0.36, chalk, 0.0, "sans", 0.001)
    q2 = ktext("AF = MIDWAY ?", (-2.2, 1.35, 5.93), 0.26, chalk, 0.0, "sans", 0.001)
    ktext("JN-25", (-3.3, 2.2, 5.93), 0.1, chalk, 0.0, "mono", 0.001)
    for k in range(4): ktext(rnd.choice(["KA-28", "RX 4F", "17 53 02", "AH AK", "KO-HO"]), (-3.3 + k * 0.6, 0.98, 5.93), 0.08, chalk, 0.0, "mono", 0.001)
    mm = mat_once("hmap", lambda: map_mat("hmap", "c07_pacific.png", 0.6))
    ikit.panel("hwmap", (2.3, 1.6, 5.94), 2.4, 1.185, mm, 0.0)
    W = Kit("wmf")
    for dx, dy, sw, sh in ((0, 0.62, 2.5, 0.05), (0, -0.62, 2.5, 0.05), (1.22, 0, 0.05, 1.29), (-1.22, 0, 0.05, 1.29)): W.box((2.3 + dx, 1.6 + dy, 5.92), (sw, sh, 0.03), top, 0.0, 0.0)
    poster(W, (0.2, 1.75, 5.97), 0.5, 0.7, 0.0, "#e8dcc0", [("SECRET", 0.12), ("NO", 0.1), ("VISITORS", 0.08)], "#7a1e1a", border="#7a1e1a")
    W.build()
    mx = 2.3 + 1.2 - (182.6 - 92) / 158 * 2.4; my = 1.6 - 0.5925 + (28.2 + 22) / 78 * 1.185
    R = Kit("ring"); R.torus((0, 0, 0), 0.09, 0.012, pm("#c8202a", 0.5), 28, 6, "z"); ring = R.build()[0]; ring.location = T(mx, my, 5.91)
    ktext("AF ?", (mx, my + 0.16, 5.91), 0.07, pm("#c8202a", 0.5), 0.0, "sans", 0.001).name = "afq"
    clock = ikit.canvas(128, 128, "#f2ead6"); ikit.ellipse(clock, 0.5, 0.5, 0.48, 0.48, "#2a2a2a", ring=0.08)
    ikit.panel("hclock", (0.2, 2.45, 5.95), 0.36, 0.36, ikit.img_mat("hclockm", clock, 0.3), 0.0)
    # bare bulbs (the motivated light), a green desk lamp on Rochefort's desk, a cool light-well at the left
    bulb = lib.emit("hbulb", (1.0, 0.8, 0.5), 25)
    for k, (x, z) in enumerate(((0.0, 1.8), (-2.6, 0.6), (2.6, 0.6), (-2.2, 4.6), (2.4, 4.6))):
        tube(f"bcord{k}", [(x, 2.8, z), (x, 2.25, z)], 0.008, pmat("kcord", "#1a1a1a", 0.6), res=2, bres=0)
        lathe(f"bulb{k}", [(0.0, 2.25), (0.04, 2.2), (0.05, 2.15), (0.0, 2.1)], (x, 0, z), bulb, 12)
        lib.light("POINT", T(x, 2.1, z), 70, (1.0, 0.72, 0.42), 0.04)
    lathe("dlamp", [(0.0, 0.0), (0.08, 0.0), (0.03, 0.02), (0.015, 0.35), (0.0, 0.35)], (0.6, 0.765, 2.25), brass(), 18)
    lathe("dlsh", [(0.06, 0.35), (0.18, 0.27), (0.19, 0.26)], (0.6, 0.765, 2.25), mat_once("rlshm", lambda: lib.principled("rlshm", hexc("#2a5a3a"), 0.3, 0.3)), 24, cap=False)
    lib.light("POINT", T(0.6, 1.0, 2.25), 20, (1.0, 0.7, 0.4), 0.05)
    CK.area((-4.5, 2.6, -1.5), (0, 1.0, 2.0), 160, (0.6, 0.72, 1.0), 1.5)
    CK.area((0, 2.0, -3.0), (0, 1.2, 2.5), 110, (1.0, 0.75, 0.5), 3)
    def update(f):
        q2.hide_render = f < 4120; ring.hide_render = f < 4140; bpy.data.objects["afq"].hide_render = f < 4140
        t1.hide_render = f < 4270; t2.hide_render = f < 4380
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
