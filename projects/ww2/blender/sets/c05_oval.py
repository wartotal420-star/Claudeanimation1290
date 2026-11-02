# Chapter 5: Roosevelt's Oval Office, 1941. The oval room (cream walls, three tall windows with drapes behind the
# desk), FDR's famously cluttered desk (ship models, figurines, books, a telephone, a lamp, papers), the US flag and a
# dark-blue flag behind it, bookcases, ship paintings, a fireplace, an oval rug, sofas.
# Layout (three coords): oval centre (0, 0, 3), semi-axes 5.6 (x) and 4.6 (z); windows on the far curve (z ~7.4);
# the desk x -1.0..1.0, z 4.6..5.5, top y 0.78; Roosevelt sits behind it at (0, 0, 5.85) (mode "chair");
# keep clear in front of the desk z 1..4.4; the fireplace on the near wall at z -1.5 (behind the cameras).
import bpy, math, random, os
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, stripes, R90
from .c05_kit import (sky, area, point, spot, sun_light, lathe, tube, worn, mat_once, cached, loft_k, img_mat, quad)
from . import ikit as I

def build(M, D):
    random.seed(1941); K_.reset(); rnd = random.Random(33)
    sky((0.3, 0.45, 0.72), (0.6, 0.7, 0.85), (0.85, 0.88, 0.85), sun_dir=(0.3, 0.5, 0.8), glow=0.4)
    K = Kit("oval"); A, B, Z0, Hh = 5.6, 4.6, 3.0, 4.6
    WALL = grime("ovwall", "#ece2c8", 0.12); TRIM = pm("#f4eee0", 0.5); FL = I.planks("ovfloor", "#8a6038", "#5a3a1e", "Y", 0.12, 1.4, 0.3, 0.3)
    K.box((0, -0.05, Z0), (13, 0.1, 11), FL, 0, 0)
    K.box((0, Hh + 0.05, Z0), (13, 0.1, 11), pm("#f4eee0", 0.8), 0, 0)
    N = 72; WIN = [math.radians(a) for a in (62, 90, 118)]
    for k in range(N):
        a0, a1 = k / N * math.tau, (k + 1) / N * math.tau; a = (a0 + a1) / 2
        x, z = A * math.cos(a), Z0 + B * math.sin(a)
        w = math.hypot(A * (math.cos(a1) - math.cos(a0)), B * (math.sin(a1) - math.sin(a0))) + 0.02
        yaw = math.atan2(-B * math.cos(a), -A * math.sin(a))
        win = any(abs(math.atan2(math.sin(a - c), math.cos(a - c))) < math.radians(7) for c in WIN)
        if win:
            K.box((x, 0.45, z), (w, 0.9, 0.25), WALL, yaw, 0.0); K.box((x, 4.0, z), (w, 1.2, 0.25), WALL, yaw, 0.0)
            K.box((x * 1.01, 2.2, z + 0.02 * math.sin(a)), (w, 2.4, 0.02), pm("#c8dcf0", 0.05), yaw, 0.0)
        else:
            K.box((x, Hh / 2, z), (w, Hh, 0.25), WALL, yaw, 0.0)
            K.box((x * 0.985, 0.08, Z0 + (z - Z0) * 0.985), (w, 0.16, 0.06), TRIM, yaw, 0.0)
            K.box((x * 0.985, 0.95, Z0 + (z - Z0) * 0.985), (w, 0.05, 0.05), TRIM, yaw, 0.0)
        K.box((x * 0.985, Hh - 0.15, Z0 + (z - Z0) * 0.985), (w, 0.3, 0.1), TRIM, yaw, 0.0)
    for c in WIN:                                   # window frames, drapes, pelmets
        x, z = A * math.cos(c) * 0.98, Z0 + B * math.sin(c) * 0.98; yaw = math.atan2(-B * math.cos(c), -A * math.sin(c))
        for k in range(4): K.box((x, 1.0 + k * 0.8, z), (1.3, 0.05, 0.08), TRIM, yaw, 0.005)
        for d in (-0.32, 0.32): K.box((x + d * math.cos(yaw), 2.2, z - d * math.sin(yaw)), (0.05, 2.4, 0.08), TRIM, yaw, 0.005)
        for sd in (-1, 1):
            dx = sd * 0.85
            I.drape(f"ovdr{c}{sd}", (x + dx * math.cos(yaw), 4.0, z - dx * math.sin(yaw) - 0.15), 0.8, 3.7, I.velvet(f"ovvel{sd}", "#a8843a"), yaw, 5, 0.06, 0.0)
        K.box((x - 0.1 * math.sin(yaw), 4.1, z - 0.1 * math.cos(yaw)), (2.4, 0.35, 0.15), I.velvet("ovpel", "#a8843a"), yaw, 0.02)
    # outside the windows: lawn, trees, a sunlit wall
    K.box((0, -0.3, 30), (80, 0.2, 40), pm("#5a8a3a", 0.9), 0, 0)
    for k in range(14): K.sphere((-30 + k * 4.6, 5 + rnd.uniform(0, 3), 22 + rnd.uniform(0, 10)), rnd.uniform(3, 5), pm(("#3a6a2a", "#4a7a32")[k % 2], 0.9), 12)
    # rug, desk and its clutter
    K.cyl((0, 0.008, Z0), 1.0, 0.012, lib.carpet("ovrug", "#2a3a6a", "#c8a24a"), 48, "y", None, 0, 0, 0)
    rug = [o for o in []]
    DW = wood("#5a3018", "#2a1408", 6, 0.35)
    K.box((0, 0.76, 5.05), (2.1, 0.06, 1.0), DW, 0, 0.02)
    for sx in (-1, 1): K.box((sx * 0.75, 0.37, 5.05), (0.55, 0.74, 0.9), DW, 0, 0.02)
    for sx in (-1, 1):
        for k in range(3): K.box((sx * 0.75, 0.15 + k * 0.22, 4.59), (0.48, 0.18, 0.02), wood("#6a3a1e", "#2e1a0a", 8, 0.35), 0, 0.005); K.cyl((sx * 0.75, 0.24 + k * 0.22, 4.575), 0.02, 0.02, brass(), 8, "z")
    K.box((0, 0.795, 5.0), (0.8, 0.01, 0.5), pm("#2a4a32", 0.8), 0, 0.0)
    Y = 0.79
    # FDR's clutter: model ships, a donkey and elephant, a pig, books, a telephone, a lamp, a cigarette box, a little flag stand
    def ship(x, z, s, col):
        K.box((x, Y + 0.03 * s, z), (0.36 * s, 0.05 * s, 0.07 * s), pm(col, 0.4), 0.0, 0.01); K.box((x, Y + 0.065 * s, z), (0.12 * s, 0.03 * s, 0.05 * s), pm("#e8e0c8", 0.4), 0, 0.005)
        for d in (-0.08, 0.08): K.cyl((x + d * s, Y + 0.14 * s, z), 0.004 * s, 0.18 * s, pm("#5a3a1e", 0.5), 6)
    ship(-0.75, 4.75, 1.0, "#3a3a44"); ship(0.8, 5.35, 0.8, "#2a2a30")
    for k, (x, z, col) in enumerate(((-0.45, 4.7, "#8a8a8a"), (-0.3, 4.72, "#5a5a5a"), (0.5, 4.72, "#e8b0b0"))):
        K.box((x, Y + 0.05, z), (0.09, 0.05, 0.04), pm(col, 0.5), 0.3, 0.01); K.sphere((x + 0.05, Y + 0.08, z), 0.028, pm(col, 0.5), 8)
        for dx in (-0.03, 0.03): K.cyl((x + dx, Y + 0.012, z), 0.008, 0.025, pm(col, 0.5), 6)
    for k in range(5): K.box((0.85, Y + 0.03 + k * 0.045, 4.85), (0.28, 0.04, 0.2), pm(("#7a1e22", "#1e3a5a", "#2a4a2a", "#6a4a1e", "#3a2a4a")[k], 0.6), 0.1 * k, 0.003)
    K.box((-0.85, Y + 0.05, 5.3), (0.2, 0.08, 0.24), pm("#141214", 0.15), 0, 0.03); K.box((-0.85, Y + 0.13, 5.27), (0.24, 0.04, 0.05), pm("#141214", 0.15), 0, 0.015)
    lathe("ovlamp", [(0.0, 0.0), (0.09, 0.0), (0.03, 0.04), (0.02, 0.4), (0.0, 0.42)], (0.65, Y, 5.35), brass(), 16)
    lathe("ovlsh", [(0.08, 0.36), (0.18, 0.2), (0.19, 0.19), (0.09, 0.35)], (0.65, Y, 5.35), lib.principled("ovlsh", hexc("#f0d8a8"), 0.8, 0.0, (1.0, 0.75, 0.45), 2.0), 24, cap=False)
    point((0.65, Y + 0.3, 5.35), 15, (1.0, 0.72, 0.42), 0.04)
    for k in range(4): K.box((0.05 + k * 0.03, Y + 0.012 + k * 0.004, 4.85), (0.3, 0.006, 0.4), paper("#f2ead6"), 0.12 * k - 0.15, 0.0)
    K.cyl((-0.2, Y + 0.04, 5.25), 0.04, 0.08, pm("#2a2a2a", 0.3), 12)                             # ashtray + cigarette holder
    K.cyl((-0.6, Y + 0.02, 4.9), 0.05, 0.04, brass(), 14); K.cyl((-0.6, Y + 0.15, 4.9), 0.004, 0.25, brass(), 6)
    K.box((-0.55, Y + 0.24, 4.9), (0.1, 0.06, 0.004), stripes("ovminiflag", "#b8202a", "#f2ece0", 140, 2), 0, 0.0)
    # chair behind the desk (FDR's own chair is drawn by the character card) and the flags
    for sx, col in ((-1.6, "us"), (1.6, "pres")):
        K.cyl((sx, 1.3, 6.4), 0.025, 2.6, brass(), 8); K.sphere((sx, 2.65, 6.4), 0.05, K_.gold(), 10)
        if col == "us":
            I.flag("ovflag", (sx, 2.5, 6.42), 1.0, 1.4, mat_once("ovusflag", lambda: us_flag_mat()), math.pi / 2 + 0.3, 0.05, 2.0)
        else:
            I.flag("ovpflag", (sx, 2.5, 6.42), 1.0, 1.4, I.velvet("ovpres", "#1e2a5a"), math.pi / 2 - 0.3 + math.pi, 0.05, 2.0)
    # bookcases with ship models, paintings of ships, the fireplace with a portrait, sofas, side tables
    from .void import bookcase
    for k, a in enumerate((math.radians(25), math.radians(155))):
        x, z = A * math.cos(a) * 0.95, Z0 + B * math.sin(a) * 0.95; yaw = math.atan2(-B * math.cos(a), -A * math.sin(a))
        bookcase(f"ovbc{k}", (x, 0, z), 1.6, 2.4, 0.4, 5, DW, yaw=yaw + math.pi, seed=k + 2)
    for k, a in enumerate((math.radians(-25), math.radians(205), math.radians(40), math.radians(140))):
        x, z = A * math.cos(a) * 0.96, Z0 + B * math.sin(a) * 0.96; yaw = math.atan2(-B * math.cos(a), -A * math.sin(a))
        I.framed(f"ovpaint{k}", (x, 2.6 if k < 2 else 3.4, z), 1.1, 0.75, I.img_mat(f"ovpm{k}", I.landscape_img(seed=20 + k, water=True), 0.6), K_.gold(), yaw + math.pi, 0.07, 0.05)
    K.box((0, 0.6, -1.45), (2.2, 1.2, 0.3), pm("#f4eee0", 0.4), 0, 0.02); K.box((0, 1.25, -1.4), (2.6, 0.1, 0.4), pm("#f4eee0", 0.4), 0, 0.02)
    K.box((0, 0.45, -1.32), (1.0, 0.8, 0.05), pm("#141010", 0.9), 0, 0.0)
    VEL = I.velvet("ovsofa", "#8a2a2a")
    for sd in (-1, 1):
        cx = sd * 3.2; K.box((cx, 0.25, 2.2), (0.85, 0.4, 2.0), VEL, 0, 0.08); K.box((cx + sd * 0.35, 0.65, 2.2), (0.2, 0.6, 2.0), VEL, 0, 0.08)
        K.box((sd * 2.6, 0.5, 4.6), (0.5, 0.04, 0.5), DW, 0, 0.01); K.cyl((sd * 2.6, 0.25, 4.6), 0.04, 0.5, DW, 8)
        K.cyl((sd * 2.6, 0.62, 4.6), 0.1, 0.2, pm(("#2a4a8a", "#8a2a2a")[sd > 0], 0.2), 16)
    K.box((0, 0.42, 2.4), (1.4, 0.05, 0.7), DW, 0, 0.01)
    for dx in (-0.6, 0.6):
        for dz in (-0.28, 0.28): K.cyl((dx, 0.2, 2.4 + dz), 0.03, 0.4, DW, 8)
    K.build()
    # light: soft daylight through the three windows, warm lamp and ceiling fill, a rim from the windows
    for c in WIN:
        x, z = A * math.cos(c) * 1.05, Z0 + B * math.sin(c) * 1.05
        area((x, 2.3, z), (x * 0.3, 1.0, Z0 + (z - Z0) * 0.3), 500, (0.85, 0.9, 1.0), 1.4, 2.6)
    sun_light((-0.3, -0.5, -0.8), 3.0, (1.0, 0.9, 0.75), 1.5)
    area((0, 4.4, 2.0), (0, 0, 3.5), 500, (1.0, 0.82, 0.62), 5)
    area((0, 2.0, -1.0), (0, 1.2, 5.5), 220, (1.0, 0.8, 0.6), 3)
    return {}

def us_flag_mat():
    """48-star flag: 13 stripes, blue canton with a field of small stars (UV)"""
    import numpy as np
    a = I.canvas(260, 494, "#f4f0e6"); x, y = I.grid(a)
    I.put(a, (np.floor(y * 13) % 2 == 0), "#b8202a")
    I.rect(a, 0, 0, 0.4, 7 / 13, "#2a3468")
    for r in range(6):
        for c in range(8): I.ellipse(a, 0.025 + c * 0.05, 0.04 + r * 0.085, 0.009, 0.016, "#f4f0e6")
    I.shade(a, 0.08, 3, 30)
    return I.img_mat("ovus", a, 0.8, sheen=0.3)
