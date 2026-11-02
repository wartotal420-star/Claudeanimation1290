# Rome, Piazza Venezia (chapter 2 shots 18-19): the palazzo facade along x at z 0 (faces -z), 40 m wide, 21 m to the
# crenellations; Mussolini's balcony at the centre: slab top y 4.6, front edge z -1.3, x -1.6..1.6 (he stands at
# (0, 4.6, -0.45)). The piazza (y 0) spreads toward -z: crowd at z -3..-16, |x| < 12; lamp posts, a fountain at
# (-11, 0, -12), the white Vittoriano colonnade at x 26..60 (seen when the camera turns right), parked cars, flags and
# tricolour drapes on the facade. Sun: high Roman afternoon from the -z/-x side, warm; blue sky fill.
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, flat_text, sign, poster, R90, cached, set_world
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets import ikit as IK

def build(M, D):
    random.seed(1935); KS.reset(); rnd = random.Random(1935)
    K = Kit("rome")
    set_world((0.25, 0.45, 0.85), (0.78, 0.84, 0.92), 1.0, (0.22, 0.42, 0.85), (0.8, 0.86, 0.94))
    ST = grime("rstone", "#c89a6a", 0.35, 3.0); ST2 = grime("rstone2", "#b8865a", 0.4, 3.0); TRV = grime("rtrav", "#e8dcc4", 0.25, 2.0)
    BRK = KS.brick("rbrick", "#b07050", "#985e42", "#6a4a3a", 3.0)
    COB = lib.cobbles("rcob", "#8a8078", "#6a625a"); MARB = lib.marble("rmarble"); IR = iron("#1e1e22")
    FLAG = IK.img_mat("rflag", IK.flag_img("it"), 0.7, sheen=0.4)
    # piazza
    K.box((0, -0.05, -20), (120, 0.1, 50), COB, 0, 0)
    K.box((0, 0.08, -0.9), (44, 0.16, 1.8), TRV, 0, 0.02)
    # facade: brick body with travertine quoins, three storeys of windows, crenellated cornice
    K.box((0, 10.5, 1.0), (40, 21, 2.0), BRK, 0, 0.02)
    for sx in (-1, 1): K.box((sx * 19.6, 10.5, -0.05), (0.9, 21, 0.2), TRV, 0, 0.02)
    for k in range(19):
        for sx in (-1, 1): K.box((sx * 19.6, 0.4 + k * 1.05, -0.15), (1.3 if k % 2 else 0.9, 0.5, 0.15), TRV, 0, 0.02)
    K.box((0, 1.5, -0.05), (40, 3.0, 0.15), ST2, 0, 0.02)
    for row, (y, h, w) in enumerate(((2.0, 1.6, 1.0), (6.2, 3.0, 1.6), (12.0, 2.4, 1.3), (16.8, 1.4, 0.9))):
        for k in range(9):
            x = -16 + k * 4
            if row == 1 and k == 4: continue
            K.box((x, y + h / 2, -0.06), (w, h, 0.1), pm("#1e2228", 0.15, 0.3), 0, 0.0)
            KS._frame(K, (x, y + h / 2, -0.12), w + 0.1, h + 0.1, 0, TRV, 0.18, 0.12)
            if row == 1:
                K.box((x, y + h + 0.5, -0.2), (w + 0.6, 0.18, 0.35), TRV, 0, 0.02)
                K.box((x, y - 0.25, -0.25), (w + 0.5, 0.12, 0.5), TRV, 0, 0.02)
                K.box((x, y + h / 2, -0.13), (0.06, h, 0.04), TRV, 0, 0.0)
                for j in range(1, 4): K.box((x, y + j * h / 4, -0.13), (w, 0.04, 0.04), TRV, 0, 0.0)
            for sd in (-1, 1):
                if row in (1, 2): K.box((x + sd * (w / 2 + 0.35), y + h / 2, -0.2), (0.5, h, 0.08), pm("#3a5a3a", 0.6), 0, 0.01, sd * 0.4)
    K.box((0, 9.9, -0.25), (40, 0.25, 0.5), TRV, 0, 0.02); K.box((0, 19.6, -0.3), (41, 0.5, 0.6), TRV, 0, 0.03)
    for k in range(27):
        x = -19.5 + k * 1.5; K.box((x, 20.5, 0.2), (0.9, 1.3, 1.0), BRK, 0, 0.02); K.box((x, 21.2, 0.2), (1.0, 0.12, 1.1), TRV, 0, 0.02)
    # the balcony: door, carved surround, slab, balustrade, a draped tricolour, two microphones
    K.box((0, 6.3, -0.06), (1.8, 3.4, 0.1), pm("#1e1a18", 0.4), 0, 0)
    KS._frame(K, (0, 6.3, -0.18), 2.0, 3.6, 0, TRV, 0.3, 0.2)
    K.box((0, 8.6, -0.35), (3.2, 0.5, 0.6), TRV, 0, 0.03); K.box((0, 9.0, -0.3), (2.6, 0.35, 0.4), ST, 0, 0.02)
    K.box((0, 4.5, -0.65), (3.6, 0.22, 1.3), TRV, 0, 0.03)
    for k in range(3): K.box((-1.2 + k * 1.2, 3.9, -1.0), (0.3, 1.0, 0.4), TRV, 0, 0.03, 0, 0)
    K.box((0, 5.6, -1.25), (3.6, 0.12, 0.22), TRV, 0, 0.02)
    for sd in (-1, 1): K.box((sd * 1.75, 5.6, -0.75), (0.22, 0.12, 1.1), TRV, 0, 0.02)
    for k in range(13):
        x = -1.65 + k * 0.275
        CK.lathe(f"bal{k}", [(0.0, 0.0), (0.07, 0.0), (0.06, 0.1), (0.04, 0.2), (0.075, 0.45), (0.04, 0.75), (0.07, 0.85), (0.0, 0.86)], (x, 4.7, -1.25), TRV, 12)
    IK.drape("rdrape", (0, 4.42, -1.36), 3.4, 1.5, FLAG, 0, 3, 0.04)
    for sd in (-1, 1):
        K.cyl((sd * 0.6, 5.0, -1.0), 0.012, 1.2, IR, 6); K.cyl((sd * 0.6, 5.65, -1.05), 0.05, 0.14, pm("#c8c8c8", 0.2, 0.9), 10, "z")
    # tricolour drapes hanging from the upper floor, flagpoles on the roof
    for x in (-12, -4, 4, 12):
        IK.drape(f"rd{x}", (x, 15.6, -0.35), 2.2, 6.0, FLAG, 0, 3, 0.05)
    for x in (-8, 8): CK.flagpole(K, (x, 21.8, 0.2), 5, FLAG, 2.4, 1.6, pm("#d8d4c8", 0.4, 0.5))
    # piazza dressing: lamp posts, fountain, parked cars, a newsstand, cafe tables, the Vittoriano to the right
    for k, (x, z) in enumerate(((-7, -4), (7, -4), (-14, -9), (14, -9), (-7, -18), (7, -18))):
        K.cyl((x, 2.2, z), 0.09, 4.4, IR, 10); K.cyl((x, 0.2, z), 0.25, 0.4, IR, 12)
        for sd in (-1, 1): K.cyl((x + sd * 0.45, 4.2, z), 0.02, 0.9, IR, 6, "x"); K.cyl((x + sd * 0.85, 4.05, z), 0.17, 0.4, pm("#f2ead0", 0.2), 12, "y", 0.1)
    K.cyl((-11, 0.4, -12), 3.2, 0.8, MARB, 32); K.cyl((-11, 0.75, -12), 2.9, 0.1, pm("#4a7a8a", 0.05, 0.2), 32)
    K.cyl((-11, 1.6, -12), 0.5, 2.0, MARB, 16); K.cyl((-11, 2.7, -12), 1.2, 0.25, MARB, 24); K.cyl((-11, 3.5, -12), 0.25, 1.4, MARB, 12)
    for k, (x, z, yaw, col) in enumerate(((15, -2.5, 0.0, "#1e1e22"), (-16, -3.0, 0.1, "#3a1e1e"), (17, -14, R90, "#1e2a3a"))):
        c = CK.X(x, 0, z, yaw)
        c.box(K, (0, 0.75, 0), (4.4, 0.7, 1.75), pm(col, 0.25, 0.4), 0.15); c.box(K, (-0.4, 1.4, 0), (2.2, 0.65, 1.6), pm(col, 0.25, 0.4), 0.15)
        c.box(K, (0.75, 1.4, 0), (0.05, 0.5, 1.5), pm("#2a3440", 0.06, 0.4), 0.01)
        for sd in (-1, 1):
            for xx in (1.4, -1.4): CK.wheel(K, c, (xx, 0.4, sd * 0.88), 0.4, 0.22, pm("#141414", 0.8), pm("#c8c8c8", 0.2, 0.9))
            c.cyl(K, (2.2, 0.95, sd * 0.6), 0.14, 0.1, pm("#e8e4d8", 0.1, 0.9), 12, "x")
    K.box((-17, 1.2, -7), (2.0, 2.4, 1.4), pm("#2a4a2a", 0.5), 0.3, 0.03)
    poster(K, (-17.25, 1.4, -7.72), 0.7, 1.0, 0.3, "#e8c84a", [("IL POPOLO", 0.12), ("D'ITALIA", 0.1), ("EDIZIONE", 0.06)], "#1a1a1a")
    poster(K, (-16.7, 1.4, -7.55), 0.6, 0.9, 0.3, "#c8202a", [("CINZANO", 0.14), ("VERMOUTH", 0.08)], "#f4ecd8")
    for k in range(4):
        x = 12 + (k % 2) * 1.6; z = -7 - (k // 2) * 1.6
        K.cyl((x, 0.72, z), 0.35, 0.04, MARB, 16); K.cyl((x, 0.36, z), 0.03, 0.72, IR, 6)
        K.cyl((x, 2.3, z), 0.03, 2.2, wood("#d8c8a8", "#a89878", 10), 6); K.cyl((x, 2.1, z), 1.1, 0.3, cloth("#e8e0d0" if k % 2 else "#c8402a"), 12, "y", 0.05)
    for k in range(12):
        x = 30 + k * 2.6; K.cyl((x, 9, -18), 0.6, 18, TRV, 16); K.box((x, 18.4, -18), (1.8, 0.8, 1.8), TRV, 0, 0.03)
    K.box((44, 20, -18), (34, 3.0, 3.0), TRV, 0, 0.05); K.box((44, 2, -14), (36, 4, 12), TRV, 0, 0.05)
    for k in range(6): K.box((44, 0.2 + k * 0.35, -20 + k * 0.6), (36, 0.35, 0.6), TRV, 0, 0.01)
    # sun + sky fill
    IK.sun((0.45, -0.75, 0.5), 3.0, (1.0, 0.9, 0.75), 1.5)
    lib.light("AREA", T(0, 8, -14), 1500, (0.95, 0.9, 1.0), 12).rotation_euler = (math.radians(-80), 0, math.pi)
    K.build()
    return {}
