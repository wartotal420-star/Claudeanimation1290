# Chapter 8: the American war factory (Willow Run style), 1943. A vast steel-truss hall: two lines of B-24 Liberators in
# bare aluminium moving down the floor (front stage fuselages on jigs, rear finished planes with wings), overhead cranes,
# yellow walkways, banners, a giant clock over the hangar doors at the end; in the foreground bay a tank line (Sherman-
# like M4s being finished) and a row of new jeeps; work stands, rivet guns, crates, sparks.
# Layout (three coords): hall floor y 0, x -40..40, z -20..260, roof trusses at y 20..26. The B-24 line runs along z at
# x -14 (finished, wings on) and x 14 (fuselages on jigs); the line creeps +z (update). The tank line at x -4..4, z -10..20
# (tanks at z -6, 6, 18, nose -z); jeeps in a row at x 24..36, z -6..16. The big doors at z 255 with the clock above
# (centre (0, 17, 254)). Rosie's stand: a B-24 fuselage section at (8, 0, 30) with a work platform (top y 1.2) on its near
# side at z 26..27 (riveters stand there); keep x 4..12, z 24..28 clear.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, crate, barrel, stripes, R90
from .c05_kit import (b24, clone, pose, show, area, point, spot, sun_light, lattice_mast, lathe, tube, worn, mat_once, cached, empty, jeep, t34, panzer, loft_k, alu)

def m4(K, c, yaw, col="#4a5232"):
    """M4 Sherman-like: tall hull with sloped front, cast turret, 75 mm gun, white star (US)"""
    P = panzer("m4", c, yaw, col, False, K)
    for sd in (-1, 1):
        cc = P(-0.4, 1.8, sd * 1.47)
        K.cyl(cc, 0.42, 0.01, pm("#f0ece0", 0.6), 5, "z", None, yaw)
    return P

def build(M, D):
    random.seed(1943); K_.reset(); rnd = random.Random(43); sid = D.get("id", 0)
    bg = bpy.context.scene.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.05, 0.06, 0.08, 1); bg.inputs[1].default_value = 1.0
    K = Kit("fac"); CONC = grime("fcconc", "#9a968c", 0.25); STEEL = mat_once("fcsteel", lambda: worn("fcsteel", "#6a7078", "#3a3a3a", 0.5, 0.6, 3, 0.72, "#4a4e54"))
    YEL = pm("#e0b020", 0.5); DARK = pm("#2a2c30", 0.6)
    K.box((0, -0.05, 120), (84, 0.1, 290), CONC, 0, 0)
    for k in range(30): K.box((0, 0.002, -15 + k * 10), (84, 0.004, 0.08), pm("#6a665e", 0.6), 0, 0.0)          # floor joints
    for x in (-24, -4.5, 4.5, 24): K.box((x, 0.004, 120), (0.15, 0.006, 290), YEL, 0, 0.0)                          # painted aisles
    for sx in (-1, 1):
        K.box((sx * 42, 12, 120), (0.4, 24, 290), K_.brick("fcbrick", "#7a4a36", "#6a3e2e", "#4a3a34", 2.5), 0, 0.0)
        for k in range(28):                                                                                         # windows high in the walls
            K.box((sx * 41.75, 15, -12 + k * 10), (0.1, 6, 7), em("#c8d8f0", 1.6), 0, 0.0)
            for j in range(4): K.box((sx * 41.7, 12.1 + j * 1.9, -12 + k * 10), (0.12, 0.1, 7), DARK, 0, 0.0)
    K.box((0, 25, 120), (84, 0.3, 290), pm("#3a3c40", 0.8), 0, 0.0)
    for k in range(29):                                                                                             # roof trusses + columns
        z = -15 + k * 10
        K.box((0, 20, z), (84, 0.5, 0.35), STEEL, 0, 0.02); K.box((0, 24.5, z), (84, 0.4, 0.35), STEEL, 0, 0.02)
        for j in range(12): K.box((-38 + j * 7, 22.2, z), (0.25, 4.6, 0.25), STEEL, 0, 0.0, 0, (0.6 if j % 2 else -0.6))
        for x in (-30, -2, 2, 30): K.box((x, 10, z), (0.5, 20, 0.5), STEEL, 0, 0.02)
        for x in (-20, 0, 20):
            K.cyl((x, 19.2, z + 5), 0.02, 1.6, DARK, 6); K.cyl((x, 18.3, z + 5), 0.6, 0.35, pm("#3a4a3a", 0.4, 0.4), 16, "y", 0.12)
            K.sphere((x, 18.15, z + 5), 0.14, em("#fff0d0", 25.0), 8)
    for x in (-14, 14):                                                                                             # overhead crane runways + bridges
        for sd in (-1, 1): K.box((x + sd * 6, 17.5, 120), (0.6, 0.8, 290), YEL, 0, 0.02)
        for k in range(4):
            z = 20 + k * 60; K.box((x, 17.8, z), (12.5, 0.9, 1.0), YEL, 0, 0.02); K.box((x, 17.0, z), (1.2, 0.8, 1.4), DARK, 0, 0.02)
            K.cyl((x, 13.5, z), 0.02, 6.2, DARK, 6); K.box((x, 10.4, z), (0.4, 0.5, 0.3), YEL, 0, 0.02)
    # the end wall: hangar doors, the big clock, banners and the tally board
    K.box((0, 12, 256), (84, 24, 0.5), K_.brick("fcbrick2", "#7a4a36", "#6a3e2e", "#4a3a34", 2.5), 0, 0.0)
    K.box((0, 6.5, 255.6), (40, 13, 0.3), pm("#5a6a5a", 0.5, 0.4), 0, 0.02)
    for k in range(8): K.box((-17.5 + k * 5, 6.5, 255.4), (0.12, 13, 0.1), DARK, 0, 0.0)
    K.cyl((0, 17.5, 255.5), 3.0, 0.4, DARK, 40, "z"); K.cyl((0, 17.5, 255.25), 2.7, 0.06, pm("#f2ece0", 0.4), 40, "z")
    for k in range(12):
        a = k / 12 * math.tau; K.box((2.3 * math.sin(a), 17.5 + 2.3 * math.cos(a), 255.2), (0.12, 0.45, 0.04), DARK, 0, 0.0, 0, -a)
    CH = empty("clockhands"); hk = Kit("hands"); hk.box((0, 0.8, 0), (0.18, 1.6, 0.04), DARK, 0, 0.0); hk.build()[0].parent = CH
    MH = empty("minhand"); mk = Kit("mhand"); mk.box((0, 1.1, 0), (0.12, 2.2, 0.04), pm("#a81e22", 0.5), 0, 0.0); mk.build()[0].parent = MH
    sign(K, (0, 21.6, 255.4), 30, 1.8, math.pi, "ARSENAL OF DEMOCRACY", "#1e2a5a", pm("#f0e8d0", 0.5), "sans", None, 0.1)
    for k, (x, txt, colr) in enumerate(((-26, "MORE PLANES!", "#c81e22"), (26, "BUY WAR BONDS", "#1e2a5a"))):
        K.box((x, 15, 255.3), (14, 3.2, 0.1), pm(colr, 0.6), 0, 0.02)
        text(txt, (x, 15, 255.2), 1.4, pm("#f4ecd8", 0.5), math.pi, "sans", 0.01, fit=13)
    K.box((-28, 7, 255.3), (10, 5, 0.1), pm("#1a1a1a", 0.7), 0, 0.02)
    text("SHIP No. 1,742", (-28, 8.2, 255.2), 0.8, pm("#f0e8d0", 0.6), math.pi, "sans", 0.004, fit=9)
    text("ONE EVERY HOUR", (-28, 6.6, 255.2), 0.75, pm("#e8c030", 0.6), math.pi, "sans", 0.004, fit=9)
    # banners hung from the trusses down the hall
    for k, (txt, bgc) in enumerate((("ATTACK ATTACK ATTACK", "#c81e22"), ("KEEP 'EM FLYING", "#1e2a5a"), ("EVERY RIVET COUNTS", "#3a6a3a"), ("WORK TO WIN", "#c81e22"))):
        z = 40 + k * 50; K.box((0, 16.5, z), (26, 2.4, 0.06), pm(bgc, 0.7), 0, 0.02)
        text(txt, (0, 16.5, z - 0.05), 1.1, pm("#f4ecd8", 0.5), 0, "sans", 0.006, fit=24)
    # US flag hanging large
    from . import ikit as I
    from .c05_oval import us_flag_mat
    I.flag("fcflag", (6, 15.8, 120), 10, 6.0, mat_once("fcusflag", us_flag_mat), math.pi, 0.08, 1.5)
    # work stands, jigs, toolboxes, rivet guns on hoses, crates, compressor drums, parts racks along the lines
    for k in range(26):
        z = 0 + k * 9
        for x in (-6.5, 6.5):
            K.box((x, 0.5, z), (1.6, 1.0, 0.8), pm(("#3a5a8a", "#8a3a2a", "#4a6a3a")[k % 3], 0.5, 0.3), 0, 0.03)
            K.box((x, 1.05, z), (1.5, 0.1, 0.7), DARK, 0, 0.01)
            for j in range(3): K.cyl((x - 0.5 + j * 0.5, 1.15, z), 0.05, 0.2, pm("#8a8a90", 0.3, 0.8), 8)
        crate(K, (rnd.choice((-25, 25)), 0.5, z + 3), 1.0, wood("#9a8458", "#5a4a2a", 10, 0.8), 0.1 * k)
    for k in range(8): K.box((-36, 2.5, 10 + k * 12), (3, 5, 8), STEEL, 0, 0.03)
    # ---- the tank bay (foreground): M4s being finished, a gantry, workers' stands ----
    for k, z in enumerate((-6, 6, 18)): m4(K, (0, 0, z), math.pi / 2, "#4a5232")
    lattice_mast(K, (-4.5, 0, 6), 9, 0.6, 0.6, YEL, 4); lattice_mast(K, (4.5, 0, 6), 9, 0.6, 0.6, YEL, 4)
    K.box((0, 9.1, 6), (9.6, 0.7, 0.7), YEL, 0, 0.02); K.cyl((0, 6.5, 6), 0.02, 5, DARK, 6); K.box((0, 4.0, 6), (0.6, 0.4, 0.4), YEL, 0, 0.02)
    for k in range(6): jeep(f"jp{k}", (30, 0, -6 + k * 4.5), math.pi / 2, "#4a5232", K)
    # ---- Rosie's stand: a fuselage section on a jig with a platform ----
    sk = alu("fcalu")
    st = [(34.0, 1.0, 1.4, 1.5, 2.2), (26.0, 1.0, 1.4, 1.5, 2.2)]
    from .c05_kit import body
    body(K, sk, st, 24, 3.2, 8.0)
    for dz in (-3, 0, 3): K.box((8.0, 0.35, 30 + dz), (2.4, 0.7, 0.3), YEL, 0, 0.02)
    for k in range(10): K.box((8.0 + 1.0 * math.cos(k * 0.35 - 1.6), 2.2 + 1.5 * math.sin(k * 0.35 - 1.6), 30 - 4.0), (0.12, 0.12, 0.02), pm("#9aa84a", 0.6), 0, 0.0)
    K.box((8.0, 1.2, 26.5), (5, 0.1, 1.4), DARK, 0, 0.02)
    for x in (5.6, 10.4): K.box((x, 0.6, 26.0), (0.08, 1.2, 0.08), DARK, 0, 0.0)
    K.box((8.0, 2.2, 25.85), (5, 0.06, 0.06), YEL, 0, 0.0)
    K.build()
    # ---- the B-24 lines (moving) ----
    fin = b24("b24a", "alu", False, True, True, 0); line = [fin] + [clone(fin, f"b24a{k}") for k in range(1, 6)]
    fus = b24("b24f", "alu", False, True, False, 2); jig = [fus] + [clone(fus, f"b24f{k}") for k in range(1, 6)]
    part = b24("b24p", "alu", False, True, True, 1); mid = [part] + [clone(part, f"b24p{k}") for k in range(1, 3)]
    sparks = []
    for k in range(12):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.04, location=(0, 0, 0)); o = bpy.context.object; o.data.materials.append(em("#ffd070", 40.0)); sparks.append(o)
    # light: high windows (cool daylight), rows of warm lamps, a warm key on the foreground bays
    area((0, 24, 120), (0, 0, 120), 60000, (0.85, 0.9, 1.0), 60, 260)
    for k in range(10): point((rnd.choice((-20, 0, 20)), 17.5, k * 28), 3000, (1.0, 0.8, 0.55), 1.0)
    area((10, 10, -16), (0, 1, 10), 5000, (1.0, 0.85, 0.65), 10)
    area((14, 6, 20), (8, 1.5, 28), 1400, (1.0, 0.82, 0.6), 4)
    def update(f):
        s = 0.012 * f
        for k, e in enumerate(line): pose(e, (-14, 2.0, 60 + k * 36 + s), math.pi, 0.0, 0.0)
        for k, e in enumerate(jig): pose(e, (14, 2.0, 50 + k * 30 + s), math.pi, 0.0, 0.0)
        for k, e in enumerate(mid): pose(e, (-14 if k % 2 else 14, 2.0, 230 + k * 7 + s), math.pi, 0.0, 0.0)
        CH.location = T(0, 17.5, 255.1); MH.location = T(0, 17.5, 255.05)
        CH.rotation_euler = (0, -1.2 - f * 0.002, 0); MH.rotation_euler = (0, -f * 0.024, 0)
        r = random.Random(f)
        for k, o in enumerate(sparks):
            u = (f * 0.37 + k * 0.13) % 1.0
            o.location = T(7.0 + (k % 3) * 1.3 + 0.5 * u * math.cos(k), 2.3 + (k % 2) * 0.8 - 0.8 * u * u, 25.9 - 0.2 * u)
    update(0)
    return {"update": update}
