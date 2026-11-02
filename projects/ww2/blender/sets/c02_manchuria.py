# Liutiaohu, Manchuria, the night of 18 September 1931 (chapter 2 shots 3-4). Layout (three coords, camera looks +z):
# the South Manchuria Railway runs along x on an embankment at z 6 (rail top y ~0.75), the charge sits on the near rail at
# x 0.4; a detonator plunger box at (1.55, 0, 3.3) with its wire to the charge. Officers stand at (-0.6, 0, 3.0) and
# (1.9, 0, 3.5) on a dirt track (z 1..5, |x| < 4, flat y 0). Kaoliang fields both sides of the track and beyond the
# rails; telegraph poles along z 7.6; a lamp-lit linesman's hut at (-4.5, 0, 4.2); the Chinese Beidaying barracks far
# off at (-18, 0, 70) with lit windows (what the officers point at in shot 4). Night: cool moon from +z/+x, warm
# hurricane lanterns by the officers; the blast (frame 424) flashes a light, and from then the near rail is broken,
# burning a little, smoke drifting.
import bpy, math, random
import lib
from lib import T, hexc
from sets import kit_sbpw as KS
from sets.kit_sbpw import pm, em, wood, cloth, gold, brass, iron, grime, paper, text, sign, poster, R90, cached, set_world
from sets import c02_kit as CK
from sets.c02_kit import Kit
from sets.void import fire, smoke_column, smoke_mat, tube

BOOM = 424
def build(M, D):
    random.seed(1931); KS.reset(); rnd = random.Random(918)
    K = Kit("manch"); KB = Kit("manchbroken")
    set_world((0.012, 0.016, 0.04), (0.05, 0.06, 0.1), 0.6, (0.01, 0.014, 0.04), (0.09, 0.1, 0.16))
    DIRT = CK.ground_mat("mdirt", "#4a3a2a", "#2e241a", 0.35); FIELD = CK.ground_mat("mfield", "#3a3220", "#221c12", 0.5)
    STALK = pm("#6a6a34", 0.7); STALK2 = pm("#7a6a3a", 0.7); LEAF = pm("#33421e", 0.75); LEAF2 = pm("#3e4a22", 0.75)
    HEAD = pm("#5a2014", 0.85); HEAD2 = pm("#6a2a18", 0.85)
    # ground: dirt track in front, fields everywhere else, a low embankment for the railway
    K.box((0, -0.05, 20), (160, 0.1, 140), FIELD, 0, 0)
    K.box((0, 0.002, 3.0), (60, 0.004, 5.5), DIRT, 0, 0)
    for k in range(40):
        x = rnd.uniform(-8, 8); z = rnd.uniform(0.8, 5.2); K.sphere((x, 0.0, z), rnd.uniform(0.04, 0.12), DIRT, 6, (1.4, 0.4, 1.0))
    for k in range(8): K.box((rnd.uniform(-6, 6), 0.006, rnd.uniform(1.5, 4.8)), (rnd.uniform(0.6, 1.5), 0.004, 0.09), pm("#2a2016", 0.9), rnd.uniform(-0.2, 0.2), 0)   # cart ruts
    K.box((0, 0.3, 6), (200, 0.6, 4.4), CK.ground_mat("membank", "#5a4a38", "#3a3024", 0.6), 0, 0.3)
    CK.rails(K, -100, 6, 100, 6, 0.6)
    # the charge on the near rail, plunger, wire
    cx = 0.4
    K.box((cx, 0.82, 6 - 0.72), (0.3, 0.12, 0.16), cloth("#8a7a5a"), 0, 0.02)
    for k in range(4): K.cyl((cx - 0.11 + k * 0.075, 0.83, 6 - 0.72), 0.03, 0.14, pm("#a83a2a", 0.6), 8, "z")
    pl = (1.55, 0, 3.3)
    K.box((pl[0], 0.14, pl[2]), (0.3, 0.28, 0.22), wood("#6a4a2a", "#3a2614", 10), 0, 0.01)
    K.cyl((pl[0], 0.42, pl[2]), 0.015, 0.3, pm("#2a2a2a", 0.4, 0.8), 8); K.box((pl[0], 0.57, pl[2]), (0.24, 0.04, 0.04), pm("#2a2a2a", 0.4, 0.8), 0, 0.01)
    text("DANGER", (pl[0], 0.16, pl[2] - 0.112), 0.045, pm("#e8d8b0", 0.6), 0, "sans", 0.001)
    tube("wire", [(pl[0], 0.1, pl[2] + 0.1), (1.2, 0.02, 4.3), (0.8, 0.05, 5.0), (0.55, 0.45, 5.2), (cx + 0.1, 0.8, 6 - 0.72)], 0.008, pm("#1a1a1a", 0.5))
    # kaoliang: tall stalks, drooping leaves, red seed heads; dense near the track, thinning into dark mass far off
    def stalk(x, z, h, y=0.0):
        lean = rnd.uniform(-0.08, 0.08)
        K.cyl((x, y + h / 2, z), 0.014, h, STALK if rnd.random() < 0.6 else STALK2, 5, "y", 0.01, pitch=lean, roll=rnd.uniform(-0.06, 0.06))
        top = (x, y + h + 0.12, z + lean * h * 0.5)
        hm = HEAD if rnd.random() < 0.5 else HEAD2
        for j in range(3): K.sphere((top[0] + rnd.uniform(-0.03, 0.03), top[1] + j * 0.06 - 0.05, top[2] + rnd.uniform(-0.03, 0.03)), 0.035, hm, 5, (1.0, 1.4, 1.0))
        for j in range(3):
            a = rnd.uniform(0, math.tau); yy = y + h * (0.35 + 0.18 * j); L = rnd.uniform(0.45, 0.7); m = LEAF if j % 2 else LEAF2
            p0 = (x, yy, z); p1 = (x + L * 0.6 * math.cos(a), yy + 0.2, z + L * 0.6 * math.sin(a)); p2 = (x + L * math.cos(a), yy - 0.15, z + L * math.sin(a))
            w = 0.07
            K.quad([(p0[0], p0[1] - w, p0[2]), (p1[0], p1[1] - w, p1[2]), (p2[0], p2[1], p2[2]), (p1[0], p1[1] + w, p1[2]), (p0[0], p0[1] + w, p0[2])], m)
    for (x0, x1, z0, z1, dens) in ((-30, -4.2, 0.0, 5.2, 1.6), (4.2, 30, 0.0, 5.2, 1.6), (-40, 40, 8.6, 22, 0.9), (-40, 40, -6, 0.0, 0.8)):
        n = int((x1 - x0) * (z1 - z0) * dens)
        for k in range(n):
            x = rnd.uniform(x0, x1); z = rnd.uniform(z0, z1)
            if -6.8 < x < -2.2 and 2.6 < z < 5.8: continue      # hut
            stalk(x, z, rnd.uniform(1.9, 2.5))
    for k in range(70):   # far field: dark ragged hedges of crop
        x = rnd.uniform(-80, 80); z = rnd.uniform(22, 60)
        K.box((x, 1.1, z), (rnd.uniform(4, 10), 2.2, rnd.uniform(2, 5)), pm("#1e2014", 0.9), rnd.uniform(-0.3, 0.3), 0.6)
    # telegraph poles and wires along the railway
    for k in range(9):
        x = -40 + k * 10; CK.telegraph(K, x, 7.9, 6.0, 0.6, 0.0)
    for d in (-0.65, -0.25, 0.25, 0.65):
        for k in range(8):
            x0 = -40 + k * 10
            tube(f"tw{d}{k}", [(x0, 6.4, 7.9 + d), (x0 + 5, 6.15, 7.9 + d), (x0 + 10, 6.4, 7.9 + d)], 0.006, pm("#1a1a1a", 0.5))
    # linesman's hut: plank walls, tin roof, lit window, lantern on a hook, a handcar and spare sleepers beside it
    PL = wood("#5a4630", "#2e2216", 7, 0.85); TIN = CK.wm("tin", "#5a5e60", "#6a4a2a", 0.5, 0.6, 12, 0.6)
    hx, hz = -4.5, 4.4
    K.box((hx, 1.1, hz), (2.4, 2.2, 1.8), PL, 0, 0.02)
    for k in range(9): K.box((hx - 1.2 + k * 0.3, 1.1, hz - 0.91), (0.02, 2.2, 0.02), pm("#2a1e14", 0.9), 0, 0)
    K.box((hx, 2.3, hz), (2.8, 0.08, 2.3), TIN, 0, 0.02, -0.12)
    K.box((hx + 0.5, 1.3, hz - 0.92), (0.6, 0.5, 0.04), CK.KS.window_glow("mwin", "#ffb050", 2.2), 0, 0.01)
    for j in range(2): K.box((hx + 0.5, 1.3, hz - 0.95), (0.6 if j else 0.04, 0.04 if j else 0.5, 0.03), PL, 0, 0)
    K.box((hx - 0.55, 0.95, hz - 0.92), (0.7, 1.9, 0.05), wood("#4a3a28", "#2a1e14", 6), 0, 0.01)
    sign(K, (hx, 2.0, hz - 0.95), 1.8, 0.32, 0, "LIUTIAOHU  S.M.R.", "#1e2a3a", pm("#f2e8d0", 0.5), "sans", "#c8a24a")
    CK.lantern(K, (hx + 1.25, 1.55, hz - 0.95), 18)
    for k in range(6): K.box((hx - 0.3 + (k % 3) * 0.02, 0.06 + k * 0.12, hz - 1.6), (2.4, 0.12, 0.22), wood("#4a3826", "#2a1e14", 6, 0.9), 0.02 * k, 0.01)
    K.box((hx + 1.7, 0.45, hz - 0.2), (0.9, 0.1, 1.3), PL, 0, 0.01)
    for sd in (-1, 1): K.cyl((hx + 1.7, 0.25, hz - 0.2 + sd * 0.6), 0.22, 0.06, iron(), 14, "z")
    for k in range(3): CK.KS.barrel(K, (hx - 1.6, 0.4, hz - 0.5 + k * 0.6), 0.28, 0.8, wood("#6a4a2a", "#3a2614", 10), iron())
    # the officers' corner: lanterns on the ground, a map case, a field telephone, a staff car's headlights in the dark
    CK.lantern(K, (-1.4, 0.0, 2.6), 90)
    CK.lantern(K, (2.6, 0.0, 3.0), 80)
    lib.light("AREA", T(0.6, 2.2, 1.2), 90, (1.0, 0.66, 0.36), 2.0).rotation_euler = (math.radians(-35), 0, math.pi)
    K.box((-1.0, 0.12, 2.3), (0.4, 0.24, 0.3), pm("#4a3a24", 0.6), 0.3, 0.02)
    K.box((0.8, 0.1, 2.0), (0.3, 0.2, 0.2), pm("#3a4030", 0.5), -0.2, 0.02)
    car = CK.X(6.5, 0, 2.2, 0.5)
    car.box(K, (0, 0.75, 0), (4.2, 0.7, 1.7), pm("#1e2226", 0.3, 0.4), 0.1)
    car.box(K, (-0.4, 1.35, 0), (2.0, 0.6, 1.6), pm("#1e2226", 0.3, 0.4), 0.1)
    for sd in (-1, 1):
        for xx in (1.4, -1.3): CK.wheel(K, car, (xx, 0.38, sd * 0.85), 0.38, 0.22, pm("#141414", 0.8), pm("#7a7a7a", 0.3, 0.8))
        car.cyl(K, (2.1, 0.95, sd * 0.6), 0.13, 0.12, em("#fff2c8", 6.0), 12, "x")
    for sd in (-1, 1):
        L = lib.light("SPOT", T(*car.p(2.4, 0.95, sd * 0.6)), 300, (1.0, 0.92, 0.75), 0.05); L.data.spot_size = math.radians(40); L.data.spot_blend = 0.5
        lib.look_at(L, T(*car.p(14, 0.0, sd * 1.5)))
    # Beidaying barracks far off: a long wall, gatehouse with a tiled roof, lit windows
    BR = grime("mbrick", "#6a5a4a", 0.4); RF = pm("#2a2a30", 0.6)
    K.box((-18, 1.6, 70), (60, 3.2, 1.0), BR, 0, 0.05)
    K.box((-18, 4.0, 70), (8, 4.0, 4), BR, 0, 0.05); K.box((-18, 6.4, 70), (10, 0.5, 6), RF, 0, 0.1)
    for k in range(6):
        x = -40 + k * 9; K.box((x, 3.2, 76), (7, 4, 6), BR, 0, 0.05); K.box((x, 5.6, 76), (8, 0.6, 7), RF, 0, 0.1)
        for j in range(3): K.box((x - 2.4 + j * 2.4, 3.2, 72.98), (0.9, 1.1, 0.05), em("#ffb050", 4.0), 0, 0)
    for k in range(4): K.box((-21 + k * 2, 4.6, 67.98), (0.8, 0.8, 0.05), em("#ffc070", 3.0), 0, 0)
    # moon
    K.sphere((60, 70, 220), 4.5, em("#e8eeff", 5.0), 20)
    sun = lib.light("SUN", T(0, 10, 0), 0.8, (0.6, 0.72, 1.0), math.radians(2)); lib.look_at(sun, T(0, 10, 0) + T(-0.35, -0.45, -1.0))
    lib.light("AREA", T(0, 3.0, -4.0), 160, (0.55, 0.65, 1.0), 4.0).rotation_euler = (math.radians(-65), 0, math.pi)
    # blast aftermath (shown from BOOM): broken rail ends, scattered ballast, small fire, smoke
    for sd, dx in ((-1, -0.25), (1, 0.65)):
        KB.box((cx + dx, 0.75, 6 - 0.72), (0.5, 0.14, 0.07), pm("#7a7470", 0.3, 0.9), 0, 0.01, 0, sd * 0.35)
    for k in range(25): KB.sphere((cx + rnd.uniform(-1.2, 1.2), 0.62 + rnd.uniform(0, 0.08), 6 + rnd.uniform(-1.6, 0.6)), rnd.uniform(0.04, 0.09), grime("c2ballast", "#6a645c", 0.5, 12.0), 6)
    K.build(); broken = KB.build()
    # the intact charge objects vs. aftermath: charge lives in the main kit; we cover it with smoke + fire after the blast
    n0 = set(bpy.context.scene.objects)
    fire("fire", (cx + 0.1, 0.62, 6 - 0.4), 0.35, 7, True, 120)
    smoke_column("smk", (cx, 0.9, 6 - 0.3), 6.0, 0.5, 2.2, smoke_mat("msmoke", "#3a3632", 0.7), (2.5, 1.0), 3, 9)
    after = [o for o in bpy.context.scene.objects if o not in n0] + broken
    flash = lib.light("POINT", T(cx, 1.6, 5.0), 0.0, (1.0, 0.7, 0.35), 0.6)
    def update(f):
        on = f >= BOOM
        for o in after: o.hide_render = not on
        k = max(0.0, 1.0 - (f - BOOM) / 14.0) if on else 0.0
        flash.data.energy = 5000 * k * k
    return {"update": update}
