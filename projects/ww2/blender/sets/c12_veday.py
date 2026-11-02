# VE Day, 8 May 1945 (chapter 12): three cities in one set, each a street packed with flags for the crowds (characters).
#   LONDON (x 0): Portland-stone street along +z (road |x| < 7, z -10..60), Union flags and bunting, a red double-decker,
#     a phone box, Big Ben's tower closing the view at (6, 0, 95).
#   PARIS (x 200): Haussmann facades with balconies and mansards, tricolores, a cafe awning, the Eiffel Tower far at (215, 0, 260).
#   NEW YORK (x 400): Times Square canyon - towers with signboards, "V-E DAY" and war-bond signs, a newsstand at
#     (395.5, 0, 6), a flagpole with the flag at half-mast at (404, 0, 14) (shot "Roosevelt dies", light "grey").
# Characters stand on the roads (y 0) at |x - X| < 6, z 0..25. Light: festive spring sun (or overcast for "grey").
import bpy, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, TS
from sets.void import lathe, tube, worn, pmat, wood_mat, mat_once, link, mesh_obj, text
from sets.front import flag as wave_flag
from sets import c09_kit as K
from sets import ikit
from sets.kit_sbpw import Kit, wet_cobbles

bx, cy = K.bx, K.cy
def flagm(kind):
    from sets.c12_yalta import flagm as fm
    return fm(kind)
def bunting(name, a, b, sag, cols, rnd):
    n = int(math.dist(a, b) / 0.45)
    pts = []
    for k in range(n + 1):
        t = k / n; pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - sag * math.sin(math.pi * t), a[2] + (b[2] - a[2]) * t))
    tube(f"{name}cord", pts, 0.01, pmat("c12cord", "#3a3a3a", 0.6), res=4, bres=0)
    for k in range(n):
        p, q = pts[k], pts[k + 1]; mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 - 0.3, (p[2] + q[2]) / 2)
        mesh_obj(f"{name}p{k}", [p, q, mid], [(0, 1, 2)], pmat("c12bunt" + cols[k % len(cols)], cols[k % len(cols)], 0.7))
def street(K2, X, rnd, style, z0=-12, z1=64):
    """two rows of facades facing the road at x = X +- 8, with windows, cornices and flags hung from sills"""
    if style == "london":
        cols = ["#d8d0bc", "#cfc6b0", "#e0d8c4", "#c8bea8"]; h0 = 14
    elif style == "paris":
        cols = ["#e8dcc0", "#e0d2b4", "#ece2c8", "#d8ccb0"]; h0 = 18
    else:
        cols = ["#8a7a6a", "#a89a88", "#6a6a70", "#b8a890", "#7a5a4a"]; h0 = 40
    win = K.mat_once("c12win", lambda: lib.principled("c12win", lib.hexc("#2a3440"), 0.1, 0.2))
    trim = K.mat_once("c12trim" + style, lambda: lib.plaster("c12trim" + style, "#f2ecdc" if style != "ny" else "#c8c0b0"))
    flags = {"london": ["uk", "uk", "us", "uk"], "paris": ["fr", "fr", "uk", "us"], "ny": ["us", "us", "us", "uk"]}[style]
    for sd in (-1, 1):
        z = z0; k = 0
        while z < z1:
            w = rnd.uniform(9, 13) if style != "ny" else rnd.uniform(12, 18); h = h0 + rnd.uniform(-2, 4) * (1 if style != "ny" else 8)
            col = cols[k % len(cols)]; m = K.mat_once(f"c12fac{style}{col}", lambda c=col: worn(f"c12fac{style}{c}", c, "#4a4440", 0.85, 0.0, 1.0, 0.62, "#8a8070"))
            x = X + sd * (8 + 4)
            K2.box((x, h / 2, z + w / 2), (8, h, w), m, 0, 0.02)
            K2.box((X + sd * 7.95, h - 0.4, z + w / 2), (0.3, 0.5, w), trim, 0, 0.01)
            floors = int((h - 2) / 3.2)
            for fl in range(floors):
                y = 3.0 + fl * 3.2
                for j in range(int(w / 2.2)):
                    zz = z + 1.1 + j * 2.2
                    K2.box((X + sd * 7.98, y, zz), (0.06, 1.8, 1.1), win, 0, 0.0)
                    K2.box((X + sd * 7.94, y - 1.0, zz), (0.15, 0.12, 1.4), trim, 0, 0.0)
                    if style == "paris" and fl in (1, 4): K2.box((X + sd * 7.7, y - 0.95, zz), (0.5, 0.06, 1.3), pmat("c12iron", "#1e1e1e", 0.5, 0.6), 0, 0.0)
            if style == "paris": K.loft2(f"mans{sd}{k}", [(4.0, -w / 2), (4.0, w / 2), (-4.0, w / 2), (-4.0, -w / 2)], h, [(2.5, -w / 2), (2.5, w / 2), (-4.0, w / 2), (-4.0, -w / 2)], h + 3.0, K.P_of(x, z + w / 2, 0, 0) if sd < 0 else K.P_of(x, z + w / 2, math.pi, 0), K.mat_once("c12slate", lambda: worn("c12slate", "#5a6068", "#3a3e44", 0.6, 0.2, 3, 0.6)))
            if k % 2 == 0:
                fy = 3.0 + rnd.randint(1, 3) * 3.2 - 0.4; fz = z + w / 2
                tube(f"fp{style}{sd}{k}", [(X + sd * 7.9, fy, fz), (X + sd * 6.4, fy + 1.2, fz)], 0.035, pmat("c12pole", "#e8e4d8", 0.4), res=2, bres=0)
                wave_flag(f"fl{style}{sd}{k}", (X + sd * 6.4, fy + 1.2, fz), 1.4, 0.9, (0, 1), flagm(flags[k % 4]), 0.08)
            z += w; k += 1
def build(M, D):
    rnd = random.Random(1945); grey = D.get("light") == "grey"
    if grey: K.sky("#8a929c", "#c8ccd0", 0.8, "#7a848e", "#c0c4c8")
    else: K.sky("#4a88d8", "#e0eef8", 1.0, "#3a7ad8", "#e8f0f8")
    K2 = Kit("veday")
    for X, style in ((0.0, "london"), (200.0, "paris"), (400.0, "ny")):
        K2.box((X, -0.05, 26), (16, 0.1, 140), wet_cobbles(f"c12road{style}", "#5a5a60", "#46464c", 0.2, 4.0) if style != "ny" else K.concrete("c12asph", "#4a4a4e", "#2a2a2e"), 0, 0.0)
        for sd in (-1, 1): K2.box((X + sd * 7.0, 0.08, 26), (2.0, 0.16, 140), K.concrete("c12walk", "#9a968e"), 0, 0.01)
        street(K2, X, rnd, style)
    K2.build()
    cols = ["#c8202c", "#f4f2ec", "#2a4a9a"]
    for X in (0.0, 200.0, 400.0):
        for k in range(7): bunting(f"bt{X}{k}", (X - 7.9, 6.5 + (k % 2), 2 + k * 7), (X + 7.9, 7.0, 5 + k * 7), 1.2, cols, rnd)
    london(rnd); paris(rnd); ny(rnd, grey)
    if grey:
        K.sun((0.3, 0.6, -0.6), 1.2, (0.85, 0.88, 0.95), 10.0)
        K.area((400, 60, -40), (400, 0, 30), 20000, (0.7, 0.76, 0.85), 80)
    else:
        K.sun((0.45, 0.7, -0.5), 4.8, (1.0, 0.92, 0.8), 1.5)
        for X in (0.0, 200.0, 400.0): K.area((X, 50, -40), (X, 0, 30), 22000, (0.62, 0.75, 1.0), 80)
    return {}
def london(rnd):
    red = K.mat_once("c12red", lambda: worn("c12red", "#b81e22", "#5a1012", 0.45, 0.2, 4, 0.66, "#8a1418"))
    win = K.mat_once("c12win", lambda: None)
    P = K.P_of(3.2, 22, -math.pi / 2, 0.0)
    bx("busl", P(0, 1.3, 0), (8.4, 2.0, 2.4), red, 0.1, -math.pi / 2); bx("busu", P(0, 3.3, 0), (8.2, 1.9, 2.35), red, 0.1, -math.pi / 2)
    for k in range(6):
        for y_ in (1.6, 3.4):
            for sd in (-1, 1): bx(f"busw{k}{y_}{sd}", P(-3.2 + k * 1.25, y_, sd * 1.19), (1.0, 0.75, 0.04), win, 0.0, -math.pi / 2)
    bx("busad", P(0, 2.45, -1.2), (6, 0.35, 0.04), pmat("c12ad", "#f2e8c8", 0.6), 0.0, -math.pi / 2)
    text("VICTORY  BUY BONDS", P(0, 2.38, -1.23), 0.22, pmat("c12adk", "#1e2a5a", 0.6), yaw=math.pi / 2, flat=False)
    for lx in (-2.6, 2.6):
        for sd in (-1, 1): K.wheel(f"busw{lx}{sd}", P, lx, 0.5, sd * 1.15, 0.5, 0.3, pmat("ftyre", "#141414", 0.8), -math.pi / 2, 18)
    bx("phonebox", (-6.6, 1.3, 9), (0.9, 2.6, 0.9), red, 0.04)
    for sd in (-1, 1): bx(f"pbw{sd}", (-6.6 + sd * 0.46, 1.4, 9), (0.03, 1.6, 0.7), win, 0.0)
    bx("pbsign", (-6.6, 2.4, 8.54), (0.7, 0.18, 0.02), pmat("c12pbs", "#f2ecdc", 0.6), 0.0); text("TELEPHONE", (-6.6, 2.39, 8.52), 0.09, pmat("kink2", "#1a1a1a", 0.6), flat=False)
    # Big Ben's tower: shaft, clock stage with four faces, belfry, spire
    st = K.mat_once("c12bb", lambda: worn("c12bb", "#c8b48a", "#8a7a5a", 0.8, 0.0, 1.2, 0.6, "#a8946a"))
    bx("bbshaft", (6, 30, 95), (12, 60, 12), st, 0.05)
    for k in range(6): bx(f"bbrib{k}", (6 - 5 + k * 2, 30, 88.95), (0.4, 58, 0.3), st, 0.01)
    bx("bbclock", (6, 66, 95), (13, 12, 13), st, 0.05)
    cy("bbface", (6, 66, 88.4), 4.6, 0.2, pmat("c12dial", "#f2ecd8", 0.5), 40, rot=(math.radians(90), 0, 0))
    for a_, ln in ((math.radians(0), 3.4), (math.radians(90), 2.4)):
        o = bx(f"bbh{ln}", (6 + ln / 2 * math.sin(a_), 66 + ln / 2 * math.cos(a_), 88.25), (0.3, ln, 0.1), pmat("kink2", "#1a1a1a", 0.6), 0.0); o.rotation_euler[1] = -a_
    bx("bbbelfry", (6, 76, 95), (11, 8, 11), st, 0.05)
    K.loft2("bbspire", [(5.5, -5.5), (5.5, 5.5), (-5.5, 5.5), (-5.5, -5.5)], 80, [(0.4, -0.4), (0.4, 0.4), (-0.4, 0.4), (-0.4, -0.4)], 100, K.P_of(6, 95, 0, 0), K.mat_once("c12spire", lambda: worn("c12spire", "#4a5a5a", "#2a3434", 0.6, 0.4, 3, 0.6)))
    for k in range(6):
        z_ = 4 + k * 9; tube(f"llamp{k}", [(-6.2, 0, z_), (-6.2, 4.2, z_)], 0.07, pmat("c12iron", "#1e1e1e", 0.5, 0.6), res=2, bres=1)
        lathe(f"llh{k}", [(0.0, 0.0), (0.22, 0.1), (0.18, 0.5), (0.0, 0.6)], (-6.2, 4.2, z_), pmat("c12iron", "#1e1e1e", 0.5, 0.6), 8)
def paris(rnd):
    X = 200.0
    awn = K.mat_once("c12awn", lambda: worn("c12awn", "#b81e22", "#f2ece0", 0.8, 0.0, 30, 0.6))
    o = bx("awning", (X - 6.8, 3.1, 14), (1.8, 0.1, 9), awn, 0.01); o.rotation_euler[1] = math.radians(-18)
    bx("cafesign", (X - 7.9, 3.9, 14), (0.1, 0.7, 6), pmat("c12cafe", "#1e3a2a", 0.5), 0.01)
    text("CAFÉ DE LA PAIX", (X - 7.84, 3.85, 14), 0.42, pmat("c12gold", "#e8c060", 0.3, 1.0), yaw=-math.pi / 2, flat=False)
    for k in range(6):
        x_, z_ = X - 6.2 + (k % 2) * 0.9, 11 + (k // 2) * 2.5
        cy(f"ctab{k}", (x_, 0.72, z_), 0.32, 0.03, pmat("c12marb", "#e8e4dc", 0.3), 20); cy(f"ctl{k}", (x_, 0.36, z_), 0.03, 0.72, pmat("c12iron", "#1e1e1e", 0.5, 0.6), 8)
    # the Eiffel Tower, far down the avenue: four tapering legs, platforms, lattice
    ir = K.mat_once("c12eiffel", lambda: worn("c12eiffel", "#6a5a48", "#3a3028", 0.6, 0.5, 2, 0.6))
    EX, EZ = X + 15, 260.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            pts = [(EX + sx * 32 * (1 - t) ** 1.8 + sx * 2, 160 * t, EZ + sz * 32 * (1 - t) ** 1.8 + sz * 2) for t in (0.0, 0.15, 0.35, 0.6, 0.85, 1.0)]
            tube(f"eleg{sx}{sz}", pts, 1.3, ir, res=6, bres=1, taper=lambda f: 1 - 0.75 * f)
    for y_, r in ((40, 24), (78, 12), (125, 5)): bx(f"eplat{y_}", (EX, y_, EZ), (r * 2, 3, r * 2), ir, 0.1)
    for k in range(4):
        a = k * math.pi / 2; tube(f"earch{k}", [(EX + 26 * math.cos(a) - 18 * math.sin(a), 0, EZ + 26 * math.sin(a) + 18 * math.cos(a)), (EX + 24 * math.cos(a), 26, EZ + 24 * math.sin(a)), (EX + 26 * math.cos(a) + 18 * math.sin(a), 0, EZ + 26 * math.sin(a) - 18 * math.cos(a))], 0.8, ir, res=8, bres=1)
    cy("espire", (EX, 172, EZ), 0.8, 24, ir, 8)
def ny(rnd, grey):
    X = 400.0
    signs = [("V-E DAY", "#c8202c", "#f6f0e0"), ("BUY WAR BONDS", "#1e3a7a", "#f2d860"), ("VICTORY", "#f2d860", "#1e1e24"), ("PALACE THEATRE", "#2a2a2e", "#f6e0a0"),
             ("THANK YOU G.I.", "#1e5a3a", "#f6f0e0"), ("HOTEL ASTOR", "#3a1e2e", "#f2d860")]
    for k, (txt, bg, fg) in enumerate(signs):
        sd = -1 if k % 2 else 1; z_ = 8 + k * 8; y_ = 9 + (k % 3) * 4
        m = lib.principled(f"c12sg{k}", lib.hexc(bg), 0.5, 0.0, lib.hexc(bg), 0.0 if grey else 0.6)
        bx(f"nysign{k}", (X + sd * 7.6, y_, z_), (0.3, 2.6, 7.0), m, 0.02)
        text(txt, (X + sd * 7.42, y_ - 0.1, z_), 0.9, lib.emit(f"c12sgt{k}", lib.hexc(fg), 0.4 if grey else 2.5), yaw=sd * math.pi / 2, flat=False)
        for j in range(16): cy(f"nyb{k}{j}", (X + sd * 7.42, y_ + 1.15, z_ - 3.3 + j * 0.44), 0.06, 0.06, lib.emit("c12bulb", (1.0, 0.85, 0.5), 0.5 if grey else 6), 8, rot=(0, math.radians(90), 0))
    # newsstand with papers, the flagpole (flag at half-mast)
    wd = wood_mat("c12stand", "#3a5a3a", "#1e2e1e", 6, 0.6)
    bx("nstand", (X - 4.5, 1.0, 6), (2.4, 2.0, 1.2), wd, 0.03); bx("nsroof", (X - 4.5, 2.2, 5.8), (2.8, 0.12, 1.8), wd, 0.02)
    for k in range(8): bx(f"npap{k}", (X - 5.5 + (k % 4) * 0.62, 1.15 + (k // 4) * 0.45, 5.38), (0.5, 0.4, 0.02), pmat("kpaper", "#f0e6cc", 0.8), 0.0)
    text("NEWS", (X - 4.5, 2.32, 4.88), 0.25, pmat("c12gold", "#e8c060", 0.3, 1.0), flat=False)
    tube("nypole", [(X + 4, 0, 14), (X + 4, 12, 14)], 0.07, pmat("c12pole", "#e8e4d8", 0.4), res=2, bres=1)
    lathe("nyball", [(0.0, 0.0), (0.15, 0.1), (0.0, 0.25)], (X + 4, 12, 14), pmat("c12gold", "#e8c060", 0.3, 1.0), 12)
    wave_flag("nyflag", (X + 4, 7.2, 14), 2.2, 1.4, (0, 1), flagm("us"), 0.06)
    lathe("nybase", [(0.0, 0.0), (0.6, 0.0), (0.5, 0.6), (0.0, 0.6)], (X + 4, 0, 14), K.concrete("c12walk", "#9a968e"), 16)
    for k in range(4):
        z_ = 3 + k * 12; tube(f"nylamp{k}", [(X + 6.3, 0, z_), (X + 6.3, 5, z_), (X + 5.5, 5.2, z_)], 0.07, pmat("c12iron", "#1e1e1e", 0.5, 0.6), res=2, bres=1)
