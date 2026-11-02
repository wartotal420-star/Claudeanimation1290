# Chapter 5: the Battle of Britain sky, summer 1940. Waves of He 111 bombers with Bf 109 escorts fly north (-z) over
# the white cliffs; Spitfires dive through them; a burning bomber falls trailing smoke. Planes move per frame (update).
# Layout (three coords): the planes fly at y ~0 (1800 m up); farmland below at y -1800 for z < 0, the Channel for
# z > 0, the chalk cliffs along z = 0; cumulus heaps at y -260..+140 between x -900..900, z -2000..900.
# Shot 6 (frames 502-645): the formation's lead bomber at (0, 0, -VB * (f - 502)), VB = 2.4 m/frame along -z; the
#   camera tracks at the same speed (ch05.ts). Spitfires dive through between frames 585 and 645.
# Shot 10 (frames 980-1035): a stricken bomber falls from (20, 30, -40) trailing black smoke; a Spitfire pulls past.
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em
from .c05_kit import (spitfire, bf109, he111, clone, show, pose, sky, cloud_mat, cumulus, fields_mat, sea_mat, sun_light, area, smoke_mat,
                      height_mesh, ground_mat, flame_mat, lathe, mat_once)
VB = 2.4

def build(M, D):
    random.seed(1940); K_.reset(); rnd = random.Random(15); sid = D.get("id", 0)
    sky((0.12, 0.3, 0.68), (0.36, 0.56, 0.85), (0.78, 0.84, 0.92), sun_dir=(-0.45, 0.6, -0.5), sun_col=(1.0, 0.88, 0.6), glow=0.8, disc=30.0, clouds=0.6)
    # ---------------- far below: England, the cliffs, the Channel ----------------
    G = -650.0
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, G, -9000)); land = bpy.context.object; land.scale = (40000, 18000, 1); bpy.ops.object.transform_apply(scale=True)
    land.data.materials.append(fields_mat())
    bpy.ops.mesh.primitive_plane_add(size=1, location=T(0, G - 40, 9000)); sea = bpy.context.object; sea.scale = (40000, 18000, 1); bpy.ops.object.transform_apply(scale=True)
    sea.data.materials.append(sea_mat("c5sea", "#1a3a58", "#2a5872", 0.1, 0.02))
    K = Kit("cliffs"); chalk = pm("#ece8dc", 0.8); turf = pm("#5a7a3a", 0.9)
    for k in range(80):
        x = -8000 + k * 200; z = 60 * math.sin(k * 0.7) + 40 * math.sin(k * 1.9)
        K.box((x, G - 20, z), (205, 44, 30), chalk, 0.15 * math.sin(k), 0.0)
        K.box((x, G + 1.5, z - 18), (205, 3, 10), turf, 0.15 * math.sin(k), 0.0)
        K.box((x, G - 41, z + 40), (205, 1, 60), pm("#d8ccb0", 0.8), 0.15 * math.sin(k), 0.0)
    K.build()
    # ---------------- clouds ----------------
    cm = cloud_mat("c5cloud", "#ffffff", "#8a9ab8", 0.95); C = Kit("clouds")
    for k in range(46):
        x, z = rnd.uniform(-1100, 1100), rnd.uniform(-2200, 900)
        if abs(x) < 90 and -600 < z < 300: x += 180 * (1 if x > 0 else -1)
        y = rnd.choice((-200, -170, -140, -110, 90, 140)) + rnd.uniform(-20, 20)
        cumulus(C, (x, y, z), rnd.uniform(60, 160), rnd.uniform(30, 70), rnd, cm, 9)
    for k in range(45):                       # the low deck far below, catching the sun
        x, z = rnd.uniform(-2500, 2500), rnd.uniform(-3000, 2000)
        cumulus(C, (x, G + 220 + rnd.uniform(-30, 30), z), rnd.uniform(120, 260), 50, rnd, cm, 6)
    C.build()
    # ---------------- aircraft ----------------
    he = he111("he0"); bf = bf109("bf0"); sp = spitfire("sp0", "QV", "K"); sp2 = spitfire("sp1", "LE", "D", col=("#3e5228", "#6a5a36", "#a8b8a8"))
    bombers = [he] + [clone(he, f"he{k}") for k in range(1, 15)]
    escorts = [bf] + [clone(bf, f"bf{k}") for k in range(1, 6)]
    FORM = [(0, 0, 0), (-26, -2, 18), (26, -3, 18), (-52, -4, 36), (52, -5, 36),                       # first wave (vics)
            (-14, 30, 160), (14, 28, 175), (-40, 26, 190), (40, 27, 190), (0, 25, 205),               # second wave, higher
            (-30, 60, 330), (10, 58, 340), (50, 57, 355), (-70, 56, 360), (30, 55, 370)]                # third wave
    ESC = [(-60, 70, -20), (-30, 76, -35), (70, 66, 10), (95, 72, 0), (-110, 90, 120), (120, 95, 140)]
    smm = smoke_mat("c5smoke", "#1e1a18", 0.75); trail = []
    fall0 = (20.0, 30.0, -40.0)
    def fall_pos(u):     # u = frames since 980
        return (fall0[0] + 0.6 * u + 6 * math.sin(u * 0.08), fall0[1] - 0.012 * u * u - 0.6 * u, fall0[2] - 1.6 * u)
    if sid == 10:
        sm2 = smoke_mat("c5smoke2", "#4a4440", 0.4); smm = smoke_mat("c5smoke", "#1a1614", 0.5)
        for k in range(36):
            u = k * 1.6; p = fall_pos(u); r = 1.6 + 0.09 * u + rnd.uniform(-0.3, 0.3)
            o = lib.blob(f"trail{k}", T(p[0] + rnd.uniform(-1, 1), p[1] + 1.0 + rnd.uniform(-1, 1), p[2] + 6), (r, r * 0.9, r * 1.2), smm if k % 3 else sm2, 0.5 * r, k)
            o.visible_shadow = False; trail.append((u, o))
        fl = flame_mat("c5fire", (1.0, 0.7, 0.2), (1.0, 0.25, 0.02), 25)
        from .void import flame
        for sd in (-1, 1):
            o = flame(f"hef{sd}", (sd * 3.7, 0.3, -1.0), 3.2, 0.55, fl, lean=0.0, seed=sd + 2); o.parent = bombers[0]
    sun_light((0.45, -0.6, 0.5), 5.0, (1.0, 0.92, 0.78), 1.0)
    def update(f):
        if sid == 10:
            u = f - 980
            for k, e in enumerate(bombers):
                if k == 0:
                    p = fall_pos(u); pose(e, p, math.pi + 0.1 + 0.004 * u, -0.25 - 0.004 * u, 0.5 + 0.035 * u)
                elif k < 5:
                    fx, fy, fz = FORM[k]; pose(e, (fx - 60, fy - 20, fz - 80 - VB * u), math.pi, 0.0, 0.0)
                else: show(e, False)
            for u0, o in trail: o.hide_render = u0 > u
            for k, e in enumerate(escorts): show(e, k < 2); pose(e, (-90 + 30 * k, 45 + 10 * k, 60 - 3.0 * u), math.pi - 0.2, 0.05, -0.4)
            pose(sp, (-40 + 3.2 * u, 12 + 0.2 * u, -10 - 1.2 * u), math.pi * 0.5 + 0.35, 0.05, -0.9); show(sp2, False)
            return
        t = f - 502
        for k, e in enumerate(bombers):
            fx, fy, fz = FORM[k]; bob = 0.6 * math.sin(f * 0.05 + k)
            pose(e, (fx, fy + bob, fz - VB * t), math.pi, 0.0, 0.02 * math.sin(f * 0.04 + k))
        for k, e in enumerate(escorts):
            ex, ey, ez = ESC[k]; pose(e, (ex + 3 * math.sin(f * 0.03 + k), ey, ez - VB * t), math.pi, 0.02, 0.15 * math.sin(f * 0.03 + k))
        # Spitfires dive through: from high on the right (+y, +x ahead) down across the formation
        for k, e in enumerate((sp, sp2)):
            u = max(-30, min(80, f - 585 - k * 10))
            p = (90 - 3.2 * u - k * 20, 120 - 2.3 * u - k * 8, -VB * t - 120 + 1.5 * u + k * 25)
            pose(e, p, -0.25 * math.pi + math.pi, -0.55, 0.6)
    update(502 if sid != 10 else 980)
    return {"update": update}
