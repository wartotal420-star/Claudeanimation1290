# Render one exported WW2 shot in Blender (Cycles). The set is built once, then per frame the camera, lens and every
# character / effect card are posed from the export manifest and the frame is written to <out>/<frame>.png.
#   blender -b --factory-startup -P render_shot.py -- <shotNN.json> <cardsDir> <outDir> [samples=24] [pct=100] [step=1] [maxFrames=0]
# (cloud preview: python3 render_shot.py -- ...)
import bpy, sys, os, json, math, importlib
from mathutils import Vector, Quaternion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import T

ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
MAN, CARDS, OUT = ARGV[0], ARGV[1], ARGV[2]
SAMPLES = int(ARGV[3]) if len(ARGV) > 3 else 24
PCT = int(ARGV[4]) if len(ARGV) > 4 else 100
STEP = int(ARGV[5]) if len(ARGV) > 5 else 1
MAXF = int(ARGV[6]) if len(ARGV) > 6 else 0
D = json.load(open(MAN))
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.engine = "CYCLES"
S.cycles.device = "GPU" if sys.platform == "darwin" else "CPU"
if sys.platform == "darwin":
    try:
        pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "METAL"; pr.get_devices()
        for dv in pr.devices: dv.use = True
    except Exception as e: print("metal", e)
S.cycles.samples = SAMPLES; S.cycles.use_denoising = True; S.cycles.max_bounces = 5; S.cycles.light_sampling_threshold = 0.02
S.cycles.use_adaptive_sampling = True; S.cycles.adaptive_threshold = 0.03
S.render.use_persistent_data = True
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = 1920, 1080, PCT
S.render.film_transparent = False
S.view_settings.view_transform = "AgX"
try: S.view_settings.look = "AgX - Punchy"
except Exception: pass
S.view_settings.exposure = 1.0
W = bpy.data.worlds.new("w"); S.world = W; W.use_nodes = True
bg = W.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.05, 0.035, 0.03, 1); bg.inputs[1].default_value = 0.5

M = lib.materials()
setmod = importlib.import_module("sets." + D["set"])
ENV = setmod.build(M, D)            # builds geometry + lights; may return per-frame hooks

# ---------------- camera ----------------
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); S.collection.objects.link(cam); S.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.clip_start = 0.03; cam.data.clip_end = 3000

# ---------------- card pools ----------------
SU = 0.00216
images = {}
def image(h):
    im = images.get(h)
    if im is None:
        im = bpy.data.images.load(os.path.join(CARDS, h + ".png")); im.alpha_mode = "STRAIGHT"; images[h] = im
    return im
def card_material(name, lit):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    for x in list(n): n.remove(x)
    out = n.new("ShaderNodeOutputMaterial"); tex = n.new("ShaderNodeTexImage"); tex.name = "tex"; tex.interpolation = "Linear"
    mix = n.new("ShaderNodeMixShader"); tr = n.new("ShaderNodeBsdfTransparent")
    op = n.new("ShaderNodeMath"); op.operation = "MULTIPLY"; op.name = "op"; op.inputs[1].default_value = 1.0
    l.new(tex.outputs["Alpha"], op.inputs[0]); l.new(op.outputs[0], mix.inputs[0]); l.new(tr.outputs[0], mix.inputs[1])
    if lit:
        b = n.new("ShaderNodeBsdfPrincipled"); b.inputs["Roughness"].default_value = 0.9
        try: b.inputs["Specular IOR Level"].default_value = 0.1
        except Exception: pass
        l.new(tex.outputs["Color"], b.inputs["Base Color"]); l.new(tex.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 0.28
        l.new(b.outputs[0], mix.inputs[2])
    else:
        em = n.new("ShaderNodeEmission"); em.name = "em"; l.new(tex.outputs["Color"], em.inputs["Color"]); l.new(em.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], out.inputs["Surface"])
    return m
class Quad:
    def __init__(self, i, lit):
        me = bpy.data.meshes.new(f"q{i}"); me.from_pydata([(0, 0, 0)] * 4, [], [(0, 1, 2, 3)])
        uv = me.uv_layers.new()
        for k, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[k].uv = c
        self.o = bpy.data.objects.new(f"q{i}", me); S.collection.objects.link(self.o)
        self.m = card_material(f"cm{i}", lit); me.materials.append(self.m)
        self.o.visible_shadow = lit
    def set(self, corners, h, op=1.0, glow=1.0):
        v = self.o.data.vertices
        for k, c in enumerate(corners): v[k].co = c
        self.o.data.update()
        self.m.node_tree.nodes["tex"].image = image(h); self.m.node_tree.nodes["op"].inputs[1].default_value = op
        em = self.m.node_tree.nodes.get("em")
        if em: em.inputs["Strength"].default_value = glow
        self.o.hide_render = False
chars, fxs = [], []
def pool(lst, i, lit):
    while len(lst) <= i: lst.append(Quad(f"{'c' if lit else 'f'}{len(lst)}", lit))
    return lst[i]

def three_cam(c):
    pos, look = Vector(c["pos"]), Vector(c["look"])
    fwd = (look - pos).normalized(); right = fwd.cross(Vector((0, 1, 0))).normalized(); up = right.cross(fwd)
    r = c["roll"]; right, up = right * math.cos(r) + up * math.sin(r), up * math.cos(r) - right * math.sin(r)
    return pos, fwd, right, up

done = 0
for fr in D["frames"][::STEP]:
    f = fr["f"]; path = os.path.join(OUT, f"{f:05d}.png")
    if os.path.exists(path): continue
    if MAXF and done >= MAXF: break
    c = fr["cam"]; pos, fwd, right, up = three_cam(c)
    cam.location = T(*pos); d = T(*Vector(c["look"])) - cam.location
    q = d.to_track_quat("-Z", "Z"); cam.rotation_mode = "QUATERNION"; cam.rotation_quaternion = q @ Quaternion((0, 0, 1), c["roll"])
    cam.data.angle = math.radians(c["fov"])
    dof = fr["dof"]
    cam.data.dof.use_dof = dof["c"] > 0.5
    if cam.data.dof.use_dof:
        fp = Vector(dof["focus"]) if dof["focus"] else Vector(c["look"])
        cam.data.dof.focus_distance = max(0.2, (fp - pos).dot(fwd)); cam.data.dof.aperture_fstop = max(1.1, min(22, 26.0 / dof["c"]))
    # characters: yaw-only billboards (feet at the anchor), drawn 600 x 1000 design units = 1.296 x 2.16 m
    for i, p in enumerate(fr["places"]):
        s = p["s"]; P = Vector(p["p"])
        yaw = p["yaw"] if p["yaw"] is not None else math.atan2(pos.x - P.x, pos.z - P.z)
        rx = Vector((math.cos(yaw), 0, -math.sin(yaw))) * (-1 if p["m"] else 1)
        w2, zb, zt = 0.648 * s, -0.054 * s, 2.106 * s
        cr, sr = math.cos(p["roll"]), math.sin(p["roll"])
        def at(u, v):
            x, y = u * cr - v * sr, u * sr + v * cr
            return T(*(P + rx * x + Vector((0, y, 0))))
        pool(chars, i, True).set([at(-w2, zb), at(w2, zb), at(w2, zt), at(-w2, zt)], p["h"])
    for k in range(len(fr["places"]), len(chars)): chars[k].o.hide_render = True
    for i, e in enumerate(fr["fx"]):
        P = Vector(e["p"]); w, h, rot = e["w"] / 2, e["hh"] / 2, e["rot"]
        if e["flat"]:
            ax, ay = Vector((math.cos(rot), 0, -math.sin(rot))), Vector((math.sin(rot), 0, math.cos(rot)))
            ay = -ay
        else:
            ax = right * math.cos(rot) + up * math.sin(rot); ay = up * math.cos(rot) - right * math.sin(rot)
        cs = [T(*(P + ax * sx * w + ay * sy * h)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        pool(fxs, i, False).set(cs, e["h"], e["op"] if e["soft"] else 1.0, e["glow"] * (0.9 if e["glow"] <= 1 else 3.0))
    for k in range(len(fr["fx"]), len(fxs)): fxs[k].o.hide_render = True
    if ENV and ENV.get("update"): ENV["update"](f)
    S.render.filepath = path
    bpy.ops.render.render(write_still=True)
    done += 1
    print("frame", f, flush=True)
print("shot done", D["id"])
