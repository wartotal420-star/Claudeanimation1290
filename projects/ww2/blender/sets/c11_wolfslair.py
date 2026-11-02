# The Wolf's Lair, 20 July 1944 (chapter 11: the July plot).
#  A. The conference hut inside (origin): room x -6..6, z -2.6..3.6 (back wall z 3.6, open windows on it), ceiling 3.0.
#     THE MAP TABLE: top x -2.9..2.9, z 0.45..1.85, y 0.86, on two massive oak supports (plinths) at x -1.9 and +1.9
#     (0.16 thick, z 0.6..1.7, the "thick wooden table leg"). Hitler leans over the table at about (0.4, 0, 0.0); the
#     briefcase (update()): hidden before ch11 frame 3905, then on the floor at (0.75, 0, 1.15) (his side of the right
#     support), slid to (2.35, 0, 1.15) (the far side) over frames 4040..4064. From frame 4125 the room is wrecked:
#     papers and splinters on the floor, the right end of the table top dropped, smoke hanging, a scorched floor.
#     Keep clear for characters: z -1.4..0.3 along the table front, x -5..5.
#  B. The hut outside at x 100 (front door at (100, 0, 3.0), facing -z): a low plastered barrack in the pine forest with
#     camouflage nets, a gravel yard x 92..110, z -10..2 (keep clear), a staff car, a sentry box, a big concrete bunker
#     behind. The windows at z 3.0, y 1.0..2.2, x 94..106 (fx flash cards go there).
# Light: summer midday, hot sun through the open windows, warm interior fill; outside the forest is dappled.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, gold, glassm
from sets import ikit as IK
from sets.void import smoke_mat, smoke_column
from sets.warroom import phone

CASE = None; WRECK = []; TOPR = None
def build(M, D):
    global CASE, TOPR
    rnd = random.Random(720); C.SB.reset()
    C.sky("day", (0.5, 0.8, 0.6), 0.8)
    C.sun((0.45, 0.75, 0.75), 4.5, (1.0, 0.92, 0.78), 2.0)
    K = Kit("lair")
    wall = C.plaster("wl", "#e4dcc8"); dark = C.SB.wood("#5a3a1e", "#2a1a0c", 5, 0.4); oak = C.SB.wood("#8a5a2e", "#4a2c14", 4, 0.4)
    fl = C.planks("wl_floor", "#9a7a52", "#5a4430", "X", 0.14, 2.0)
    # ================= A. inside =================
    K.box((0, -0.05, 0.5), (12.2, 0.1, 6.4), fl, 0, 0); K.box((0, 3.05, 0.5), (12.2, 0.1, 6.4), C.plaster("wlc", "#f0ead8"), 0, 0)
    for k in range(6): K.box((-5 + k * 2, 2.9, 0.5), (0.18, 0.22, 6.2), dark, 0, 0.01)
    K.box((0, 1.5, -2.65), (12.2, 3.0, 0.1), wall, 0, 0)
    for sx in (-1, 1): K.box((sx * 6.05, 1.5, 0.5), (0.1, 3.0, 6.4), wall, 0, 0)
    # back wall with five open windows (casements swung inward), sunlit pines outside
    WX = (-4.4, -2.2, 0, 2.2, 4.4); y0, y1 = 0.95, 2.35
    edges = [-6.1] + [v for x in WX for v in (x - 0.7, x + 0.7)] + [6.1]
    for k in range(0, len(edges), 2): K.box(((edges[k] + edges[k + 1]) / 2, 1.5, 3.65), (edges[k + 1] - edges[k], 3.0, 0.2), wall, 0, 0)
    pines = IK.img_mat("wl_out", IK.landscape_img(720, 512, 256), 0.8, emit=1.6)
    for x in WX:
        K.box((x, y0 / 2, 3.65), (1.4, y0, 0.2), wall, 0, 0); K.box((x, (y1 + 3.0) / 2, 3.65), (1.4, 3.0 - y1, 0.2), wall, 0, 0)
        K.box((x, y0 - 0.03, 3.5), (1.6, 0.06, 0.3), pm("#f0ead8", 0.5), 0, 0.01)
        for s in (-1, 1):
            hx = x + s * 0.7; a = s * 1.1
            K.box((hx - s * 0.35 * math.cos(a), (y0 + y1) / 2, 3.55 - 0.35 * math.sin(abs(a))), (0.7, y1 - y0, 0.04), pm("#f0ead8", 0.4), -a if s > 0 else a, 0.01)
        IK.panel(f"wl_v{x}", (x, 1.7, 4.4), 1.6, 1.8, pines)
    for x in WX:
        IK.beam(f"wl_sh{x}", [(x - 0.7, y1, 3.55), (x + 0.7, y1, 3.55), (x + 0.7, y0, 3.55), (x - 0.7, y0, 3.55)], (-0.3, -0.6, -1.0), 4.0, (1.0, 0.9, 0.7), 0.12)
    # the map table on its two massive supports
    TK = Kit("tabletop")
    TK.box((0, 0.84, 1.15), (5.8, 0.06, 1.4), oak, 0, 0.01)
    for sz in (-1, 1): TK.box((0, 0.8, 1.15 + sz * 0.68), (5.8, 0.06, 0.04), dark, 0, 0.005)
    maps = [IK.img_mat(f"wl_map{k}", IK.landscape_img(900 + k, 256, 192, naive=True), 0.7) for k in range(2)]
    docs = [IK.img_mat(f"wl_doc{k}", IK.doc_img(k, ["LAGE OST", "MELDUNG", "GEHEIM"][k % 3]), 0.8) for k in range(3)]
    tops = TK.build()
    TOPR = C.rig(tops, (-1.9, 0.84, 1.15))
    IK.floor_quad("wl_m1", (-1.0, 1.15), 2.0, 1.25, maps[0], 0.02, 0.875); IK.floor_quad("wl_m2", (1.2, 1.12), 1.6, 1.2, maps[1], -0.03, 0.876)
    for k in range(5): IK.floor_quad(f"wl_d{k}", (-2.6 + k * 1.3, 0.62), 0.24, 0.32, docs[k % 3], rnd.uniform(-0.3, 0.3), 0.878)
    for sx in (-1.9, 1.9):
        K.box((sx, 0.4, 1.15), (0.16, 0.8, 1.1), oak, 0, 0.02)
        K.box((sx, 0.05, 1.15), (0.36, 0.1, 1.3), dark, 0, 0.02); K.box((sx, 0.76, 1.15), (0.3, 0.08, 1.2), dark, 0, 0.02)
    K.box((0, 0.5, 1.15), (3.6, 0.1, 0.12), oak, 0, 0.01)
    for k in range(3): K.cyl((-2.0 + k * 1.6, 0.9, 1.75), 0.008, 0.18, pm("#3a2a1a", 0.6), 6, "x", None, 0.6 * k)
    # chairs pushed back, side tables with telephones, a coat stand, a radiator, a map board, a clock
    seat = C.SB.cloth("#6a5a40")
    for k, (x, z, yaw) in enumerate(((-4.7, 2.6, math.pi), (-3.6, 2.7, math.pi + 0.3), (3.8, 2.6, math.pi - 0.2), (5.0, -1.8, 0.4), (-5.2, -1.5, -0.3))):
        IK.chair(f"wl_ch{k}", x, z, yaw, oak, seat, 0.46, True, None)
    for sx in (-1, 1):
        K.box((sx * 5.6, 0.75, -0.6), (0.6, 0.05, 1.2), dark, 0, 0.01)
        for sz in (-0.5, 0.5): K.box((sx * 5.6, 0.37, -0.6 + sz), (0.05, 0.74, 0.05), dark, 0, 0)
    phone("wl_ph1", (5.6, 0.78, -0.8), -math.pi / 2); phone("wl_ph2", (-5.6, 0.78, -0.4), math.pi / 2)
    for k in range(10): K.box((-5.9, 0.45, -2.0 + k * 0.08), (0.12, 0.6, 0.04), iron("#c8c4b8"), 0, 0.01)
    K.box((0, 1.6, -2.57), (3.0, 1.8, 0.04), pm("#d8cca8", 0.8), 0, 0.01)
    IK.panel("wl_wallmap", (0, 1.6, -2.54), 2.8, 1.6, maps[1], math.pi)
    K.cyl((4.6, 0.9, -2.0), 0.02, 1.8, dark, 8); K.box((4.6, 1.75, -2.0), (0.5, 0.04, 0.04), dark, 0, 0)
    for k in range(2): K.box((4.5 + k * 0.2, 1.4, -2.0), (0.35, 0.7, 0.14), pm(["#5e6658", "#4a5040"][k], 0.9), 0, 0.05)
    K.cyl((4.6, 1.85, -1.95), 0.12, 0.08, pm("#5e6658", 0.7), 16, "y", 0.1)
    for x in (-3, 0, 3):
        K.cyl((x, 2.85, 0.6), 0.25, 0.14, pm("#f0ead8", 0.5), 20, "y", 0.12); K.cyl((x, 2.76, 0.6), 0.06, 0.06, em("#fff4dc", 8), 10)
    C.fill((0, 2.6, -2.2), (0, 0.8, 1.2), 380, (1.0, 0.9, 0.76), 5, 1.5)
    C.fill((0, 2.0, 5.0), (0, 0.8, 0.5), 900, (0.85, 0.92, 1.0), 10, 1.2)
    C.fill((2.0, 0.4, -1.2), (1.8, 0.2, 1.2), 30, (1.0, 0.9, 0.75), 1.5)
    # the briefcase (rigged)
    BK = Kit("case"); leather = C.SB.cloth("#5a3a22")
    BK.box((0, 0.21, 0), (0.44, 0.34, 0.14), leather, 0, 0.03); BK.box((0, 0.39, 0), (0.42, 0.03, 0.12), C.SB.cloth("#4a2e1a"), 0, 0.01)
    BK.torus((0, 0.43, 0), 0.06, 0.012, leather, 12, 5, "z", 0, 0, 0, (1.0, 1.0, 1.0), math.pi)
    for s in (-1, 1): BK.box((s * 0.14, 0.33, -0.072), (0.04, 0.04, 0.01), brass(), 0, 0)
    CASE = C.rig(BK.build(), (0, 0, 0))
    # the wreck (shown from frame 4125): splinters, papers, scorch, smoke
    WK = Kit("wreck")
    for k in range(60):
        x, z = rnd.uniform(-5, 5), rnd.uniform(-2.3, 3.2)
        WK.box((x, 0.01, z), (rnd.uniform(0.2, 0.6), 0.02, rnd.uniform(0.03, 0.09)), oak if k % 2 else dark, rnd.random() * 3, 0.0)
    for k in range(40):
        x, z = rnd.uniform(-5, 5), rnd.uniform(-2.3, 3.2)
        WK.box((x, 0.012, z), (0.21, 0.004, 0.3), C.SB.paper("#f0e8d4"), rnd.random() * 3, 0.0, rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2))
    WK.cyl((2.35, 0.006, 1.15), 1.1, 0.01, pm("#141010", 0.9), 24)
    for k in range(4): WK.box((rnd.uniform(-4, 4), 0.25, rnd.uniform(-2, 0)), (0.5, 0.06, 0.5), seat, rnd.random() * 3, 0.01, 1.2, 0.3)
    WRECK.extend(WK.build())
    sm = smoke_mat("wl_smoke", "#8a8478", 0.35)
    WRECK.extend(C.grab(smoke_column, "wl_sm", (2.3, 0.4, 1.2), 2.4, 0.8, 2.2, sm, (-1.5, 0.5), 3, 7))
    # ================= B. outside =================
    OX = 100.0
    gm = C.grass_mat("wl_grass", "#4a6a2a", "#6a7a34", "#9a8a4a")
    C.ground("wl_ground", OX - 60, OX + 60, -40, 70, 1.0, lambda x, z: 0.0 if (abs(x - OX) < 14 and -14 < z < 12) else 0.2 * C.nz2(x, z, 0.08, 3), gm)
    K.box((OX, 0.01, -4), (18, 0.02, 14), C.sand_mat("wl_gravel", "#a8a090", "#7a7468"), 0, 0)
    ext = C.plaster("wlx", "#c8c0a8")
    K.box((OX, 1.6, 6.0), (14, 3.2, 6.0), ext, 0, 0.02)
    for k in range(6):
        x = OX - 6 + k * 2.4
        if abs(x - OX) < 0.5: continue
        K.box((x, 1.6, 2.98), (1.2, 1.2, 0.04), pm("#1e2228", 0.1), 0, 0)
        for s in (-1, 1): K.box((x + s * 0.62, 1.6, 2.94), (0.06, 1.3, 0.06), pm("#f0ead8", 0.5), 0, 0); K.box((x, 1.6 + s * 0.62, 2.94), (1.3, 0.06, 0.06), pm("#f0ead8", 0.5), 0, 0)
    K.box((OX, 1.1, 2.97), (1.1, 2.2, 0.06), dark, 0, 0.01); K.box((OX, 2.35, 2.9), (1.6, 0.12, 0.3), dark, 0, 0.01)
    for k in range(2): K.box((OX, 0.08 + k * 0.16, 2.6 - k * 0.3), (1.8, 0.16, 0.4), C.concrete("wl_step", "#9a9488"), 0, 0.01)
    K.quad([(OX + 7.4, 3.2, 2.6), (OX - 7.4, 3.2, 2.6), (OX - 7.4, 3.9, 6.0), (OX + 7.4, 3.9, 6.0)], C.SB.stripes("wl_roof", "#3a3a36", "#2e2e2a", 5, 2))
    K.quad([(OX - 7.4, 3.2, 9.4), (OX + 7.4, 3.2, 9.4), (OX + 7.4, 3.9, 6.0), (OX - 7.4, 3.9, 6.0)], C.SB.stripes("wl_roof", "#3a3a36", "#2e2e2a", 5, 2))
    netm = C.foliage_mat("wl_net", "#4a5a2a", "#2a3418")
    for k in range(26): K.sphere((OX - 7 + rnd.uniform(0, 14), 3.9, rnd.uniform(3, 9)), rnd.uniform(0.6, 1.2), netm, 8, (1.3, 0.35, 1.2))
    sign(K, (OX - 1.6, 2.0, 2.92), 0.8, 0.3, 0.0, "LAGE", board="#f0ead8", ink=pm("#1e1e1e", 0.6), kind="sans")
    K.box((OX + 22, 6, 18), (16, 12, 14), C.concrete("wl_bunk", "#8a8a80"), 0, 0.2)
    for k in range(10): K.sphere((OX + 22 + rnd.uniform(-8, 8), 12.2, 18 + rnd.uniform(-7, 7)), rnd.uniform(1.4, 2.4), netm, 8, (1.3, 0.4, 1.2))
    K.box((OX - 10, 1.3, -6), (1.3, 2.6, 1.3), C.SB.wood("#6a6a5a", "#4a4a3a", 4), 0.3, 0.02)
    K.quad([(OX - 10.9, 2.6, -6.9), (OX - 9.1, 2.6, -6.9), (OX - 10, 3.1, -6)], C.SB.stripes("wl_roof", "#3a3a36", "#2e2e2a", 5, 2))
    for k in range(6): K.box((OX - 10 + 0.65 * math.cos(0.3), 0.2 + k * 0.42, -6.4), (0.02, 0.21, 1.32), pm("#c8202c" if k % 2 else "#f0ead8", 0.6), 0.3, 0)
    CM = dict(body=C.worn("wl_car", "#2a2e2a", "#1a1a18", 0.4, 0.3, 6, 0.75), dark=pm("#1a1a1a", 0.5), tyre=pm("#141414", 0.85), canvas=C.SB.cloth("#4a4a3a"))
    C.truck(K, OX + 8, -9, 0.4, CM, canvas=False)
    sign(K, (OX - 7, 1.6, -11), 2.2, 0.5, 0.2, "SPERRKREIS I", board="#f0ead8", ink=pm("#8a1e1e", 0.6), kind="sans", trim="#1e1e1e")
    for s in (-1, 1): K.box((OX - 7 + s * 0.9 * math.cos(0.2), 0.7, -11 + s * 0.9 * math.sin(-0.2)), (0.08, 1.4, 0.08), dark, 0, 0)
    PM = C.pine_mats(False); TM = C.tree_mats("summer")
    for k in range(300):
        x, z = rnd.uniform(OX - 60, OX + 60), rnd.uniform(-40, 70)
        if abs(x - OX) < 30 and -40 < z < 14: continue
        if abs(x - OX - 22) < 10 and 10 < z < 26: continue
        if k % 6 == 0: C.birch(K, x, 0, z, rnd.uniform(9, 14), rnd, TM)
        else: C.pine(K, x, 0, z, rnd.uniform(11, 17), rnd, PM)
    C.fill((OX, 8, -24), (OX, 1, 3), 6000, (1.0, 0.9, 0.75), 20)
    K.build()
    sm2 = smoke_mat("wl_smoke2", "#6a6460", 0.4)
    WRECK.extend(C.grab(smoke_column, "wl_xsm", (OX + 1.5, 3.4, 4.0), 12, 1.0, 4.0, sm2, (-5, 3), 9, 10))
    def update(f):
        wreck = f >= 4125 and f < 4320
        for o in WRECK:
            try: o.hide_render = not wreck
            except ReferenceError: pass
        if TOPR: TOPR.rotation_euler = (0, -0.12 if wreck else 0.0, 0)
        if CASE:
            CASE.hide_render = f < 3905
            for ch in CASE.children: ch.hide_render = f < 3905
            u = max(0.0, min(1.0, (f - 4040) / 24.0)); u = u * u * (3 - 2 * u)
            CASE.location = T(0.75 + 1.6 * u, 0.0, 1.15)
    return {"update": update}
