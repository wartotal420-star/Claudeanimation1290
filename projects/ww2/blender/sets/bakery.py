# The 1923 bakery (shots 14-15), built in three.js layout coordinates (see story.ts / cast.ts):
# counter x -3..3, z 1.6..2.3; shelves on the back wall z ~3.8; baker at (0.9, 0, 3.0); price tag (-1.25, 1.62, 1.7);
# wheelbarrow of cash at (-1.2, 0, -0.4); the shop window in the left wall (x = +6 in three = camera left).
import bpy, math, random
from mathutils import Vector
import lib
from lib import T, TS

def bx(name, c, s, m, bev=0.01, yaw=0.0): return lib.box(name, T(*c), TS(*s), m, bev, rot=(0, 0, yaw))
def cy(name, c, r, h, m, verts=24, rot=(0, 0, 0)): return lib.cyl(name, T(*c), r, h, m, verts, rot)
def bl(name, c, s, m, rough=0.03): return lib.blob(name, T(*c), TS(*s), m, rough)
def tx(body, c, size, m, align="CENTER", extrude=0.004): return lib.text(body, T(*c), size, m, align=align, extrude=extrude)

TAG = None
def tag_text(f): return "200.000.000.000 M" if f < 1858 else "350.000.000.000 M" if f < 1890 else "500.000.000.000 M"

def build(M, D):
    global TAG
    random.seed(1923)
    RH = 3.9
    bx("floor", (0, -0.05, -1), (13, 0.1, 11), M["floor"], 0)
    bx("ceiling", (0, RH + 0.05, -1), (13, 0.1, 11), M["ceiling"], 0)
    for k in range(6): bx(f"beam{k}", (-5 + k * 2, RH - 0.12, -1), (0.24, 0.26, 11), M["beam"], 0.02)
    # back wall (z 4.1): wallpaper, wainscot panels, rail, crown
    bx("back", (0, RH / 2, 4.2), (13, RH, 0.2), M["wall"], 0)
    bx("wains", (0, 0.55, 4.06), (13, 1.1, 0.08), M["wainscot"], 0.01)
    for k in range(16): bx(f"pan{k}", (-5.6 + k * 0.75, 0.55, 4.01), (0.58, 0.8, 0.03), M["trim"], 0.008)
    bx("rail", (0, 1.12, 4.0), (13, 0.06, 0.1), M["trim"], 0.01); bx("crown", (0, RH - 0.1, 4.0), (13, 0.18, 0.16), M["trim"], 0.02)
    # side walls; the right one (three x = -6.1) plain with a door, the left one (x = +6.1) a big shop window
    for sx in (-1, 1):
        bx(f"side{sx}", (sx * 6.2, RH / 2, -1), (0.2, RH, 11), M["wall"], 0)
        bx(f"sidew{sx}", (sx * 6.06, 0.55, -1), (0.08, 1.1, 11), M["wainscot"], 0.01)
    bx("front", (0, RH / 2, -6.3), (13, RH, 0.2), M["wall"], 0)
    for k in range(5): bx(f"mull{k}", (6.0, 2.05, -3.0 + k * 1.0), (0.1, 2.2, 0.06), M["trim"], 0.005)
    for y in (1.0, 2.05, 3.1): bx(f"tran{y}", (6.0, y, -1.0), (0.1, 0.06, 4.0), M["trim"], 0.005)
    bx("winglass", (6.12, 2.05, -1.0), (0.02, 2.1, 4.0), M["glass"], 0)
    bx("door", (-6.02, 1.1, -2.0), (0.06, 2.2, 1.1), M["trim"], 0.01); cy("knob", (-5.98, 1.05, -1.6), 0.04, 0.06, M["brass"], 12, (0, math.radians(90), 0))
    # daylight through the window + a warm sun shaft
    bpy.ops.object.light_add(type="AREA", location=T(8.0, 2.3, -1.0)); a = bpy.context.object; a.data.shape = "RECTANGLE"; a.data.size, a.data.size_y = 4.2, 2.4
    a.rotation_euler = (0, math.radians(-90), 0); a.data.energy = 1100; a.data.color = (0.78, 0.87, 1.0)
    bpy.ops.object.light_add(type="SUN"); s = bpy.context.object; s.data.energy = 3.0; s.data.color = (1.0, 0.88, 0.7); s.data.angle = math.radians(2)
    s.rotation_euler = (math.radians(60), 0, math.radians(110))
    # shelves with loaves, baskets of rolls, jars (three rows)
    for row in range(3):
        y = 1.2 + row * 0.66
        bx(f"shelf{row}", (0, y, 3.82), (9.0, 0.05, 0.44), M["shelf"], 0.008)
        for k in range(11): bx(f"brk{row}{k}", (-4.4 + k * 0.88, y - 0.08, 3.95), (0.04, 0.14, 0.2), M["trim"], 0.004)
        x = -4.3
        while x < 4.3:
            kind = random.random()
            if kind < 0.55: bl(f"loaf{row}{x:.2f}", (x, y + 0.12, 3.82), (0.17, 0.09, 0.1), M["bread"] if random.random() < 0.6 else M["bread2"], 0.02); x += 0.36
            elif kind < 0.8:
                cy(f"bask{row}{x:.2f}", (x + 0.1, y + 0.01, 3.82), 0.16, 0.14, M["wicker"])
                for j in range(4): bl(f"roll{row}{x:.2f}{j}", (x + 0.02 + (j % 2) * 0.13, y + 0.17, 3.78 + (j // 2) * 0.08), (0.06, 0.05, 0.05), M["roll"], 0.01)
                x += 0.4
            else: cy(f"jar{row}{x:.2f}", (x + 0.05, y + 0.02, 3.82), 0.07, 0.24, M["jar"]); x += 0.25
    # shop sign + chalk price board + clock
    bx("signboard", (0, 3.4, 4.0), (3.8, 0.5, 0.06), M["sign"], 0.01)
    for sx in (-1, 1): bx(f"signedge{sx}", (sx * 1.9, 3.4, 3.98), (0.06, 0.54, 0.08), M["gold"], 0.005)
    tx("BÄCKEREI  KLEIN", (0, 3.33, 3.96), 0.25, M["gold"])
    bx("chalk", (-4.6, 2.4, 4.0), (1.0, 1.25, 0.04), M["chalk"], 0.01); bx("chalkfr", (-4.6, 2.4, 4.02), (1.1, 1.35, 0.03), M["trim"], 0.01)
    for i, line in enumerate(["BROT", "SEMMEL", "KUCHEN", "BREZEL"]):
        tx(line, (-4.25, 2.75 - i * 0.24, 3.97), 0.11, M["white"], "LEFT", 0.0)
    cy("clock", (4.6, 2.9, 3.98), 0.27, 0.06, M["white"], 32, (math.radians(90), 0, 0)); cy("clockrim", (4.6, 2.9, 3.99), 0.3, 0.05, M["brass"], 32, (math.radians(90), 0, 0))
    # the counter (panelled front, marble top), display case, register, scale, bags, loaves, baskets
    bx("counter", (0, 0.5, 1.95), (6.0, 1.0, 0.7), M["counter"], 0.015)
    for k in range(7): bx(f"cpan{k}", (-2.55 + k * 0.85, 0.5, 1.58), (0.68, 0.72, 0.04), M["trim"], 0.01)
    bx("plinth", (0, 0.06, 1.62), (6.1, 0.12, 0.1), M["trim"], 0.01)
    bx("ctop", (0, 1.03, 1.95), (6.2, 0.06, 0.85), M["marble"], 0.01)
    bx("case", (1.2, 1.32, 2.0), (1.8, 0.52, 0.55), M["glass"], 0.005)
    for x in (0.3, 2.1): bx(f"cframe{x}", (x, 1.32, 2.0), (0.04, 0.54, 0.57), M["brass"], 0.004)
    for k in range(5): bl(f"cake{k}", (0.45 + k * 0.32, 1.15, 2.0), (0.12, 0.06, 0.12), M["roll"], 0.01)
    bx("reg", (2.3, 1.28, 1.95), (0.55, 0.45, 0.45), M["brass"], 0.02); bx("regtop", (2.3, 1.58, 2.02), (0.5, 0.18, 0.2), M["brass"], 0.02)
    for i in range(4):
        for j in range(5): cy(f"key{i}{j}", (2.12 + j * 0.09, 1.5 - i * 0.02, 1.8 + i * 0.06), 0.025, 0.03, M["white"], 12)
    cy("scaleb", (-2.6, 1.06, 1.95), 0.15, 0.08, M["iron"]); cy("scalep", (-2.6, 1.14, 1.95), 0.02, 0.18, M["iron"]); cy("scalepan", (-2.6, 1.32, 1.95), 0.2, 0.02, M["brass"])
    for k in range(4): bx(f"bag{k}", (2.75 - k * 0.05, 1.2, 2.1), (0.22, 0.3, 0.14), M["paper"], 0.01, 0.1 * k)
    for k in range(3): bl(f"cloaf{k}", (-0.4 - k * 0.35, 1.12, 1.75), (0.16, 0.08, 0.09), M["bread"], 0.02)
    for k in range(2):
        cy(f"cbask{k}", (-1.6 - k * 0.6, 1.06, 2.05), 0.2, 0.16, M["wicker"])
        for j in range(5): bl(f"cbr{k}{j}", (-1.62 - k * 0.6 + (j % 3 - 1) * 0.1, 1.27, 2.02 + (j // 3) * 0.08), (0.07, 0.05, 0.06), M["roll"], 0.01)
    # the price tag on its stand (text changes with the inflation)
    bx("tagpost", (-1.25, 1.33, 1.78), (0.04, 0.55, 0.04), M["iron"], 0)
    bx("tag", (-1.25, 1.62, 1.72), (1.5, 0.44, 0.03), M["paper"], 0.01)
    tx("1 BROT", (-1.25, 1.74, 1.69), 0.08, M["dark"])
    TAG = tx(tag_text(0), (-1.25, 1.53, 1.69), 0.14, M["red"])
    # pendant lamps (real light)
    for x in (-1.5, 1.5):
        cy(f"cord{x}", (x, 3.25, 1.9), 0.008, 1.2, M["dark"], 8)
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.32, radius2=0.08, depth=0.24, location=T(x, 2.62, 1.9)); o = bpy.context.object; o.data.materials.append(M["shade"])
        md = o.modifiers.new("s", "SOLIDIFY"); md.thickness = 0.01; bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=T(x, 2.48, 1.9)); bpy.context.object.data.materials.append(M["bulb"])
        bpy.ops.object.light_add(type="POINT", location=T(x, 2.42, 1.9)); pl = bpy.context.object.data; pl.energy = 160; pl.color = (1.0, 0.72, 0.42); pl.shadow_soft_size = 0.1
    # soft warm fill from the front of the shop
    bpy.ops.object.light_add(type="AREA", location=T(0, 2.6, -5.5)); f = bpy.context.object; f.data.size = 5; f.data.energy = 220; f.data.color = (1.0, 0.85, 0.7)
    f.rotation_euler = (math.radians(70), 0, math.radians(180))
    # floor clutter: flour sacks, crates, a broom, a stool, the wheelbarrow of cash
    for k, (x, z) in enumerate(((-4.6, 3.0), (-5.1, 2.6), (-4.8, 2.2), (5.3, 3.3))): bl(f"sack{k}", (x, 0.36, z), (0.32, 0.38, 0.26), M["sack"], 0.05)
    for k, (x, z) in enumerate(((-4.2, -1.0), (-4.8, -1.4), (-4.5, -1.2))): bx(f"crate{k}", (x, 0.25 + (0.5 if k == 2 else 0), z), (0.5, 0.5, 0.5), M["wicker"], 0.01, 0.2 * k)
    cy("broom", (5.7, 0.9, 3.5), 0.02, 1.8, M["trim"], 8, (0.15, 0, 0))
    yaw = 0.5
    def wb(dx, dy, dz): return Vector((-1.2, 0, -0.4)) + Vector((dx * math.cos(yaw) + dz * math.sin(yaw), dy, -dx * math.sin(yaw) + dz * math.cos(yaw)))
    bx("wbtray", wb(0, 0.6, 0), (1.0, 0.35, 0.7), M["iron"], 0.03, yaw)
    cy("wbwheel", wb(0.6, 0.25, 0), 0.25, 0.08, M["dark"], 24, (math.radians(90), 0, -yaw + math.radians(90)))
    for sz in (-1, 1): bx(f"wbh{sz}", wb(-0.8, 0.65, sz * 0.28), (0.9, 0.05, 0.05), M["trim"], 0.01, yaw)
    for k in range(18):
        p = wb(-0.35 + (k % 4) * 0.23, 0.82 + (k // 8) * 0.1, -0.22 + (k // 4 % 2) * 0.22)
        bx(f"cash{k}", p, (0.22, 0.09, 0.11), M["cash"], 0.004, yaw + random.uniform(-0.3, 0.3))
    return {"update": lambda f: setattr(TAG.data, "body", tag_text(f))}
