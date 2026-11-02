# Kamikaze attacks, 1944-45 (chapter 13). SERIOUS, slow: a single plane diving at an American carrier through the flak,
# seen from the carrier's deck and from the sea; then a lone plane flying away into the evening (the young pilots).
# three.js layout: a US carrier at the origin, bow +x (yaw 0), flight deck top y 16 (x -110..110, z -13..13), island at
#   (14, 16, 10.5). Sailors man a 40 mm gun tub on the port deck edge at (-20, 15.4, -15) and stand on deck at x -12..-2,
#   z -10..-4. The diving Zero: dive(f) from (-900, 700, -900) toward the island, F_DIVE0..F_DIVE1 (it never arrives on
#   screen: the shot cuts before). The lone plane flies toward the low sun (+x, far) f >= F_LONE.
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, hexc
from sets.kit_sbpw import Kit, pm, em, wood
from sets.void import lathe, tube, worn, pmat, mat_once, link, mesh_obj
from sets import c07_kit as CK

DECK = 16.0
F_DIVE0, F_DIVE1 = 1500, 1700
F_LONE = 1696
SUN = (0.95, 0.12, 0.2)

def dive(f):
    u = (f - F_DIVE0) / (F_DIVE1 - F_DIVE0)
    a = Vector((-900, 700, -900)); b = Vector((10, DECK + 8, 6))
    return a.lerp(b, max(0.0, u) * 0.9), (b - a)

def build(M, D):
    rnd = random.Random(1945)
    S = bpy.context.scene
    CK.sky(S.world, SUN, [(0.0, (1.0, 0.62, 0.32)), (0.05, (0.86, 0.55, 0.4)), (0.15, (0.45, 0.42, 0.55)), (0.45, (0.16, 0.22, 0.42)), (1.0, (0.04, 0.07, 0.2))],
           sun_col=(28, 14, 6), cloud_dark=(0.2, 0.16, 0.22), cloud_lit=(1.3, 0.75, 0.4), cover=0.55, strength=0.85, glow_col=(1.0, 0.55, 0.25), glow=0.9)
    CK.sun_light(SUN, 3.6, (1.0, 0.7, 0.42), 1.5)
    CK.sea("ksea", -9000, 9000, -9000, 9000, -0.25, CK.water_mat("kwater2", "#0e2a40", "#2a4a5a", 0.6, 0.08, 0.7))
    CK.whitecaps("kcaps", -1500, 1500, -1500, 1500, 900, rnd)
    P = CK.carrier("kcv", 0, 0, 0.0, 230, 26, False, mark="17", deck_h=DECK)
    CK.wake("kcv", P, 230, 26, 1.0)
    K = Kit("kdeck"); CK.deck_props(K, P, DECK, -100, 60, 26, rnd, False)
    gun = pm("#5e6a76", 0.5, 0.3); dk = pm("#2c3036", 0.5, 0.3)
    K.cyl((-20, DECK - 0.9, -15), 2.2, 1.2, gun, 20)
    for sd in (-1, 1): K.cyl((-20 + sd * 0.35, DECK + 0.6, -15.6), 0.07, 2.6, dk, 8, "z", None, 0.0, 0.0, -0.9)
    K.box((-20, DECK + 0.1, -15), (1.4, 0.8, 1.2), gun, 0.0, 0.03)
    K.build()
    for r in range(4):
        for j, lz in enumerate((-7.0, 1.0, 8.0)):
            o = CK.inst(CK.plane("wildcat" if r < 2 else "sbd", gear=True, spin=False), f"kp{r}{j}"); CK.place(o, (-40 - r * 14 + (j % 2) * 2, DECK + 1.35, lz), (1, 0.14, 0))
    # flak bursts and tracer streams climbing at the attacker
    flak = []
    for k in range(40):
        p = Vector((rnd.uniform(-800, -50), rnd.uniform(120, 650), rnd.uniform(-800, -50)))
        flak.append((F_DIVE0 + rnd.randrange(0, 180), CK.smoke(f"kfl{k}", tuple(p), 1, rnd.uniform(4, 7), 7, "#1a1816", 0.92, seed=k + 3, puffs=2)))
    tr_m = lib.emit("ktracer", (1.0, 0.7, 0.3), 25)
    tracers = []
    for k in range(10):
        a = Vector((-20 + rnd.uniform(-30, 30), DECK + 2, -15 + rnd.uniform(-10, 4))); b = a + Vector((-1, 0.75, -0.9)).normalized() * rnd.uniform(300, 700) + Vector((rnd.uniform(-60, 60), 0, rnd.uniform(-60, 60)))
        tracers.append(tube(f"ktr{k}", [tuple(a), tuple(b)], 0.25, tr_m, res=2, bres=0))
    z0 = CK.inst(CK.plane("zero", gear=False, spin=True), "kz")
    trail = CK.smoke("ktrail", (-900, 700, -900), 1, 3, 5, "#3a3634", 0.6, seed=5, puffs=2)
    lone = CK.inst(CK.plane("zero", gear=False, spin=True), "klone")
    CK.area((20, DECK + 10, -40), (-10, DECK + 1, -8), 8000, (1.0, 0.85, 0.7), 20)
    def update(f):
        on = F_DIVE0 <= f < F_LONE
        for f0, objs in flak: CK.show(objs, on and f >= f0)
        CK.show(tracers, on and (f // 3) % 3 != 0)
        p, d = dive(f); z0.hide_render = not on; CK.place(z0, tuple(p), tuple(d), 0.2 * math.sin(f * 0.1), 1.2)
        for k, o in enumerate(trail): o.hide_render = not on; o.location = T(*(p - d.normalized() * (12 + 10 * k)))
        u = (f - F_LONE) / 30.0
        lone.hide_render = u < 0
        CK.place(lone, (-60 + 70 * u, 60 + 6 * u, -120 - 8 * u), (1, 0.08, -0.1), 0.05, 1.0)
    update(D["frames"][0]["f"] if D.get("frames") else 0)
    return {"update": update}
