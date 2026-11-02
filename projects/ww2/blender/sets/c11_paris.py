# Paris liberated, August 1944 (chapter 11). A Haussmann boulevard (the Champs-Elysees) running along z with the Arc de
# Triomphe closing it at z 210 and the Eiffel tower over the roofs at (-150, 0, 330).
#  - The road x -11..11 (y 0), the sidewalks |x| 11..17 (y 0.15) with plane trees at |x| 12.5 every 10 m (z -20..190),
#    Haussmann blocks with facades at |x| 18 (six floors + mansard, balconies, flags), a cafe with a red awning on the
#    left at z 14..24, a Morris column at (13.5, 0.15, 6).
#  - Keep clear: the road |x| < 10.5 for z -10..120 (the tank, de Gaulle, cheering crowds); sidewalks are for crowds.
#  - The French Sherman at (2.5, 0, 34) facing the camera (-z).
# Light: bright summer day, sun from the right/back, warm bounce; flags everywhere.
import bpy, math, random
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, gold, glassm
from sets import ikit as IK

def build(M, D):
    rnd = random.Random(1825); C.SB.reset()
    sd = (-0.55, 0.62, 0.55); C.sky("day", sd, 0.9); C.sun(sd, 4.4, (1.0, 0.94, 0.82), 2.0)
    K = Kit("paris"); TM = C.tree_mats("summer")
    stone = C.SB.grime("pa_stone", "#e4d6b8", 0.25, 3.0); trim = pm("#efe4cc", 0.6); zinc = C.SB.stripes("pa_zinc", "#6a7480", "#5a6470", 6, 2)
    road = C.SB.wet_cobbles("pa_road", "#8a8680", "#6a6662", 0.1, 3.0)
    C.ground("pa_g", -240, 240, -60, 420, 4.0, lambda x, z: 0.0, C.grass_mat("pa_grass", "#5a7a34", "#7a8a3a", "#a89a58"))
    K.box((0, 0.01, 80), (22, 0.02, 280), road, 0, 0)
    for s in (-1, 1):
        K.box((s * 14, 0.075, 80), (6, 0.15, 280), C.concrete("pa_walk", "#b8b0a0"), 0, 0.01)
        K.box((s * 11.05, 0.08, 80), (0.3, 0.16, 280), C.concrete("pa_kerb", "#9a948a"), 0, 0)
    win = C.SB.window_glow("paw", "#ffd090", 1.0)
    flags = ["fr", "fr", "fr", "us", "uk", "fr"]
    for side in (-1, 1):
        z = -30.0; k = 0
        while z < 200:
            w = rnd.uniform(16, 22)
            C.house(K, side * 25, z + w / 2, w, 14, 6, side * math.pi / 2, stone, trim, zinc, win, rnd, 3.3, roof="mansard", shutters=None, balcony="all",
                    base=C.concrete("pa_base", "#c8bca0"), lit=0.05)
            for j in range(int(w / 3.4)):
                if rnd.random() < 0.55: C.banner(f"pab{side}{k}{j}", (side * 17.3, 7.3 + 3.3 * rnd.randint(0, 2), z + 1.8 + j * 3.4), 1.1, 1.6, rnd.choice(flags), side * math.pi / 2)
            z += w + 0.4; k += 1
    # plane trees, lamp posts, benches
    for z in range(-20, 195, 10):
        for s in (-1, 1):
            C.leafy(K, s * 12.6, 0.15, z + 2, rnd.uniform(9, 12), rnd, TM)
            K.cyl((s * 11.6, 2.2, z + 6), 0.08, 4.4, iron("#2a2e2a"), 8)
            K.cyl((s * 11.6, 4.5, z + 6), 0.22, 0.45, glassm(), 12, "y", 0.12); K.cyl((s * 11.6, 4.78, z + 6), 0.26, 0.12, iron("#2a2e2a"), 12, "y", 0.05)
    # the cafe: red awning, chairs and little tables, a sign
    awn = C.SB.stripes("pa_awn", "#b8202c", "#f0e8d8", 6.0, 1)
    K.box((-16.4, 3.4, 19), (3.0, 0.06, 10), awn, 0, 0.01, 0, -0.35)
    sign(K, (-17.85, 4.4, 19), 6.0, 0.6, -math.pi / 2, "CAFÉ DE LA PAIX", board="#1e3a2a", ink=C.gold(), kind="serif")
    for k in range(6):
        x, z = -15.5 + (k % 2) * 1.6, 15 + (k // 2) * 3
        K.cyl((x, 0.88, z), 0.32, 0.03, pm("#d8d4c8", 0.3, 0.4), 16); K.cyl((x, 0.5, z), 0.03, 0.72, iron("#2a2a2a"), 6)
        for a in (0.5, 3.6): K.box((x + 0.55 * math.cos(a), 0.6, z + 0.55 * math.sin(a)), (0.4, 0.05, 0.4), C.SB.wood("#7a5a3a", "#4a3020", 8), a, 0.01)
        K.cyl((x + 0.1, 0.95, z), 0.03, 0.1, glassm(), 8)
    # the Morris column with posters
    K.cyl((13.5, 1.9, 6), 0.75, 3.5, pm("#2e4a3a", 0.5), 24); K.cyl((13.5, 3.75, 6), 0.85, 0.3, pm("#2e4a3a", 0.5), 24); K.cyl((13.5, 4.2, 6), 0.5, 0.7, pm("#2e4a3a", 0.5), 16, "y", 0.1)
    for k in range(6):
        a = k / 6 * math.tau
        po = C.poster_img([(["VIVE", "PARIS", "LIBRE", "VIVE DE", "VICTOIRE", "AUX"][k], 0.16, "#2a3a8a"), (["LA FRANCE", "LIBÉRÉ", "!", "GAULLE", "1944", "ARMES"][k], 0.13, "#b8202c")], "#f0e8d4", "#1e1e1e", 120, 170, seed=30 + k)
        IK.panel(f"pa_mp{k}", (13.5 - 0.77 * math.sin(a), 2.0, 6 - 0.77 * math.cos(a)), 0.55, 0.8, IK.img_mat(f"pa_mpm{k}", po, 0.8), a)
    # the Arc de Triomphe at the end
    arc = C.SB.grime("pa_arc", "#e8dcc0", 0.2, 2.0)
    for s in (-1, 1): K.box((s * 15, 15, 215), (12, 30, 22), arc, 0, 0.1)
    K.box((0, 38, 215), (42, 16, 22), arc, 0, 0.1); K.box((0, 47, 215), (44, 2, 23), arc, 0, 0.05)
    for k in range(13):
        a = math.pi * k / 12; K.box((9 * math.cos(a), 30 + 9 * math.sin(a), 204), (2.0, 1.4, 1.0), arc, 0, 0.05, 0, a + math.pi / 2)
    for s in (-1, 1):
        for k in range(3): K.box((s * 15, 8 + k * 7, 203.8), (9, 0.4, 0.4), arc, 0, 0.02)
    C.flagpole("pa_arcflag", 0, 0.0, 214, 30, "fr", 0.0, 9, 6, 0.4)
    # the Eiffel tower over the roofs
    ir = iron("#6a4e3a")
    ex, ez = -150.0, 330.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            for k in range(14):
                f0 = k / 14; f1 = (k + 1) / 14
                y0, y1 = f0 * 120, f1 * 120
                r0 = 30 * (1 - f0) ** 2.2 + 3; r1 = 30 * (1 - f1) ** 2.2 + 3
                K.box((ex + sx * (r0 + r1) / 2, (y0 + y1) / 2, ez + sz * (r0 + r1) / 2), (2.2, y1 - y0 + 0.5, 2.2), ir, 0, 0.0, -sz * math.atan((r0 - r1) / (y1 - y0)), sx * math.atan((r0 - r1) / (y1 - y0)))
    for y, r in ((57, 16), (115, 5.5)): K.box((ex, y, ez), (2 * r + 6, 3, 2 * r + 6), ir, 0, 0.1)
    K.cyl((ex, 140, ez), 2.2, 50, ir, 8, "y", 0.4); K.cyl((ex, 170, ez), 0.3, 12, ir, 6)
    for s in (-1, 1): K.torus((ex, 20, ez + s * 28), 18, 0.8, ir, 24, 4, "z", 0, 0, 0, (1, 1, 1), math.pi)
    # the French Sherman (2e DB): star painted out, a tricolour roundel, a name on the hull, flowers, flags
    objs = C.tank_at("fr_tank", 2.5, 0, 34, math.pi / 2, "#58603c", None)
    for k, c in enumerate(("#1f3f8f", "#f4f1ea", "#d2232e")): K.cyl((1.31 - k * 0.004, 1.1, 34.6), 0.32 - k * 0.1, 0.02, pm(c, 0.6), 20, "x")
    text("PARIS", (1.28, 1.1, 33.3), 0.22, pm("#e8e4d8", 0.7), math.pi / 2, "sans", 0.002)
    for k in range(10): K.sphere((2.5 + rnd.uniform(-1.0, 1.0), 1.65 + rnd.uniform(0, 0.2), 34 - 2.2 + rnd.uniform(-0.4, 0.4)), 0.08, pm(["#e8c040", "#c82a3a", "#f0f0f0", "#e86aa8"][k % 4], 0.5), 8)
    C.flagpole("pa_tf", 3.5, 2.6, 35, 1.6, "fr", 0.4, 0.8, 0.55, 0.06)
    C.fill((0, 14, -30), (0, 1, 30), 9000, (1.0, 0.92, 0.82), 30)
    C.fill((0, 20, 120), (0, 1, 60), 6000, (0.8, 0.88, 1.0), 40)
    K.build()
    return {}
