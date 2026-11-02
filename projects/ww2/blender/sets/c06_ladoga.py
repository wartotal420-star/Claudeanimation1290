# Chapter 6: the Road of Life across frozen Lake Ladoga, winter night 1941-42. A line of GAZ-AA trucks with hooded
# lights drives over the ice between marker poles; snow ridges, cracks, a traffic controller's post with a lantern, a
# tent and an anti-aircraft gun on the ice, a broken-through truck half sunk, stars and a cold moon.
# Layout (three coords): the ice at y 0, the road (packed snow) along z through x -3..3 from z -20 to 900; the trucks
# drive toward -z (update: frames 2134-2264); the controller's post at (6, 0, 6); the AA gun at (-14, 0, 22);
# keep x 3.5..6, z 2..10 clear (the controller and a driver).
import bpy, math, random
from mathutils import Vector, noise
import lib
from lib import T, hexc
from . import kit_sbpw as K_
from .kit_sbpw import Kit, pm, em, wood, cloth, brass, iron, grime, paper, text, glassm, crate, barrel, R90
from .c05_kit import (sky, ground_mat, height_mesh, sun_light, area, point, spot, truck, lathe, tube, worn, mat_once, cached, snow_mat, fsphere, empty, beam_mat, searchlight, aim)

def ice_mat():
    def mk():
        m = lib.principled("c6ice", hexc("#8aa8c0"), 0.12); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 0.15
        try: vo.feature = "DISTANCE_TO_EDGE"
        except Exception: pass
        l.new(tc.outputs["Object"], vo.inputs["Vector"])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.05; nz.inputs["Detail"].default_value = 4; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = lib.ramp(n, l, nz.outputs["Fac"], [(0.3, hexc("#5a7a98")), (0.5, hexc("#9ab4c8")), (0.7, hexc("#d8e4ee"))])
        cr = lib.ramp(n, l, vo.outputs["Distance"], [(0.0, (0.85, 0.92, 1.0)), (0.02, (1, 1, 1))])
        mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1.0; l.new(r.outputs["Color"], mx.inputs[6]); l.new(cr.outputs["Color"], mx.inputs[7])
        l.new(mx.outputs[2], b.inputs["Base Color"]); lib.bump(n, l, vo.outputs["Distance"], 0.3, 0.02)
        return m
    return cached("c6ice", mk)

def stars_world():
    W = bpy.context.scene.world; nt = W.node_tree; n = nt.nodes; l = nt.links
    for x in list(n): n.remove(x)
    out = n.new("ShaderNodeOutputWorld"); bg = n.new("ShaderNodeBackground"); l.new(bg.outputs[0], out.inputs[0])
    co = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(co.outputs["Generated"], sep.inputs[0])
    rmp = lib.ramp(n, l, sep.outputs["Z"], [(0.0, (0.06, 0.08, 0.16)), (0.15, (0.02, 0.03, 0.08)), (0.6, (0.004, 0.006, 0.02))])
    vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 300; l.new(co.outputs["Generated"], vo.inputs["Vector"])
    st = lib.ramp(n, l, vo.outputs["Distance"], [(0.0, (3.0, 3.0, 3.2)), (0.05, (0, 0, 0))])
    ad = n.new("ShaderNodeMix"); ad.data_type = "RGBA"; ad.blend_type = "ADD"; ad.inputs[0].default_value = 1.0; l.new(rmp.outputs["Color"], ad.inputs[6]); l.new(st.outputs["Color"], ad.inputs[7])
    l.new(ad.outputs[2], bg.inputs[0]); bg.inputs[1].default_value = 1.0

def build(M, D):
    random.seed(1942); K_.reset(); rnd = random.Random(19)
    stars_world()
    SNOW = snow_mat("ldsnow", "#d8e2f0", "#8a9ab8")
    def H(x, z): return 0.04 * noise.noise(Vector((x * 0.1, z * 0.1, 0.5)))
    height_mesh("ice", -400, 400, -40, 1200, 8.0, H, ice_mat())
    K = Kit("lad"); road = ground_mat("c6packed", [(0.3, "#9aa8b8"), (0.6, "#c8d4e0")], 0.4, 4, 0.7, 0.5)
    K.box((0, 0.03, 430), (6, 0.06, 900), road, 0, 0.0)
    for x in (-1.6, 1.6): K.box((x, 0.065, 430), (0.45, 0.02, 900), pm("#6a7888", 0.8), 0, 0.0)
    for k in range(60):                                  # marker poles with rags, snow ridges ploughed along the road
        z = -15 + k * 15
        for sx in (-1, 1):
            K.cyl((sx * 4.2, 0.9, z), 0.04, 1.8, wood("#5a4a32", "#3a3020", 8, 0.8), 6)
            K.box((sx * 4.2 + 0.12, 1.65, z), (0.25, 0.18, 0.02), cloth("#a83a2a"), 0, 0.0)
            fsphere(K, (sx * 3.6, 0.15, z), 1.0, SNOW, 10, (0.6, 0.3, 8))
    for k in range(40):                                  # pressure ridges and snow drifts on the ice
        x, z = rnd.uniform(-200, 200), rnd.uniform(0, 600)
        if abs(x) < 8: continue
        fsphere(K, (x, 0.1, z), rnd.uniform(1, 4), SNOW, 10, (2.5, 0.25, 0.8))
    # the controller's post: a little hut of boards and snow blocks, a lantern, a sign
    K.box((7.5, 1.0, 8), (2.0, 2.0, 2.0), wood("#5a4a32", "#3a3020", 6, 0.8), 0, 0.03); K.box((7.5, 2.1, 8), (2.4, 0.2, 2.4), SNOW, 0, 0.08)
    for k in range(8): K.box((6.2 + (k % 4) * 0.5, 0.25 + (k // 4) * 0.5, 6.6), (0.48, 0.48, 0.48), SNOW, 0.1 * k, 0.04)
    K.cyl((5.4, 1.0, 6.5), 0.04, 2.0, wood("#5a4a32", "#3a3020", 8, 0.8), 6)
    K.box((5.4, 1.8, 6.45), (1.2, 0.35, 0.04), wood("#c8c0a0", "#8a8468", 12, 0.8), 0, 0.01)
    text("ДОРОГА ЖИЗНИ", (5.4, 1.8, 6.42), 0.12, pm("#a81e22", 0.6), 0, "sans", 0.002, fit=1.1)
    K.cyl((6.6, 1.5, 7.0), 0.08, 0.25, em("#ffb060", 8.0), 8)
    point((6.6, 1.6, 6.8), 40, (1.0, 0.65, 0.3), 0.05)
    # AA gun with crew position, a tent, crates, a broken-through truck nose-down in black water
    K.cyl((-14, 0.5, 22), 1.2, 1.0, SNOW, 16)
    K.cyl((-14, 1.4, 22), 0.2, 1.2, pm("#3a4a3a", 0.5, 0.4), 10)
    K.cyl((-13.0, 2.6, 22.5), 0.08, 3.0, pm("#3a4a3a", 0.5, 0.4), 8, "z", None, 0.7, 0, -0.9)
    lathe("ldtent", [(1.8, 0.0), (1.6, 0.4), (0.1, 2.4), (0.0, 2.45)], (-20, 0, 26), cloth("#d8dce0"), 4, math.pi / 4)
    for k in range(5): K.box((-17 + k * 0.6, 0.25, 19), (0.55, 0.5, 0.5), wood("#7a6a4a", "#4a3a24", 10, 0.8), 0.1 * k, 0.02)
    K.cyl((16, -0.05, 60), 3.0, 0.1, pm("#06080c", 0.02), 24)
    truck("ldsunk", (16, -1.4, 60), 0.8, "#3a4a3a", "#5a6050")
    K.build()
    trucks = []
    for k in range(7):
        e = empty(f"ldtr{k}"); kk = Kit(f"ldtk{k}")
        def bags(K2, P, yaw):
            for j in range(9): K2.box(P(-2.4 + (j % 3) * 0.9, 1.35 + (j // 3) * 0.32, (j % 2) * 0.3 - 0.15), (0.8, 0.3, 0.9), cloth(("#c8b88a", "#a89a72", "#d8c8a0")[j % 3]), yaw, 0.08)
        truck(f"ldt{k}", (0, 0, 0), 0.0, "#4a5a42", "#6a6a58", lights=True, load=bags if k % 2 else None, Kx=kk)
        for sd in (-1, 1): kk.box((2.42, 1.42, sd * 0.42), (0.02, 0.12, 0.2), pm("#1a1a1a", 0.6), 0, 0.0)   # blackout hoods
        for o in kk.build(): o.parent = e
        trucks.append(e)
    beams = [searchlight(f"hl{k}", (0, 1.4, 0), 0, -0.08, 22, 0.1, 2.2, 1.2, (1.0, 0.85, 0.6)) for k in range(7)]
    lib.light("SUN", (0, 0, 10), 0.6, (0.6, 0.72, 1.0), math.radians(1), (math.radians(65), 0, math.radians(140)))
    moon = Kit("ldmoon"); moon.sphere((-200, 300, 900), 18, em("#e8ecff", 8.0), 20); moon.build()
    area((0, 40, -30), (0, 0, 40), 4000, (0.5, 0.6, 1.0), 40)
    lamps = [point((0, 1.3, 0), 60, (1.0, 0.8, 0.5), 0.1) for _ in range(7)]
    def update(f):
        u = max(0, f - 2050)
        for k, e in enumerate(trucks):
            z = 10 + k * 16 - 0.15 * u; x = 0.0
            e.location = T(x, 0.02, z); e.rotation_euler = (0, 0, math.pi / 2)
            aim(beams[k], (x, 1.42, z - 2.45), math.pi, -0.06)
            lamps[k].location = T(x, 1.2, z - 4.0)
    update(2134)
    return {"update": update}
