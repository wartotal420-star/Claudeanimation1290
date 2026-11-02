# Every sound effect + ambience bed of the Kiska short as a cue list timed to the picture (timeline.py), rendered into
# one stereo SFX stem. Same level rule as the bridge short: EVENTS sit SFX_DB = -6 dB under their "naive" level
# (LU relative to the voice, max momentary loudness); ambience BEDS (integrated) are not reduced.
import numpy as np
from dsp import (SR, ns, tt, rng, dbg, lp, hp, bp, peq, pan, place, fades, widen, make_ir, convolve_st,
                 momentary_max, integrated, colored, smooth_noise, modal, phase)
import sfx_gen as G
import instruments as I
import timeline as T

N = ns(T.DUR)
SFX_DB = -6.0


class Cue:
    def __init__(self, t, name, desc, gen, naive, kind="event", p=0.0, extra=0.0, lpf=None, send=0.12, group=None, cut=None):
        self.t, self.name, self.desc, self.gen, self.naive = t, name, desc, gen, naive
        self.kind, self.p, self.extra, self.lpf, self.send, self.cut = kind, p, extra, lpf, send, cut
        self.group = group or name
        self.applied = naive + (SFX_DB if kind == "event" else 0.0) + extra
        self.measured = None


# ---------------------------------------------------------------- synth helpers (our own)
def gunshot(r, far=0.0):
    """rifle shot: supersonic crack + muzzle boom + rolling tail (far: duller, longer)"""
    d = 1.6
    t = tt(d)
    nz = r.standard_normal(len(t))
    crack = hp(nz, 2500) * np.exp(-t / 0.0025) * 1.6 * (1 - 0.7 * far)
    boom = lp(nz, 900, 2) * np.exp(-t / 0.03) * 2.2
    thump = np.sin(phase(70 * (1 + 0.8 * np.exp(-t / 0.01)))) * np.exp(-t / 0.06) * 1.2
    tail = lp(colored(len(t), r, 1.2), 700 - 300 * far, 2) * np.exp(-t / (0.35 + 0.4 * far)) * 0.5 * np.clip(t / 0.02, 0, 1)
    y = crack + boom + thump + tail
    if far:
        y = lp(y, 2500, 2)
    return fades(y, 0.0, 0.2)


def explosion(r, big=1.0, water=False):
    d = 3.5
    t = tt(d)
    nz = colored(len(t), r, 1.6)
    body = lp(nz, 260, 2) * np.exp(-t / (0.35 * big)) * np.clip(t / 0.006, 0, 1) * 3.0
    sub = np.sin(phase(42 * (1 + 0.9 * np.exp(-t / 0.05)))) * np.exp(-t / 0.4) * 2.0
    crack = bp(r.standard_normal(len(t)), 800, 6000, 1) * np.exp(-t / 0.02) * 1.2
    debris = G.rattle(2.0, r, 45, np.exp(-np.linspace(0, 1, ns(2.0)) * 3), heavy=True) * 0.35
    y = body + sub + crack
    G._place_mono(y, debris, 0.15)
    if water:
        G._place_mono(y, G.splash_big(r).mean(0) if np.ndim(G.splash_big(r)) == 2 else G.splash_big(r), 0.25)
    return fades(y * big, 0.0, 0.3)


def bomb_whistle(r, dur=0.9):
    t = tt(dur)
    f = 1900 * (1 - 0.55 * t / dur)
    return fades(np.sin(phase(f)) * (0.3 + 0.7 * t / dur) * 0.6, 0.05, 0.01)


def drone(dur, r, f0=78.0, n_eng=4):
    """piston bombers passing over: beating engine harmonics, swelling then fading"""
    t = tt(dur)
    y = np.zeros(len(t))
    for k in range(n_eng):
        ff = f0 * (1 + 0.012 * k) * (1 + 0.03 * np.sin(2 * np.pi * 0.2 * t + k))
        for h in range(1, 7):
            y += np.sin(phase(ff * h)) / h ** 1.1
    y += 0.3 * bp(colored(len(t), r, 1.0), 200, 1800, 1)
    env = np.exp(-0.5 * ((t - dur * 0.45) / (dur * 0.25)) ** 2)
    return fades(lp(y * env, 2200, 2) * 0.3, 0.3, 0.5)


def ship_rumble(dur, r):
    t = tt(dur)
    y = lp(colored(len(t), r, 2.0), 120, 2) * 1.2 + 0.4 * np.sin(phase(38 + 2 * np.sin(2 * np.pi * 0.3 * t)))
    return fades(y * (0.6 + 0.4 * smooth_noise(len(t), r, 0.2)), 0.8, 0.8)


def foghorn(r, dur=2.6):
    t = tt(dur)
    y = sum(np.sin(phase(98 * h)) / h for h in range(1, 9))
    y = lp(y, 900, 2) * np.clip(t / 0.25, 0, 1) * np.clip((dur - t) / 0.6, 0, 1)
    return y * 0.4


def woof(r, small=False, happy=False):
    """one bark: a short formant 'wuf' with a pitch flick"""
    d = 0.16 if happy else 0.2
    n = ns(d + 0.05)
    t = np.arange(n) / SR
    base = (420 if small else 300) * r.uniform(0.9, 1.1)
    f0 = base * G._track(n, [(0, 1.0), (0.03, 1.35), (d, 0.85)], t)
    forms = G.vowel_track(n, [(0, "U"), (0.04, "a"), (d, "U")])
    amp = np.clip(t / 0.006, 0, 1) * np.clip((d - t) / 0.05, 0, 1)
    y = G.vox(f0, forms, amp, r, 0.75 if small else 0.85, tilt=0.9, breath=0.45)
    return fades(y + hp(r.standard_normal(n), 1500) * np.exp(-t / 0.01) * 0.3, 0.001, 0.02)


def pant(dur, r):
    t = tt(dur)
    y = bp(r.standard_normal(len(t)), 900, 3500, 1) * (0.5 + 0.5 * np.sin(2 * np.pi * 5.2 * t)) ** 3
    return y * 0.4


def rifle_click(r):
    return modal(0.12, [(2800, 0.7, 0.01), (5200, 0.4, 0.006), (1300, 0.5, 0.012)], r) + hp(r.standard_normal(ns(0.12)), 3000) * np.exp(-tt(0.12) / 0.004) * 0.6


def boots_sand(dur, r, rate=6.0):
    out = np.zeros((2, ns(dur)))
    tm = r.uniform(0, 0.1)
    while tm < dur - 0.3:
        x = G.stroll_step(r, 1.0)
        x = lp(x, 2500, 1) + bp(r.standard_normal(len(x)), 1500, 6000, 1) * np.exp(-tt(len(x) / SR) / 0.04) * 0.3
        place(out, pan(x * r.uniform(0.4, 1.0), r.uniform(-0.8, 0.8)), tm)
        tm += r.exponential(1 / rate) + 0.03
    return out


def surf(dur, r, level=1.0):
    n = ns(dur)
    t = np.arange(n) / SR
    out = np.zeros((2, n))
    for ch in range(2):
        swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / 7.5 + ch * 0.8 + r.uniform(0, 6)) ** 2
        out[ch] = lp(colored(n, r, 1.0), 1400, 2) * swell * level + 0.2 * bp(colored(n, r, 0.5), 2000, 7000, 1) * swell ** 3 * level
    return out


# ---------------------------------------------------------------- part-1 helpers
def click(r, hard=1.0):
    return modal(0.08, [(r.uniform(2600, 3400), 0.6, 0.006), (r.uniform(5200, 6400), 0.4, 0.004), (r.uniform(900, 1300), 0.5, 0.012)], r) * hard


def domino_cascade(r, n, dt):
    out = np.zeros(ns(n * dt + 0.5))
    for i in range(n):
        G._place_mono(out, click(r, r.uniform(0.5, 1.0)) * (0.9 ** (i / 40)), i * dt + r.normal(0, 0.003))
    return out


def press_clatter(dur, r, rate=4.0):
    out = np.zeros(ns(dur))
    k = 0
    tm = 0.0
    while tm < dur - 0.3:
        G._place_mono(out, modal(0.25, [(r.uniform(150, 220), 1.0, 0.04), (r.uniform(500, 700), 0.6, 0.02), (1900, 0.3, 0.01)], r) * 0.8, tm)
        G._place_mono(out, rifle_click(r) * 0.4, tm + 0.11)
        k += 1
        tm += 1 / rate
        rate = min(9.0, rate * 1.01)
    return out


def rustle(dur, r):
    t = tt(dur)
    return bp(r.standard_normal(len(t)), 1500, 7000, 1) * (0.4 + 0.6 * np.abs(smooth_noise(len(t), r, 6.0))) * 0.5


def murmur(dur, r, people=12, base=(95, 180)):
    out = np.zeros((2, ns(dur)))
    for k in range(people):
        y = G.babble(dur, r, r.uniform(*base), r.uniform(0.9, 1.15), rate=r.uniform(3.5, 5), active=0.6)
        out += pan(lp(y, r.uniform(2500, 4000), 1) * r.uniform(0.3, 0.8), r.uniform(-0.8, 0.8))
    return out


def cheer(r, people=14):
    out = np.zeros((2, ns(1.6)))
    for k in range(people):
        place(out, pan(G.hurrah(r, r.uniform(100, 170), r.uniform(0.95, 1.12)) * r.uniform(0.4, 1.0), r.uniform(-0.8, 0.8)), r.uniform(0, 0.5))
    return out


def crackle(dur, r):
    out = np.zeros(ns(dur))
    tm = 0.0
    while tm < dur - 0.05:
        G._place_mono(out, hp(r.standard_normal(ns(0.02)), 2000) * np.exp(-tt(0.02) / 0.004) * r.uniform(0.2, 1.0), tm)
        tm += r.exponential(0.04)
    return out + lp(colored(ns(dur), r, 1.5), 300, 2) * 0.3


# ---------------------------------------------------------------- cue list
def cues():
    C = []
    R = rng(1919)
    rr = lambda: rng(int(R.integers(1 << 30)))
    add = C.append
    s = T.shot_t
    fr = T.fr

    def bed(a, b, gen, naive, name, desc):
        add(Cue(a, name, desc, lambda: (fades(gen(b - a), 0.3, 0.4), 0.0), naive, kind="bed", send=0.05))
    # beds
    bed(0.0, s(1)[1], lambda d: G.breeze(d, rr(), 0.2, 0.1, 300), -38, "room_void", "near-silent air (void)")
    bed(s(2)[0], s(4)[1], lambda d: G.breeze(d, rr(), 1.0, 0.25, 600) + 0.5 * np.stack([crackle(d, rr()), crackle(d, rr())]), -26, "amb_front", "wind, distant fires crackling")
    bed(s(5)[0], s(5)[1], lambda d: G.bird_chirps(d, rr(), 1.2, "sparrow") * 0.6 + G.crickets(d, rr(), 4), -26, "amb_jungle", "jungle birds + insects")
    bed(s(6)[0], s(8)[1], lambda d: G.breeze(d, rr(), 0.25, 0.1, 400), -36, "room_war", "quiet room tone")
    bed(s(9)[0], s(12)[1], lambda d: murmur(d, rr(), 10) * 0.6, -30, "amb_paris", "a hall of murmuring diplomats")
    bed(s(13)[0], s(13)[1], lambda d: np.stack([press_clatter(d, rr()), press_clatter(d, rr())]) * 0.7, -22, "press", "printing press thumping and clattering, speeding up")
    bed(s(14)[0], s(15)[1], lambda d: murmur(d, rr(), 4) * 0.4, -32, "amb_bakery", "a few customers")
    bed(s(17)[0], s(17)[1], lambda d: murmur(d, rr(), 8) * 0.6, -28, "amb_jazz", "evening street chatter")
    bed(s(18)[0], s(18)[1], lambda d: murmur(d, rr(), 8) * 0.7, -28, "amb_stocks", "trading floor chatter")
    bed(s(19)[0], s(20)[1], lambda d: G.breeze(d, rr(), 0.8, 0.2, 700) + murmur(d, rr(), 10) * 0.4, -28, "amb_street", "grey street, low murmur")
    bed(s(22)[0], s(22)[1], lambda d: murmur(d, rr(), 6) * 0.6, -28, "amb_beer", "back-room chatter")
    bed(s(23)[0], s(23)[1], lambda d: murmur(d, rr(), 24) * 0.8, -24, "amb_crowd", "a growing crowd")
    bed(s(24)[0], T.DUR, lambda d: G.breeze(d, rr(), 0.7, 0.15, 500) + 0.6 * np.stack([crackle(d, rr()), crackle(d, rr())]), -28, "amb_night", "night street, torches crackling")
    # events
    add(Cue(T.DOMINO_T0, "domino", "first domino tips, then the cascade", lambda r=rr(): (domino_cascade(r, 120, T.DOMINO_DT), 0.0), -10, send=0.2))
    add(Cue(fr(140), "tanks", "tank engines and tracks rolling past", lambda r=rr(): (lp(drone(2.6, r, 52, 2), 900, 2) + 0.4 * G.rattle(2.6, r, 40, heavy=True), 0.0), -6, send=0.1))
    add(Cue(fr(212), "bombers", "bombers droning over the ruins", lambda r=rr(): (drone(2.4, r, 80), 0.0), -8, send=0.1))
    add(Cue(fr(240), "far_boom", "distant explosions", lambda r=rr(): (lp(explosion(r, 0.7), 900, 2), 0.0), -12, send=0.4))
    add(Cue(fr(300), "far_flash", "a deep, far-away rumble (no impact shown)", lambda r=rr(): (lp(explosion(r, 1.4), 300, 2), 0.0), -10, send=0.6))
    add(Cue(fr(830), "pen", "pens scratching, paper", lambda r=rr(): (rustle(1.5, r), 0.0), -24))
    add(Cue(fr(1100), "sign", "German delegate signs", lambda r=rr(): (rustle(1.0, r), 0.0), -20))
    for i in range(10):
        add(Cue(fr(1190) + i * 0.06 + 0.15, "toy", "toy soldiers clatter over", lambda r=rr(): (click(r, 1.0), 0.0), -18, p=-0.3 + i * 0.06))
    add(Cue(fr(1294), "unroll", "the bill unrolls down the carpet", lambda r=rr(): (G.whoosh(3.4, r, 3.0, 300, 1400, 0.9, 0.4, 0.2) + rustle(3.4, r) * 0.6, 0.0), -14, send=0.2))
    add(Cue(fr(1410), "stamp", "PAID stamp slams down", lambda r=rr(): (G.hammer_hit(r, 1.0), 0.0), -6, send=0.2))
    add(Cue(fr(1440), "notes", "banknotes fluttering", lambda r=rr(): (rustle(7.5, r), 0.0), -22))
    add(Cue(fr(1680), "bell", "shop bell", lambda r=rr(): (modal(1.2, [(2350, 0.6, 0.4), (3600, 0.4, 0.25), (5100, 0.2, 0.15)], r), 0.0), -18))
    add(Cue(fr(1858), "tag_flip", "price tag flips higher", lambda r=rr(): (click(r, 1.0), 0.0), -14))
    add(Cue(fr(1890), "tag_flip", "price tag flips higher again", lambda r=rr(): (click(r, 1.0), 0.0), -14))
    add(Cue(fr(2040), "tower", "cash tower topples", lambda r=rr(): (rustle(0.8, r) + 0.6 * G.rattle(0.8, r, 30), 0.0), -14))
    add(Cue(fr(2166), "crash", "the market crashes: groans across the floor", lambda r=rr(): (murmur(1.6, r, 10, (90, 140)) * 1.2, 0.0), -10))
    add(Cue(fr(2627), "stamp", "REJECTED", lambda r=rr(): (G.hammer_hit(r, 0.9), 0.0), -6))
    add(Cue(fr(2678), "stamp", "REJECTED again", lambda r=rr(): (G.hammer_hit(r, 0.9), 0.0), -6))
    add(Cue(fr(2860), "crate", "steps up onto the beer crate", lambda r=rr(): (G.stroll_step(r, 1.0), 0.0), -16))
    for k in range(4):
        add(Cue(fr(2870) + k * 0.4, "clink", "steins clink", lambda r=rr(): (G.clink(r), 0.0), -20, p=(k - 1.5) * 0.4))
    add(Cue(fr(3119), "cheer", "the crowd cheers", lambda r=rr(): (cheer(r, 18), 0.0), -6, send=0.3))
    add(Cue(fr(3312), "padlock", "padlock snaps shut, chain rattles", lambda r=rr(): (np.concatenate([G.clink(r), np.zeros(ns(0.6))])[:ns(0.6)] + 0.5 * G.rattle(0.6, r, 25), 0.0), -10))
    add(Cue(fr(3410), "steps", "a family's footsteps, suitcases", lambda r=rr(): (boots_sand(2.6, r, 3.0), 0.0), -22))
    return C


# ================================================================ render
def render(v_ref, on_event=None):
    C = cues()
    out = np.zeros((2, N))
    send = np.zeros(N)
    for c in C:
        x, anchor = c.gen()
        x = np.asarray(x, float)
        x = pan(x, c.p) if x.ndim == 1 else x
        if c.cut is not None:
            k = ns(c.cut - (c.t - anchor))
            if 0 < k < x.shape[1]:
                x = fades(x[:, :k], 0.0, 0.02)
        tgt = v_ref + c.applied
        cur = momentary_max(x) if c.kind == "event" else integrated(x)
        if np.isfinite(cur):
            x = x * dbg(tgt - cur)
        if c.lpf:
            x = lp(x, c.lpf, 1)
        c.measured = momentary_max(x) - v_ref if c.kind == "event" else integrated(x) - v_ref
        t0 = c.t - anchor
        place(out, x, t0)
        if on_event:
            on_event(c, x, t0)
        if c.send > 0:
            G._place_mono(send, c.send * x.mean(0), t0)
    valley = make_ir(1.6, 77, pre=0.012, hf=1.4, early=[(0.09, 0.45, -0.5), (0.14, 0.3, 0.6), (0.23, 0.2, -0.2)])
    out += 0.55 * convolve_st(send, valley)
    out = hp(out, 25, 2)
    end = ns(T.DUR - 0.12)
    out[:, end:] *= np.linspace(1, 0, N - end)[None, :] ** 2
    return out, C
