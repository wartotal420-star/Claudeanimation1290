// Timeline of "The Island That Was Already Empty" (Kiska, 1943): shots timed to the voice words
// (~/kiska-short/voice/words.json, 64.4 s), cameras, lens blur and impact kicks. Camera grammar as the bridge short:
// smootherstep glides 18-40 f, cuts on big reframes, every hold creeps in, flip-sign kicks on impacts.
import { H, shoreZ, CAMP, V3 } from "./island";
import type { LightName } from "./lights";
export type { V3 };
export const FPS = 30;
export const TOTAL = 1940;

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;
/** ground point (x, ground + dy, z) */
export const P = (x: number, z: number, dy = 0): V3 => [x, H(x, z) + dy, z];

// ---------------- places ----------------
export const FIELD: [number, number] = [40, -20];          // fog field above the landing beach (hook, crowd)
export const BEACH_X = 50;
export const BZ = shoreZ(BEACH_X);                          // waterline at the landing beach
export const P7: [number, number] = [70, -18];             // boots in the fog
export const P8a: [number, number] = [61.2, -10];          // first shooter (US)
export const P8b: [number, number] = [74.4, -8];           // second shooter (Canadian)
export const P12: [number, number] = [66, -5];             // squinting soldier / shapes in the fog
export const ROOM: V3 = [3000, 0, 3000];                   // the dark room (far away from the island)
export const USS: V3 = [480, 0, -420];                     // US destroyer (lookout, mine)
export const PIER_X = -115;
export const PIER_END = -84;
export const LANE_X = -114;                                 // open lane through the camp (dogs at its end)
export const DOGS_Z = 11;
export const WOUNDED_X = 130;

// ---------------- shots ----------------
export type Light = LightName;
export type ShotDef = { id: number; a: number; b: number; light: Light; fog?: [number, number]; sunAz?: number; sunEl?: number };
export const SHOTS: ShotDef[] = [
  { id: 1, a: 0, b: 162, light: "fog", fog: [3, 70] },        // hook: soldiers on the fog beach, no enemy
  { id: 2, a: 162, b: 336, light: "grey", fog: [80, 2200] },                    // 1943, Kiska, freezing rock, over a year
  { id: 3, a: 336, b: 504, light: "fog", fog: [8, 170] },      // ships sneak in, everyone boards
  { id: 4, a: 504, b: 532, light: "fog", fog: [2, 40] },       // nobody notices
  { id: 5, a: 532, b: 651, light: "grey" },                    // two weeks of bombing the empty island
  { id: 6, a: 651, b: 810, light: "fog", fog: [12, 160] },       // 35,000 storm the beaches
  { id: 7, a: 810, b: 895, light: "fog" },                     // can't see their own boots
  { id: 8, a: 895, b: 1005, light: "fog" },                    // opens fire / fires back
  { id: 9, a: 1005, b: 1131, light: "night" },                 // all night, both on the same side
  { id: 10, a: 1131, b: 1182, light: "grey", fog: [20, 260] }, // luckily the enemy wasn't there
  { id: 11, a: 1182, b: 1247, light: "fog", fog: [3, 60] },    // unluckily everybody else was
  { id: 12, a: 1247, b: 1343, light: "fog" },                  // your brain fills in the blanks
  { id: 13, a: 1343, b: 1446, light: "night", fog: [10, 120] },// dark room, coat on the door
  { id: 14, a: 1446, b: 1508, light: "night", fog: [10, 120] },// now give everyone a rifle
  { id: 15, a: 1508, b: 1685, light: "grey", fog: [18, 300] }, // fog, booby traps, the mine, 300 casualties
  { id: 16, a: 1685, b: 1838, light: "day", fog: [40, 520] },  // searched the island: a few dogs
  { id: 17, a: 1838, b: TOTAL, light: "day", fog: [40, 520] }, // Explosion used to be American
];
export const XFADE: Record<number, number> = { 3: 8, 5: 6, 9: 8, 10: 8, 13: 10, 15: 6, 16: 12 };
export const FLASH_AT = 162;
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};

// ---------------- camera ----------------
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
type Shot = Partial<Cam> & { pos: V3; look: V3 };
type Key = { f: number; dur?: number; cut?: boolean; s: (f: number) => Shot };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
const mix = (a: Cam, b: Cam, k: number): Cam => ({
  pos: a.pos.map((v, i) => v + (b.pos[i] - v) * k) as V3, look: a.look.map((v, i) => v + (b.look[i] - v) * k) as V3,
  fov: a.fov + (b.fov - a.fov) * k, roll: a.roll + (b.roll - a.roll) * k,
});
const full = (c: Shot): Cam => ({ fov: 40, roll: 0, ...c });
const run = (keys: Key[], f: number) => {
  let cur = full(keys[0].s(f));
  for (let i = 1; i < keys.length; i++) {
    const k = keys[i];
    if (f < k.f) break;
    cur = k.cut ? full(k.s(f)) : mix(cur, full(k.s(f)), glide((f - k.f) / (k.dur ?? 24)));
  }
  return cur;
};
const T = (f: number) => f / FPS;
const pushK = (f: number, f0: number, rate: number, punch = 0, n = 35) => {
  const x = Math.max(0, f - f0);
  let s = rate * x;
  if (punch > rate) for (let i = 0; i < Math.min(x, n); i++) s += (punch - rate) * Math.max(0, Math.min(1, (i + 0.5) / 8, (n - i - 0.5) / 8));
  return Math.exp(-s);
};
const dolly = (pos: V3, look: V3, k: number, rest: Partial<Cam> = {}): Shot =>
  ({ pos: [look[0] + (pos[0] - look[0]) * k, look[1] + (pos[1] - look[1]) * k, look[2] + (pos[2] - look[2]) * k], look, ...rest });
const zoom = (pos: V3, look: V3, fov: number, k: number, rest: Partial<Cam> = {}): Shot =>
  ({ pos, look, fov: (360 / Math.PI) * Math.atan(Math.tan((fov * Math.PI) / 360) * k), ...rest });
const add = (a: V3, d: V3): V3 => [a[0] + d[0], a[1] + d[1], a[2] + d[2]];

const [FX, FZ] = FIELD;
const R = ROOM;
const CAMS: Record<number, Key[]> = {
  1: [
    { f: 0, s: (f) => dolly(P(FX + 4, FZ - 16, 1.5), P(FX, FZ - 2, 1.3), pushK(f, 0, 0.0025), { fov: 42, roll: -0.03 }) },
    { f: 117, cut: true, s: (f) => dolly(P(FX + 0.4, FZ - 7.4, 1.62), P(FX + 0.1, FZ - 3.6, 1.55), pushK(f, 117, 0.003, 0.006, 30), { fov: 36, roll: 0.035 }) },
  ],
  2: [
    { f: 160, s: (f) => zoom([-330, 70, -360], [-80, 30, 120], 44, pushK(f, 160, 0.0018)) },
    { f: 244, cut: true, s: (f) => dolly(P(CAMP[0] + 3, CAMP[2] - 12, 1.7), P(CAMP[0], CAMP[2] - 4, 1.4), pushK(f, 244, 0.0028, 0.006, 30), { fov: 40 }) },
  ],
  3: [
    { f: 330, s: (f) => zoom([PIER_X + 7, 4.8, PIER_END + 18], [PIER_X - 12, 7, -165], 40, pushK(f, 330, 0.002)) },
    { f: 425, cut: true, s: (f) => dolly([PIER_X + 9, 2.6, -62], [PIER_X, 2.0, -64], pushK(f, 425, 0.0025), { fov: 40 }) },
  ],
  4: [{ f: 504, s: (f) => dolly([USS[0] + 17, 5.75, USS[2] + 9.6], [USS[0] + 17, 5.55, USS[2] + 4.5], pushK(f, 504, 0.005), { fov: 36 }) }],
  5: [
    { f: 529, s: (f) => zoom(P(CAMP[0] - 6, CAMP[2] - 18, 1.4), [CAMP[0] - 3, 48, CAMP[2] + 30], 50, pushK(f, 529, 0.0015), { roll: 0.05 }) },
    { f: 594, cut: true, s: (f) => zoom(P(CAMP[0] + 38, CAMP[2] - 34, 16), P(CAMP[0], CAMP[2] + 14, 1), 42, pushK(f, 594, 0.002)) },
  ],
  6: [
    { f: 648, s: (f) => dolly(P(BEACH_X + 2.5, BZ + 12, 0.9), P(BEACH_X, BZ - 1, 1.8), pushK(f, 648, 0.0025), { fov: 46, roll: -0.03 }) },
    { f: 763, cut: true, s: (f) => dolly(P(BEACH_X + 0.6, BZ + 14.6, 0.95), P(BEACH_X, BZ + 11.5, 1.75), pushK(f, 763, 0.003, 0.006, 30), { fov: 38, roll: 0.04 }) },
  ],
  7: [
    { f: 810, s: (f) => dolly(P(P7[0] + 0.3, P7[1] - 2.3, 1.75), P(P7[0], P7[1], 1.68), pushK(f, 810, 0.0025), { fov: 34 }) },
    { f: 855, dur: 26, s: (f) => dolly(P(P7[0] + 0.25, P7[1] - 2.0, 1.15), P(P7[0], P7[1], 0.15), pushK(f, 855, 0.002), { fov: 40, roll: 0.04 }) },
  ],
  8: [
    { f: 895, s: (f) => dolly(P(P8a[0] - 0.4, P8a[1] - 4.3, 1.6), P(P8a[0] - 0.4, P8a[1], 1.4), pushK(f, 895, 0.0025, 0.006, 30), { fov: 38 }) },
    { f: 955, cut: true, s: (f) => dolly(P(P8b[0] + 0.4, P8b[1] - 4.2, 1.6), P(P8b[0] + 0.4, P8b[1], 1.4), pushK(f, 955, 0.0025), { fov: 38, roll: -0.04 }) },
  ],
  9: [
    { f: 1001, s: (f) => dolly(P(57, 5, 5.5), P(57, 25, 1.2), pushK(f, 1001, 0.0018), { fov: 50 }) },
    { f: 1075, cut: true, s: (f) => dolly(P(57, 24.2, 1.5), P(57, 30, 1.25), pushK(f, 1075, 0.0025, 0.007, 30), { fov: 44 }) },
  ],
  10: [{ f: 1127, s: (f) => dolly(P(LANE_X + 1.5, -8, 1.7), P(LANE_X - 0.5, 16, 1.9), pushK(f, 1127, 0.004), { fov: 42 }) }],
  11: [{ f: 1178, s: (f) => dolly(P(FX + 1, FZ - 12, 2.4), P(FX, FZ - 1, 1.3), pushK(f, 1178, 0.003, 0.006, 30), { fov: 42, roll: 0.03 }) }],
  12: [
    { f: 1247, s: (f) => dolly(P(P12[0] + 0.25, P12[1] - 2.0, 1.78), P(P12[0], P12[1], 1.72), pushK(f, 1247, 0.003), { fov: 32 }) },
    { f: 1296, cut: true, s: (f) => dolly(P(P12[0], P12[1] - 0.6, 1.6), P(P12[0], P12[1] + 22, 1.8), pushK(f, 1296, 0.004), { fov: 44 }) },
  ],
  13: [
    { f: 1338, s: (f) => dolly(add(R, [2.2, 1.45, 1.4]), add(R, [-3, 1.15, -1.2]), pushK(f, 1338, 0.0025), { fov: 42 }) },
    { f: 1394, cut: true, s: (f) => dolly(add(R, [-2.2, 1.2, -0.6]), add(R, [1.4, 1.35, 2.9]), pushK(f, 1394, 0.002, 0.007, 30), { fov: 40, roll: -0.04 }) },
  ],
  14: [{ f: 1446, s: (f) => dolly(add(R, [2.6, 2.1, -2.6]), add(R, [-0.2, 1.1, 0.9]), pushK(f, 1446, 0.003), { fov: 50, roll: 0.04 }) }],
  15: [
    { f: 1505, s: (f) => dolly(P(56, -13, 1.8), P(55, -4, 1.2), pushK(f, 1505, 0.0025), { fov: 42 }) },
    { f: 1556, cut: true, s: (f) => zoom([USS[0] - 70, 9, USS[2] + 60], [USS[0], 5, USS[2]], 38, pushK(f, 1556, 0.002)) },
    { f: 1606, cut: true, s: (f) => dolly(P(WOUNDED_X + 2.5, shoreZ(WOUNDED_X) + 11, 1.5), P(WOUNDED_X, shoreZ(WOUNDED_X) + 16, 0.9), pushK(f, 1606, 0.0016), { fov: 40 }) },
  ],
  16: [
    { f: 1679, s: (f) => dolly(P(LANE_X + 1, 19, 1.5), P(LANE_X, 6, 1.35), pushK(f, 1679, 0.0025), { fov: 42 }) },
    { f: 1748, cut: true, s: (f) => dolly(P(LANE_X + 11, DOGS_Z + 1.9, 1.4), P(LANE_X - 1, DOGS_Z + 1.9, 0.95), pushK(f, 1748, 0.0022, 0.006, 32), { fov: 44 }) },
  ],
  17: [{ f: 1838, s: (f) => dolly(P(LANE_X + 1.45, DOGS_Z - 0.15, 0.72), P(LANE_X - 0.1, DOGS_Z, 0.55), pushK(f, 1838, 0.003, 0.006, 30), { fov: 36 }) }],
};

// impact kicks: image offset flips sign every frame, decays over 7 f
const KICKS: [number, number][] = [[940 / 30, 0.6], [985 / 30, 0.6], [602 / 30, 0.9], [614 / 30, 0.9], [627 / 30, 1.1], [640 / 30, 0.8],
  [1546 / 30, 1.2], [1589 / 30, 1.5]];
export const kickAt = (t: number) => {
  let a = 0;
  for (const [t0, g] of KICKS) {
    const n = Math.floor((t - t0) * FPS + 1e-6);
    if (n >= 0 && n < 7) a += g * (n % 2 ? -1 : 1) * (1 - n / 7) ** 1.5;
  }
  return a;
};
export const camAt = (id: number, f: number): Cam => {
  const c = run(CAMS[id], f), a = kickAt(T(f));
  if (!a) return c;
  const d: V3 = [c.look[0] - c.pos[0], c.look[1] - c.pos[1], c.look[2] - c.pos[2]];
  const L = Math.hypot(...d), h = Math.hypot(d[0], d[2]) || 1;
  const m = (3 / 640) * Math.tan((c.fov * Math.PI) / 360) * L * a;
  return { ...c, look: [c.look[0] - (d[2] / h) * m, c.look[1] + 0.6 * m, c.look[2] + (d[0] / h) * m], roll: c.roll + a * 0.004 };
};

// ---------------- lens ----------------
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
export const DOF: Dof[] = [
  { f: 0, cInf: 8, focus: () => P(FX, FZ - 3.6, 1.5) },
  { f: 117, cInf: 13, focus: () => P(FX, FZ - 3.6, 1.55) },
  { f: 162, cInf: 0 },
  { f: 244, cInf: 9, focus: () => P(CAMP[0], CAMP[2] - 4, 1.5) },
  { f: 336, cInf: 0 },
  { f: 425, cInf: 7 },
  { f: 504, cInf: 14 },
  { f: 532, cInf: 0 },
  { f: 651, cInf: 6, focus: () => P(BEACH_X, BZ + 7, 1.4) },
  { f: 763, cInf: 13, focus: () => P(BEACH_X, BZ + 11.5, 1.75) },
  { f: 810, cInf: 12 },
  { f: 855, dur: 26, cInf: 10 },
  { f: 895, cInf: 9 },
  { f: 1005, cInf: 0 },
  { f: 1075, cInf: 9 },
  { f: 1131, cInf: 5 },
  { f: 1182, cInf: 6, focus: () => P(FX, FZ - 3, 1.5) },
  { f: 1247, cInf: 15 },
  { f: 1296, cInf: 0 },
  { f: 1343, cInf: 8 },
  { f: 1394, cInf: 10 },
  { f: 1446, cInf: 5 },
  { f: 1508, cInf: 6 },
  { f: 1556, cInf: 0 },
  { f: 1606, cInf: 8 },
  { f: 1685, cInf: 7 },
  { f: 1748, cInf: 7, focus: () => P(LANE_X - 0.5, DOGS_Z + 1, 0.6) },
  { f: 1838, cInf: 14, focus: () => P(LANE_X, DOGS_Z, 0.55) },
];
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
