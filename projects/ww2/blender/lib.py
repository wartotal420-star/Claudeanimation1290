# Shared Blender helpers for the WW2 sets: procedural materials, bevelled geometry, text, lamps, cards, and the
# three.js -> Blender coordinate map (three (x, y, z), y up -> Blender (-x, z, y), z up; yaw about three +y = about Blender +z).
import bpy, math, random
from mathutils import Vector

def T(x, y, z): return Vector((-x, z, y))
def TS(sx, sy, sz): return (sx, sz, sy)

# ---------------- materials ----------------
def nodes(m):
    m.use_nodes = True; t = m.node_tree; return t, t.nodes, t.links
def principled(name, col, rough=0.6, metal=0.0, emit=None, emit_s=0.0):
    m = bpy.data.materials.new(name); t, n, l = nodes(m); b = n["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit: b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = emit_s
    return m
def hexc(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
def ramp(n, l, fac_out, stops, loc=(-200, 0)):
    r = n.new("ShaderNodeValToRGB"); r.location = loc
    r.color_ramp.elements[0].position, r.color_ramp.elements[0].color = stops[0][0], (*stops[0][1], 1)
    r.color_ramp.elements[1].position, r.color_ramp.elements[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]: e = r.color_ramp.elements.new(p); e.color = (*c, 1)
    l.new(fac_out, r.inputs["Fac"]); return r
def bump(n, l, height_out, strength=0.3, dist=0.02):
    b = n.new("ShaderNodeBump"); b.inputs["Strength"].default_value = strength; b.inputs["Distance"].default_value = dist
    l.new(height_out, b.inputs["Height"]); l.new(b.outputs["Normal"], n["Principled BSDF"].inputs["Normal"])
def wood(name, a, b2, scale=6.0, rough=0.5):
    m = principled(name, hexc(a), rough); t, n, l = nodes(m)
    tc = n.new("ShaderNodeTexCoord"); wv = n.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = scale; wv.inputs["Distortion"].default_value = 6; wv.inputs["Detail"].default_value = 3
    wv.bands_direction = "Y" if hasattr(wv, "bands_direction") else wv.bands_direction
    l.new(tc.outputs["Object"], wv.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 40; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = n.new("ShaderNodeMix"); mx.data_type = "FLOAT"; mx.inputs[0].default_value = 0.25; l.new(wv.outputs["Fac"], mx.inputs[2]); l.new(nz.outputs["Fac"], mx.inputs[3])
    r = ramp(n, l, mx.outputs[0], [(0.2, hexc(b2)), (0.55, hexc(a)), (0.9, tuple(min(1, c * 1.25) for c in hexc(a)))])
    l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"]); bump(n, l, wv.outputs["Fac"], 0.15)
    return m
def tiles(name, a, b2, grout="#3a3430", scale=3.0):
    m = principled(name, hexc(a), 0.35); t, n, l = nodes(m)
    tc = n.new("ShaderNodeTexCoord"); br = n.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = scale; br.offset = 0.0
    br.inputs["Mortar Size"].default_value = 0.012; br.inputs["Color1"].default_value = (*hexc(a), 1); br.inputs["Color2"].default_value = (*hexc(b2), 1); br.inputs["Mortar"].default_value = (*hexc(grout), 1)
    br.inputs["Brick Width"].default_value = 0.5; br.inputs["Row Height"].default_value = 0.25
    ck = n.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = scale * 2; ck.inputs["Color1"].default_value = (*hexc(a), 1); ck.inputs["Color2"].default_value = (*hexc(b2), 1)
    l.new(tc.outputs["Object"], br.inputs["Vector"]); l.new(tc.outputs["Object"], ck.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1.0
    l.new(br.outputs["Fac"], mx.inputs[0]); l.new(ck.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = (*hexc(grout), 1)
    dirt = n.new("ShaderNodeMix"); dirt.data_type = "RGBA"; dirt.blend_type = "MULTIPLY"; l.new(nz.outputs["Fac"], dirt.inputs[0]); l.new(mx.outputs[2], dirt.inputs[6]); dirt.inputs[7].default_value = (0.75, 0.7, 0.65, 1)
    dirt.inputs[0].default_value = 0.3
    l.new(dirt.outputs[2], n["Principled BSDF"].inputs["Base Color"]); bump(n, l, br.outputs["Fac"], 0.4, 0.004)
    return m
def wallpaper(name, a, b2):
    m = principled(name, hexc(a), 0.8); t, n, l = nodes(m)
    tc = n.new("ShaderNodeTexCoord"); wv = n.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 9; wv.bands_direction = "X"
    vo = n.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 30
    l.new(tc.outputs["Object"], wv.inputs["Vector"]); l.new(tc.outputs["Object"], vo.inputs["Vector"])
    mx = n.new("ShaderNodeMath"); mx.operation = "MULTIPLY"; l.new(wv.outputs["Fac"], mx.inputs[0]); l.new(vo.outputs["Distance"], mx.inputs[1])
    r = ramp(n, l, wv.outputs["Fac"], [(0.35, hexc(a)), (0.65, hexc(b2))])
    l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
    return m
def marble(name):
    m = principled(name, (0.9, 0.88, 0.84), 0.15); t, n, l = nodes(m)
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 12; nz.inputs["Distortion"].default_value = 4
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    r = ramp(n, l, nz.outputs["Fac"], [(0.45, (0.92, 0.9, 0.87)), (0.5, (0.45, 0.43, 0.42)), (0.55, (0.9, 0.88, 0.85))])
    l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
    return m
def bread(name, a="#c8873a"):
    m = principled(name, hexc(a), 0.7); t, n, l = nodes(m)
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14; l.new(tc.outputs["Object"], nz.inputs["Vector"])
    r = ramp(n, l, nz.outputs["Fac"], [(0.3, hexc("#8a4a1e")), (0.55, hexc(a)), (0.8, hexc("#e8b86a"))])
    l.new(r.outputs["Color"], n["Principled BSDF"].inputs["Base Color"]); bump(n, l, nz.outputs["Fac"], 0.5, 0.01)
    return m
def cloth(name, a):
    m = principled(name, hexc(a), 0.9); t, n, l = nodes(m)
    tc = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; l.new(tc.outputs["Object"], nz.inputs["Vector"]); bump(n, l, nz.outputs["Fac"], 0.25)
    return m
def emit(name, col, s):
    m = bpy.data.materials.new(name); t, n, l = nodes(m); b = n["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Emission Color"].default_value = (*col, 1); b.inputs["Emission Strength"].default_value = s
    return m
def glass(name):
    m = bpy.data.materials.new(name); t, n, l = nodes(m); b = n["Principled BSDF"]
    b.inputs["Transmission Weight"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.02; b.inputs["IOR"].default_value = 1.45
    return m


# ---------------- geometry helpers ----------------
def box(name, loc, size, mat, bevel=0.01, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); bpy.ops.object.transform_apply(scale=True)
    if bevel: md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2; md.limit_method = "ANGLE"
    o.data.materials.append(mat); return o
def cyl(name, loc, r, h, mat, verts=24, rot=(0, 0, 0), bevel=0.005):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot); o = bpy.context.object; o.name = name
    if bevel: md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2
    o.data.materials.append(mat); bpy.ops.object.shade_smooth(); return o
def blob(name, loc, size, mat, rough=0.08, seed=0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc); o = bpy.context.object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    tex = bpy.data.textures.new(name + "t", "CLOUDS"); tex.noise_scale = 0.3
    d = o.modifiers.new("d", "DISPLACE"); d.texture = tex; d.strength = rough
    o.data.materials.append(mat); bpy.ops.object.shade_smooth(); return o
def text(body, loc, size, mat, rot=(math.radians(90), 0, 0), align="CENTER", extrude=0.004):
    bpy.ops.object.text_add(location=loc, rotation=rot); o = bpy.context.object; o.data.body = body
    o.data.size = size; o.data.align_x = align; o.data.extrude = extrude
    fonts = [f for f in ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf") if __import__("os").path.exists(f)]
    if fonts: o.data.font = bpy.data.fonts.load(fonts[0])
    o.data.materials.append(mat); return o



def materials():
    return dict(
        floor=tiles("floor", "#e8dcc2", "#8a2e2a"), wainscot=wood("wainscot", "#6a3a1e", "#3a1e10", 5), wall=wallpaper("wall", "#d8b878", "#c89a5a"),
        trim=wood("trim", "#5a3018", "#2a140a", 9, 0.35), counter=wood("counter", "#7a4422", "#3e1e0e", 4), marble=marble("marble"),
        shelf=wood("shelf", "#6a3a1e", "#341a0c", 7), bread=bread("bread"), bread2=bread("bread2", "#a8682a"), roll=bread("roll", "#d89a4a"),
        brass=principled("brass", hexc("#c8963a"), 0.25, 1.0), iron=principled("iron", hexc("#2a2a2e"), 0.4, 0.8), wicker=wood("wicker", "#b88a4a", "#6a4a20", 30, 0.8),
        ceiling=principled("ceiling", hexc("#e8dcc4"), 0.9), beam=wood("beam", "#5a3418", "#2a160a", 3), sack=cloth("sack", "#d8c8a0"), paper=principled("paper", hexc("#f4ecd8"), 0.8),
        cash=principled("cash", hexc("#9fbf8a"), 0.8), band=principled("band", hexc("#e8dcb8"), 0.8), bulb=emit("bulb", (1.0, 0.75, 0.45), 30), dark=principled("dark", hexc("#1c1612"), 0.6),
        glass=glass("glass"), sign=principled("sign", hexc("#1e3a2a"), 0.5), gold=principled("gold", hexc("#e8c060"), 0.3, 1.0), red=principled("red", hexc("#b8202c"), 0.5),
        chalk=principled("chalk", hexc("#262a28"), 0.9), white=principled("white", hexc("#f2ece0"), 0.6), jar=glass("jar"), shade=principled("shade", hexc("#2f4a3a"), 0.4, 0.6),
    )
