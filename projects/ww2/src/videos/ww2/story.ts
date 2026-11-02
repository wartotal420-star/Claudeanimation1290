// WW2 long-form, part 1 (cold open + chapter 1 "The Bad Peace"): shots timed to ~/ww2/voice/words_part1.json
// (121.1 s incl. a 1.5 s chapter gap at 25.99 s). Cameras are written in each set's local coordinates (sets.ts origin
// added here). Camera grammar as the shorts: glides 18-40 f, cuts on big reframes, holds always creep, kicks on impacts.
import type { LightName } from "./lights";
import { SetName, setOrigin } from "./sets";
export type V3 = [number, number, number];
export const FPS = 30;
export const TOTAL = 3633;
export const W = 1920, H = 1080;

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

export type Light = LightName;
export type ShotDef = { id: number; a: number; b: number; set: SetName; night?: boolean; light: Light; fog?: [number, number]; sunAz?: number; sunEl?: number };
export const SHOTS: ShotDef[] = [
  { id: 1, a: 0, b: 140, set: "void", light: "void" },                                   // domino falls, the chain spreads
  { id: 2, a: 140, b: 212, set: "front", light: "dusk", fog: [40, 260] },                 // tanks: seventy million
  { id: 3, a: 212, b: 270, set: "front", light: "dusk", fog: [40, 300] },                 // flattened cities, bombers
  { id: 4, a: 270, b: 386, set: "front", light: "dusk", fog: [120, 1600] },               // ships, the far mushroom cloud
  { id: 5, a: 386, b: 504, set: "jungle", light: "day", fog: [6, 60], sunAz: 120, sunEl: 60 },                // the one soldier, 1974
  { id: 6, a: 504, b: 690, set: "warroom", light: "interior" },                           // title: the entire history
  { id: 7, a: 690, b: 779, set: "warroom", light: "interior" },                           // the war before it
  { id: 8, a: 779, b: 825, set: "warroom", light: "interior" },                           // CHAPTER 1 card
  { id: 9, a: 825, b: 1027, set: "paris", light: "interior", fog: [30, 120] },            // Paris 1919
  { id: 10, a: 1027, b: 1071, set: "paris", light: "interior", fog: [30, 120] },          // spoiler: nothing good
  { id: 11, a: 1071, b: 1290, set: "paris", light: "interior", fog: [30, 120] },          // fault, land, army, damage
  { id: 12, a: 1290, b: 1435, set: "paris", light: "interior", fog: [30, 120] },          // the bill... 2010
  { id: 13, a: 1435, b: 1672, set: "press", light: "interior" },                          // print more money
  { id: 14, a: 1672, b: 1815, set: "bakery", light: "interior" },                         // 200 billion marks
  { id: 15, a: 1815, b: 1930, set: "bakery", light: "interior" },                         // paid twice a day
  { id: 16, a: 1930, b: 2057, set: "playroom", light: "interior", sunAz: -50 },           // cash building blocks
  { id: 17, a: 2057, b: 2111, set: "street", night: true, light: "night", fog: [20, 120] }, // things calm down
  { id: 18, a: 2111, b: 2285, set: "wallst", light: "interior" },                         // the crash
  { id: 19, a: 2285, b: 2384, set: "street", light: "gloom" },                            // six million jobless
  { id: 20, a: 2384, b: 2547, set: "street", light: "gloom" },                            // listening to anyone sure
  { id: 21, a: 2547, b: 2707, set: "atelier", light: "interior", sunAz: -40 },            // the failed art student
  { id: 22, a: 2707, b: 2902, set: "beerhall", light: "interior" },                       // the back room of a beer hall
  { id: 23, a: 2902, b: 3182, set: "beerhall", light: "interior" },                       // running it, the crowds
  { id: 24, a: 3182, b: 3287, set: "street", night: true, light: "night", fog: [20, 160] }, // Chancellor, torches
  { id: 25, a: 3287, b: 3355, set: "street", light: "gloom" },                            // parties banned
  { id: 26, a: 3355, b: 3405, set: "press", light: "interior" },                          // newspapers controlled
  { id: 27, a: 3405, b: 3495, set: "street", light: "gloom" },                            // pushed out of public life
  { id: 28, a: 3495, b: TOTAL, set: "street", night: true, light: "night", fog: [20, 160] }, // one man's country
];
export const XFADE: Record<number, number> = { 2: 6, 5: 10, 6: 12, 9: 10, 13: 8, 14: 8, 16: 8, 17: 8, 18: 8, 19: 8, 21: 8, 22: 8, 24: 8, 28: 10 };
export const FLASH_AT = -100;
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};
/** on-screen title cards (React overlays in WW2.tsx) */
export const CARDS: { a: number; b: number; kind: "title" | "chapter"; lines: string[] }[] = [
  { a: 506, b: 676, kind: "title", lines: ["THE ENTIRE HISTORY OF", "WORLD WAR II"] },
  { a: 779, b: 825, kind: "chapter", lines: ["CHAPTER 1", "THE BAD PEACE", "1919 – 1933"] },
];

// ---------------- camera ----------------
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
type Shot = Partial<Cam> & { pos: V3; look: V3 };
type Key = { f: number; dur?: number; cut?: boolean; s: (f: number) => Shot };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
const mixC = (a: Cam, b: Cam, k: number): Cam => ({
  pos: a.pos.map((v, i) => v + (b.pos[i] - v) * k) as V3, look: a.look.map((v, i) => v + (b.look[i] - v) * k) as V3,
  fov: a.fov + (b.fov - a.fov) * k, roll: a.roll + (b.roll - a.roll) * k,
});
const full = (c: Shot): Cam => ({ fov: 40, roll: 0, ...c });
const run = (keys: Key[], f: number) => {
  let cur = full(keys[0].s(f));
  for (let i = 1; i < keys.length; i++) {
    const k = keys[i];
    if (f < k.f) break;
    cur = k.cut ? full(k.s(f)) : mixC(cur, full(k.s(f)), glide((f - k.f) / (k.dur ?? 24)));
  }
  return cur;
};
const pushK = (f: number, f0: number, rate: number, punch = 0, n = 35) => {
  const x = Math.max(0, f - f0);
  let s = rate * x;
  if (punch > rate) for (let i = 0; i < Math.min(x, n); i++) s += (punch - rate) * Math.max(0, Math.min(1, (i + 0.5) / 8, (n - i - 0.5) / 8));
  return Math.exp(-s);
};
/** dolly push in set-local coordinates */
const D = (set: SetName, pos: V3, look: V3, f: number, f0: number, rate = 0.0025, rest: Partial<Cam> = {}, punch = 0) => {
  const o = setOrigin(set), k = pushK(f, f0, rate, punch);
  return { pos: [o[0] + look[0] + (pos[0] - look[0]) * k, o[1] + look[1] + (pos[1] - look[1]) * k, o[2] + look[2] + (pos[2] - look[2]) * k] as V3,
    look: [o[0] + look[0], o[1] + look[1], o[2] + look[2]] as V3, ...rest };
};
/** pan/track: camera and target both slide by (dx, dz) per frame */
const Tr = (set: SetName, pos: V3, look: V3, f: number, f0: number, v: V3, rest: Partial<Cam> = {}) => {
  const o = setOrigin(set), t = f - f0;
  return { pos: [o[0] + pos[0] + v[0] * t, o[1] + pos[1] + v[1] * t, o[2] + pos[2] + v[2] * t] as V3, look: [o[0] + look[0] + v[0] * t, o[1] + look[1] + v[1] * t, o[2] + look[2] + v[2] * t] as V3, ...rest };
};
export const DOM0: V3 = [0.47, 0.02, 1.49];
const CAMS: Record<number, Key[]> = {
  1: [
    { f: 0, s: (f) => D("void", [DOM0[0] - 0.25, 0.32, DOM0[2] - 0.62], [DOM0[0], 0.26, DOM0[2]], f, 0, 0.003, { fov: 30, roll: 0.03 }) },
    { f: 92, dur: 40, s: (f) => D("void", [0.6, 3.6, -3.4], [0.2, 0, 0.6], f, 92, 0.002, { fov: 44 }) },
  ],
  2: [{ f: 137, s: (f) => Tr("front", [2, 0.9, -2], [-3, 1.6, 14], f, 137, [0, 0, 0.05], { fov: 42, roll: -0.03 }) }],
  3: [{ f: 212, s: (f) => D("front", [-4, 2.5, 46], [2, 9, 74], f, 212, 0.003, { fov: 46 }) }],
  4: [
    { f: 270, s: (f) => D("front", [52, 3, 10], [130, 4, 90], f, 270, 0.0015, { fov: 40 }) },
    { f: 300, dur: 40, s: (f) => D("front", [56, 2.2, 6], [210, 40, 330], f, 300, 0.0012, { fov: 36 }) },
  ],
  5: [
    { f: 381, s: (f) => D("jungle", [1.4, 1.7, -1.5], [0, 1.4, 4], f, 381, 0.002, { fov: 42 }) },
    { f: 440, dur: 34, s: (f) => D("jungle", [0.35, 1.6, 2.3], [0, 1.55, 4], f, 440, 0.0025, { fov: 34 }) },
  ],
  6: [
    { f: 498, s: (f) => D("warroom", [0, 3.2, -1.6], [0, 0.95, 1.1], f, 498, 0.0016, { fov: 46 }) },
    { f: 600, dur: 40, s: (f) => Tr("warroom", [-1.4, 1.3, 0.1], [0.4, 0.96, 1.3], f, 600, [0.004, 0, 0.002], { fov: 40, roll: 0.03 }) },
  ],
  7: [{ f: 690, s: (f) => D("warroom", [0.55, 1.28, 1.05], [1.2, 1.0, 1.7], f, 690, 0.004, { fov: 32 }) }],
  8: [{ f: 779, s: (f) => D("warroom", [0, 2.4, -0.6], [0, 0.95, 1.2], f, 779, 0.002, { fov: 44 }) }],
  9: [
    { f: 820, s: (f) => D("paris", [0, 4.6, -5.2], [0, 1.6, 9], f, 820, 0.0018, { fov: 46 }) },
    { f: 900, dur: 30, s: (f) => D("paris", [0.5, 1.7, 7.4], [0, 1.75, 11], f, 900, 0.0022, { fov: 40 }) },
    { f: 985, dur: 34, s: (f) => D("paris", [4.4, 1.6, -4.6], [6.35, 1.25, -2.3], f, 985, 0.003, { fov: 36, roll: -0.03 }) },
  ],
  10: [{ f: 1027, s: (f) => D("paris", [5.95, 1.32, -3.25], [6.35, 1.28, -2.3], f, 1027, 0.004, { fov: 30, roll: 0.04 }, 0.008) }],
  11: [
    { f: 1071, s: (f) => D("paris", [2.4, 1.7, -0.9], [0, 1.15, 2.4], f, 1071, 0.002, { fov: 42 }) },
    { f: 1140, cut: true, s: (f) => D("paris", [0.5, 1.45, 1.35], [0, 0.82, 2.75], f, 1140, 0.002, { fov: 40 }) },
    { f: 1250, cut: true, s: (f) => D("paris", [-1.8, 1.6, 0.1], [0, 1.3, 2.0], f, 1250, 0.003, { fov: 40 }) },
  ],
  12: [
    { f: 1290, s: (f) => D("paris", [0.9, 0.45, -5.0], [0, 0.25, 1.5], f, 1290, 0.0015, { fov: 46, roll: 0.03 }) },
    { f: 1395, dur: 18, s: (f) => D("paris", [0.25, 1.3, -4.4], [0.05, 0.02, -2.6], f, 1395, 0.002, { fov: 40 }) },
  ],
  13: [
    { f: 1430, s: (f) => D("press", [-3.6, 1.8, -2.6], [-0.4, 1.3, 2.6], f, 1430, 0.002, { fov: 44 }) },
    { f: 1580, dur: 26, s: (f) => D("press", [-1.2, 1.5, -1.4], [-0.4, 1.4, 2.6], f, 1580, 0.003, { fov: 40, roll: 0.03 }) },
    { f: 1636, dur: 30, s: (f) => D("press", [-3.4, 0.9, -0.9], [-2.1, 0.5, 0.6], f, 1636, 0.004, { fov: 40, roll: -0.04 }) },
  ],
  14: [
    { f: 1668, s: (f) => D("bakery", [0.4, 1.5, -2.2], [0, 1.4, 1.8], f, 1668, 0.002, { fov: 44 }) },
    { f: 1755, dur: 24, s: (f) => D("bakery", [-0.6, 1.62, 0.5], [-0.6, 1.62, 1.7], f, 1755, 0.003, { fov: 36 }, 0.007) },
  ],
  15: [{ f: 1815, s: (f) => D("bakery", [-1.4, 1.55, -3.0], [-0.7, 1.3, 1.6], f, 1815, 0.0025, { fov: 46, roll: 0.03 }) }],
  16: [
    { f: 1926, s: (f) => D("playroom", [0.25, 0.8, -1.6], [0.05, 0.6, 0.8], f, 1926, 0.0025, { fov: 42 }) },
    { f: 2030, dur: 20, s: (f) => D("playroom", [0.3, 0.6, -0.9], [0.05, 0.4, 0.7], f, 2030, 0.002, { fov: 44, roll: 0.05 }) },
  ],
  17: [{ f: 2053, s: (f) => Tr("street", [1.0, 1.65, -1.2], [-1.0, 1.4, 4.5], f, 2053, [0, 0, 0.02], { fov: 44 }) }],
  18: [
    { f: 2107, s: (f) => D("wallst", [0.5, 1.75, -2.8], [0, 2.4, 6.6], f, 2107, 0.002, { fov: 46 }) },
    { f: 2226, cut: true, s: (f) => D("wallst", [1.95, 1.55, -0.2], [1.5, 1.35, 1.4], f, 2226, 0.003, { fov: 36, roll: -0.03 }) },
  ],
  19: [{ f: 2281, s: (f) => D("street", [2.4, 1.75, 7.5], [7.3, 1.4, 20], f, 2281, 0.002, { fov: 42 }) }],
  20: [
    { f: 2384, s: (f) => D("street", [0.4, 2.2, 21], [0, 2.1, 35], f, 2384, 0.0015, { fov: 42 }) },
    { f: 2465, dur: 40, s: (f) => D("street", [0.2, 1.9, 30.2], [0, 2.3, 34.4], f, 2465, 0.003, { fov: 38 }) },
  ],
  21: [{ f: 2543, s: (f) => D("atelier", [0.7, 1.6, -2.3], [0.15, 1.35, 0.7], f, 2543, 0.0022, { fov: 42 }) }],
  22: [
    { f: 2703, s: (f) => D("beerhall", [3.2, 1.8, 2.2], [-0.5, 1.6, 7.5], f, 2703, 0.002, { fov: 44 }) },
    { f: 2850, dur: 26, s: (f) => D("beerhall", [1.2, 1.7, 6.2], [0, 1.9, 10.4], f, 2850, 0.003, { fov: 40, roll: 0.03 }) },
  ],
  23: [
    { f: 2898, s: (f) => D("beerhall", [0, 3.4, -3.5], [0, 2, 10], f, 2898, 0.0015, { fov: 46 }) },
    { f: 3115, cut: true, s: (f) => D("beerhall", [0.45, 1.25, 8.5], [0, 2.3, 10.6], f, 3115, 0.003, { fov: 36, roll: -0.04 }, 0.007) },
  ],
  24: [{ f: 3178, s: (f) => D("street", [1.2, 1.7, 33], [0, 6.6, 45], f, 3178, 0.002, { fov: 36 }) }],
  25: [{ f: 3287, s: (f) => D("street", [3.6, 1.5, 26], [6.1, 1.5, 26], f, 3287, 0.004, { fov: 36 }) }],
  26: [{ f: 3355, s: (f) => D("press", [3.4, 1.55, 0.9], [3.8, 0.95, 2.0], f, 3355, 0.004, { fov: 38 }) }],
  27: [{ f: 3405, s: (f) => D("street", [-5.2, 1.5, 15.2], [-7.3, 1.15, 20.4], f, 3405, 0.0015, { fov: 42 }) }],
  28: [{ f: 3491, s: (f) => D("street", [0, 1.4, 25], [0, 8, 46], f, 3491, -0.0012, { fov: 46 }) }],
};

const KICKS: [number, number][] = [[53 / 30, 0.4], [1410 / 30, 1.2], [2166 / 30, 0.9], [2627 / 30, 0.7], [2678 / 30, 0.7], [3312 / 30, 0.5]];
export const kickAt = (t: number) => {
  let a = 0;
  for (const [t0, g] of KICKS) {
    const n = Math.floor((t - t0) * FPS + 1e-6);
    if (n >= 0 && n < 7) a += g * (n % 2 ? -1 : 1) * (1 - n / 7) ** 1.5;
  }
  return a;
};
export const camAt = (id: number, f: number): Cam => {
  const c = run(CAMS[id], f), a = kickAt(f / FPS);
  if (!a) return c;
  const d: V3 = [c.look[0] - c.pos[0], c.look[1] - c.pos[1], c.look[2] - c.pos[2]];
  const L = Math.hypot(...d), h = Math.hypot(d[0], d[2]) || 1;
  const m = (3 / 640) * Math.tan((c.fov * Math.PI) / 360) * L * a;
  return { ...c, look: [c.look[0] - (d[2] / h) * m, c.look[1] + 0.6 * m, c.look[2] + (d[0] / h) * m], roll: c.roll + a * 0.004 };
};

// ---------------- lens ----------------
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
export const DOF: Dof[] = [
  { f: 0, cInf: 16 }, { f: 92, dur: 40, cInf: 4 }, { f: 140, cInf: 6 }, { f: 212, cInf: 0 }, { f: 270, cInf: 0 },
  { f: 386, cInf: 10 }, { f: 440, dur: 34, cInf: 14 }, { f: 504, cInf: 5 }, { f: 600, cInf: 9 }, { f: 690, cInf: 14 }, { f: 779, cInf: 18 },
  { f: 825, cInf: 4 }, { f: 900, cInf: 10 }, { f: 985, cInf: 12 }, { f: 1027, cInf: 16 }, { f: 1071, cInf: 9 }, { f: 1140, cInf: 12 },
  { f: 1250, cInf: 10 }, { f: 1290, cInf: 8 }, { f: 1395, dur: 18, cInf: 12 }, { f: 1435, cInf: 7 }, { f: 1636, cInf: 12 },
  { f: 1672, cInf: 8 }, { f: 1755, cInf: 14 }, { f: 1815, cInf: 8 }, { f: 1930, cInf: 11 }, { f: 2057, cInf: 6 }, { f: 2111, cInf: 6 },
  { f: 2226, cInf: 13 }, { f: 2285, cInf: 7 }, { f: 2384, cInf: 6 }, { f: 2465, dur: 40, cInf: 10 }, { f: 2547, cInf: 9 },
  { f: 2707, cInf: 8 }, { f: 2850, dur: 26, cInf: 11 }, { f: 2902, cInf: 4 }, { f: 3115, cInf: 13 }, { f: 3182, cInf: 6 },
  { f: 3287, cInf: 13 }, { f: 3355, cInf: 13 }, { f: 3405, cInf: 8 }, { f: 3495, cInf: 4 },
];
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
