# The war room (shots 6-8): title, "the war before it", chapter card. sets.ts buildWarroom layout: room x -8..8,
# z -8..6 (back wall z 6), map table at (0, 1) 4.2 x 2.6 (top 0.95; the map spans x -1.95..1.95, z -0.2..2.2),
# a hanging lamp over it, the WW1 helmet at (1.2, 0.99, 1.7).
# The table map (maps/map_table.png, lon -42..192, lat 80.8..-63) puts Flanders / the Western Front under the helmet.
import bpy, math, random
from mathutils import Vector, Matrix
import lib
from lib import T, TS
from sets.void import (map_mat, map_plane, lathe, tube, worn, pmat, wood_mat, brass, glassm, gold, ink, text, mat_once, link,
                       toy_tank, pin_flag, unit_block, book, cup, compass, dividers, magnifier, pocket_watch, toy_ship, candle,
                       bookcase, window, sconce, smoke_mat)

def bx(name, c, s, m, bev=0.01, yaw=0.0): return lib.box(name, T(*c), TS(*s), m, bev, rot=(0, 0, yaw))
def cy(name, c, r, h, m, verts=20, rot=(0, 0, 0), bev=0.005): return lib.cyl(name, T(*c), r, h, m, verts, rot, bev)
Y = 0.952   # map surface

def helmet(name, c, yaw=0.3):
    """British Brodie (WW1): shallow sand-textured dome, wide flat brim with a rolled edge, rivet, leather chinstrap"""
    prof = [(0.0, 0.098), (0.05, 0.094), (0.082, 0.082), (0.102, 0.062), (0.112, 0.04), (0.118, 0.026), (0.165, 0.011), (0.18, 0.008),
            (0.184, 0.004), (0.178, 0.0), (0.163, 0.002), (0.112, 0.02), (0.106, 0.038), (0.096, 0.058), (0.077, 0.076), (0.047, 0.087), (0.0, 0.091)]
    m = worn("brodie", "#56603a", "#3a2a1e", 0.8, 0.2, 26, 0.68, "#6a6448")
    tilt = Matrix.Rotation(math.radians(7), 3, "X") @ Matrix.Rotation(math.radians(-4), 3, "Z")
    o = lathe(name, prof, (c[0], c[1] + 0.012, c[2]), m, 64, yaw=yaw, sz=0.86, cap=False, tilt=tilt)
    rnd = random.Random(14)
    dents = [(Vector((rnd.uniform(-0.08, 0.08), rnd.uniform(-0.07, 0.07), 0)), rnd.uniform(0.006, 0.012)) for _ in range(5)]
    ctr = o.data.vertices[0].co.copy()
    for v in o.data.vertices:
        for dc, depth in dents:
            d = ((v.co - ctr).xy - dc.xy).length
            if d < 0.04 and v.co.z > ctr.z - 0.06: v.co.z -= depth * (1 - d / 0.04) ** 2
    lathe(f"{name}rv", [(0.0, 0.0), (0.012, 0.0), (0.009, 0.006), (0.0, 0.008)], (c[0], c[1] + 0.012 + 0.096, c[2] + 0.008), m, 16, tilt=tilt)
    leather = mat_once("leather", lambda: worn("leather", "#5a3418", "#2a160a", 0.6, 0.0, 30, 0.7, "#3a2010"))
    tube(f"{name}strap", [(c[0] - 0.1, c[1] + 0.03, c[2] - 0.02), (c[0] - 0.16, c[1] + 0.004, c[2] - 0.12), (c[0] - 0.08, c[1] + 0.003, c[2] - 0.24),
                          (c[0] + 0.05, c[1] + 0.003, c[2] - 0.22), (c[0] + 0.12, c[1] + 0.004, c[2] - 0.12), (c[0] + 0.1, c[1] + 0.03, c[2] - 0.02)], 0.006, leather, bres=1)
    for sd in (-1, 1): bx(f"{name}buck{sd}", (c[0] + sd * 0.14, c[1] + 0.006, c[2] - 0.17), (0.022, 0.004, 0.026), brass(), 0.002, 0.4 * sd)
    return o
def shell_casing(name, c, r=0.022, h=0.16, lying=False, yaw=0.0):
    prof = [(0.0, 0.0), (r * 1.15, 0.0), (r * 1.15, 0.008), (r, 0.012), (r, h * 0.7), (r * 0.9, h * 0.8), (r * 0.9, h), (r * 0.8, h), (0.0, h * 0.4)]
    tilt = Matrix.Rotation(math.radians(90), 3, "Z") if lying else None
    return lathe(name, prof, (c[0], c[1] + (r * 1.15 if lying else 0), c[2]), brass(), 28, yaw=yaw, cap=False, tilt=tilt)
def letters(name, c, yaw, n=4, string=True):
    pap = pmat("kenv", "#e8dcc0", 0.85)
    for k in range(n):
        bx(f"{name}{k}", (c[0] + k * 0.006, c[1] + 0.002 + k * 0.003, c[2] - k * 0.004), (0.2, 0.003, 0.11), pap, 0.001, yaw + k * 0.07)
    bx(f"{name}st", (c[0] + 0.05, c[1] + 0.003 + n * 0.003, c[2] + 0.02), (0.03, 0.001, 0.035), pmat("kstamp", "#a83a2a", 0.7), 0, yaw)
    if string:
        bx(f"{name}s1", (c[0] + 0.01, c[1] + 0.004 + n * 0.003, c[2] - 0.006), (0.205, 0.003, 0.006), pmat("ktwine", "#a8946a", 0.9), 0, yaw)
        bx(f"{name}s2", (c[0] + 0.01, c[1] + 0.004 + n * 0.003, c[2] - 0.006), (0.006, 0.003, 0.115), pmat("ktwine", "#a8946a", 0.9), 0, yaw)
    text("Mrs. E. Hart", (c[0] - 0.02, c[1] + 0.004 + n * 0.003, c[2] - 0.03), 0.016, ink(), yaw=yaw)
def photo(name, c, yaw):
    bx(f"{name}", (c[0], c[1] + 0.002, c[2]), (0.11, 0.003, 0.14), pmat("kphb", "#f0e8d4", 0.7), 0.001, yaw)
    bx(f"{name}i", (c[0], c[1] + 0.0036, c[2] + 0.006), (0.09, 0.001, 0.105), mat_once("ksepia", lambda: sepia()), 0, yaw)
def sepia():
    m = lib.principled("ksepia", lib.hexc("#8a6a48"), 0.5); t, n, l = lib.nodes(m)
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    r = lib.ramp(n, l, nz.outputs["Fac"], [(0.35, lib.hexc("#3a2818")), (0.55, lib.hexc("#9a7a54")), (0.7, lib.hexc("#d8c098"))])
    l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"]); return m
def medal(name, c, yaw, ribbon="#b82a2a", ribbon2="#e8d8b0"):
    bx(f"{name}r", (c[0], c[1] + 0.002, c[2] + 0.04), (0.035, 0.003, 0.05), pmat("krib" + ribbon, ribbon, 0.8), 0.001, yaw)
    bx(f"{name}r2", (c[0], c[1] + 0.0035, c[2] + 0.04), (0.008, 0.001, 0.05), pmat("krib" + ribbon2, ribbon2, 0.8), 0, yaw)
    bz = pmat("kbronze", "#a8743a", 0.35, 1.0)
    for k in range(2): bx(f"{name}x{k}", (c[0], c[1] + 0.004, c[2]), (0.05 if k == 0 else 0.016, 0.004, 0.016 if k == 0 else 0.05), bz, 0.002, yaw)
    cy(f"{name}c", (c[0], c[1] + 0.006, c[2]), 0.012, 0.003, bz, 16)
def whistle(name, c, yaw):
    o = cy(f"{name}", (c[0], c[1] + 0.011, c[2]), 0.011, 0.075, brass(), 16); o.rotation_euler = (0, math.radians(90), yaw)
    tube(f"{name}ch", [(c[0] + 0.04 * math.cos(yaw), c[1] + 0.01, c[2] - 0.04 * math.sin(yaw)), (c[0] + 0.09, c[1] + 0.003, c[2] - 0.05), (c[0] + 0.15, c[1] + 0.003, c[2] + 0.01)], 0.002, pmat("ksteel", "#8a8a8a", 0.3, 1.0), bres=1)
def barbed_coil(name, c, L, r, axis_yaw, mat, turns=9):
    """concertina wire coil lying on its side, with barbs"""
    pts = []; cw, sw = math.cos(axis_yaw), math.sin(axis_yaw)
    for k in range(turns * 10 + 1):
        a = k / 10 * math.tau; u = k / (turns * 10) * L - L / 2
        lx, ly, lz = u, r + r * math.sin(a), r * math.cos(a)
        pts.append((c[0] + lx * cw + lz * sw, c[1] + ly, c[2] - lx * sw + lz * cw))
    o = tube(name, pts, r * 0.025, mat, res=4, bres=1)
    for k in range(0, len(pts), 4):
        p = pts[k]; tube(f"{name}b{k}", [(p[0] - r * 0.12, p[1] + r * 0.05, p[2]), (p[0] + r * 0.12, p[1] - r * 0.05, p[2] + r * 0.06)], r * 0.02, mat, res=2, bres=0)
    return o
def chair(name, c, yaw, wood, seat):
    cw, sw = math.cos(yaw), math.sin(yaw); P = lambda lx, ly, lz: (c[0] + lx * cw + lz * sw, c[1] + ly, c[2] - lx * sw + lz * cw)
    for sx in (-1, 1):
        for sz in (-1, 1): cy(f"{name}l{sx}{sz}", P(sx * 0.2, 0.22, sz * 0.2), 0.022, 0.44, wood, 10)
        cy(f"{name}p{sx}", P(sx * 0.2, 0.7, 0.2), 0.022, 0.5, wood, 10)
    bx(f"{name}s", P(0, 0.47, 0), (0.48, 0.07, 0.46), seat, 0.025, yaw)
    bx(f"{name}b", P(0, 0.86, 0.21), (0.44, 0.18, 0.035), wood, 0.01, yaw)
    for k in (-1, 0, 1): bx(f"{name}sl{k}", P(k * 0.12, 0.66, 0.21), (0.03, 0.26, 0.025), wood, 0.005, yaw)
def phone(name, c, yaw):
    blk = pmat("kbakelite", "#141214", 0.15)
    lathe(f"{name}b", [(0.0, 0), (0.07, 0), (0.07, 0.02), (0.03, 0.035), (0.0, 0.035)], c, blk, 28)
    lathe(f"{name}s", [(0.012, 0.03), (0.012, 0.26), (0.0, 0.26)], c, blk, 12)
    lathe(f"{name}m", [(0.0, 0.25), (0.025, 0.25), (0.035, 0.29), (0.0, 0.3)], c, blk, 20, tilt=Matrix.Rotation(math.radians(-30), 3, "X"))
    tube(f"{name}hk", [(c[0], c[1] + 0.2, c[2]), (c[0] - 0.04, c[1] + 0.2, c[2]), (c[0] - 0.05, c[1] + 0.22, c[2])], 0.004, brass())
    o = cy(f"{name}r", (c[0] - 0.06, c[1] + 0.15, c[2]), 0.016, 0.13, blk, 14)
    lathe(f"{name}ec", [(0.0, 0.0), (0.03, 0.0), (0.032, 0.02), (0.0, 0.03)], (c[0] - 0.06, c[1] + 0.07, c[2]), blk, 18)
    tube(f"{name}cord", [(c[0] + 0.05, c[1] + 0.01, c[2]), (c[0] + 0.15, c[1] + 0.003, c[2] + 0.05), (c[0] + 0.22, c[1] + 0.003, c[2] - 0.08), (c[0] + 0.3, c[1] + 0.003, c[2] + 0.02)], 0.005, pmat("kcord", "#3a2a1e", 0.7))
def banker_lamp(name, c, yaw, energy=18):
    lathe(f"{name}b", [(0.0, 0), (0.11, 0), (0.11, 0.02), (0.05, 0.035), (0.0, 0.035)], c, brass(), 32)
    lathe(f"{name}st", [(0.012, 0.03), (0.012, 0.32), (0.0, 0.32)], c, brass(), 12)
    gm = mat_once("kgreenglass", lambda: lib.principled("kgreenglass", lib.hexc("#1a6a3a"), 0.12, 0.0, (0.2, 0.8, 0.4), 0.6))
    o = cy(f"{name}sh", (c[0], c[1] + 0.36, c[2]), 0.075, 0.36, gm, 24, rot=(0, math.radians(90), yaw)); o.scale.z = 0.6
    lib.light("AREA", T(c[0], c[1] + 0.31, c[2]), energy, (1.0, 0.75, 0.45), 0.2, (0, 0, 0))
def typewriter(name, c, yaw):
    blk = pmat("kbakelite", "#141214", 0.15); cw, sw = math.cos(yaw), math.sin(yaw); P = lambda lx, ly, lz: (c[0] + lx * cw + lz * sw, c[1] + ly, c[2] - lx * sw + lz * cw)
    bx(f"{name}b", P(0, 0.05, 0), (0.42, 0.1, 0.3), blk, 0.03, yaw); bx(f"{name}t", P(0, 0.12, 0.08), (0.36, 0.08, 0.14), blk, 0.03, yaw)
    o = cy(f"{name}pl", P(0, 0.17, 0.1), 0.03, 0.5, pmat("krubber", "#1a1a1a", 0.8), 16); o.rotation_euler = (0, math.radians(90), yaw)
    bx(f"{name}pp", P(0, 0.26, 0.12), (0.26, 0.2, 0.003), pmat("kpaper", "#f0e6cc", 0.8), 0, yaw)
    for r in range(3):
        for k in range(10): cy(f"{name}k{r}{k}", P(-0.15 + k * 0.033 + r * 0.01, 0.1 + r * 0.012, -0.12 + r * 0.035), 0.011, 0.012, pmat("kkey", "#e8e0d0", 0.4), 10)
def wall_clock(name, c, label):
    lathe(f"{name}", [(0.0, 0.0), (0.24, 0.0), (0.25, 0.03), (0.22, 0.06), (0.0, 0.06)], c, wood_mat("kclock", "#5a2a12", "#2a1006", 10, 0.3), 36, tilt=Matrix.Rotation(math.radians(-90), 3, "X"))
    cy(f"{name}f", (c[0], c[1], c[2] - 0.062), 0.2, 0.004, pmat("kdial", "#efe4c8", 0.5), 36, rot=(math.radians(90), 0, 0), bev=0)
    for k in range(12):
        a = k / 12 * math.tau; bx(f"{name}m{k}", (c[0] + 0.17 * math.sin(a), c[1] + 0.17 * math.cos(a), c[2] - 0.066), (0.012, 0.03, 0.002), ink(), 0, 0)
    rnd = random.Random(hash(label) % 1000)
    for k, (L, w) in enumerate(((0.1, 0.012), (0.15, 0.008))):
        a = rnd.random() * math.tau
        o = bx(f"{name}h{k}", (c[0] + L / 2 * math.sin(a), c[1] + L / 2 * math.cos(a), c[2] - 0.07 - k * 0.003), (w, L, 0.003), ink(), 0)
        o.rotation_euler = (0, -a, 0)
    bx(f"{name}pl", (c[0], c[1] - 0.33, c[2] - 0.02), (0.3, 0.07, 0.01), brass(), 0.004)
    text(label, (c[0], c[1] - 0.345, c[2] - 0.03), 0.04, ink(), flat=False)
def rake(name, c, yaw, L=1.1):
    wd = wood_mat("krake", "#a87a4a", "#6a4a2a", 20, 0.4)
    p1 = (c[0] + L * math.cos(yaw), c[1] + 0.012, c[2] - L * math.sin(yaw))
    tube(f"{name}", [(c[0], c[1] + 0.012, c[2]), p1], 0.009, wd, bres=1)
    bx(f"{name}t", (c[0], c[1] + 0.015, c[2]), (0.025, 0.03, 0.22), wd, 0.004, yaw)

def build(M, D):
    random.seed(1918)
    S = bpy.context.scene; bg = S.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.01, 0.012, 0.02, 1); bg.inputs[1].default_value = 1.0
    FL = lib.parquet("wrfloor", "#6a4228", "#4a2c18"); WL = lib.wallpaper("wrwall", "#5a2a24", "#6a3430"); WD = lib.wood("wrwood", "#4a2814", "#22120a", 5, 0.35)
    PN = lib.wood("wrpanel", "#3a1e0e", "#1a0c06", 4, 0.4)
    bx("floor", (0, -0.05, -1), (17, 0.1, 15), FL, 0)
    bx("rug", (0, 0.004, 1), (6.4, 0.012, 4.6), lib.carpet("wrrug", "#6a1418", "#c8a24a"), 0.003)
    bx("ceil", (0, 4.05, -1), (17, 0.1, 15), lib.plaster("wrceil", "#3a3430"), 0)
    for k in range(5): bx(f"beam{k}", (0, 3.9, -6 + k * 3), (17, 0.2, 0.25), WD, 0.02)
    bx("back", (0, 2, 6.15), (17, 4, 0.3), WL, 0)
    for sx in (-1, 1): bx(f"side{sx}", (sx * 8.15, 2, -1), (0.3, 4, 15), WL, 0)
    bx("wains", (0, 0.55, 5.96), (16, 1.1, 0.08), PN, 0.01); bx("wrail", (0, 1.12, 5.92), (16, 0.06, 0.12), PN, 0.01)
    for sx in (-1, 1):
        bx(f"wains{sx}", (sx * 7.96, 0.55, -1), (0.08, 1.1, 15), PN, 0.01); bx(f"wrail{sx}", (sx * 7.92, 1.12, -1), (0.12, 0.06, 15), PN, 0.01)
    # ---------- the map table: heavy legs, apron, brass corners, the map ----------
    bx("ttop", (0, 0.92, 1), (4.3, 0.06, 2.7), WD, 0.02)
    bx("tapron", (0, 0.78, 1), (4.1, 0.22, 2.5), WD, 0.02)
    for sx in (-1, 1):
        for sz in (-1, 1): lathe(f"tleg{sx}{sz}", [(0.0, 0.0), (0.1, 0.0), (0.07, 0.1), (0.05, 0.3), (0.09, 0.45), (0.06, 0.55), (0.08, 0.68), (0.0, 0.68)], (sx * 1.9, 0, 1 + sz * 1.1), WD, 20)
    map_plane("map", -1.95, 1.95, -0.2, 2.2, Y, map_mat("wrmap", "map_table.png", 0.45))
    for sx in (-1, 1):
        for sz in (-0.2, 2.2): bx(f"corner{sx}{sz}", (sx * 1.95, 0.955, sz), (0.12, 0.012, 0.12), brass(), 0.003)
    # ---------- the WW1 still life round the helmet (Flanders): helmet, letters, photo, medal, whistle, casings, wire ----------
    helmet("helmet", (1.2, Y, 1.7))
    letters("let", (1.55, Y, 1.5), 0.5)
    photo("ph", (0.82, Y, 1.92), -0.25)
    medal("med", (0.93, Y, 1.5), 0.3)
    whistle("wh", (1.48, Y, 1.95), 2.6)
    for k, (x, z, yw) in enumerate(((0.95, 1.72, 0.4), (1.02, 1.36, 1.9), (1.62, 1.82, 2.8))): shell_casing(f"cas{k}", (x, Y, z), 0.008, 0.06, True, yw)
    shell_casing("shell", (1.72, Y, 2.08), 0.04, 0.3)
    barbed_coil("wire", (0.6, Y, 2.05), 0.6, 0.05, 0.25, pmat("kwire", "#5a5650", 0.45, 0.9), 20)
    pocket_watch("watch", (1.75, Y, 1.62), 2.0)
    candle("cand", (1.85, Y, 2.12), 0.14, 11, 0.6)
    # ---------- general staff clutter across the map ----------
    for k, (x, z, yw, col) in enumerate(((0.15, 1.6, 0.3, "#6a6e64"), (0.0, 1.45, 0.1, "#6a6e64"), (-0.45, 1.7, 3.0, "#7a3a2a"), (-0.6, 1.4, 3.2, "#7a3a2a"),
                                         (-1.35, 1.05, 2.4, "#b0a040"), (-1.5, 1.3, 2.2, "#b0a040"), (0.35, 0.75, 1.2, "#5a6a3a"))):
        toy_tank(f"tt{k}", (x, Y, z), yw, col, 1.0)
    for k, (x, z, yw) in enumerate(((1.4, 0.9, 0.4), (1.1, 0.4, 0.6), (-1.75, 0.2, 2.0), (-1.2, 0.5, 2.6), (-0.9, -0.05, 2.2))): toy_ship(f"ts{k}", (x, Y, z), yw, 0.22, "#6a7280" if k < 2 else "#6a6e78")
    pins = [(0.05, 1.55, "#3a3a3a"), (-0.2, 1.62, "#b02a2a"), (-0.55, 1.85, "#b02a2a"), (-1.3, 1.25, "#e8c040"), (-1.45, 0.75, "#e8c040"), (0.6, 1.3, "#2a4a9a"),
            (-0.3, 0.9, "#2a7a3a"), (0.2, 1.1, "#2a4a9a"), (-1.0, 0.85, "#e8c040"), (-0.85, 1.55, "#b02a2a")]
    for k, (x, z, col) in enumerate(pins): pin_flag(f"pf{k}", (x, Y, z), col, 0.1)
    red = pmat("kstring", "#c01e22", 0.6)
    for a_, b_ in ((0, 1), (1, 2), (3, 4), (4, 8), (5, 7)):
        p, q = pins[a_], pins[b_]; tube(f"str{a_}{b_}", [(p[0], Y + 0.06, p[1]), ((p[0] + q[0]) / 2, Y + 0.05, (p[1] + q[1]) / 2), (q[0], Y + 0.06, q[1])], 0.0018, red, bres=1)
    for k, (x, z, yw, col) in enumerate(((0.4, 1.75, 0.1, "#5a5e58"), (-0.05, 1.85, 0.2, "#5a5e58"), (-0.75, 1.15, 0.0, "#8a3a2a"), (-1.6, 0.95, 0.3, "#b8a040"), (0.75, 0.95, 0.2, "#3a4a8a"))):
        unit_block(f"ub{k}", (x, Y, z), yw, col)
    rake("rake1", (-0.9, Y, -0.05), 0.5, 1.0); rake("rake2", (1.6, Y, 0.0), 2.4, 0.9)
    for k in range(4): bx(f"pap{k}", (-1.55 + k * 0.04, Y + 0.002 + k * 0.002, 0.15), (0.24, 0.002, 0.32), pmat("kpaper", "#f0e6cc", 0.8), 0, 0.2 * k)
    text("SECRET", (-1.45, Y + 0.012, 0.12), 0.04, pmat("kred", "#a81e22", 0.5), yaw=0.6)
    compass("comp", (0.6, Y, 0.1), 0.06); dividers("div", (0.15, Y, 0.0), 0.3, 0.2); magnifier("mag", (0.95, Y, 0.45), 2.8)
    cup("cup", (-1.75, Y, 1.95)); cup("cup2", (1.85, Y, -0.05))
    lathe("ash", [(0.0, 0.0), (0.07, 0.0), (0.08, 0.025), (0.065, 0.025), (0.055, 0.008), (0.0, 0.008)], (-1.72, Y, 1.55), glassm(), 32)
    cig = tube("cigar", [(-1.68, Y + 0.03, 1.55), (-1.55, Y + 0.012, 1.5)], 0.009, pmat("kcigar", "#5a3218", 0.8))
    lathe("cigtip", [(0.0, 0.0), (0.009, 0.0), (0.0, 0.004)], (-1.555, Y + 0.012, 1.5), lib.emit("ember", (1.0, 0.35, 0.08), 8), 10, tilt=Matrix.Rotation(math.radians(80), 3, "Z"))
    tube("smoke1", [(-1.55, Y + 0.02, 1.5), (-1.53, Y + 0.15, 1.52), (-1.58, Y + 0.3, 1.47), (-1.52, Y + 0.45, 1.5), (-1.56, Y + 0.6, 1.55)], 0.006, smoke_mat("wrsmoke", "#c8c0b8", 0.35))
    phone("phone", (1.8, Y - 0.002 + 0.006, 0.55), 0.4)
    # ---------- the room: bookcases, framed world map, night windows, clocks, desk corner, filing cabinets, chairs ----------
    for sx in (-1, 1): bookcase(f"shelf{sx}", (sx * 5, 0, 5.75), 3.0, 2.7, 0.4, 5, WD, seed=4 + sx)
    wm = map_mat("wallmap", "map_world.png", 0.5)
    me = bpy.data.meshes.new("wallmap"); me.from_pydata([T(1.2, 2.0, 5.97), T(-1.2, 2.0, 5.97), T(-1.2, 3.2, 5.97), T(1.2, 3.2, 5.97)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for k, cc in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = cc
    o = link(bpy.data.objects.new("wallmap", me)); me.materials.append(wm)
    bx("framemapf", (0, 2.6, 6.0), (2.6, 1.4, 0.05), lib.gilt(), 0.02)
    for sx in (-1, 1): window(f"win{sx}", (sx * 2.6, 1.3, 6.0), 0.9, 2.0, (0.3, 0.45, 1.0), 2.5)
    for x_, lab in ((-1.6, "LONDON"), (0, "BERLIN"), (1.6, "TOKYO")): wall_clock(f"clk{lab}", (x_, 3.55, 5.97), lab)
    for x_ in (-3.8, 3.8, -6.6, 6.6): sconce(f"sc{x_}", (x_, 2.4, 6.0), 70)
    # desk corner (seen past the helmet): desk, banker's lamp, typewriter, radio, filing cabinets, coat stand
    bx("desk", (5.6, 0.76, 3.4), (1.8, 0.06, 0.9), WD, 0.02)
    for sx in (-1, 1): bx(f"deskped{sx}", (5.6 + sx * 0.7, 0.37, 3.4), (0.4, 0.74, 0.86), WD, 0.02)
    banker_lamp("blamp", (5.0, 0.79, 3.55), 0.2, 25); typewriter("tw", (5.8, 0.79, 3.35), 0.15)
    book("dbk", (6.3, 0.79, 3.6), (0.26, 0.06, 0.2), "#6a1e1e", 0.3)
    bx("radio", (7.4, 1.6, 4.6), (0.55, 0.38, 0.3), wood_mat("kradio", "#6a3a1a", "#2a140a", 9, 0.3), 0.04, -0.5)
    bx("rdial", (7.33, 1.66, 4.46), (0.28, 0.1, 0.01), lib.emit("wrdial", (1.0, 0.65, 0.25), 6), 0.005, -0.5)
    bx("radioshelf", (7.6, 1.38, 4.6), (0.6, 0.05, 0.6), WD, 0.01)
    for k in range(2):
        z_ = 1.6 + k * 0.75
        bx(f"file{k}", (7.6, 0.7, z_), (0.6, 1.4, 0.7), worn(f"filecab{k}", "#5a6050", "#2a2a26", 0.5, 0.5, 30, 0.7), 0.01)
        for d_ in range(4):
            bx(f"fd{k}{d_}", (7.29, 0.25 + d_ * 0.33, z_), (0.02, 0.28, 0.6), pmat("kfiledr", "#646a58", 0.45, 0.5), 0.005)
            bx(f"fh{k}{d_}", (7.27, 0.33 + d_ * 0.33, z_), (0.02, 0.025, 0.14), brass(), 0.003)
    lathe("coatst", [(0.0, 0.0), (0.25, 0.0), (0.03, 0.05), (0.025, 1.85), (0.04, 1.9), (0.0, 1.92)], (-6.8, 0, 4.8), WD, 16)
    tube("coat", [(-6.8, 1.78, 4.8), (-6.62, 1.5, 4.72), (-6.6, 0.9, 4.75), (-6.7, 0.5, 4.7)], 0.17, mat_once("kgreatcoat", lambda: lib.cloth("kgreatcoat", "#4a4a2e")), taper=lambda f: 0.6 + f * 0.6)
    lathe("cap", [(0.0, 0.0), (0.16, 0.0), (0.16, 0.02), (0.12, 0.08), (0.0, 0.09)], (-6.7, 1.88, 4.85), mat_once("kcapc", lambda: lib.cloth("kcapc", "#4a4a2e")), 24)
    seat = mat_once("kseat", lambda: lib.cloth("kseat", "#6a1e18"))
    for k, (x_, z_, yw) in enumerate(((-2.5, 0.6, 1.4), (2.5, 0.8, -1.5), (-1.0, -0.6, 0.1), (1.1, -0.65, -0.1), (5.6, 2.7, 0.1))): chair(f"ch{k}", (x_, 0, z_), yw, WD, seat)
    # ---------- light: the green-shaded lamp over the map (warm key), sconces, desk lamp, cool moonlight through the windows ----------
    cy("cord", (0, 3.3, 1), 0.008, 1.5, M["dark"], 6)
    lathe("lshade", [(0.07, 0.25), (0.5, 0.0), (0.52, -0.02), (0.08, 0.23)], (0, 2.35, 1), mat_once("klshade", lambda: worn("klshade", "#2a5a3a", "#1a2a1e", 0.35, 0.6, 20, 0.75)), 40, cap=False)
    lathe("lshadein", [(0.068, 0.248), (0.495, 0.0)], (0, 2.35, 1), lib.principled("lshin", lib.hexc("#f2ead0"), 0.6, 0.0, (1.0, 0.85, 0.6), 1.5), 40, cap=False)
    lathe("bulb", [(0.0, 0.18), (0.05, 0.13), (0.045, 0.08), (0.0, 0.06)], (0, 2.35, 1), M["bulb"], 20)
    sp = lib.light("SPOT", T(0, 2.45, 1), 1400, (1.0, 0.76, 0.48), 0.25); lib.look_at(sp, T(0, 0.9, 1)); sp.data.spot_size = math.radians(115); sp.data.spot_blend = 0.6
    lib.light("POINT", T(0, 2.75, 1), 40, (1.0, 0.75, 0.45), 0.2)
    for sx in (-1, 1):
        mo = lib.light("AREA", T(sx * 2.6, 2.3, 6.4), 140, (0.45, 0.6, 1.0), 1.2, size_y=2.2); lib.look_at(mo, T(sx * 1.2, 0.9, 1.5))
    bounce = lib.light("AREA", T(0, 3.8, 1), 220, (1.0, 0.7, 0.45), 6); bounce.rotation_euler = (0, 0, 0)
    for sx in (-1, 1):
        wl = lib.light("AREA", T(sx * 5, 3.6, 4.5), 120, (1.0, 0.72, 0.45), 2.5); lib.look_at(wl, T(sx * 5, 1.2, 5.9))
    rim = lib.light("AREA", T(4, 3, -5), 180, (0.55, 0.65, 1.0), 4); lib.look_at(rim, T(0, 1, 1))
    return {}
