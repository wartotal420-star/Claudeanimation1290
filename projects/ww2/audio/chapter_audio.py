# Sound for chapters 2-14: an original score generated from a per-chapter mood map (sections start at sentences),
# set-driven ambience beds, explosions on the chapter's camera kicks, and the mix (voice on top, music ducked under
# speech, -15 LUFS integrated, <= -1.2 dBTP).
#   python3 chapter_audio.py chNN <voiceDir> <exportDir> <out.wav>
# exportDir = PART=chNN export (timeline.json: shots with set names, kicks); voiceDir has chNN.wav + chNN_words/lines.json
import sys, os, json
import numpy as np
from dsp import SR, ns, rng, pan, place, dbg, make_ir, convolve_st, integrated, true_peak, read_wav, write_wav, lp, hp, bp, colored, fades, st
import instruments as I
import sfx_gen as X
from mix import limiter, speech_spans

CH, VD, EXP, OUT = sys.argv[1:5]
F = I.m2f

# ---------------------------------------------------------------- mood maps: (sentence index, mood); "sting" = card
MOODS = {
    "ch02": [(0, "comic"), (7, "tense"), (10, "solemn"), (14, "tense"), (16, "comic"), (20, "march"), (28, "comic")],
    "ch03": [(0, "tense"), (4, "spy"), (7, "march"), (9, "tense"), (10, "comic"), (14, "tense"), (17, "comic")],
    "ch04": [(0, "comic"), (5, "winter"), (7, "heroic"), (9, "comic"), (10, "march"), (21, "tense"), (23, "heroic"), (26, "solemn"), (28, "comic"), (32, "tense")],
    "ch05": [(0, "heroic"), (4, "tense"), (6, "battle"), (7, "spy"), (9, "heroic"), (12, "solemn"), (15, "comic"), (20, "tense"), (23, "hopeful")],
    "ch06": [(0, "tense"), (2, "battle"), (5, "comic"), (9, "tense"), (13, "solemn"), (23, "hymn"), (27, "solemn"), (30, "march"), (31, "winter"), (39, "heroic"), (42, "tense")],
    "ch07": [(0, "pacific"), (6, "battle"), (8, "tense"), (12, "comic"), (15, "pacific"), (17, "comic"), (19, "solemn"), (21, "comic"), (26, "tense"),
             (28, "solemn"), (29, "comic"), (31, "tense"), (32, "spy"), (38, "comic"), (39, "triumph"), (43, "pacific"), (48, "solemn"), (50, "hopeful")],
    "ch08": [(0, "comic"), (2, "triumph"), (9, "heroic"), (12, "comic"), (14, "triumph")],
    "ch09": [(0, "tense"), (2, "heroic"), (6, "tense"), (10, "battle"), (13, "heroic"), (16, "tense"), (19, "comic"), (22, "solemn"), (25, "tense"),
             (26, "spy"), (28, "heroic"), (29, "battle"), (32, "heroic"), (34, "comic"), (37, "tense"), (38, "comic")],
    "ch10": [(0, "solemn")],
    "ch11": [(0, "spy"), (6, "tense"), (8, "solemn"), (11, "heroic"), (12, "tense"), (15, "comic"), (19, "battle"), (20, "comic"), (23, "battle"), (25, "heroic"),
             (27, "march"), (31, "tense"), (36, "comic"), (37, "solemn"), (38, "tense"), (42, "solemn"), (44, "triumph"), (46, "tense"), (49, "comic"), (50, "winter"), (53, "comic")],
    "ch12": [(0, "tense"), (7, "solemn"), (8, "tense"), (9, "battle"), (10, "solemn"), (12, "triumph"), (14, "pacific")],
    "ch13": [(0, "pacific"), (5, "battle"), (6, "tense"), (11, "solemn"), (15, "battle"), (17, "solemn"), (31, "hopeful"), (32, "hymn")],
    "ch14": [(0, "solemn"), (2, "tense"), (3, "hopeful"), (4, "tense"), (7, "comic"), (15, "hymn")],
}
NO_STING = {"ch10"}
KEY = {"ch02": 50, "ch03": 48, "ch04": 52, "ch05": 50, "ch06": 47, "ch07": 49, "ch08": 50, "ch09": 47, "ch10": 45, "ch11": 50, "ch12": 48, "ch13": 49, "ch14": 50}
TEMPO = {"comic": 112, "march": 104, "battle": 120, "heroic": 92, "triumph": 100, "tense": 72, "spy": 116, "solemn": 58, "hymn": 64, "hopeful": 80, "winter": 62, "pacific": 76, "sting": 90}
MINOR = {"tense", "solemn", "spy", "battle", "winter", "pacific", "march"}
# music level under the voice (LU) per mood
LEVEL = {"comic": -10.5, "march": -10.0, "battle": -9.5, "heroic": -10.0, "triumph": -9.0, "tense": -11.5, "spy": -11.0, "solemn": -13.0, "hymn": -11.5,
         "hopeful": -11.5, "winter": -12.5, "pacific": -11.0, "sting": -6.0}

lines = json.load(open(f"{VD}/{CH}_lines.json")); words = json.load(open(f"{VD}/{CH}_words.json"))
vx, sr = read_wav(f"{VD}/{CH}.wav"); assert sr == SR
TL = json.load(open(f"{EXP}/timeline.json"))
DUR = TL["total"] / 30.0
N = ns(DUR)
voice = np.zeros(N); v0 = vx[0] if vx.shape[0] == 1 else vx.mean(0); voice[: min(N, len(v0))] = v0[:N]
voice = st(voice)

secs = []
if CH not in NO_STING: secs.append(("sting", 0.0, max(0.5, lines[0]["s"] - 0.2)))
mm = MOODS[CH]
for i, (k, mood) in enumerate(mm):
    a = 0.0 if (i == 0 and CH in NO_STING) else max(0.0, lines[k]["s"] - 0.25)
    if i == 0 and CH not in NO_STING: a = secs[0][2]
    b = DUR if i + 1 == len(mm) else max(0.0, lines[mm[i + 1][0]]["s"] - 0.25)
    secs.append((mood, a, b))

R = rng(hash(CH) % (1 << 30))
_r = lambda: rng(int(R.integers(1 << 30)))
MAJ, MIN = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]
PROG_MIN = [(0, 3, 7), (8, 0, 3), (5, 8, 0), (7, 11, 2)]          # i VI iv V
PROG_MAJ = [(0, 4, 7), (7, 11, 2), (9, 0, 4), (5, 9, 0)]          # I V vi IV


def section(mood, dur, root, seed):
    """render one mood section (stereo, dur s) starting at a bar line"""
    r = rng(seed); rr = lambda: rng(int(r.integers(1 << 30)))
    n = ns(dur + 2.5); y = np.zeros((2, n))
    def add(x, t, p=0.0, g=1.0):
        if t < dur + 0.5: place(y, pan(x, p) if np.ndim(x) == 1 else x, t, g)
    bpm = TEMPO[mood]; beat = 60 / bpm; bar = 4 * beat
    prog = PROG_MIN if mood in MINOR else PROG_MAJ
    nb = int(np.ceil(dur / bar)) + 1
    for b in range(nb):
        t0 = b * bar
        ch = prog[b % 4]; rt = root + ch[0]
        tones = [root + c for c in ch]
        if mood in ("tense", "solemn", "winter", "pacific", "hymn", "hopeful", "spy", "march", "battle", "heroic", "sting"):
            vel = {"solemn": 0.24, "winter": 0.2, "hymn": 0.22, "battle": 0.3, "march": 0.26, "heroic": 0.3, "sting": 0.34}.get(mood, 0.26)
            warm = 500 if mood in ("tense", "battle", "march", "pacific") else 800 if mood != "winter" else 1600
            pv = [F(m - 12) for m in tones] + ([F(tones[1] + 12)] if mood == "winter" else [])
            add(I.pad(pv, bar + 0.4, vel, rr(), att=0.5, rel=0.8, warm=warm), t0)
        if mood == "sting":
            if b == 0:
                for m in (tones + [tones[0] + 12]): add(I.brass(F(m), 1.4, 0.75, rr(), "stab", scoop=-8), 0.25, (m - 55) / 40)
                add(I.timpani(F(root - 12), 0.9, rr()), 0.25); add(I.cymbal(0.5, rr()), 0.25, 0.2)
            continue
        if mood == "comic":
            for k in range(4):
                if k % 2 == 0: add(I.brass(F(rt - 12 + (7 if k == 2 else 0)), beat * 0.6, 0.55, rr(), "tuba", scoop=-18), t0 + k * beat, -0.2)
                else:
                    for m in tones: add(I.pluck(F(m), 0.35, rr(), dur=0.3, bright=0.6), t0 + k * beat, 0.25)
            for k in range(8):
                if r.random() < 0.45: add(I.glock(F(tones[int(r.integers(3))] + 12 + (12 if r.random() < 0.3 else 0)), 0.32, rr()), t0 + k * beat / 2, 0.4)
        elif mood in ("march", "battle"):
            for k in range(4):
                add(I.brass(F(rt - 12), beat * 0.8, 0.6, rr(), "tuba", scoop=-12), t0 + k * beat, -0.15)
                add(I.snare(0.55 if k % 2 == 0 else 0.35, rr()), t0 + k * beat, 0.05)
                add(I.snare(0.22, rr(), dur=0.12), t0 + k * beat + beat * 0.75, 0.05)
            add(I.timpani(F(rt - 12), 0.6 if mood == "battle" else 0.45, rr()), t0)
            if mood == "battle":
                for k in range(8): add(I.timpani(F(rt - 12 + (7 if k % 4 == 3 else 0)), 0.35, rr(), dur=0.6), t0 + k * beat / 2, -0.1)
                if b % 2 == 0: add(I.cymbal(0.35, rr()), t0, 0.3)
            if b % 2 == 0:
                for m in tones: add(I.brass(F(m), bar * 0.45, 0.5, rr(), "horn", scoop=-10), t0, (m - 55) / 40)
        elif mood == "heroic":
            mel = [tones[0] + 12, tones[1] + 12, tones[2] + 12, tones[1] + 12]
            add(I.brass(F(mel[b % 4]), bar * 0.9, 0.5, rr(), "horn", scoop=-12), t0, 0.1)
            add(I.brass(F(rt - 12), bar * 0.9, 0.45, rr(), "tuba", scoop=-14), t0, -0.2)
            for k in range(4): add(I.snare(0.18, rr(), dur=0.15), t0 + k * beat, 0.1)
            add(I.timpani(F(rt - 12), 0.4, rr()), t0)
        elif mood == "triumph":
            for k, d in ((0, 1.5), (1.5, 0.5), (2, 2)):
                for m in tones: add(I.brass(F(m + 12), beat * d * 0.9, 0.62, rr(), "stab", scoop=-8), t0 + k * beat, (m - 55) / 40)
            add(I.brass(F(rt - 12), bar * 0.9, 0.5, rr(), "tuba"), t0, -0.2)
            for k in range(4): add(I.snare(0.4 if k % 2 == 0 else 0.25, rr()), t0 + k * beat)
            if b % 2 == 0: add(I.cymbal(0.4, rr()), t0, 0.25)
            for k in range(4): add(I.glock(F(tones[k % 3] + 24), 0.3, rr()), t0 + k * beat + beat / 2, 0.4)
        elif mood == "spy":
            walk = [tones[0], tones[0] + 3, tones[2], tones[0] + 6 if b % 2 else tones[1]]
            for k in range(8): add(I.pluck(F(walk[k // 2] - 12 + (12 if k % 2 else 0)), 0.45, rr(), dur=0.18, bright=0.35), t0 + k * beat / 2, -0.15)
            for k in range(4): add(I.brush(0.25, rr(), swish=k % 2 == 1), t0 + k * beat, 0.2)
            if r.random() < 0.5: add(I.vibes(F(tones[2] + 12), 0.3, rr()), t0 + 3 * beat, 0.35)
        elif mood == "tense":
            for k in range(8): add(I.pluck(F(rt - 12 + (7 if k % 4 == 2 else 0)), 0.3, rr(), dur=0.25, bright=0.25), t0 + k * beat / 2, -0.1)
            add(I.timpani(F(rt - 12), 0.32, rr()), t0)
        elif mood == "pacific":
            for k in range(8):
                if k in (0, 3, 6): add(I.timpani(F(rt - 12), 0.42 if k == 0 else 0.3, rr(), dur=1.0), t0 + k * beat / 2, -0.1)
            if b % 2 == 1:
                penta = [0, 3, 5, 7, 10]
                ph = [root + 12 + penta[int(r.integers(5))] for _ in range(3)]
                for k, m in enumerate(ph): add(I.fife(F(m), beat * 0.9, 0.3, rr()), t0 + k * beat, 0.25)
        elif mood == "solemn":
            for k in (0, 2):
                if r.random() < 0.8: add(I.pluck(F(tones[(b + k) % 3] + 12), 0.28, rr(), dur=2.2, bright=0.3), t0 + k * beat, 0.15)
        elif mood == "hymn":
            for m in [tones[0] - 12] + tones + [tones[2] + 12]: add(I.brass(F(m), bar * 0.95, 0.32, rr(), "soft", scoop=-6), t0, (m - 55) / 50)
        elif mood == "hopeful":
            for k in range(8): add(I.musicbox(F(tones[k % 3] + 12 + (12 if k >= 4 else 0)), 0.3, rr()), t0 + k * beat / 2, 0.3 * np.sin(k))
        elif mood == "winter":
            if r.random() < 0.6: add(I.glock(F(tones[int(r.integers(3))] + 24), 0.22, rr(), dur=2.5), t0 + beat * r.integers(4), 0.4)
            if b % 2 == 0: add(I.triangle(0.18, rr()), t0, -0.4)
    y = y[:, : ns(dur + 1.5)]
    env = np.ones(y.shape[1]); fi, fo = ns(0.35), ns(1.2)
    env[:fi] = np.linspace(0, 1, fi); env[ns(dur): ns(dur) + fo] = np.linspace(1, 0, min(fo, y.shape[1] - ns(dur))); env[ns(dur) + fo:] = 0
    return y * env


def ambience(name, light, dur, r):
    """set-driven bed (stereo)"""
    s = name.lower(); n = ns(dur)
    def noise_bed(lo, hi, lvl): return st(bp(colored(n, r, -1.0), lo, hi) * lvl)
    has = lambda *ks: any(k in s for k in ks)
    if has("camp", "c10_", "holocaust", "rail", "memorial", "hiroshima", "nagasaki", "trinity"): return X.breeze(dur, r, 0.35, 0.1, 500)
    if has("jungle", "guadal", "lubang", "island", "okinawa"): return st(X.bird_chirps(dur, r, 0.6)) * 0.5 + st(X.crickets(dur, r)) * 0.25 + noise_bed(200, 2000, 0.02)
    if has("sea", "ship", "harbor", "harbour", "pearl", "dunkirk", "midway", "carrier", "channel", "leyte", "beach", "omaha", "fleet", "missouri", "boat"):
        return st(X.water_bed(dur, r, 0.6)) * 0.4 + X.breeze(dur, r, 0.6, 0.2, 900)
    if has("desert", "alamein", "africa", "dune"): return X.breeze(dur, r, 1.0, 0.3, 1400)
    if has("snow", "winter", "moscow", "leningrad", "bastogne", "bulge", "finland", "ardennes", "frozen", "ice"): return X.breeze(dur, r, 0.9, 0.35, 600)
    if has("factory", "plant", "assembly", "shipyard", "forge"): return noise_bed(60, 400, 0.05) + noise_bed(1500, 5000, 0.01)
    if has("sky", "air", "dogfight", "plane", "bomber", "raf", "spitfire", "cockpit"): return noise_bed(80, 900, 0.06)
    if has("front", "stalingrad", "battle", "kursk", "bagration", "ruin", "border", "berlin", "warsaw", "steppe", "trench", "bunker_ext", "iwo"):
        return noise_bed(30, 200, 0.06) + X.breeze(dur, r, 0.5, 0.25, 700)
    if has("street", "city", "paris", "london", "blitz", "vienna", "town", "square", "crowd", "ve_"):
        return X.breeze(dur, r, 0.4, 0.15, 900) + noise_bed(150, 1500, 0.012)
    return noise_bed(40, 300, 0.012)                                   # room tone


def boom(r, big=1.0):
    d = 2.6; n = ns(d); t = np.arange(n) / SR
    body = lp(r.standard_normal(n), 140, 2) * np.exp(-t / 0.5) * 2.2
    thump = np.sin(2 * np.pi * (55 * t - 18 * t * t)) * np.exp(-t / 0.18)
    crack = hp(r.standard_normal(n), 900, 2) * np.exp(-t / 0.05) * 0.5
    deb = bp(r.standard_normal(n), 1500, 6000, 1) * np.exp(-((t - 0.7) / 0.5) ** 2) * 0.12
    return fades((body + thump + crack + deb) * big, 0.001, 0.3)


# ---------------------------------------------------------------- render
music = np.zeros((2, N)); level = np.zeros(N)
for i, (mood, a, b) in enumerate(secs):
    if b - a < 0.3: continue
    x = section(mood, b - a, KEY[CH] + 12 if mood in ("comic", "triumph", "hopeful") else KEY[CH], int(R.integers(1 << 30)))
    place(music, x, a)
    level[ns(a): ns(b)] = LEVEL[mood]
ir = make_ir(1.8, 7, pre=0.02, hf=0.6)
music = music + 0.22 * convolve_st(music.mean(0), ir)[:, :N]

amb = np.zeros((2, N)); sfx = np.zeros((2, N))
for s in TL["shots"]:
    a, b = s["a"] / 30, s["b"] / 30
    x = ambience(s.get("set", ""), s.get("light", ""), b - a + 0.6, _r())
    e = np.ones(x.shape[1]); k = min(ns(0.3), len(e) // 2); e[:k] = np.linspace(0, 1, k); e[-k:] = np.linspace(1, 0, k)
    place(amb, x * e, max(0, a - 0.3))
for t, g in TL.get("kicks", []):
    if t * SR < N: place(sfx, pan(boom(_r(), 0.6 + 0.4 * min(1.5, g)), float(_r().uniform(-0.3, 0.3))), max(0, t - 0.03))

# ---------------------------------------------------------------- mix
spans = speech_spans(words)
ctrl = 1000; nc = int(DUR * ctrl) + 2; va = np.zeros(nc)
for s0, e0 in spans: va[max(0, int((s0 - 0.08) * ctrl)): int((e0 + 0.12) * ctrl)] = 1
env = np.zeros(nc); e = 0.0
for i in range(nc): e += (va[i] - e) * ((1 - np.exp(-1 / 70)) if va[i] > e else (1 - np.exp(-1 / 450))); env[i] = e
duck = np.interp(np.arange(N) / SR, np.arange(nc) / ctrl, -3.0 * env)
Lv = integrated(voice)
Lm = integrated(music * dbg(duck)[None, :])
# per-mood level: music integrated (ducked) set to voice + LEVEL[mood] overall, then the per-section offsets
base = Lv + float(np.mean([LEVEL[m] for m, a, b in secs])) - Lm
off = level - float(np.mean([LEVEL[m] for m, a, b in secs]))
from scipy import ndimage
gcurve = ndimage.uniform_filter1d(base + off, ns(0.5), mode="nearest") + duck
M = music * dbg(gcurve)[None, :]
A = amb * dbg(Lv - 22 - integrated(amb)) if np.isfinite(integrated(amb)) else amb
S = sfx * dbg(Lv - 16 - integrated(sfx)) if np.isfinite(integrated(sfx)) and np.abs(sfx).max() > 0 else sfx
mix = voice + M + A + S
G = -15.0 - integrated(mix)
for it in range(6):
    y, g = limiter(mix * dbg(G))
    L = integrated(y)
    if abs(L + 15.0) < 0.05: break
    G += -15.0 - L
write_wav(OUT, fades(y, 0.002, 0.3))
print(f"{CH}: {DUR:.1f} s, {len(secs)} music sections, {len(TL.get('kicks', []))} kicks, mix {integrated(y):.2f} LUFS, TP {true_peak(y):.2f} dBTP")
