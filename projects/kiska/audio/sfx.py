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


# ---------------------------------------------------------------- cue list
def cues():
    C = []
    R = rng(1943)
    rr = lambda: rng(int(R.integers(1 << 30)))
    add = C.append
    s = T.shot_t

    # beds
    def bed(a, b, gen, naive, name, desc):
        add(Cue(a, name, desc, lambda: (fades(gen(b - a), 0.4, 0.5), 0.0), naive, kind="bed", send=0.05))
    bed(0.0, T.FLASH, lambda d: G.breeze(d, rr(), 1.0, 0.25, 700) + surf(d, rr(), 0.6), -24, "amb_fogbeach", "wind + low surf on the fog beach (hook)")
    bed(T.FLASH, s(5)[1], lambda d: G.breeze(d, rr(), 1.2, 0.2, 900) + surf(d, rr(), 0.8), -24, "amb_island", "Aleutian wind, surf (island, harbor)")
    bed(s(6)[0], s(9)[0], lambda d: surf(d, rr(), 1.0) + G.breeze(d, rr(), 0.6, 0.2, 600), -24, "amb_landing", "surf on the landing beach, then fog hush")
    bed(s(9)[0], s(10)[0], lambda d: G.breeze(d, rr(), 0.7, 0.1, 400), -30, "amb_night", "night wind")
    bed(s(10)[0], s(13)[0], lambda d: G.breeze(d, rr(), 1.0, 0.25, 800), -26, "amb_empty", "wind through the empty camp / fog")
    bed(s(15)[0], s(16)[0], lambda d: G.breeze(d, rr(), 0.8, 0.2, 700) + surf(d, rr(), 0.7), -26, "amb_toll", "wind, sea")
    bed(s(16)[0], T.DUR, lambda d: G.breeze(d, rr(), 0.6, 0.2, 1000), -28, "amb_clear", "light breeze, fog lifted")

    # flash + camera whooshes on the place changes
    add(Cue(T.FLASH, "flash_whoosh", "reverse swell into the white flash", lambda r=rr(): (G.whoosh(1.0, r, 0.9, 250, 2400, 0.9, 0.15, 0.2), 0.9), -10, send=0.15))
    for f in (330, 529, 648, 1001, 1127, 1338, 1505, 1679):
        add(Cue(T.fr(f), "whoosh", "transition whoosh", lambda r=rr(): (G.whoosh(0.7, r, 0.3, 300, 1800, 0.9, 0.2, 0.12), 0.3), -16, send=0.1))
    # hook: boots shuffling in the sand, rifles rattling
    add(Cue(0.2, "shuffle", "boots shuffle on sand, kit rattle", lambda r=rr(): (boots_sand(4.5, r, 4.0), 0.0), -22, lpf=6000, send=0.1, cut=T.FLASH))
    # harbor: foghorn far off, ship engines
    add(Cue(T.fr(345), "foghorn", "distant ship horn through the fog", lambda r=rr(): (lp(foghorn(r), 600, 2), 0.0), -14, send=0.4))
    add(Cue(T.fr(336), "ship_rumble", "warships' engines idling in the harbor", lambda r=rr(): (ship_rumble(T.fr(504 - 336), r), 0.0), -20, kind="bed"))
    add(Cue(T.fr(425), "pier_steps", "boots on the wooden pier", lambda r=rr(): (boots_sand(2.6, r, 7.0), 0.0), -18, send=0.1))
    # bombing
    add(Cue(T.fr(532), "planes", "bombers passing low overhead", lambda r=rr(): (drone(4.0, r), 0.0), -8, send=0.1))
    for f in T.BOOMS:
        add(Cue(T.fr(f), "bomb_whistle", "falling bomb whistle", lambda r=rr(): (bomb_whistle(r), 0.9), -14, send=0.05))
        add(Cue(T.fr(f), "bomb_boom", "bomb hits the empty camp", lambda r=rr(): (explosion(r, 1.0), 0.0), -4, send=0.3))
    # landing
    add(Cue(T.fr(655), "ramp_clank", "landing-craft ramps slam down", lambda r=rr(): (G.hammer_hit(r, 1.0), 0.0), -12, send=0.2))
    add(Cue(T.fr(660), "charge_feet", "hundreds of boots splashing and running up the sand", lambda r=rr(): (boots_sand(5.0, r, 14.0), 0.0), -14, send=0.15))
    for k in range(6):
        add(Cue(T.fr(680) + k * 0.35, "hurrah", "charging soldiers shout", lambda r=rr(): (G.hurrah(r, r.uniform(100, 150), r.uniform(0.95, 1.1)), 0.0), -18, p=(k % 3 - 1) * 0.5, send=0.3))
    # the two shots in the fog
    add(Cue(T.SHOT_A, "gunshot", "first rifle shot in the fog", lambda r=rr(): (gunshot(r), 0.0), -2, send=0.45))
    add(Cue(T.SHOT_B, "gunshot", "the reply, from somewhere else in the fog", lambda r=rr(): (gunshot(r, 0.3), 0.0), -4, p=0.3, send=0.5))
    add(Cue(T.fr(926), "rifle_click", "rifle brought up, bolt", lambda r=rr(): (rifle_click(r), 0.0), -18))
    # night battle
    for (t, left) in T.night_shots():
        add(Cue(t, "night_shot", "night fire across the ridges", lambda r=rr(): (gunshot(r, 0.6), 0.0), -12, p=-0.6 if left else 0.6, send=0.5))
    # room
    add(Cue(T.fr(1345), "door_creak", "door creaks open", lambda r=rr(): (G.creak(1.0, r, 90, 160), 0.0), -18, send=0.2))
    add(Cue(T.fr(1394), "gasp", "kid gasps", lambda r=rr(): (G.whoa(r, 260, 0.35), 0.0), -16, send=0.1))
    for k in range(4):
        add(Cue(T.fr(1478) + k * 0.13, "rifle_click", "rifles cocked in the dark room", lambda r=rr(): (rifle_click(r), 0.0), -14, p=(k - 1.5) * 0.4))
    # booby trap, mine, toll
    add(Cue(T.TRAP, "trap_boom", "booby trap goes off", lambda r=rr(): (explosion(r, 0.7), 0.0), -4, send=0.35))
    for k in range(3):
        add(Cue(T.TRAP + 0.1 + k * 0.12, "oof", "soldiers thrown down", lambda r=rr(), kk=k: (G.oof(r, ["oof", "ugh", "oh"][kk]), 0.0), -18, p=(k - 1) * 0.4))
    add(Cue(T.MINE, "mine_boom", "destroyer hits a mine: deep underwater blast", lambda r=rr(): (explosion(r, 1.3), 0.0), -2, send=0.4))
    add(Cue(T.MINE + 0.2, "spout", "water column crashes back", lambda r=rr(): (G.splash_big(r), 0.0), -10, send=0.3))
    add(Cue(T.fr(1610), "groans", "wounded men on the beach", lambda r=rr(): (sum_groans(r), 0.0), -24, send=0.2))
    # dogs
    add(Cue(T.fr(1690), "search_steps", "soldiers creeping into the camp", lambda r=rr(): (boots_sand(2.0, r, 5.0), 0.0), -22))
    for tm, small, happy, p in [(T.fr(1813), False, False, 0.2), (T.fr(1823), True, True, 0.35), (T.fr(1830), False, True, -0.1)]:
        add(Cue(tm, "woof", "dog barks", lambda r=rr(), a=small, b=happy: (woof(r, a, b), 0.0), -12, p=p, send=0.15))
    add(Cue(T.fr(1838), "pant", "Explosion panting happily", lambda r=rr(): (pant(2.2, r), 0.0), -26))
    add(Cue(T.fr(1932), "arf", "Explosion's happy bark on the last word", lambda r=rr(): (woof(r, True, True), 0.0), -10, send=0.12))
    return C


def sum_groans(r):
    out = np.zeros(ns(2.5))
    for k in range(4):
        y = G.oof(r, ["ugh", "oh", "ow", "ugh"][k], base=r.uniform(90, 120))
        G._place_mono(out, y * r.uniform(0.4, 0.8), 0.2 + k * 0.5)
    return out


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
