# Original score for WW2 part 1 (cold open + chapter 1), composed and synthesized here. Sections follow the picture:
# domino + war montage (brooding drone, drums) | distant bomb (held, quiet) | jungle (sparse) | title theme (brass, D minor
# -> F major) | chapter sting | Paris (pompous brass + glock) | hyperinflation (accelerating comic oom-pah) | kids (music box) |
# jazz (vibes + brushes) | crash (falling brass) | depression (slow pizzicato) | the beer hall (menacing march) |
# chancellor -> one man's country (dark low brass, no jokes).
import numpy as np
from dsp import SR, ns, rng, pan, place, dbg, make_ir, convolve_st, integrated, hp
import instruments as I
import timeline as T

N = ns(T.DUR)
F = I.m2f
fr = T.fr

SECTIONS = [
    ("open", 0.0, fr(386)), ("jungle", fr(386), fr(504)), ("title", fr(504), fr(779)), ("sting", fr(779), fr(825)),
    ("paris", fr(825), fr(1435)), ("money", fr(1435), fr(1930)), ("kids", fr(1930), fr(2057)), ("jazz", fr(2057), fr(2111)),
    ("crash", fr(2111), fr(2285)), ("depression", fr(2285), fr(2547)), ("rise", fr(2547), fr(3182)), ("dark", fr(3182), T.DUR),
]


class Band:
    def __init__(self):
        self.tr, self.send, self.cues = {}, {}, []

    def add(self, name, x, t, p=0.0, g=1.0, send=0.18):
        if name not in self.tr:
            self.tr[name] = np.zeros((2, N)); self.send[name] = send
        place(self.tr[name], pan(x, p) if np.ndim(x) == 1 else x, t, g)


R = rng(1939)
_r = lambda: rng(int(R.integers(1 << 30)))


def pad(b, t0, t1, ms, vel=0.32, warm=900.0, att=0.6, rel=0.9):
    if t1 - t0 > 0.2:
        b.add("pad", I.pad([F(m) for m in ms], t1 - t0, vel, _r(), att=att, rel=rel, warm=warm), t0)


def roll(b, t0, t1, v0, v1, accent=None):
    for t, v in I.snare_roll(t0, t1, v0, v1, _r()):
        b.add("snare", I.snare(v, _r(), dur=0.14, buzz=True), t, 0.05)
    if accent:
        b.add("snare", I.snare(accent, _r()), t1, 0.05); b.add("cymbal", I.cymbal(accent * 0.6, _r()), t1)


def brass(b, t, ms, dur, vel, kind="stab", p=0.0):
    for m in ms:
        b.add("stab", I.brass(F(m), dur, vel, _r(), kind, scoop=-10), t, p + (m - 55) / 40)


def build():
    b = Band()
    # ===== OPEN 0-12.9: brooding D minor drone, timpani on the domino, war drums under the montage
    pad(b, 0.0, fr(386) + 0.4, [38, 45, 50], 0.3, 600)
    b.add("timpani", I.timpani(F(38), 0.9, _r()), T.DOMINO_T0)
    for k in range(10):
        b.add("timpani", I.timpani(F(38 if k % 2 == 0 else 45), 0.55 + 0.03 * k, _r(), dur=1.0), fr(140) + k * 0.5)
    roll(b, fr(140), fr(212) - 0.05, 0.08, 0.4)
    brass(b, fr(212), [38, 45, 50, 53], 1.8, 0.6, "tuba")
    pad(b, fr(296), fr(386), [62, 69, 74], 0.18, 2200, att=1.5)            # a thin high shimmer for the far flash
    b.cues.append((0.0, "brooding D minor drone; timpani on the domino; war drums + roll under the montage; high shimmer for the far bomb"))
    # ===== JUNGLE 12.9-16.8: sparse, a lonely low flute-like fife and pad
    pad(b, fr(386), fr(504) + 0.3, [41, 48, 53], 0.24, 700)
    for k, m in enumerate([69, 72, 74, 72]):
        b.add("fife", I.fife(F(m), 0.8, 0.45, _r()), fr(400) + k * 0.9, 0.2)
    # ===== TITLE 16.8-26: the main theme, brass over a march snare
    tt = fr(504)
    theme = [(0, 1, 62), (1, .5, 62), (1.5, .5, 65), (2, 1, 69), (3, 1, 67), (4, 1.5, 65), (5.5, .5, 64), (6, 2, 62), (8, 1, 65), (9, .5, 65), (9.5, .5, 69),
             (10, 1, 72), (11, 1, 74), (12, 3, 77)]
    for (bt, d, m) in theme:
        b.add("stab", I.brass(F(m), d * 0.5 * 0.95, 0.7, _r(), "stab", scoop=-8), tt + bt * 0.5, 0.0)
        b.add("glock", I.glock(F(m + 12), 0.25, _r()), tt + bt * 0.5, 0.3)
    for k in range(16):
        b.add("timpani", I.timpani(F(38 if k % 4 == 0 else 45), 0.4, _r(), dur=0.8), tt + k * 0.5)
        if k % 2: b.add("snare", I.snare(0.35, _r()), tt + k * 0.5)
    pad(b, tt, fr(779), [50, 53, 57, 62], 0.3, 900)
    brass(b, tt + 6.0, [41, 53, 57, 60, 65], 2.4, 0.6)
    roll(b, fr(760), fr(779), 0.1, 0.7, accent=0.9)
    # ===== CHAPTER STING
    brass(b, fr(779), [38, 50, 57, 62, 65], 1.4, 0.8); b.add("timpani", I.timpani(F(38), 0.95, _r()), fr(779))
    b.cues.append((fr(504), "main theme on brass + glock over timpani march; snare roll into the chapter sting (brass + timpani + cymbal)"))
    # ===== PARIS 27.5-47.8: pompous brass chorale + glock, a dead stop on "Spoiler"
    tp = fr(825)
    for k, (ms, d) in enumerate([([53, 57, 60, 65], 2.0), ([55, 58, 62, 67], 2.0), ([53, 57, 60, 65], 2.0), ([52, 55, 60, 64], 1.0)]):
        brass(b, tp + k * 2.0, ms, d * 0.9, 0.45, "horn")
    b.add("pluck", I.pluck(F(41), 0.9, _r(), dur=1.0), fr(1027))               # "Spoiler:" stop
    b.add("stab", I.brass(F(46), 0.9, 0.6, _r(), "stab", fall=-40.0), fr(1052))  # "nothing good" droopy brass
    for k, ms in enumerate([[50, 53, 57], [48, 52, 55], [46, 50, 53], [45, 49, 52]]):
        pad(b, fr(1071) + k * 1.8, fr(1071) + (k + 1) * 1.8 + 0.2, ms, 0.26, 800)
    for k in range(8):
        b.add("pluck", I.pluck(F([50, 53, 57, 53][k % 4] - 12), 0.7, _r(), dur=0.4), fr(1071) + k * 0.9)
    roll(b, fr(1380), fr(1410), 0.1, 0.6)
    brass(b, fr(1410), [46, 53, 58, 62], 0.5, 0.8)                                # PAID 2010 stamp
    # ===== MONEY 47.8-64.3: accelerating comic oom-pah (tempo rises with "more... then a lot more")
    t = fr(1435); bpm = 110.0; k = 0
    while t < fr(1930) - 0.2:
        q = 60 / bpm
        root = [41, 48][k % 2]
        b.add("tuba", I.brass(F(root), q * 0.7, 0.6, _r(), "tuba"), t, -0.1)
        b.add("pah", I.brass(F(57 + (k % 4 == 3) * 2), q * 0.4, 0.35, _r(), "horn", scoop=-12), t + q / 2, 0.3)
        if k % 2: b.add("snare", I.snare(0.3, _r()), t + q / 2)
        t += q; k += 1
        if fr(1584) < t < fr(1672): bpm = min(200, bpm * 1.035)
        elif t >= fr(1672): bpm = 132
    b.add("glock", I.glock(F(84), 0.6, _r()), fr(1762)); b.add("glock", I.glock(F(89), 0.6, _r()), fr(1780))  # the price
    b.cues.append((fr(1435), "comic oom-pah that speeds up with the printing press, settles for the bakery"))
    # ===== KIDS 64.3-68.6: music box, a little tumble on "toys"
    for k, m in enumerate([77, 81, 84, 81, 79, 77, 76, 74, 76, 79]):
        b.add("musicbox", I.musicbox(F(m), 0.5, _r()), fr(1935) + k * 0.4, 0.2)
    for k, m in enumerate([84, 81, 77, 74, 72]):
        b.add("musicbox", I.musicbox(F(m), 0.45, _r()), fr(2040) + k * 0.08, 0.1)
    # ===== JAZZ 68.6-70.4: vibes + brushes + walking bass
    for k, m in enumerate([43, 47, 50, 52]):
        b.add("pluck", I.pluck(F(m), 0.85, _r(), dur=0.5), fr(2057) + k * 0.45)
        b.add("brush", I.brush(0.4, _r(), swish=True), fr(2057) + k * 0.45, 0.15)
    for m in [67, 71, 74, 78]:
        b.add("vibes", I.vibes(F(m), 0.35, _r(), dur=1.6), fr(2060), 0.25)
    # ===== CRASH 70.4-76.2: bright ticker tune, then a falling brass slide + timpani on "crashes"
    for k, m in enumerate([72, 74, 76, 79, 81, 84]):
        b.add("glock", I.glock(F(m), 0.4, _r()), fr(2111) + k * 0.25, 0.3)
    for m in [55, 62, 67]:
        b.add("stab", I.brass(F(m), 1.4, 0.75, _r(), "stab", fall=-700.0), fr(2166))
    b.add("timpani", I.timpani(F(36), 0.95, _r()), fr(2166)); b.add("cymbal", I.cymbal(0.6, _r()), fr(2166))
    pad(b, fr(2190), fr(2285) + 0.3, [41, 48, 51], 0.26, 600)
    # ===== DEPRESSION 76.2-84.9: slow sad pizzicato over a low pad, darkens toward "Enter Adolf Hitler"
    pad(b, fr(2285), fr(2547), [38, 45, 50, 53], 0.24, 600)
    for k, m in enumerate([62, 60, 58, 57, 55, 53, 52, 50, 57, 55, 53, 50, 49, 50]):
        b.add("pluck", I.pluck(F(m - 12), 0.6, _r(), dur=0.9), fr(2290) + k * 0.6, -0.1)
    for k in range(4):
        b.add("timpani", I.timpani(F(38), 0.3 + 0.12 * k, _r(), dur=1.2), fr(2470) + k * 0.6)
    # ===== RISE 84.9-106: rejected stamps, then a menacing march that grows with the crowd
    for tm in (fr(2627), fr(2678)):
        brass(b, tm, [44, 50, 56], 0.4, 0.7)
    tr = fr(2707)
    for k in range(int((fr(3182) - tr) / 0.5)):
        t = tr + k * 0.5
        grow = min(1.0, k / 60)
        b.add("timpani", I.timpani(F(38 if k % 2 == 0 else 33), 0.35 + 0.4 * grow, _r(), dur=0.8), t)
        if k % 2 == 1 and t > fr(2902): b.add("snare", I.snare(0.25 + 0.4 * grow, _r()), t)
        if k % 8 == 0 and t > fr(2902): brass(b, t, [38, 45, 50] if (k // 8) % 2 == 0 else [37, 44, 49], 1.8, 0.35 + 0.35 * grow, "tuba")
    pad(b, tr, fr(3182), [38, 45, 49, 53], 0.24, 700)
    brass(b, fr(3119), [38, 45, 50, 53, 57], 1.6, 0.85); b.add("cymbal", I.cymbal(0.5, _r()), fr(3119))
    # ===== DARK 106-121: low brass chords, sparse, no jokes; a final unresolved chord on "one man's country"
    for k, ms in enumerate([[38, 45, 50], [37, 44, 49], [36, 43, 48], [38, 44, 50], [34, 41, 46]]):
        brass(b, fr(3182) + k * 2.6, ms, 2.4, 0.4, "tuba")
        pad(b, fr(3182) + k * 2.6, fr(3182) + (k + 1) * 2.6 + 0.3, [m + 12 for m in ms], 0.22, 600)
    brass(b, fr(3556), [38, 44, 50, 56], 3.0, 0.55, "tuba"); b.add("timpani", I.timpani(F(38), 0.7, _r(), dur=3.0), fr(3556))
    end = np.ones(N); a = ns(T.DUR - 0.8); end[a:] = np.linspace(1, 0, N - a) ** 1.5
    for k in b.tr:
        b.tr[k] *= end[None, :]
    return b


TARGET = {"pad": -4.0, "vibes": -3.0, "snare": -6.0, "cymbal": -11.0, "timpani": -3.0, "tuba": -3.0, "glock": -6.0, "pluck": -3.0,
          "brush": -13.0, "stab": -2.0, "pah": -8.0, "fife": -2.0, "musicbox": -2.0}


def render(b, ref=-20.0):
    hall = make_ir(1.8, 7, pre=0.02, hf=1.4)
    dry = np.zeros((2, N)); wet = np.zeros((2, N)); levels = {}
    for k, x in b.tr.items():
        if not np.any(x):
            continue
        L = integrated(x); g = dbg(ref + TARGET.get(k, -6) - L); levels[k] = round(L, 1)
        x = x * g; b.tr[k] = x; dry += x; wet += b.send[k] * x
    return hp(dry + 0.7 * convolve_st(wet.mean(0), hall), 30, 2), levels
