# The 1923 bakery (shots 14-15), built in three.js layout coordinates (see story.ts / cast.ts):
# counter x -3..3, z 1.6..2.3; shelves on the back wall z ~3.8; baker at (0.9, 0, 3.0); price tag (-1.25, 1.62, 1.7);
# wheelbarrow of cash at (-1.2, 0, -0.4); the shop window in the left wall (x = +6 in three = camera left).
# Customers stand at (-2.3, -0.9), (-4, -1), (-3.4, 0.8), (-0.6, 1). The shot-14 close-up looks at (-0.6, 1.62, 1.7),
# so the price block on the tag sits on the tag's +x half (x -1.09..-0.55). Back wall: doorway to the bakehouse at
# x -5.3..-4.3 (oven glow). Light: low sun + sky through the (shadowless) window glass with soft shafts, two pendant
# lamps, wall sconces, oven glow, warm fill and a rim from above the shelves.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, TS
from sets import ikit as K
from sets.ikit import bx, cy, bl, sph, cone, torus, txt

TAG = None
def tag_text(f): return "200.000.000.000" if f < 1858 else "350.000.000.000" if f < 1890 else "500.000.000.000"

def build(M, D):
    global TAG
    random.seed(1923); rs = random.Random(1923)
    RH = 3.9
    WALLP = K.wall_mat("bwallp", K.wallpaper_img(), 0.42)
    DW = K.grain("bdark", "#6a3418", "#2a1006", "X", 1.0, 0.35, 0.35); DWV = K.grain("bdarkv", "#6a3418", "#2a1006", "Z", 1.0, 0.35, 0.35)
    CW = K.grain("bcounter", "#9a4e24", "#4a1e0a", "X", 0.9, 0.3, 0.5); CWL = K.grain("bcpanel", "#b8682e", "#6a3012", "Z", 0.9, 0.3, 0.5)
    SHW = K.grain("bshelf", "#8a5228", "#4a2410", "X", 1.0, 0.45, 0.2); PINE = K.grain("bpine", "#c09058", "#7a5428", "X", 1.0, 0.6)
    BR = M["brass"]; DARK = M["dark"]; WHITE = K.flat("bwhite", "#f4eedc", 0.5); GLASS = M["glass"]
    note = K.new_img("bnote_im", K.banknote_img(3)); NOTE = K.img_mat("bnote", note, 0.7); STACK = K.stack_mat("bstack", note); BAND = M["band"]
    # ---------------- shell ----------------
    bx("floor", (0, -0.05, 0.3), (13, 0.1, 13.6), M["floor"], 0)
    bx("ceiling", (0, RH + 0.05, 0.3), (13, 0.1, 13.6), lib.plaster("bceil", "#efe2c4"), 0)
    for k in range(6): bx(f"beam{k}", (-5 + k * 2, RH - 0.12, 0.3), (0.24, 0.26, 13.4), K.grain("bbeam", "#5a3418", "#2a160a", "Z", 0.6, 0.6), 0.02)
    # back wall (z 4.2) with the bakehouse doorway at x -5.3..-4.3
    bx("backA", (-5.8, RH / 2, 4.2), (1.0, RH, 0.2), WALLP, 0); bx("backB", (1.0, RH / 2, 4.2), (10.6, RH, 0.2), WALLP, 0)
    bx("backC", (-4.8, (2.3 + RH) / 2, 4.2), (1.0, RH - 2.3, 0.2), WALLP, 0)
    for x0, x1 in ((-6.3, -5.3), (-4.3, 6.3)):
        bx(f"wains{x0}", ((x0 + x1) / 2, 0.55, 4.06), (x1 - x0, 1.1, 0.08), DW, 0.01)
        bx(f"rail{x0}", ((x0 + x1) / 2, 1.12, 4.0), (x1 - x0, 0.06, 0.1), DW, 0.01)
        n = int((x1 - x0) / 0.75)
        for k in range(n): bx(f"pan{x0}{k}", (x0 + 0.375 + k * 0.75, 0.55, 4.0), (0.56, 0.78, 0.03), DWV, 0.008)
    bx("crown", (0, RH - 0.1, 4.05), (13, 0.18, 0.16), DW, 0.02)
    for sx in (-1, 1): bx(f"djamb{sx}", (-4.8 + sx * 0.54, 1.15, 4.08), (0.08, 2.3, 0.16), DW, 0.01)
    bx("dhead", (-4.8, 2.34, 4.08), (1.16, 0.1, 0.16), DW, 0.01)
    K.drape("dcurt", (-4.55, 2.28, 4.0), 0.55, 2.25, lib.cloth("dcurtm", "#7a2a1e"), 0, 4, 0.04, gather=1.0)
    # the bakehouse behind: brick oven with a glowing mouth, peel, sacks
    BRICK = lib.brickmat("bbrick", "#8a3a22", "#6a2a18", "#3a2a22", 5.0)
    bx("bhback", (-4.8, RH / 2, 7.0), (3.2, RH, 0.2), BRICK, 0); bx("bhside", (-3.3, RH / 2, 5.6), (0.2, RH, 3.0), BRICK, 0)
    bx("oven", (-4.9, 0.9, 6.4), (2.0, 1.8, 1.0), BRICK, 0.02)
    bx("ovmouth", (-4.9, 0.95, 5.89), (0.7, 0.42, 0.02), lib.emit("ovglow", (1.0, 0.38, 0.08), 12), 0)
    bx("ovlintel", (-4.9, 1.21, 5.87), (0.86, 0.08, 0.04), M["iron"], 0.01); bx("ovsill", (-4.9, 0.71, 5.85), (0.9, 0.06, 0.1), M["iron"], 0.01)
    K.point((-4.8, 1.0, 5.4), 140, (1.0, 0.45, 0.15), 0.25)
    cy("peel", (-4.0, 1.1, 5.6), 0.015, 2.2, PINE, 6, (0.3, 0, 0))
    # side walls: right (x -6.2) plain with a door, left (x +6.2) the big shop window
    bx("sideR", (-6.2, RH / 2, -1), (0.2, RH, 11), WALLP, 0)
    for sx in (-1, 1): bx(f"sidew{sx}", (sx * 6.06, 0.5, -1), (0.08, 1.0, 11), DW, 0.01)
    for z0, z1 in ((-6.5, -3.05), (0.95, 4.3)): bx(f"sideL{z0}", (6.2, RH / 2, (z0 + z1) / 2), (0.2, RH, z1 - z0), WALLP, 0)
    bx("sideLlow", (6.2, 0.5, -1.05), (0.2, 1.0, 4.0), WALLP, 0); bx("sideLhi", (6.2, 3.5, -1.05), (0.2, 0.8, 4.0), WALLP, 0)
    bx("front", (0, RH / 2, -6.3), (13, RH, 0.2), WALLP, 0)
    for k in range(5): bx(f"mull{k}", (6.1, 2.05, -3.0 + k * 1.0), (0.1, 2.2, 0.07), DW, 0.005)
    for y in (1.0, 2.05, 3.1): bx(f"tran{y}", (6.1, y, -1.0), (0.1, 0.07, 4.0), DW, 0.005)
    g = bx("winglass", (6.15, 2.05, -1.0), (0.02, 2.1, 4.0), GLASS, 0); K.shadowless_glass(g)
    outside = K.panel("street", (8.5, 2.0, -1.0), 9, 4.5, K.img_mat("bstreet", K.landscape_img(23, 512, 256, house=True), 0.9, emit=1.2), math.radians(90)); K.hide_from_light(outside)
    bx("winshelf", (5.85, 0.98, -1.0), (0.45, 0.04, 4.0), SHW, 0.01)
    for k in range(9): bl(f"wloaf{k}", (5.85, 1.07, -2.8 + k * 0.45), (0.1, 0.07, 0.17), M["bread"] if k % 2 else M["bread2"], 0.02)
    bx("door", (-6.06, 1.1, -2.0), (0.06, 2.2, 1.1), DW, 0.01); cy("knob", (-6.0, 1.05, -1.6), 0.04, 0.06, BR, 12, (0, math.radians(90), 0))
    SUN_D = (-1.0, -0.42, 0.12)
    K.sun(SUN_D, 18.0, (1.0, 0.8, 0.55), 1.0)
    K.area((7.6, 2.3, -1.0), (4, 1.2, -1.0), 700, (0.75, 0.85, 1.0), 4.0, 2.2)
    K.beam("bshaft", [(6.1, 3.1, -3.0), (6.1, 3.1, 1.0), (6.1, 1.0, 1.0), (6.1, 1.0, -3.0)], SUN_D, 6.5, (1.0, 0.85, 0.6), 0.35)
    # ---------------- shelves of bread on the back wall ----------------
    BREADS = [M["bread"], M["bread2"], M["roll"]]
    for row in range(3):
        y = 1.2 + row * 0.66
        bx(f"shelf{row}", (0.4, y, 3.82), (7.9, 0.05, 0.44), SHW, 0.008); bx(f"shlip{row}", (0.4, y + 0.03, 3.6), (7.9, 0.06, 0.02), SHW, 0.004)
        for k in range(10): bx(f"brk{row}{k}", (-3.4 + k * 0.85, y - 0.1, 3.98), (0.04, 0.16, 0.24), BR, 0.004)
        x = -3.35
        while x < 4.2:
            kind = rs.random()
            if kind < 0.3: bl(f"loaf{row}{x:.2f}", (x + 0.17, y + 0.1, 3.82), (0.17, 0.09, 0.1), rs.choice(BREADS[:2]), 0.02); x += 0.38
            elif kind < 0.45:
                bl(f"rnd{row}{x:.2f}", (x + 0.13, y + 0.09, 3.82), (0.13, 0.08, 0.13), M["bread2"], 0.015)
                for j in range(3): bx(f"score{row}{x:.2f}{j}", (x + 0.08 + j * 0.05, y + 0.17, 3.78), (0.012, 0.01, 0.12), K.flat("score", "#e8c890", 0.8), 0.003, 0.3)
                x += 0.3
            elif kind < 0.62:
                cy(f"bask{row}{x:.2f}", (x + 0.17, y + 0.07, 3.82), 0.17, 0.13, M["wicker"], 20)
                for j in range(5): bl(f"roll{row}{x:.2f}{j}", (x + 0.08 + (j % 3) * 0.09, y + 0.17 + (j // 3) * 0.03, 3.76 + (j // 3) * 0.1), (0.055, 0.045, 0.05), M["roll"], 0.01)
                x += 0.4
            elif kind < 0.75:
                for j in range(3): cy(f"bag{row}{x:.2f}{j}", (x + 0.06 + j * 0.03, y + 0.2, 3.9 - j * 0.03), 0.025, 0.42, M["bread"], 8, (rs.uniform(-0.25, -0.1), 0, 0))
                x += 0.22
            elif kind < 0.87:
                cy(f"jar{row}{x:.2f}", (x + 0.08, y + 0.14, 3.82), 0.07, 0.26, GLASS, 16); cy(f"jarl{row}{x:.2f}", (x + 0.08, y + 0.28, 3.82), 0.072, 0.03, BR, 16)
                for j in range(5): sph(f"cook{row}{x:.2f}{j}", (x + 0.08 + rs.uniform(-0.03, 0.03), y + 0.05 + j * 0.03, 3.82 + rs.uniform(-0.03, 0.03)), 0.028, K.flat("cookie", "#c88a3a", 0.7), 8)
                x += 0.22
            else:
                for j in range(3): bl(f"zopf{row}{x:.2f}{j}", (x + 0.1 + j * 0.1, y + 0.08, 3.82), (0.07, 0.06, 0.08), M["roll"], 0.01)
                x += 0.36
        for k in range(3):
            px = -2.8 + k * 2.6 + row * 0.5
            bx(f"plab{row}{k}", (px, y - 0.02, 3.585), (0.16, 0.07, 0.005), WHITE, 0.001); txt(rs.choice(["80 MRD", "95 MRD", "120 MRD", "60 MRD"]), (px, y - 0.02, 3.58), 0.03, DARK)
    # shop sign, wall sconces, exchange-rate notice, calendar, chalk price board with crossed-out prices, clock
    bx("signboard", (0, 3.42, 4.0), (3.8, 0.52, 0.06), M["sign"], 0.01)
    for sx in (-1, 1): bx(f"signedge{sx}", (sx * 1.9, 3.42, 3.98), (0.06, 0.56, 0.08), M["gold"], 0.005)
    for sy in (-1, 1): bx(f"signedgeh{sy}", (0, 3.42 + sy * 0.26, 3.98), (3.86, 0.04, 0.08), M["gold"], 0.005)
    txt("BÄCKEREI  KLEIN", (0, 3.42, 3.96), 0.25, M["gold"])
    for sx in (-1, 1):
        x = sx * 2.45; bx(f"scpl{sx}", (x, 3.25, 4.08), (0.12, 0.2, 0.03), BR, 0.01); cy(f"scarm{sx}", (x, 3.25, 3.95), 0.012, 0.25, BR, 6, (math.radians(90), 0, 0))
        cone(f"scsh{sx}", (x, 3.3, 3.82), 0.09, 0.05, 0.1, lib.principled("scglass", (1.0, 0.9, 0.7), 0.3, 0, (1.0, 0.8, 0.5), 2.0), 16)
        K.point((x, 3.25, 3.8), 30, (1.0, 0.72, 0.42), 0.05)
    PAPER = K.flat("bposter", "#efe2bc", 0.8); RED = M["red"]
    bx("notice", (-3.15, 3.35, 4.08), (0.62, 0.62, 0.01), PAPER, 0.002)
    for i, (s, sz, m) in enumerate((("KURS", 0.06, DARK), ("1 DOLLAR =", 0.045, DARK), ("4.200.000.000.000", 0.045, RED), ("MARK", 0.06, RED), ("REICHSBANK", 0.03, DARK))):
        txt(s, (-3.15, 3.57 - i * 0.11, 4.07), sz, m)
    bx("calendar", (3.15, 3.33, 4.08), (0.42, 0.56, 0.01), WHITE, 0.002); bx("calhead", (3.15, 3.55, 4.07), (0.42, 0.12, 0.01), RED, 0.002)
    txt("NOVEMBER", (3.15, 3.55, 4.06), 0.05, WHITE); txt("1923", (3.15, 3.38, 4.06), 0.13, DARK); txt("15", (3.15, 3.18, 4.06), 0.07, RED)
    bx("chalk", (5.15, 1.9, 4.06), (1.0, 1.25, 0.04), M["chalk"], 0.01); bx("chalkfr", (5.15, 1.9, 4.08), (1.1, 1.35, 0.03), DW, 0.01)
    CH = K.flat("chalkw", "#e8e6dc", 0.9)
    txt("BROT", (5.15, 2.38, 4.03), 0.13, CH)
    for i, (p, struck) in enumerate((("20 MRD", True), ("80 MRD", True), ("140 MRD", True), ("200 MRD!", False))):
        y = 2.13 - i * 0.2; txt(p, (5.15, y, 4.03), 0.09, CH if struck else lib.principled("chalkr", lib.hexc("#e8a090"), 0.9))
        if struck: bx(f"strike{i}", (5.15, y, 4.025), (0.5, 0.015, 0.005), CH, 0, rs.uniform(-0.12, 0.12)).rotation_euler[1] = rs.uniform(-0.15, 0.15)
    cy("clock", (5.15, 3.2, 4.06), 0.27, 0.06, WHITE, 32, (math.radians(90), 0, 0)); torus("clockrim", (5.15, 3.2, 4.02), 0.28, 0.025, BR, (math.radians(90), 0, 0))
    for a, ln in ((math.radians(20), 0.15), (math.radians(-110), 0.21)):
        bx(f"hand{ln}", (5.15 - ln / 2 * math.sin(a), 3.2 + ln / 2 * math.cos(a), 4.02), (0.012, ln, 0.006), DARK, 0).rotation_euler[1] = a
    # banknotes pinned to the wall like wallpaper (worthless)
    for k in range(7):
        K.panel(f"wnote{k}", (-3.9 + (k % 2) * 0.22 + rs.uniform(-0.05, 0.05), 1.4 + k * 0.17, 4.085), 0.24, 0.12, NOTE, 0).rotation_euler[1] = rs.uniform(-0.3, 0.3)
    # ---------------- the counter: varnished panels, brass foot rail, marble top ----------------
    bx("counter", (0, 0.5, 1.95), (6.0, 1.0, 0.7), CW, 0.015)
    for k in range(7):
        x = -2.55 + k * 0.85
        bx(f"cpan{k}", (x, 0.52, 1.585), (0.62, 0.62, 0.03), CWL, 0.012)
        for sy in (-1, 1): bx(f"cmh{k}{sy}", (x, 0.52 + sy * 0.33, 1.575), (0.7, 0.04, 0.03), DW, 0.008)
        for sx in (-1, 1): bx(f"cmv{k}{sx}", (x + sx * 0.33, 0.52, 1.575), (0.04, 0.7, 0.03), DW, 0.008)
    bx("plinth", (0, 0.07, 1.6), (6.1, 0.14, 0.1), DW, 0.01); bx("cornice", (0, 0.95, 1.58), (6.1, 0.06, 0.06), DW, 0.01)
    cy("footrail", (0, 0.14, 1.4), 0.025, 5.6, BR, 12, (0, math.radians(90), 0))
    for k in range(5): bx(f"frb{k}", (-2.6 + k * 1.3, 0.14, 1.5), (0.03, 0.03, 0.2), BR, 0.005)
    bx("ctop", (0, 1.03, 1.95), (6.2, 0.06, 0.85), M["marble"], 0.01)
    # display case of cakes
    case = bx("case", (1.2, 1.32, 2.0), (1.8, 0.52, 0.55), GLASS, 0.005); K.shadowless_glass(case)
    for x in (0.3, 2.1): bx(f"cframe{x}", (x, 1.32, 2.0), (0.04, 0.54, 0.57), BR, 0.004)
    bx("cframet", (1.2, 1.585, 2.0), (1.84, 0.03, 0.57), BR, 0.004)
    CREAM = K.flat("cream", "#f6ead2", 0.5); CHOC = K.flat("choc", "#4a2614", 0.4); CHER = K.flat("cherry", "#b8101c", 0.2)
    for k in range(4):
        x = 0.5 + k * 0.42; cy(f"plate{k}", (x, 1.07, 2.0), 0.16, 0.012, WHITE, 24)
        cy(f"cake{k}", (x, 1.15, 2.0), 0.13, 0.14, CHOC if k % 2 else M["roll"], 24); cy(f"icing{k}", (x, 1.23, 2.0), 0.135, 0.025, CREAM if k % 2 == 0 else CHOC, 24)
        for j in range(6): sph(f"cher{k}{j}", (x + 0.09 * math.cos(j), 1.26, 2.0 + 0.09 * math.sin(j)), 0.017, CHER, 8)
    # brass cash register with its drawer stuffed with money
    bx("reg", (2.3, 1.28, 1.95), (0.55, 0.45, 0.45), BR, 0.03); bx("regtop", (2.3, 1.6, 2.05), (0.5, 0.2, 0.22), BR, 0.03)
    bx("regwin", (2.3, 1.62, 1.93), (0.3, 0.08, 0.01), WHITE, 0.003); txt("0000", (2.3, 1.62, 1.92), 0.05, DARK)
    for i in range(4):
        for j in range(5): cy(f"key{i}{j}", (2.12 + j * 0.09, 1.5 - i * 0.04, 1.75 + i * 0.03), 0.025, 0.03, WHITE, 12, (math.radians(70), 0, 0))
    bx("drawer", (2.3, 1.12, 1.6), (0.5, 0.1, 0.35), BR, 0.01)
    for k in range(6): K.note_stack(f"dnote{k}", (2.15 + (k % 3) * 0.15, 1.19 + (k // 3) * 0.03, 1.55 + (k // 3) * 0.05), (0.14, 0.03, 0.07), rs.uniform(-0.3, 0.3), STACK, None, BAND)
    # scale weighing money, paper bags, bread, baskets, a pretzel stand
    cy("scaleb", (-2.6, 1.1, 1.95), 0.15, 0.08, M["iron"]); cy("scalep", (-2.6, 1.22, 1.95), 0.02, 0.18, M["iron"]); cy("scalepan", (-2.6, 1.32, 1.95), 0.2, 0.02, BR, 24)
    for k in range(5): K.note_stack(f"snote{k}", (-2.6 + rs.uniform(-0.05, 0.05), 1.36 + k * 0.035, 1.95 + rs.uniform(-0.04, 0.04)), (0.16, 0.035, 0.08), rs.uniform(0, 3), STACK, None, BAND)
    for k in range(4): bx(f"pbag{k}", (2.78 - k * 0.04, 1.22, 2.15), (0.22, 0.32, 0.14), K.flat("pbag", "#d8b888", 0.85), 0.01, 0.1 * k)
    for k in range(2):
        cy(f"cbask{k}", (-1.6 - k * 0.6, 1.12, 2.08), 0.2, 0.16, M["wicker"], 20)
        for j in range(5): bl(f"cbr{k}{j}", (-1.62 - k * 0.6 + (j % 3 - 1) * 0.1, 1.24, 2.05 + (j // 3) * 0.08), (0.07, 0.05, 0.06), M["roll"], 0.01)
    cy("pstand", (-0.15, 1.45, 2.15), 0.015, 0.8, BR, 8); cy("pstandb", (-0.15, 1.07, 2.15), 0.1, 0.02, BR, 16)
    for k, (dx, y) in enumerate(((-0.12, 1.7), (0.12, 1.7), (-0.12, 1.45), (0.12, 1.45))):
        K.pretzel(f"pretz{k}", (-0.15 + dx, y, 2.15), 1.0, M["bread2"])
    # money on the counter by the price tag
    for k in range(7): K.note_stack(f"cnote{k}", (-0.32 + (k % 2) * 0.17, 1.075 + (k // 2) * 0.035, 1.82 + rs.uniform(-0.02, 0.02)), (0.16, 0.035, 0.08), rs.uniform(-0.25, 0.25), STACK, None, BAND)
    cy("bell", (2.85, 1.1, 1.75), 0.05, 0.04, BR, 16); sph("bellk", (2.85, 1.14, 1.75), 0.015, BR)
    # ---------------- the price tag on its stand (text changes with the inflation) ----------------
    bx("tagpost", (-1.25, 1.24, 1.78), (0.04, 0.38, 0.04), BR, 0); cy("tagfoot", (-1.25, 1.07, 1.78), 0.1, 0.02, BR, 16)
    bx("tag", (-1.25, 1.62, 1.72), (1.5, 0.44, 0.03), M["paper"], 0.01)
    for sy in (-1, 1): bx(f"tagb{sy}", (-1.25, 1.62 + sy * 0.2, 1.704), (1.46, 0.015, 0.004), RED, 0)
    for sx in (-1, 1): bx(f"tagbv{sx}", (-1.25 + sx * 0.73, 1.62, 1.704), (0.015, 0.415, 0.004), RED, 0)
    bx("tagdiv", (-1.15, 1.62, 1.704), (0.01, 0.34, 0.004), RED, 0)
    txt("1 BROT", (-0.82, 1.75, 1.69), 0.065, DARK)
    TAG = txt(tag_text(0), (-0.82, 1.62, 1.69), 0.09, RED, extrude=0.003)
    txt("MARK", (-0.82, 1.5, 1.69), 0.06, DARK)
    txt("HEUTE", (-1.58, 1.72, 1.69), 0.06, DARK); txt("FRISCH!", (-1.58, 1.6, 1.69), 0.075, RED)
    bl("tagloaf", (-1.58, 1.49, 1.69), (0.12, 0.035, 0.01), M["bread"], 0.005)
    # pendant lamps (real light) with glowing shade interiors
    SHADE_IN = lib.principled("shin", (1.0, 0.9, 0.7), 0.4, 0, (1.0, 0.8, 0.5), 1.5)
    for x in (-1.5, 1.5):
        cy(f"cord{x}", (x, 3.25, 1.9), 0.008, 1.2, DARK, 8); cy(f"cap{x}", (x, 2.76, 1.9), 0.05, 0.06, BR, 12)
        o = cone(f"shade{x}", (x, 2.62, 1.9), 0.32, 0.08, 0.24, M["shade"], 24); md = o.modifiers.new("s", "SOLIDIFY"); md.thickness = 0.01
        cone(f"shadein{x}", (x, 2.615, 1.9), 0.31, 0.075, 0.23, SHADE_IN, 24).scale = (0.98, 0.98, 0.98)
        sph(f"bulb{x}", (x, 2.48, 1.9), 0.06, M["bulb"])
        K.point((x, 2.42, 1.9), 110, (1.0, 0.72, 0.42), 0.1)
    # fills: warm from the front, rim from above the shelves, cool bounce from the window side
    K.area((0, 2.8, -5.5), (0, 1.3, 2), 70, (1.0, 0.84, 0.66), 5)
    K.area((0.5, 3.6, 3.4), (0.5, 1.0, 0.5), 90, (1.0, 0.8, 0.55), 3, 0.6)
    # ---------------- floor clutter: flour sacks, crates, churn, broom, loose money, the wheelbarrow ----------------
    SACK = M["sack"]; STEN = K.flat("stencil", "#3a4a7a", 0.9)
    for k, (x, z, yaw) in enumerate(((-3.9, 3.3, 0.2), (-5.8, 3.3, -0.3), (3.9, 3.2, 0.3), (4.4, 2.8, -0.2), (4.0, 2.6, 0.5))):
        bl(f"sack{k}", (x, 0.36, z), (0.3, 0.38, 0.24), SACK, 0.05); bl(f"sackt{k}", (x, 0.76, z), (0.12, 0.08, 0.1), SACK, 0.03)
        txt("MEHL", (x, 0.38, z - 0.24), 0.11, STEN, yaw, tilt=0.15)
    CR = K.grain("bcrate", "#b88a50", "#6a4a24", "X", 1.0, 0.7)
    for k, (x, z, y) in enumerate(((4.7, 2.0, 0.2), (4.7, 2.0, 0.6), (5.2, 2.6, 0.2))):
        for j in range(3): bx(f"crs{k}{j}", (x, y - 0.12 + j * 0.13, z), (0.5, 0.09, 0.42), CR, 0.005)
        for sx in (-1, 1): bx(f"crc{k}{sx}", (x + sx * 0.23, y, z), (0.04, 0.4, 0.42), CR, 0.004)
    cy("churn", (3.5, 0.35, 2.9), 0.16, 0.7, K.metal("churn", "#a8a8a0", 0.35), 20); cy("churnl", (3.5, 0.74, 2.9), 0.09, 0.1, K.metal("churn2", "#a8a8a0", 0.35), 16)
    cy("broom", (5.75, 0.9, 3.6), 0.02, 1.8, PINE, 8, (0.15, 0, 0)); bx("broomh", (5.75, 0.08, 3.47), (0.3, 0.14, 0.08), K.flat("straw", "#c8a050", 0.9), 0.02)
    cy("bucket", (5.4, 0.18, 3.4), 0.15, 0.36, K.metal("bucket", "#8a8a84", 0.4), 16)
    for k in range(18):
        K.floor_quad(f"lnote{k}", (rs.uniform(-3.2, 1.2), rs.uniform(-1.6, 1.3)), 0.16, 0.08, NOTE, rs.uniform(0, 6.28), 0.004 + k * 0.0004)
    BASK = M["wicker"]
    cy("wbask", (-3.0, 0.22, 0.2), 0.32, 0.44, BASK, 24)
    for k in range(10): K.note_stack(f"bk{k}", (-3.0 + rs.uniform(-0.16, 0.16), 0.46 + rs.uniform(0, 0.08), 0.2 + rs.uniform(-0.16, 0.16)), (0.16, 0.035, 0.08), rs.uniform(0, 3), STACK, None, BAND)
    yaw = 0.5
    def wb(dx, dy, dz): return Vector((-1.2, 0, -0.4)) + Vector((dx * math.cos(yaw) + dz * math.sin(yaw), dy, -dx * math.sin(yaw) + dz * math.cos(yaw)))
    WBM = K.metal("wbm", "#3a5a4a", 0.45)
    bx("wbtray", wb(0, 0.55, 0), (1.0, 0.08, 0.7), WBM, 0.02, yaw)
    for sz in (-1, 1): bx(f"wbside{sz}", wb(0, 0.7, sz * 0.36), (1.0, 0.32, 0.04), WBM, 0.01, yaw)
    for sx in (-1, 1): bx(f"wbend{sx}", wb(sx * 0.5, 0.7, 0), (0.04, 0.32, 0.72), WBM, 0.01, yaw)
    cy("wbwheel", wb(0.65, 0.25, 0), 0.25, 0.08, DARK, 24, (math.radians(90), 0, -yaw + math.radians(90)))
    cy("wbhub", wb(0.65, 0.25, 0), 0.05, 0.12, M["iron"], 12, (math.radians(90), 0, -yaw + math.radians(90)))
    for sz in (-1, 1):
        bx(f"wbh{sz}", wb(-0.8, 0.62, sz * 0.28), (1.1, 0.05, 0.05), PINE, 0.01, yaw)
        bx(f"wbleg{sz}", wb(-0.35, 0.25, sz * 0.28), (0.05, 0.5, 0.05), PINE, 0.005, yaw)
    for k in range(30):
        p = wb(-0.38 + (k % 5) * 0.19, 0.64 + (k // 10) * 0.07, -0.22 + (k // 5 % 2) * 0.24 + rs.uniform(-0.03, 0.03))
        K.note_stack(f"cash{k}", p, (0.2, 0.06, 0.1), yaw + rs.uniform(-0.3, 0.3), STACK, None, BAND)
    return {"update": lambda f: setattr(TAG.data, "body", tag_text(f))}
