# Shared kit for the chapter 11 (1944) and chapter 14 (after the war) sets (c11_*, c14_*). Three.js layout coordinates
# (y up, lib.T maps to Blender). Batched geometry through kit_sbpw.Kit; skies, terrain, trees, period buildings (cell
# facades that can be intact, lit or ruined), wire fences, guard towers, landing craft, trucks, jeeps, flags.
# Blender 4.5 + 5.x safe (no Nishita sky, no version-specific node names beyond those lib.py already uses).
import bpy, math, random
import numpy as np
from mathutils import Vector, Matrix, noise
import lib
from lib import T, hexc
from sets import kit_sbpw as SB
from sets.kit_sbpw import pm, em, text, sign, poster, paper, window_glow, cloth, iron, brass, gold, glassm
from sets import ikit as IK
from sets.void import lathe, tube, worn, mat_once, link, mesh_obj, fire, flame, flame_mat, smoke_mat, smoke_column
from sets import front as FR

R90 = math.pi / 2

class Kit(SB.Kit):
    """kit_sbpw.Kit with fast cylinders / cones / spheres (bmesh.ops.create_cone gets slow on a big bmesh)"""
    def cyl(self, c, r, h, m, seg=16, axis="y", r2=None, yaw=0.0, bev=0.0, pitch=0.0, roll=0.0):
        bm, _ = self._get(bev)
        a = {"y": Matrix.Identity(4), "x": Matrix.Rotation(R90, 4, "Y"), "z": Matrix.Rotation(R90, 4, "X")}[axis]
        M = Matrix.Translation(T(*c)) @ SB._rot(yaw, pitch, roll) @ a
        r2 = r if r2 is None else r2
        bot = [bm.verts.new(M @ Vector((r * math.cos(k / seg * math.tau), r * math.sin(k / seg * math.tau), -h / 2))) for k in range(seg)]
        if r2 > 1e-6: top = [bm.verts.new(M @ Vector((r2 * math.cos(k / seg * math.tau), r2 * math.sin(k / seg * math.tau), h / 2))) for k in range(seg)]
        else: top = [bm.verts.new(M @ Vector((0, 0, h / 2)))] * seg
        vs = list(bot) + list(dict.fromkeys(top))
        for k in range(seg):
            k2 = (k + 1) % seg
            if r2 > 1e-6: bm.faces.new((bot[k], bot[k2], top[k2], top[k]))
            else: bm.faces.new((bot[k], bot[k2], top[0]))
        bm.faces.new(list(reversed(bot)))
        if r2 > 1e-6: bm.faces.new(top)
        ax = (M.to_3x3() @ Vector((0, 0, 1))).normalized()
        self._finish(vs, m, bev, ax)
    def sphere(self, c, r, m, seg=12, scale=(1, 1, 1), bev=0.0):
        bm, _ = self._get(bev)
        M = Matrix.Translation(T(*c)) @ Matrix.Diagonal((scale[0], scale[2], scale[1], 1.0))
        nv = max(6, seg // 2); top = bm.verts.new(M @ Vector((0, 0, r))); botv = bm.verts.new(M @ Vector((0, 0, -r)))
        rings = []
        for j in range(1, nv):
            th = math.pi * j / nv
            rings.append([bm.verts.new(M @ Vector((r * math.sin(th) * math.cos(k / seg * math.tau), r * math.sin(th) * math.sin(k / seg * math.tau), r * math.cos(th)))) for k in range(seg)])
        for k in range(seg):
            k2 = (k + 1) % seg
            bm.faces.new((top, rings[0][k], rings[0][k2]))
            bm.faces.new((botv, rings[-1][k2], rings[-1][k]))
            for j in range(len(rings) - 1): bm.faces.new((rings[j][k], rings[j + 1][k], rings[j + 1][k2], rings[j][k2]))
        self._finish([top, botv] + [v for rr in rings for v in rr], m, bev, True)

# ------------------------------------------------------------------ grouping
def grab(fn, *a, **k):
    """run a builder and return the objects it created"""
    before = set(bpy.data.objects[:]); fn(*a, **k); return [o for o in bpy.data.objects if o not in before]
def rig(objs, pivot):
    """parent objects to an empty at pivot (three coords); scale / move the empty to animate them together"""
    e = bpy.data.objects.new("rig", None); link(e); e.location = T(*pivot); bpy.context.view_layer.update()
    inv = e.matrix_world.inverted()
    for o in objs:
        if o.parent is None: o.parent = e; o.matrix_parent_inverse = inv
    return e
def recolor(objs, old_key, m):
    for o in objs:
        if getattr(o.data, "materials", None):
            for i, s in enumerate(o.data.materials):
                if s and old_key in s.name: o.data.materials[i] = m

# ------------------------------------------------------------------ sky + sun
SKIES = {
    "day":    dict(z="#2a5aa6", m="#6c9ad6", h="#d8e4ec", g="#4e524a", sun=(1.0, 0.95, 0.86), glow=0.25, cloud="#ffffff", cl=0.5, cs=(1.0, 0.98, 0.95)),
    "golden": dict(z="#2a4888", m="#7c8cb8", h="#f8c88c", g="#3e342c", sun=(1.0, 0.74, 0.44), glow=0.8, cloud="#fff0dc", cl=0.45, cs=(1.0, 0.7, 0.42)),
    "dawn":   dict(z="#26305c", m="#7a6c9c", h="#f6aa84", g="#363038", sun=(1.0, 0.68, 0.46), glow=0.9, cloud="#f8c8b0", cl=0.5, cs=(1.0, 0.62, 0.42)),
    "dusk":   dict(z="#121636", m="#583a60", h="#f28a4a", g="#262024", sun=(1.0, 0.5, 0.25), glow=1.0, cloud="#5a3448", cl=0.55, cs=(1.0, 0.45, 0.15)),
    "night":  dict(z="#02040c", m="#08122c", h="#1c2a4c", g="#05070c", sun=(0.62, 0.76, 1.0), glow=0.25, cloud="#1e2840", cl=0.4, cs=(0.5, 0.6, 0.9), stars=True),
    "grey":   dict(z="#56606e", m="#8a929c", h="#c6cacd", g="#46484a", sun=(0.9, 0.92, 0.95), glow=0.05, cloud="#9aa0aa", cl=0.85, cs=(0.95, 0.95, 0.95)),
    "snow":   dict(z="#66768e", m="#a4b0c2", h="#e4e8ee", g="#9aa0aa", sun=(0.95, 0.95, 1.0), glow=0.12, cloud="#c4cad4", cl=0.8, cs=(1.0, 0.95, 0.9)),
}
def sky(kind, sun_dir, strength=1.0, cam_strength=1.0):
    """gradient sky with a sun glow + disc, a band of clouds above the horizon (lit near the sun), stars at night.
    sun_dir = three-space direction TOWARDS the sun."""
    P = SKIES[kind]; W = bpy.context.scene.world; nt = W.node_tree; n = nt.nodes; l = nt.links
    for x in list(n): n.remove(x)
    out = n.new("ShaderNodeOutputWorld"); co = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(co.outputs["Generated"], sep.inputs[0])
    mr = n.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.15; mr.inputs["From Max"].default_value = 1.0; l.new(sep.outputs["Z"], mr.inputs["Value"])
    r = n.new("ShaderNodeValToRGB"); l.new(mr.outputs["Result"], r.inputs["Fac"]); e = r.color_ramp.elements
    e[0].position, e[0].color = 0.0, (*hexc(P["g"]), 1)
    for p, c in ((0.115, P["g"]), (0.13, P["h"]), (0.3, P["m"])): el = e.new(p); el.color = (*hexc(c), 1)
    e[-1].position, e[-1].color = 1.0, (*hexc(P["z"]), 1)
    sd = T(*sun_dir).normalized()
    dot = n.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; l.new(co.outputs["Generated"], dot.inputs[0]); dot.inputs[1].default_value = tuple(sd)
    mx0 = n.new("ShaderNodeMath"); mx0.operation = "MAXIMUM"; mx0.inputs[1].default_value = 0.0; l.new(dot.outputs["Value"], mx0.inputs[0])
    def pw(e_, k_):
        p = n.new("ShaderNodeMath"); p.operation = "POWER"; p.inputs[1].default_value = e_; l.new(mx0.outputs[0], p.inputs[0])
        m = n.new("ShaderNodeMath"); m.operation = "MULTIPLY"; m.inputs[1].default_value = k_; l.new(p.outputs[0], m.inputs[0]); return m
    g1, g2 = pw(6, 0.35 * P["glow"]), pw(60, 0.9 * P["glow"])
    gl = n.new("ShaderNodeMath"); gl.operation = "ADD"; l.new(g1.outputs[0], gl.inputs[0]); l.new(g2.outputs[0], gl.inputs[1])
    add = n.new("ShaderNodeMix"); add.data_type = "RGBA"; add.blend_type = "ADD"; l.new(gl.outputs[0], add.inputs[0]); l.new(r.outputs["Color"], add.inputs[6]); add.inputs[7].default_value = (*P["cs"], 1)
    # clouds projected on a plane, banded above the horizon
    zp = n.new("ShaderNodeMath"); zp.operation = "ADD"; zp.inputs[1].default_value = 0.1; l.new(sep.outputs["Z"], zp.inputs[0])
    px = n.new("ShaderNodeMath"); px.operation = "DIVIDE"; l.new(sep.outputs["X"], px.inputs[0]); l.new(zp.outputs[0], px.inputs[1])
    py = n.new("ShaderNodeMath"); py.operation = "DIVIDE"; l.new(sep.outputs["Y"], py.inputs[0]); l.new(zp.outputs[0], py.inputs[1])
    cmb = n.new("ShaderNodeCombineXYZ"); l.new(px.outputs[0], cmb.inputs[0]); l.new(py.outputs[0], cmb.inputs[1])
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.6, 1.5, 1.0); l.new(cmb.outputs[0], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.1; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.6; l.new(mp.outputs[0], nz.inputs["Vector"])
    cov = n.new("ShaderNodeValToRGB"); l.new(nz.outputs["Fac"], cov.inputs["Fac"]); cov.color_ramp.elements[0].position = 1.0 - P["cl"] * 0.75; cov.color_ramp.elements[1].position = min(0.99, 1.0 - P["cl"] * 0.75 + 0.2)
    band = n.new("ShaderNodeMapRange"); band.inputs["From Min"].default_value = 0.0; band.inputs["From Max"].default_value = 0.08; l.new(sep.outputs["Z"], band.inputs["Value"])
    fade = n.new("ShaderNodeMapRange"); fade.inputs["From Min"].default_value = 0.8; fade.inputs["From Max"].default_value = 0.3; l.new(sep.outputs["Z"], fade.inputs["Value"])
    m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; l.new(cov.outputs["Color"], m1.inputs[0]); l.new(band.outputs["Result"], m1.inputs[1])
    m2 = n.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; l.new(m1.outputs[0], m2.inputs[0]); l.new(fade.outputs["Result"], m2.inputs[1])
    lit = n.new("ShaderNodeMath"); lit.operation = "POWER"; lit.inputs[1].default_value = 3.0; l.new(mx0.outputs[0], lit.inputs[0])
    cc = n.new("ShaderNodeMix"); cc.data_type = "RGBA"; l.new(lit.outputs[0], cc.inputs[0]); cc.inputs[6].default_value = (*hexc(P["cloud"]), 1); cc.inputs[7].default_value = (*[min(4, v * 1.6) for v in P["cs"]], 1)
    mc = n.new("ShaderNodeMix"); mc.data_type = "RGBA"; l.new(m2.outputs[0], mc.inputs[0]); l.new(add.outputs[2], mc.inputs[6]); l.new(cc.outputs[2], mc.inputs[7])
    last = mc
    if P.get("stars"):
        vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 260; l.new(co.outputs["Generated"], vo.inputs["Vector"])
        st = lib.ramp(n, l, vo.outputs["Distance"], [(0.0, (3.0, 3.0, 3.2)), (0.05, (0, 0, 0))])
        up = n.new("ShaderNodeMapRange"); up.inputs["From Min"].default_value = 0.05; up.inputs["From Max"].default_value = 0.3; l.new(sep.outputs["Z"], up.inputs["Value"])
        sm = n.new("ShaderNodeMix"); sm.data_type = "RGBA"; sm.blend_type = "ADD"; l.new(up.outputs["Result"], sm.inputs[0]); l.new(last.outputs[2], sm.inputs[6]); l.new(st.outputs["Color"], sm.inputs[7]); last = sm
    disc = pw(4000 if not P.get("stars") else 9000, 1.0)
    ds = n.new("ShaderNodeMix"); ds.data_type = "RGBA"; ds.blend_type = "ADD"; l.new(disc.outputs[0], ds.inputs[0]); l.new(last.outputs[2], ds.inputs[6])
    ds.inputs[7].default_value = (30.0, 22.0, 12.0, 1) if not P.get("stars") else (6.0, 7.0, 8.0, 1)
    b1 = n.new("ShaderNodeBackground"); b1.inputs[1].default_value = strength; l.new(ds.outputs[2], b1.inputs[0])
    b2 = n.new("ShaderNodeBackground"); b2.inputs[1].default_value = cam_strength; l.new(ds.outputs[2], b2.inputs[0])
    lp = n.new("ShaderNodeLightPath"); mx = n.new("ShaderNodeMixShader"); l.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); l.new(b1.outputs[0], mx.inputs[1]); l.new(b2.outputs[0], mx.inputs[2])
    l.new(mx.outputs[0], out.inputs["Surface"])
def sun(sun_dir, energy, col, angle=1.5):
    """sun lamp shining FROM sun_dir (three, towards the sun)"""
    o = lib.light("SUN", T(0, 50, 0), energy, col, math.radians(angle)); lib.look_at(o, o.location - T(*sun_dir)); return o
def fill(c, target, energy, col, size, size_y=None):
    o = IK.area(c, target, energy, col, size, size_y)
    for a in ("visible_camera", "visible_glossy"):
        try: setattr(o, a, False)
        except Exception: pass
    return o
def lamp(c, energy, col=(1.0, 0.68, 0.36), r=0.05):
    o = IK.point(c, energy, col, r)
    try: o.visible_camera = False
    except Exception: pass
    return o

# ------------------------------------------------------------------ terrain + ground materials
def ground(name, x0, x1, z0, z1, st, H, mat, skip=None):
    nx, nz = int((x1 - x0) / st) + 1, int((z1 - z0) / st) + 1
    vs, fs = [], []
    for j in range(nz):
        for i in range(nx):
            x, z = x0 + i * st, z0 + j * st; vs.append(T(x, H(x, z), z))
    for j in range(nz - 1):
        for i in range(nx - 1):
            if skip and skip(x0 + (i + 0.5) * st, z0 + (j + 0.5) * st): continue
            a = j * nx + i; fs.append((a, a + 1, a + nx + 1, a + nx))
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs); me.update()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat); return link(bpy.data.objects.new(name, me))
def nz2(x, z, s=0.05, o=0.0): return noise.noise(Vector((x * s, z * s, o)))
def _mixmat(name, stops, s_big=0.08, s_fine=3.0, rough=0.85, bump_s=0.4, fine_k=0.35, coords="Object"):
    m = lib.principled(name, hexc(stops[0][1]), rough); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    big = n.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = s_big; big.inputs["Detail"].default_value = 6; l.new(tc.outputs[coords], big.inputs["Vector"])
    r = lib.ramp(n, l, big.outputs["Fac"], [(p, hexc(c)) for p, c in stops])
    fine = n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = s_fine; fine.inputs["Detail"].default_value = 10; l.new(tc.outputs[coords], fine.inputs["Vector"])
    mu = n.new("ShaderNodeMix"); mu.data_type = "RGBA"; mu.blend_type = "MULTIPLY"; mu.inputs[0].default_value = fine_k; l.new(r.outputs["Color"], mu.inputs[6]); l.new(fine.outputs["Color"], mu.inputs[7])
    l.new(mu.outputs[2], b.inputs["Base Color"]); lib.bump(n, l, fine.outputs["Fac"], bump_s, 0.05)
    return m
def grass_mat(name="c_grass", a="#3e6224", b2="#6e8a34", dry="#a8964e"):
    return mat_once(name, lambda: _mixmat(name, [(0.3, "#2a4418"), (0.45, a), (0.6, b2), (0.75, dry)], 0.06, 2.5, 0.9, 0.5))
def snow_mat(name="c_snow"):
    def mk():
        m = _mixmat(name, [(0.35, "#c8d4e6"), (0.5, "#e6ecf4"), (0.7, "#f8fafe")], 0.1, 1.2, 0.55, 0.25, 0.12)
        b = m.node_tree.nodes["Principled BSDF"]
        s = IK._sock(b, "Subsurface Weight")
        if s: s.default_value = 0.0
        s = IK._sock(b, "Sheen Weight")
        if s: s.default_value = 0.4
        return m
    return mat_once(name, mk)
def sand_mat(name="c_sand", a="#c8ae7c", b2="#a88e60", wet=False):
    def mk():
        m = _mixmat(name, [(0.35, b2), (0.6, a), (0.8, "#d8c49a")] if not wet else [(0.35, "#5a4a36"), (0.6, "#7a6648"), (0.8, "#8a7656")], 0.07, 4, 0.9 if not wet else 0.25, 0.3)
        t, n, l = lib.nodes(m); tc = n.new("ShaderNodeTexCoord"); wv = n.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 1.6; wv.inputs["Distortion"].default_value = 3
        l.new(tc.outputs["Object"], wv.inputs["Vector"]); lib.bump(n, l, wv.outputs["Fac"], 0.3, 0.03)
        return m
    return mat_once(name + str(wet), mk)
def mud_mat(name="c_mud"): return mat_once(name, lambda: _mixmat(name, [(0.3, "#2a1e14"), (0.5, "#4a3626"), (0.7, "#6a5236")], 0.08, 3, 0.75, 0.5))
def water_mat(name="c_water", deep="#0c2438", shallow="#2a5a66", rough=0.08):
    def mk():
        m = lib.principled(name, hexc(deep), rough); t, n, l = lib.nodes(m); b = n["Principled BSDF"]
        tc = n.new("ShaderNodeTexCoord"); mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 0.35, 1.0); l.new(tc.outputs["Object"], mp.inputs["Vector"])
        w1 = n.new("ShaderNodeTexWave"); w1.inputs["Scale"].default_value = 0.25; w1.inputs["Distortion"].default_value = 8; w1.inputs["Detail"].default_value = 4; l.new(mp.outputs[0], w1.inputs["Vector"])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.2; nz.inputs["Detail"].default_value = 10; l.new(tc.outputs["Object"], nz.inputs["Vector"])
        hh = n.new("ShaderNodeMath"); hh.operation = "MULTIPLY_ADD"; hh.inputs[1].default_value = 0.6; l.new(w1.outputs["Fac"], hh.inputs[0]); l.new(nz.outputs["Fac"], hh.inputs[2])
        lib.bump(n, l, hh.outputs[0], 0.35, 0.3)
        r = lib.ramp(n, l, nz.outputs["Fac"], [(0.35, hexc(deep)), (0.7, hexc(shallow))]); l.new(r.outputs["Color"], b.inputs["Base Color"])
        return m
    return mat_once(name, mk)
def foliage_mat(name, a, b2):
    def mk():
        m = _mixmat(name, [(0.35, b2), (0.55, a), (0.75, "#" + "".join(f"{min(255, int(int(a[i:i + 2], 16) * 1.25)):02x}" for i in (1, 3, 5)))], 1.2, 8, 0.8, 0.9, 0.4)
        s = IK._sock(m.node_tree.nodes["Principled BSDF"], "Subsurface Weight")
        return m
    return mat_once(name, mk)
def bark_mat(name="c_bark", a="#4a3828", b2="#2a1e14"): return mat_once(name, lambda: worn(name, a, b2, 0.9, 0.0, 6, 0.5, "#1a120c"))
def birch_mat(name="c_birch"):
    def mk():
        m = lib.principled(name, hexc("#eae6dc"), 0.7); t, n, l = lib.nodes(m); tc = n.new("ShaderNodeTexCoord")
        mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (8, 8, 0.8); l.new(tc.outputs["Object"], mp.inputs["Vector"])
        nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 3; l.new(mp.outputs[0], nz.inputs["Vector"])
        r = lib.ramp(n, l, nz.outputs["Fac"], [(0.28, hexc("#1e1a18")), (0.33, hexc("#eae6dc")), (0.7, hexc("#d8d0c4"))]); l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
        return m
    return mat_once(name, mk)
def concrete(name="c_conc", a="#8a8478"): return mat_once(name + a, lambda: worn(name + a, a, "#5a564e", 0.9, 0.0, 2, 0.6, "#4a463e"))
def plaster(name, a): return mat_once("pl" + name + a, lambda: SB.grime("c_pl" + name, a, 0.3, 3.0, 0.88))
def brickm(name="c_brick", a="#8a4a36", b2="#6a3424"): return mat_once(name + a, lambda: SB.brick(name + a, a, b2, "#5a4e46", 4.0))
def planks(name, a, b2, along="Y", w=0.16, L=1.6): return mat_once(name, lambda: IK.planks(name, a, b2, along, w, L, 0.7, 0.05))

# ------------------------------------------------------------------ trees (batched)
def pine(K, x, y, z, h, rnd, M, snow=False):
    """spruce: trunk + stacked needle tiers (cones), a snow cap on each tier in winter"""
    K.cyl((x, y + h * 0.45, z), 0.02 * h + 0.04, h * 0.9, M["bark"], 8)
    n = 6 + int(h > 12)
    for i in range(n):
        f = i / n; r = (0.3 * h * (1 - f) ** 0.95 + 0.05 * h) * rnd.uniform(0.85, 1.1); th = 0.3 * h * (1 - 0.4 * f)
        cy_ = y + h * (0.22 + 0.72 * f) + th / 2 - th * 0.35
        m = M["ndl"] if (i + int(x * 3)) % 3 else M["ndl2"]
        K.cyl((x + rnd.uniform(-0.05, 0.05) * h, cy_, z + rnd.uniform(-0.05, 0.05) * h), r, th, m, 11, "y", 0.0, rnd.uniform(0, 6))
        if snow: K.cyl((x, cy_ + th * 0.18, z), r * 0.82, th * 0.66, M["snow"], 11, "y", 0.0, rnd.uniform(0, 6))
def pine_mats(snow=False):
    return dict(bark=bark_mat("c_pbark", "#4a3424", "#22160e"), ndl=foliage_mat("c_ndl", "#1e4a2a", "#0e2a18"), ndl2=foliage_mat("c_ndl2", "#2a5a30", "#123a1e"), snow=snow_mat())
def birch(K, x, y, z, h, rnd, M):
    K.cyl((x, y + h * 0.4, z), 0.012 * h + 0.05, h * 0.8, M["birch"], 8)
    for k in range(7):
        a = rnd.random() * math.tau; d = rnd.uniform(0.05, 0.16) * h; r = rnd.uniform(0.1, 0.17) * h
        K.sphere((x + d * math.cos(a), y + h * rnd.uniform(0.55, 0.92), z + d * math.sin(a)), r, M["leaf"] if k % 2 else M["leaf2"], 10, (1.0, 0.8, 1.0))
def leafy(K, x, y, z, h, rnd, M, bare=False):
    """broad tree (oak / plane / linden): trunk, two limbs, a crown of foliage clumps (bare in winter)"""
    K.cyl((x, y + h * 0.25, z), 0.035 * h + 0.06, h * 0.5, M["bark"], 9)
    for s in (-1, 1): K.cyl((x + s * 0.08 * h, y + h * 0.55, z), 0.02 * h, h * 0.35, M["bark"], 7, "y", None, 0, 0, s * 0.45)
    if bare:
        for k in range(9):
            a = rnd.random() * math.tau
            K.cyl((x + 0.12 * h * math.cos(a), y + h * rnd.uniform(0.6, 0.9), z + 0.12 * h * math.sin(a)), 0.008 * h, 0.35 * h, M["bark"], 5, "y", None, yaw=a, pitch=rnd.uniform(-0.7, 0.7), roll=rnd.uniform(-0.7, 0.7))
        return
    for k in range(9):
        a = rnd.random() * math.tau; d = rnd.uniform(0.0, 0.22) * h; r = rnd.uniform(0.16, 0.24) * h
        K.sphere((x + d * math.cos(a), y + h * rnd.uniform(0.62, 0.88), z + d * math.sin(a)), r, M["leaf"] if k % 3 else M["leaf2"], 12, (1.0, 0.78, 1.0))
def tree_mats(season="summer"):
    if season == "autumn": a, b2, a2, b3 = "#8a7a2a", "#4a4a18", "#a8642a", "#5a3414"
    else: a, b2, a2, b3 = "#4a7a2a", "#24441a", "#6a8a34", "#34501e"
    return dict(bark=bark_mat(), birch=birch_mat(), leaf=foliage_mat("c_leaf" + season, a, b2), leaf2=foliage_mat("c_leaf2" + season, a2, b3), snow=snow_mat())
def hedge(K, x0, z0, x1, z1, h, rnd, M):
    L = math.hypot(x1 - x0, z1 - z0); n = max(2, int(L / 0.9))
    for k in range(n + 1):
        f = k / n; x, z = x0 + (x1 - x0) * f, z0 + (z1 - z0) * f
        K.sphere((x + rnd.uniform(-0.2, 0.2), h * rnd.uniform(0.45, 0.6), z + rnd.uniform(-0.2, 0.2)), h * rnd.uniform(0.5, 0.65), M["leaf2"] if k % 2 else M["leaf"], 10, (1.0, 0.85, 1.0))

# ------------------------------------------------------------------ buildings
def _P(x, z, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return lambda lx, ly, lz: (x + lx * c + lz * s, ly, z - lx * s + lz * c)
def house(K, x, z, w, d, floors, yaw, wall, trim, roofm, win, rnd, fh=3.0, roof="gable", ruin=0.0, shutters=None, door="#4a2a1a",
          snow=None, base=None, cornice=True, lit=0.0, dark=None, sill_snow=False, flowers=None, balcony=None, signs=()):
    """townhouse whose facade faces local -z (the camera at yaw 0). Facade cells: piers, spandrels, framed windows (lit
    or dark glass), shutters, sills, a cornice and floor bands. ruin > 0: a jagged broken skyline, empty window holes,
    no roof, rubble at the foot. roof: gable | mansard | flat. Returns the top height."""
    P = _P(x, z, yaw); ncol = max(2, int(w / 2.3)); cw = w / ncol; ww = cw * 0.46; wh = fh * 0.56; sl = fh * 0.24
    H = floors * fh; fz = -d / 2
    dark = dark or pm("#141218", 0.08)
    sky = [H * (1 - ruin * rnd.uniform(0.15, 0.85)) if ruin else H + 1 for _ in range(ncol)]
    if ruin:
        for k in range(1, ncol): sky[k] = 0.5 * sky[k] + 0.5 * sky[k - 1]
    B = lambda c, s, m, bev=0.01: K.box(P(*c), s, m, yaw, bev)
    if not ruin:
        B((0, H / 2, 0.15), (w - 0.02, H, d - 0.3), wall, 0.0)
    else:
        for s in (-1, 1): B((s * (w / 2 - 0.15), min(sky[0 if s < 0 else -1], H) / 2, 0), (0.3, min(sky[0 if s < 0 else -1], H), d), wall, 0.0)
        B((0, 0.2, 0), (w - 0.4, 0.4, d - 0.4), pm("#2a221c", 0.9), 0.0)
    if base: B((0, 0.45, fz - 0.03), (w + 0.04, 0.9, 0.12), base, 0.01)
    for fi in range(floors):
        y0 = fi * fh
        for ci in range(ncol):
            lx = -w / 2 + (ci + 0.5) * cw; top = sky[ci]
            if y0 >= top: continue
            hh = min(fh, top - y0)
            pw_ = (cw - ww) / 2
            for s in (-1, 1): B((lx + s * (ww / 2 + pw_ / 2), y0 + hh / 2, fz), (pw_ + 0.002, hh, 0.3), wall, 0.0)
            ground_door = fi == 0 and ci == ncol // 2 and door
            if ground_door:
                dh = min(hh, fh * 0.8)
                B((lx, y0 + dh + (hh - dh) / 2, fz), (ww, hh - dh, 0.3), wall, 0.0)
                B((lx, y0 + dh / 2, fz + 0.12), (ww * 0.9, dh, 0.06), pm(door, 0.5) if isinstance(door, str) else door, 0.01)
                B((lx, y0 + dh + 0.08, fz - 0.06), (ww * 1.1, 0.16, 0.1), trim, 0.01)
                B((lx + ww * 0.3, y0 + dh * 0.5, fz + 0.06), (0.05, 0.05, 0.06), brass(), 0.005)
                B((lx, 0.08, fz - 0.25), (ww * 1.2, 0.16, 0.5), base or trim, 0.01)
                continue
            if hh < sl + 0.1: B((lx, y0 + hh / 2, fz), (ww, hh, 0.3), wall, 0.0); continue
            B((lx, y0 + sl / 2, fz), (ww, sl, 0.3), wall, 0.0)
            wt = min(wh, hh - sl)
            if hh > sl + wh: B((lx, y0 + sl + wh + (hh - sl - wh) / 2, fz), (ww, hh - sl - wh, 0.3), wall, 0.0)
            wy = y0 + sl + wt / 2
            if not ruin or top > y0 + sl + wh + 0.2:
                for s in (-1, 1): B((lx + s * (ww / 2 - 0.035), wy, fz - 0.03), (0.07, wt, 0.1), trim, 0.008)
                B((lx, y0 + sl - 0.03, fz - 0.1), (ww + 0.16, 0.07, 0.24), trim, 0.01)
                if sill_snow: B((lx, y0 + sl + 0.03, fz - 0.1), (ww + 0.12, 0.06, 0.2), snow_mat(), 0.02)
                if wt > wh - 0.01: B((lx, y0 + sl + wh + 0.05, fz - 0.06), (ww + 0.14, 0.1, 0.16), trim, 0.01)
            if ruin:
                if rnd.random() < 0.25 and top > y0 + sl + wh: B((lx, wy, fz + 0.1), (ww - 0.07, wt, 0.04), dark, 0.0)
                continue
            glow = lit > 0 and rnd.random() < lit
            B((lx, wy, fz + 0.05), (ww - 0.07, wt, 0.04), win if glow else dark, 0.0)
            B((lx, wy, fz + 0.02), (0.04, wt, 0.05), trim, 0.0); B((lx, y0 + sl + wt * 0.62, fz + 0.02), (ww - 0.07, 0.04, 0.05), trim, 0.0)
            if shutters and fi > 0:
                for s in (-1, 1): B((lx + s * (ww / 2 + ww * 0.24), wy, fz - 0.06), (ww * 0.46, wt, 0.04), shutters, 0.006)
            if flowers and fi == 1 and ci % 2 == 0:
                B((lx, y0 + sl + 0.08, fz - 0.2), (ww * 0.9, 0.16, 0.18), pm("#8a4a2a", 0.7), 0.01)
                for k in range(5): K.sphere(P(lx - ww * 0.36 + k * ww * 0.18, y0 + sl + 0.22, fz - 0.2), 0.07, pm(flowers[k % len(flowers)], 0.6), 6)
            if balcony and fi > 0 and (balcony == "all" or fi == 1):
                B((lx, y0 + 0.05, fz - 0.35), (ww + 0.5, 0.08, 0.6), trim, 0.01)
                for k in range(9): B((lx - ww / 2 - 0.2 + k * (ww + 0.4) / 8, y0 + 0.5, fz - 0.63), (0.025, 0.9, 0.025), iron(), 0.0)
                B((lx, y0 + 0.95, fz - 0.63), (ww + 0.5, 0.04, 0.04), iron(), 0.0)
        if cornice and fi > 0 and not ruin: B((0, y0, fz - 0.06), (w, 0.12, 0.14), trim, 0.01)
    if ruin:
        rubble(K, P(0, 0, fz - 1.4)[0], P(0, 0, fz - 1.4)[2], w * 0.55, 1.2 * floors * ruin, rnd, [wall, trim, pm("#3a3430", 0.9)])
        return max(sky)
    if cornice: B((0, H + 0.12, fz - 0.12), (w + 0.3, 0.24, 0.3), trim, 0.02)
    if roof == "gable":
        rh = d * 0.45; ov = 0.35
        K.quad([P(-w / 2 - 0.2, H, fz - ov), P(w / 2 + 0.2, H, fz - ov), P(w / 2 + 0.2, H + rh, 0), P(-w / 2 - 0.2, H + rh, 0)], roofm)
        K.quad([P(w / 2 + 0.2, H, -fz + ov), P(-w / 2 - 0.2, H, -fz + ov), P(-w / 2 - 0.2, H + rh, 0), P(w / 2 + 0.2, H + rh, 0)], roofm)
        for s in (-1, 1): K.quad([P(s * w / 2, H, fz), P(s * w / 2, H, -fz), P(s * w / 2, H + rh, 0)], wall)
        if snow: K.quad([P(-w / 2 - 0.2, H + 0.06, fz - ov), P(w / 2 + 0.2, H + 0.06, fz - ov), P(w / 2 + 0.2, H + rh + 0.06, 0), P(-w / 2 - 0.2, H + rh + 0.06, 0)], snow)
        cx_ = rnd.uniform(-w / 3, w / 3); B((cx_, H + rh * 0.8, d * 0.15), (0.5, rh * 0.9, 0.5), base or wall, 0.01)
        return H + rh
    if roof == "mansard":
        rh = 2.6; inset = 0.9
        K.quad([P(-w / 2, H, fz), P(w / 2, H, fz), P(w / 2 - 0.1, H + rh, fz + inset), P(-w / 2 + 0.1, H + rh, fz + inset)], roofm)
        B((0, H + rh, 0), (w - 0.2, 0.1, d - 2 * inset), roofm, 0.0)
        for ci in range(ncol):
            lx = -w / 2 + (ci + 0.5) * cw
            B((lx, H + 1.2, fz + 0.45), (ww * 0.8, 1.3, 0.9), wall, 0.01); B((lx, H + 1.15, fz + 0.0), (ww * 0.55, 0.9, 0.04), win if lit and rnd.random() < lit else dark, 0)
            K.quad([P(lx - ww * 0.5, H + 1.85, fz - 0.02), P(lx + ww * 0.5, H + 1.85, fz - 0.02), P(lx, H + 2.25, fz + 0.3)], roofm)
        for k in range(2): B((-w / 3 + k * w * 0.66, H + rh + 0.6, 0.5), (0.6, 1.2, 0.4), plaster("chim", "#b8806a"), 0.01)
        return H + rh
    return H

def rubble(K, x, z, r, h, rnd, mats, n=None):
    n = n or int(30 + r * 12)
    for k in range(n):
        a = rnd.random() * math.tau; d = r * math.sqrt(rnd.random()); f = 1 - d / r
        s = rnd.uniform(0.15, 0.55) * (0.6 + 0.6 * f)
        K.box((x + d * math.cos(a), max(0.05, h * f * rnd.uniform(0.5, 1.0)) - s * 0.2, z + d * math.sin(a) * 0.7), (s * rnd.uniform(0.8, 2.2), s * 0.6, s), rnd.choice(mats), rnd.uniform(0, 3), 0.02, rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6))
    for k in range(int(n * 0.6)):
        a = rnd.random() * math.tau; d = r * 1.3 * math.sqrt(rnd.random())
        K.box((x + d * math.cos(a), 0.04, z + d * math.sin(a) * 0.7), (0.24, 0.07, 0.12), mats[0], rnd.uniform(0, 3), 0.005)

# ------------------------------------------------------------------ fences, towers, sandbags
def wire_fence(K, pts, h, post_m, wire_m, rnd, step=2.6, strands=7, barbs=True, lean=0.0):
    """posts along a polyline, strands of wire, little barbs; lean > 0 tilts the top strands outward (local -z of each run)"""
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / step)); yaw = math.atan2(-(b[1] - a[1]), b[0] - a[0])
        for k in range(n + 1):
            f = k / n; x, z = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            K.box((x, h / 2, z), (0.14, h, 0.14), post_m, yaw + rnd.uniform(-0.05, 0.05), 0.01, rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03))
            if k < n and k % 2 == 0: K.box((x + (b[0] - a[0]) / n / 2, h * 0.45, z + (b[1] - a[1]) / n / 2), (L / n * 1.1, 0.06, 0.06), post_m, yaw, 0.005, 0, math.atan2(h * 0.8, L / n))
        for s in range(strands):
            y = 0.3 + (h - 0.4) * s / (strands - 1)
            K.box(((a[0] + b[0]) / 2, y, (a[1] + b[1]) / 2), (L, 0.012, 0.012), wire_m, yaw, 0.0)
            if barbs:
                for k in range(int(L / 0.45)):
                    f = (k + 0.5) / int(L / 0.45)
                    K.box((a[0] + (b[0] - a[0]) * f, y, a[1] + (b[1] - a[1]) * f), (0.06, 0.012, 0.012), wire_m, yaw + 0.8 + k, 0.0)
def coil(K, x0, z0, x1, z1, r, wire_m, turns_per_m=3.0, y=0.0):
    L = math.hypot(x1 - x0, z1 - z0); n = int(L * turns_per_m); yaw = math.atan2(-(z1 - z0), x1 - x0)
    for k in range(n):
        f = (k + 0.5) / n
        K.torus((x0 + (x1 - x0) * f, y + r, z0 + (z1 - z0) * f), r, 0.008, wire_m, 14, 3, "x", yaw, 0, (k % 3 - 1) * 0.15)
def tower(K, x, z, yaw, h, M, rnd):
    """guard tower: splayed legs, cross braces, a ladder, a boarded hut with a pitched roof; returns the searchlight point"""
    P = _P(x, z, yaw); wd = M["wood"]
    for sx in (-1, 1):
        for sz in (-1, 1): K.box(P(sx * 1.15, h / 2, sz * 1.15), (0.2, h + 0.1, 0.2), wd, yaw, 0.01, -sz * 0.06, sx * 0.06)
    for k in range(3):
        y = h * (0.2 + 0.28 * k)
        for s in (-1, 1):
            K.box(P(0, y, s * 1.2), (2.6, 0.12, 0.1), wd, yaw, 0.005, 0, 0.6 if k % 2 else -0.6)
            K.box(P(s * 1.2, y, 0), (0.1, 0.12, 2.6), wd, yaw, 0.005, 0.6 if k % 2 else -0.6, 0)
    for k in range(int(h / 0.35)): K.box(P(0.0, 0.2 + k * 0.35, -1.45), (0.6, 0.05, 0.06), wd, yaw, 0.0)
    for s in (-1, 1): K.box(P(s * 0.3, h / 2, -1.45), (0.07, h, 0.07), wd, yaw, 0.0)
    K.box(P(0, h, 0), (3.0, 0.15, 3.0), wd, yaw, 0.01)
    for s in (-1, 1):
        K.box(P(0, h + 0.55, s * 1.45), (3.0, 1.0, 0.08), M["board"], yaw, 0.005); K.box(P(s * 1.45, h + 0.55, 0), (0.08, 1.0, 3.0), M["board"], yaw, 0.005)
    for sx in (-1, 1):
        for sz in (-1, 1): K.box(P(sx * 1.4, h + 1.3, sz * 1.4), (0.1, 2.6, 0.1), wd, yaw, 0.0)
    K.quad([P(-1.8, h + 2.5, -1.8), P(1.8, h + 2.5, -1.8), P(0, h + 3.3, 0)], M["roof"]); K.quad([P(1.8, h + 2.5, 1.8), P(-1.8, h + 2.5, 1.8), P(0, h + 3.3, 0)], M["roof"])
    K.quad([P(1.8, h + 2.5, -1.8), P(1.8, h + 2.5, 1.8), P(0, h + 3.3, 0)], M["roof"]); K.quad([P(-1.8, h + 2.5, 1.8), P(-1.8, h + 2.5, -1.8), P(0, h + 3.3, 0)], M["roof"])
    if M.get("snow"):
        K.quad([P(-1.8, h + 2.53, -1.8), P(1.8, h + 2.53, -1.8), P(0, h + 3.33, 0)], M["snow"]); K.quad([P(-1.8, h + 2.53, 1.8), P(-1.8, h + 2.53, -1.8), P(0, h + 3.33, 0)], M["snow"])
    sp = P(0.9, h + 1.35, -1.6)
    K.cyl(sp, 0.28, 0.4, iron("#2a2c2e"), 16, "z", None, yaw); K.cyl(P(0.9, h + 1.35, -1.81), 0.24, 0.02, em("#fff4dc", 25), 16, "z", None, yaw)
    K.box(P(0.9, h + 1.08, -1.55), (0.08, 0.3, 0.08), iron(), yaw, 0)
    return sp
def sandbags(K, x, y, z, yaw, n, rows, m, rnd, curve=0.0):
    P = _P(x, z, yaw)
    for r in range(rows):
        for k in range(n - (r % 2)):
            lx = (k - (n - 1) / 2 + (0.5 if r % 2 else 0)) * 0.6; lz = curve * lx * lx
            K.box(P(lx, y + 0.11 + r * 0.2, lz), (0.58, 0.24, 0.34), m, yaw + rnd.uniform(-0.12, 0.12) - 2 * curve * lx, 0.07, rnd.uniform(-0.04, 0.04), rnd.uniform(-0.05, 0.05))
def sandbag_m(): return mat_once("c_sandbag", FR.sandmat)

# ------------------------------------------------------------------ vehicles + boats
def lcvp(K, x, y, z, yaw, ramp, M, rnd, number="PA 26-17"):
    """Higgins boat (LCVP), bow ramp toward local +z: plywood hull, steel ramp hinged at the bow floor (ramp 0 = up, 1 =
    down), coxswain's stand and two machine guns aft, fenders. The deck is at local y 0.15 (troops stand on it)."""
    P = _P(x, z, yaw); hull, ins, st = M["hull"], M["inside"], M["steel"]
    L, Wd, Hs = 10.4, 3.2, 1.65
    K.box(P(0, y - 0.25, 0), (Wd - 0.2, 0.5, L - 0.6), hull, yaw, 0.12)
    K.box(P(0, y + 0.1, 0), (Wd - 0.5, 0.06, L - 1.4), ins, yaw, 0.0)
    for s in (-1, 1):
        K.box(P(s * (Wd / 2 - 0.08), y + Hs / 2 - 0.3, 0), (0.16, Hs + 0.3, L), hull, yaw, 0.04)
        K.box(P(s * (Wd / 2 - 0.2), y + Hs / 2 - 0.2, 0), (0.06, Hs, L - 0.4), ins, yaw, 0.0)
        K.box(P(s * (Wd / 2 - 0.05), y + Hs - 0.42, 0), (0.2, 0.08, L), st, yaw, 0.02)
        for k in range(4): K.cyl(P(s * (Wd / 2 + 0.05), y + 0.55, -3.5 + k * 2.3), 0.1, 0.5, pm("#2a2220", 0.9), 8, "y", None, yaw)
    K.box(P(0, y + Hs / 2, -L / 2 + 0.3), (Wd, Hs + 0.6, 0.6), hull, yaw, 0.05)
    K.box(P(0, y + Hs + 0.25, -L / 2 + 1.0), (1.4, 0.5, 1.0), hull, yaw, 0.04)
    for s in (-1, 1):
        K.cyl(P(s * 1.15, y + Hs + 0.25, -L / 2 + 1.4), 0.04, 0.5, st, 8, "y", None, yaw)
        K.cyl(P(s * 1.15, y + Hs + 0.5, -L / 2 + 1.75), 0.035, 0.9, st, 8, "z", None, yaw)
        K.box(P(s * 1.15, y + Hs + 0.48, -L / 2 + 1.35), (0.12, 0.2, 0.45), st, yaw, 0.01)
    if ramp is None: return P
    a = ramp * math.radians(85); hr = Hs + 0.25
    hz = L / 2 - 0.1; cy_ = y - 0.1 + math.cos(a) * hr / 2; cz = hz + math.sin(a) * hr / 2
    K.box(P(0, cy_, cz), (Wd - 0.15, hr, 0.14), st, yaw, 0.02, a)
    for k in range(5): K.box(P(-0.9 + k * 0.45, cy_, cz - 0.08 * math.cos(a)), (0.08, hr * 0.95, 0.06), M["ramp_in"], yaw, 0.0, a)
    if number: text(number, P(1.62, y + 0.7, -1.0), 0.28, pm("#e8e4d8", 0.7), yaw - R90, "sans", 0.003)
    return P
def truck(K, x, z, yaw, M, canvas=True):
    """2.5 t truck, length along local x (cab at +x): chassis, bonnet with grille, cab, slatted bed with a canvas tilt"""
    P = _P(x, z, yaw); b, dk, tyre = M["body"], M["dark"], M["tyre"]
    K.box(P(0, 0.75, 0), (6.4, 0.25, 1.4), dk, yaw, 0.02)
    K.box(P(2.5, 1.35, 0), (1.3, 0.9, 1.5), b, yaw, 0.12); K.box(P(3.18, 1.3, 0), (0.06, 0.8, 1.1), dk, yaw, 0.01)
    for k in range(8): K.box(P(3.2, 1.0 + k * 0.1, 0), (0.04, 0.03, 1.0), iron("#5a5a50"), yaw, 0)
    for s in (-1, 1): K.box(P(2.5, 1.0, s * 0.95), (1.4, 0.12, 0.5), b, yaw, 0.05); K.cyl(P(3.2, 1.25, s * 0.55), 0.13, 0.08, glassm(), 12, "x", None, yaw)
    K.box(P(1.35, 1.75, 0), (1.1, 1.5, 2.0), b, yaw, 0.08); K.box(P(1.82, 2.05, 0), (0.06, 0.6, 1.7), pm("#1a2228", 0.05), yaw, 0)
    K.box(P(-1.3, 1.25, 0), (4.0, 0.8, 2.2), b, yaw, 0.02)
    for k in range(6): K.box(P(-3.0 + k * 0.7, 1.75, 0), (0.06, 0.25, 2.24), M.get("wood", b), yaw, 0)
    if canvas:
        K.box(P(-1.3, 2.35, 0), (4.0, 1.4, 2.2), M["canvas"], yaw, 0.15)
        for k in range(4): K.box(P(-2.8 + k * 1.0, 2.4, 0), (0.05, 1.5, 2.26), shade_m(M["canvas"]), yaw, 0.02)
    for wx in (2.4, -0.8, -2.2):
        for s in (-1, 1): K.cyl(P(wx, 0.5, s * 0.95), 0.5, 0.32, tyre, 18, "z", None, yaw); K.cyl(P(wx, 0.5, s * 1.1), 0.22, 0.04, b, 12, "z", None, yaw)
    return P
def shade_m(m):
    return m
def jeep(K, x, z, yaw, M):
    P = _P(x, z, yaw); b, tyre = M["body"], M["tyre"]
    K.box(P(0, 0.75, 0), (3.2, 0.5, 1.5), b, yaw, 0.06); K.box(P(1.0, 0.98, 0), (1.1, 0.12, 1.3), b, yaw, 0.04)
    K.box(P(1.62, 0.8, 0), (0.06, 0.55, 1.1), b, yaw, 0.01)
    for k in range(9): K.box(P(1.66, 0.82, -0.4 + k * 0.1), (0.03, 0.4, 0.04), pm("#141410", 0.7), yaw, 0)
    for s in (-1, 1): K.cyl(P(1.67, 0.9, s * 0.48), 0.09, 0.05, glassm(), 12, "x", None, yaw)
    K.box(P(0.35, 1.25, 0), (0.05, 0.45, 1.4), iron("#3a3a34"), yaw, 0.01, 0, -0.2)
    for s in (-1, 1): K.box(P(-0.3, 1.05, s * 0.35), (0.5, 0.12, 0.5), M["seat"], yaw, 0.04); K.box(P(-0.55, 1.3, s * 0.35), (0.1, 0.5, 0.5), M["seat"], yaw, 0.03)
    K.cyl(P(-1.7, 1.0, 0.5), 0.3, 0.12, tyre, 16, "x", None, yaw)
    K.cyl(P(0.25, 1.2, -0.35), 0.17, 0.03, pm("#1a1a1a", 0.6), 16, "x", None, yaw, 0, 0, 0.9)
    for wx in (1.05, -1.05):
        for s in (-1, 1): K.cyl(P(wx, 0.4, s * 0.72), 0.4, 0.26, tyre, 16, "z", None, yaw); K.cyl(P(wx, 0.4, s * 0.84), 0.18, 0.03, b, 10, "z", None, yaw)
    K.cyl(P(-1.4, 1.6, 0.6), 0.012, 2.0, iron(), 4, "y", None, yaw, 0, 0.15)
    return P

def tank_at(name, x, y, z, yaw, col="#58603c", star=None, burnt=False, tilt=0.0, whitewash=False):
    """front.tank (US-style medium) re-used: star None removes the white stars, "red" repaints them (Soviet), "white"
    keeps them; y lifts the whole tank; whitewash swaps the hull paint for winter white."""
    objs = grab(FR.tank, name, x, z, yaw, col, burnt, tilt); keep = []
    for o in objs:
        if f"{name}star" in o.name:
            if star is None: bpy.data.objects.remove(o, do_unlink=True); continue
            elif star == "red": o.data.materials[0] = pm("#b82020", 0.6)
        keep.append(o)
    objs = keep
    if whitewash: recolor(objs, "tank" + col, mat_once("c_whitewash", lambda: worn("c_whitewash", "#d4d4c8", "#5a5e50", 0.7, 0.2, 5, 0.66, "#8a8a7a")))
    if y:
        for o in objs:
            if o.parent is None: o.location.z += y
    return objs

# ------------------------------------------------------------------ flags + posters (numpy images)
def flag_img(kind, w=384, h=256):
    if kind in ("fr", "it", "uk", "us", "jp"): return IK.flag_img(kind, w, h)
    a = IK.canvas(h, w, "#ffffff"); x, y = IK.grid(a)
    if kind == "pl": IK.put(a, y >= 0.5, "#d4213d")
    elif kind == "red": IK.put(a, x >= 0, "#b81c22")
    elif kind == "white": pass
    elif kind == "su":
        IK.put(a, x >= 0, "#c41e1e")
        pts = [(0.17 + 0.07 * math.cos(-R90 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.4), 0.2 + 0.105 * math.sin(-R90 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.4)) for k in range(10)]
        IK.poly(a, pts, "#f0c838")
    elif kind == "un":
        IK.put(a, x >= 0, "#5b92e5"); IK.ellipse(a, 0.5, 0.5, 0.17, 0.26, "#ffffff", ring=0.12); IK.ellipse(a, 0.5, 0.5, 0.1, 0.15, "#ffffff", ring=0.25)
        IK.put(a, (np.abs(x - 0.5) < 0.004) & (np.abs(y - 0.5) < 0.26), "#ffffff"); IK.put(a, (np.abs(y - 0.5) < 0.006) & (np.abs(x - 0.5) < 0.17), "#ffffff")
    elif kind == "nl":
        for i, c in enumerate(("#ae1c28", "#f4f1ea", "#21468b")): IK.put(a, (y >= i / 3) & (y < (i + 1) / 3), c)
    elif kind == "be":
        for i, c in enumerate(("#1a1a1a", "#f4d03a", "#e0303a")): IK.put(a, (x >= i / 3) & (x < (i + 1) / 3), c)
    elif kind == "cn":
        IK.put(a, x >= 0, "#d03030"); IK.rect(a, 0, 0, 0.5, 0.5, "#1a3a8a"); IK.ellipse(a, 0.25, 0.25, 0.08, 0.12, "#ffffff")
    elif kind == "ca":
        IK.put(a, x >= 0, "#c8202c"); IK.rect(a, 0, 0, 0.5, 0.5, "#1d2f6e")
    elif kind == "gr":
        for i in range(9): IK.put(a, (y >= i / 9) & (y < (i + 1) / 9), "#2a5ab8" if i % 2 == 0 else "#ffffff")
    elif kind == "br":
        IK.put(a, x >= 0, "#2a9a3a"); IK.poly(a, [(0.5, 0.12), (0.9, 0.5), (0.5, 0.88), (0.1, 0.5)], "#f4d03a"); IK.ellipse(a, 0.5, 0.5, 0.17, 0.25, "#1a3a8a")
    elif kind == "in":
        for i, c in enumerate(("#f49a32", "#ffffff", "#1a8a3a")): IK.put(a, (y >= i / 3) & (y < (i + 1) / 3), c)
        IK.ellipse(a, 0.5, 0.5, 0.06, 0.09, "#1a2a8a", ring=0.3)
    elif kind == "no":
        IK.put(a, x >= 0, "#ba0c2f"); IK.put(a, (np.abs(x - 0.36) < 0.1) | (np.abs(y - 0.5) < 0.14), "#ffffff"); IK.put(a, (np.abs(x - 0.36) < 0.05) | (np.abs(y - 0.5) < 0.07), "#00205b")
    elif kind == "dk":
        IK.put(a, x >= 0, "#c8102e"); IK.put(a, (np.abs(x - 0.36) < 0.06) | (np.abs(y - 0.5) < 0.08), "#ffffff")
    elif kind == "mx":
        for i, c in enumerate(("#1a7a3a", "#ffffff", "#c8202c")): IK.put(a, (x >= i / 3) & (x < (i + 1) / 3), c)
        IK.ellipse(a, 0.5, 0.5, 0.06, 0.09, "#8a6a2a")
    elif kind == "au":
        IK.put(a, x >= 0, "#1d2f6e"); IK.ellipse(a, 0.25, 0.75, 0.05, 0.07, "#ffffff"); IK.ellipse(a, 0.75, 0.3, 0.03, 0.045, "#ffffff"); IK.ellipse(a, 0.8, 0.7, 0.03, 0.045, "#ffffff")
        IK.rect(a, 0, 0, 0.5, 0.5, "#1d2f6e"); IK.put(a, ((np.abs(x - 0.25) < 0.04) & (y < 0.5)) | ((np.abs(y - 0.25) < 0.05) & (x < 0.5)), "#ffffff"); IK.put(a, ((np.abs(x - 0.25) < 0.02) & (y < 0.5)) | ((np.abs(y - 0.25) < 0.025) & (x < 0.5)), "#c8202c")
    elif kind == "ph":
        IK.put(a, y < 0.5, "#0038a8"); IK.put(a, y >= 0.5, "#ce1126"); IK.poly(a, [(0, 0), (0.43, 0.5), (0, 1)], "#ffffff"); IK.ellipse(a, 0.14, 0.5, 0.04, 0.06, "#fcd116")
    elif kind == "tr":
        IK.put(a, x >= 0, "#e30a17"); IK.ellipse(a, 0.4, 0.5, 0.15, 0.22, "#ffffff"); IK.ellipse(a, 0.44, 0.5, 0.12, 0.18, "#e30a17")
    else:
        IK.put(a, x >= 0, kind if kind.startswith("#") else "#8a8a8a")
    IK.shade(a, 0.06, len(kind) * 7, 16)
    return a
_FM = {}
def flag_m(kind):
    if kind not in _FM: _FM[kind] = IK.img_mat("c_flag" + kind, flag_img(kind), 0.75, sheen=0.4)
    return _FM[kind]
def flagpole(name, x, y, z, h, kind, yaw=0.0, fw=1.5, fh=1.0, wave=0.08, pole_m=None):
    pole_m = pole_m or pm("#d8d4c8", 0.4, 0.3)
    IK.cy(f"{name}p", (x, y + h / 2, z), 0.035, h, pole_m, 10); IK.sph(f"{name}b", (x, y + h + 0.05, z), 0.06, gold())
    IK.flag(f"{name}f", (x - 0.03 * math.cos(yaw), y + h - 0.05, z + 0.03 * math.sin(yaw)), fw, fh, flag_m(kind), yaw, wave, 2.2)
def banner(name, c, w, h, kind, yaw=0.0):
    """flag hung flat from a window / balcony (drapes a little)"""
    return IK.drape(name, c, w, h, flag_m(kind), yaw, 3, 0.03)

def img_panel(name, c, w, h, arr, yaw=0.0, emit=0.0, rough=0.7):
    return IK.panel(name, c, w, h, IK.img_mat(name + "m", arr, rough, emit), yaw)
def poster_img(lines, bg="#e8dcc0", ink="#2a1a1a", w=256, h=360, accent=None, seed=0):
    """printed poster: border, optional coloured band, lines of bitmap capitals [(text, rel height, colour?)]"""
    a = IK.canvas(h, w, bg)
    IK.frame_border(a, 0.04, ink)
    if accent: IK.rect(a, 0.08, 0.42, 0.92, 0.62, accent)
    y = 0.1
    for item in lines:
        s, hgt = item[0], item[1]; col = item[2] if len(item) > 2 else ink
        IK.stamp(a, s, 0.5, y, hgt, col, 1.0, 0.1, "center"); y += hgt * 1.5 + 0.02
    IK.shade(a, 0.08, seed, 12)
    return a
def boards(name, a, b2, w=0.2, L=3.2):
    """vertical weatherboards for walls of any orientation (bricks one board wide, one wall tall)"""
    return mat_once("bd" + name, lambda: SB.brick(name, a, b2, "#1e1610", 1.0, w, L, 0.85))
def beam_cone(name, apex, target, r_end, col=(1.0, 0.95, 0.8), strength=0.25, seg=24):
    """visible searchlight / headlight beam: an open cone from apex toward target, camera-only soft emission"""
    A, B = Vector(apex), Vector(target); d = (B - A); L = d.length; d.normalize()
    up = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0)); u = d.cross(up).normalized(); v = d.cross(u).normalized()
    vs = [tuple(A + d * 0.05 + (u * math.cos(k / seg * math.tau) + v * math.sin(k / seg * math.tau)) * 0.08) for k in range(seg)]
    vs += [tuple(B + (u * math.cos(k / seg * math.tau) + v * math.sin(k / seg * math.tau)) * r_end) for k in range(seg)]
    fs = [(k, (k + 1) % seg, seg + (k + 1) % seg, seg + k) for k in range(seg)]
    me = bpy.data.meshes.new(name); me.from_pydata([T(*p) for p in vs], [], fs)
    uv = me.uv_layers.new()
    for p in me.polygons:
        for li in p.loop_indices: vi = me.loops[li].vertex_index; uv.data[li].uv = ((vi % seg) / seg, 0 if vi < seg else 1)
    o = link(bpy.data.objects.new(name, me))
    m = bpy.data.materials.new(name + "m"); t, n, l = lib.nodes(m)
    for x in list(n): n.remove(x)
    out = n.new("ShaderNodeOutputMaterial"); tr = n.new("ShaderNodeBsdfTransparent"); emn = n.new("ShaderNodeEmission"); emn.inputs["Color"].default_value = (*col, 1)
    add = n.new("ShaderNodeAddShader"); lw = n.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    tc = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["UV"], sep.inputs[0])
    fade = n.new("ShaderNodeMath"); fade.operation = "SUBTRACT"; fade.inputs[0].default_value = 1.0; l.new(sep.outputs[1], fade.inputs[1])
    f2 = n.new("ShaderNodeMath"); f2.operation = "POWER"; f2.inputs[1].default_value = 1.5; l.new(fade.outputs[0], f2.inputs[0])
    m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; l.new(lw.outputs["Facing"], m1.inputs[0]); l.new(f2.outputs[0], m1.inputs[1])
    m2 = n.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; m2.inputs[1].default_value = strength; l.new(m1.outputs[0], m2.inputs[0])
    l.new(m2.outputs[0], emn.inputs["Strength"]); l.new(tr.outputs[0], add.inputs[0]); l.new(emn.outputs[0], add.inputs[1]); l.new(add.outputs[0], out.inputs["Surface"])
    try: m.blend_method = "BLEND"
    except Exception: pass
    me.materials.append(m); IK.hide_from_light(o)
    return o
