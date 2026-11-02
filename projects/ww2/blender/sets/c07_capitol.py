# The House chamber, 8 December 1941 (chapter 7 shot 12): Roosevelt at the rostrum asks for war on Japan.
# three.js layout: rostrum front face at z 4.0; the lectern with the radio microphones at (0, 1.0, 4.4) (lectern top
# y 2.1); Roosevelt stands on the platform at (0, 1.0, 4.75); the Speaker's dais behind at z 6.2 (top y 1.9) with two
# officials at (+-1.1, 1.9, 6.4); back wall z 7.6 with the big flag. Members stand on the floor at z -1..2.6
# (x -6..6) between curved desks at z -3.5 / -5.5 (keep z -1..2.6 clear). Newsreel cameras on tripods at (+-4.5, 0, 1).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, poster, gold, brass, paper
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK
from sets import ikit

def build(M, D):
    rnd = random.Random(1208)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.06, 0.05, 0.05, 1); bg.inputs[1].default_value = 0.2
    K = Kit("cap")
    mahog = wood("#5a2a18", "#2a120a", 5.0, 0.35); marble = mat_once("cmarble", lambda: lib.marble("cmarble")); cream = pm("#e8dcc0", 0.7)
    blue = mat_once("ccarpet", lambda: lib.carpet("ccarpet", "#2a3a6a", "#c8a24a")); goldm = gold()
    # floor, carpet, walls with pilasters and a coffered ceiling with a glowing skylight
    K.box((0, -0.05, 0), (24, 0.1, 24), mat_once("cfloor", lambda: lib.parquet("cfloor", "#7a4a2a", "#5a3218")), 0.0, 0.0)
    K.box((0, 0.005, 0), (14, 0.01, 14), blue, 0.0, 0.0)
    wallm = mat_once("cwall", lambda: lib.plaster("cwall", "#d8ccb0"))
    K.box((0, 5, 7.7), (24, 10, 0.2), wallm, 0.0, 0.0); K.box((-11, 5, 0), (0.2, 10, 24), wallm, 0.0, 0.0); K.box((11, 5, 0), (0.2, 10, 24), wallm, 0.0, 0.0)
    for k in range(9):
        x = -8 + k * 2
        K.box((x, 4.5, 7.5), (0.7, 9, 0.3), marble, 0.0, 0.02); K.box((x, 0.3, 7.45), (0.9, 0.6, 0.4), marble, 0.0, 0.02); K.box((x, 8.8, 7.45), (0.95, 0.4, 0.4), goldm, 0.0, 0.02)
    K.box((0, 1.4, 7.5), (24, 2.8, 0.15), mahog, 0.0, 0.01)
    for sx in (-1, 1):
        for k in range(6): K.box((sx * 10.8, 4.5, -8 + k * 3), (0.3, 9, 0.7), marble, 0.0, 0.02)
    K.box((0, 10.05, 0), (24, 0.1, 24), cream, 0.0, 0.0)
    for i in range(5):
        for j in range(5):
            K.box((-8 + i * 4, 9.9, -8 + j * 4), (3.4, 0.2, 3.4), pm("#c8b890", 0.6), 0.0, 0.02)
            K.box((-8 + i * 4, 9.82, -8 + j * 4), (2.6, 0.05, 2.6), em("#fff0d0", 1.2) if (i + j) % 2 == 0 else pm("#a89870", 0.6), 0.0, 0.0)
    # the dais: three tiers of marble and mahogany, the Speaker's desk with its gavel, the clerk's desk, the rostrum
    K.box((0, 0.5, 5.0), (9, 1.0, 2.4), marble, 0.0, 0.02); K.box((0, 0.95, 4.0), (9.2, 0.1, 0.2), goldm, 0.0, 0.0)
    K.box((0, 1.45, 6.6), (7, 0.9, 2.0), marble, 0.0, 0.02); K.box((0, 1.95, 6.6), (7.2, 0.1, 2.1), goldm, 0.0, 0.0)
    K.box((0, 2.35, 6.0), (5.4, 0.9, 0.5), mahog, 0.0, 0.02); K.box((0, 2.82, 6.0), (5.6, 0.06, 0.65), mahog, 0.0, 0.01)
    for k in range(6): K.box((-2.25 + k * 0.9, 2.35, 5.74), (0.6, 0.6, 0.02), mahog, 0.0, 0.01)
    K.cyl((0.6, 2.9, 6.0), 0.05, 0.1, mahog, 10); K.cyl((0.6, 2.92, 6.0), 0.03, 0.22, mahog, 8, "x")
    K.box((0, 1.5, 4.25), (5.0, 1.0, 0.3), mahog, 0.0, 0.02)
    for k in range(5): K.box((-2.0 + k * 1.0, 1.5, 4.08), (0.7, 0.7, 0.02), mahog, 0.0, 0.01)
    # lectern with the network microphones
    K.box((0, 1.55, 4.4), (1.1, 1.1, 0.6), mahog, 0.0, 0.02); K.box((0, 2.12, 4.38), (1.25, 0.06, 0.75), mahog, 0.0, 0.01, -0.2)
    for k in range(3): K.box((0.05 + k * 0.03, 2.16 + k * 0.004, 4.45), (0.32, 0.003, 0.42), paper("#f2ead6", 0.2), 0.05 * k, 0.0, -0.2)
    chrome = pm("#c8ccd0", 0.15, 1.0); blk = pm("#141414", 0.4, 0.3)
    nets = [("NBC", -0.62, "#1e2a5a"), ("CBS", -0.38, "#5a1e1e"), ("MBS", 0.38, "#1e4a2a"), ("NBC", 0.62, "#1e2a5a")]
    for k, (lab, x, col) in enumerate(nets):
        K.cyl((x, 2.3, 4.18), 0.012, 0.36, chrome, 8); K.box((x, 2.5, 4.18), (0.14, 0.18, 0.08), blk, 0.0, 0.01)
        K.cyl((x, 2.5, 4.13), 0.055, 0.02, chrome, 16, "z")
        K.box((x, 2.68, 4.18), (0.2, 0.16, 0.02), pm(col, 0.5), 0.0, 0.0)
        ktext(lab, (x, 2.68, 4.165), 0.07, pm("#f2efe6", 0.5), 0.0, "sans", 0.002)
    # the big flag on the back wall, smaller flags on staffs at both sides, a clock, the gallery rail
    fm = CK.us_flag_mat()
    ikit.panel("bigflag", (0, 5.6, 7.55), 6.0, 3.16, fm, 0.0)
    for sx in (-3.1, 3.1): K.box((sx, 5.6, 7.55), (0.12, 3.4, 0.1), goldm, 0.0, 0.0)
    for k, sx in enumerate((-4.2, 4.2)):
        K.cyl((sx, 1.95 + 1.3, 6.9), 0.035, 2.6, goldm, 8); K.sphere((sx, 4.62, 6.9), 0.07, goldm, 10)
        ikit.flag(f"sflag{k}", (sx - 0.05 * (1 if sx > 0 else -1), 4.5, 6.85), 1.3, 0.8, fm, 0.0 if sx > 0 else math.pi, 0.06)
    K.cyl((7.5, 6.5, 7.55), 0.5, 0.12, goldm, 28, "z")
    clock = ikit.canvas(128, 128, "#f2ead6"); ikit.ellipse(clock, 0.5, 0.5, 0.48, 0.48, "#2a2a2a", ring=0.08)
    ikit.panel("cclock", (7.5, 6.5, 7.48), 0.85, 0.85, ikit.img_mat("cclockm", clock, 0.3), 0.0)
    K.box((0, 4.0, 3.5), (0.01, 0.01, 0.01), cream, 0.0, 0.0)
    for sx in (-1, 1):
        K.box((sx * 9.5, 4.3, 0), (3, 0.15, 22), marble, 0.0, 0.0); K.box((sx * 8.05, 4.75, 0), (0.12, 0.9, 22), goldm, 0.0, 0.0)
        for k in range(22): K.cyl((sx * 8.05, 4.75, -10.5 + k), 0.04, 0.9, goldm, 8)
    # members' curved desks and chairs in front (z -3.5 / -5.5 / -7.5)
    for r in range(3):
        R = 9 + r * 2.0
        for k in range(15):
            a = -0.7 + k * 0.1; x, z = R * math.sin(a), 4.0 - R * math.cos(a)
            if z > -2.5: continue
            K.box((x, 0.4, z), (1.0, 0.8, 0.5), mahog, -a, 0.02); K.box((x, 0.82, z), (1.1, 0.04, 0.6), mahog, -a, 0.01)
            K.box((x + 0.2 * math.sin(a), 0.92, z - 0.05), (0.28, 0.003, 0.2), paper("#f2ead6", 0.25), -a + rnd.uniform(-0.3, 0.3), 0.0)
            cz = z - 0.6 * math.cos(a); cx = x - 0.6 * math.sin(a)
            K.box((cx, 0.45, cz), (0.5, 0.08, 0.5), pm("#6a1e1e", 0.8), -a, 0.02); K.box((cx - 0.25 * math.sin(a), 0.85, cz - 0.25 * math.cos(a)), (0.5, 0.8, 0.08), pm("#6a1e1e", 0.8), -a, 0.02)
    # newsreel cameras on tripods with big film lamps
    for k, sx in enumerate((-4.6, 4.6)):
        for j in range(3):
            a = j / 3 * math.tau; tube(f"tri{k}{j}", [(sx + 0.5 * math.cos(a), 0, 1.0 + 0.5 * math.sin(a)), (sx, 1.5, 1.0)], 0.02, pmat("ctri", "#2a2a2a", 0.5, 0.5), res=2, bres=0)
        K.box((sx, 1.7, 1.0), (0.35, 0.35, 0.6), blk, 0.0, 0.02); K.cyl((sx, 1.7, 1.38), 0.08, 0.2, chrome, 12, "z")
        for d in (-0.15, 0.15): K.cyl((sx, 2.0, 1.0 + d), 0.17, 0.06, blk, 16, "x")
        lathe(f"flamp{k}", [(0.05, 0.0), (0.25, 0.15), (0.32, 0.4)], (sx * 1.3, 2.6, 0.2), pm("#3a3a3a", 0.4, 0.6), 24)
        K.cyl((sx * 1.3, 1.3, 0.2), 0.03, 2.6, blk, 8)
    K.build()
    # lights: warm skylight, two newsreel floods on the rostrum, cool fill, warm back rim on the dais
    CK.area((0, 9.6, 0), (0, 0, 2), 900, (1.0, 0.86, 0.66), 10, 10)
    for sx in (-6.0, 6.0): CK.area((sx, 3.0, 0.2), (0, 2.2, 4.6), 700, (1.0, 0.92, 0.8), 0.8)
    CK.area((0, 4.5, -8), (0, 1.5, 2), 500, (0.62, 0.72, 1.0), 6)
    CK.area((0, 5.0, 7.3), (0, 2.2, 4.6), 300, (1.0, 0.7, 0.4), 4)
    return {}
