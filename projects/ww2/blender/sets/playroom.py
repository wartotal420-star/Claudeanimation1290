# The kids' playroom (shot 16), sets.ts buildPlayroom layout: room x -5..5, z -5..5 (back wall z 3.5), carpet
# x -1.8..1.8, z -1..2.2; the kids at (-0.55, 0.6) and (0.65, 0.75); the cash tower is exported cards (~(0.1, 0.95)).
# Low camera (y 0.6-0.8) from z -1.6 .. -0.8 looking +z: the back wall, window (x 0.88..2.12, y 0.98..2.62, a real
# opening with daylight and a sun patch on the carpet behind the kids) and the floor fill the frame.
import bpy, math, random
import numpy as np
import lib
from lib import T, TS
from sets import ikit as K
from sets.ikit import bx, cy, bl, sph, cone, torus, txt

def frieze_img(w=1024, h=96):
    a = K.canvas(h, w, "#f2e6c8"); x, y = K.grid(a)
    K.rect(a, 0, 0, 1, 0.08, "#2a5a9a"); K.rect(a, 0, 0.92, 1, 1, "#2a5a9a")
    cols = ["#c8323a", "#e8b22a", "#3a8a4a", "#2a6ac8"]
    for k in range(16):
        cx = (k + 0.5) / 16; c = cols[k % 4]
        if k % 4 == 0: K.ellipse(a, cx, 0.55, 0.018, 0.2, c); K.ellipse(a, cx + 0.012, 0.35, 0.01, 0.12, c); K.rect(a, cx + 0.018, 0.33, cx + 0.028, 0.38, "#e8902a")  # duck
        elif k % 4 == 1: K.rect(a, cx - 0.02, 0.4, cx + 0.02, 0.75, c); K.poly(a, [(cx - 0.026, 0.42), (cx, 0.18), (cx + 0.026, 0.42)], "#8a3a2a")  # house
        elif k % 4 == 2: K.rect(a, cx - 0.004, 0.55, cx + 0.004, 0.8, "#6a4a2a"); K.ellipse(a, cx, 0.42, 0.018, 0.25, c)  # tree
        else: K.rect(a, cx - 0.025, 0.42, cx + 0.025, 0.7, c); K.ellipse(a, cx - 0.015, 0.74, 0.008, 0.1, "#222222"); K.ellipse(a, cx + 0.015, 0.74, 0.008, 0.1, "#222222")  # wagon
    K.shade(a, 0.04, 2, 10)
    return a

def build(M, D):
    random.seed(1923); rs = random.Random(1923)
    FL = K.planks("plfloor", "#a8784a", "#5a3a1e", "Y", 0.15, 1.8, 0.45, 0.2)
    WP = K.wall_mat("plwallp", K.wallpaper_img("#e8d8a8", "#5a8ab8", "#c86a4a", seed=5), 0.38)
    WD = K.grain("plwood", "#8a5228", "#3e200c", "X", 1.0, 0.45, 0.3); WDV = K.grain("plwoodv", "#f0e6d0", "#d8ccb0", "Z", 1.0, 0.5)
    BR = M["brass"]; DARK = M["dark"]; WHITE = K.flat("plwhite", "#f2ece0", 0.5)
    note = K.new_img("plnote_im", K.banknote_img(7)); NOTE = K.img_mat("plnote", note, 0.7); STACK = K.stack_mat("plstack", note); BAND = M["band"]
    bx("floor", (0, -0.05, 0), (11, 0.1, 11), FL, 0)
    bx("ceil", (0, 3.45, 0), (11, 0.1, 11), lib.plaster("plceil", "#efe6d2"), 0)
    # back wall with a real window opening x 0.88..2.12, y 0.98..2.62
    bx("backL", (-2.06, 1.7, 3.65), (5.88, 3.4, 0.3), WP, 0); bx("backR", (3.56, 1.7, 3.65), (2.88, 3.4, 0.3), WP, 0)
    bx("backB", (1.5, 0.49, 3.65), (1.24, 0.98, 0.3), WP, 0); bx("backT", (1.5, 3.01, 3.65), (1.24, 0.78, 0.3), WP, 0)
    bx("left", (5.15, 1.7, 0), (0.3, 3.4, 11), WP, 0); bx("right", (-5.15, 1.7, 0), (0.3, 3.4, 11), WP, 0)
    bx("dado", (0, 0.42, 3.48), (10.4, 0.84, 0.04), WDV, 0.005); bx("dadorail", (0, 0.86, 3.46), (10.4, 0.05, 0.06), WD, 0.005)
    bx("skirt", (0, 0.08, 3.46), (10.4, 0.16, 0.06), WD, 0.005)
    FRZ = K.img_mat("frieze", frieze_img(), 0.7)
    for k in range(3): K.panel(f"frieze{k}", (-3.4 + k * 3.4 if k != 1 else -0.5, 2.95, 3.495), 3.4 if k != 1 else 2.7, 0.3, FRZ, 0)
    # window: white frame, muntins, sill with a toy boat, curtains on a rod, the street outside
    for sx in (-1, 1): bx(f"wj{sx}", (1.5 + sx * 0.66, 1.8, 3.5), (0.08, 1.72, 0.22), WHITE, 0.005)
    bx("wt", (1.5, 2.62, 3.5), (1.4, 0.08, 0.22), WHITE, 0.005); bx("wsill", (1.5, 0.96, 3.38), (1.6, 0.05, 0.3), WHITE, 0.01)
    for y in (1.53, 2.08): bx(f"wb{y}", (1.5, y, 3.52), (1.24, 0.035, 0.04), WHITE, 0.003)
    bx("wv", (1.5, 1.8, 3.52), (0.04, 1.64, 0.04), WHITE, 0.003)
    out = K.panel("street", (1.5, 1.8, 7.0), 8, 4, K.img_mat("plout", K.rooftops_img(1923), 0.9, emit=1.0), 0); K.hide_from_light(out)
    cy("rod", (1.5, 2.8, 3.38), 0.015, 2.4, BR, 8, (0, math.radians(90), 0))
    CUR = lib.cloth("curt", "#d8642a")
    for sx in (-1, 1): K.drape(f"curt{sx}", (1.5 + sx * 0.95, 2.8, 3.36), 0.6, 2.75, CUR, 0, 4, 0.05, gather=sx * 1.0)
    bx("boat", (1.2, 1.03, 3.38), (0.3, 0.08, 0.1), K.flat("boat", "#c8323a", 0.4), 0.02); cy("mast", (1.2, 1.17, 3.38), 0.006, 0.22, WD, 6)
    cone("sail", (1.16, 1.18, 3.38), 0.07, 0.0, 0.16, WHITE, 3)
    cy("cactus", (1.85, 1.06, 3.38), 0.05, 0.14, K.flat("pot", "#b85a32", 0.8), 12); bl("cact", (1.85, 1.2, 3.38), (0.035, 0.08, 0.035), K.flat("cact", "#3a7a3a", 0.6), 0.01)
    K.area((1.5, 1.8, 4.2), (1.0, 0.6, 0.5), 300, (0.75, 0.85, 1.0), 1.2, 1.6)
    SUN_D = (0.15, -0.6, -1.0)
    K.sun(SUN_D, 10.0, (1.0, 0.82, 0.58), 1.0)
    K.beam("plshaft", [(0.88, 2.62, 3.55), (2.12, 2.62, 3.55), (2.12, 0.98, 3.55), (0.88, 0.98, 3.55)], SUN_D, 4.0, (1.0, 0.86, 0.62), 0.2)
    # carpet
    K.floor_quad("carpet", (0, 0.6), 3.6, 3.2, K.img_mat("plcarpet", K.carpet_img(384, 336, "#2a4a7a", "#e8c84a", "#c8323a"), 0.95, sheen=0.4), y=0.006)
    # pictures, a clock, a blackboard with sums the kids copied from the grown-ups
    K.framed("pic", (-1.6, 2.0, 3.47), 0.8, 0.6, K.img_mat("plpic", K.landscape_img(11, house=True), 0.5), WD, 0, 0.06, 0.04)
    K.framed("pic2", (-0.4, 1.75, 3.47), 0.4, 0.5, K.img_mat("plpic2", K.portrait_img(12), 0.5), WD, 0, 0.05, 0.04)
    cy("clock", (0.0, 2.45, 3.47), 0.17, 0.05, WHITE, 32, (math.radians(90), 0, 0)); torus("clockr", (0.0, 2.45, 3.45), 0.18, 0.02, BR, (math.radians(90), 0, 0))
    for a, ln in ((0.6, 0.1), (-1.9, 0.14)): bx(f"hand{ln}", (-ln / 2 * math.sin(a), 2.45 + ln / 2 * math.cos(a), 3.44), (0.01, ln, 0.005), DARK, 0).rotation_euler[1] = a
    bx("board", (-3.0, 1.55, 3.46), (1.1, 0.8, 0.03), M["chalk"], 0.01); bx("boardf", (-3.0, 1.55, 3.48), (1.2, 0.9, 0.03), WD, 0.01)
    CH = K.flat("plchalk", "#ece8dc", 0.9)
    for i, s in enumerate(("1 $ =", "4.200.000.000.000", "MARK")): txt(s, (-3.0, 1.78 - i * 0.2, 3.44), 0.08 if i != 1 else 0.065, CH)
    # toy shelf with dolls, tin soldiers, a drum; a dollhouse; a rocking horse
    for row in range(3):
        bx(f"sh{row}", (3.4, 0.4 + row * 0.55, 3.28), (1.6, 0.04, 0.35), WD, 0.005)
        for k in range(6):
            x = 2.8 + k * 0.24; c = ["#c8323a", "#2a6ac8", "#e8c84a", "#3a9a4a", "#f2f2f2"][(row + k) % 5]
            if (row + k) % 3 == 0: bl(f"doll{row}{k}", (x, 0.52 + row * 0.55, 3.25), (0.06, 0.1, 0.05), K.flat(f"dc{c}", c, 0.5), 0.01); sph(f"dollh{row}{k}", (x, 0.66 + row * 0.55, 3.25), 0.045, K.flat("skin", "#f0c8a0", 0.5), 12)
            elif (row + k) % 3 == 1: cy(f"tin{row}{k}", (x, 0.5 + row * 0.55, 3.25), 0.07, 0.16, K.metal(f"tin{c}", c, 0.3), 16)
            else: bx(f"toyb{row}{k}", (x, 0.5 + row * 0.55, 3.25), (0.15, 0.17, 0.15), K.flat(f"tb{c}", c, 0.4), 0.02, k * 0.2)
    for sx in (-1, 1): bx(f"shs{sx}", (3.4 + sx * 0.8, 0.9, 3.28), (0.04, 1.8, 0.37), WD, 0.005)
    DH = K.flat("dh", "#f2dca8", 0.6); ROOF = K.flat("dhroof", "#a83a2a", 0.6)
    bx("dhouse", (-2.3, 0.4, 3.0), (0.8, 0.8, 0.45), DH, 0.01)
    o = bx("dhroof", (-2.3, 0.95, 3.0), (0.62, 0.62, 0.48), ROOF, 0.01); o.rotation_euler[1] = math.radians(45); o.scale = (1, 1, 0.55)
    for i in range(2):
        for j in range(3): bx(f"dhw{i}{j}", (-2.55 + j * 0.25, 0.25 + i * 0.35, 2.77), (0.12, 0.14, 0.01), K.flat("dhwin", "#4a7ab8", 0.2), 0.002)
    bx("dhdoor", (-2.3, 0.12, 2.77), (0.12, 0.22, 0.01), WD, 0.002)
    RED = K.flat("rh", "#c8323a", 0.35); MANE = K.flat("mane", "#2a1a10", 0.8); WHITEP = K.flat("rhw", "#f2ece0", 0.4)
    for dz in (-0.18, 0.18):
        o = cy(f"rock{dz}", (2.4, 0.3, 1.9 + dz), 0.55, 0.05, WD, 32, (0, math.radians(90), 0)); o.scale = (1, 1, 1)
    bl("rhbody", (2.4, 0.62, 1.9), (0.38, 0.17, 0.15), WHITEP, 0.01)
    for k in range(5): sph(f"rhspot{k}", (2.25 + k * 0.08, 0.7 + 0.04 * (k % 2), 1.76), 0.035, RED, 8)
    bl("rhneck", (2.15, 0.82, 1.9), (0.08, 0.16, 0.08), WHITEP, 0.01); bl("rhhead", (2.05, 0.95, 1.9), (0.14, 0.08, 0.07), WHITEP, 0.01)
    bl("rhmane", (2.18, 0.9, 1.9), (0.06, 0.15, 0.04), MANE, 0.02); bx("saddle", (2.45, 0.78, 1.9), (0.2, 0.04, 0.3), RED, 0.02)
    for dx in (-0.25, 0.25):
        for dz in (-0.1, 0.1): cy(f"rhleg{dx}{dz}", (2.4 + dx, 0.42, 1.9 + dz), 0.025, 0.28, WHITEP, 8)
    # side table with a lamp (warm), a teddy, a ball, a drum, blocks with letters, train on its track
    bx("stab", (-3.2, 0.68, 2.6), (0.8, 0.05, 0.6), WD, 0.01)
    for dx in (-0.35, 0.35):
        for dz in (-0.25, 0.25): bx(f"stl{dx}{dz}", (-3.2 + dx, 0.33, 2.6 + dz), (0.05, 0.66, 0.05), WD, 0)
    cy("lb", (-3.2, 0.72, 2.6), 0.08, 0.04, BR); cy("ls", (-3.2, 0.88, 2.6), 0.012, 0.32, BR)
    o = cone("lshade", (-3.2, 1.1, 2.6), 0.2, 0.1, 0.18, lib.principled("plshade", lib.hexc("#e88a3a"), 0.6, 0, (1.0, 0.6, 0.3), 1.5), 20)
    K.point((-3.2, 1.05, 2.6), 70, (1.0, 0.7, 0.4), 0.06)
    TED = lib.cloth("teddy", "#a0703a")
    bl("teddy", (1.6, 0.2, 2.5), (0.2, 0.22, 0.16), TED, 0.02); bl("teddyh", (1.6, 0.5, 2.5), (0.14, 0.13, 0.12), TED, 0.02)
    for sx in (-1, 1): sph(f"tedear{sx}", (1.6 + sx * 0.1, 0.62, 2.5), 0.045, TED, 10); bl(f"tedarm{sx}", (1.6 + sx * 0.18, 0.22, 2.45), (0.06, 0.11, 0.06), TED, 0.01)
    sph("tedeye1", (1.56, 0.53, 2.39), 0.015, DARK, 8); sph("tedeye2", (1.64, 0.53, 2.39), 0.015, DARK, 8)
    sph("ball", (-1.6, 0.14, 1.9), 0.14, K.flat("ball", "#e84a3a", 0.3)); torus("ballst", (-1.6, 0.14, 1.9), 0.141, 0.02, K.flat("ballw", "#f2ece0", 0.3), (math.radians(90), 0, 0.5))
    cy("drum", (2.2, 0.12, 0.2), 0.17, 0.22, K.flat("drum", "#c8323a", 0.4), 24); cy("drumt", (2.2, 0.235, 0.2), 0.172, 0.01, WHITE, 24)
    for k in range(2): cy(f"stick{k}", (2.0 + k * 0.08, 0.02, -0.1), 0.008, 0.3, WD, 6, (math.radians(90), 0, 0.3 + k * 0.4))
    BLK = [K.flat(f"blk{k}", c, 0.4) for k, c in enumerate(["#2a5a8a", "#c8a24a", "#3a7a3a", "#c8323a"])]
    for k, (x, z, y) in enumerate(((-1.5, -0.3, 0), (-1.33, -0.25, 0), (-1.42, -0.28, 0.17), (1.2, 0.0, 0), (1.38, 0.05, 0), (-0.5, -0.45, 0))):
        bx(f"blk{k}", (x, 0.085 + y, z), (0.17, 0.17, 0.17), BLK[k % 4], 0.015, k * 0.3)
        txt("ABCDEF"[k], (x, 0.085 + y, z - 0.087), 0.11, WHITE, k * 0.3)
    for k in range(14): bx(f"trk{k}", (-1.4 + k * 0.22, 0.01, -0.85), (0.04, 0.02, 0.18), WD, 0);
    for sx in (-1, 1): bx(f"rail{sx}", (0.0, 0.025, -0.85 + sx * 0.06), (3.0, 0.015, 0.012), K.metal("rail", "#8a8a8a", 0.3), 0)
    for k in range(3):
        bx(f"car{k}", (-0.9 + k * 0.32, 0.1, -0.85), (0.28, 0.14, 0.14), K.metal(f"car{k}", ["#1e1e22", "#c8323a", "#2a6a3a"][k], 0.3), 0.02)
        for sx in (-1, 1): cy(f"wh{k}{sx}", (-0.9 + k * 0.32 + 0.08 * sx, 0.04, -0.85), 0.035, 0.18, DARK, 12, (math.radians(90), 0, 0))
    cy("chimney", (-0.98, 0.22, -0.85), 0.03, 0.1, K.metal("car0", "#1e1e22", 0.3), 10)
    # money everywhere: bundle towers already built, an overflowing laundry basket, a toy wagon of cash, loose notes
    for (x, z, n) in ((-1.3, 1.6, 9), (1.35, 1.5, 6), (-0.15, 2.0, 4)):
        for j in range(n): K.note_stack(f"tw{x}{j}", (x + rs.uniform(-0.01, 0.01), 0.025 + j * 0.05, z), (0.3, 0.05, 0.14), (j % 2) * math.pi / 2 + rs.uniform(-0.1, 0.1), STACK, None, BAND)
    cy("lbask", (-2.2, 0.2, 1.0), 0.3, 0.4, M["wicker"], 24)
    for k in range(12): K.note_stack(f"lb{k}", (-2.2 + rs.uniform(-0.17, 0.17), 0.42 + rs.uniform(0, 0.1), 1.0 + rs.uniform(-0.17, 0.17)), (0.3, 0.05, 0.14), rs.uniform(0, 3), STACK, None, BAND)
    bx("wagon", (2.0, 0.17, -0.5), (0.6, 0.14, 0.38), K.flat("wagon", "#2a6ac8", 0.4), 0.02, 0.4)
    for sx in (-1, 1):
        for sz in (-1, 1): cy(f"wgw{sx}{sz}", (2.0 + sx * 0.22 * math.cos(0.4) + sz * 0.2 * math.sin(0.4), 0.07, -0.5 - sx * 0.22 * math.sin(0.4) + sz * 0.2 * math.cos(0.4)), 0.07, 0.03, DARK, 16, (math.radians(90), 0, -0.4 + math.radians(90)))
    for k in range(6): K.note_stack(f"wg{k}", (2.0 + rs.uniform(-0.15, 0.15), 0.27 + (k // 3) * 0.05, -0.5 + rs.uniform(-0.08, 0.08)), (0.3, 0.05, 0.14), 0.4 + rs.uniform(-0.2, 0.2), STACK, None, BAND)
    cy("wghandle", (1.6, 0.25, -0.75), 0.01, 0.4, DARK, 6, (0.6, 0.5, 0))
    k = 0
    while k < 22:
        x, z = rs.uniform(-1.7, 1.7), rs.uniform(-0.6, 2.0)
        if abs(x - 0.1) < 0.4 and 0.6 < z < 1.3: continue
        if k < 10: K.note_stack(f"cash{k}", (x, 0.03, z), (0.3, 0.05, 0.14), rs.uniform(0, 3), STACK, None, BAND)
        else: K.floor_quad(f"lnote{k}", (x, z), 0.3, 0.14, NOTE, rs.uniform(0, 6.28), 0.008 + k * 0.0003)
        k += 1
    # fills: warm low fill from the camera side, warm rim from high behind
    K.area((0, 2.2, -4.6), (0, 0.8, 1.0), 260, (1.0, 0.86, 0.72), 5)
    K.area((-1.5, 3.0, 3.0), (0.0, 0.5, 0.8), 70, (1.0, 0.8, 0.55), 1.5)
    return {}
