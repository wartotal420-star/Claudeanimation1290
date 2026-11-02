// Chapter 9: The Turn (1942-1943). Voice ~/ww2/voice/ch09.wav (169.88 s, 5096 frames), word frames from ch09_words.json.
// Sets (layouts and anchors at the top of each ~/ww2/blender/sets/<set>.py): c09_map (map room, Europe map table),
// c09_desert (El Alamein night barrage, Rommel's panzers, the Tunisian surrender camp by day), c09_stalingrad (street,
// station square, skyline, the pocket, the steppe road, a gutted flat, a stairwell), c09_cellar (Paulus' Univermag
// basement), c09_sea (convoy, U-boats, escorts), c09_bletchley (Hut 6, the Bombe, an Enigma), c09_kursk (trenches,
// minefields, the tank wave), c09_italy (Sicily beach, Villa Savoia, the mountain), c09_kiska (fog island, the dog).
import { makeChapter } from "../chapter";
import type { ChShot } from "../chapter";
import { D, Tr, smooth, clamp01 } from "../story";
import type { Key, Dof, V3 } from "../story";
import { P, F, W_, act, talk, hh, q, mist, stamp, at } from "../cast";
import type { Ctx, Beat } from "../cast";
import { HITLER_WAR, STALIN_COAT, ROMMEL, MONTGOMERY, EISENHOWER, PAULUS, MUSSOLINI, officer, winter, soviet, german, italian, tommy, gi, codebreaker } from "../cast";
import { fxBurst, fxBoom, fxSplash, fxBomber, dogSit, INK } from "../toon";
import type { Outfit, Expr, FrontOpts, Pen } from "../toon";

const TOTAL = 5096;
// ---------------- cast for this chapter ----------------
type Who3 = [Outfit, string];
const KING: Who3 = [{ ...officer("it", 9)[0], build: "short", moustache: "#f2f2f2", stache: "walrus", brows: "#e8e8e8", bushy: true, nose: "big", skin: "#f5d6bc" }, "kingVE"];
const coldGerman = (i: number): Who3 => { const [o, k] = german(i); return [{ ...o, haggard: true, stubble: true, scarf: ["#6a5a46", "#4a4e46", "#7a6a5a"][i % 3], coat: o.coat ?? "#5a6054" }, `cg${k}`]; };
const pow = (i: number): Who3 => { const [o, k] = i % 4 === 3 ? italian(i) : german(i); return [{ ...o, haggard: true, stubble: true, rifle: false, smg: undefined, scarf: ["#6a5a46", "#4a4e46", "#7a6a5a", "#5a4a40"][i % 4], coat: i % 4 === 3 ? undefined : "#5a6054" }, `pw${k}`]; };
const surr = (i: number): Who3 => { const [o, k] = i % 2 ? italian(i) : german(i); return [{ ...o, rifle: false, smg: undefined, haggard: i % 3 === 0 }, `su${k}`]; };

// ---------------- shots ----------------
const S = (id: number, a: number, b: number, set: string, light: ChShot["light"], night = false): ChShot => ({ id, a, b, set, light, night });
const MP = "c09_map", DS = "c09_desert", ST = "c09_stalingrad", CE = "c09_cellar", SE = "c09_sea", BL = "c09_bletchley", KU = "c09_kursk", IT = "c09_italy", KI = "c09_kiska";
const SHOTS: ChShot[] = [
  S(1, 0, 204, MP, "interior"), S(2, 204, 293, MP, "interior"), S(3, 293, 392, DS, "night", true), S(4, 392, 452, DS, "night", true), S(5, 452, 600, MP, "interior"),
  S(6, 600, 670, DS, "golden"), S(7, 670, 788, DS, "golden"), S(8, 788, 900, ST, "dusk"), S(9, 900, 940, ST, "dusk"), S(10, 940, 1088, MP, "interior"),
  S(11, 1088, 1184, MP, "interior"), S(12, 1184, 1290, ST, "dusk"), S(13, 1290, 1330, ST, "dusk"), S(14, 1330, 1407, ST, "dusk"), S(15, 1407, 1518, ST, "dusk"),
  S(16, 1518, 1752, MP, "interior"), S(17, 1752, 1830, MP, "interior"), S(18, 1830, 2022, ST, "dusk"), S(19, 2022, 2084, MP, "interior"), S(20, 2084, 2128, MP, "interior"),
  S(21, 2128, 2262, ST, "dusk"), S(22, 2262, 2436, CE, "interior"), S(23, 2436, 2478, CE, "interior"), S(24, 2478, 2645, CE, "interior"), S(25, 2645, 2715, ST, "dusk"),
  S(26, 2715, 2817, ST, "dusk"), S(27, 2817, 2907, ST, "dusk"), S(28, 2907, 3010, SE, "grey"), S(29, 3010, 3102, SE, "grey"), S(30, 3102, 3276, BL, "interior"),
  S(31, 3276, 3434, SE, "grey"), S(32, 3434, 3510, BL, "interior"), S(33, 3510, 3567, SE, "grey"), S(34, 3567, 3747, KU, "golden"), S(35, 3747, 3849, KU, "golden"),
  S(36, 3849, 4020, KU, "golden"), S(37, 4020, 4074, KU, "golden"), S(38, 4074, 4152, KU, "golden"), S(39, 4152, 4266, IT, "day"), S(40, 4266, 4428, IT, "day"),
  S(41, 4428, 4480, IT, "day"), S(42, 4480, 4734, IT, "day"), S(43, 4734, 4948, KI, "fog"), S(44, 4948, 5012, KI, "fog"), S(45, 5012, TOTAL, KI, "fog"),
];
const XFADE: Record<number, number> = { 3: 8, 8: 12, 22: 10, 26: 10, 27: 14, 28: 10, 30: 8, 34: 10, 39: 10, 42: 10, 43: 12 };

// ---------------- cameras ----------------
type T3 = [number, number, number];
const k1 = (f0: number, set: string, pos: T3, look: T3, fov = 42, rate = 0.002, roll = 0, punch = 0): Key => ({ f: f0, s: (f) => D(set, pos, look, f, f0, rate, { fov, roll }, punch) });
const tr = (f0: number, set: string, pos: T3, look: T3, v: T3, fov = 44, roll = 0): Key => ({ f: f0, s: (f) => Tr(set, pos, look, f, f0, v, { fov, roll }) });
const cut = (k: Key): Key => ({ ...k, cut: true });
const glideTo = (k: Key, dur: number): Key => ({ ...k, dur });
// the map table (c09_map): lon/lat -> set coordinates
const mx = (lon: number) => 1.95 - (lon + 14) / 18.4615, mz = (lat: number) => -0.0565 + (lat - 24) / 18.4615;
const SHEET: T3 = [-1.05, 0.958, 1.12];                    // Stalingrad operations sheet on the map (0.9 x 0.615)
const sheetXZ = (px: number, py: number): [number, number] => [SHEET[0] + 0.45 - (px / 1024) * 0.9, SHEET[2] + 0.3075 - (py / 700) * 0.615];
const KAL = sheetXZ(440, 360);
const CAMS: Record<number, Key[]> = {
  1: [k1(0, MP, [0, 2.3, -1.4], [0, 1.05, 1.3], 50, 0.0012), glideTo(k1(150, MP, [1.0, 1.75, 0.15], [0.4, 1.45, 2.85], 42, 0.002), 40)],
  2: [k1(204, MP, [0.62, 1.2, 0.15], [0.42, 1.3, 2.85], 40, 0.003, 0.03, 0.006)],
  3: [tr(289, DS, [-3.6, 1.2, 6.3], [8, 1.55, 14.5], [0.014, 0, 0.004], 46, -0.02)],
  4: [k1(392, DS, [4.7, 3.0, 59.3], [6.1, 3.05, 62.7], 34, 0.003, 0.02)],
  5: [k1(452, MP, [0.76, 2.6, -0.1], [0.76, 0.95, 0.5], 44, 0.0012)],
  6: [k1(600, DS, [70, 1.45, -7.2], [70, 1.3, -3], 40, 0.003)],
  7: [tr(666, DS, [63.0, 1.5, -2.0], [66.5, 1.4, 3], [0.03, 0, 0], 42)],
  8: [k1(782, ST, [-30, 22, -20], [20, 4, 120], 50, 0.0012, -0.02)],
  9: [k1(900, ST, [0, 1.5, 40.5], [0, 6.2, 66], 46, 0.004, 0, 0.012)],
  10: [k1(940, MP, [-1.35, 1.55, -0.1], [-1.05, 1.3, 2.1], 40, 0.002), glideTo(k1(1050, MP, [-1.25, 1.3, 0.55], [-1.2, 1.0, 1.6], 38, 0.003), 24)],
  11: [k1(1088, MP, [0.4, 1.6, -0.1], [-1.7, 1.42, 1.9], 42, 0.002, 0.02)],
  12: [tr(1184, ST, [-4.2, 1.05, 3.5], [1.5, 1.25, 20], [0, 0, 0.035], 46, 0.02), cut(k1(1245, ST, [-1.5, 1.6, 8.8], [-4.8, 0.8, 12.5], 44, 0.003, -0.03))],
  13: [k1(1290, ST, [200.7, 1.25, -3.2], [199.5, 0.95, 2.0], 46, 0.003)],
  14: [k1(1330, ST, [236.7, 1.9, 1.7], [240.5, 1.8, 1.9], 58, 0.0015)],
  15: [k1(1407, ST, [0, 1.7, 37], [0, 3.0, 60], 50, 0.0015)],
  16: [k1(1518, MP, [-1.05, 1.95, 0.5], [-1.05, 0.95, 1.12], 40, 0.0012)],
  17: [k1(1752, MP, [KAL[0] + 0.05, 1.5, KAL[1] - 0.3], [KAL[0], 0.95, KAL[1]], 38, 0.002)],
  18: [k1(1830, ST, [2.6, 1.35, -41.4], [2, 1.0, -35.5], 44, 0.0015)],
  19: [k1(2022, MP, [0.45, 1.58, 1.4], [0.4, 1.6, 2.85], 38, 0.004, 0, 0.01)],
  20: [k1(2084, MP, [1.35, 1.45, 0.4], [0.45, 1.55, 2.85], 40, 0.002, -0.02)],
  21: [k1(2128, ST, [1.0, 1.05, -42.8], [3, 5.5, -30], 52, 0.0015)],
  22: [k1(2262, CE, [0.95, 1.55, -0.3], [0.3, 1.35, 3.0], 42, 0.002)],
  23: [k1(2436, CE, [0.18, 1.68, 2.0], [0.05, 1.7, 3.1], 34, 0.004)],
  24: [k1(2478, CE, [0.3, 1.32, 1.6], [0.3, 0.79, 1.95], 40, 0.002), cut(k1(2590, CE, [0.6, 1.5, 0.95], [0.05, 1.5, 3.1], 38, 0.003))],
  25: [k1(2645, ST, [3.4, 1.5, 26.8], [8.0, 1.0, 30.5], 44, 0.002)],
  26: [k1(2711, ST, [9, 1.3, -74], [0, 1.1, -96], 44, 0.0015)],
  27: [k1(2813, ST, [16, 7, -66], [0, 0.5, -135], 40, -0.001)],
  28: [k1(2903, SE, [-1.2, 1.0, 1.2], [12, 2.0, 60], 48, 0.002)],
  29: [k1(3010, SE, [-30, 4, 92], [30, 8, 190], 42, 0.002)],
  30: [k1(3098, BL, [1.9, 1.6, -1.6], [-0.2, 1.25, 5.5], 50, 0.0018), cut(k1(3232, BL, [1.35, 1.1, 2.02], [1.35, 0.8, 2.42], 40, 0.003))],
  31: [k1(3276, SE, [-75, 7, 35], [-25, 2, 80], 44, 0.0015)],
  32: [k1(3434, BL, [1.5, 1.6, -0.1], [3.15, 1.65, 0.65], 44, 0.003)],
  33: [k1(3510, SE, [-46, 3, 10], [-20, 0.5, 36], 40, 0.002)],
  34: [tr(3563, KU, [0, 0.95, -2.5], [2, 2.5, 60], [0, 0, 0.05], 44)],
  35: [k1(3747, KU, [-10, 2, 20], [10, 2.5, 60], 46, 0.002, 0.02)],
  36: [tr(3849, KU, [-10, 1.4, 5.0], [-4, -0.3, -2], [0.05, 0, 0], 46), glideTo(k1(3950, KU, [-6, 16, 14], [0, 0, -40], 50, 0.001), 40)],
  37: [k1(4020, KU, [4.2, 1.5, 16.8], [8.5, 1.8, 25], 42, 0.003)],
  38: [k1(4074, KU, [58, 1.0, -27], [62, 1.6, -2], 46, 0.003, -0.02)],
  39: [k1(4148, IT, [3, 1.0, 3.2], [-1, 1.2, 15], 46, 0.002)],
  40: [k1(4266, IT, [195.5, 1.5, 1.0], [200.5, 1.6, 8.5], 44, 0.002)],
  41: [k1(4428, IT, [0, 1.45, -3.0], [0, 1.25, 2.5], 42, 0.003)],
  42: [k1(4476, IT, [-296, 1.2, -8], [-300, 8, 40], 46, 0.0015), glideTo(k1(4600, IT, [-291, 11, -22], [-300, 26, 100], 46, 0.001), 50)],
  43: [tr(4730, KI, [1.5, 1.4, -12], [0, 1.2, 10], [0, 0, 0.025], 44)],
  44: [k1(4948, KI, [100.2, 0.8, -1.5], [100.4, 0.5, 3.0], 46, 0.003)],
  45: [k1(5012, KI, [2.5, 1.3, 16.5], [0, 1.0, 23.5], 44, 0.002)],
};
const DOF: Dof[] = [
  { f: 0, cInf: 4 }, { f: 150, dur: 40, cInf: 9 }, { f: 204, cInf: 12 }, { f: 293, cInf: 5 }, { f: 392, cInf: 10 }, { f: 452, cInf: 5 }, { f: 600, cInf: 9 },
  { f: 670, cInf: 7 }, { f: 788, cInf: 0 }, { f: 900, cInf: 3 }, { f: 940, cInf: 9 }, { f: 1088, cInf: 9 }, { f: 1184, cInf: 6 }, { f: 1290, cInf: 8 }, { f: 1330, cInf: 6 },
  { f: 1407, cInf: 4 }, { f: 1518, cInf: 4 }, { f: 1752, cInf: 7 }, { f: 1830, cInf: 9 }, { f: 2022, cInf: 13 }, { f: 2084, cInf: 10 }, { f: 2128, cInf: 6 },
  { f: 2262, cInf: 9 }, { f: 2436, cInf: 14 }, { f: 2478, cInf: 9 }, { f: 2590, cInf: 12 }, { f: 2645, cInf: 7 }, { f: 2715, cInf: 5 }, { f: 2817, cInf: 2 },
  { f: 2907, cInf: 6 }, { f: 3010, cInf: 3 }, { f: 3102, cInf: 8 }, { f: 3232, cInf: 13 }, { f: 3276, cInf: 3 }, { f: 3434, cInf: 8 }, { f: 3510, cInf: 4 },
  { f: 3567, cInf: 4 }, { f: 3747, cInf: 4 }, { f: 3849, cInf: 6 }, { f: 3950, dur: 40, cInf: 1 }, { f: 4020, cInf: 7 }, { f: 4074, cInf: 6 }, { f: 4152, cInf: 5 },
  { f: 4266, cInf: 6 }, { f: 4428, cInf: 9 }, { f: 4480, cInf: 3 }, { f: 4734, cInf: 5 }, { f: 4948, cInf: 10 }, { f: 5012, cInf: 7 },
];
const BOOMS_RM = [400, 418, 436];
const KICKS: [number, number][] = [[300 / 30, 0.5], [330 / 30, 0.6], [360 / 30, 0.5], ...BOOMS_RM.map((f) => [f / 30, 0.7] as [number, number]), [907 / 30, 0.6],
  [1222 / 30, 0.3], [1256 / 30, 0.3], [1811 / 30, 0.8], [2036 / 30, 0.7], [3013 / 30, 0.9], [3354 / 30, 0.5], [3364 / 30, 0.5], [3374 / 30, 0.5], [3532 / 30, 0.6],
  [3760 / 30, 0.6], [3790 / 30, 0.7], [3815 / 30, 0.6], [4031 / 30, 0.5]];

// ---------------- staging helpers ----------------
const put = (c: Ctx, w: Who3, i: number, x: number, y: number, z: number, beats: Beat[], extra: FrontOpts = {}, scale = 1, ri = 0.18) => {
  const a = act(c.t, beats, ri);
  P(c, W_(w[0], i, w[1]), x, y, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, ...extra }, scale);
};
const speaking = (c: Ctx, f0: number, f1: number, a: Expr, b: Expr, base: Expr) => (c.f >= f0 && c.f < f1 ? talk(c.t, a, b) : base);
const fog = (c: Ctx, n: number, x0: number, x1: number, y: number, z0: number, z1: number, w: number, col = "#e6ecf2", op = 0.5) => {
  for (let i = 0; i < n; i++) mist(c.out, ...c.O(x0 + (x1 - x0) * hh(i, 3), y + (i % 3) * 0.4, z0 + (z1 - z0) * hh(i, 5)), w, c.t, i, col, op);
};
const burst = (c: Ctx, x: number, y: number, z: number, w: number, f0: number, len = 6, col = "#fff3b0", glow = 3) => {
  if (c.f < f0 || c.f >= f0 + len) return;
  const u = q((c.f - f0) / len, 6);
  F(c, { key: `c9burst${col}${u}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, u, col), x, y, z, w, h: w, glow });
};
const boom = (c: Ctx, x: number, y: number, z: number, w: number, f0: number, len = 26, glow = 1.6) => {
  if (c.f < f0 || c.f >= f0 + len) return;
  const u = q((c.f - f0) / len, 12);
  F(c, { key: `c9boom${u}`, cw: 600, ch: 600, draw: (p) => fxBoom(p, u), x, y: y + w * 0.35, z, w, h: w, glow });
};
const splash = (c: Ctx, x: number, y: number, z: number, w: number, f0: number, len = 30) => {
  if (c.f < f0 || c.f >= f0 + len) return;
  const u = q((c.f - f0) / len, 15);
  F(c, { key: `c9splash${u}`, cw: 800, ch: 800, draw: (p) => fxSplash(p, u), x, y: y + w * 0.4, z, w, h: w, glow: 1.0 });
};
/** a lit, flat-painted prop on the 600 x 1000 character canvas (dog, plane) placed like a character (feet at y) */
const prop = (c: Ctx, key: string, draw: (p: Pen) => void, x: number, y: number, z: number, scale: number) => {
  const [X, Y, Z] = c.O(x, y, z); c.out.places.push({ key, draw, x: X, y: Y, z: Z, scale, size: [600, 1000, 1] });
};
const rnd = (i: number, s = 0) => hh(i, s);

// ---------------- painted overlays (canvas fx) ----------------
type Pt = [number, number];
const bez = (a: Pt, k: Pt, b: Pt, u: number): Pt => [(1 - u) ** 2 * a[0] + 2 * (1 - u) * u * k[0] + u * u * b[0], (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * k[1] + u * u * b[1]];
/** a fat campaign arrow along a quadratic curve, drawn to fraction u, with an ink rim and an arrow head */
const arrow = (g: CanvasRenderingContext2D, a: Pt, k: Pt, b: Pt, u: number, col: string, w: number) => {
  if (u <= 0.01) return;
  const pts: Pt[] = []; const n = 40;
  for (let i = 0; i <= n; i++) pts.push(bez(a, k, b, (u * i) / n));
  const e = pts[n], d = bez(a, k, b, Math.max(0, u - 0.02)), ang = Math.atan2(e[1] - d[1], e[0] - d[0]);
  const body = pts.slice(0, Math.max(2, n - 3));
  g.lineCap = "round"; g.lineJoin = "round";
  g.beginPath(); body.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.strokeStyle = INK; g.lineWidth = w + 10; g.stroke();
  g.beginPath(); body.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.strokeStyle = col; g.lineWidth = w; g.stroke();
  const L = w * 2.1, W2 = w * 1.35;
  const tip: Pt = [e[0] + Math.cos(ang) * L * 0.35, e[1] + Math.sin(ang) * L * 0.35];
  const head: Pt[] = [tip, [tip[0] - Math.cos(ang) * L + Math.cos(ang + Math.PI / 2) * W2, tip[1] - Math.sin(ang) * L + Math.sin(ang + Math.PI / 2) * W2],
    [tip[0] - Math.cos(ang) * L - Math.cos(ang + Math.PI / 2) * W2, tip[1] - Math.sin(ang) * L - Math.sin(ang + Math.PI / 2) * W2]];
  g.beginPath(); head.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath(); g.fillStyle = col; g.fill(); g.strokeStyle = INK; g.lineWidth = 6; g.stroke();
};
const label = (g: CanvasRenderingContext2D, s: string, x: number, y: number, px: number, col = "#2a1810", halo = "#f6e8c8", font = "Georgia, 'DejaVu Serif', serif") => {
  g.font = `bold ${px}px ${font}`; g.textAlign = "center"; g.textBaseline = "middle";
  g.lineWidth = px * 0.22; g.strokeStyle = halo; g.lineJoin = "round"; g.strokeText(s, x, y); g.fillStyle = col; g.fillText(s, x, y);
};
// Europe overlay: canvas 2048 x 1110 over the whole map (lon -14..58, lat 63..24)
const EW = 2048, EH = 1110;
const ep = (lon: number, lat: number): Pt => [((lon + 14) / 72) * EW, ((63 - lat) / 39) * EH];
const AXIS_EU: Pt[] = [[-4.8, 48.4], [-1.6, 49.6], [1.6, 50.9], [4, 51.6], [4.8, 53], [8, 53.7], [8.2, 55.6], [8.6, 57.2], [10.6, 57.7], [12.6, 55.7], [14, 54.2], [19, 54.6],
  [21, 55.6], [21, 57.2], [24, 57.6], [28, 59.6], [30.2, 59.8], [31.5, 58.5], [32, 57], [34.3, 56.2], [35, 55], [36, 53.5], [37.5, 52], [39.2, 51.6], [40.5, 50.5],
  [42, 49.5], [44.3, 48.8], [45, 47.4], [44.3, 46.3], [44.6, 43.7], [42.4, 43.3], [39.5, 44.2], [38, 44.7], [36.5, 45.3], [35.5, 45.3], [33.5, 44.5], [32.5, 45.4],
  [31, 46.6], [29.6, 45.4], [28.6, 44], [27.8, 42.5], [26.5, 41.3], [26.3, 40.9], [24, 40.6], [23, 39.2], [23.5, 38], [22.5, 36.5], [21.5, 36.8], [21, 38.3],
  [19.5, 40], [19.4, 41.8], [16, 43.5], [13.7, 45.6], [12.3, 44.5], [13.6, 43.5], [16, 41.5], [18.5, 40.2], [16, 38], [15.6, 38], [16.2, 39.5], [15.5, 40.1],
  [12.6, 41.5], [10.5, 43.5], [8.8, 44.4], [7.5, 43.8], [6, 43.1], [3, 43.2], [3.1, 42.4], [-1.8, 43.4], [-1.4, 44.5], [-1.2, 46.2], [-2.3, 47.2], [-4.7, 48]];
const AXIS_NO: Pt[] = [[5, 58], [7.5, 58], [10.5, 59.2], [11.5, 59.1], [12.3, 61], [12.5, 63], [5, 63]];
const AXIS_AF: Pt[] = [[8.3, 37.2], [10.3, 37.3], [11, 35.5], [10.2, 33.5], [11.5, 33.2], [15, 32.3], [19.5, 30.5], [20, 31.5], [23, 32.6], [25.2, 31.6], [28.9, 30.9],
  [28.9, 29.5], [25, 29.5], [25, 24], [10, 24], [10, 30], [9.5, 30.3], [8, 32], [8.3, 35.5]];
const axisFill = (g: CanvasRenderingContext2D, k: number, crack: number) => {
  g.save(); const [bx, by] = ep(13.4, 52.5);
  g.beginPath(); g.arc(bx, by, 60 + 2200 * k, 0, Math.PI * 2); g.clip();
  for (const poly of [AXIS_EU, AXIS_NO, AXIS_AF]) {
    g.beginPath(); poly.forEach(([lo, la], i) => { const [x, y] = ep(lo, la); if (i) g.lineTo(x, y); else g.moveTo(x, y); }); g.closePath();
    g.fillStyle = "rgba(34,26,30,0.55)"; g.fill();
    g.save(); g.clip(); g.strokeStyle = "rgba(20,14,18,0.6)"; g.lineWidth = 7;
    for (let x = -EH; x < EW; x += 26) { g.beginPath(); g.moveTo(x, EH); g.lineTo(x + EH, 0); g.stroke(); }
    g.restore();
    g.setLineDash([22, 12]); g.strokeStyle = "#a81e1e"; g.lineWidth = 9; g.stroke(); g.setLineDash([]);
  }
  g.restore();
  if (crack > 0) {   // cracks running out from Berlin across the shaded empire
    const cr: Pt[][] = [[[13.4, 52.5], [18, 50], [24, 51.5], [30, 49], [37, 50.5], [44.5, 48.7]], [[13.4, 52.5], [12, 47], [14, 43], [16, 38], [14, 33], [21, 30.5], [28.9, 30.8]],
      [[13.4, 52.5], [7, 50], [2, 47.5], [-2, 46]], [[13.4, 52.5], [22, 56], [30, 59.5]]];
    g.strokeStyle = "#f6e8c8"; g.lineCap = "round";
    for (const line of cr) {
      const n = Math.max(1, Math.round((line.length - 1) * crack));
      for (const [w, col] of [[16, INK], [7, "#f6e8c8"]] as [number, string][]) {
        g.beginPath(); g.lineWidth = w; g.strokeStyle = col;
        for (let i = 0; i <= n; i++) { const [x, y] = ep(line[i][0], line[i][1]); const jx = (i % 2 ? 9 : -9); if (i) g.lineTo(x + jx, y); else g.moveTo(x, y); }
        g.stroke();
      }
    }
  }
  if (k > 0.8) label(g, "AXIS  1942", ep(22, 47.6)[0], ep(22, 47.6)[1], 64, "#f6e8c8", "#1e1418");
};
const torchMap = (g: CanvasRenderingContext2D, ka: number, kt: number) => {
  axisFill(g, 1, 0);
  const A = (lo: number, la: number) => ep(lo, la);
  arrow(g, A(29.5, 30.6), A(24, 31.6), A(17.5, 31.2), ka, "#c8202c", 26);
  if (ka > 0.05) { const [x, y] = A(28.9, 30.8); g.fillStyle = INK; g.beginPath(); g.arc(x, y, 14, 0, 7); g.fill(); label(g, "EL ALAMEIN", x - 10, y + 52, 44); }
  arrow(g, A(-14, 36.5), A(-11, 34.5), A(-7.8, 33.8), kt, "#2a5ac8", 24);
  arrow(g, A(-9, 40), A(-4, 38.5), A(-0.8, 35.9), clamp01(kt * 1.1 - 0.05), "#2a5ac8", 24);
  arrow(g, A(-3, 41), A(1, 39.5), A(3.0, 36.9), clamp01(kt * 1.15 - 0.12), "#2a5ac8", 24);
  if (kt > 0.4) { const [x, y] = A(-6, 39.2); label(g, "TORCH", x, y, 58, "#f6e8c8", "#1e2a5a"); label(g, "U.S. + BRITISH", x, y + 52, 34, "#f6e8c8", "#1e2a5a"); }
  if (ka > 0.6) { const [x, y] = A(23.5, 33.6); label(g, "8th ARMY", x, y, 40, "#f6e8c8", "#7a1418"); }
  if (kt > 0.9) {   // Rommel's pin caught between the two
    const [x, y] = A(13, 31.6); g.fillStyle = "#2e2e30"; g.strokeStyle = INK; g.lineWidth = 6; g.fillRect(x - 70, y - 30, 140, 60); g.strokeRect(x - 70, y - 30, 140, 60);
    label(g, "ROMMEL", x, y, 34, "#f6e8c8", "#2e2e30");
  }
};
/** Stalingrad operations sheet (1024 x 700): Volga, Don, the city, 6th Army, the Romanian flanks, the two Soviet arms */
const uranus = (g: CanvasRenderingContext2D, k: number, roman: number, ring: number) => {
  g.fillStyle = "#efe4c4"; g.fillRect(0, 0, 1024, 700); g.strokeStyle = "#5a3a22"; g.lineWidth = 10; g.strokeRect(8, 8, 1008, 684);
  g.strokeStyle = "rgba(90,60,30,0.18)"; g.lineWidth = 2; for (let x = 64; x < 1024; x += 64) { g.beginPath(); g.moveTo(x, 10); g.lineTo(x, 690); g.stroke(); } for (let y = 64; y < 700; y += 64) { g.beginPath(); g.moveTo(10, y); g.lineTo(1014, y); g.stroke(); }
  const river = (pts: Pt[], w: number) => { g.lineCap = "round"; g.lineJoin = "round"; g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.strokeStyle = "#2a5a8a"; g.lineWidth = w + 6; g.stroke(); g.strokeStyle = "#7ab0d8"; g.lineWidth = w; g.stroke(); };
  river([[790, 0], [745, 140], [715, 260], [705, 330], [735, 450], [790, 560], [860, 700]], 22);
  river([[0, 130], [150, 160], [300, 230], [400, 300], [432, 360], [415, 450], [470, 560], [560, 700]], 13);
  label(g, "VOLGA", 820, 210, 34, "#1e3a6a"); label(g, "DON", 300, 190, 30, "#1e3a6a");
  // the Romanian flanks (yellow hatching, flash while named)
  const hatch = (x: number, y: number, w: number, h: number, col: string) => { g.save(); g.beginPath(); g.ellipse(x, y, w, h, -0.3, 0, 7); g.fillStyle = col; g.fill(); g.clip(); g.strokeStyle = "rgba(80,60,10,0.5)"; g.lineWidth = 4; for (let i = -300; i < 300; i += 18) { g.beginPath(); g.moveTo(x + i, y - h); g.lineTo(x + i + h * 2, y + h); g.stroke(); } g.restore(); g.strokeStyle = INK; g.lineWidth = 5; g.beginPath(); g.ellipse(x, y, w, h, -0.3, 0, 7); g.stroke(); };
  const ry = roman > 0 ? `rgba(248,${200 + Math.round(40 * roman)},40,0.9)` : "rgba(232,200,90,0.75)";
  hatch(330, 190, 120, 40, ry); hatch(690, 560, 120, 40, ry);
  label(g, "3rd ROMANIAN", 330, 128, 30); label(g, "4th ROMANIAN", 690, 628, 30);
  // 6th Army round the city
  g.beginPath(); g.ellipse(585, 330, 150, 95, 0, 0, 7); g.fillStyle = "rgba(90,96,90,0.85)"; g.fill(); g.strokeStyle = INK; g.lineWidth = 6; g.stroke();
  label(g, "6th ARMY", 560, 322, 40, "#f6e8c8", "#2a2a2c");
  g.fillStyle = "#5a5a5e"; g.fillRect(680, 300, 50, 70); g.strokeStyle = INK; g.strokeRect(680, 300, 50, 70);
  label(g, "STALINGRAD", 820, 380, 36, "#7a1418");
  arrow(g, [150, 60], [330, 260], [440, 345], k, "#c8202c", 34);
  arrow(g, [960, 650], [560, 610], [450, 385], k, "#c8202c", 34);
  if (ring > 0) { g.setLineDash([26, 16]); g.strokeStyle = "#c8202c"; g.lineWidth = 12; g.beginPath(); g.ellipse(600, 340, 200 + 40 * (1 - ring), 140 + 30 * (1 - ring), 0, 0, 7 * ring); g.stroke(); g.setLineDash([]); }
  label(g, "OPERATION URANUS  ·  19 NOV 1942", 512, 668, 26, "#5a3a22");
};
const stalinLabel = (g: CanvasRenderingContext2D, k: number) => {
  g.clearRect(0, 0, 600, 200);
  g.font = "bold 96px Georgia, 'DejaVu Serif', serif"; g.textBaseline = "middle"; g.textAlign = "left";
  const w1 = g.measureText("STALIN").width, w2 = g.measureText("GRAD").width, x0 = 300 - (w1 + w2) / 2;
  g.lineWidth = 18; g.strokeStyle = "#f6e8c8"; g.lineJoin = "round"; g.strokeText("STALIN", x0, 100); g.strokeText("GRAD", x0 + w1, 100);
  g.fillStyle = k > 0 ? "#c8202c" : "#2a1810"; g.fillText("STALIN", x0, 100); g.fillStyle = "#2a1810"; g.fillText("GRAD", x0 + w1, 100);
  if (k > 0) { g.strokeStyle = "#c8202c"; g.lineWidth = 10; g.beginPath(); g.moveTo(x0, 160); g.lineTo(x0 + w1 * k, 160 + 6 * Math.sin(k * 9)); g.stroke(); }
};
const telegram = (g: CanvasRenderingContext2D, ps: number) => {
  g.fillStyle = "#f2e8c8"; g.fillRect(0, 0, 800, 600); g.strokeStyle = "#7a5a3a"; g.lineWidth = 8; g.strokeRect(6, 6, 788, 588);
  g.fillStyle = "#c8a24a"; g.fillRect(6, 6, 788, 70);
  g.fillStyle = "#2a1810"; g.font = "bold 46px Georgia, 'DejaVu Serif', serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("TELEGRAMM", 400, 42);
  g.textAlign = "left"; g.font = "bold 26px 'Courier New', 'DejaVu Sans Mono', monospace"; g.fillStyle = "#3a2a1a";
  g.fillText("TO:   GEN. F. PAULUS - STALINGRAD", 40, 120); g.fillText("FROM: FUEHRER HQ          30.1.1943", 40, 158);
  g.strokeStyle = "#7a5a3a"; g.lineWidth = 3; g.beginPath(); g.moveTo(40, 185); g.lineTo(760, 185); g.stroke();
  g.font = "bold 40px 'Courier New', 'DejaVu Sans Mono', monospace"; g.fillStyle = "#1e1410";
  g.fillText("CONGRATULATIONS:", 40, 240); g.fillText("YOU ARE NOW", 40, 292); g.fillText("FIELD MARSHAL.", 40, 344);
  if (ps > 0) {
    g.globalAlpha = Math.min(1, ps); g.font = "bold 32px 'Courier New', 'DejaVu Sans Mono', monospace"; g.fillStyle = "#8a1418";
    g.fillText("P.S. NO GERMAN FIELD MARSHAL", 40, 430); g.fillText("     HAS EVER SURRENDERED.", 40, 472);
    g.save(); g.translate(600, 540); g.rotate(-0.12); g.strokeStyle = "#8a1418"; g.lineWidth = 5; g.strokeRect(-110, -34, 220, 68); g.font = "bold 30px Georgia, serif"; g.textAlign = "center"; g.fillText("STRENG", 0, 0); g.restore();
    g.globalAlpha = 1;
  }
};
const chalk = (g: CanvasRenderingContext2D, title: string, n: number, big: boolean) => {
  g.fillStyle = "#24302a"; g.fillRect(0, 0, 1000, 600); g.strokeStyle = "#5a3a1e"; g.lineWidth = 22; g.strokeRect(11, 11, 978, 578);
  g.fillStyle = "#ecece4"; g.font = "bold 56px 'DejaVu Sans', Arial, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(title, 500, 80);
  g.strokeStyle = "#ecece4"; g.lineWidth = 9; g.lineCap = "round";
  for (let i = 0; i < n; i++) {
    const grp = Math.floor(i / 5), j = i % 5, gx = 90 + (grp % 5) * 165, gy = 170 + Math.floor(grp / 5) * 120;
    g.beginPath();
    if (j < 4) { g.moveTo(gx + j * 26, gy); g.lineTo(gx + j * 26 + 4, gy + 80); } else { g.moveTo(gx - 14, gy + 70); g.lineTo(gx + 96, gy + 12); }
    g.stroke();
  }
  if (big && n > 0) { g.font = "bold 110px 'DejaVu Sans', Arial, sans-serif"; g.fillStyle = "#f2d860"; g.fillText(String(n), 860, 500); }
};
const ju52 = (p: Pen) => {   // three-engined transport, side-on, nose right, on the 600 x 1000 canvas (centred at y 500)
  const c = "#5a5e58", d = "#3a3e3a", g = p.g;
  p.poly([[40, 500], [120, 470], [470, 462], [540, 478], [560, 500], [540, 520], [470, 530], [130, 528]], c, 7);
  for (let x = 140; x < 460; x += 16) p.stroke([[x, 468], [x, 524]], 2, d);
  p.poly([[40, 500], [20, 430], [70, 430], [110, 480]], c, 7);
  p.poly([[220, 500], [380, 498], [400, 510], [200, 514]], d, 6);
  p.poly([[440, 470], [480, 452], [520, 460], [530, 474]], "#9aaab8", 5);
  for (const [x, y] of [[560, 500], [300, 512]] as Pt[]) { p.ell(x, y, 22, 18, d, 6); p.stroke([[x + 8, y - 60], [x + 8, y + 60]], 6, "#2a2a2a"); }
  p.stroke([[330, 528], [320, 560]], 6, INK); p.ell(318, 566, 14, 14, "#1a1a1a", 4);
  g.globalAlpha = 1;
};
const chute = (p: Pen, sway: number) => {   // supply container under a parachute, on the 600 x 1000 canvas
  p.g.save(); p.g.translate(300, 500); p.g.rotate(sway * 0.12); p.g.translate(-300, -500);
  p.poly([[120, 380], [170, 250], [300, 210], [430, 250], [480, 380], [420, 360], [360, 380], [300, 362], [240, 380], [180, 360]], "#ece6d4", 9);
  for (const x of [120, 240, 360, 480]) p.stroke([[x, 380], [300, 700]], 4, "#6a6050");
  p.poly([[262, 700], [338, 700], [338, 860], [262, 860]], "#4a5048", 8); p.stroke([[262, 760], [338, 760]], 5, "#2a2e2a");
  p.g.restore();
};

// ---------------- staging ----------------
const GUNS = Array.from({ length: 19 }, (_, i) => -54 + 6 * i);
const flashOn = (i: number, f: number) => ((f * 7 + i * 13) % 23) < 6;           // = c09_desert.flash_on
const HIT_X = 0.4, HIT_Z = 2.85;
const hitler = (c: Ctx, beats: Beat[], extra: FrontOpts = {}, x = HIT_X, z = HIT_Z) => put(c, [HITLER_WAR, "hitw"], 1, x, 0, z, beats, extra);
const staff = (c: Ctx, i: number, x: number, z: number, beats: Beat[], extra: FrontOpts = {}) => put(c, officer("de", i), 10 + i, x, 0, z, beats, extra);
const axisOverlay = (c: Ctx, k: number, crack: number) =>
  F(c, { key: `c9axis${q(k, 24)}_${q(crack, 12)}`, cw: EW, ch: EH, draw: (p) => axisFill(p.g, q(k, 24), q(crack, 12)), x: 0, y: 0.957, z: 1.0, w: 3.9, h: 2.113, flat: true, rot: Math.PI, soft: true, opacity: 1, glow: 0.95 });

const STAGE: Record<number, (c: Ctx) => void> = {
  1: (c) => {
    // "By late 1942, the Axis controls more of the world than ever before."
    axisOverlay(c, smooth((c.f - 100) / 85), 0);
    hitler(c, [[0, "hips", "smug"], [110, "point", "proud"], [151, "armsUp", "beam"], [178, "hips", "smug"]], { facing: c.f >= 110 && c.f < 151 ? -1 : 0 });
    staff(c, 0, -0.9, 2.75, [[0, "cross", "stern"], [160, "clap", "grin"]]);
    staff(c, 1, 1.75, 2.55, [[0, null, "neutral"], [150, "clap", "smile"]]);
  },
  2: (c) => {
    // "And within a few months, it starts falling apart."
    axisOverlay(c, 1, smooth((c.f - 252) / 30));
    hitler(c, [[204, "hips", "smug"], [238, "chin", "worried"], [256, "head", "shock"], [270, "head", "panic"]], {}, HIT_X, HIT_Z);
  },
  3: (c) => {
    // "In North Africa, the British finally beat Rommel at a place called El Alamein in Egypt."
    GUNS.forEach((gx, i) => {
      for (let row = 0; row < 2; row++) {
        if (row && Math.abs(gx) > 40) continue;
        const x = gx + (row ? 3 : 0), z = row ? 19.7 : 12.7, j = i + row * 19;
        if (flashOn(i, c.f + row * 5)) {
          const ph = ((c.f + row * 5) * 7 + i * 13) % 23;
          F(c, { key: `c9mz${ph}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, ph / 6, "#ffd27a", 12, 50, 240), x, y: 1.1, z, w: 3.4, h: 3.4, glow: 3 });
        }
        if (j % 3 === 0) burst(c, -40 + rnd(j) * 90, 1 + rnd(j, 2) * 3, 95 + rnd(j, 3) * 40, 6, 300 + ((j * 17) % 90), 8, "#ffb04a", 2.6);
      }
    });
    for (const gx of [-6, 0, 6, 12]) {
      const i = GUNS.indexOf(gx), fl = flashOn(i, c.f) || flashOn(i, c.f - 1);
      put(c, tommy(i), 30 + i, gx - 1.15, 0, 8.7, [[293, null, "determined"]], { prop: "crate", pose: undefined, expr: fl ? "shock" : "determined" });
      put(c, tommy(i + 7), 50 + i, gx + 1.35, 0, 9.3, [[293, "head", "grim"]], { pose: fl ? "head" : "point", pk: 1, expr: fl ? "pained" : "yell", facing: fl ? 0 : 1 });
      if (gx === 0) put(c, officer("uk", 2), 70, gx + 0.3, 0, 7.6, [[293, "point", "shout"], [355, "fist", "yell"], [363, "pointUp", "yell"]], { expr: talk(c.t, "shout", "yell") });
    }
    fog(c, 4, -20, 30, 0.6, 22, 40, 14, "#4a3a3a", 0.35);
  },
  4: (c) => {
    // "...beat Rommel at a place called El Alamein in Egypt."
    const duck = smooth((c.f - 436) / 10);
    put(c, [ROMMEL, "rommel"], 2, 6.11, 1.42 - 0.55 * duck, 62.74, [[392, "chin", "proud"], [404, "collar", "shock"], [420, "head", "panic"], [436, "head", "fear"]], { prop: c.f < 404 ? "binoc" : null });
    BOOMS_RM.forEach((f0, k) => boom(c, [2.0, 10.5, 6.5][k], 0, [67, 66.5, 71][k], 6 + k, f0, 28, 1.8));
    for (let k = 0; k < 5; k++) burst(c, -10 + k * 7, 2 + (k % 2), 75 + k * 4, 3, 392 + k * 11, 6, "#ffb04a", 2.4);
  },
  5: (c) => {
    // "At the same time, American and British troops land behind him in Morocco and Algeria."
    const ka = smooth((c.f - 452) / 40), kt = smooth((c.f - 515) / 60);
    F(c, { key: `c9torch${q(ka, 20)}_${q(kt, 30)}`, cw: EW, ch: EH, draw: (p) => torchMap(p.g, q(ka, 20), q(kt, 30)), x: 0, y: 0.957, z: 1.0, w: 3.9, h: 2.113, flat: true, rot: Math.PI, soft: true, opacity: 1, glow: 0.95 });
  },
  6: (c) => {
    // "Rommel is squeezed from both sides."
    const u = smooth((c.f - 620) / 26);
    put(c, [ROMMEL, "rommel"], 2, 70, 0, -3, [[600, "hips", "smug"], [616, "collar", "nervous"], [638, "palms", "panic"], [652, "head", "shock"]],
      { tilt: q(Math.sin(c.t * 22) * 3 * u, 4) }, 1);
    put(c, [MONTGOMERY, "monty"], 3, 72.6 - 1.55 * u, 0, -2.8, [[600, "cross", "smug"], [622, "palms", "determined"]], { facing: -1, mode: u > 0 && u < 1 ? "march" : "stand", phase: q((c.t * 2) % 1, 30) });
    put(c, [EISENHOWER, "ike"], 4, 67.4 + 1.55 * u, 0, -2.8, [[600, "hips", "grin"], [622, "palms", "determined"]], { facing: 1, mode: u > 0 && u < 1 ? "march" : "stand", phase: q((c.t * 2 + 0.5) % 1, 30) });
  },
  7: (c) => {
    // "By May 1943, the Axis armies in Africa surrender."
    for (let i = 0; i < 11; i++) {
      const x = 63 + i * 1.15 + (rnd(i) - 0.5) * 0.3, z = 3.0 + (i % 2) * 0.5;
      const late = c.f > 764 + (i % 4) * 3;
      put(c, surr(i), 80 + i, x, 0, z, [[670, i % 3 === 0 ? "armsUp" : null, i % 2 ? "relief" : "exhausted"], [764 + (i % 4) * 3, "armsUp", i % 2 ? "relief" : "sad"]],
        { prop: i === 6 ? ["flag", "white"] : null, flutter: q((c.t * 1.3) % 1, 20), look: late ? 0 : Math.round(rnd(i, 4) * 2 - 1) });
    }
    put(c, tommy(3), 100, 66.2, 0, 0.6, [[670, "hips", "stern"], [740, null, "smile"]]);
    put(c, gi(5), 101, 71.8, 0, 0.4, [[670, "cross", "grin"], [764, "point", "laugh"]]);
    put(c, [MONTGOMERY, "monty"], 3, 69.6, 0, 1.0, [[670, "hips", "proud"], [727, "pointUp", "smug"]]);
  },
  8: (c) => {
    // "But the biggest battle is happening in a Soviet city on the Volga river."
    fog(c, 5, -20, 40, 6, 40, 90, 40, "#c8b4b0", 0.25);
  },
  9: (c) => {
    // "Stalingrad."
    put(c, winter(1), 110, -3.2, 0, 48.5, [[900, null, "determined"]], { mode: "crouch", prop: "ppsh" });
    put(c, winter(2), 111, 3.0, 0, 47.4, [[900, null, "grim"]], { mode: "kneel" });
    fog(c, 3, -10, 10, 1.5, 58, 64, 10, "#d8c4c0", 0.3);
  },
  10: (c) => {
    // "Hitler wants it because it's an important industrial city, and maybe because it has Stalin's name on it."
    axisOverlay(c, 1, 0);
    const k = clamp01((c.f - 1053) / 20);
    if (c.f >= 1040) F(c, { key: `c9stlabel${q(k, 10)}`, cw: 600, ch: 200, draw: (p) => stalinLabel(p.g, q(k, 10)), x: mx(44.5) + 0.05, y: 0.962, z: mz(48.7) + 0.13, w: 0.6, h: 0.2, flat: true, rot: Math.PI, soft: true, opacity: 1, glow: 1 });
    hitler(c, [[940, "point", "scheme"], [995, "fist", "proud"], [1023, "chin", "scheme"], [1047, "point", "grin"], [1068, "point", "laugh"]], { facing: -1 }, -0.9, 2.75);
    staff(c, 2, 0.5, 2.85, [[940, null, "nervous"], [1068, "shrug", "worried"]]);
  },
  11: (c) => {
    // "Stalin refuses to lose it for exactly the same reason."
    axisOverlay(c, 1, 0);
    put(c, [STALIN_COAT, "stalinc"], 5, -2.75, 0, 1.35, [[1088, "cross", "stern"], [1106, "fist", "determined"], [1143, "point", "angry"], [1170, "cross", "smug"]], { facing: 1 });
    hitler(c, [[1088, "point", "scheme"], [1110, "palms", "angry"], [1150, "fists", "furious"]], { facing: -1 }, -0.9, 2.75);
  },
  12: (c) => {
    // "The fighting is street by street, house by house, sometimes room by room."
    const SOV: [number, number, FrontOpts["mode"]][] = [[-5.0, 8.0, "crouch"], [-4.4, 11.6, "kneel"], [5.2, 13.0, "crouch"], [-4.8, 17.5, "kneel"]];
    SOV.forEach(([x, z, m], i) => put(c, winter(i + 3), 120 + i, x, 0, z, [[1184, null, i % 2 ? "determined" : "grim"], [1222 + i * 6, null, "yell"]], { mode: m, prop: i % 2 ? "ppsh" : null }));
    if (c.f >= 1240 && c.f < 1275) {
      const u = (c.f - 1240) / 35;
      put(c, winter(8), 128, -6 + 12 * u, 0, 15.5, [[1240, null, "yell"]], { mode: "run", phase: q((c.t * 2.4) % 1, 30), prop: "ppsh" });
    }
    const GER: [number, number][] = [[4.2, 27.0], [-3.6, 31.0], [5.5, 33.5]];
    GER.forEach(([x, z], i) => put(c, german(i + 2), 130 + i, x, 0, z, [[1184, null, "angry"]], { mode: i === 1 ? "kneel" : "crouch" }));
    [1192, 1209, 1227, 1245, 1261, 1278].forEach((f0, k) => burst(c, k % 2 ? 4.4 : -4.5, 1.0, k % 2 ? 26.5 : 11.2, 0.8, f0, 4, "#ffd27a", 2.6));
    fog(c, 3, -6, 6, 1.2, 20, 36, 8, "#bca8a8", 0.3);
  },
  13: (c) => {
    // "...sometimes room by room."
    put(c, winter(4), 140, 198.6, 0, 2.3, [[1290, null, "determined"], [1306, null, "scheme"]], { mode: "crouch", prop: "ppsh" });
    put(c, winter(6), 141, 201.6, 0, 0.0, [[1290, null, "fear"], [1310, "point", "yell"]], { mode: "kneel" });
    put(c, german(5), 142, 200.3, 0.25, 4.6, [[1290, null, "shock"], [1310, null, "panic"]], { mode: "crouch" });
  },
  14: (c) => {
    // "Soldiers fight over a single staircase."
    const peekT = Math.floor((c.f - 1330) / 16) % 2;
    put(c, winter(5), 150, 240.0, 3.3, 5.3, [[1330, null, "scheme"], [1380, null, "angry"]], { mode: peekT ? "kneel" : "crouch", prop: "ppsh", headTilt: peekT ? 0 : -12 });
    put(c, german(6), 151, 240.1, 0, -1.3, [[1330, null, "nervous"], [1380, "fist", "furious"]], { mode: peekT ? "crouch" : "kneel", headTilt: peekT ? 12 : 0 });
  },
  15: (c) => {
    // "The city's main train station changes hands more than a dozen times."
    const n = Math.max(0, Math.min(13, Math.floor((c.f - 1445) / 4.5)));
    for (let w = 0; w < 13; w++) {
      const f0 = 1440 + w * 4.5, u = (c.f - f0) / 26;
      if (u < 0 || u > 1) continue;
      const dir = w % 2 ? -1 : 1;
      for (let k = 0; k < 3; k++) {
        const who = w % 2 ? german(w + k) : winter(w + k);
        put(c, who, 160 + (w % 4) * 3 + k, -dir * 13 + dir * 26 * u + k * 1.4 * dir, 0, 50 + k * 1.6 + (w % 3), [[1407, null, w % 2 ? "angry" : "yell"]], { mode: "run", phase: q((c.t * 2.6 + k * 0.3) % 1, 30), prop: k === 1 && !(w % 2) ? "ppsh" : null });
      }
    }
    F(c, { key: `c9tally${n}`, cw: 1000, ch: 600, draw: (p) => chalk(p.g, "STATION CHANGED HANDS", n, true), x: -3.6, y: 1.25, z: 41.5, w: 1.6, h: 0.96, glow: 0.95 });
  },
  16: (c) => {
    // "Then, in November 1942, the Soviets launch a surprise attack around the city, through the weaker Romanian armies..."
    const k = smooth((c.f - 1604) / (1811 - 1604)), rom = c.f >= 1689 && c.f < 1740 ? q(0.5 + 0.5 * Math.sin((c.f - 1689) * 0.5), 6) : 0;
    axisOverlay(c, 1, 0);
    F(c, { key: `c9uranus${q(k, 40)}_${rom}`, cw: 1024, ch: 700, draw: (p) => uranus(p.g, q(k, 40), rom, 0), x: SHEET[0], y: SHEET[1], z: SHEET[2], w: 0.9, h: 0.615, flat: true, rot: Math.PI, glow: 0.95 });
  },
  17: (c) => {
    // "In four days, their two arms meet."
    const k = 0.62 + 0.38 * smooth((c.f - 1758) / (1811 - 1758)), ring = smooth((c.f - 1811) / 14);
    F(c, { key: `c9uranus${q(k, 40)}_0_${q(ring, 10)}`, cw: 1024, ch: 700, draw: (p) => uranus(p.g, q(k, 40), 0, q(ring, 10)), x: SHEET[0], y: SHEET[1], z: SHEET[2], w: 0.9, h: 0.615, flat: true, rot: Math.PI, glow: 0.95 });
    stamp(c.out, c.t, at(1811), "TRAPPED", ...c.O(KAL[0] - 0.1, 0.966, KAL[1] + 0.06), 0.34, true, Math.PI);
  },
  18: (c) => {
    // "The entire German Sixth Army, around three hundred thousand men including their allies, is trapped inside."
    const RING: [number, number, FrontOpts["mode"]][] = [[0.3, -35.1, "stand"], [1.25, -34.5, "stand"], [2.8, -34.4, "stand"], [3.8, -35.1, "stand"], [4.2, -36.6, "kneel"], [-0.3, -37.0, "kneel"], [2.0, -33.6, "stand"]];
    RING.forEach(([x, z, m], i) => {
      const shiv = q(Math.sin(c.t * 26 + i) * 1.6, 4);
      put(c, coldGerman(i), 170 + i, x, 0, z, [[1830, i % 2 ? "cross" : "collar", i % 3 ? "exhausted" : "sad"], [1987 + i * 2, i % 2 ? "cross" : "collar", i % 3 ? "dread" : "fear"]], { mode: m, tilt: shiv });
    });
    fog(c, 4, -6, 10, 0.5, -30, -24, 10, "#e8eef4", 0.35);
  },
  19: (c) => {
    // "Hitler forbids them to break out."
    hitler(c, [[2022, "fist", "angry"], [2036, "fists", "furious"], [2061, "point", "yell"]], { expr: speaking(c, 2026, 2075, "yell", "furious", "furious") });
    stamp(c.out, c.t, at(2061), "NO\nBREAKOUT", ...c.O(-0.25, 1.95, 2.6), 0.8);
  },
  20: (c) => {
    // "Instead, he promises to fly in supplies."
    hitler(c, [[2084, "palms", "scheme"], [2113, "pointUp", "proud"]], { expr: speaking(c, 2086, 2128, "shout", "proud", "proud") });
    staff(c, 3, 1.55, 2.6, [[2084, null, "nervous"], [2113, "shrug", "worried"]]);
    staff(c, 4, -0.8, 2.75, [[2084, "cross", "dread"]]);
  },
  21: (c) => {
    // "The planes bring a fraction of what the army needs."
    const u = (c.f - 2128) / 100;
    prop(c, "c9ju52", ju52, -36 + 70 * u, 14, -18, 6);
    const d = clamp01((c.f - 2165) / 90), px = -36 + 70 * ((2165 - 2128) / 100) + 9 * d, py = 21 * (1 - d) + 0.0;
    if (c.f >= 2165) prop(c, `c9chute${q(Math.sin(c.t * 3), 4)}`, (p) => chute(p, q(Math.sin(c.t * 3), 4)), Math.min(px, 6), py, -26, 0.8);
    const sad = c.f > 2204;
    [[-0.6, -38.6], [1.5, -39.4], [3.6, -38.4]].forEach(([x, z], i) =>
      put(c, coldGerman(i + 2), 180 + i, x, 0, z, [[2128, "pointUp", "joy"], [2204 + i * 3, i === 1 ? "shrug" : "collar", "sad"], [2241, "head", "exhausted"]], { look: sad ? 0 : -1, headTilt: sad ? 0 : -14 }));
  },
  22: (c) => {
    // "In January 1943, with his men starving, General Paulus gets a promotion to Field Marshal."
    put(c, [PAULUS, "paulus"], 6, 0, 0, 3.1, [[2262, "chin", "exhausted"], [2334, "collar", "sad"], [2385, "chin", "nervous"], [2407, null, "shock"]], { prop: c.f >= 2385 ? "paper" : null });
    staff(c, 5, 1.65, 2.5, [[2262, null, "neutral"], [2370, "point", "stern"], [2385, "hips", "smug"]], { prop: c.f < 2385 ? "paper" : null, facing: -1 });
    staff(c, 6, -1.9, 3.0, [[2262, "cross", "exhausted"]]);
  },
  23: (c) => {
    // "It's not a reward."
    put(c, [PAULUS, "paulus"], 6, 0, 0, 3.1, [[2436, null, "dread"], [2452, "collar", "dread"]], { prop: "paper" });
  },
  24: (c) => {
    // "No German Field Marshal had ever surrendered, so Hitler was basically telling him to fight to the death."
    const ps = clamp01((c.f - 2525) / 12);
    if (c.f < 2590) F(c, { key: `c9tgram${q(ps, 6)}`, cw: 800, ch: 600, draw: (p) => telegram(p.g, q(ps, 6)), x: 0.3, y: 0.798, z: 1.93, w: 0.48, h: 0.36, flat: true, rot: Math.PI + 0.06, glow: 0.92 });
    else put(c, [PAULUS, "paulus"], 6, 0, 0, 3.1, [[2590, "collar", "fear"], [2620, "head", "dread"]], { prop: c.f < 2620 ? "paper" : null });
  },
  25: (c) => {
    // "The next day, Paulus surrenders."
    const u = smooth((c.f - 2650) / 55), x = 9.9 - 2.4 * u, y = x > 8.2 ? -(x - 8.2) * 0.62 : 0;
    put(c, [PAULUS, "paulus"], 6, x, y, 30.5, [[2645, "collar", "exhausted"], [2687, null, "sorrow"]], { mode: u > 0 && u < 1 ? "march" : "stand", phase: q((c.t * 1.2) % 1, 30), lift: 30 });
    put(c, winter(9), 190, 6.2, 0, 28.8, [[2645, null, "determined"]], { prop: "ppsh" });
    put(c, winter(10), 191, 6.0, 0, 32.3, [[2645, null, "grim"]]);
    put(c, officer("su", 1), 192, 5.2, 0, 30.6, [[2645, "hips", "stern"], [2687, "point", "stern"]], { facing: 1 });
    fog(c, 3, 3, 10, 0.6, 33, 38, 8, "#e8eef4", 0.3);
  },
  26: (c) => {
    // "About ninety thousand Germans walk into Soviet captivity."
    for (let i = 0; i < 36; i++) {
      const row = Math.floor(i / 3), lane = i % 3, z = -70 - row * 2.6 - (c.f - 2715) * 0.035 + (rnd(i) - 0.5) * 0.6;
      put(c, pow(i), 200 + i, -0.9 + lane * 0.9 + (rnd(i, 2) - 0.5) * 0.3, 0, z, [[2715, i % 4 === 0 ? "collar" : i % 4 === 1 ? "cross" : null, (["exhausted", "sad", "grief", "exhausted", "sorrow"] as Expr[])[i % 5]]],
        { mode: "stroll", phase: q((c.t * 0.7 + rnd(i, 3)) % 1, 40) });
    }
    for (let i = 0; i < 4; i++) put(c, winter(11 + i), 240 + i, 3.0, 0, -72 - i * 9 - (c.f - 2715) * 0.035, [[2715, null, "grim"]], { mode: "stroll", phase: q((c.t * 0.7 + i * 0.3) % 1, 40) });
    fog(c, 4, -12, 12, 0.4, -100, -80, 12, "#eef2f6", 0.3);
  },
  27: (c) => {
    // "Only about five thousand of them ever make it home."
    for (let i = 0; i < 18; i++) {
      const row = Math.floor(i / 3), z = -112 - row * 3.2 - (c.f - 2817) * 0.03;
      if (c.f > 2850 + i * 2 && i % 6 !== 0) continue;
      put(c, pow(i + 5), 260 + i, -0.9 + (i % 3) * 0.9, 0, z, [[2817, null, "exhausted"]], { mode: "stroll", phase: q((c.t * 0.7 + rnd(i, 3)) % 1, 40) });
    }
    fog(c, 5, -20, 20, 0.6, -130, -100, 18, "#eef2f6", 0.45);
  },
  28: (c) => {
    // "Meanwhile, at sea, German submarines called U-boats have been sinking the ships that carry food and weapons to Britain."
    fog(c, 4, -40, 60, 2, 80, 160, 40, "#a8b0b8", 0.3);
  },
  29: (c) => {
    // (the torpedoed tanker)
    boom(c, 22, 2, 184, 26, 3013, 40, 2.0);
    for (let k = 0; k < 3; k++) splash(c, 10 + k * 14, -0.25, 178 - k * 2, 14, 3016 + k * 6, 34);
  },
  30: (c) => {
    // "But at a country house called Bletchley Park, British codebreakers have cracked the German Enigma code."
    if (c.f < 3232) {
      put(c, codebreaker(0), 300, -0.4, 0, 6.3, [[3102, "chin", "determined"], [3209, "cheer", "joy"]]);
      put(c, codebreaker(1), 301, 2.2, 0, 3.6, [[3102, null, "neutral"], [3172, "chin", "scheme"], [3209, "armsUp", "joy"]], { prop: c.f < 3209 ? "paper" : null });
      put(c, codebreaker(2), 302, -1.7, 0, 3.3, [[3102, null, "neutral"], [3209, "clap", "grin"]], { mode: "chair", desk: "type" });
    }
  },
  31: (c) => {
    // "Add radar, long-range planes, and better escorts, and in May 1943 alone..."
    const u = (c.f - 3276) / 158;
    F(c, { key: "c9lib", cw: 600, ch: 200, draw: fxBomber, x: -120 + 150 * u, y: 34, z: 130, w: 24, h: 8 });
    [3354, 3364, 3374, 3390].forEach((f0, k) => splash(c, -28 + k * 10, -0.25, 92 + (k % 2) * 6, 12, f0, 34));
    fog(c, 3, -60, 20, 3, 120, 200, 40, "#a8b0b8", 0.25);
  },
  32: (c) => {
    // "...the Germans lose forty-one U-boats."
    const n = Math.max(0, Math.min(41, Math.floor((c.f - 3453) / 1.0)));
    F(c, { key: `c9ub${n}`, cw: 1000, ch: 600, draw: (p) => chalk(p.g, "U-BOATS SUNK · MAY 1943", n, true), x: 3.08, y: 1.66, z: 0.6, w: 1.7, h: 1.02, glow: 0.9 });
    put(c, codebreaker(0), 300, 2.3, 0, 1.6, [[3434, null, "scheme"], [3476, "cheer", "joy"]], { facing: 1 });
    put(c, codebreaker(3), 303, 1.9, 0, 2.6, [[3434, "chin", "neutral"], [3494, "clap", "laugh"]], { facing: 1 });
  },
  33: (c) => {
    // "They call it Black May."
    stamp(c.out, c.t, at(3532), "BLACK MAY", ...c.O(-37, 4.2, 18), 9);
    fog(c, 3, -40, 0, 0.5, 30, 50, 20, "#7a8288", 0.35);
  },
  34: (c) => {
    // "In the summer of 1943, Germany tries one last big attack in the East, at Kursk."
    for (let i = 0; i < 8; i++) {
      const z = 52 - (c.f - 3567) * 0.03 + rnd(i) * 10, x = -16 + i * 4.5 + rnd(i, 2) * 2;
      put(c, german(i + 10), 320 + i, x, 0.2, z, [[3567, null, "determined"]], { mode: "march", phase: q((c.t * 1.4 + rnd(i, 3)) % 1, 30) });
    }
  },
  35: (c) => {
    // "It turns into one of the largest tank battles in history."
    [3756, 3772, 3790, 3806, 3815, 3830].forEach((f0, k) => boom(c, -12 + k * 6, 0.5, 42 + (k % 3) * 9, 7, f0, 28, 1.7));
    for (let k = 0; k < 10; k++) burst(c, -20 + k * 5, 2.2, 60 + (k % 3) * 20, 2.5, 3750 + k * 9, 5, "#ffd27a", 2.6);
  },
  36: (c) => {
    // "And the Soviets are ready for it with mines, trenches, and guns stretching back for miles."
    const zz = (x: number) => 1.2 * Math.sin(x * 0.12);
    for (let i = 0; i < 9; i++) {
      const x = -13 + i * 2.6;
      put(c, soviet(i + 2), 340 + i, x, -1.25, zz(x) + 0.2, [[3849, null, i % 2 ? "determined" : "grim"], [3904 + i * 2, i % 3 === 0 ? "point" : null, "determined"]], { prop: i % 3 === 1 ? "ppsh" : null });
    }
    [[-12, 2.8], [6, 2.8]].forEach(([gx, gz], k) => {
      put(c, soviet(20 + k), 360 + k, gx - 0.8, 0.0, gz - 1.0 + 1.2 * Math.sin(gx * 0.12), [[3849, null, "determined"]], { mode: "kneel" });
      put(c, soviet(22 + k), 362 + k, gx + 0.9, 0.0, gz - 1.2 + 1.2 * Math.sin(gx * 0.12), [[3849, "point", "yell"]], { mode: "stand" });
    });
  },
  37: (c) => {
    // "The attack fails."
    put(c, german(20), 370, 9.6, 1.25, 24.2, [[4020, "armsUp", "panic"]], {}, 1);
    const u = smooth((c.f - 4031) / 40);
    put(c, german(21), 371, 11 + 4 * u, 0, 22.6, [[4020, "head", "fear"]], { mode: "run", phase: q((c.t * 2.4) % 1, 30) });
    put(c, german(22), 372, 6.0, 0, 22.4, [[4020, null, "dazed"], [4044, "head", "exhausted"]], { mode: "kneel" });
  },
  38: (c) => {
    // "From now on, the Soviets do the attacking."
    for (let i = 0; i < 9; i++) {
      const z = -22 + (c.f - 4074) * 0.09 + rnd(i) * 3, x = 55 + i * 1.4 + rnd(i, 2);
      put(c, soviet(i + 30), 380 + i, x, 0, z, [[4074, null, i % 2 ? "yell" : "determined"]], { mode: "run", phase: q((c.t * 2.2 + rnd(i, 3)) % 1, 30), prop: i === 4 ? ["flag", "su"] : i % 3 === 0 ? "ppsh" : null, flutter: q((c.t * 1.5) % 1, 20) });
    }
  },
  39: (c) => {
    // "That same summer, the Allies land on the Italian island of Sicily."
    for (let i = 0; i < 11; i++) {
      const lane = [-8, 0, 9][i % 3], f0 = 4152 + Math.floor(i / 3) * 18, u = Math.max(0, (c.f - f0) / 90);
      const z = 9.5 - 7 * u + (i % 2) * 0.4, x = lane + ((i % 4) - 1.5) * 0.6;
      put(c, i % 4 === 3 ? tommy(i) : gi(i), 400 + i, x, 0.6 - 0.07 * z, z, [[4152, null, "determined"], [4200, null, i % 2 ? "yell" : "determined"]], { mode: "run", phase: q((c.t * 2 + rnd(i, 3)) % 1, 30) });
    }
    fog(c, 3, -20, 20, 1.0, 20, 40, 20, "#c8c0b0", 0.3);
  },
  40: (c) => {
    // "Within weeks, Mussolini's own party votes against him, and the King of Italy has him arrested."
    const u = smooth((c.f - 4300) / 90), z = 10.4 - 3.6 * u, y = 1.6 * clamp01((z - 8.4) / 2.0);
    put(c, [MUSSOLINI, "duce"], 7, 200, y, z, [[4266, "hips", "proud"], [4334, "palms", "shock"], [4404, "head", "panic"]], { mode: u > 0 && u < 1 ? "march" : "stand", phase: q((c.t * 1.6) % 1, 30) });
    for (const sd of [-1, 1]) put(c, officer("it", 3 + sd), 410 + sd, 200 + sd * 0.85, y, z + 0.2, [[4266, null, "stern"]], { mode: u > 0 && u < 1 ? "march" : "stand", phase: q((c.t * 1.6 + 0.5) % 1, 30) });
    put(c, KING, 8, 196.6, 1.6, 10.4, [[4266, "cross", "stern"], [4370, "point", "smug"], [4404, "hips", "smug"]], { facing: 1 }, 0.84);
  },
  41: (c) => {
    // "Italy switches sides."
    const u = smooth((c.f - 4433) / 26);
    put(c, italian(2), 420, -1.0 + 2.1 * u, 0.42, 2.5, [[4428, null, "nervous"], [4442, null, "grin"], [4457, "hug", "joy"]], { mode: u > 0 && u < 1 ? "march" : "stand", phase: q((c.t * 2) % 1, 30) });
    put(c, german(3), 421, -2.3, 0.42, 2.6, [[4428, "cross", "smug"], [4445, "palms", "shock"], [4460, "fists", "furious"]]);
    put(c, gi(4), 422, 2.3, 0.42, 2.4, [[4428, "hips", "neutral"], [4457, "hug", "grin"]]);
  },
  42: (c) => {
    // "But German troops pour into Italy and fight for every mountain... climbing up the country one hill at a time."
    const path = (z: number): [number, number] => [-300 + 3 * Math.sin(z * 0.25), Math.max(0, 0.28 * z)];
    for (let i = 0; i < 7; i++) {
      const z = 2 + i * 3.4 + (c.f - 4480) * 0.012, [x, y] = path(z);
      put(c, i % 3 === 1 ? tommy(i + 3) : gi(i + 6), 430 + i, x + ((i % 2) - 0.5) * 0.6, y, z, [[4480, i % 3 ? "collar" : null, "exhausted"], [4653, null, i % 2 ? "exhausted" : "determined"]], { mode: "march", phase: q((c.t * 0.8 + rnd(i, 3)) % 1, 30), lift: 70, tilt: 8 });
    }
    for (let i = 0; i < 2; i++) { const z = 54 + i * 3, [x, y] = path(z); put(c, german(i + 25), 440 + i, x + 1.2, y, z, [[4480, null, "determined"]], { mode: "kneel" }); }
  },
  43: (c) => {
    // "Oh, and that same summer, thirty-five thousand American and Canadian soldiers invaded a Japanese-held island near Alaska."
    for (let i = 0; i < 6; i++) {
      const z = -7 + (c.f - 4734) * 0.022 + i * 1.6 - (i % 2) * 0.8, x = 0.3 * Math.sin(z * 0.3) + ((i % 3) - 1) * 1.3;
      put(c, i % 2 ? tommy(i + 9) : gi(i + 9), 450 + i, x, 0, z, [[4734, null, i % 3 ? "nervous" : "fear"], [4880, null, "dread"]], { mode: i % 3 === 2 ? "crouch" : "march", phase: q((c.t * 0.9 + rnd(i, 3)) % 1, 30), lift: 25 });
    }
    fog(c, 10, -14, 14, 0.3, 0, 40, 12, "#e8eef0", 0.55);
  },
  44: (c) => {
    // "The Japanese had already left."
    const wag = c.f > 4975 ? q(0.5 + 0.5 * Math.sin(c.t * 14), 6) : 0.5;
    prop(c, `c9dog${wag}${c.f > 4975 ? "h" : "a"}`, (p) => dogSit(p, { coat: "#b8864a", patch: "#f2e6d0", ear: "#6a4224", expr: c.f > 4975 ? "happy" : "alert", wag }), 100.4, 0, 3.2, 0.48);
    put(c, gi(13), 460, 99.0, 0, -0.6, [[4948, null, "fear"], [4980, null, "shock"]], { mode: "crouch" });
  },
  45: (c) => {
    // "But that's a story for another video."
    const u = smooth((c.f - 5020) / 50), wag = q(0.5 + 0.5 * Math.sin(c.t * 14), 6);
    prop(c, `c9dogo${wag}`, (p) => dogSit(p, { coat: "#b8864a", patch: "#f2e6d0", ear: "#6a4224", expr: "happy", wag }), 0.3 - 0.6 * u, 0, 23.4 - 2.8 * u, 0.48);
    put(c, gi(13), 460, -1.6, 0, 19.6, [[5012, "shrug", "relief_open"], [5043, "head", "laugh"]]);
    put(c, tommy(10), 461, 1.8, 0, 19.3, [[5012, "palms", "dazed"], [5052, "shrug", "smile"]]);
    put(c, gi(14), 462, -3.1, 0, 18.2, [[5012, null, "relief"]], { mode: "kneel" });
    fog(c, 6, -10, 10, 0.4, 24, 34, 10, "#e8eef0", 0.5);
  },
};

export const CH = makeChapter({
  total: TOTAL, shots: SHOTS, xfade: XFADE,
  cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER 9", "THE TURN", "1942 – 1943"] }],
  cams: CAMS, dof: DOF, kicks: KICKS, stage: STAGE,
});
export type { V3 };
