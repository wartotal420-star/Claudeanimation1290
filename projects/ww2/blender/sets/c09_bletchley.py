# Bletchley Park, Hut 6/11, night 1943 (chapter 9: the codebreakers). A cream-and-green timber hut: the Bombe (a tall
# cabinet of spinning coloured drums, turning in update()), an Enigma on the trestle table, papers, teacups, ashtrays,
# card indexes, a blackboard of cribs, blackout curtains, a coke stove, green-shaded lamps; through the window the house.
# Layout (three, y up): hut x -3.2..3.2, z -3..8 (floor y 0, ceiling 2.7); the Bombe at (-0.6, 0, 7.5) faces -z
# (front z 7.0, 2.2 wide, 1.95 tall); the operator stands at (-0.4, 0, 6.3); the Enigma on the table at (1.35, 0.78, 2.4)
# (the table x 0.6..2.6, z 1.8..3.4, top 0.76); a second worker sits/stands at (2.3, 0, 3.9); window on x -3.2, z 2..3.4.
import bpy, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text, cup, book, candle
from sets.warroom import phone, chair, typewriter, banker_lamp
from sets import c09_kit as K

bx, cy = K.bx, K.cy
DRUMS = []
def build(M, D):
    rnd = random.Random(1943)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.01, 0.012, 0.025, 1); bg.inputs[1].default_value = 1.0
    CREAM = K.mat_once("c9hcream", lambda: lib.plaster("c9hcream", "#d8cca8")); GREEN = K.mat_once("c9hgreen", lambda: lib.plaster("c9hgreen", "#4a6a4a"))
    BOARD = wood_mat("c9hboard", "#a87a4a", "#6a4a2a", 3, 0.6); LINO = K.mat_once("c9lino", lambda: lib.tiles("c9lino", "#6a3a2a", "#5a3022", "#3a2016", 1.5))
    bx("floor", (0, -0.05, 2.5), (7, 0.1, 12), LINO, 0)
    bx("ceil", (0, 2.75, 2.5), (7, 0.1, 12), CREAM, 0)
    for k in range(6): bx(f"truss{k}", (0, 2.6, -2.5 + k * 2.1), (6.6, 0.18, 0.14), BOARD, 0.01)
    for sd in (-1, 1):
        bx(f"wallu{sd}", (sd * 3.3, 1.9, 2.5), (0.2, 1.7, 12), CREAM, 0); bx(f"walll{sd}", (sd * 3.3, 0.55, 2.5), (0.2, 1.1, 12), GREEN, 0)
        bx(f"dado{sd}", (sd * 3.18, 1.1, 2.5), (0.05, 0.08, 12), BOARD, 0.005)
        for k in range(24): bx(f"bat{sd}{k}", (sd * 3.19, 1.9, -3 + k * 0.48), (0.03, 1.7, 0.05), CREAM, 0.004)
    bx("back", (0, 1.35, 8.1), (7, 2.7, 0.2), CREAM, 0); bx("backl", (0, 0.55, 7.99), (7, 1.1, 0.02), GREEN, 0)
    bx("front", (0, 1.35, -3.2), (7, 2.7, 0.2), CREAM, 0)
    # window on the left wall: blackout curtains half open, the house at night outside
    for (z0, z1, y0, y1) in ((-3, 2.0, 0.9, 2.2), (3.4, 8, 0.9, 2.2)): pass
    bx("winpane", (-3.32, 1.55, 2.7), (0.02, 1.2, 1.4), lib.emit("c9hwin", (0.08, 0.12, 0.25), 1.0), 0)
    for k in range(3): bx(f"winm{k}", (-3.24, 1.55, 2.0 + k * 0.7), (0.05, 1.25, 0.05), BOARD, 0.005)
    bx("winh", (-3.24, 1.55, 2.7), (0.05, 0.05, 1.45), BOARD, 0.005)
    BO = K.mat_once("c9blackout", lambda: lib.cloth("c9blackout", "#14141a"))
    for sz in (-1, 1):
        for k in range(5): cy(f"bo{sz}{k}", (-3.1, 1.55, 2.7 + sz * (0.75 + k * 0.08)), 0.05, 1.5, BO, 8)
    K.blob3("house", (-12, 3, 3), (1.0, 3, 9), K.mat_once("c9house", lambda: lib.principled("c9house", lib.hexc("#2a2430"), 0.9)), 0.1, 2)
    # ---------- the Bombe ----------
    cab = K.mat_once("c9bombe", lambda: worn("c9bombe", "#2e2a26", "#5a5048", 0.45, 0.4, 20, 0.7, "#1e1a18"))
    bx("bcab", (-0.6, 0.98, 7.5), (2.3, 1.95, 0.9), cab, 0.03)
    bx("bface", (-0.6, 1.1, 7.04), (2.1, 1.55, 0.04), pmat("c9bface", "#c8b89a", 0.5, 0.2), 0.005)
    cols = ["#1a1a1a", "#b81e1e", "#2a5a2a", "#e8c040", "#1e3a7a"]
    DRUMS.clear()
    for r in range(3):
        for k in range(12):
            x_, y_ = -1.5 + k * 0.165, 1.55 - r * 0.42
            col = cols[(k // 3 + r) % len(cols)] if k % 3 == 0 else "#1a1a1a"
            o = cy(f"drum{r}{k}", (x_, y_, 6.95), 0.072, 0.07, drum_mat(col), 24, rot=(math.radians(90), 0, 0)); o.rotation_mode = "ZYX"
            DRUMS.append((o, rnd.uniform(0.6, 2.4) * (1 if k % 2 else -1)))
    for r in range(4): bx(f"brail{r}", (-0.6, 1.76 - r * 0.42, 6.98), (2.1, 0.02, 0.04), pmat("c9chrome", "#b8b8b8", 0.2, 1.0), 0.003)
    for k in range(40):   # the cable tangle down the right side
        tube(f"bcab{k}", [(0.5 + rnd.uniform(-0.05, 0.05), 1.7 - k * 0.03, 6.98), (0.62 + rnd.uniform(0, 0.1), 1.2 - k * 0.02, 6.94), (0.52, 0.3 + rnd.uniform(0, 0.2), 6.98)], 0.006, pmat(f"c9wire{k % 4}", ["#b81e1e", "#1a1a1a", "#e8c040", "#2a4a8a"][k % 4], 0.5), res=6, bres=0) if k % 3 == 0 else None
    bx("bplate", (-0.6, 0.2, 7.02), (2.0, 0.25, 0.02), pmat("c9bplate", "#3a3430", 0.5, 0.3), 0.0)
    text("BRITISH TABULATING MACHINE Co.", (-0.6, 0.2, 7.0), 0.055, pmat("c9brass", "#c8a050", 0.3, 1.0), flat=False)
    # ---------- trestle table with the Enigma ----------
    WD = wood_mat("c9htable", "#8a5a30", "#5a3418", 5, 0.5)
    bx("ttop", (1.6, 0.74, 2.6), (2.0, 0.05, 1.6), WD, 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1): bx(f"tleg{sx}{sz}", (1.6 + sx * 0.9, 0.36, 2.6 + sz * 0.7), (0.06, 0.72, 0.06), WD, 0.005)
    enigma((1.35, 0.765, 2.4), 0.0)
    for k in range(18): bx(f"pap{k}", (1.6 + rnd.uniform(-0.85, 0.85), 0.768 + k * 0.0006, 2.6 + rnd.uniform(-0.6, 0.65)), (0.21, 0.001, 0.29), pmat("kpaper", "#f0e6cc", 0.8), 0, rnd.uniform(-0.6, 0.6))
    for k in range(4):
        x_, z_ = 2.2 + (k % 2) * 0.2, 2.0 + (k // 2) * 0.6
        text(" ".join("".join(rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(5)) for _ in range(3)), (x_, 0.771, z_), 0.022, pmat("kink3", "#2a2a34", 0.6), yaw=0.1 * k, align="CENTER")
    cup("tea1", (2.4, 0.765, 3.2), "#e8e0d0"); cup("tea2", (0.8, 0.765, 3.2), "#d8e0e8")
    lathe("ash", [(0.0, 0.0), (0.07, 0.0), (0.08, 0.025), (0.065, 0.025), (0.055, 0.008), (0.0, 0.008)], (0.75, 0.765, 1.95), pmat("c9ashg", "#3a4a44", 0.1), 32)
    for k in range(3): tube(f"cig{k}", [(0.73 + k * 0.02, 0.79, 1.95), (0.65 + k * 0.03, 0.775, 1.9 + k * 0.02)], 0.005, pmat("c9cig", "#f2ece0", 0.7), res=2, bres=0)
    book("cbook", (2.35, 0.765, 1.95), (0.3, 0.05, 0.22), "#1e3a5a", 0.2)
    banker_lamp("hlamp", (2.45, 0.765, 2.9), -0.6, 20)
    # card index boxes and a filing shelf, blackboard of cribs, notices, the stove, chairs, coat pegs
    for k in range(6):
        bx(f"cidx{k}", (3.0, 0.9 + (k // 3) * 0.32, 4.6 + (k % 3) * 0.45), (0.3, 0.26, 0.4), wood_mat("c9cidx", "#6a4a2a", "#3a2814", 10, 0.6), 0.01)
        bx(f"cidxl{k}", (2.84, 0.95 + (k // 3) * 0.32, 4.6 + (k % 3) * 0.45), (0.01, 0.06, 0.12), pmat("c9label", "#f2ecd8", 0.7), 0.0)
    bx("shelf", (3.05, 0.75, 5.05), (0.35, 0.04, 1.5), WD, 0.005); bx("shelf2", (3.05, 1.07, 5.05), (0.35, 0.04, 1.5), WD, 0.005)
    bx("bboard", (3.17, 1.65, 0.6), (0.04, 1.0, 1.8), pmat("c9chalk", "#262a28", 0.9), 0.01)
    bx("bbframe", (3.15, 1.65, 0.6), (0.06, 1.08, 1.88), WD, 0.01)
    text("CRIB:  WETTERVORHERSAGE\nKEINE BESONDEREN EREIGNISSE\nQWE  ZTR  ...  ?", (3.12, 1.7, 0.6), 0.075, pmat("c9chalkw", "#e8e8e0", 0.9), yaw=-math.pi / 2, flat=False)
    for k, (z_, txt_) in enumerate(((-1.4, "HUT 6\nNO ADMITTANCE"), (4.0, "CARELESS TALK\nCOSTS LIVES"))):
        bx(f"notice{k}", (-3.17, 1.75, z_), (0.01, 0.5, 0.4), pmat(f"c9notice{k}", ["#f2ecd8", "#e8c860"][k], 0.7), 0.0)
        text(txt_, (-3.155, 1.77, z_), 0.045, pmat("kink3", "#2a2a34", 0.6), yaw=math.pi / 2, flat=False)
    lathe("stove", [(0.0, 0.0), (0.28, 0.0), (0.28, 0.85), (0.15, 0.9), (0.0, 0.9)], (-2.6, 0, 6.6), pmat("c9stove", "#2a2622", 0.6, 0.6), 20)
    tube("stp", [(-2.6, 0.9, 6.6), (-2.6, 2.7, 6.6)], 0.06, pmat("c9stove", "#2a2622", 0.6, 0.6), res=2, bres=1)
    bx("stglow", (-2.6, 0.3, 6.31), (0.16, 0.12, 0.02), lib.emit("c9ember", (1.0, 0.35, 0.08), 8), 0.01)
    K.lamp_glow("stl", (-2.6, 0.4, 6.0), 25, (1.0, 0.45, 0.15), 0.1)
    for k, (x_, z_, yw) in enumerate(((1.0, 1.4, 0.2), (2.2, 3.7, 3.0), (-2.4, 3.8, 1.2))): chair(f"ch{k}", (x_, 0, z_), yw, WD, K.mat_once("c9hseat", lambda: lib.cloth("c9hseat", "#3a4a3a")))
    for k in range(4):
        z_ = -2.2 + k * 0.45; cy(f"peg{k}", (-3.15, 1.75, z_), 0.015, 0.12, pmat("c9brass", "#c8a050", 0.3, 1.0), 8, rot=(0, math.radians(90), 0))
        tube(f"hcoat{k}", [(-3.1, 1.72, z_), (-3.05, 1.35, z_ + 0.02), (-3.07, 0.85, z_)], 0.14, K.mat_once(f"c9hcoat{k % 3}", lambda: lib.cloth(f"c9hcoat{k % 3}", ["#5a4a3a", "#3a4a5a", "#7a3a3a"][k % 3])), taper=lambda f: 0.6 + f * 0.6)
    typewriter("tw", (-2.4, 0.765, 1.2), 1.57)
    bx("desk2", (-2.45, 0.74, 1.4), (1.0, 0.05, 1.8), WD, 0.01)
    for sz in (-1, 1): bx(f"d2leg{sz}", (-2.45, 0.36, 1.4 + sz * 0.8), (0.9, 0.72, 0.05), WD, 0.005)
    for k in range(8): bx(f"teleprint{k}", (-2.4 + rnd.uniform(-0.3, 0.3), 0.768, 2.0 + rnd.uniform(-0.2, 0.2)), (0.2, 0.001, 0.25), pmat("c9tape", "#f2ead0", 0.8), 0, rnd.uniform(-0.8, 0.8))
    # light: two green-shaded pendants (warm), the desk lamp, the stove; cold moon through the window
    for k, (x_, z_) in enumerate(((1.5, 2.6), (-0.6, 5.9))):
        cy(f"pcord{k}", (x_, 2.5, z_), 0.006, 0.5, M["dark"], 6)
        lathe(f"pshade{k}", [(0.04, 0.12), (0.26, 0.0), (0.27, -0.01), (0.05, 0.11)], (x_, 2.12, z_), K.mat_once("klshade", lambda: worn("klshade", "#2a5a3a", "#1a2a1e", 0.35, 0.6, 20, 0.75)), 32, cap=False)
        lathe(f"pbulb{k}", [(0.0, 0.1), (0.035, 0.07), (0.03, 0.03), (0.0, 0.02)], (x_, 2.12, z_), M["bulb"], 16)
        sp = lib.light("SPOT", T(x_, 2.18, z_), 500, (1.0, 0.78, 0.5), 0.12); lib.look_at(sp, T(x_, 0.7, z_)); sp.data.spot_size = math.radians(110); sp.data.spot_blend = 0.6
    K.area((-3.8, 1.6, 2.7), (0, 1.2, 4), 90, (0.5, 0.62, 1.0), 1.2, 1.0)
    K.area((0, 2.4, -2.5), (0, 1.2, 4), 160, (1.0, 0.82, 0.62), 4)
    def update(f):
        for o, sp_ in DRUMS: o.rotation_euler[2] = f * sp_ * 0.12
    update(0)
    return {"update": update}

def drum_mat(col):
    """drum face: base colour with four white index marks round the rim (object-space angle), so the spin reads"""
    def mk():
        m = lib.principled("c9drum" + col, lib.hexc(col), 0.3, 0.2); t, n, l = lib.nodes(m)
        tc = n.new("ShaderNodeTexCoord"); gr = n.new("ShaderNodeTexGradient"); gr.gradient_type = "RADIAL"; l.new(tc.outputs["Object"], gr.inputs["Vector"])
        mu = n.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = 4.0; l.new(gr.outputs["Fac"], mu.inputs[0])
        fr = n.new("ShaderNodeMath"); fr.operation = "FRACT"; l.new(mu.outputs[0], fr.inputs[0])
        sep = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sep.inputs[0])
        ln = n.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; l.new(tc.outputs["Object"], ln.inputs[0])
        r1 = lib.ramp(n, l, fr.outputs[0], [(0.0, (1, 1, 1)), (0.08, (1, 1, 1)), (0.1, (0, 0, 0)), (1.0, (0, 0, 0))])
        r2 = n.new("ShaderNodeMath"); r2.operation = "GREATER_THAN"; r2.inputs[1].default_value = 0.045; l.new(ln.outputs["Value"], r2.inputs[0])
        mk_ = n.new("ShaderNodeMath"); mk_.operation = "MULTIPLY"; l.new(r1.outputs["Color"], mk_.inputs[0]); l.new(r2.outputs[0], mk_.inputs[1])
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; l.new(mk_.outputs[0], mx.inputs[0]); mx.inputs[6].default_value = (*lib.hexc(col), 1); mx.inputs[7].default_value = (0.95, 0.92, 0.85, 1)
        l.new(mx.outputs[2], n["Principled BSDF"].inputs["Base Color"])
        return m
    return K.mat_once("c9drum" + col, mk)
def enigma(c, yaw):
    """Enigma I: open oak box, lid up, 3 rows of round keys, glowing lampboard, three rotors with letter windows, plugboard"""
    x, y, z = c; WD = wood_mat("c9enbox", "#6a3a1a", "#3a1e0a", 8, 0.35)
    blk = pmat("c9enblack", "#1a1a1c", 0.35, 0.3); key = pmat("c9key", "#f2ecd8", 0.4)
    bx("enbox", (x, y + 0.075, z), (0.34, 0.15, 0.28), WD, 0.006)
    bx("enpanel", (x, y + 0.152, z), (0.31, 0.006, 0.25), blk, 0.002)
    bx("enlid", (x, y + 0.24, z + 0.17), (0.34, 0.2, 0.012), WD, 0.004).rotation_euler[0] = 0.25
    rows = ["QWERTZUIO", "ASDFGHJK", "PYXCVBNML"]
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            kx = x - 0.12 + k * 0.03 + r * 0.008; kz = z - 0.085 + r * 0.028
            cy(f"key{r}{k}", (kx, y + 0.165, kz), 0.011, 0.012, key, 12)
            lit = (r == 1 and k == 3)
            cy(f"lamp{r}{k}", (kx, y + 0.158, kz + 0.09), 0.009, 0.006, lib.emit("c9enlit", (1.0, 0.82, 0.3), 12) if lit else pmat("c9enlamp", "#d8d0b8", 0.3), 12)
    for k in range(3):
        bx(f"rot{k}", (x - 0.05 + k * 0.045, y + 0.17, z + 0.1), (0.03, 0.03, 0.05), pmat("c9rot", "#8a8a80", 0.3, 0.8), 0.004)
        bx(f"rwin{k}", (x - 0.05 + k * 0.045, y + 0.186, z + 0.085), (0.012, 0.002, 0.012), pmat("c9rwin", "#f2ecd8", 0.3), 0.0)
    for k in range(13):
        cy(f"plug{k}", (x - 0.12 + k * 0.02, y + 0.06, z - 0.142), 0.004, 0.006, blk, 8, rot=(math.radians(90), 0, 0))
    for k in range(5): tube(f"cable{k}", [(x - 0.1 + k * 0.04, y + 0.06, z - 0.145), (x - 0.06 + k * 0.03, y + 0.01, z - 0.2), (x - 0.02 + k * 0.025, y + 0.06, z - 0.145)], 0.003, pmat("c9cablee", "#2a1a14", 0.5), res=6, bres=0)
    lib.light("POINT", T(x - 0.03, y + 0.2, z + 0.03), 1.5, (1.0, 0.8, 0.35), 0.01).visible_camera = False
