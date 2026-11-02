# The League of Nations council hall, Geneva (chapter 2 shots 6-8, 21-22). Layout (three coords, cameras look +z):
# hall x -9..9, z -5..15, ceiling 7.5. Horseshoe council table: the curve centred (0, 7) radius 3.6 (open toward the
# camera), straight arms along x = +-3.6 from z 7 down to z 2; table top y 0.78, baize green, nameplates, papers, carafes,
# microphones. Delegates stand OUTSIDE the horseshoe: arms at x +-4.4 (z 2.5..6.5), curve at radius 4.4 (z ~11.4 at the
# back). The rapporteur's lectern stands inside the horseshoe at (0, 0, 4.3) facing the camera. The president's dais is
# at z 12.6 (top 0.5) with a long desk, the SOCIÉTÉ DES NATIONS banner and the member flags behind. Exit doors on the -x
# wall at (-8.9, 0, 3) with a SORTIE lamp (Japan walks out there, shot 8). Light: tall windows on the +x wall (Lake
# Geneva beyond, sun shafts), three chandeliers, warm fill from the camera end.
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK

NAMES = ["JAPON", "CHINE", "FRANCE", "ROYAUME-UNI", "ITALIE", "ALLEMAGNE", "ESPAGNE", "POLOGNE", "SUÈDE", "PERSE", "PÉROU", "IRLANDE",
         "NORVÈGE", "TCHÉCOSLOVAQUIE", "MEXIQUE", "PANAMA", "GUATEMALA", "YOUGOSLAVIE"]
def build(M, D):
    random.seed(1932); KS.reset(); rnd = random.Random(1932)
    K = Kit("league")
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.4, 0.5, 0.65, 1); bg.inputs[1].default_value = 0.3
    FL = IK.planks("lfloor", "#9a6a3a", "#5a3a1e", "Y", 0.1, 0.8, 0.35, 0.3, diag=False); WALL = lib.plaster("lwall", "#e8dcc4"); PAN = lib.plaster("lpanel", "#f2e8d4")
    OAK = wood("#8a5a30", "#4a2a14", 6, 0.35); DOAK = wood("#5a3418", "#2a160a", 5, 0.35); BAIZE = lib.cloth("lbaize", "#2e5a3a")
    GILT = lib.gilt("lgilt"); BR = brass(); MARB = lib.marble("lmarble"); VEL = IK.velvet("lvel", "#2a3a6a", 0.9); LEATH = pm("#6a2a1a", 0.45)
    RH = 7.5
    # ---------------- shell ----------------
    K.box((0, -0.05, 5), (18.4, 0.1, 20.4), FL, 0, 0)
    K.box((0, 0.006, 6.5), (12, 0.012, 12), lib.carpet("lrug", "#7a2a22", "#d8b860"), 0, 0.003)
    K.box((0, RH + 0.1, 5), (18.4, 0.2, 20.4), PAN, 0, 0)
    for k in range(7): K.box((0, RH - 0.2, -4 + k * 3), (18, 0.35, 0.4), GILT, 0, 0.03)
    K.box((0, RH / 2, 15.2), (18.4, RH, 0.4), WALL, 0, 0)
    K.box((0, RH / 2, -5.2), (18.4, RH, 0.4), WALL, 0, 0)
    K.box((-9.2, RH / 2, 5), (0.4, RH, 20.4), WALL, 0, 0)
    for sx in (-1, 1):
        K.box((sx * 8.96, 0.6, 5), (0.08, 1.2, 20), DOAK, 0, 0.01); K.box((sx * 8.92, 1.22, 5), (0.12, 0.06, 20), GILT, 0, 0.01)
    K.box((0, 0.6, 14.96), (18, 1.2, 0.08), DOAK, 0, 0.01); K.box((0, 1.22, 14.92), (18, 0.06, 0.12), GILT, 0, 0.01)
    # +x wall: tall windows between marble pilasters, lake view, real openings with sun shafts
    ZW = [-2.0, 2.0, 6.0, 10.0]; y0, y1 = 1.0, 5.8; ow = 1.3
    edges = [-5.4] + [v for z in ZW for v in (z - ow, z + ow)] + [15.4]
    for k in range(0, len(edges), 2):
        a, b = edges[k], edges[k + 1]; K.box((9.2, RH / 2, (a + b) / 2), (0.4, RH, b - a), WALL, 0, 0)
    for z in ZW:
        K.box((9.2, y0 / 2, z), (0.4, y0, 2 * ow), WALL, 0, 0); K.box((9.2, (y1 + RH) / 2, z), (0.4, RH - y1, 2 * ow), WALL, 0, 0)
        for j in range(1, 7): K.box((9.05, y0 + j * (y1 - y0) / 7, z), (0.05, 0.04, 2 * ow), PAN, 0, 0.003)
        K.box((9.05, (y0 + y1) / 2, z), (0.06, y1 - y0, 0.06), PAN, 0, 0.003)
        for sd in (-1, 1): IK.drape(f"ld{z}{sd}", (8.75, y1 + 0.4, z + sd * (ow + 0.15)), 0.8, y1 + 0.3, VEL, -R90, 5, 0.06, gather=sd * 0.8)
        K.box((8.7, y1 + 0.5, z), (0.15, 0.35, 2 * ow + 0.6), GILT, 0, 0.02)
        CK.lib.light("AREA", T(9.6, (y0 + y1) / 2, z), 300, (0.75, 0.85, 1.0), 2.4, size_y=4.6).rotation_euler = (0, math.radians(-90), 0)
    out = IK.panel("lake", (14, 3.2, 4.0), 30, 9, IK.img_mat("lakei", IK.landscape_img(1936, 768, 288, water=True), 1.0, emit=0.8), R90)
    IK.hide_from_light(out)
    SUN_D = (-0.8, -0.45, 0.35)
    IK.sun(SUN_D, 5.0, (1.0, 0.86, 0.66), 1.0)
    for z in ZW: IK.beam(f"lsh{z}", [(9.0, y1, z - ow), (9.0, y1, z + ow), (9.0, y0, z + ow), (9.0, y0, z - ow)], SUN_D, 10.0, (1.0, 0.88, 0.66), 0.14)
    for z in (0.0, 4.0, 8.0, 12.0):
        K.box((8.9, RH / 2, z), (0.25, RH, 0.6), MARB, 0, 0.01); K.box((8.82, RH - 0.6, z), (0.35, 0.35, 0.8), GILT, 0, 0.02)
    # -x wall: exit doors with SORTIE lamp, press gallery benches, portraits
    dz = 3.0
    K.box((-8.95, 1.6, dz), (0.12, 3.2, 2.2), DOAK, 0, 0.02)
    for sd in (-1, 1):
        K.box((-8.86, 1.6, dz + sd * 0.55), (0.06, 2.9, 1.0), OAK, 0, 0.02)
        for j in range(2): K.box((-8.82, 0.9 + j * 1.4, dz + sd * 0.55), (0.03, 1.1, 0.75), DOAK, 0, 0.02)
        K.cyl((-8.78, 1.4, dz + sd * 0.12), 0.02, 0.35, BR, 8)
    K.box((-8.86, 3.4, dz), (0.1, 0.3, 2.6), GILT, 0, 0.02)
    K.box((-8.8, 3.85, dz), (0.08, 0.32, 1.1), pm("#1a1a1a", 0.4), 0, 0.01)
    text("SORTIE", (-8.75, 3.85, dz), 0.2, em("#7aff8a", 4.0), -R90, "sans", 0.004)
    for k in range(3):
        z = 7.5 + k * 1.6
        K.box((-7.6, 0.25 + k * 0.45, z - 1.3), (2.4, 0.08, 0.45), OAK, 0, 0.01)
    for j in range(3):
        for k in range(3): K.box((-7.0 - j * 0.6, 0.45 + j * 0.4, -1.8 + k * 1.6), (0.5, 0.06, 1.3), OAK, 0, 0.01)
    for k, z in enumerate((-1.5, 8.0, 12.0)):
        IK.framed(f"lp{k}", (-8.98, 3.9, z), 1.0, 1.3, IK.img_mat(f"lpi{k}", IK.portrait_img(100 + k), 0.55, coat=0.3), GILT, -math.pi / 2, 0.08, 0.06)
    # back: the president's dais, banner, flags, clock
    K.box((0, 0.25, 13.0), (10, 0.5, 3.6), DOAK, 0, 0.02)
    for k in range(3): K.box((0, 0.08 + k * 0.17, 11.1 - k * 0.0), (10 - k * 0.2, 0.17, 0.5 - k * 0.0), OAK, 0, 0.01) if k == 0 else None
    K.box((0, 0.95, 12.5), (6.0, 0.9, 0.9), OAK, 0, 0.02); K.box((0, 1.42, 12.5), (6.2, 0.06, 1.1), BAIZE, 0, 0.01)
    for k in range(6): K.box((-2.5 + k, 0.95, 12.04), (0.7, 0.6, 0.03), DOAK, 0, 0.02)
    K.box((0, 4.6, 14.9), (9.0, 1.6, 0.1), pm("#1e2a5a", 0.6), 0, 0.02)
    KS._frame(K, (0, 4.6, 14.84), 9.0, 1.6, 0, GILT, 0.08, 0.06)
    text("SOCIÉTÉ DES NATIONS", (0, 4.85, 14.82), 0.5, gold(), 0, "serif", 0.01, fit=8.2)
    text("LEAGUE OF NATIONS", (0, 4.2, 14.82), 0.32, pm("#e8dcc0", 0.5), 0, "serif", 0.006, fit=6)
    K.cyl((0, 2.8, 14.85), 0.6, 0.06, gold(), 32, "z"); K.cyl((0, 2.8, 14.82), 0.48, 0.03, pm("#1e2a5a", 0.6), 32, "z")
    text("SDN", (0, 2.8, 14.79), 0.3, gold(), 0, "serif", 0.004)
    kinds = ["fr", "uk", "it", "jp"]
    for k, x in enumerate((-7.0, -5.6, -4.2, 4.2, 5.6, 7.0)):
        CK.flagpole(K, (x, 0.5, 14.3), 4.2, IK.img_mat(f"lfl{k}", IK.flag_img(kinds[k % 4]) if kinds[k % 4] in ("fr", "uk", "it", "us") else _plain_flag(k), 0.75, sheen=0.4), 1.3, 0.85, BR)
    K.cyl((-6.5, 6.0, 14.9), 0.5, 0.08, pm("#f2ece0", 0.4), 32, "z"); K.torus((-6.5, 6.0, 14.86), 0.52, 0.05, GILT, 32, 6, "z")
    for a, ln in ((0.5, 0.3), (-1.2, 0.4)): K.box((-6.5 + ln / 2 * math.sin(a), 6.0 + ln / 2 * math.cos(a), 14.84), (0.03, ln, 0.02), pm("#1a1a1a", 0.5), 0, 0, 0, a)
    # ---------------- the horseshoe table ----------------
    R0, RD, CZ = 3.6, 0.9, 7.0
    def seg(x, z, L, yaw):
        K.box((x, 0.75, z), (L, 0.06, RD), BAIZE, yaw, 0.01)
        K.box((x, 0.6, z), (L - 0.05, 0.28, RD - 0.12), OAK, yaw, 0.01)
    n = 14
    for k in range(n):
        a = math.pi * (k + 0.5) / n; L = math.pi * R0 / n + 0.02
        seg(R0 * math.cos(a), CZ + R0 * math.sin(a), L, -(a + math.pi / 2))
    for sx in (-1, 1):
        seg(sx * R0, (CZ + 2.0) / 2, CZ - 2.0, R90)
        for z in (2.3, 4.0, 5.7): K.box((sx * R0, 0.3, z), (0.08, 0.6, 0.08), DOAK, 0, 0.01)
    # places: nameplate, blotter, papers, carafe & glass, microphone, inkwell; chairs outside
    places = []
    for k in range(4): places.append((R0, 2.6 + k * 1.3, -R90))
    for k in range(4): places.append((-R0, 2.6 + k * 1.3, R90))
    for k in range(7):
        a = math.pi * (k + 0.5) / 7; places.append((R0 * math.cos(a), CZ + R0 * math.sin(a), math.pi / 2 - a + math.pi))
    MIC = pm("#2a2a2a", 0.3, 0.7); CAR = lib.glass("lcarafe"); PAPER = paper()
    docs = [IK.img_mat(f"ldoc{k}", IK.doc_img(k + 7, ["RAPPORT", "MANDCHOURIE", "PROCÈS-VERBAL", "RÉSOLUTION"][k]), 0.8) for k in range(4)]
    order = [0, 1, 4, 5, 2, 3, 7, 6, 8, 9, 10, 11, 12, 13, 14]
    for i, (x, z, yaw) in enumerate(places):
        nm = NAMES[order[i % len(order)]]
        # facing: toward the horseshoe centre line; the delegate stands outside, so things sit on the table
        ux, uz = (0 - x), ((CZ if z > CZ - 0.1 else z) - z)
        if abs(x) >= R0 - 0.01 and z <= CZ: ux, uz = -math.copysign(1, x), 0.0
        L = math.hypot(ux, uz) or 1; ux /= L; uz /= L
        px, pz = x + ux * 0.15, z + uz * 0.15
        pyaw = math.atan2(ux, uz) + math.pi    # plate faces the centre (away from its delegate)
        K.box((px + ux * 0.2, 0.86, pz + uz * 0.2), (0.5, 0.13, 0.02), pm("#f2ece0", 0.5), pyaw, 0.003)
        text(nm, (px + ux * 0.21 - math.sin(pyaw) * 0.0, 0.86, pz + uz * 0.21), 0.05, pm("#1a1a1a", 0.5), pyaw, "serif", 0.001, fit=0.46)
        text(nm, (px + ux * 0.19, 0.86, pz + uz * 0.19), 0.05, pm("#1a1a1a", 0.5), pyaw + math.pi, "serif", 0.001, fit=0.46)
        K.box((px - ux * 0.15, 0.785, pz - uz * 0.15), (0.45, 0.006, 0.35), pm("#5a2a1a", 0.7), pyaw, 0.001)
        CK.quad_uv(f"ldc{i}", [(px - ux * 0.15 - 0.1, 0.79, pz - uz * 0.15 - 0.14), (px - ux * 0.15 + 0.1, 0.79, pz - uz * 0.15 - 0.14),
                               (px - ux * 0.15 + 0.1, 0.79, pz - uz * 0.15 + 0.14), (px - ux * 0.15 - 0.1, 0.79, pz - uz * 0.15 + 0.14)], docs[i % 4])
        side = (-uz, ux)
        K.cyl((px + side[0] * 0.3, 0.88, pz + side[1] * 0.3), 0.05, 0.2, CAR, 12); K.cyl((px + side[0] * 0.4, 0.83, pz + side[1] * 0.4), 0.03, 0.1, CAR, 10)
        K.cyl((px - side[0] * 0.3, 0.8, pz - side[1] * 0.3), 0.05, 0.02, MIC, 12); K.cyl((px - side[0] * 0.3, 0.92, pz - side[1] * 0.3), 0.008, 0.24, MIC, 6)
        K.sphere((px - side[0] * 0.3 + ux * 0.04, 1.06, pz - side[1] * 0.3 + uz * 0.04), 0.035, MIC, 10)
        for j in range(rnd.randint(1, 3)): K.box((px - side[0] * 0.05 + rnd.uniform(-0.05, 0.05), 0.8 + j * 0.03, pz - side[1] * 0.05), (0.24, 0.03, 0.32), PAPER if j % 2 else pm("#c8b88a", 0.8), pyaw + rnd.uniform(-0.2, 0.2), 0.003)
        cxx, czz = x - ux * 0.95, z - uz * 0.95
        IK.chair(f"lch{i}", cxx, czz, math.atan2(ux, uz), DOAK, LEATH, 0.48, True, GILT)
    # the rapporteur's lectern inside the horseshoe, the stacked report, a bell
    LEC = IK.grain("llec", "#7a4a24", "#3a2010", "Y", 1.0, 0.4)
    K.box((0, 0.55, 4.6), (0.7, 1.1, 0.5), LEC, 0, 0.02); K.box((0, 1.15, 4.55), (0.8, 0.06, 0.6), LEC, 0, 0.02, -0.25)
    for j in range(5): K.box((0.9 + j * 0.0, 0.8 + j * 0.06, 6.9), (0.45, 0.06, 0.6), PAPER if j % 2 else pm("#d8c8a0", 0.8), 0.05 * j, 0.004)
    K.box((0.9, 1.12, 6.9), (0.06, 0.04, 0.62), pm("#a81e22", 0.6), 0, 0.002)
    flat_text("RAPPORT\nLYTTON", (0.9, 1.115, 6.9), 0.07, pm("#1a1a1a", 0.6), 0, "serif")
    K.cyl((0.0, 1.47, 12.3), 0.07, 0.1, BR, 16)
    # chandeliers
    for z in (1.0, 6.5, 11.0):
        K.cyl((0, RH - 0.8, z), 0.025, 1.6, GILT, 8)
        for r, y, n_ in ((1.1, RH - 2.0, 12), (0.6, RH - 1.6, 8)):
            K.torus((0, y, z), r, 0.03, GILT, 36, 6, "y")
            for j in range(n_):
                a = j / n_ * math.tau; K.cyl((r * math.cos(a), y + 0.1, z + r * math.sin(a)), 0.02, 0.14, pm("#f4eedc", 0.4), 8)
                K.sphere((r * math.cos(a), y + 0.21, z + r * math.sin(a)), 0.03, em("#ffe2b0", 12.0), 6)
        lib.light("POINT", T(0, RH - 1.8, z), 600, (1.0, 0.75, 0.48), 0.8)
    # fill from the camera end, soft side fill
    lib.light("AREA", T(0, 4.5, -4.6), 700, (1.0, 0.86, 0.68), 7, size_y=3).rotation_euler = (math.radians(-70), 0, math.pi)
    lib.light("AREA", T(-6.5, 5.0, 5.0), 200, (0.9, 0.9, 1.0), 4).rotation_euler = (0, math.radians(60), 0)
    K.build()
    return {}

def _plain_flag(k):
    cols = [("#1e3a8a", "#f2ece0", "#1e3a8a"), ("#c8202a", "#f2ece0", "#c8202a"), ("#2a7a3a", "#f2ece0", "#c8202a")][k % 3]
    a = IK.canvas(256, 384, cols[0]); IK.rect(a, 0, 1 / 3, 1, 2 / 3, cols[1]); IK.rect(a, 0, 2 / 3, 1, 1, cols[2]); return a
