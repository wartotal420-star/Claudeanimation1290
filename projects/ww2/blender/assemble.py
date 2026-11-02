# Assemble the rendered shots into the final video inside Blender's sequencer: every shot's frames as an image strip
# (shots overlap by their crossfade and the later one fades in), title / chapter cards faded over the picture, the
# sound mix, H.264 + AAC out.  blender -b --factory-startup -P assemble.py -- <exportDir> <framesDir> <mix.wav> <out.mp4> [ext=png]
import bpy, sys, os, json
ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
EXP, FR, MIX, OUT = ARGV[:4]
EXT = ARGV[4] if len(ARGV) > 4 else "png"
TL = json.load(open(os.path.join(EXP, "timeline.json")))
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = 1920, 1080, 100
S.render.fps = TL["fps"]; S.frame_start = 1; S.frame_end = TL["total"]
S.sequence_editor_create(); SE = S.sequence_editor
try: strips = SE.strips
except AttributeError: strips = SE.sequences
def new_img(**kw):
    try: return strips.new_image(fit_method="FIT", **kw)
    except TypeError: return strips.new_image(**kw)
def img_strip(name, folder, files, start, channel):
    st = new_img(name=name, filepath=os.path.join(folder, files[0]), channel=channel, frame_start=start)
    for f in files[1:]: st.elements.append(f)
    return st
# preview frames may be rendered at 50%: output at the frames' own size (every strip is fitted to it)
for s in TL["shots"]:
    d = os.path.join(FR, f"shot{s['id']:02d}")
    fs_ = sorted(f for f in os.listdir(d) if f.endswith("." + EXT)) if os.path.isdir(d) else []
    if fs_:
        im = bpy.data.images.load(os.path.join(d, fs_[0])); S.render.resolution_percentage = max(10, round(100 * im.size[0] / 1920)); break
for k, s in enumerate(TL["shots"]):
    folder = os.path.join(FR, f"shot{s['id']:02d}")
    if not os.path.isdir(folder): print("missing frames for shot", s["id"]); continue
    files = sorted(f for f in os.listdir(folder) if f.endswith("." + EXT))
    if not files: print("missing frames for shot", s["id"]); continue
    f0 = int(files[0].split(".")[0])
    st = img_strip(f"shot{s['id']}", folder, files, f0 + 1, 2 + (k % 2))
    x = TL["xfade"].get(str(s["id"]))
    if x:  # fade the later shot in over the overlap
        st.blend_type = "ALPHA_OVER"; a = s["a"] - x // 2 + 1
        st.blend_alpha = 0.0; st.keyframe_insert("blend_alpha", frame=a)
        st.blend_alpha = 1.0; st.keyframe_insert("blend_alpha", frame=a + x)
for i, c in enumerate(TL["cards"]):
    st = new_img(name=f"card{i}", filepath=os.path.join(EXP, c["file"]), channel=6, frame_start=c["a"] + 1)
    st.frame_final_duration = c["b"] - c["a"]; st.blend_type = "ALPHA_OVER"
    for fr, v in ((c["a"] + 1, 0.0), (c["a"] + 11, 1.0), (c["b"] - 7, 1.0), (c["b"] + 1, 0.0)):
        st.blend_alpha = v; st.keyframe_insert("blend_alpha", frame=fr)
strips.new_sound(name="mix", filepath=MIX, channel=1, frame_start=1)
try: S.render.image_settings.media_type = "VIDEO"      # Blender 5.x; 4.5 has no media_type
except Exception: pass
S.render.image_settings.file_format = "FFMPEG"
S.render.ffmpeg.format = "MPEG4"; S.render.ffmpeg.codec = "H264"; S.render.ffmpeg.constant_rate_factor = "HIGH"; S.render.ffmpeg.ffmpeg_preset = "GOOD"
S.render.ffmpeg.audio_codec = "AAC"; S.render.ffmpeg.audio_bitrate = 320; S.render.ffmpeg.audio_channels = "STEREO"; S.render.ffmpeg.audio_mixrate = 48000
S.render.filepath = OUT
bpy.ops.render.render(animation=True)
print("assembled", OUT)
