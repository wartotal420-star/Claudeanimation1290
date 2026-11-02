// Chapter 6: The Biggest Invasion in History (1941). Voice ~/ww2/voice/ch06.wav (138.73 s, 4162 frames), word frames
// from ch06_words.json. Sets (layouts at the top of each ~/ww2/blender/sets/<set>.py): c05_berghof (the torn photo,
// Hitler's failure, the globe), c06_kremlin (Stalin ignores the warnings, the Eastern Front map), c06_border (dawn 22 June,
// the airfield), c06_steppe (tank column, prisoners near Kyiv), c06_leningrad (the siege: street + apartment),
// c06_ladoga (the Road of Life), c06_hall (the Seventh Symphony + loudspeakers), c06_road (mud, winter, Siberians).
// Leningrad's starvation is told seriously: slow shots, no gags, sorrowful faces.
import { makeChapter } from "../chapter";
import type { ChShot } from "../chapter";
import { D, Tr } from "../story";
import type { Key, Dof } from "../story";
import { P, F, W_, act, talk, toward, q, stamp, MEN, WOMEN, WORKERS } from "../cast";
import type { Ctx, Beat } from "../cast";
import { HITLER_WAR, STALIN, STALIN_COAT, ZHUKOV, soviet, winter, german, officer, refugee, evacuee, pilot, tommy } from "../cast";
import { bodyFront, fxBoom } from "../toon";
import type { Outfit, Expr, Pose, FrontOpts, Pen } from "../toon";

const TOTAL = 4162;
const at = (f: number) => f / 30;
const S = (id: number, a: number, b: number, set: string, light: ChShot["light"], night = false): ChShot => ({ id, a, b, set, light, night });
const BG = "c05_berghof", KR = "c06_kremlin", BD = "c06_border", ST = "c06_steppe", LN = "c06_leningrad", LD = "c06_ladoga", HL = "c06_hall", RD = "c06_road";
const SHOTS: ChShot[] = [
  S(1, 0, 124, BG, "interior"), S(2, 124, 167, BG, "interior"), S(3, 167, 244, BD, "dusk"), S(4, 244, 306, BD, "dusk"), S(5, 306, 441, KR, "interior"),
  S(6, 441, 602, ST, "day"), S(7, 602, 666, KR, "interior"), S(8, 666, 831, KR, "interior"), S(9, 831, 884, KR, "interior"), S(10, 884, 959, BD, "dusk"),
  S(11, 959, 1133, BD, "dusk"), S(12, 1133, 1182, ST, "day"), S(13, 1182, 1343, ST, "day"), S(14, 1343, 1503, LN, "grey"), S(15, 1503, 1602, KR, "interior"),
  S(16, 1602, 1722, LN, "interior"), S(17, 1722, 1814, LN, "interior"), S(18, 1814, 1937, LN, "interior"), S(19, 1937, 2050, LN, "grey"),
  S(20, 2050, 2134, LD, "night", true), S(21, 2134, 2264, LD, "night", true), S(22, 2264, 2340, LD, "night", true), S(23, 2340, 2483, HL, "interior"),
  S(24, 2483, 2682, HL, "interior"), S(25, 2682, 2776, HL, "golden"), S(26, 2776, 2816, HL, "interior"), S(27, 2816, 2964, LN, "interior"),
  S(28, 2964, 3020, LN, "grey"), S(29, 3020, 3141, KR, "interior"), S(30, 3141, 3217, KR, "interior"), S(31, 3217, 3332, RD, "grey"),
  S(32, 3332, 3370, RD, "fog"), S(33, 3370, 3495, RD, "fog"), S(34, 3495, 3572, RD, "fog"), S(35, 3572, 3608, RD, "fog"), S(36, 3608, 3618, RD, "fog"),
  S(37, 3618, 3660, RD, "fog"), S(38, 3660, 3833, RD, "fog"), S(39, 3833, 3897, RD, "fog"), S(40, 3897, 4008, BG, "interior"), S(41, 4008, TOTAL, BG, "interior"),
];
const XFADE: Record<number, number> = { 3: 10, 6: 8, 14: 12, 16: 10, 19: 12, 20: 12, 23: 12, 27: 14, 28: 10, 29: 8, 31: 8, 32: 8, 40: 10, 41: 10 };

// ---------------- cameras ----------------
type V3 = [number, number, number];
const k1 = (f0: number, set: string, pos: V3, look: V3, fov = 42, rate = 0.002, roll = 0, punch = 0): Key => ({ f: f0, s: (f) => D(set, pos, look, f, f0, rate, { fov, roll }, punch) });
const tr = (f0: number, set: string, pos: V3, look: V3, v: V3, fov = 42, roll = 0): Key => ({ f: f0, s: (f) => Tr(set, pos, look, f, f0, v, { fov, roll }) });
const gl = (k: Key, dur: number): Key => ({ ...k, dur });
// map on the Kremlin wall: lon 6..66 -> x 2.4..-2.4, lat 68..36 -> y 4.1..0.9, z 7.8
const MAPP = (lon: number, lat: number, z = 7.8): V3 => [2.4 - (lon - 6) / 12.5, 4.1 - (68 - lat) / 10, z];
const LENI = MAPP(30.3, 59.9), MOSC = MAPP(37.6, 55.75);
const CAMS: Record<number, Key[]> = {
  1: [k1(0, BG, [3.5, 1.6, 0.0], [7.85, 1.8, 1.4], 48, 0.002), gl(k1(70, BG, [5.0, 1.65, 0.6], [7.85, 1.85, 1.4], 42, 0.0025), 40)],
  2: [k1(124, BG, [5.9, 1.75, 1.15], [7.85, 1.95, 1.45], 38, 0.004, 0.03, 0.009)],
  3: [k1(163, BD, [7.0, 1.0, 11.5], [2.5, 1.5, 26], 48, 0.0018, 0.02)],
  4: [k1(244, BD, [6.2, 1.3, 8.0], [1.0, 1.7, 30], 50, 0.002, -0.03), gl(k1(280, BD, [5.4, 0.8, 12.5], [0.5, 2.4, 24], 46, 0.003, 0.04, 0.008), 12)],
  5: [k1(302, KR, [0, 2.5, 3.6], [0, 2.5, 7.8], 54, 0.002), gl(k1(380, KR, [0.2, 2.8, 5.4], [0.3, 2.8, 7.8], 46, 0.003), 40)],
  6: [k1(441, ST, [9, 4.5, -10], [-2, 1.2, 40], 50, 0.0015), gl(k1(530, ST, [6, 1.2, -4], [0, 2.2, 30], 48, 0.002, 0.03), 40)],
  7: [k1(602, KR, [3.2, 1.4, 1.6], [3.6, 1.35, 4.3], 42, 0.003, 0, 0.007)],
  8: [k1(666, KR, [2.0, 1.55, 0.4], [2.8, 1.3, 3.9], 50, 0.0018)],
  9: [k1(831, KR, [3.35, 1.55, 2.5], [3.6, 1.5, 4.3], 36, 0.003, -0.03, 0.008)],
  10: [k1(880, BD, [-4.5, 1.4, 3.5], [0, 1.6, 24], 50, 0.002)],
  11: [k1(959, BD, [124, 1.5, -7], [128, 4, 30], 56, 0.0015), gl(k1(1060, BD, [121, 1.3, -1], [124, 1.6, 12], 46, 0.003), 30)],
  12: [k1(1133, ST, [-0.5, 1.5, 1.0], [-5, 1.3, 12], 48, 0.002)],
  13: [k1(1182, ST, [-1.2, 1.7, -2.5], [-5, 1.3, 20], 46, 0.0015), gl(k1(1270, ST, [-2.5, 1.5, 0.5], [-5.2, 1.4, 10], 40, 0.002), 40)],
  14: [k1(1339, LN, [0.5, 2.1, -6], [1.5, 3.2, 40], 54, 0.0012)],
  15: [k1(1503, KR, [0.3, 3.15, 5.6], [LENI[0], LENI[1], 7.8], 42, 0.003)],
  16: [k1(1598, LN, [43.0, 1.35, 1.4], [43, 0.95, 3.8], 46, 0.0016)],
  17: [k1(1722, LN, [43.05, 1.2, 2.95], [43.0, 0.8, 3.62], 32, 0.0015)],
  18: [k1(1814, LN, [42.6, 1.3, 0.4], [41.2, 0.95, 2.2], 44, 0.002), gl(k1(1860, LN, [43.4, 1.45, 2.3], [41.6, 1.3, 4.7], 44, 0.002), 30)],
  19: [k1(1933, LN, [-0.5, 1.4, 2.0], [-1.5, 1.0, 16], 44, 0.0008)],
  20: [k1(2046, LD, [9, 2.6, -12], [0, 1, 40], 50, 0.0012)],
  21: [k1(2134, LD, [5.6, 1.35, -1.5], [0, 1.4, 12], 48, 0.0018)],
  22: [k1(2264, LD, [4.5, 1.6, 4.4], [5.4, 1.7, 6.45], 40, 0.003)],
  23: [k1(2336, HL, [0, 2.0, -7], [0, 2.2, 6], 52, 0.0012)],
  24: [k1(2483, HL, [2.4, 2.6, 10.5], [0, 2.0, 2.5], 46, 0.0015), gl(k1(2600, HL, [-1.8, 2.1, 0.0], [-1.5, 2.0, 4.5], 40, 0.002), 40)],
  25: [k1(2678, HL, [63.2, 1.3, 8.2], [66.5, 4.3, 14], 52, 0.0018, 0.03)],
  26: [k1(2776, HL, [0, 2.0, 2.6], [0, 1.4, -6], 50, 0.0025)],
  27: [k1(2812, LN, [43.6, 1.25, 1.8], [43.2, 0.9, 3.8], 40, 0.0008)],
  28: [k1(2964, LN, [-0.3, 1.0, 6.0], [-1.6, 1.7, 13], 40, 0.0025, 0.03)],
  29: [k1(3016, KR, [0.0, 2.6, 4.2], [0, 2.6, 7.8], 52, 0.002), gl(k1(3080, KR, [MOSC[0], MOSC[1], 6.0], [MOSC[0], MOSC[1], 7.8], 38, 0.003), 40)],
  30: [k1(3141, KR, [5.0, 1.5, 1.2], [6.2, 1.5, 3.4], 42, 0.0025)],
  31: [k1(3213, RD, [3.8, 1.5, 7.5], [-0.5, 1.0, 22], 48, 0.0018)],
  32: [k1(3332, RD, [1.0, 1.7, -4], [0, 2.2, 30], 54, 0.002)],
  33: [k1(3370, RD, [-0.6, 1.5, 3.4], [0.6, 1.5, 6.0], 40, 0.0025)],
  34: [k1(3495, RD, [3.05, 1.6, 3.15], [3.2, 1.6, 4.1], 30, 0.003, 0, 0.008)],
  35: [k1(3572, RD, [0.6, 1.7, 19.4], [-2.0, 1.7, 25.5], 40, 0.004, 0.03, 0.01)],
  36: [k1(3608, RD, [-2.75, 1.0, 4.9], [-3.6, 0.7, 6.4], 40, 0.004, -0.03)],
  37: [k1(3618, RD, [-2.4, 1.55, 5.5], [-3.0, 1.55, 7.6], 36, 0.004, 0, 0.01)],
  38: [k1(3660, RD, [0.4, 0.9, 6], [0, 2.0, 40], 54, 0.0015), gl(k1(3780, RD, [0.6, 1.4, 14], [0.4, 1.5, 21], 40, 0.003), 24)],
  39: [k1(3833, RD, [0, 1.5, 4.5], [0, 1.5, 20], 50, 0.0015)],
  40: [k1(3893, BG, [0.5, 1.6, 7.2], [0, 1.55, 4.9], 38, 0.003, 0, 0.008)],
  41: [k1(4008, BG, [-3.9, 1.7, 4.4], [-5.2, 1.45, 6.6], 44, 0.003)],
};
const DOF: Dof[] = [
  { f: 0, cInf: 8 }, { f: 124, cInf: 13 }, { f: 167, cInf: 5 }, { f: 306, cInf: 6 }, { f: 380, dur: 40, cInf: 10 }, { f: 441, cInf: 2 }, { f: 602, cInf: 11 },
  { f: 666, cInf: 8 }, { f: 831, cInf: 13 }, { f: 884, cInf: 5 }, { f: 959, cInf: 3 }, { f: 1133, cInf: 6 }, { f: 1182, cInf: 5 }, { f: 1343, cInf: 3 },
  { f: 1503, cInf: 10 }, { f: 1602, cInf: 10 }, { f: 1722, cInf: 15 }, { f: 1814, cInf: 10 }, { f: 1937, cInf: 6 }, { f: 2050, cInf: 2 }, { f: 2134, cInf: 5 },
  { f: 2264, cInf: 10 }, { f: 2340, cInf: 3 }, { f: 2483, cInf: 8 }, { f: 2682, cInf: 5 }, { f: 2776, cInf: 6 }, { f: 2816, cInf: 11 }, { f: 2964, cInf: 9 },
  { f: 3020, cInf: 6 }, { f: 3141, cInf: 9 }, { f: 3217, cInf: 5 }, { f: 3332, cInf: 3 }, { f: 3370, cInf: 11 }, { f: 3495, cInf: 15 }, { f: 3572, cInf: 11 },
  { f: 3608, cInf: 12 }, { f: 3618, cInf: 13 }, { f: 3660, cInf: 4 }, { f: 3833, cInf: 5 }, { f: 3897, cInf: 13 }, { f: 4008, cInf: 10 },
];
const KICKS: [number, number][] = [[at(136), 0.4], [at(258), 0.7], [at(343), 0.4], [at(1054), 0.6], [at(1599), 0.3], [at(3599), 0.3], [at(3614), 0.3], [at(3639), 0.3],
  [at(3705), 0.5], [at(3960), 0.6]];

// ---------------- helpers ----------------
type Who = [Outfit, string];
const fo = (o: Partial<FrontOpts>): FrontOpts => ({ mode: "stand", ...o });
const actor = (c: Ctx, w: Who, i: number, x: number, y: number, z: number, beats: Beat[], extra: Partial<FrontOpts> = {}, sc = 1, talkOn?: [number, number][]) => {
  const a = act(c.t, beats, 0.18); let expr = a.expr;
  if (talkOn) for (const [f0, f1] of talkOn) if (c.f >= f0 && c.f < f1) expr = talk(c.t, a.expr, "shout");
  P(c, W_(w[0], i, w[1]), x, y, z, fo({ expr, pose: a.pose, pk: a.pk, ...extra }), sc);
};
const HI: Who = [HITLER_WAR, "hitlerw"], SL: Who = [STALIN, "stalin"], ZH: Who = [ZHUKOV, "zhukov"];
/** the Hitler-Stalin handshake photo (800 x 600), torn apart by `tear` 0..1 */
const photo = (tear: number) => (p: Pen) => {
  const g = p.g;
  const pic = (s: number) => {
    g.fillStyle = "#3a2a1a"; g.fillRect(0, 0, 800, 600); g.fillStyle = "#d8c8a4"; g.fillRect(30, 30, 740, 540);
    g.save(); g.translate(150, 70); g.scale(0.5, 0.5); bodyFront(p, HITLER_WAR, { mode: "stand", expr: "grin", pose: "hug", pk: 1, facing: 1, seed: 3 }); g.restore();
    g.save(); g.translate(350, 60); g.scale(0.5, 0.5); bodyFront(p, STALIN, { mode: "stand", expr: "smug", pose: "hug", pk: 1, facing: -1, seed: 5 }); g.restore();
    g.globalCompositeOperation = "multiply"; g.fillStyle = "rgba(190,150,100,0.55)"; g.fillRect(30, 30, 740, 540); g.globalCompositeOperation = "source-over";
    g.fillStyle = "#2a1a10"; g.font = "bold 34px Georgia, serif"; g.textAlign = "center"; g.fillText("MOSCOW, AUGUST 1939", 400, 548); void s;
  };
  const jag: [number, number][] = []; for (let k = 0; k <= 12; k++) jag.push([400 + (k % 2 ? 18 : -18), k * 50]);
  for (const side of [-1, 1]) {
    g.save(); g.beginPath();
    if (side < 0) { g.moveTo(0, 0); jag.forEach(([x, y]) => g.lineTo(x, y)); g.lineTo(0, 600); }
    else { g.moveTo(800, 0); jag.forEach(([x, y]) => g.lineTo(x, y)); g.lineTo(800, 600); }
    g.closePath(); g.translate(side * tear * 70, tear * 30); g.translate(400, 300); g.rotate(side * tear * 0.18); g.translate(-400, -300); g.clip(); pic(side); g.restore();
  }
};
const ringCard = (p: Pen) => { const g = p.g; g.setLineDash([26, 16]); g.lineWidth = 16; g.strokeStyle = "#202020"; g.beginPath(); g.arc(300, 300, 240, 0, Math.PI * 2); g.stroke();
  g.strokeStyle = "#c81e22"; g.lineWidth = 9; g.stroke(); };
const label = (txt: string, bg = "#f2ead6", ink = "#1a1a1a") => (p: Pen) => {
  const g = p.g; g.fillStyle = bg; g.fillRect(10, 10, 580, 180); g.strokeStyle = ink; g.lineWidth = 6; g.strokeRect(20, 20, 560, 160);
  g.fillStyle = ink; g.textAlign = "center"; g.textBaseline = "middle"; g.font = "bold 96px Georgia, serif"; g.fillText(txt, 300, 104);
};

// ---------------- staging ----------------
const s1 = (c: Ctx) => {
  // "Remember that deal between Hitler and Stalin?"
  F(c, { key: "photo0", cw: 800, ch: 600, draw: photo(0), x: 7.84, y: 2.0, z: 1.5, w: 1.1, h: 0.82 });
  actor(c, HI, 1, 6.7, 0, 0.35, [[0, "hips", "smug"], [94, "point", "grin"]], { facing: toward(c, 6.7, 0.35, 7.84, 1.5) });
};
const s2 = (c: Ctx) => {
  // "Hitler never meant to keep it."
  const k = Math.min(1, Math.max(0, (c.f - 136) / 8));
  F(c, { key: `photo${q(k, 10)}`, cw: 800, ch: 600, draw: photo(q(k, 10)), x: 7.84, y: 2.0, z: 1.5, w: 1.1, h: 0.82 });
  actor(c, HI, 1, 6.95, 0, 0.6, [[124, "chin", "scheme"], [136, "fists", "sneer"], [155, "hips", "smug"]], {}, 1, [[124, 165]]);
};
const s3 = (c: Ctx) => {
  // "On the twenty-second of June 1941..." a quiet dawn at the frontier post
  actor(c, soviet(2), 10, 5.4, 0, 17.4, [[167, "head", "neutral"], [197, null, "smile_closed"]], { blink: c.f < 220 ? 1 : 0 });
  actor(c, soviet(5), 11, 2.2, 0, 15.0, [[167, null, "neutral"]], { facing: -1 });
};
const s4 = (c: Ctx) => {
  // "...Germany invades the Soviet Union." tanks roll past the post
  actor(c, soviet(2), 10, 5.4, 0, 17.4, [[244, null, "shock"], [258, "head", "panic"]]);
  actor(c, soviet(5), 11, 3.4, 0, 14.2, [[244, "armsUp", "fear"]], { mode: "run" });
  for (let k = 0; k < 6; k++) { const u = (c.f - 244) * 0.06; P(c, W_(german(k)[0], 20 + k, german(k)[1]), (k % 2 ? -5 : 5) + (k % 3) * 1.2, 0, 34 + k * 3 - u, fo({ mode: "march", phase: q((c.t * 1.8 + k * 0.3) % 1, 40), expr: "grim" })); }
  if (c.f > 260) { const g = Math.min(1, (c.f - 260) / 12); F(c, { key: `boom${q(g, 10)}`, cw: 600, ch: 600, draw: (p) => fxBoom(p, q(g, 10)), x: -30, y: 6, z: 120, w: 26, h: 26, glow: 2.4 }); }
};
const s5 = (c: Ctx) => {
  // "It's called Operation Barbarossa, and it's the largest invasion in history."
  stamp(c.out, c.t, at(343), "OPERATION\nBARBAROSSA", ...c.O(-0.6, 1.5, 7.6), 2.0);
  actor(c, ZH, 30, 2.95, 0, 6.6, [[306, "point", "grim"], [394, "chin", "dread"]], { facing: toward(c, 2.95, 6.6, 0, 7.8) });
};
const s6 = (c: Ctx) => {
  // "More than three million soldiers attack along a front line almost three thousand kilometres long."
  const u = (c.f - 441) / 30;
  for (let i = 0; i < 30; i++) {
    const [o, k] = german(i + 6); const side = i % 2 ? -1 : 1; const row = Math.floor(i / 2);
    P(c, W_(o, 40 + i, k), side * (4.6 + (row % 3) * 0.8), 0, 2 + row * 2.2 - u * 1.2, fo({ mode: "march", phase: q((c.t * 1.9 + (i % 2) * 0.5) % 1, 40), expr: (["grim", "stern", "determined"] as Expr[])[i % 3], lift: 45 }));
  }
};
const desk = (c: Ctx, beats: Beat[], extra: Partial<FrontOpts> = {}, talkOn?: [number, number][]) => actor(c, SL, 2, 3.6, 0, 4.35, beats, extra, 1, talkOn);
const s7 = (c: Ctx) => {
  // "The crazy part? Stalin was warned."
  desk(c, [[602, "cross", "smug"], [645, "chin", "smug"]]);
};
const s8 = (c: Ctx) => {
  // "His spies, the British, and even a German soldier who deserted the night before all told him it was coming."
  desk(c, [[666, "cross", "smug"], [760, "chin", "scheme"], [800, "cross", "stern"]]);
  const vis: [Who, number, number, number][] = [[[MEN[3], "m3"], 674, 2.2, 3.1], [officer("uk", 5), 696, 1.7, 3.9], [german(9), 737, 2.3, 4.6]];
  vis.forEach(([w, f0, x, z], i) => { if (c.f < f0 - 6) return; actor(c, w, 50 + i, x, 0, z, [[f0, "point", i === 2 ? "fear" : "worried"], [f0 + 40, "palms", "nervous"]], { facing: toward(c, x, z, 3.6, 4.35), prop: i === 0 ? null : null }); });
};
const s9 = (c: Ctx) => {
  // "He didn't believe any of them."
  desk(c, [[831, "throw", "smug"], [860, "cross", "sneer"]], { prop: c.f < 845 ? "paper" : null });
};
const s10 = (c: Ctx) => {
  // "The first weeks are a disaster for the Soviets."
  for (let i = 0; i < 5; i++) {
    const [o, k] = soviet(i + 8); const u = Math.max(0, c.f - 884 - i * 4);
    P(c, W_(o, 60 + i, k), 3 - u * 0.14 + i * 0.6, 0, 9 + i * 1.6, fo({ expr: (["fear", "panic", "shock"] as Expr[])[i % 3] }), 1, { so: { mode: "run", phase: q((c.t * 2.4 + i * 0.3) % 1, 30), stride: 1.2 }, mirror: false });
  }
  if (c.f > 900) { const g = Math.min(1, ((c.f - 900) % 30) / 14); F(c, { key: `boom${q(g, 10)}`, cw: 600, ch: 600, draw: (p) => fxBoom(p, q(g, 10)), x: 10, y: 3, z: 40, w: 12, h: 12, glow: 2.4 }); }
};
const s11 = (c: Ctx) => {
  // "On the first day alone, more than a thousand Soviet planes are destroyed, most of them before they even take off."
  actor(c, pilot(2), 70, 126, 0, 6.0, [[959, "head", "shock"], [1054, "head", "panic"]]);
  actor(c, soviet(14), 71, 123.5, 0, 4.5, [[959, "point", "fear"], [1077, "palms", "dread"]], { facing: 1 });
  actor(c, soviet(15), 72, 129, 0, 8.5, [[959, "armsUp", "panic"]], { mode: "run" });
  stamp(c.out, c.t, at(1010), "1,200\nPLANES", ...c.O(132, 6, 26), 3.4);
};
const s12 = (c: Ctx) => {
  // "Whole armies are surrounded."
  for (let i = 0; i < 9; i++) { const [o, k] = soviet(i + 20); P(c, W_(o, 80 + i, k), -6 + (i % 3) * 0.9, 0, 8 + Math.floor(i / 3) * 1.1, fo({ pose: "armsUp", pk: 1, expr: (["dread", "fear", "exhausted"] as Expr[])[i % 3] })); }
  for (let i = 0; i < 4; i++) { const [o, k] = german(i + 40); P(c, W_(o, 95 + i, k), -8.5 + i * 1.6 + (i > 1 ? 2.5 : 0), 0, 6.0 + (i % 2) * 5, fo({ expr: "grim" })); }
};
const s13 = (c: Ctx) => {
  // "In one battle near Kyiv, the Germans capture over six hundred thousand Soviet soldiers."
  const u = (c.f - 1182) / 30;
  for (let i = 0; i < 40; i++) {
    const [o, k] = soviet(i + 30); const z = 4 + i * 1.3 - u * 0.7; if (z < 3) continue;
    P(c, W_(o, 110 + i, k), -5.3 + 0.3 * Math.sin(i * 1.3), 0, z, fo({ mode: "march", phase: q((c.t * 1.2 + i * 0.37) % 1, 40), lift: 25, expr: (["sorrow", "exhausted", "grim", "dread"] as Expr[])[i % 4] }));
  }
  actor(c, german(50), 160, -3.4, 0, 9, [[1182, null, "grim"]]);
  stamp(c.out, c.t, at(1288), "600,000", ...c.O(-9.5, 3.6, 18), 3.0);
};
const s14 = (c: Ctx) => {
  // "In the north, the Germans reach Leningrad, the Soviet Union's second-biggest city."
  const q_: Who[] = [refugee(0), refugee(2), refugee(4), refugee(1), refugee(5), refugee(3)];
  q_.forEach((w, i) => actor(c, w, 170 + i, 6.4 - (i % 2) * 0.4, 0.3, 7 + i * 1.1, [[1343, null, (["sorrow", "exhausted", "grim"] as Expr[])[i % 3]]]));
  actor(c, refugee(6), 177, -1.5, 0.3, 19.0, [[1343, null, "exhausted"]], { mode: "march", phase: q((c.t * 0.8) % 1, 40), lift: 20 });
  actor(c, soviet(40), 178, -4.2, 0.3, 10, [[1343, null, "determined"], [1424, "point", "grim"]], { facing: 1 });
};
const s15 = (c: Ctx) => {
  // "They don't storm it. They surround it and try to starve it to death."
  const k = Math.min(1, Math.max(0, (c.f - 1535) / 20));
  if (k > 0) F(c, { key: `ring${q(k, 10)}`, cw: 600, ch: 600, draw: (p) => { p.g.globalAlpha = q(k, 10); ringCard(p); p.g.globalAlpha = 1; }, x: LENI[0], y: LENI[1], z: 7.76, w: 0.75, h: 0.75 });
  actor(c, ZH, 30, 1.45, 0, 6.9, [[1503, "point", "grim"], [1573, "chin", "dread"]], { facing: toward(c, 1.45, 6.9, LENI[0], 7.8) });
};
const AX = 40;
const s16 = (c: Ctx) => {
  // "At the worst point, people get about one hundred and twenty-five grams of bread a day."
  actor(c, refugee(4), 180, AX + 3.25, 0, 4.45, [[1602, null, "sorrow"], [1693, "pray", "exhausted"]], { mode: "chair" });
  if (c.f > 1690) F(c, { key: "125g", cw: 600, ch: 200, draw: label("125 g"), x: AX + 2.5, y: 1.05, z: 3.7, w: 0.42, h: 0.14 });
};
const s17 = (c: Ctx) => {
  // "That's roughly two slices, and much of it isn't even flour." (close on the ration)
  if (c.f > 1782) F(c, { key: "sawdust", cw: 600, ch: 200, draw: label("+ SAWDUST", "#e8dcc0", "#6a2a1a"), x: AX + 3.25, y: 0.97, z: 3.66, w: 0.26, h: 0.087 });
};
const s18 = (c: Ctx) => {
  // "People boil leather belts and scrape the glue off wallpaper to eat it."
  actor(c, refugee(3), 181, AX + 1.55, 0, 2.6, [[1814, "point", "exhausted"]], { facing: -1 });
  actor(c, refugee(0), 182, AX + 1.9, 0, 4.55, [[1866, "point", "sorrow"]], { facing: toward(c, AX + 1.9, 4.55, AX + 1.2, 5.0) });
};
const s19 = (c: Ctx) => {
  // "In the first winter alone, hundreds of thousands of people starve." the sled, slowly
  const z = 20 - 0.075 * Math.max(0, Math.min(c.f, 2050) - 1937);
  actor(c, refugee(2), 185, -1.5, 0.3, z - 1.75, [[1937, null, "sorrow"]], { mode: "march", phase: q((c.t * 0.7) % 1, 40), lift: 18 });
  actor(c, evacuee(1), 186, -1.5, 0.55, z + 0.15, [[1937, null, "exhausted"]], { mode: "sit" }, 0.7);
};
const s20 = (c: Ctx) => {
  // "The only way in is across a frozen lake."
  actor(c, soviet(44), 190, 5.0, 0, 5.2, [[2050, null, "grim"]], { prop: ["flag", "red"], flutter: q(c.t % 1, 12) });
};
const s21 = (c: Ctx) => {
  // "Trucks drive over the ice at night, bringing in food and taking out children."
  actor(c, soviet(44), 190, 4.4, 0, 6.0, [[2134, null, "determined"], [2196, "wave", "grim"]], { prop: ["flag", "red"], flutter: q(c.t % 1, 12) });
  [evacuee(0), evacuee(2), evacuee(3)].forEach((w, i) => actor(c, w, 191 + i, 5.6 + i * 0.5, 0, 8.5 + i * 0.3, [[2232, "wave", "joy"]], {}, 0.72));
};
const s22 = (c: Ctx) => {
  // "The people call it the Road of Life."
  actor(c, soviet(44), 190, 6.35, 0, 6.2, [[2264, null, "determined"], [2300, "pointUp", "joy"]]);
  stamp(c.out, c.t, at(2300), "THE ROAD\nOF LIFE", ...c.O(4.0, 2.6, 7.4), 1.4);
};
const PLAYERS: [number, number][] = [[0, 1], [0, 3], [0, 5], [0, 7], [1, 0], [1, 2], [1, 4], [1, 6], [2, 1], [2, 3], [2, 5]];
const orchestra = (c: Ctx, play: boolean) => {
  PLAYERS.forEach(([r, k], i) => {
    const x = (k - (8 - r) / 2) * 1.5, z = 3.2 + r * 1.3 + 0.08 * x * x;
    const [o, key] = i % 3 === 0 ? soviet(60 + i) : refugee(i);
    P(c, W_(o, 200 + i, key), x, 1.0, z + 0.05, fo({ mode: "chair", chair: false, expr: play ? (["exhausted", "determined", "grim", "sorrow"] as Expr[])[i % 4] : "exhausted",
      headTilt: play ? q(4 * Math.sin(c.t * 2 + i), 4) : 0 }));
  });
};
const conductor = (c: Ctx, beats: Beat[]) => actor(c, [MEN[0], "m0"], 199, 0, 1.3, 1.9, beats);
const s23 = (c: Ctx) => {
  // "And in the summer of 1942, the city does something incredible."
  orchestra(c, false);
  conductor(c, [[2340, null, "exhausted"], [2405, "pointUp", "determined"]]);
  for (let i = 0; i < 18; i++) { const [o, k] = i % 2 ? refugee(i + 3) : soviet(i + 70); const r = Math.floor(i / 6), col = i % 6;
    P(c, W_(o, 230 + i, k), -6.3 + col * 2.5 + (r % 2) * 0.9, 0, -2.5 - r * 1.15, fo({ mode: "chair", chair: false, expr: (["sorrow", "grim", "determined"] as Expr[])[i % 3] })); }
};
const s24 = (c: Ctx) => {
  // "The surviving musicians, so weak... perform a brand new symphony."
  orchestra(c, c.f > 2627);
  const beat = Math.floor(c.t * 2.2) % 2;
  conductor(c, c.f < 2627 ? [[2483, null, "exhausted"], [2575, "palms", "exhausted"]] : [[2627, beat ? "armsUp" : "pointUp", "determined"]]);
};
const s25 = (c: Ctx) => {
  // "It's broadcast on loudspeakers, pointed straight at the German lines."
  actor(c, soviet(80), 240, 64.4, 0, 10.6, [[2682, null, "determined"], [2722, "point", "grim"]], { prop: "mic", facing: 1 });
  actor(c, [WORKERS[1], "k1"], 241, 62.9, 0, 11.6, [[2682, "cross", "grim"]]);
};
const s26 = (c: Ctx) => {
  // "The message is simple: we're still here."
  for (let i = 0; i < 18; i++) { const [o, k] = i % 2 ? refugee(i + 3) : soviet(i + 70); const r = Math.floor(i / 6), col = i % 6;
    P(c, W_(o, 230 + i, k), -6.3 + col * 2.5 + (r % 2) * 0.9, 0, -2.5 - r * 1.15, fo({ pose: i % 3 === 0 ? "clap" : "fist", pk: 1, expr: (["determined", "joy", "grim"] as Expr[])[i % 3] })); }
};
const s27 = (c: Ctx) => {
  // "The siege lasts eight hundred and seventy-two days. Around a million people die." (an empty chair, a candle)
  void c;
};
const s28 = (c: Ctx) => {
  // "But Leningrad never falls."
  actor(c, refugee(2), 185, -1.5, 0.3, 9.25, [[2964, null, "sorrow"], [2988, null, "determined"]]);
  actor(c, evacuee(1), 186, -1.5, 0.55, 11.15, [[2964, null, "exhausted"], [3000, null, "determined"]], { mode: "sit" }, 0.7);
  actor(c, soviet(46), 187, -2.6, 0.3, 10.6, [[2964, null, "determined"]], { prop: ["flag", "su"], flutter: q(c.t % 1, 12) });
};
const s29 = (c: Ctx) => {
  // "Meanwhile, in the center, the main German army pushes on toward Moscow."
  actor(c, SL, 2, -2.9, 0, 6.6, [[3020, "chin", "worried"], [3124, "collar", "dread"]], { facing: toward(c, -2.9, 6.6, 0, 7.8) });
};
const s30 = (c: Ctx) => {
  // "But then Russia does what Russia does."
  actor(c, [STALIN_COAT, "stalinc"], 3, 6.2, 0, 3.4, [[3141, "hips", "smug"], [3188, "chin", "scheme"]]);
};
const s31 = (c: Ctx) => {
  // "First comes the autumn rain, which turns every road into mud."
  const pushers: [number, number][] = [[-3.3, 23.8], [-0.8, 23.4], [-2.0, 22.8]];
  pushers.forEach(([x, z], i) => actor(c, german(i + 60), 250 + i, x, -0.25, z, [[3217, "palms", "pained"], [3312, "head", "exhausted"]]));
  actor(c, german(64), 254, 2.6, -0.2, 13.5, [[3217, "head", "dread"]]);
};
const s32 = (c: Ctx) => { actor(c, german(65), 255, 0.6, 0, 8, [[3332, "cross", "fear"]]); };
const s33 = (c: Ctx) => {
  // "The Germans planned to win before winter, so most of them don't even have winter coats."
  actor(c, [german(66)[0], german(66)[1]], 256, 0.6, 0, 6.0, [[3370, "cross", "fear"], [3453, "hug", "exhausted"]], { headTilt: q(5 * Math.sin(c.t * 30), 2) });
};
const s34 = (c: Ctx) => { void c; };
const s35 = (c: Ctx) => { void c; };
const s36 = (c: Ctx) => { void c; };
const s37 = (c: Ctx) => {
  // "Soldiers freeze."
  actor(c, german(67), 257, -3.0, 0, 7.6, [[3618, null, "dazed"], [3639, "cross", "shock"]], { blink: 0 });
};
const s38 = (c: Ctx) => {
  // "...the Soviets counterattack with fresh troops from Siberia, who are very much dressed for the weather."
  const u = Math.max(0, c.f - 3700);
  for (let i = 0; i < 12; i++) {
    const [o, k] = winter(i); const z = 44 - u * 0.2 + (i % 3) * 1.2; if (z < 14.5 && i !== 0) continue;
    P(c, W_(o, 270 + i, k), -6 + i * 1.1, 0, Math.max(z, 14.5), fo({ mode: c.f > 3700 ? "run" : "crouch", phase: q((c.t * 2.2 + i * 0.27) % 1, 30), expr: (["determined", "grin", "joy", "grim"] as Expr[])[i % 4],
      prop: i % 3 === 0 ? "ppsh" : null }));
  }
};
const s39 = (c: Ctx) => {
  // "The Germans are pushed back from Moscow."
  for (let i = 0; i < 5; i++) { const [o, k] = german(i + 70); const u = c.f - 3833;
    P(c, W_(o, 290 + i, k), -6 + u * 0.15 + i * 0.9, 0, 18 + (i % 2), fo({ expr: (["panic", "fear"] as Expr[])[i % 2] }), 1, { so: { mode: "run", phase: q((c.t * 2.4 + i * 0.3) % 1, 30), stride: 1.2 }, mirror: true }); }
  for (let i = 0; i < 4; i++) { const [o, k] = winter(i + 20); const u = c.f - 3833;
    P(c, W_(o, 300 + i, k), -11 + u * 0.15 + i * 1.0, 0, 16 + (i % 2), fo({ expr: "determined" }), 1, { so: { mode: "run", phase: q((c.t * 2.4 + i * 0.4) % 1, 30), stride: 1.2 }, mirror: true }); }
};
const s40 = (c: Ctx) => {
  // "For the first time, Hitler's army has failed at something big."
  actor(c, HI, 1, 0, 0, 4.9, [[3897, "fists", "furious"], [3943, "head", "pained"], [3960, "fist", "furious"]], {}, 1, [[3900, 3990]]);
  stamp(c.out, c.t, at(3960), "FAILED", ...c.O(0.9, 2.3, 4.6), 0.9);
};
const s41 = (c: Ctx) => {
  // "And just two days later, on the other side of the world, everything changes again."
  actor(c, HI, 1, -6.3, 0, 7.6, [[4008, "chin", "worried"], [4076, "point", "shock"]], { facing: toward(c, -6.3, 7.6, -5.2, 6.6) });
};
const STAGE: Record<number, (c: Ctx) => void> = { 1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7, 8: s8, 9: s9, 10: s10, 11: s11, 12: s12, 13: s13, 14: s14,
  15: s15, 16: s16, 17: s17, 18: s18, 19: s19, 20: s20, 21: s21, 22: s22, 23: s23, 24: s24, 25: s25, 26: s26, 27: s27, 28: s28, 29: s29, 30: s30, 31: s31,
  32: s32, 33: s33, 34: s34, 35: s35, 36: s36, 37: s37, 38: s38, 39: s39, 40: s40, 41: s41 };
void WOMEN; void tommy;

export const CH = makeChapter({
  total: TOTAL, shots: SHOTS, xfade: XFADE,
  cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER 6", "THE BIGGEST INVASION IN HISTORY", "1941"] }],
  cams: CAMS, dof: DOF, kicks: KICKS, stage: STAGE,
});
