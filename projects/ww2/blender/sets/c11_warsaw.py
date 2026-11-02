# Summer 1944 in the east (chapter 11): Operation Bagration's road and the Warsaw uprising, one set.
#  - East bank (z < 56, ground y 0): a dirt road along x 0 (z -90..40) through birch groves and wheat (BAGRATION: the
#    T-34s rolling toward the camera at (0, -14) and (-3.5, -36), riders sit on the decks at y ~2.4); the Soviet tank line
#    parked on the river bank at (-24, 48) (-8, 50) (9, 47) (26, 50) facing the city (+z); crews' camp fire at (-1, 0, 42).
#    Keep clear: the road |x| < 3 for z -10..30; the bank strip z 38..45, x -20..20 (crews sit / stand there).
#  - The Vistula z 58..140 (water y -1.4) between stone embankments; the burnt-out bridge piers at x 40.
#  - West bank: the Old Town riverfront (z 146..160) with the Royal Castle clock tower at x -32, church spires; fires and
#    smoke at dusk. THE UPRISING STREET at x 0 running z 162..262 between house rows (facades at x -9 / +9), the
#    barricade across it at z 186 (fighters stand at z 187..190, y 0), a flat roof with a parapet at (-13, 15.2, 205)
#    (fighters on the rooftop, x -16..-10, z 200..210); Polish flags hang from the windows.
#  - THE RUINED STREET (after the uprising) at x 80, same layout (z 162..262), gutted, smoking, empty.
# Light: golden (Bagration), dusk (the Soviets wait / the city burns), day / gloom (the uprising), grey (the ruins).
import bpy, math, random
import lib
from lib import T
from sets import c11_kit as C
from sets.c11_kit import Kit, pm, em, text, sign, iron, brass, glassm
from sets import ikit as IK
from sets.void import fire, smoke_mat, smoke_column, mat_once

def H(x, z):
    if z < 56: return 0.25 * C.nz2(x, z, 0.04, 2.0) * min(1.0, max(0.0, abs(x) - 4) / 8) * (1 if z < 36 else 0)
    if z < 142: return -3.0
    return 0.0

def build(M, D):
    light = D.get("light", "day"); rnd = random.Random(1944); C.SB.reset()
    kind = {"golden": "golden", "dusk": "dusk", "day": "day", "gloom": "grey", "grey": "grey", "night": "night"}.get(light, "day")
    sd = {"golden": (-0.6, 0.3, 0.75), "dusk": (0.4, 0.1, 1.0), "day": (0.5, 0.7, 0.6), "grey": (0.3, 0.7, 0.6), "night": (0.3, 0.5, 1.0)}[kind]
    C.sky(kind, sd, 0.9); C.sun(sd, {"golden": 3.8, "dusk": 2.4, "day": 4.0, "grey": 1.8, "night": 0.3}[kind], C.SKIES[kind]["sun"], 2.0)
    burning = kind in ("dusk", "night")
    K = Kit("warsaw"); TM = C.tree_mats("summer")
    gm = C.grass_mat("ws_grass", "#5a7a2a", "#8a9a3a", "#b8a85a")
    C.ground("ws_ground", -160, 200, -100, 300, 1.2, H, gm)
    K.box((20, -1.4, 99), (400, 0.05, 86), C.water_mat("ws_river", "#1e3236", "#4a625e", 0.05), 0, 0)
    stone = C.concrete("ws_emb", "#8a8478")
    K.box((20, -1.6, 57), (400, 3.4, 2.0), stone, 0, 0.02); K.box((20, -1.6, 142), (400, 3.4, 2.0), stone, 0, 0.02)
    for k in range(3): K.box((40, -2.0, 75 + k * 25), (5, 4.0, 3.5), stone, 0, 0.05)
    K.box((40, 1.0, 70), (5.5, 1.0, 8), iron("#3a3634"), 0, 0.02, 0.3, 0.05)
    # ---------- east bank: the road, wheat, birches, the tank line, the crews' camp ----------
    road = C.sand_mat("ws_road", "#8a7656", "#6a5a42")
    K.box((0, 0.01, -25), (5.0, 0.02, 130), road, 0, 0)
    wheat = C.mat_once("ws_wheat", lambda: C._mixmat("ws_wheat", [(0.3, "#a88a3a"), (0.55, "#d8b860"), (0.75, "#e8cc78")], 0.2, 30, 0.9, 1.0, 0.4))
    for s in (-1, 1):
        K.box((s * 30, 0.45, -20), (40, 0.9, 90), wheat, 0, 0.3)
    for k in range(240):
        s = rnd.choice((-1, 1)); x = s * rnd.uniform(6, 60); z = rnd.uniform(-100, 34)
        if 10 < abs(x) < 50 and -60 < z < 25 and rnd.random() < 0.8: continue
        C.birch(K, x, 0, z, rnd.uniform(9, 15), rnd, TM)
    for k in range(40):
        x, z = rnd.uniform(-150, 190), rnd.uniform(-20, 40)
        if abs(x) < 40: continue
        C.birch(K, x, 0, z, rnd.uniform(9, 14), rnd, TM)
    for n, (x, z, yw) in enumerate(((0, -14, math.pi / 2 + 0.05), (-3.5, -36, math.pi / 2 - 0.1), (2.0, -58, math.pi / 2), (-24, 48, -math.pi / 2 + 0.1), (-8, 50, -math.pi / 2), (9, 47, -math.pi / 2 - 0.15), (26, 50, -math.pi / 2 + 0.05))):
        C.tank_at(f"t34_{n}", x, 0, z, yw, "#4a5a30", "red")
    for k in range(3):   # burnt-out German vehicles by the road
        C.tank_at(f"wreck{k}", [-9, 10, -12][k], 0, [-28, -50, -72][k], [0.4, 2.6, 1.2][k], "#5e6658", None, burnt=True, tilt=0.1)
    TRM = dict(body=C.worn("ws_truck", "#5e6658", "#3a3a32", 0.7, 0.2, 6, 0.6), dark=pm("#2a2a24", 0.6), tyre=pm("#1a1a1a", 0.85), canvas=C.SB.cloth("#5a5a48"))
    C.truck(K, 8, -40, 2.2, TRM)
    fire("ws_cf", (-1, 0.0, 42), 0.5, seed=2, energy=500)
    for k in range(8): K.cyl((-1 + 0.6 * math.cos(k), 0.08, 42 + 0.6 * math.sin(k)), 0.06, 0.6, C.bark_mat(), 6, "x", None, k * 0.8)
    for k in range(5): K.box((3 + k * 0.5, 0.2, 40 + (k % 2) * 0.4), (0.45, 0.4, 0.4), C.SB.wood("#6a5a3a", "#3a2e1a", 8), 0.2 * k, 0.02)
    K.box((-6, 0.3, 40.5), (2.0, 0.06, 0.4), C.SB.wood("#6a5a3a", "#3a2e1a", 8), 0, 0.01)
    C.flagpole("ws_sf", -14, 0, 44, 4.0, "su", 0.0, 1.2, 0.8, 0.07)
    # ---------- the west bank: Old Town riverfront + castle + spires ----------
    pal = ["#d8a868", "#c87a5a", "#a8b880", "#e0c8a0", "#8aa8b8", "#d89070", "#c8b870", "#b8706a", "#e8d8b8", "#9ab088"]
    roof = C.SB.stripes("ws_roof", "#8a3a2a", "#7a3222", 8, 2); trim = pm("#efe6d2", 0.6)
    fireglow = C.SB.window_glow("wsf", "#ff7a2a", 6.0) if burning else C.SB.window_glow("wsw", "#ffc070", 1.5)
    x = -110.0
    while x < 150:
        w = rnd.uniform(6, 9)
        if abs(x + w / 2 - 0) < 9: x += 18; continue
        if abs(x + w / 2 - 80) < 9: x += 18; continue
        C.house(K, x + w / 2, 152 + rnd.uniform(-0.5, 0.5), w, 10, rnd.randint(4, 5), 0.0, C.plaster(f"ws{len(pal)}", rnd.choice(pal)), trim, roof, fireglow, rnd, 3.2,
                shutters=pm("#3a5a3a", 0.6), lit=0.35 if burning else 0.1, base=stone)
        x += w + 0.1
    C.house(K, -32, 168, 34, 14, 3, 0.0, C.plaster("wscastle", "#d87a5a"), trim, C.SB.stripes("ws_croof", "#4a5a54", "#3a4a44", 6, 2), fireglow, rnd, 4.0, roof="gable", lit=0.2)
    K.box((-32, 22, 160), (6, 20, 6), C.plaster("wscastle", "#d87a5a"), 0, 0.05)
    K.cyl((-32, 34, 160), 2.6, 6, C.SB.stripes("ws_croof", "#4a5a54", "#3a4a44", 6, 2), 8, "y", 0.6)
    K.cyl((-32, 38.5, 160), 0.6, 4, C.SB.stripes("ws_croof", "#4a5a54", "#3a4a44", 6, 2), 8, "y", 0.0)
    K.cyl((-32, 26, 156.9), 1.4, 0.2, pm("#f0e8d0", 0.4), 24, "z"); K.cyl((-32, 26, 156.8), 1.5, 0.12, C.gold(), 24, "z")
    for x, z, h in ((18, 200, 46), (-60, 210, 40), (52, 230, 38)):
        K.box((x, h / 2 - 6, z), (7, h - 12, 7), C.brickm("ws_ch", "#8a4a36", "#6a3424"), 0, 0.05); K.cyl((x, h, z), 4.0, 14, C.SB.stripes("ws_croof", "#4a5a54", "#3a4a44", 6, 2), 8, "y", 0.0, math.pi / 8)
    for k in range(40):
        x, z = rnd.uniform(-140, 190), rnd.uniform(175, 300)
        if abs(x) < 16 or abs(x - 80) < 16: continue
        C.house(K, x, z, rnd.uniform(8, 14), 10, rnd.randint(4, 6), 0.0, C.plaster(f"wsb{k % 5}", pal[k % len(pal)]), trim, roof, fireglow, rnd, 3.2, roof="gable" if k % 3 else "flat", lit=0.3 if burning else 0.05)
    # ---------- the uprising street (x 0) ----------
    cob = C.SB.wet_cobbles("ws_cob", "#6e6a68", "#4c4846", 0.3, 4.0)
    for sx in (0, 80):
        K.box((sx, 0.01, 212), (18, 0.02, 104), cob, 0, 0)
        for s in (-1, 1): K.box((sx + s * 7.8, 0.1, 212), (2.4, 0.2, 104), C.concrete("ws_kerb", "#9a948a"), 0, 0.01)
    for side in (-1, 1):
        z = 162.0; k = 0
        while z < 262:
            w = rnd.uniform(7, 10)
            flat = side < 0 and abs(z + w / 2 - 205) < 5
            if flat:
                C.house(K, side * 13, z + w / 2, w, 8, 5, side * math.pi / 2, C.plaster("wsfl", "#c8b090"), trim, roof, fireglow, rnd, 3.0, roof="flat", lit=0.1, shutters=pm("#5a3a2a", 0.6))
                for s2 in (-1, 1): K.box((-13, 15.4, z + w / 2 + s2 * (w / 2 - 0.15)), (8, 0.7, 0.3), C.plaster("wsfl", "#c8b090"), 0, 0.01)
                K.box((-9.15, 15.4, z + w / 2), (0.3, 0.7, w), C.plaster("wsfl", "#c8b090"), 0, 0.01)
            else:
                C.house(K, side * 13, z + w / 2, w, 8, rnd.randint(4, 5), side * math.pi / 2, C.plaster(f"wss{k % 6}", pal[(k * 3 + (side > 0)) % len(pal)]), trim, roof, fireglow, rnd, 3.0,
                        shutters=pm(rnd.choice(["#3a5a3a", "#5a3a2a", "#3a4a6a"]), 0.6), lit=0.1 if not burning else 0.4, base=stone, balcony="one" if k % 3 == 1 else None)
                if k % 2 == 0: C.banner(f"wsb{side}{k}", (side * 8.85, 9.5, z + w / 2), 1.2, 1.8, "pl", side * math.pi / 2)
            z += w + 0.05; k += 1
        z = 162.0; k = 0
        while z < 262:
            w = rnd.uniform(7, 10)
            C.house(K, 80 + side * 13, z + w / 2, w, 8, rnd.randint(4, 5), side * math.pi / 2, C.plaster(f"wsr{k % 6}", pal[(k * 5) % len(pal)]), trim, roof, fireglow, rnd, 3.0, ruin=rnd.uniform(0.4, 0.95))
            z += w + 0.05; k += 1
    # the barricade: paving stones, an overturned tram, sandbags, furniture, a cart; the anchor sign and posters
    pave = C.concrete("ws_pave", "#7a7470")
    for k in range(90):
        K.box((rnd.uniform(-6.5, 6.5), rnd.uniform(0.1, 1.3), 186 + rnd.uniform(-0.6, 0.6)), (0.35, 0.22, 0.25), pave, rnd.random() * 3, 0.02, rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4))
    tram = C.SB.stripes("ws_tram", "#b8282a", "#e8dcc0", 3.0, 2)
    K.box((-2.5, 1.1, 185.6), (8.0, 2.2, 2.4), pm("#b8282a", 0.5), 0.12, 0.08, 0, 1.45)
    for k in range(6): K.box((-5.5 + k * 1.2, 1.1, 184.35), (0.8, 0.02, 0.6), pm("#1e2228", 0.1), 0.12, 0, math.pi / 2, 1.45)
    C.sandbags(K, 4.0, 0.0, 185.2, 0.0, 7, 3, C.sandbag_m(), rnd)
    for k in range(4): K.box((rnd.uniform(-6, 6), 0.4, 186.6 + rnd.uniform(0, 0.4)), (1.0, 0.8, 0.5), C.SB.wood("#6a4a2a", "#3a2614", 6), rnd.random(), 0.02, 0, rnd.uniform(-0.6, 0.6))
    anchor = C.poster_img([("PW", 0.5, "#1e1e1e")], "#d8ccb0", "#1e1e1e", 128, 128, seed=4)
    IK.panel("ws_anchor", (-8.75, 2.2, 190), 1.0, 1.0, IK.img_mat("ws_anc", anchor, 0.8), math.pi / 2)
    for k in range(3):
        a = C.poster_img([(["WARSZAWA", "WALCZY!", "POLSKA"][k], 0.16, "#b8202c"), (["1 VIII", "1944", "ZYJE"][k], 0.12)], "#f0e8d4", "#1e1e1e", 140, 190, seed=10 + k)
        IK.panel(f"ws_pos{k}", (8.75, 1.8, 195 + k * 1.3), 0.8, 1.05, IK.img_mat(f"ws_posm{k}", a, 0.8), -math.pi / 2)
    C.flagpole("ws_bf", 1.2, 1.4, 186.2, 2.6, "pl", 0.0, 1.1, 0.7, 0.07, C.SB.wood("#6a4a2a", "#3a2614", 6))
    C.flagpole("ws_rf", -12.5, 15.2, 207, 2.4, "pl", 0.3, 1.2, 0.75, 0.08, C.SB.wood("#6a4a2a", "#3a2614", 6))
    for k in range(6): K.box((-15 + k * 0.9, 15.4, 201.5), (0.6, 0.35, 0.4), C.sandbag_m(), 0.2 * k, 0.07)
    # lamp posts and tram wires along the street
    for z in range(166, 262, 14):
        for s in (-1, 1):
            K.cyl((s * 7.0, 2.4, z), 0.08, 4.8, iron("#2a2a2a"), 8); K.cyl((s * 6.7, 4.8, z), 0.2, 0.3, iron("#2a2a2a"), 10, "y", 0.08)
        K.box((0, 6.2, z), (14, 0.02, 0.02), iron("#1a1a1a"), 0, 0)
    K.box((0, 6.0, 212), (0.02, 0.02, 100), iron("#1a1a1a"), 0, 0)
    # the ruined street: rubble ridges, a burnt tram, bent lamp posts
    for k in range(10): C.rubble(K, 80 + rnd.uniform(-5, 5), 168 + k * 9.5, rnd.uniform(2.5, 4.5), rnd.uniform(0.8, 2.0), rnd, [pave, C.brickm("fd_hb", "#8a4a36", "#6a3424"), pm("#3a3430", 0.9)])
    K.box((78, 1.0, 200), (8.0, 2.0, 2.4), pm("#2a2220", 0.8), 0.4, 0.08)
    sm = smoke_mat("ws_smoke", "#2a2420" if burning else "#5a5450", 0.45)
    if burning:
        for k in range(10):
            x, z = rnd.uniform(-100, 140), rnd.uniform(152, 260)
            smoke_column(f"wsm{k}", (x, 16, z), 40, 3, 12, sm, (30, 20), 70 + k, 12)
            fire(f"wsfi{k}", (x, 14, z - 4), 2.5, seed=80 + k, energy=8000)
    else:
        for k in range(5):
            x, z = 80 + rnd.uniform(-10, 10), rnd.uniform(170, 255)
            smoke_column(f"wsr{k}", (x, 2, z), 30, 1.5, 6, sm, (10, 6), 90 + k, 10)
        for k in range(4): smoke_column(f"wsd{k}", (rnd.uniform(-80, 140), 18, rnd.uniform(200, 290)), 40, 3, 10, sm, (20, 10), 95 + k, 10)
    C.fill((0, 12, -30), (0, 1, 0), 8000, (1.0, 0.85, 0.65), 30)
    C.fill((0, 10, 30), (0, 1, 48), 3000 if not burning else 1500, (1.0, 0.8, 0.6) if not burning else (1.0, 0.5, 0.25), 20)
    C.fill((0, 12, 168), (0, 1, 200), 5000, (1.0, 0.9, 0.8) if not burning else (1.0, 0.55, 0.3), 14)
    C.fill((80, 12, 168), (80, 1, 200), 4000, (0.85, 0.88, 0.95), 14)
    K.build()
    return {}
