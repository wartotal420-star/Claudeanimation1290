# Paris 1919 (shots 9-12), in the three.js layout of sets.ts buildParis: hall x -8..8, z -6..14, back wall z 14 with
# tall windows, mirrors on x = +8, paintings on x = -8, long table x 0, z 1.5..10.5 (top 0.8), chandeliers at z 2/7/12,
# leaders at z ~11, the German delegate's corner at (6.4, -2.3); the bill unrolls down the carpet in shot 12.
# Keep clear: the treaty fx card lies flat at (-0.15, 0.81, 2.65) 0.75 x 0.75 (shot 11); the bill's end card at
# (0.06, 0.04, -2.6) (shot 12). Lighting: low golden sun through five real window openings (+ soft shafts), cool sky
# fill at each window, three candle chandeliers, wall sconces, torcheres, table candelabra, warm fill from the camera end.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, TS
from sets import ikit as K
from sets.ikit import bx, cy, sph, cone, torus, txt

SCROLL = None
WINX = (-6, -3, 0, 3, 6)
def build(M, D):
    global SCROLL
    random.seed(1919); rs = random.Random(1919)
    G = lib.gilt(); G2 = K.metal("gilt2", "#b8862e", 0.35)
    WALL = lib.plaster("pwall", "#e6cc9a"); PAN = lib.plaster("ppanel", "#f0dcb4"); MARB = lib.marble("pmarble")
    FL = K.planks("pfloor", "#a8683a", "#5a3218", "Y", 0.12, 0.9, 0.3, 0.35, diag=True)
    BAIZE = lib.cloth("baize", "#2a6a3c"); VEL = K.velvet("velvet", "#8a1a24"); DRAPE = K.velvet("drape", "#7a1020", 0.8)
    TW = K.grain("ptable", "#7a3e1c", "#3a1a0a", "X", 1.0, 0.3, 0.4); DADO = K.grain("pdado", "#6a3418", "#2e1408", "Y", 1.0, 0.35, 0.3)
    WHITE = K.flat("pwhite", "#f4eedc", 0.45); DARK = M["dark"]; PAPER = M["paper"]; BRASS = M["brass"]; CRYS = lib.glass("crystal")
    FLAME = lib.emit("pflame", (1.0, 0.62, 0.25), 25)
    RH = 7.0
    # ---------------- floor, carpet, ceiling ----------------
    bx("floor", (0, -0.05, 4), (17, 0.1, 23), FL, 0)
    K.floor_quad("carpet", (0, 6), 3.2, 16, K.img_mat("pcarpet", K.carpet_img(), 0.9, sheen=0.15), y=0.007)
    bx("ceiling", (0, RH + 0.1, 4), (17, 0.2, 23), PAN, 0)
    for k in range(8): bx(f"coffer{k}", (0, RH - 0.15, -5 + k * 3), (16.3, 0.3, 0.32), G, 0.03)
    for k in range(5): bx(f"cofx{k}", (-6 + k * 3, RH - 0.15, 4.5), (0.32, 0.3, 21), G, 0.03)
    frescos = [K.img_mat(f"fresco{k}", K.fresco_img(k + 3), 0.8, emit=0.15) for k in range(3)]
    for i in range(4):
        for j in range(7): K.floor_quad(f"fr{i}{j}", (-4.5 + i * 3, -3.5 + j * 3), 2.5, 2.5, frescos[(i + j) % 3], y=RH - 0.02)
    bx("crown", (0, RH - 0.25, 13.95), (16.3, 0.35, 0.3), G, 0.03)
    for sx in (-1, 1): bx(f"crowns{sx}", (sx * 7.92, RH - 0.25, 4), (0.3, 0.35, 22), G, 0.03)
    # ---------------- back wall with five real window openings ----------------
    ox, y0, y1, ZW = 0.8, 0.9, 5.1, 14.2
    edges = [-8.6] + [v for x in WINX for v in (x - ox, x + ox)] + [8.6]
    for k in range(0, len(edges), 2):
        a, b = edges[k], edges[k + 1]; bx(f"pier{k}", ((a + b) / 2, RH / 2, ZW), (b - a, RH, 0.4), WALL, 0)
    for x in WINX:
        bx(f"sill{x}", (x, y0 / 2, ZW), (2 * ox, y0, 0.4), WALL, 0); bx(f"head{x}", (x, (y1 + RH) / 2, ZW), (2 * ox, RH - y1, 0.4), WALL, 0)
        # casement: cream frames with a muntin grid, gilt arch moulding above, marble sill, drapes and a gilt pelmet
        for sx in (-1, 1): bx(f"jamb{x}{sx}", (x + sx * (ox - 0.05), (y0 + y1) / 2, ZW - 0.1), (0.1, y1 - y0, 0.22), WHITE, 0.01)
        bx(f"wtop{x}", (x, y1 - 0.05, ZW - 0.1), (2 * ox, 0.1, 0.22), WHITE, 0.01); bx(f"wbot{x}", (x, y0 + 0.05, ZW - 0.1), (2 * ox, 0.1, 0.22), WHITE, 0.01)
        bx(f"wmid{x}", (x, (y0 + y1) / 2, ZW - 0.05), (0.07, y1 - y0, 0.07), WHITE, 0.005)
        for j in range(1, 6): bx(f"wmun{x}{j}", (x, y0 + j * (y1 - y0) / 6, ZW - 0.05), (2 * ox, 0.035, 0.05), WHITE, 0.003)
        for sx in (-1, 1): bx(f"wmv{x}{sx}", (x + sx * ox / 2, (y0 + y1) / 2, ZW - 0.05), (0.035, y1 - y0, 0.05), WHITE, 0.003)
        bx(f"msill{x}", (x, y0 - 0.04, ZW - 0.22), (2 * ox + 0.3, 0.08, 0.3), MARB, 0.01)
        for k in range(13):
            a = math.pi * k / 12; r = 1.05
            bx(f"arch{x}{k}", (x + r * math.cos(a), y1 + 0.15 + r * 0.55 * math.sin(a), ZW - 0.22), (0.16, 0.12, 0.08), G, 0.01).rotation_euler[1] = -a
        sph(f"keyst{x}", (x, y1 + 0.78, ZW - 0.24), 0.12, G)
        bx(f"pelmet{x}", (x, y1 + 0.35, ZW - 0.35), (2.5, 0.35, 0.12), G2, 0.03)
        for j in range(20): cy(f"tass{x}{j}", (x - 1.2 + j * 0.126, y1 + 0.12, ZW - 0.42), 0.012, 0.12, G2, 6)
        for sx in (-1, 1):
            K.drape(f"drape{x}{sx}", (x + sx * 1.0, y1 + 0.2, ZW - 0.45), 0.75, y1 + 0.2, DRAPE, 0, 5, 0.06, gather=sx * 1.0)
            sph(f"tie{x}{sx}", (x + sx * 1.15, 1.85, ZW - 0.5), 0.05, G)
        # cool sky through the opening
        K.area((x, (y0 + y1) / 2, ZW + 0.5), (x, (y0 + y1) / 2 - 1, ZW - 3), 260, (0.72, 0.82, 1.0), 1.6, y1 - y0)
    SUN_D = (0.22, -0.5, -1.0)
    K.sun(SUN_D, 7.0, (1.0, 0.8, 0.55), 1.2)
    for x in WINX:
        K.beam(f"shaft{x}", [(x - ox, y1, ZW), (x + ox, y1, ZW), (x + ox, y0, ZW), (x - ox, y0, ZW)], SUN_D, 9.0, (1.0, 0.82, 0.55), 0.18)
    # the view outside: gardens under a late sky (emissive backdrop, casts nothing), terrace and balustrade
    out = K.panel("outside", (0, 3.4, 19.0), 34, 12, K.img_mat("pout", K.landscape_img(1919, 768, 288, water=True), 1.0, emit=0.75), 0)
    K.hide_from_light(out)
    bx("terrace", (0, -0.02, 16.5), (30, 0.04, 4.4), lib.tiles("pterr", "#d8ccb0", "#bfb090", "#8a8070", 1.5), 0)
    for k in range(16): cy(f"balu{k}", (-8 + k * 1.07, 0.45, 17.6), 0.08, 0.9, PAN, 12)
    bx("balrail", (0, 0.95, 17.6), (30, 0.12, 0.25), PAN, 0.02)
    # pilasters between the windows (marble with gilt capitals) and corner columns
    for x in (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5):
        bx(f"pil{x}", (x, RH / 2, 13.92), (0.55, RH, 0.18), MARB, 0.01)
        bx(f"pilc{x}", (x, RH - 0.65, 13.82), (0.7, 0.3, 0.12), G, 0.02); bx(f"pilb{x}", (x, 0.25, 13.82), (0.7, 0.5, 0.14), G2, 0.02)
        for f in (-0.15, 0, 0.15): bx(f"flut{x}{f}", (x + f, RH / 2, 13.82), (0.04, RH - 1.6, 0.02), PAN, 0.004)
    for sx in (-1, 1):
        cy(f"col{sx}", (sx * 6.9, RH / 2, 12.9), 0.38, RH - 0.8, MARB, 32)
        cy(f"colb{sx}", (sx * 6.9, 0.2, 12.9), 0.5, 0.4, G2, 32); cy(f"colc{sx}", (sx * 6.9, RH - 0.5, 12.9), 0.5, 0.35, G, 32)
    # ---------------- flags of the Allies: big, folded, on gilt standards ----------------
    for x, kind in ((4.5, "us"), (1.5, "fr"), (-1.5, "uk"), (-4.5, "it")):
        z = 13.25
        cy(f"fpole{x}", (x, 2.05, z), 0.035, 4.1, G, 12); cone(f"ftip{x}", (x, 4.22, z), 0.07, 0.0, 0.25, G, 12)
        sph(f"fball{x}", (x, 4.08, z), 0.06, G); cy(f"fbase{x}", (x, 0.1, z), 0.28, 0.2, G2, 24); cy(f"fbase2{x}", (x, 0.25, z), 0.14, 0.12, G2, 16)
        K.flag(f"flag{x}", (x - 0.03, 4.0, z), 1.55, 1.05, K.img_mat(f"flagm{kind}", K.flag_img(kind), 0.75, sheen=0.5), 0, 0.07, 2.2)
        for t in (0.25, 0.75): cy(f"fcord{x}{t}", (x - 0.05, 3.0 - t * 0.6, z - 0.04), 0.01, 0.5, G2, 6)
    # ---------------- side walls: dado, gilt panels; mirrors on +x, paintings on -x; sconces between ----------------
    MIR = K.metal("pmir", "#c8c4b8", 0.06)
    paints = [K.img_mat(f"ppaint{k}", K.landscape_img(40 + k, house=k % 4 == 0, water=k % 3 == 0) if k % 2 == 0 else K.portrait_img(40 + k), 0.55, coat=0.3) for k in range(7)]
    for sx in (-1, 1):
        bx(f"side{sx}", (sx * 8.15, RH / 2, 4), (0.3, RH, 23), WALL, 0)
        bx(f"dado{sx}", (sx * 7.95, 0.5, 4), (0.1, 1.0, 22), DADO, 0.01); bx(f"dadorail{sx}", (sx * 7.9, 1.02, 4), (0.12, 0.06, 22), G, 0.01)
        bx(f"skirt{sx}", (sx * 7.9, 0.08, 4), (0.14, 0.16, 22), MARB, 0.01)
        for k in range(7):
            z = -4 + k * 3
            for dz in (-1.15, 1.15): bx(f"pnlg{sx}{k}{dz}", (sx * 7.93, 3.6, z + dz), (0.06, 4.6, 0.09), G, 0.01)
            bx(f"pnlt{sx}{k}", (sx * 7.93, 5.95, z), (0.06, 0.09, 2.4), G, 0.01); bx(f"pnlb{sx}{k}", (sx * 7.93, 1.3, z), (0.06, 0.09, 2.4), G, 0.01)
            for dz in (-0.75, 0.75): bx(f"dpn{sx}{k}{dz}", (sx * 7.89, 0.5, z + dz), (0.03, 0.6, 1.2), DADO, 0.02)
            if sx > 0:
                # arched mirror of small panes (Hall of Mirrors)
                bx(f"mir{k}", (7.9, 3.4, z), (0.02, 3.6, 1.7), MIR, 0)
                for j in range(1, 5): bx(f"mirh{k}{j}", (7.88, 1.6 + j * 0.72, z), (0.03, 0.03, 1.7), G, 0.004)
                for dz in (-0.43, 0.43): bx(f"mirv{k}{dz}", (7.88, 3.4, z + dz), (0.03, 3.6, 0.03), G, 0.004)
                for j in range(9):
                    a = math.pi * j / 8; bx(f"marc{k}{j}", (7.88, 5.25 + 0.4 * math.sin(a), z + 0.85 * math.cos(a)), (0.05, 0.1, 0.22), G, 0.01)
            else:
                K.framed(f"paint{k}", (-7.86, 3.5, z), 1.5, 1.9 if k % 2 else 1.2, paints[k], G, -math.pi / 2, 0.14, 0.08)
                bx(f"plight{k}", (-7.7, 4.75 if k % 2 else 4.45, z), (0.12, 0.05, 0.6), BRASS, 0.01)
            # sconce between panels: gilt back plate, three arms, candles, real warm light
            zc = z + 1.5
            if zc < 13:
                bx(f"scp{sx}{k}", (sx * 7.9, 2.6, zc), (0.05, 0.4, 0.18), G, 0.02)
                for dz in (-0.18, 0, 0.18):
                    cy(f"sca{sx}{k}{dz}", (sx * 7.78, 2.68, zc + dz), 0.012, 0.25, G, 6, (0, math.radians(90), 0))
                    cy(f"scc{sx}{k}{dz}", (sx * 7.66, 2.82, zc + dz), 0.017, 0.16, WHITE, 8); cy(f"scf{sx}{k}{dz}", (sx * 7.66, 2.94, zc + dz), 0.011, 0.04, FLAME, 6)
                K.point((sx * 7.6, 3.0, zc), 22, (1.0, 0.68, 0.38), 0.08)
    # front wall (behind the cameras, for bounce)
    bx("front", (0, RH / 2, -7.3), (17, RH, 0.3), WALL, 0)
    # ---------------- the long table ----------------
    bx("ttop", (0, 0.77, 6), (2.3, 0.06, 9.2), BAIZE, 0.02)
    for sx in (-1, 1): bx(f"tedge{sx}", (sx * 1.16, 0.77, 6), (0.03, 0.07, 9.25), G, 0.01)
    for sz in (-1, 1): bx(f"tedgez{sz}", (0, 0.77, 6 + sz * 4.62), (2.35, 0.07, 0.03), G, 0.01)
    bx("tskirt", (0, 0.62, 6), (2.2, 0.24, 9.1), TW, 0.01)
    for sx in (-1, 1): bx(f"tbead{sx}", (sx * 1.11, 0.54, 6), (0.02, 0.03, 9.1), G, 0.005)
    for sx in (-1, 1):
        for z in (1.7, 3.8, 6, 8.2, 10.3):
            cy(f"tleg{sx}{z}", (sx * 1.0, 0.27, z), 0.055, 0.54, TW, 12); cy(f"tlegr{sx}{z}", (sx * 1.0, 0.45, z), 0.07, 0.05, G, 12)
            cy(f"tlegf{sx}{z}", (sx * 1.0, 0.03, z), 0.07, 0.06, G, 12)
    INK = lib.glass("inkg"); BLOT = lib.cloth("blot", "#5a2a1a")
    docs = [K.img_mat(f"pdoc{k}", K.doc_img(k, ["TRAITÉ DE PAIX", "ARTICLE 231", "CONDITIONS", "REPARATIONS"][k], seal=k == 0), 0.8) for k in range(4)]
    for k in range(6):
        z = 2.5 + k * 1.4
        for sx in (-1, 1):
            K.chair(f"ch{k}{sx}", sx * 1.5, z, -sx * math.pi / 2, G2, VEL, 0.48, True, G)
            px = sx * (0.74 if k == 0 else 0.62)
            bx(f"blot{k}{sx}", (px, 0.803, z), (0.42, 0.006, 0.55), BLOT, 0.002)
            for j in range(2):
                K.floor_quad(f"pap{k}{sx}{j}", (px + rs.uniform(-0.05, 0.05), z + rs.uniform(-0.1, 0.1)), 0.22, 0.3, docs[(k + j) % 4], rs.uniform(-0.4, 0.4), 0.808 + j * 0.002)
            cy(f"ink{k}{sx}", (sx * 0.95, 0.83, z + 0.32), 0.045, 0.06, INK, 12); cy(f"inkl{k}{sx}", (sx * 0.95, 0.87, z + 0.32), 0.03, 0.02, BRASS, 12)
            cy(f"pen{k}{sx}", (sx * 0.9, 0.815, z - 0.2), 0.007, 0.2, DARK, 6, (math.radians(90), 0, rs.uniform(-0.6, 0.6)))
            cy(f"glass{k}{sx}", (sx * 0.85, 0.86, z - 0.4), 0.035, 0.12, CRYS, 12)
    # centre of the table: candelabra, carafes, flowers, the treaty stack at the leaders' end
    for z in (3.6, 6.0, 8.6):
        cy(f"cstick{z}", (0, 0.82, z), 0.09, 0.04, G); cy(f"cstem{z}", (0, 0.98, z), 0.025, 0.32, G)
        cy(f"carm{z}", (0, 1.12, z), 0.012, 0.42, G, 8, (0, math.radians(90), 0))
        for dx in (-0.2, 0, 0.2): cy(f"cand{z}{dx}", (dx, 1.22, z), 0.019, 0.18, WHITE, 10); cy(f"fl{z}{dx}", (dx, 1.34, z), 0.012, 0.04, FLAME, 8)
        K.point((0, 1.42, z), 30, (1.0, 0.66, 0.36), 0.05)
    for z in (4.8, 7.4):
        cy(f"caraf{z}", (0.1, 0.92, z), 0.06, 0.22, CRYS, 16); cy(f"cvase{z}", (-0.15, 0.88, z), 0.07, 0.14, K.flat(f"vase{z}", "#2a4a8a", 0.2), 16)
        for j in range(7): sph(f"flw{z}{j}", (-0.15 + rs.uniform(-0.1, 0.1), 1.0 + rs.uniform(0, 0.12), z + rs.uniform(-0.1, 0.1)), 0.04, K.flat(f"flw{j % 3}", ["#e8c8d8", "#c82a3a", "#f2ece0"][j % 3], 0.6), 8)
    RED_B = K.flat("rbind", "#7a1a1a", 0.5); BLU_B = K.flat("bbind", "#1e2a5a", 0.5)
    for j in range(6): bx(f"treaty{j}", (0.2, 0.83 + j * 0.05, 10.0), (0.45, 0.05, 0.6), PAPER if j % 2 else K.flat("tpg", "#e8dcbc", 0.8), 0.003, rs.uniform(-0.1, 0.1))
    bx("treatyrib", (0.2, 0.98, 10.0), (0.05, 0.31, 0.62), RED_B, 0.002)
    K.books("tbk", -0.6, 0.8, 9.9, 5, [RED_B, BLU_B, K.flat("gbind", "#2a4a2a", 0.5)], math.pi / 2)
    cy("bell", (0.6, 0.86, 10.1), 0.06, 0.08, BRASS, 16); sph("bellk", (0.6, 0.92, 10.1), 0.02, BRASS)
    for x, name in ((-0.55, "ITALIA"), (0.55, "BRITISH EMPIRE"), (0.0, "FRANCE")):
        bx(f"plac{x}", (x, 0.86, 10.35), (0.42, 0.11, 0.02), WHITE, 0.003, 0); txt(name, (x, 0.86, 10.33), 0.04, DARK)
    # ---------------- chandeliers: gilt frame, three tiers of candles, crystal drops, real light ----------------
    for z in (2, 7, 12):
        cy(f"chc{z}", (0, 5.9, z), 0.025, 2.2, G, 8); cy(f"chcan{z}", (0, 6.95, z), 0.25, 0.1, G, 20)
        sph(f"chbowl{z}", (0, 4.75, z), 0.22, G); cone(f"chdrop{z}", (0, 4.45, z), 0.12, 0.0, 0.35, CRYS, 16)
        for r, y, n in ((0.95, 4.95, 12), (0.6, 5.4, 8), (0.3, 5.8, 6)):
            torus(f"chr{z}{r}", (0, y, z), r, 0.03, G, maj=40, mi=8)
            for k in range(n):
                a = k / n * math.pi * 2; x, zz = r * math.cos(a), z + r * math.sin(a)
                cy(f"chcd{z}{r}{k}", (x, y + 0.08, zz), 0.018, 0.14, WHITE, 8); cy(f"chf{z}{r}{k}", (x, y + 0.18, zz), 0.012, 0.04, FLAME, 6)
                sph(f"chx{z}{r}{k}", (x * 1.04, y - 0.12, z + (zz - z) * 1.04), 0.025, CRYS, 8)
        K.point((0, 5.25, z), 300, (1.0, 0.7, 0.42), 0.7)
    # ---------------- room dressing: palms, busts, torcheres, rope line, a press camera ----------------
    POT = K.flat("potc", "#2a4a6a", 0.25); PALM = K.flat("palm", "#2f6a2a", 0.5)
    for x, z in ((-7.2, 12.4), (7.2, 12.4), (-7.2, -5.2)):
        cy(f"pot{x}{z}", (x, 0.3, z), 0.3, 0.6, POT, 20); cy(f"potr{x}{z}", (x, 0.6, z), 0.33, 0.05, G, 20)
        for j in range(9):
            a = j / 9 * math.pi * 2
            o = K.bl(f"palm{x}{z}{j}", (x + 0.45 * math.cos(a), 1.5 + rs.uniform(-0.2, 0.3), z + 0.45 * math.sin(a)), (0.55, 0.06, 0.16), PALM, 0.02)
            o.rotation_euler = (0, 0.4, -a)
        cy(f"palmt{x}{z}", (x, 1.0, z), 0.04, 0.9, K.flat("palmt", "#5a4020", 0.8), 8)
    for x, z in ((-7.2, 9.0), (-7.2, 3.0), (7.2, 9.0), (7.2, 3.0)):
        cy(f"ped{x}{z}", (x, 0.6, z), 0.22, 1.2, MARB, 20); cy(f"pedt{x}{z}", (x, 1.22, z), 0.28, 0.06, G2, 20)
        K.bl(f"bust{x}{z}", (x, 1.55, z), (0.16, 0.22, 0.14), MARB, 0.02); K.bl(f"bustb{x}{z}", (x, 1.32, z), (0.24, 0.12, 0.16), MARB, 0.02)
    for sx in (-1, 1):
        for z in (0.5, 5.5, 10.5):
            x = sx * 7.3; cy(f"tor{sx}{z}", (x, 0.9, z), 0.04, 1.8, G2, 8); cy(f"torb{sx}{z}", (x, 0.05, z), 0.2, 0.1, G2, 16)
            for dx in (-0.12, 0.12):
                cy(f"torc{sx}{z}{dx}", (x + dx, 1.9, z), 0.02, 0.2, WHITE, 8); cy(f"torf{sx}{z}{dx}", (x + dx, 2.03, z), 0.012, 0.04, FLAME, 6)
            K.point((x, 2.1, z), 18, (1.0, 0.66, 0.36), 0.05)
    ROPE = K.velvet("rope", "#a8182a")
    for sx in (-1, 1):
        for k in range(4):
            z = -3.0 + k * 1.3; x = sx * 2.0
            cy(f"stan{sx}{k}", (x, 0.45, z), 0.025, 0.9, BRASS, 10); cy(f"stanb{sx}{k}", (x, 0.02, z), 0.12, 0.04, BRASS, 16); sph(f"stank{sx}{k}", (x, 0.92, z), 0.04, BRASS, 10)
            if k < 3:
                for j in range(6):
                    t = (j + 0.5) / 6; sag = 0.18 * math.sin(math.pi * t); slope = math.atan(0.18 * math.pi * math.cos(math.pi * t) / 1.3)
                    cy(f"rope{sx}{k}{j}", (x, 0.86 - sag, z + 1.3 * t), 0.018, 0.25, ROPE, 8, (math.radians(90) - slope, 0, 0))
    x, z = -5.6, 9.8
    for a in (0, 2.1, 4.2): cy(f"trip{a}", (x + 0.18 * math.cos(a), 0.7, z + 0.18 * math.sin(a)), 0.015, 1.45, TW, 6, (0.12 * math.sin(a), 0.12 * math.cos(a), 0))
    bx("pcam", (x, 1.45, z), (0.3, 0.3, 0.38), DARK, 0.02, 0.5); cy("plens", (x + 0.15, 1.45, z - 0.2), 0.06, 0.12, BRASS, 12, (math.radians(90), 0, 0))
    bx("pcamcl", (x - 0.1, 1.38, z + 0.2), (0.4, 0.42, 0.25), lib.cloth("camcloth", "#151214"), 0.04, 0.5)
    # ---------------- the German delegate's corner: plain, cramped, a little sad ----------------
    PINE = K.grain("pine", "#a8804a", "#6a4a22", "X", 1.2, 0.6)
    bx("cstool", (6.6, 0.45, -2.5), (0.42, 0.05, 0.42), PINE, 0.01, -0.7)
    for dx in (-0.16, 0.16):
        for dz in (-0.16, 0.16): bx(f"cstl{dx}{dz}", (6.6 + dx, 0.22, -2.5 + dz), (0.04, 0.44, 0.04), PINE, 0)
    bx("ctab", (7.3, 0.74, -1.2), (0.7, 0.04, 0.7), PINE, 0.01); bx("ctabl", (7.3, 0.37, -1.2), (0.08, 0.74, 0.08), PINE, 0); bx("ctabf", (7.3, 0.02, -1.2), (0.4, 0.04, 0.4), PINE, 0.01)
    cy("cwater", (7.15, 0.82, -1.35), 0.04, 0.12, CRYS, 12); cy("cjug", (7.45, 0.86, -1.05), 0.07, 0.2, K.flat("jug", "#e8e2d2", 0.3), 16)
    K.floor_quad("cdoc", (7.3, -1.2), 0.24, 0.32, docs[3], 0.3, 0.765)
    bx("cplac", (7.2, 0.8, -1.5), (0.36, 0.1, 0.02), WHITE, 0.003, 0); txt("ALLEMAGNE", (7.2, 0.8, -1.52), 0.035, DARK)
    cy("hatb", (7.42, 0.77, -0.98), 0.14, 0.012, DARK, 20); cy("hatc", (7.42, 0.83, -0.98), 0.085, 0.11, DARK, 20)
    IRON = M["iron"]
    for j in range(12): bx(f"rad{j}", (7.8, 0.42, -3.4 + j * 0.08), (0.14, 0.6, 0.05), IRON, 0.015)
    cy("cstand", (7.4, 0.9, 0.3), 0.025, 1.8, PINE, 8); cy("cstandb", (7.4, 0.03, 0.3), 0.22, 0.06, PINE, 12)
    for a in (0, 2.1, 4.2): cy(f"chook{a}", (7.4 + 0.1 * math.cos(a), 1.75, 0.3 + 0.1 * math.sin(a)), 0.012, 0.2, BRASS, 6, (0.6 * math.sin(a), -0.6 * math.cos(a), 0))
    K.bl("coat", (7.43, 1.35, 0.32), (0.18, 0.45, 0.12), lib.cloth("coat", "#3a3a40"), 0.04)
    cy("umb", (7.2, 0.45, 0.45), 0.03, 0.9, DARK, 8, (0.15, 0, 0))
    cy("clock", (7.92, 4.1, -2.5), 0.32, 0.05, WHITE, 32, (0, math.radians(90), 0)); torus("clockr", (7.9, 4.1, -2.5), 0.33, 0.03, G, (0, math.radians(90), 0))
    for a, ln in ((math.radians(60), 0.18), (math.radians(-80), 0.24)):
        bx(f"hand{ln}", (7.88, 4.1 + ln / 2 * math.cos(a), -2.5 - ln / 2 * math.sin(a)), (0.01, ln, 0.02), DARK, 0).rotation_euler[0] = a
    bx("plaque", (7.92, 2.1, -1.2), (0.03, 0.22, 0.6), BRASS, 0.01); txt("DÉLÉGATION ALLEMANDE", (7.9, 2.1, -1.2), 0.035, DARK, math.radians(90))
    K.point((7.2, 2.6, -2.0), 25, (0.75, 0.82, 1.0), 0.3)   # a cold little light on him
    # ---------------- fill: warm bounce from the camera end, soft side fill ----------------
    K.area((0, 4.5, -6.6), (0, 1.5, 4), 550, (1.0, 0.82, 0.62), 7, 3)
    K.area((-6, 5.5, 2), (2, 0.5, 6), 250, (1.0, 0.86, 0.7), 3)
    # the bill (shot 12): a long paper strip with ruled lines, scaled per frame
    me = bpy.data.meshes.new("bill"); me.from_pydata([T(-0.45, 0.02, 0), T(0.45, 0.02, 0), T(0.45, 0.02, -1), T(-0.45, 0.02, -1)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for k, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = c
    SCROLL = bpy.data.objects.new("bill", me); bpy.context.collection.objects.link(SCROLL)
    bm = lib.principled("billm", lib.hexc("#f2ecdc"), 0.8); t, n, l = lib.nodes(bm)
    tc = n.new("ShaderNodeTexCoord"); wv = n.new("ShaderNodeTexWave"); wv.bands_direction = "Y"; wv.inputs["Scale"].default_value = 1.0
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 40, 1); l.new(tc.outputs["UV"], mp.inputs[0]); l.new(mp.outputs[0], wv.inputs["Vector"])
    r = lib.ramp(n, l, wv.outputs["Fac"], [(0.0, lib.hexc("#6a6458")), (0.12, lib.hexc("#f2ecdc"))]); l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
    me.materials.append(bm); SCROLL.location = T(0, 0, 1.3)
    sm = lambda u: (lambda x: x * x * (3 - 2 * x))(max(0.0, min(1.0, u)))
    def update(f):
        on = D["id"] == 12
        SCROLL.hide_render = not on
        if on:
            ln = 0.02 + 24 * sm((f - 1294) / 100); SCROLL.scale = (1, ln, 1)
            mp.inputs["Scale"].default_value = (1, 40 * ln / 1.5, 1)
    return {"update": update}
