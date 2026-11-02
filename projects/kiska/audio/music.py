# Original score for the Kiska short, composed and synthesized here. D minor, 120 bpm (Q = 0.5 s). Sections follow the
# picture: fog mystery (hook) | cold island | sneaky pizzicato evacuation | dead stop "Nobody notices." | bombing hits |
# heroic landing march | fog suspense (drops out for the shots) | night drum pulse | "Luckily / Unluckily" sad-brass gag |
# curious music-box explanation (spooky in the dark room) | snare roll into "rifle" | sombre toll | playful dog march,
# ending on a bright chord on "American".
import numpy as np
from dsp import SR, ns, rng, pan, place, fades, dbg, make_ir, convolve_st, integrated, lp, hp
import instruments as I
import timeline as T

N = ns(T.DUR)
Q = 0.5
F = I.m2f
fr = T.fr

SECTIONS = [
    ("hook", 0.0, T.FLASH), ("island", T.FLASH, fr(336)), ("sneak", fr(336), fr(504)), ("stop", fr(504), fr(532)),
    ("bomb", fr(532), fr(651)), ("landing", fr(651), fr(810)), ("fog", fr(810), fr(1005)), ("night", fr(1005), fr(1131)),
    ("gag", fr(1131), fr(1247)), ("explain", fr(1247), fr(1446)), ("rifle", fr(1446), fr(1508)), ("toll", fr(1508), fr(1685)),
    ("dogs", fr(1685), T.DUR),
]


class Band:
    def __init__(self):
        self.tr, self.send, self.cues = {}, {}, []

    def add(self, name, x, t, p=0.0, g=1.0, send=0.18):
        if name not in self.tr:
            self.tr[name] = np.zeros((2, N))
            self.send[name] = send
        place(self.tr[name], pan(x, p) if np.ndim(x) == 1 else x, t, g)


R = rng(1943)


def _r():
    return rng(int(R.integers(1 << 30)))


def pad(b, t0, t1, ms, vel=0.35, warm=900.0, att=0.6, rel=0.9, trem=None):
    if t1 - t0 > 0.2:
        b.add("pad", I.pad([F(m) for m in ms], t1 - t0, vel, _r(), att=att, rel=rel, warm=warm, trem=trem), t0, 0.0)


def snare_roll(b, t0, t1, v0, v1, accent=None):
    for t, v in I.snare_roll(t0, t1, v0, v1, _r()):
        b.add("snare", I.snare(v, _r(), dur=0.14, buzz=True), t, 0.05)
    if accent:
        b.add("snare", I.snare(accent, _r()), t1, 0.05)
        b.add("cymbal", I.cymbal(accent * 0.5, _r()), t1, 0.0)


def build():
    b = Band()
    # ============ HOOK 0-5.4: fog mystery: low Dm pad, vibes tremolo figure, snare swell into the flash
    pad(b, 0.0, T.FLASH + 0.3, [38, 50, 53, 57], 0.32, 700)
    for k, m in enumerate([62, 65, 69, 65, 62, 65, 69, 72, 69, 65]):
        b.add("vibes", I.vibes(F(m), 0.3, _r(), dur=1.4, trem_depth=0.35), 0.25 + k * 0.5, 0.2)
    snare_roll(b, T.FLASH - 1.6, T.FLASH, 0.08, 0.6, accent=0.8)
    b.add("timpani", I.timpani(F(38), 0.8, _r()), T.FLASH, -0.1)
    b.cues.append((0.0, "fog mystery: low D minor pad, vibes tremolo arpeggio, snare swell + timpani on the flash"))
    # ============ ISLAND 5.4-11.2: cold and lonely: low brass Dm - Bb - Gm - A, glock icicles
    for (t0, t1, ms, bass) in [(5.4, 6.9, [50, 53, 57], 38), (6.9, 8.4, [50, 53, 58], 34), (8.4, 9.9, [50, 55, 58], 43), (9.9, 11.2, [49, 52, 57], 45)]:
        pad(b, t0, t1 + 0.2, ms, 0.3, 800, att=0.3, rel=0.4)
        b.add("tuba", I.brass(F(bass), t1 - t0 - 0.1, 0.5, _r(), "tuba", scoop=-10), t0, -0.1)
    for k, m in enumerate([81, 77, 74, 76, 81, 79, 77, 76]):
        b.add("glock", I.glock(F(m), 0.4, _r()), 5.6 + k * 0.7, 0.3)
    b.cues.append((5.4, "cold island: low brass Dm-Bb-Gm-A, glockenspiel 'icicles'"))
    # ============ SNEAK 11.2-16.8: sneaky pizzicato walk in D minor, brushes
    walk = [50, 53, 57, 53, 52, 55, 58, 55, 50, 53, 57, 60, 58, 57, 55, 52, 50, 53, 57, 62, 61, 57, 52, 49]
    t0 = 11.27
    for k, m in enumerate(walk):
        t = t0 + k * Q * 0.5
        if t > 16.75:
            break
        b.add("pluck", I.pluck(F(m - 12), 0.75, _r(), dur=0.35, bright=0.35), t, -0.1)
        if k % 2 == 0:
            b.add("brush", I.brush(0.35, _r()), t, 0.15)
    for k, m in enumerate([74, 0, 77, 0, 76, 74, 73, 0, 74]):
        if m:
            b.add("vibes", I.vibes(F(m), 0.25, _r(), dur=0.6, damp=0.3), 12.27 + k * 0.5, 0.25)
    b.cues.append((11.27, "sneaky pizzicato walk (staccato eighths), vibes answers"))
    # ============ STOP 16.8: one plucked note, then nothing for "Nobody notices."
    b.add("pluck", I.pluck(F(38), 0.9, _r(), dur=1.2, bright=0.2), 16.8, 0.0)
    b.cues.append((16.8, "single low pluck, silence under 'Nobody notices.'"))
    # ============ BOMB 17.7-21.7: low brass stabs + timpani on each bomb
    for k, f in enumerate(T.BOOMS):
        tb = fr(f)
        for m in [38, 45, 50, 53]:
            b.add("stab", I.brass(F(m + (0, 1, -2, 3)[k]), 0.25, 0.65, _r(), "stab", scoop=-14), tb, (m - 45) / 20)
        b.add("timpani", I.timpani(F(38 + (0, 1, -2, 3)[k]), 0.85, _r()), tb, -0.1)
    pad(b, 17.7, 21.7, [38, 45, 50], 0.25, 600)
    b.cues.append((17.7, "drone + low brass stab and timpani on every bomb"))
    # ============ LANDING 21.7-27: heroic march in D major: snare march pattern, oom-pah, fife melody
    SN = [3, 0, 1, 1, 2, 0, 1, 0, 3, 0, 1, 1, 2, 0, 1, 1]
    tl = 21.7
    for bar in range(3):
        tb = tl + bar * 4 * Q
        for s_, v in enumerate(SN):
            if v:
                b.add("snare", I.snare(0.6 * {1: 0.5, 2: 0.9, 3: 1.0}[v], _r()), tb + s_ * Q / 4, 0.05)
        for beat in range(4):
            root = [38, 45, 43, 45][(bar * 4 + beat) // 4 % 4]
            b.add("tuba", I.brass(F(root if beat % 2 == 0 else root + 7), 0.28, 0.7, _r(), "tuba"), tb + beat * Q, -0.1)
            for kk, m in enumerate([57, 62, 66]):
                b.add("pah", I.brass(F(m), 0.14, 0.38, _r(), "horn", scoop=-12), tb + beat * Q + Q / 2 + 0.004 * kk, 0.3 - 0.12 * kk)
    mel = [(0, 1, 74), (1, .5, 74), (1.5, .5, 76), (2, 1, 78), (3, 1, 74), (4, 1, 79), (5, .5, 78), (5.5, .5, 76), (6, 1.5, 74), (7.5, .5, 71),
           (8, 1, 74), (9, 1, 78), (10, 2, 81)]
    for (bt, d, m) in mel:
        b.add("fife", I.fife(F(m), d * Q * 0.9, 0.75, _r()), tl + bt * Q, 0.0)
    b.add("cymbal", I.cymbal(0.5, _r()), fr(763), 0.0)
    for m in [50, 57, 62, 66, 69]:
        b.add("stab", I.brass(F(m), 1.2, 0.7, _r(), "stab", scoop=-10), fr(763), (m - 60) / 20)
    b.add("timpani", I.timpani(F(38), 0.8, _r()), fr(763), -0.1)
    b.cues.append((21.7, "heroic landing march (D major): snare, oom-pah, fife; brass chord + cymbal on 'ready for the fight'"))
    # ============ FOG 27-33.5: suspense: high thin pad, low pulse, cut out before the shots
    pad(b, 27.0, 31.2, [62, 63, 69], 0.22, 1200, att=0.8, rel=0.3)
    pad(b, 27.0, 31.2, [38], 0.3, 400, att=0.5, rel=0.3)
    for k in range(6):
        b.add("timpani", I.timpani(F(38), 0.25, _r(), dur=0.8), 27.2 + k * 0.66, -0.1)
    b.cues.append((27.0, "fog suspense: thin dissonant pad + soft heartbeat timpani, drops out for the first shot"))
    # ============ NIGHT 33.5-37.7: low drum pulse and dark pad, sting on "same side"
    pad(b, 33.5, 37.0, [38, 41, 45], 0.28, 500)
    for k in range(7):
        b.add("timpani", I.timpani(F(38), 0.4 if k % 2 == 0 else 0.25, _r(), dur=0.8), 33.55 + k * 0.5, -0.1)
    for m in [62, 65, 68]:
        b.add("stab", I.brass(F(m), 0.6, 0.55, _r(), "stab", scoop=-8, fall=0.0), fr(1104), (m - 65) / 10)
    b.cues.append((33.5, "night: dark pad, timpani pulse, brass sting on 'same side'"))
    # ============ GAG 37.7-41.6: "Luckily" bright chord, "Unluckily" sad brass fall
    for m in [62, 66, 69, 74]:
        b.add("vibes", I.vibes(F(m), 0.4, _r(), dur=1.2), fr(1131), 0.2)
    for k, m in enumerate([58, 57, 56, 55]):
        b.add("stab", I.brass(F(m), 0.35 if k < 3 else 0.9, 0.6, _r(), "stab", scoop=-5, fall=-60.0 if k == 3 else 0.0), fr(1182) + k * 0.36, 0.0)
    b.cues.append((37.7, "'Luckily' bright vibes chord; 'Unluckily' sad-trombone four-note fall"))
    # ============ EXPLAIN 41.6-48.2: curious music box, spooky vibes in the dark room
    box = [69, 72, 76, 72, 74, 77, 81, 77, 76, 72, 69, 72, 71, 68, 64, 0]
    for k, m in enumerate(box):
        if m:
            b.add("musicbox", I.musicbox(F(m), 0.5, _r()), 41.6 + k * 0.4, 0.2)
    pad(b, 41.6, 48.2, [45, 52, 57, 60], 0.24, 900)
    for k, m in enumerate([69, 68, 69, 68, 69, 72, 71]):
        b.add("vibes", I.vibes(F(m), 0.3, _r(), dur=1.0, trem_depth=0.5), 44.8 + k * 0.45, -0.2)
    b.cues.append((41.6, "curious music-box tune, then spooky tremolo vibes in the dark room"))
    # ============ RIFLE 48.2-50.2: snare roll into a stab on "rifle"
    snare_roll(b, 48.2, fr(1487), 0.1, 0.7, accent=0.85)
    for m in [50, 56, 62]:
        b.add("stab", I.brass(F(m), 0.3, 0.75, _r(), "stab"), fr(1487), 0.0)
    # ============ TOLL 50.2-56.1: sombre slow brass chorale + pad, timpani on the trap and the mine
    for (t0, t1, ms) in [(50.3, 52.3, [38, 50, 53, 57]), (52.3, 54.3, [34, 50, 53, 58]), (54.3, 56.1, [33, 49, 52, 57])]:
        pad(b, t0, t1 + 0.2, ms[1:], 0.3, 700)
        b.add("tuba", I.brass(F(ms[0]), t1 - t0, 0.45, _r(), "tuba", scoop=-6), t0, -0.1)
    for tm in (T.TRAP, T.MINE):
        b.add("timpani", I.timpani(F(38), 0.9, _r()), tm, -0.1)
    b.cues.append((50.3, "sombre chorale Dm-Bb-A, timpani on the booby trap and the mine"))
    # ============ DOGS 56.2-64.6: playful dog march: pizz bass, glock tune, light snare; bright chord on "American"
    td = 56.25
    bass = [50, 57, 50, 57, 55, 62, 55, 62, 50, 57, 50, 57, 45, 52, 45, 52]
    for k in range(32):
        t = td + k * Q * 0.5
        if t > 63.55:
            break
        b.add("pluck", I.pluck(F(bass[k % 16] - 12), 0.8, _r(), dur=0.3, bright=0.45), t, -0.1)
        if k % 2 == 1:
            b.add("brush", I.brush(0.3, _r()), t, 0.15)
    tune = [(0, .5, 74), (.5, .5, 76), (1, .5, 78), (1.5, .5, 74), (2, 1, 81), (3, 1, 78), (4, .5, 79), (4.5, .5, 78), (5, .5, 76), (5.5, .5, 74),
            (6, 1, 76), (7, 1, 0), (8, .5, 74), (8.5, .5, 76), (9, .5, 78), (9.5, .5, 81), (10, 1, 83), (11, 1, 81), (12, 2, 78)]
    for (bt, d, m) in tune:
        if m:
            b.add("glock", I.glock(F(m), 0.5, _r()), td + bt * Q, 0.25)
    fin = fr(1908)
    for m in [50, 62, 66, 69, 74, 78]:
        b.add("vibes", I.vibes(F(m), 0.5, _r(), dur=1.4), fin, 0.2)
        b.add("stab", I.brass(F(m - 12), 0.6, 0.5, _r(), "stab", scoop=-10), fin, 0.0)
    b.add("triangle", I.triangle(0.4, _r()), fin, 0.3)
    b.add("cymbal", I.cymbal(0.3, _r(), dur=1.4), fin, 0.0)
    b.cues.append((56.25, "playful dog march: pizzicato bass, glockenspiel tune, brushes; bright D major chord on 'American'"))
    end = np.ones(N)
    a = ns(T.DUR - 0.5)
    end[a:] = np.linspace(1, 0, N - a) ** 1.5
    for k in b.tr:
        b.tr[k] *= end[None, :]
    return b


TARGET = {"pad": -4.0, "vibes": -3.0, "snare": -5.0, "cymbal": -11.0, "timpani": -4.0, "tuba": -3.0, "glock": -5.0, "pluck": -2.5,
          "brush": -13.0, "stab": -3.0, "pah": -8.0, "fife": -1.0, "musicbox": -2.0, "triangle": -14.0}


def render(b, ref=-20.0):
    hall = make_ir(1.6, 7, pre=0.018, hf=1.4)
    dry = np.zeros((2, N))
    wet = np.zeros((2, N))
    levels = {}
    for k, x in b.tr.items():
        if not np.any(x):
            continue
        L = integrated(x)
        g = dbg(ref + TARGET.get(k, -6) - L)
        levels[k] = (round(L, 1), round(ref + TARGET.get(k, -6), 1))
        x = x * g
        b.tr[k] = x
        dry += x
        wet += b.send[k] * x
    out = dry + 0.7 * convolve_st(wet.mean(0), hall)
    out = hp(out, 30, 2)
    return out, levels
