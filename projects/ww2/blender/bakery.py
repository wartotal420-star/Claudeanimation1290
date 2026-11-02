# WW2 part 1 Blender test: the 1923 bakery. Run: python3 bakery.py <cards_dir> <out.png> [samples] [scale%]
# Detailed procedural set (bevelled geometry, procedural wood / tiles / wallpaper / marble / bread), real lights
# (warm pendant lamps + cool window daylight), Cycles + denoise, AgX Punchy. Characters are 2D PNG cards lit by the scene.
import bpy, math, random, sys
from mathutils import Vector

ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
CARDS, OUT = ARGV[0], ARGV[1]
SAMPLES = int(ARGV[2]) if len(ARGV) > 2 else 64
PCT = int(ARGV[3]) if len(ARGV) > 3 else 50
ENGINE = ARGV[4] if len(ARGV) > 4 else "CYCLES"
random.seed(1923)
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.engine = "BLENDER_EEVEE" if ENGINE == "EEVEE" else "CYCLES"; S.cycles.device = "GPU" if sys.platform == "darwin" else "CPU";
if sys.platform == "darwin":
    try:
        pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "METAL"; pr.get_devices(); [setattr(d, "use", True) for d in pr.devices]
    except Exception as e: print("metal", e)
 S.cycles.samples = SAMPLES; S.cycles.use_denoising = True
S.cycles.max_bounces = 6; S.cycles.light_sampling_threshold = 0.01
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = 1920, 1080, PCT
S.view_settings.view_transform = "AgX"
try: S.view_settings.look = "AgX - Punchy"
except Exception: pass
S.view_settings.exposure = 1.1
W = bpy.data.worlds.new("w"); S.world = W; W.use_nodes = True
W.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.035, 0.03, 1); W.node_tree.nodes["Background"].inputs[1].default_value = 0.6

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

M = dict(
    floor=tiles("floor", "#e8dcc2", "#8a2e2a"), wainscot=wood("wainscot", "#6a3a1e", "#3a1e10", 5), wall=wallpaper("wall", "#d8b878", "#c89a5a"),
    trim=wood("trim", "#5a3018", "#2a140a", 9, 0.35), counter=wood("counter", "#7a4422", "#3e1e0e", 4), marble=marble("marble"),
    shelf=wood("shelf", "#6a3a1e", "#341a0c", 7), bread=bread("bread"), bread2=bread("bread2", "#a8682a"), roll=bread("roll", "#d89a4a"),
    brass=principled("brass", hexc("#c8963a"), 0.25, 1.0), iron=principled("iron", hexc("#2a2a2e"), 0.4, 0.8), wicker=wood("wicker", "#b88a4a", "#6a4a20", 30, 0.8),
    ceiling=principled("ceiling", hexc("#e8dcc4"), 0.9), beam=wood("beam", "#5a3418", "#2a160a", 3), sack=cloth("sack", "#d8c8a0"), paper=principled("paper", hexc("#f4ecd8"), 0.8),
    cash=principled("cash", hexc("#9fbf8a"), 0.8), band=principled("band", hexc("#e8dcb8"), 0.8), bulb=emit("bulb", (1.0, 0.75, 0.45), 30), dark=principled("dark", hexc("#1c1612"), 0.6),
    glass=glass("glass"), sign=principled("sign", hexc("#1e3a2a"), 0.5), gold=principled("gold", hexc("#e8c060"), 0.3, 1.0), red=principled("red", hexc("#b8202c"), 0.5),
    chalk=principled("chalk", hexc("#262a28"), 0.9), white=principled("white", hexc("#f2ece0"), 0.6), jar=glass("jar"), shade=principled("shade", hexc("#2f4a3a"), 0.4, 0.6),
)

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

# ---------------- the room (camera looks +Y, Z up) ----------------
RW, RD, RH = 9.0, 7.0, 3.8
box("floor", (0, 1.5, -0.05), (RW, RD + 4, 0.1), M["floor"], 0)
box("ceiling", (0, 1.5, RH + 0.05), (RW, RD + 4, 0.1), M["ceiling"], 0)
for k in range(5): box(f"beam{k}", (-3.6 + k * 1.8, 1.5, RH - 0.12), (0.22, RD + 4, 0.24), M["beam"], 0.02)
# back wall: wainscot + chair rail + wallpaper + crown
BY = 4.0
box("backwall", (0, BY + 0.1, RH / 2), (RW, 0.2, RH), M["wall"], 0)
box("wainscot", (0, BY - 0.02, 0.55), (RW, 0.08, 1.1), M["wainscot"], 0.01)
for k in range(12): box(f"panel{k}", (-4.0 + k * 0.72, BY - 0.07, 0.55), (0.56, 0.03, 0.8), M["trim"], 0.008)
box("rail", (0, BY - 0.08, 1.12), (RW, 0.1, 0.06), M["trim"], 0.01)
box("crown", (0, BY - 0.08, RH - 0.1), (RW, 0.16, 0.18), M["trim"], 0.02)
# side walls
for s in (-1, 1):
    box(f"side{s}", (s * RW / 2, 1.5, RH / 2), (0.2, RD + 4, RH), M["wall"], 0)
    box(f"sidew{s}", (s * (RW / 2 - 0.06), 1.5, 0.55), (0.08, RD + 4, 1.1), M["wainscot"], 0.01)
# left wall: big shop window with mullions + daylight behind it
WX = -RW / 2 + 0.02
for (y0, y1) in ((-1.4, 1.6),):
    box("winhole", (WX, (y0 + y1) / 2, 2.05), (0.24, y1 - y0, 2.1), M["glass"], 0)
    for k in range(5): box(f"mull{k}", (WX + 0.05, y0 + k * (y1 - y0) / 4, 2.05), (0.1, 0.06, 2.2), M["trim"], 0.005)
    for z in (1.0, 2.05, 3.1): box(f"tran{z}", (WX + 0.05, (y0 + y1) / 2, z), (0.1, y1 - y0, 0.06), M["trim"], 0.005)
bpy.ops.object.light_add(type="AREA", location=(WX - 1.5, 0.1, 2.3), rotation=(0, math.radians(-75), 0)); L = bpy.context.object.data
L.shape = "RECTANGLE"; L.size, L.size_y = 2.4, 3.4; L.energy = 900; L.color = (0.75, 0.85, 1.0)
bpy.ops.object.light_add(type="SUN", location=(-6, -2, 6), rotation=(math.radians(55), math.radians(-35), math.radians(-60))); sun = bpy.context.object.data
sun.energy = 3.5; sun.color = (1.0, 0.9, 0.75); sun.angle = math.radians(2)

# shelves on the back wall with bread, baskets, jars
for row in range(3):
    z = 1.45 + row * 0.62
    box(f"shelf{row}", (0, BY - 0.25, z), (7.2, 0.42, 0.05), M["shelf"], 0.008)
    for k in range(9): box(f"brk{row}{k}", (-3.4 + k * 0.85, BY - 0.12, z - 0.08), (0.04, 0.2, 0.14), M["trim"], 0.004)
    x = -3.4
    while x < 3.4:
        kind = random.random()
        if kind < 0.55: blob(f"loaf{row}{x:.2f}", (x, BY - 0.25, z + 0.12), (0.17, 0.1, 0.09), M["bread"] if random.random() < 0.6 else M["bread2"], 0.02); x += 0.36
        elif kind < 0.8:
            cyl(f"bask{row}{x:.2f}", (x + 0.1, BY - 0.25, z + 0.08), 0.16, 0.14, M["wicker"])
            for j in range(4): blob(f"roll{row}{x:.2f}{j}", (x + 0.02 + (j % 2) * 0.13, BY - 0.27 + (j // 2) * 0.08, z + 0.17), (0.06, 0.05, 0.05), M["roll"], 0.01)
            x += 0.4
        else: cyl(f"jar{row}{x:.2f}", (x + 0.05, BY - 0.25, z + 0.13), 0.07, 0.24, M["jar"]); x += 0.25
# shop sign over the shelves + chalk price board + clock
box("signboard", (0, BY - 0.12, 3.35), (3.6, 0.06, 0.48), M["sign"], 0.01)
for s in (-1, 1): box(f"signedge{s}", (s * 1.8, BY - 0.14, 3.35), (0.06, 0.08, 0.52), M["gold"], 0.005)
text("BÄCKEREI  KLEIN", (0, BY - 0.16, 3.28), 0.24, M["gold"])
box("chalk", (3.75, BY - 0.12, 2.3), (0.9, 0.04, 1.2), M["chalk"], 0.01); box("chalkframe", (3.75, BY - 0.1, 2.3), (1.0, 0.03, 1.3), M["trim"], 0.01)
for i, line in enumerate(["BROT", "SEMMEL", "KUCHEN", "BREZEL"]):
    text(line, (3.42, BY - 0.15, 2.65 - i * 0.24), 0.11, M["white"], align="LEFT", extrude=0.0)
    text("???", (4.06, BY - 0.15, 2.65 - i * 0.24), 0.11, M["white"], align="RIGHT", extrude=0.0)
cyl("clock", (-3.75, BY - 0.12, 2.85), 0.26, 0.06, M["white"], rot=(math.radians(90), 0, 0)); cyl("clockrim", (-3.75, BY - 0.1, 2.85), 0.29, 0.05, M["brass"], rot=(math.radians(90), 0, 0))
for a, ln in ((0.6, 0.18), (2.1, 0.13)): box(f"hand{a}", (-3.75 + math.sin(a) * ln / 2, BY - 0.16, 2.85 + math.cos(a) * ln / 2), (0.018, 0.01, ln), M["dark"], 0, rot=(0, -a, 0))

# the counter: panelled wooden front, marble top, glass display case, register, scale, paper bags
CY = 1.6
box("counter", (0, CY, 0.5), (5.2, 0.8, 1.0), M["counter"], 0.015)
for k in range(6): box(f"cpanel{k}", (-2.1 + k * 0.84, CY - 0.42, 0.5), (0.66, 0.04, 0.7), M["trim"], 0.01)
box("plinth", (0, CY - 0.38, 0.06), (5.3, 0.1, 0.12), M["trim"], 0.01)
box("ctop", (0, CY, 1.03), (5.4, 0.95, 0.06), M["marble"], 0.01)
box("case", (-1.2, CY + 0.05, 1.32), (1.8, 0.6, 0.52), M["glass"], 0.005)
for x in (-2.1, -0.3):
    box(f"caseframe{x}", (x, CY + 0.05, 1.32), (0.04, 0.62, 0.54), M["brass"], 0.004)
for k in range(5): blob(f"cake{k}", (-1.85 + k * 0.32, CY + 0.05, 1.15), (0.12, 0.12, 0.06), M["roll"], 0.01)
# register
box("reg", (1.5, CY + 0.05, 1.28), (0.55, 0.45, 0.45), M["brass"], 0.02)
box("regtop", (1.5, CY + 0.12, 1.58), (0.5, 0.2, 0.18), M["brass"], 0.02)
for i in range(4):
    for j in range(5): cyl(f"key{i}{j}", (1.32 + j * 0.09, CY - 0.12 + i * 0.07, 1.52 - i * 0.02), 0.025, 0.03, M["white"], 12)
# scale + paper bags + bread on the counter
cyl("scalebase", (2.3, CY, 1.1), 0.15, 0.08, M["iron"]); cyl("scalepan", (2.3, CY, 1.3), 0.2, 0.02, M["brass"]); cyl("scalepost", (2.3, CY, 1.2), 0.02, 0.2, M["iron"])
for k in range(4): box(f"bag{k}", (-2.4 + k * 0.05, CY + 0.15, 1.2), (0.22, 0.14, 0.3), M["paper"], 0.01, rot=(0, 0, 0.1 * k))
for k in range(3): blob(f"cloaf{k}", (0.15 + k * 0.35, CY - 0.15, 1.12), (0.16, 0.09, 0.08), M["bread"], 0.02)
# the price tag on its stand
box("tagpost", (0.45, CY + 0.2, 1.35), (0.04, 0.04, 0.6), M["iron"], 0)
box("tag", (0.45, CY + 0.18, 1.72), (1.45, 0.03, 0.42), M["paper"], 0.01)
text("1 BROT", (0.45, CY + 0.15, 1.83), 0.08, M["dark"])
text("200.000.000.000 M", (0.45, CY + 0.15, 1.62), 0.14, M["red"])

# pendant lamps with real light
for x in (-2.0, 0.6, 2.8):
    cyl(f"cord{x}", (x, CY + 0.4, 3.2), 0.008, 1.2, M["dark"], 8)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.32, radius2=0.08, depth=0.24, location=(x, CY + 0.4, 2.55)); o = bpy.context.object; o.data.materials.append(M["shade"])
    s = o.modifiers.new("s", "SOLIDIFY"); s.thickness = 0.01; bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(x, CY + 0.4, 2.42)); bpy.context.object.data.materials.append(M["bulb"])
    bpy.ops.object.light_add(type="POINT", location=(x, CY + 0.4, 2.38)); pl = bpy.context.object.data; pl.energy = 140; pl.color = (1.0, 0.72, 0.42); pl.shadow_soft_size = 0.08

# floor clutter: flour sacks, crates, a broom, bread baskets, the wheelbarrow of cash (foreground left)
for k, (x, y) in enumerate(((3.6, 2.6), (3.2, 2.9), (3.9, 3.2), (-3.9, 2.8))):
    blob(f"sack{k}", (x, y, 0.35), (0.32, 0.26, 0.38), M["sack"], 0.05)
for k, (x, y) in enumerate(((2.9, 0.4), (3.5, 0.3), (3.2, 0.5))): box(f"crate{k}", (x, y, 0.25 + (0.5 if k == 2 else 0)), (0.5, 0.5, 0.5), M["wicker"], 0.01, rot=(0, 0, 0.2 * k))
cyl("broom", (-3.95, 3.4, 0.9), 0.02, 1.8, M["trim"], rot=(0.15, 0, 0))
WB = Vector((-1.9, -0.9, 0))
box("wbtray", WB + Vector((0, 0, 0.6)), (1.0, 0.7, 0.35), M["iron"], 0.03)
cyl("wbwheel", WB + Vector((0.6, 0, 0.25)), 0.25, 0.08, M["dark"], rot=(math.radians(90), 0, 0))
for s in (-1, 1): box(f"wbh{s}", WB + Vector((-0.8, s * 0.28, 0.65)), (0.9, 0.05, 0.05), M["trim"], 0.01)
for k in range(16):
    p = WB + Vector((-0.35 + (k % 4) * 0.23, -0.22 + (k // 4 % 2) * 0.22, 0.82 + (k // 8) * 0.1))
    box(f"cash{k}", p, (0.22, 0.11, 0.09), M["cash"], 0.004, rot=(0, 0, random.uniform(-0.3, 0.3)))
    box(f"band{k}", p + Vector((0, 0, 0)), (0.05, 0.115, 0.095), M["band"], 0, rot=(0, 0, 0))

# ---------------- characters (2D cards lit by the scene) ----------------
def card(name, png, loc, h, cam):
    img = bpy.data.images.load(png); m = bpy.data.materials.new("m_" + name); t, n, l = nodes(m)
    b = n["Principled BSDF"]; it = n.new("ShaderNodeTexImage"); it.image = img
    l.new(it.outputs["Color"], b.inputs["Base Color"]); l.new(it.outputs["Alpha"], b.inputs["Alpha"])
    l.new(it.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 0.25; b.inputs["Roughness"].default_value = 0.9
    w = h * 0.6
    me = bpy.data.meshes.new(name); me.from_pydata([(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(); [setattr(uv.data[i], "uv", c) for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)])]
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    d = Vector(cam) - Vector(loc); o.location = loc; o.rotation_euler = (0, 0, math.atan2(-d.x, d.y))
    o.data.materials.append(m); return o
CAM = (0.9, -4.6, 1.55)
H = 2.16
card("baker", f"{CARDS}/baker.png", (0.9, CY + 0.75, 0.0), H * 1.0, CAM)
card("worker", f"{CARDS}/worker.png", (-0.6, 0.4, 0.0), H, CAM)
card("lady", f"{CARDS}/lady.png", (2.2, -0.2, 0.0), H * 0.95, CAM)
card("gent", f"{CARDS}/gent.png", (-3.2, 0.9, 0.0), H, CAM)

# soft warm fill from behind the camera (keeps the foreground readable)
bpy.ops.object.light_add(type="AREA", location=(0.9, -6.0, 2.6), rotation=(math.radians(75), 0, 0)); F = bpy.context.object.data
F.size = 5; F.energy = 260; F.color = (1.0, 0.85, 0.7)
# ---------------- camera ----------------
bpy.ops.object.camera_add(location=CAM); cam = bpy.context.object; S.camera = cam
tgt = Vector((0.2, 2.0, 1.35)); d = tgt - cam.location; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 30; cam.data.dof.use_dof = True; cam.data.dof.focus_distance = (Vector((-0.6, 0.4, 1.6)) - cam.location).length; cam.data.dof.aperture_fstop = 4.0
S.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("rendered", OUT)
