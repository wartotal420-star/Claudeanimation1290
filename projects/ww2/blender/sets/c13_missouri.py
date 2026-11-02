# The surrender on USS Missouri, Tokyo Bay, 2 September 1945 (chapter 13 last shots).
# A close set of the battleship's starboard deck beside turret No. 2: teak deck, the surrender table with its green cloth
# and the two copies of the instrument, MacArthur's microphones, the superstructure wall with portholes and ladders,
# sailors packed on the turret roof, the gun barrels and the decks above; Tokyo Bay beyond the rails with the fleet,
# Mount Fuji, and a fly-over of planes at the end (update: f >= F_FLYOVER).
# three.js layout: deck y 0 over x -14..14, z -6..10; the rail along z -6 (the sea side, toward the camera cameras at
#   z < -3 look +z at the table) ... the table centred (0, 0, 2.0), 2.4 x 0.9, top y 0.78; MacArthur's microphones at
#   (-1.8, 0, 2.3); the Japanese delegation stands in two rows at x 2.5..6, z 0.5..1.6 facing -x/-z; the Allied officers
#   in rows at x -6..-2.5, z 3.5..5.0; the superstructure wall at z 8; turret No. 2 centred (6, 0, 13) with barrels
#   pointing over the deck toward -x at y ~4.5; sailors sit on the turret roof (y 3.6) and stand on the 01 deck (y 3.2,
#   z 7..8).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood, text as ktext, sign, paper
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK
from sets import front as FR
from sets import ikit

F_FLYOVER = 3990

def build(M, D):
    rnd = random.Random(902)
    S = bpy.context.scene
    CK.sky(S.world, (0.4, 0.55, 0.75), [(0.0, (0.72, 0.74, 0.76)), (0.1, (0.55, 0.6, 0.68)), (0.4, (0.36, 0.44, 0.56)), (1.0, (0.18, 0.24, 0.36))],
           sun_col=(10, 10, 9), cloud_dark=(0.42, 0.44, 0.48), cloud_lit=(0.95, 0.95, 0.94), cover=0.9, strength=0.85, glow_col=(1.0, 0.95, 0.85), glow=0.2, band=(0.0, 0.35), fade=(1.0, 0.55))
    CK.sun_light((0.4, 0.55, 0.75), 3.2, (1.0, 0.95, 0.88), 6.0)
    CK.sea("bay", -6000, 6000, -6000, 6000, -9.0, CK.water_mat("mwater", "#2a4048", "#4a6268", 0.7, 0.07, 0.4))
    K = Kit("mo")
    teak = mat_once("mteak", lambda: lib.brickmat("mteak", "#a08a68", "#8a7458", "#3a3026", 1.0, 6.0, 0.14, 0.75))
    grey = mat_once("mgrey", lambda: worn("mgrey", "#7a828c", "#4a525a", 0.55, 0.2, 1.0, 0.68, "#5a6068"))
    grey2 = pm("#5e6670", 0.5, 0.3); dk = pm("#2c3036", 0.5, 0.3)
    K.box((0, -0.15, 2), (40, 0.3, 30), teak, 0.0, 0.0)
    # rails with stanchions and chains along the sea side, life rings
    for k in range(29): K.cyl((-14 + k, 0.55, -6), 0.03, 1.1, dk, 8)
    for y in (0.6, 1.1): K.cyl((0, y, -6), 0.02, 28, dk, 8, "x")
    for k, x in enumerate((-10, 9)):
        for j in range(8): K.torus((x, 0.85, -6.05), 0.36, 0.07, pm("#e8e4dc", 0.6) if j % 2 == 0 else pm("#c8302a", 0.6), 4, 8, "z", arc=math.pi / 4, roll=j * math.pi / 4)
    # the superstructure wall: plating, portholes, doors, ladders, the 01 deck with its rail crowded with sailors
    K.box((0, 1.6, 8.4), (40, 3.2, 0.8), grey, 0.0, 0.02)
    for k in range(18): K.cyl((-13 + k * 1.6, 1.8, 7.99), 0.16, 0.05, pm("#1a2026", 0.1), 16, "z"); K.torus((-13 + k * 1.6, 1.8, 7.98), 0.18, 0.03, pm("#b8902a", 0.3, 0.8), 16, 4, "z")
    for x in (-8, 3): K.box((x, 0.95, 7.98), (0.9, 1.9, 0.06), dk, 0.0, 0.02)
    K.box((0, 3.2, 7.2), (40, 0.15, 3.0), teak, 0.0, 0.0)
    for k in range(29): K.cyl((-14 + k, 3.75, 5.75), 0.03, 1.1, dk, 8)
    K.cyl((0, 4.25, 5.75), 0.02, 28, dk, 8, "x")
    for j in range(10): K.box((-11.5, 0.2 + j * 0.32, 7.8 - j * 0.05), (0.8, 0.04, 0.14), dk, 0.0, 0.0)
    K.box((0, 6.0, 9.6), (24, 5.6, 2.4), grey, 0.0, 0.05)
    for k in range(10): K.box((-9 + k * 2, 7.0, 8.38), (1.2, 0.7, 0.05), pm("#141a20", 0.1), 0.0, 0.0)
    # turret No. 2 and its three 16-inch barrels over the deck (sailors sit on them)
    K.box((8, 2.8, 13), (12, 3.6, 10), grey, 0.0, 0.3); K.box((8, 4.7, 13), (11, 0.3, 9.2), grey2, 0.0, 0.1)
    for k, dz in enumerate((-2.2, 0.0, 2.2)):
        for i in range(6):
            r = 0.55 - 0.035 * i; K.cyl((2.0 - i * 2.4 - 1.2, 3.4, 13 + dz), r, 2.45, grey2, 20, "x", r - 0.03)
        K.cyl((1.6, 3.4, 13 + dz), 0.75, 0.9, pm("#c8c0a8", 0.9), 16, "x")
    # the surrender table: green baize, two documents in leather folders, pens, chairs
    K.box((0, 0.74, 2.0), (2.4, 0.06, 0.9), wood("#5a3a22", "#2a1a10", 5.0, 0.4), 0.0, 0.01)
    K.box((0, 0.775, 2.0), (2.45, 0.01, 0.95), pm("#2e5a34", 0.9), 0.0, 0.0)
    for sx in (-1.1, 1.1):
        for sz in (1.65, 2.35): K.box((sx, 0.37, sz), (0.06, 0.74, 0.06), pm("#3a2a1a", 0.5), 0.0, 0.0)
    for k, x in enumerate((-0.45, 0.45)):
        K.box((x, 0.79, 1.95), (0.5, 0.015, 0.38), pm("#3a2a1e" if k else "#2a2a3a", 0.5), 0.05 * (k * 2 - 1), 0.0)
        K.box((x, 0.8, 1.95), (0.44, 0.004, 0.32), paper("#f2ead6", 0.2), 0.05 * (k * 2 - 1), 0.0)
    for k in range(4): K.cyl((-0.15 + k * 0.1, 0.795, 2.3), 0.008, 0.16, pm("#1a1a1a", 0.3, 0.5), 8, "z")
    for sz in (1.2,): K.box((0, 0.45, sz), (0.45, 0.06, 0.45), pm("#3a2a1a", 0.6), 0.0, 0.02); K.box((0, 0.8, sz - 0.2), (0.45, 0.65, 0.06), pm("#3a2a1a", 0.6), 0.0, 0.02)
    # microphones (MacArthur speaks into them), a newsreel camera stand
    for k, dx in enumerate((-0.15, 0.15)):
        K.cyl((-1.8 + dx, 0.75, 2.3), 0.012, 1.5, pm("#c8ccd0", 0.15, 1.0), 8); K.box((-1.8 + dx, 1.55, 2.3), (0.1, 0.16, 0.06), pm("#141414", 0.4), 0.0, 0.01)
    K.cyl((-1.8, 0.02, 2.3), 0.22, 0.04, pm("#141414", 0.4), 16)
    for j in range(3):
        a = j / 3 * math.tau; tube(f"mtri{j}", [(-7 + 0.5 * math.cos(a), 3.2, 6.5 + 0.5 * math.sin(a)), (-7, 4.7, 6.5)], 0.02, pmat("ctri", "#2a2a2a", 0.5, 0.5), res=2, bres=0)
    K.box((-7, 4.9, 6.5), (0.35, 0.35, 0.6), pm("#141414", 0.4), 0.3, 0.02)
    K.build()
    # the flags: the US flag on the mainmast staff, and the 1853 Perry flag framed on the superstructure (as on the day)
    tube("mstaff", [(-12, 5, 9.2), (-12, 13, 9.2)], 0.06, dk, res=2, bres=0)
    ikit.flag("mflag", (-12.05, 12.8, 9.2), 3.0, 1.6, CK.us_flag_mat(), math.pi, 0.08)
    perry = ikit.flag_img("us"); ikit.panel("perry", (2.0, 6.3, 8.36), 2.4, 1.5, ikit.img_mat("perrym", perry, 0.8), 0.0)
    fr = Kit("pf")
    for dx, dy, sw, sh in ((0, 0.8, 2.6, 0.1), (0, -0.8, 2.6, 0.1), (1.25, 0, 0.1, 1.7), (-1.25, 0, 0.1, 1.7)): fr.box((2.0 + dx, 6.3 + dy, 8.35), (sw, sh, 0.06), pm("#5a3a1e", 0.5), 0.0, 0.0)
    fr.build()
    # Tokyo Bay: the Allied fleet at anchor, Mount Fuji in the haze, the shore
    ship = CK.us_battleship("mbb", -900, -1400, 0.4, 180, 30, 0.0)
    for k, (x, z) in enumerate(((-300, -2200), (800, -1700), (1600, -2600), (-1800, -2900), (300, -3500))): CK.clone(ship, x + 900, z + 1400, f"mc{k}")
    mesh_obj("fuji", [(-9000, -9, -14000), (9000, -9, -14000), (0, 3700, -14000)], [(0, 1, 2)], lib.principled("mfuji", hexc("#7a8698"), 0.9))
    mesh_obj("fujisnow", [(-1700, 3000, -13990), (1700, 3000, -13990), (0, 3700, -13990)], [(0, 1, 2)], lib.principled("mfujis", hexc("#e4e8ee"), 0.8))
    CK.heightfield("shore", -12000, 12000, -9000, -6000, 200, lambda x, z: -9 + 120 * (1 + math.sin(x * 0.0007)) * min(1, (-6000 - z) / 1500), mat_once("mshore", lambda: CK.green_hill_mat("mshore", "#4a5a4a", "#3a463a", "#6a6a60")))
    # the fly-over: B-29s and carrier planes in formation
    fly = [CK.inst(CK.plane("b29" if k < 6 else "wildcat", gear=False, spin=True), f"mfly{k}") for k in range(14)]
    CK.area((0, 6, -10), (0, 1.5, 2), 2200, (1.0, 0.95, 0.88), 14)
    def update(f):
        u = (f - F_FLYOVER) / 30.0
        for k, o in enumerate(fly):
            o.hide_render = u < 0
            row, col = divmod(k, 3)
            CK.place(o, (-1400 + 160 * u + col * 70 + row * 40, 420 + row * 40, -600 - col * 80 - row * 30), (1, 0, -0.1), 0.0, 1.0)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
