# The Trinity test, New Mexico, 16 July 1945, 5:29 am (chapter 13 shots on "Then, in July 1945..." / "An atomic bomb").
# SERIOUS: no jokes. The light is shown, nothing else: pre-dawn desert, the far steel tower, the observation bunker with the
# scientists; at F_FLASH the whole desert is lit white, then a slowly rising glowing fireball and dust column far away.
# three.js layout: the observation bunker at the origin (timber + earth, its door facing -z at z -2.2), sandbag wall and
#   instrument benches in front at z -4..-2.5; scientists stand at x -4..4, z -6..-3.5 facing -z... the tower is far away
#   at (0, 0, 900) beyond them, so cameras sit at z < -8 looking +z (the scientists face the camera, the light behind them),
#   or at z ~ -2 looking +z past them. Mountains (Oscura) z 4000+. Ground y 0.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, crate, barrel
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK

F_FLASH = 2802
TOWER = (0, 0, 900)

def build(M, D):
    rnd = random.Random(1945)
    S = bpy.context.scene
    CK.sky(S.world, (0.8, 0.02, -0.4), [(0.0, (0.5, 0.32, 0.3)), (0.04, (0.3, 0.24, 0.36)), (0.15, (0.1, 0.11, 0.24)), (1.0, (0.01, 0.015, 0.05))],
           sun_col=(0, 0, 0), cloud_dark=(0.03, 0.03, 0.06), cloud_lit=(0.4, 0.25, 0.25), cover=0.3, strength=1.0, glow_col=(0.8, 0.4, 0.3), glow=0.4, disc=False)
    sky_bg = S.world.node_tree.nodes["Background"]
    moon = CK.sun_light((0.8, 0.12, -0.4), 0.6, (0.6, 0.62, 0.9), 2.0)
    sand = mat_once("tsand", lambda: CK.green_hill_mat("tsand", "#8a7a5e", "#6a5a44", "#a08a6a"))
    CK.heightfield("tground", -3000, 3000, -300, 3000, 20, lambda x, z: 1.5 * math.sin(x * 0.01) * math.sin(z * 0.013) * min(1, max(0, (abs(x) + abs(z) - 60) / 200)), sand)
    rock = mat_once("tmount", lambda: CK.green_hill_mat("tmount", "#5a4a44", "#3a3036", "#7a6a5a"))
    CK.heightfield("oscura", -9000, 9000, 3800, 9000, 120, CK.ridge_fn(3800, 6000, -40, 900, 2, 0.0012), rock)
    K = Kit("tr")
    # creosote and yucca bushes scattered over the flats
    bush = pm("#3a4a2a", 0.9); yuc = pm("#5a6a3a", 0.8)
    for k in range(260):
        x, z = rnd.uniform(-160, 160), rnd.uniform(-60, 420)
        if abs(x) < 7 and -10 < z < 4: continue
        r = rnd.uniform(0.25, 0.7); K.sphere((x, r * 0.5, z), r, bush, 8, (1, 0.6, 1))
        if k % 9 == 0:
            for j in range(10): K.box((x + 0.3, 0.45, z), (0.03, 0.9, 0.06), yuc, j * 0.6, 0.0, 0.5 * math.cos(j), 0.5 * math.sin(j))
    # the bunker: timber front, earth mound, door, sandbags, periscope, cable reels, instrument benches, a field telephone
    earth = mat_once("tearth", lambda: CK.green_hill_mat("tearth", "#7a6a50", "#5a4a38", "#8a7a5a"))
    CK.puff("mound", (0, -0.8, 1.5), (7, 3.8, 5), earth, 2, True)
    tim = wood("#6a5034", "#3a2a1a", 4.0, 0.8)
    K.box((0, 1.1, -2.3), (6.0, 2.2, 0.3), tim, 0.0, 0.02)
    for k in range(7): K.box((-2.7 + k * 0.9, 1.1, -2.48), (0.14, 2.2, 0.08), tim, 0.0, 0.0)
    K.box((0, 0.95, -2.5), (1.0, 1.9, 0.05), pm("#2a2420", 0.7), 0.0, 0.0)
    K.box((0, 2.3, -2.5), (6.4, 0.25, 0.4), tim, 0.0, 0.02)
    K.cyl((1.8, 2.9, -1.5), 0.08, 1.4, pm("#3a3e3a", 0.4, 0.5), 10); K.box((1.8, 3.6, -1.6), (0.25, 0.2, 0.35), pm("#3a3e3a", 0.4, 0.5), 0.0, 0.02)
    sb = mat_once("tsb", lambda: lib.cloth("tsb", "#a8946a"))
    for row in range(3):
        for k in range(10): K.box((-4.5 + k * 0.62 + (row % 2) * 0.3, 0.16 + row * 0.3, -2.9), (0.6, 0.3, 0.38), sb, 0.0, 0.08)
    for side in (-1, 1):
        K.box((side * 5.0, 0.8, -3.6), (1.6, 0.06, 0.7), tim, 0.0, 0.01)
        for sx in (-0.7, 0.7): K.box((side * 5.0 + sx, 0.4, -3.6), (0.06, 0.8, 0.6), tim, 0.0, 0.0)
        K.box((side * 5.0 - 0.3, 1.0, -3.6), (0.5, 0.35, 0.4), pm("#3a3a36", 0.4, 0.4), 0.0, 0.02)
        for j in range(4): K.cyl((side * 5.0 - 0.45 + j * 0.1, 1.08, -3.79), 0.025, 0.01, em("#ffb050", 3.0), 8, "z")
        K.box((side * 5.0 + 0.4, 0.95, -3.6), (0.4, 0.25, 0.3), pm("#5a4a3a", 0.5), 0.0, 0.02)
    for k in range(2): K.cyl((3.0 + k * 1.2, 0.5, -1.0), 0.5, 0.4, tim, 18, "x")
    K.build()
    cable = pmat("tcable", "#141414", 0.6)
    for k in range(3): tube(f"cab{k}", [(-1 + k, 0.03, -2.6), (-1.5 + k * 1.2, 0.03, 40), (-2 + k * 1.5, 0.03, 300), (k - 1, 0.03, 890)], 0.04, cable, res=6, bres=0)
    # the tower: steel lattice, 30 m, the shack on top (where the device sits), guy wires
    T_ = Kit("tower"); st = pm("#5a5a5a", 0.5, 0.7); tx, ty, tz = TOWER
    for sx in (-1, 1):
        for sz in (-1, 1):
            T_.box((tx + sx * 2.2, 15, tz + sz * 2.2), (0.3, 30.5, 0.3), st, 0.0, 0.0, -sz * 0.06, sx * 0.06)
    for lv in range(10):
        y = lv * 3 + 1.5; w = 4.6 - lv * 0.25
        for sd in (-1, 1): T_.box((tx, y, tz + sd * w / 2), (w, 0.15, 0.15), st, 0.0, 0.0); T_.box((tx + sd * w / 2, y, tz), (0.15, 0.15, w), st, 0.0, 0.0)
    T_.box((tx, 31.2, tz), (3.0, 2.2, 3.0), pm("#7a6a54", 0.8), 0.0, 0.0)
    T_.build()
    # the flash and the fireball: a growing glowing sphere, a dust skirt, a stem, a strong light; the sky lit up
    fb_m = bpy.data.materials.new("tfire"); fb_m.use_nodes = True; nn = fb_m.node_tree.nodes; ll = fb_m.node_tree.links
    for x_ in list(nn): nn.remove(x_)
    out = nn.new("ShaderNodeOutputMaterial"); emn = nn.new("ShaderNodeEmission"); emn.inputs["Color"].default_value = (1.0, 0.75, 0.45, 1); emn.inputs["Strength"].default_value = 60
    ll.new(emn.outputs[0], out.inputs["Surface"])
    fire_ = CK.puff("fireball", (tx, 30, tz), (1, 1, 1), fb_m, 1, False)
    dust = CK.smoke("tdust", (tx, 5, tz), 120, 50, 160, "#8a6a5a", 0.7, (60, 0), 3, 9)
    flash_l = lib.light("POINT", T(tx, 200, tz - 100), 0, (1.0, 0.92, 0.8), 30); flash_l.visible_camera = False
    fill = CK.area((0, 6, -30), (0, 1.2, -3), 300, (0.55, 0.6, 0.9), 12)
    def update(f):
        u = (f - F_FLASH) / 30.0
        on = u >= 0
        fire_.hide_render = not on; CK.show(dust, u > 0.8)
        if on:
            r = 30 + 140 * min(1.0, u / 3.0) ** 0.6; y = 30 + r * 0.8 + 60 * max(0, u - 2)
            fire_.location = T(tx, y, tz); fire_.scale = (r, r, r * 0.9)
            k = math.exp(-max(0.0, u - 0.15) * 1.3)
            flash_l.data.energy = 4e10 * (0.08 + 0.92 * k)
            sky_bg.inputs[1].default_value = 1.0 + 60 * k
            fire_.active_material.node_tree.nodes["Emission"].inputs["Strength"].default_value = 40 + 400 * k
        else:
            flash_l.data.energy = 0; sky_bg.inputs[1].default_value = 1.0
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
