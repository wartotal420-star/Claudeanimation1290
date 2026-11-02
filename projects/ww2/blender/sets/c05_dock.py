# Chapter 5: Lend-Lease, 1941: a New York pier. A cargo ship alongside, a dockside crane swinging a crate aboard, crates
# stencilled TANKS / FOOD / PLANES / U.S.A., a light tank waiting, warehouses with signs, the Statue of Liberty across
# the harbour, and a convoy steaming out to sea.
# Layout (three coords): the pier deck at y 0 for z < 8 (edge at z 8, water at y -2.5 beyond); the ship alongside,
# bow +x, centred (10, 0, 19) (its deck y 9 above the waterline: hull top at y 6.5 here); the crane at (-6, 0, 5);
# crate stacks at x -14..14, z -2..6 (keep x -4..4, z -1..3 clear for people); warehouses at z -14; the convoy far out
# at z 300..900; Liberty at (-420, 0, 700).
# The swinging crate (update): frames 2497-2600 rises from (-2, 0.6, 4) and swings over the ship's hold.
import bpy, math, random
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, sign, poster, glassm, barrel, stripes, R90
from .c05_kit import (sky, sea_mat, area, point, sun_light, lathe, tube, worn, mat_once, cached, cargo_ship, lattice_mast, truck, empty, loft_k)

def stencil_crate(K, c, s, label, yaw=0.0, col="#8a7448"):
    W = wood(col, "#5a4a2a", 10, 0.8); x, y, z = c
    K.box((x, y + s[1] / 2, z), s, W, yaw, 0.02)
    for dy in (0.15, s[1] - 0.15): K.box((x, y + dy, z), (s[0] + 0.03, 0.1, s[2] + 0.03), wood("#6a5432", "#3a2a14", 10, 0.8), yaw, 0.01)
    ca, sa = math.cos(yaw), math.sin(yaw)
    fz = -s[2] / 2 - 0.02
    text(label, (x + fz * sa, y + s[1] * 0.55, z + fz * ca), min(0.5, s[1] * 0.38), pm("#1a1a1a", 0.7), yaw, "sans", 0.003, fit=s[0] * 0.85)
    text("U.S.A.", (x + fz * sa, y + s[1] * 0.25, z + fz * ca), s[1] * 0.14, pm("#1a1a1a", 0.7), yaw, "sans", 0.002, fit=s[0] * 0.5)

def build(M, D):
    random.seed(1941); K_.reset(); rnd = random.Random(12); sid = D.get("id", 0)
    sky((0.2, 0.38, 0.68), (0.5, 0.62, 0.8), (0.86, 0.84, 0.8), sun_dir=(0.45, 0.55, -0.7), sun_col=(1.0, 0.82, 0.55), glow=0.7, clouds=0.9)
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, -2.5, 1500)); sea = bpy.context.object; sea.scale = (6000, 3000, 1); bpy.ops.object.transform_apply(scale=True)
    sea.data.materials.append(sea_mat("c5harb", "#24404e", "#3a6068", 0.08, 0.3))
    K = Kit("dock")
    DECK = wood("#6a5a48", "#3a3024", 3, 0.85); CONC = grime("c5conc", "#a8a090", 0.3)
    K.box((0, -0.25, -10), (120, 0.5, 36), DECK, 0, 0.0)
    K.box((0, -1.5, 7.9), (120, 2.2, 0.3), CONC, 0, 0.02)
    for k in range(40): K.cyl((-60 + k * 3, -2.0, 8.3), 0.25, 3.0, wood("#3a2e22", "#1e1812", 4, 0.9), 10)
    for k in range(12):                                         # bollards with mooring lines
        x = -30 + k * 6; K.cyl((x, 0.3, 7.2), 0.22, 0.6, pm("#2a2a2a", 0.4, 0.6), 14); K.cyl((x, 0.62, 7.2), 0.3, 0.06, pm("#2a2a2a", 0.4, 0.6), 14)
    for x, x2 in ((-18, -40), (30, 52)): tube(f"rope{x}", [(x, 0.5, 7.2), ((x + x2) / 2, 3.5, 11), (x2, 6.5, 12)], 0.05, pm("#c8b890", 0.8))
    for k in range(60): K.box((-60 + k * 2, 0.01, 6.6), (1.9, 0.02, 0.12), pm("#d8c830", 0.6), 0, 0.0)
    # warehouses with signs, a rail track in the deck, a gangway
    BR = K_.brick("c5whbrick", "#8a4a36", "#7a3e2e", "#4a3a34", 3.0)
    for k, (x, lab) in enumerate(((-24, "PIER 7"), (6, "U.S. LEND-LEASE  CARGO"), (34, "BETHLEHEM STEEL"))):
        K.box((x, 6, -20), (26, 12, 10), BR, 0, 0.05); K.box((x, 12.3, -20), (27, 0.6, 11), pm("#3a3a3a", 0.7), 0, 0.02)
        for j in range(3): K.box((x - 8 + j * 8, 2.6, -14.95), (5, 5.2, 0.1), pm("#3a4a3a", 0.6, 0.2), 0, 0.01)
        sign(K, (x, 8.6, -14.9), 14, 1.3, 0, lab, "#f0e8d0", pm("#1a1a1a", 0.6), "sans", None, 0.08)
        for j in range(5): K.box((x - 10 + j * 5, 10.5, -14.95), (2.0, 1.2, 0.05), pm("#1a2230", 0.08), 0, 0.0)
    for x in (-60, 60): K.box((0, 0.02, -6 + (x > 0) * 1.4), (120, 0.04, 0.08), pm("#7a7a80", 0.3, 0.9), 0, 0.0)
    # crate stacks
    LAB = ["TANKS", "FOOD", "PLANES", "TANKS", "FOOD", "SHELLS", "FOOD", "PLANES", "MEDICINE", "TRUCKS"]
    for k in range(10):
        x = -14 + (k % 5) * 6.5 + (0 if k < 5 else 2.0); z = 4.5 if k < 5 else -3.0
        if -4.5 < x < 4.5 and z > 0: x += 9
        stencil_crate(K, (x, 0, z), (2.4, 1.6, 1.6), LAB[k], rnd.uniform(-0.1, 0.1))
        if k % 2 == 0: stencil_crate(K, (x + 0.2, 1.6, z), (2.0, 1.3, 1.4), LAB[(k + 3) % 10], rnd.uniform(-0.1, 0.1), "#9a8458")
    for k in range(14):
        x, z = rnd.uniform(-30, 30), rnd.uniform(-8, 0)
        if abs(x) < 5: continue
        barrel(K, (x, 0.45, z), 0.3, 0.9, pm(("#3a4a3a", "#6a2a1e", "#2a3a5a")[k % 3], 0.5, 0.3), pm("#2a2a24", 0.5, 0.5))
    for k in range(8): K.box((18 + (k % 4) * 0.7, 0.3 + (k // 4) * 0.55, -1), (0.6, 0.55, 0.9), cloth("#c8b48a"), 0.1 * k, 0.12)
    # a light tank waiting to be loaded (M3 Stuart-like), US star on the side
    from .c05_kit import panzer
    P = panzer("stuart", (-24, 0, 1.5), 0.1, "#5a5a3a", False)
    for sd in (-1, 1):
        c = P(-0.4, 1.75, sd * 1.47)
        K.cyl(c, 0.42, 0.01, pm("#f0ece0", 0.6), 5, "z", None, 0.1)
    # the dockside crane: lattice tower, jib, cab; the hook and crate move in update()
    steel = mat_once("c5crane", lambda: worn("c5crane", "#3a3e44", "#6a3a22", 0.55, 0.6, 3, 0.7, "#2a2a2a"))
    lattice_mast(K, (-6, 0, 3), 16, 3.5, 2.2, steel, 6)
    K.box((-6, 17.0, 3), (3.4, 2.4, 3.0), steel, 0, 0.05); K.box((-4.25, 17.2, 3), (0.05, 1.2, 1.6), pm("#1a2230", 0.08), 0, 0.0)
    jib = Kit("jib"); lattice_mast(jib, (0, 0, 0), 24, 1.2, 0.5, steel, 8)
    jo = jib.build(); J = empty("jib")
    for o in jo: o.parent = J
    HOOK = empty("hook"); hk = Kit("hookk"); hk.cyl((0, 0, 0), 0.25, 0.4, pm("#c8a020", 0.4, 0.5), 12); hk.box((0, -0.5, 0), (0.08, 0.6, 0.08), steel, 0, 0.0)
    before = set(bpy.data.objects.keys())
    stencil_crate(hk, (0, -2.6, 0), (3.0, 1.8, 1.8), "TANKS")
    for o in hk.build(): o.parent = HOOK
    for nm in set(bpy.data.objects.keys()) - before:
        o = bpy.data.objects[nm]
        if o.type == "FONT": o.parent = HOOK
    cable = []
    for k in range(10):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.0); o = bpy.context.object; o.data.materials.append(pm("#1a1a1a", 0.5, 0.6)); cable.append(o)
    # the ship alongside and the convoy far out; Liberty across the water
    cargo_ship("lship", 10, 19.5, 0.0, 134, 17, "#5a6068", "#c8c4b8", rust=True)
    for k, (x, z, yw) in enumerate(((-200, 420, 0.25), (80, 520, 0.2), (300, 640, 0.15), (-60, 780, 0.2), (180, 900, 0.18))):
        cargo_ship(f"conv{k}", x, z, yw + R90 * 0.0, 134, 17, ("#5a6068", "#4a5058", "#6a6a6a")[k % 3], "#b8b4a8", deck_cargo=False)
    LB = mat_once("c5liberty", lambda: worn("c5liberty", "#6a9a8a", "#4a7a6a", 0.6, 0.2, 2, 0.6))
    lx, lz = -420, 700
    K.box((lx, 15, lz), (40, 30, 40), grime("c5ped", "#b8b0a0", 0.3), 0.3, 0.2)
    lathe("lib_body", [(0.0, 30), (6.0, 30), (7.0, 45), (5.0, 60), (3.2, 72), (2.5, 76), (0.0, 78)], (lx, 0, lz), LB, 16)
    K.sphere((lx, 81, lz), 3.0, LB, 12); K.cyl((lx, 84, lz), 3.5, 1.2, LB, 14, "y", 2.0)
    tube("lib_arm", [(lx + 3, 70, lz), (lx + 5, 85, lz), (lx + 5.5, 96, lz)], 1.0, LB)
    K.cyl((lx + 5.5, 98.5, lz), 1.3, 3.0, LB, 10); K.sphere((lx + 5.5, 101, lz), 1.0, K_.gold(), 8)
    for k in range(30): K.box((rnd.uniform(-800, 600), rnd.uniform(5, 30) / 2, rnd.uniform(1400, 1800)), (rnd.uniform(20, 60), rnd.uniform(5, 30), 20), grime("c5far", "#8a8a90", 0.2), 0, 0.0)
    # tugboat
    K.box((40, 0.5, 60), (14, 3, 5), pm("#2a2a2a", 0.6), 0.3, 0.6); K.box((38, 3.0, 60), (6, 2.5, 4), pm("#b81e1a", 0.5), 0.3, 0.1); K.cyl((36.5, 5.5, 60.5), 0.8, 3, pm("#1a1a1a", 0.5), 12)
    K.build()
    sun_light((-0.45, -0.55, 0.7), 4.5, (1.0, 0.88, 0.7), 1.0)
    area((0, 20, -30), (0, 2, 5), 6000, (0.65, 0.75, 1.0), 30)
    from mathutils import Vector
    base = Vector((-6.0, 18.2, 3.0))
    def update(f):
        u = max(0.0, min(1.0, (f - 2505) / 80.0)); u = u * u * (3 - 2 * u)
        ang = 0.5 + 1.15 * u                                  # the jib slews from over the pier toward the ship's hold
        el = math.radians(28); L = 24.0
        tip = base + Vector((L * math.cos(el) * math.sin(ang), L * math.sin(el), L * math.cos(el) * math.cos(ang)))
        d = T(*tip) - T(*base)
        J.location = T(*base); J.rotation_mode = "QUATERNION"; J.rotation_quaternion = d.to_track_quat("Z", "Y")
        hy = 0.6 + 2.6 + 9.0 * min(1.0, max(0.0, (f - 2497) / 25.0)) + 0.3 * math.sin(f * 0.15)
        HOOK.location = T(tip.x, hy, tip.z)
        for k, o in enumerate(cable):
            seg = (tip.y - hy) / 10; o.location = T(tip.x, tip.y - seg * (k + 0.5), tip.z); o.scale = (1, 1, seg)
    update(2497)
    return {"update": update}
