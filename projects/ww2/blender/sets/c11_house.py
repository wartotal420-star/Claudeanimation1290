# Two German interiors, 6 June 1944 (chapter 11):
#  A. Rommel's living room at home in Herrlingen (origin): room x -4..4, z -3..4.2 (back wall z 4.2), ceiling 3.0.
#     The birthday table at (0, 1.9) 1.7 x 0.95, top y 0.76: cake with candles at (0, 0.77, 1.9), presents, flowers,
#     the coffee set. Keep clear for characters: z -0.6..1.3, |x| < 2.4 (Rommel at about (-0.85, 0, 1.0), his wife at
#     (0.85, 0, 1.0)). Afternoon sun through the window on the right (+x is screen left from the -z side; the window is on
#     the x -4 wall = screen right), a tiled stove, a sideboard with a gramophone, garlands, photos.
#  B. The Berghof corridor at x 40: hall x 38.2..41.8, z -2..8.5, ceiling 3.4; THE BEDROOM DOOR at (40, 0, 8.4) facing -z
#     with a "BITTE NICHT STÖREN" sign; a ringing telephone on a table at (41.4, 0.8, 5.0); keep clear x 38.6..41.4,
#     z 2..7.5 (officers). Night-blue window light from the left wall, warm sconces, a long runner carpet, paintings.
import bpy, math, random
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, gold, glassm
from sets import ikit as IK
from sets.void import candle, cup, bookcase, lathe, tube
from sets.warroom import phone, wall_clock

def build(M, D):
    rnd = random.Random(1944); C.SB.reset()
    S = bpy.context.scene; bg = S.world.node_tree.nodes.get("Background")
    if bg: bg.inputs[0].default_value = (0.5, 0.6, 0.75, 1); bg.inputs[1].default_value = 0.4
    K = Kit("house")
    # ================= A. the living room =================
    wp = IK.wall_mat("hs_wp", IK.wallpaper_img("#c8b078", "#7a4a2a", "#e8d8a8", seed=3), 0.5)
    fl = C.planks("hs_floor", "#8a5a32", "#4a2a14", "X", 0.11, 1.2)
    dado = C.SB.wood("#5a3a22", "#2a1a0e", 5, 0.4); white = pm("#f0ead8", 0.5)
    K.box((0, -0.05, 0.6), (8.2, 0.1, 7.4), fl, 0, 0)
    IK.floor_quad("hs_rug", (0, 1.0), 4.2, 3.0, IK.img_mat("hs_rugm", IK.carpet_img(192, 256, "#7a2a22", "#d8b860", "#2a3a5a"), 0.9), 0, 0.006)
    K.box((0, 3.05, 0.6), (8.2, 0.1, 7.4), C.plaster("hsc", "#efe6d2"), 0, 0)
    K.box((0, 2.95, 0.6), (8.0, 0.1, 0.1), white, 0, 0.01)
    for (cx, cz, w, d) in ((0, 4.25, 8.2, 0.1), (0, -3.05, 8.2, 0.1), (4.05, 0.6, 0.1, 7.4)):
        K.box((cx, 1.5, cz), (w, 3.0, d), wp, 0, 0)
    for (cx, cz, w, d) in ((0, 4.17, 8.0, 0.06), (4.0, 0.6, 0.06, 7.2)):
        K.box((cx, 0.45, cz), (w, 0.9, d), dado, 0, 0.005); K.box((cx, 0.92, cz), (w + 0.02, 0.05, d + 0.04), dado, 0, 0.005)
        K.box((cx, 2.88, cz), (w, 0.12, d + 0.06), white, 0, 0.01)
    # the -x wall with a big window: frame, mullions, net curtains, drapes, the garden beyond
    wx = -4.05
    for (cz, w) in ((-1.9, 2.3), (3.3, 1.9)): K.box((wx, 1.5, cz), (0.1, 3.0, w), wp, 0, 0)
    K.box((wx, 0.45, 1.2), (0.1, 0.9, 2.9), wp, 0, 0); K.box((wx, 2.75, 1.2), (0.1, 0.5, 2.9), wp, 0, 0)
    for k in range(4): K.box((wx + 0.02, 1.7, -0.2 + k * 0.94), (0.08, 1.6, 0.07), white, 0, 0.005)
    for k in range(3): K.box((wx + 0.02, 0.9 + k * 0.8, 1.2), (0.08, 0.07, 2.9), white, 0, 0.005)
    K.box((wx + 0.12, 0.88, 1.2), (0.3, 0.05, 3.0), white, 0, 0.01)
    garden = IK.img_mat("hs_garden", IK.landscape_img(4, 384, 256, house=True), 0.8, emit=1.4)
    IK.panel("hs_view", (-5.2, 1.6, 1.2), 4.0, 2.6, garden, math.pi / 2)
    for s in (-1, 1):
        IK.drape(f"hs_dr{s}", (wx + 0.2, 2.75, 1.2 + s * 1.65), 0.8, 2.7, IK.velvet("hs_drape", "#6a2a2a", 0.8), math.pi / 2, 5, 0.05, gather=s * 1.0)
    C.sun((-1.0, 0.45, 0.25), 4.0, (1.0, 0.84, 0.62), 2.0)
    C.fill((-4.8, 1.8, 1.2), (0, 1.0, 1.2), 420, (0.85, 0.9, 1.0), 2.8, 1.6)
    # the birthday table: cloth, cake with candles, presents (one from Paris: shoes), flowers, coffee things
    oak = C.SB.wood("#6a3e1e", "#3a200e", 5, 0.35)
    K.box((0, 0.73, 1.9), (1.8, 0.05, 1.0), oak, 0, 0.01)
    K.box((0, 0.755, 1.9), (1.86, 0.01, 1.06), pm("#f4f0e4", 0.8), 0, 0.0)
    for s in (-1, 1): K.box((s * 0.93, 0.62, 1.9), (0.01, 0.26, 1.06), pm("#f4f0e4", 0.8), 0, 0.0)
    for sx in (-0.8, 0.8):
        for sz in (-0.4, 0.4): K.cyl((sx, 0.36, 1.9 + sz), 0.04, 0.72, oak, 10)
    K.cyl((0, 0.8, 1.9), 0.2, 0.05, pm("#e8e4dc", 0.3), 32)
    K.cyl((0, 0.9, 1.9), 0.17, 0.16, pm("#f2e2c8", 0.6), 32); K.cyl((0, 0.985, 1.9), 0.175, 0.02, pm("#f8f0f0", 0.5), 32)
    for k in range(12): K.sphere((0.16 * math.cos(k / 12 * math.tau), 0.98, 1.9 + 0.16 * math.sin(k / 12 * math.tau)), 0.02, pm("#c8202c", 0.4), 8)
    for k in range(5):
        a = k / 5 * math.tau; candle(f"hs_c{k}", (0.08 * math.cos(a), 0.99, 1.9 + 0.08 * math.sin(a)), 0.08, k, 0.6)
    for k, (x, z, s, col, rib) in enumerate(((-0.6, 1.75, 0.22, "#3a6aa8", "#e8c040"), (-0.55, 2.1, 0.16, "#c84a6a", "#f0f0f0"), (0.6, 2.05, 0.18, "#4a8a4a", "#c8202c"))):
        K.box((x, 0.76 + s / 2, z), (s * 1.3, s, s), pm(col, 0.5), 0.3 * k, 0.01)
        K.box((x, 0.76 + s / 2, z), (s * 1.32, s + 0.005, 0.03), pm(rib, 0.4), 0.3 * k, 0.0); K.box((x, 0.76 + s / 2, z), (0.03, s + 0.005, s + 0.01), pm(rib, 0.4), 0.3 * k, 0.0)
        K.sphere((x, 0.77 + s, z), 0.03, pm(rib, 0.4), 8, (1.4, 0.6, 1.0))
    K.box((0.62, 0.82, 1.62), (0.36, 0.12, 0.22), pm("#e8e0d0", 0.6), -0.2, 0.01)
    text("PARIS", (0.62, 0.885, 1.62), 0.05, pm("#2a2a2a", 0.6), -0.2, "serif", 0.001, pitch=-math.pi / 2)
    K.cyl((0.35, 0.86, 2.2), 0.06, 0.2, glassm(), 16)
    for k in range(9):
        a = rnd.random() * math.tau; K.sphere((0.35 + 0.08 * math.cos(a), 1.02 + rnd.uniform(0, 0.12), 2.2 + 0.08 * math.sin(a)), 0.045, pm(["#e8c8d8", "#c82a3a", "#f2e2a8"][k % 3], 0.6), 8)
    for k, (x, z) in enumerate(((-0.4, 1.55), (0.3, 1.55), (-0.25, 2.25))): cup(f"hs_cup{k}", (x, 0.76, z), "#f4f0e8", True)
    K.cyl((-0.15, 0.85, 2.25), 0.06, 0.18, pm("#f4f0e8", 0.3), 16)
    for s in (-1, 1): IK.chair(f"hs_ch{s}", s * 1.25, 1.9, -s * math.pi / 2, oak, IK.velvet("hs_seat", "#5a3a2a", 0.6), 0.48, True, None)
    IK.chair("hs_ch0", 0, 2.75, math.pi, oak, IK.velvet("hs_seat", "#5a3a2a", 0.6), 0.48, True, None)
    # garland of little flags + "ALLES GUTE" banner on the back wall
    for k in range(17):
        x = -3.2 + k * 0.4; y = 2.6 - 0.25 * math.sin(math.pi * k / 16)
        K.quad([(x - 0.12, y, 4.12), (x + 0.12, y, 4.12), (x, y - 0.25, 4.12)], pm(["#c8202c", "#e8c040", "#3a6aa8", "#4a8a4a"][k % 4], 0.6))
    K.box((0, 2.62, 4.12), (6.6, 0.01, 0.01), pm("#f0ead8", 0.8), 0, 0)
    ban = C.poster_img([("ALLES GUTE", 0.3, "#8a1e1e")], "#f4ecd8", "#8a1e1e", 512, 96, seed=2)
    IK.panel("hs_banner", (0.6, 2.05, 4.14), 2.0, 0.38, IK.img_mat("hs_ban", ban, 0.8), 0)
    # the back wall: a tiled stove, a sideboard with a gramophone, photos, a cuckoo clock
    tile = C.SB.brick("hs_tile", "#3a6a5a", "#2e5a4c", "#d8d0c0", 3.0, 0.2, 0.2, 0.3)
    K.box((2.9, 1.0, 3.7), (1.0, 2.0, 0.8), tile, 0, 0.02); K.box((2.9, 2.05, 3.7), (1.1, 0.1, 0.9), white, 0, 0.01)
    K.box((2.9, 0.45, 3.29), (0.3, 0.25, 0.02), pm("#2a2a2a", 0.4, 0.6), 0, 0.005)
    K.box((-2.4, 0.45, 3.9), (1.8, 0.9, 0.5), oak, 0, 0.02)
    for k in range(3): K.box((-3.0 + k * 0.6, 0.5, 3.64), (0.5, 0.7, 0.02), C.SB.wood("#7a4a26", "#4a2814", 6), 0, 0.01)
    K.box((-2.6, 1.0, 3.9), (0.4, 0.2, 0.4), oak, 0, 0.01); lathe("hs_horn", [(0.02, 0.0), (0.04, 0.1), (0.1, 0.3), (0.25, 0.45), (0.26, 0.46)], (-2.6, 1.1, 3.95), brass(), 24)
    K.cyl((-2.6, 1.11, 3.9), 0.15, 0.01, pm("#141414", 0.3), 24)
    for k in range(4):
        IK.framed(f"hs_ph{k}", (-3.2 + k * 0.42, 1.25 + (k % 2) * 0.05, 3.98), 0.26, 0.32, IK.img_mat(f"hs_phm{k}", IK.portrait_img(140 + k, 96, 120), 0.5), gold(), 0, 0.03, 0.02)
    IK.framed("hs_paint", (-1.25, 1.75, 4.16), 1.0, 0.65, IK.img_mat("hs_land", IK.landscape_img(77, 256, 160, water=True), 0.5, coat=0.3), gold(), 0, 0.07, 0.04)
    wall_clock("hs_clk", (1.6, 2.2, 4.1), "")
    # the +x side: an armchair, standing lamp (lit), a small table with the newspaper and a radio
    K.box((3.2, 0.25, 0.2), (0.9, 0.5, 0.9), IK.velvet("hs_arm", "#4a5a3a", 0.8), 0, 0.08); K.box((3.55, 0.75, 0.2), (0.2, 1.0, 0.9), IK.velvet("hs_arm", "#4a5a3a", 0.8), 0, 0.08)
    for s in (-1, 1): K.box((3.2, 0.6, 0.2 + s * 0.42), (0.9, 0.3, 0.12), IK.velvet("hs_arm", "#4a5a3a", 0.8), 0, 0.05)
    K.cyl((3.4, 0.8, -1.0), 0.02, 1.6, brass(), 8); K.cyl((3.4, 1.7, -1.0), 0.22, 0.3, pm("#f0c890", 0.8), 20, "y", 0.14)
    C.lamp((3.4, 1.62, -1.0), 50, (1.0, 0.7, 0.4), 0.08)
    K.cyl((3.3, 0.55, 1.2), 0.3, 0.03, oak, 20); K.cyl((3.3, 0.28, 1.2), 0.03, 0.55, oak, 8)
    K.box((3.3, 0.68, 1.2), (0.36, 0.24, 0.22), C.SB.wood("#6a3a1a", "#3a1e0c", 8), 0.3, 0.02); K.box((3.18, 0.7, 1.13), (0.02, 0.12, 0.14), pm("#d8c8a0", 0.8), 0.3, 0)
    C.fill((0, 2.4, -2.7), (0, 1.0, 1.6), 260, (1.0, 0.86, 0.68), 3.0, 1.5)
    # ================= B. the Berghof corridor =================
    CX = 40.0
    stone = C.plaster("hsb", "#d8ccb4"); panel = C.SB.wood("#5a3a20", "#2a1a0c", 5, 0.4)
    K.box((CX, -0.05, 3.2), (3.8, 0.1, 11), C.planks("hs_bfl", "#6a4428", "#3a2414", "Z", 0.12, 1.4), 0, 0)
    K.box((CX, 3.45, 3.2), (3.8, 0.1, 11), stone, 0, 0)
    for k in range(6): K.box((CX, 3.3, -1.5 + k * 2), (3.6, 0.2, 0.25), panel, 0, 0.02)
    for sx in (-1, 1):
        K.box((CX + sx * 1.85, 1.7, 3.2), (0.1, 3.4, 11), stone, 0, 0)
        K.box((CX + sx * 1.78, 0.6, 3.2), (0.06, 1.2, 10.8), panel, 0, 0.005); K.box((CX + sx * 1.76, 1.22, 3.2), (0.08, 0.05, 10.8), panel, 0, 0.005)
    K.box((CX, 1.7, 8.55), (3.8, 3.4, 0.1), stone, 0, 0); K.box((CX, 1.7, -2.05), (3.8, 3.4, 0.1), stone, 0, 0)
    IK.floor_quad("hs_runner", (CX, 3.5), 1.4, 9.5, IK.img_mat("hs_runm", IK.carpet_img(96, 640, "#6a1a1a", "#c8a24a", "#1e2a3a"), 0.9), 0, 0.006)
    # the bedroom door: heavy panelled oak, brass handle, the sign
    door = C.SB.wood("#5a3418", "#2a1608", 4, 0.35)
    K.box((CX, 1.25, 8.46), (1.4, 2.5, 0.1), door, 0, 0.02)
    for r in range(2):
        for c in range(2): K.box((CX - 0.33 + c * 0.66, 0.7 + r * 1.15, 8.4), (0.5, 0.9, 0.04), C.SB.wood("#6a4020", "#3a2010", 5, 0.35), 0, 0.02)
    for s in (-1, 1): K.box((CX + s * 0.78, 1.3, 8.45), (0.16, 2.7, 0.16), panel, 0, 0.01)
    K.box((CX, 2.7, 8.45), (1.8, 0.18, 0.16), panel, 0, 0.01)
    K.box((CX + 0.52, 1.1, 8.38), (0.05, 0.05, 0.06), brass(), 0, 0); K.cyl((CX + 0.45, 1.1, 8.35), 0.012, 0.14, brass(), 8, "x")
    K.box((CX + 0.42, 0.98, 8.37), (0.004, 0.24, 0.004), pm("#3a2a1a", 0.8), 0, 0)
    sg = C.poster_img([("BITTE", 0.2, "#8a1e1e"), ("NICHT", 0.2, "#8a1e1e"), ("STÖREN", 0.2, "#8a1e1e")], "#f4ecd8", "#2a1a14", 160, 200, seed=8)
    IK.panel("hs_dnd", (CX + 0.42, 0.75, 8.37), 0.3, 0.38, IK.img_mat("hs_dndm", sg, 0.7), 0)
    # the hall table with the ringing telephone, a clock, a long bench, paintings, sconces, a tall window
    K.box((CX + 1.45, 0.78, 5.0), (0.5, 0.05, 1.0), panel, 0, 0.01)
    for sz in (-0.4, 0.4): K.box((CX + 1.45, 0.39, 5.0 + sz), (0.06, 0.78, 0.06), panel, 0, 0)
    phone("hs_ph", (CX + 1.4, 0.8, 5.0), math.pi / 2)
    wall_clock("hs_clk2", (CX - 1.78, 2.3, 6.5), "")
    K.box((CX - 1.5, 0.45, 2.5), (0.45, 0.06, 1.8), panel, 0, 0.01)
    for k in range(3):
        IK.framed(f"hs_bp{k}", (CX + 1.79, 2.0, 0.5 + k * 2.6), 1.0, 0.7, IK.img_mat(f"hs_bpm{k}", IK.landscape_img(200 + k, 256, 180, water=k == 1), 0.5, coat=0.3), gold(), -math.pi / 2, 0.06, 0.04)
    for z in (1.5, 4.5, 7.2):
        for sx in (-1, 1):
            K.box((CX + sx * 1.76, 2.2, z), (0.06, 0.2, 0.12), brass(), 0, 0.01)
            K.cyl((CX + sx * 1.62, 2.38, z), 0.07, 0.14, pm("#f0c890", 0.8), 16, "y", 0.1)
            C.lamp((CX + sx * 1.55, 2.32, z), 18, (1.0, 0.68, 0.38), 0.05)
    K.box((CX - 1.82, 1.9, 1.0), (0.04, 2.2, 1.4), em("#7a9ad8", 1.2), 0, 0)
    for k in range(3): K.box((CX - 1.78, 0.8 + k * 1.1, 1.0), (0.08, 0.06, 1.5), panel, 0, 0.005)
    C.fill((CX - 1.6, 1.9, 1.0), (CX + 1, 1.0, 3.0), 60, (0.6, 0.72, 1.0), 1.0, 2.0)
    C.fill((CX, 2.8, -1.6), (CX, 1.0, 6.0), 120, (1.0, 0.8, 0.6), 2.5, 1.0)
    C.lamp((CX, 2.6, 7.6), 30, (1.0, 0.7, 0.42), 0.1)
    K.build()
    return {}
