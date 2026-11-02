// Chapter 11 "Closing In" (1944): the Great Escape, the fake army, D-Day and Omaha, Bagration, the July plot, the Warsaw
// uprising, Paris, Arnhem, the Bulge. Voice ~/ww2/voice/ch11.wav (217.4 s, 6522 frames); word frames from ch11_words.json.
// Sets: c11_stalag, c11_maproom, c11_fields, c11_normandy, c11_house, c11_wolfslair, c11_warsaw, c11_paris, c11_ardennes, street.
import { makeChapter } from "../chapter";
import { D, Tr, clamp01, smooth, FPS } from "../story";
import type { Key, Dof, Light, V3 } from "../story";
import {
  P, F, W_, act, talk, at, hh, q, mist, stamp, crowd, gi, german, soviet, polish, french, para, pilot, officer, tommy, SK, WOMEN, MEN, WORKERS,
  EISENHOWER, MONTGOMERY, ROMMEL, STAUFFENBERG, HITLER_WAR, ZHUKOV, STALIN, DEGAULLE,
} from "../cast";
import type { Ctx, Beat } from "../cast";
import { Pen, bodyFront, fxBoom, fxBomber, fxTracer, fxMuzzle, fxStars, fxFlame, INK } from "../toon";
import type { Outfit, Expr, Pose, FrontOpts } from "../toon";

// ---------------------------------------------------------------- helpers
const pk = <T,>(a: T[], i: number) => a[((i % a.length) + a.length) % a.length];
const ph = (t: number, r = 1.6, o = 0) => q((t * r + o) % 1, 60);
/** a figure lying down (rolled card): on a trolley, wounded, asleep */
const lie = (c: Ctx, o: Outfit, key: string, x: number, y: number, z: number, fo: FrontOpts, scale = 1, roll = Math.PI / 2) => {
  const [X, Y, Z] = c.O(x, y, z);
  const opts: FrontOpts = { mode: "stand", seed: 3, ...fo };
  c.out.places.push({ key: `L|${key}|${JSON.stringify(opts)}`, draw: (p) => bodyFront(p, o, opts), x: X, y: Y, z: Z, scale, roll, size: [1080, 1800, 1.8] });
};
const txt = (g: CanvasRenderingContext2D, s: string, x: number, y: number, px: number, col: string, stroke?: string, font = "Georgia, serif") => {
  g.font = `bold ${px}px ${font}`; g.textAlign = "center"; g.textBaseline = "middle";
  if (stroke) { g.lineWidth = px * 0.18; g.strokeStyle = stroke; g.lineJoin = "round"; g.strokeText(s, x, y); }
  g.fillStyle = col; g.fillText(s, x, y);
};
/** speech / radio bubble with a tail, on a 600 x 300 canvas */
const fxBubble = (p: Pen, s: string, col = "#1e1e24") => {
  const g = p.g; g.fillStyle = "#fbf8ef"; g.strokeStyle = INK; g.lineWidth = 10;
  g.beginPath(); g.ellipse(300, 130, 270, 110, 0, 0, Math.PI * 2); g.fill(); g.stroke();
  g.beginPath(); g.moveTo(170, 215); g.lineTo(120, 292); g.lineTo(240, 228); g.closePath(); g.fill(); g.stroke();
  g.fillStyle = "#fbf8ef"; g.fillRect(150, 205, 110, 22);
  let px = 92; g.font = `bold ${px}px Georgia, serif`; while (g.measureText(s).width > 470 && px > 30) { px -= 4; g.font = `bold ${px}px Georgia, serif`; }
  txt(g, s, 300, 132, px, col);
};
const fxQuestion = (p: Pen) => { txt(p.g, "?", 100, 110, 190, "#c8202c", "#fbf8ef"); };
/** sand trickling out of a trouser leg, t = phase, on a 120 x 200 canvas */
const fxSand = (p: Pen, t: number) => {
  for (let i = 0; i < 26; i++) { const u = (i / 26 + t) % 1; p.dot(60 + 14 * Math.sin(i * 2.3) * u, 10 + 175 * u, 4 + 2 * (i % 3), i % 2 ? "#d8c08a" : "#b89a62"); }
  p.ell(60, 190, 46, 9, "#c8ac74", 0);
};
/** parachute with a dangling paratrooper, sway -1..1, on a 300 x 420 canvas */
const fxChute = (p: Pen, sway: number, col = "#e8e2d0") => {
  const g = p.g, cx = 150 + 18 * sway;
  g.save(); g.translate(cx, 120); g.rotate(sway * 0.12);
  p.poly([[-130, 30], [-110, -40], [-60, -80], [0, -92], [60, -80], [110, -40], [130, 30], [80, 18], [40, 26], [0, 18], [-40, 26], [-80, 18]].map(([x, y]) => [x + 150, y + 120]) as [number, number][], col, 7);
  for (const x of [-80, -40, 0, 40, 80]) p.stroke([[150 + x * 0.9, 120 - 70 + Math.abs(x) * 0.25], [150 + x * 0.98, 145]], 3, "rgba(60,50,40,.6)");
  g.restore();
  for (const x of [-120, -60, 0, 60, 120]) p.stroke([[cx + x, 150], [150 + 30 * sway, 300]], 2.5, "#4a4038");
  p.ell(150 + 30 * sway, 300, 16, 16, "#6a6044", 5); p.poly([[136 + 30 * sway, 312], [164 + 30 * sway, 312], [168 + 30 * sway, 370], [132 + 30 * sway, 370]], "#8a7a54", 5);
  p.stroke([[140 + 30 * sway, 370], [136 + 30 * sway, 410]], 9, "#5a4a34"); p.stroke([[160 + 30 * sway, 370], [166 + 30 * sway, 410]], 9, "#5a4a34");
};
/** C-47 Dakota, side-on, nose right, invasion stripes, on a 600 x 200 canvas */
const fxDakota = (p: Pen) => {
  const c = "#4a4e3a";
  p.poly([[30, 100], [90, 84], [470, 80], [540, 92], [575, 104], [540, 116], [470, 120], [90, 114]], c, 5);
  p.poly([[40, 98], [70, 30], [110, 30], [120, 92]], c, 5); p.poly([[60, 104], [140, 110], [140, 120], [50, 110]], c, 4);
  p.poly([[250, 98], [330, 98], [300, 160], [250, 160]], c, 4);
  for (let k = 0; k < 5; k++) p.poly([[180 + k * 18, 82], [190 + k * 18, 82], [190 + k * 18, 118], [180 + k * 18, 118]], k % 2 ? "#1a1a1a" : "#f0ece0", 0);
  p.ell(300, 88, 30, 13, "#3a3e2e", 4); for (let k = 0; k < 6; k++) p.ell(390 + k * 22, 92, 6, 6, "#9ab0c0", 0);
};
/** typed note, on a 400 x 300 canvas */
const fxNuts = (p: Pen) => {
  const g = p.g; p.poly([[14, 14], [386, 8], [392, 290], [10, 292]], "#f4eedc", 6);
  g.fillStyle = "#2a2a30"; g.font = "bold 22px Courier New, monospace"; g.textAlign = "left";
  g.fillText("December 22nd 1944", 40, 52); g.fillText("To the German Commander,", 40, 96);
  txt(g, "NUTS!", 200, 170, 96, "#1e1e24", undefined, "Courier New, monospace");
  g.font = "bold 22px Courier New, monospace"; g.textAlign = "left"; g.fillStyle = "#2a2a30"; g.fillText("The American Commander", 40, 258);
};
const fxZzz = (p: Pen, t: number) => { for (let k = 0; k < 3; k++) { const u = (t + k / 3) % 1; txt(p.g, "Z", 60 + k * 60 + 30 * u, 220 - 160 * u - k * 20, 50 + k * 22, `rgba(40,40,70,${(1 - u).toFixed(2)})`, `rgba(250,248,240,${(1 - u).toFixed(2)})`); } };
const fxLabel = (p: Pen, s: string, px = 54) => {
  const g = p.g; p.poly([[20, 20], [780, 20], [780, 120], [20, 120]], "#fbf3d6", 8); txt(g, s, 400, 72, px, "#8a1e1e");
  p.poly([[380, 120], [420, 120], [400, 196]], "#fbf3d6", 7);
};
const fxDay = (p: Pen, n: number) => { const g = p.g; p.poly([[20, 20], [380, 20], [380, 220], [20, 220]], "#f4ecd8", 9); txt(g, "DAY", 200, 70, 56, "#3a2a1a"); txt(g, String(n), 200, 160, 110, "#c8202c"); };
const fxConfetti = (p: Pen, s: number) => { for (let k = 0; k < 60; k++) { const x = (hh(k, s) * 600), y = hh(k, s + 1) * 400; p.poly([[x, y], [x + 12, y + 3], [x + 10, y + 14], [x - 2, y + 11]], pk(["#c8202c", "#f4f1ea", "#1f3f8f", "#e8c040", "#e86aa8"], k), 0); } };
const fxBubbles = (p: Pen, t: number) => { for (let k = 0; k < 14; k++) { const u = (t + hh(k, 2)) % 1; p.ell(40 + hh(k, 3) * 220, 280 - 260 * u, 6 + 10 * hh(k), 6 + 10 * hh(k), null, 4); } };
const fxTitle = (p: Pen, s: string) => { const g = p.g; txt(g, s, 400, 100, 110, "#f2d24a", "#2a1a10", "Impact, Georgia, serif"); };

// ---- map overlays on the c11_maproom table (lon -9..33, lat 43.5..59; card 1560 x 920 covers the map, rot pi) ----
const MX = (lon: number) => ((lon + 9) / 42) * 1560, MY = (lat: number) => ((59 - lat) / 15.5) * 920;
const mapPos = (lon: number, lat: number): [number, number] => [1.95 - ((lon + 9) / 42) * 3.9, -0.15 + ((lat - 43.5) / 15.5) * 2.3];
const arrow = (p: Pen, pts: [number, number][], k: number, col: string, w = 18, dash = false) => {
  const P_ = pts.map(([lo, la]) => [MX(lo), MY(la)] as [number, number]);
  let L = 0; const seg: number[] = []; for (let i = 1; i < P_.length; i++) { const d = Math.hypot(P_[i][0] - P_[i - 1][0], P_[i][1] - P_[i - 1][1]); seg.push(d); L += d; }
  let rem = L * clamp01(k); const out: [number, number][] = [P_[0]];
  for (let i = 1; i < P_.length && rem > 0; i++) { const f = Math.min(1, rem / seg[i - 1]); out.push([P_[i - 1][0] + (P_[i][0] - P_[i - 1][0]) * f, P_[i - 1][1] + (P_[i][1] - P_[i - 1][1]) * f]); rem -= seg[i - 1]; }
  if (out.length < 2) return;
  const g = p.g; g.lineCap = "round"; g.lineJoin = "round";
  if (dash) g.setLineDash([w * 1.4, w * 1.1]);
  g.strokeStyle = "rgba(20,10,10,.55)"; g.lineWidth = w + 8; g.beginPath(); out.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.stroke();
  g.strokeStyle = col; g.lineWidth = w; g.beginPath(); out.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.stroke(); g.setLineDash([]);
  const [x1, y1] = out[out.length - 1], [x0, y0] = out[out.length - 2], a = Math.atan2(y1 - y0, x1 - x0), hl = w * 2.6;
  p.poly([[x1 + Math.cos(a) * hl * 0.6, y1 + Math.sin(a) * hl * 0.6], [x1 + Math.cos(a + 2.4) * hl, y1 + Math.sin(a + 2.4) * hl], [x1 + Math.cos(a - 2.4) * hl, y1 + Math.sin(a - 2.4) * hl]], col, 5);
};
const mapLabel = (p: Pen, s: string, lon: number, lat: number, px = 26, col = "#8a1e1e") => txt(p.g, s, MX(lon), MY(lat), px, col, "#f6ecd0");
const fxMap = (p: Pen, kind: string, k: number) => {
  if (kind === "invade") {
    arrow(p, [[-1.0, 50.85], [-0.9, 50.1], [-0.6, 49.45]], k, "#2a5ab8", 14); arrow(p, [[-3.0, 50.6], [-1.6, 49.9], [-1.1, 49.45]], k, "#2a5ab8", 14);
  } else if (kind === "calais") {
    arrow(p, [[0.9, 51.4], [1.3, 51.25], [1.75, 51.0]], k, "#c8202c", 16, true); if (k > 0.6) mapLabel(p, "FAKE ARMY", 0.0, 51.75, 30, "#c8202c");
  } else if (kind === "beaches") {
    ([["UTAH", -1.25, 49.5], ["OMAHA", -0.9, 49.55], ["GOLD", -0.55, 49.5], ["JUNO", -0.38, 49.62], ["SWORD", -0.2, 49.5]] as [string, number, number][]).forEach(([s, lo, la], i) => {
      if (k * 5 > i) { mapLabel(p, s, lo, la + (i % 2) * 0.12, 13, "#1e3a8a"); p.dot(MX(lo), MY(la - 0.12), 4, "#c8202c"); } });
  } else if (kind === "bagration") {
    const g = p.g; g.strokeStyle = "rgba(30,30,30,.7)"; g.lineWidth = 6; g.setLineDash([12, 8]); g.beginPath(); g.moveTo(MX(30.5), MY(56.5)); g.quadraticCurveTo(MX(31), MY(53.5), MX(29.5), MY(51.5)); g.stroke(); g.setLineDash([]);
    arrow(p, [[31.5, 54.3], [28.5, 54.0], [25.0, 53.4], [21.6, 52.4]], k, "#c8202c", 34); arrow(p, [[30.5, 52.7], [27.0, 52.4], [23.5, 52.0]], k * 0.9, "#c8202c", 22);
    if (k > 0.05) mapLabel(p, "OPERATION BAGRATION", 27.5, 55.6, 34, "#c8202c");
  } else if (kind === "warsaw") {
    p.ell(MX(21), MY(52.23), 40, 34, null, 6); mapLabel(p, "WARSAW", 21, 52.9, 26, "#8a1e1e");
    const g = p.g; g.strokeStyle = "#c8202c"; g.lineWidth = 8; g.beginPath(); g.moveTo(MX(21.9), MY(51.6)); g.lineTo(MX(21.9), MY(52.9)); g.stroke();
  } else if (kind === "bulge") {
    const g = p.g, cx = MX(6.4), cy = MY(50.4), r = 24 + 70 * k;
    g.fillStyle = "rgba(90,96,88,.75)"; g.strokeStyle = "#2a2a2a"; g.lineWidth = 6;
    g.beginPath(); g.moveTo(MX(6.6), MY(51.2)); g.bezierCurveTo(cx - r * 1.4, cy - r * 0.6, cx - r * 1.2, cy + r * 1.1, MX(6.5), MY(49.6)); g.closePath(); g.fill(); g.stroke();
    if (k > 0.3) mapLabel(p, "THE BULGE", 4.0, 50.9, 30, "#1e1e1e");
    p.dot(MX(5.72), MY(50.0), 8, "#2a5ab8");
  }
};
const mapCard = (c: Ctx, kind: string, k: number) =>
  F(c, { key: `map${kind}${q(k, 24)}`, cw: 1560, ch: 920, draw: (p) => fxMap(p, kind, q(k, 24)), x: 0, y: 0.932, z: 1.0, w: 3.9, h: 2.3, flat: true, rot: Math.PI });

// ---------------------------------------------------------------- cast
const PATTON: Outfit = { ...EISENHOWER, hat: "m1", helmCol: "#4a5040", net: false, jaw: true, build: "tall", medals: 10, nose: "long", brows: "#c8c0b0", tie: "#6a5a3a" };
const raf = (i: number): [Outfit, string] => { const [o] = pilot(i * 4); return [{ ...o, hat: "hair", hair: pk(["#3a2a1a", "#8a6a4a", "#c8a060", "#1e1a18", "#a0502a"], i), tallBoots: false,
  jacket: pk(["#6a4a30", "#5a6a86", "#7a5236", "#56647e", "#6a6a5a"], i), pants: pk(["#4a5468", "#4e5c76", "#5a5a50"], i), scarf: i % 3 === 0 ? "#f4f0e6" : undefined }, `raf${i % 12}`]; };
const civvy = (i: number): [Outfit, string] => [MEN[(i * 5 + 1) % MEN.length], `m${(i * 5 + 1) % MEN.length}`];
const HITLER_TORN: Outfit = { ...HITLER_WAR, shorts: true, socks: "#e8e4da", worn: true, sweat: true, hair: "#2e2218" };
const WIFE = WOMEN[3];
const MCAULIFFE = officer("us", 4);

// HTML-free word frames (round(s * 30)) from ch11_words.json
type Sh = { a: number; b: number; set: string; light: Light; night?: boolean; cam: (a: number, b: number) => Key[]; dof?: number; st?: (c: Ctx) => void };
const DL = (set: string, pos: V3, look: V3, rate = 0.002, fov = 42, roll = 0, punch = 0) => (a: number): Key[] => [{ f: a, s: (f) => D(set, pos, look, f, a, rate, { fov, roll }, punch) }];
const TRK = (set: string, pos: V3, look: V3, v: V3, fov = 42, roll = 0) => (a: number): Key[] => [{ f: a, s: (f) => Tr(set, pos, look, f, a, v, { fov, roll }) }];
const DX = 100, HX = 6, HZ = 55.5;
const RX = -100, BX = -20, BY = 24, BZ = 62;
const fog = (c: Ctx, n: number, x0: number, x1: number, z0: number, z1: number, y = 1.5, w = 14, col = "#e6ecf2", op = 0.5) => {
  for (let i = 0; i < n; i++) mist(c.out, ...c.O(x0 + (x1 - x0) * hh(i, 4), y + (i % 3) * 1.2, z0 + (z1 - z0) * hh(i, 5)), w, c.t, i, col, op);
};
/** Omaha beach height (c11_normandy H without the noise: the draw path and the sand are noise-free) */
const NH = (x: number, z: number) => {
  if (z < 36) return Math.max(-4, 0.04 * z);
  if (z <= 38) return 1.44 + (z - 36) * 0.06;
  const u = clamp01((z - 40) / 32), s = u * u * (3 - 2 * u), dr = Math.exp(-(((x - 5) / 6) ** 2)) * 0.35 + Math.exp(-(((x + 42) / 9) ** 2)) * 0.5;
  return 1.56 + 23 * s * (1 - dr * (1 - u));
};

// ---------------------------------------------------------------- shots
const SH: Sh[] = [];
const add = (s: Sh) => SH.push(s);

// ===== the Great Escape =====
add({ a: 0, b: 248, set: "c11_stalag", light: "grey", dof: 3, cam: (a) => [
  { f: a, s: (f) => D("c11_stalag", [-9, 9.5, -17], [3, 1.2, 26], f, a, 0.0018, { fov: 46 }) },
  { f: 150, dur: 60, s: (f) => D("c11_stalag", [-4, 2.2, -6], [1, 1.2, 8], f, 150, 0.002, { fov: 40 }) }],
  st: (c) => {
    // "In March 1944, in a German prison camp for captured airmen, a group of prisoners has been digging."
    for (let i = 0; i < 8; i++) {
      const [o, k] = raf(i), dir = i % 2 ? 1 : -1, x = -5 + (i % 4) * 3.2 + dir * 0.35 * (c.t - 2), z = 4 + Math.floor(i / 4) * 5 + (i % 3);
      P(c, W_(o, 10 + i, k), x, 0, z, { mode: "stroll", phase: ph(c.t, 1.1, hh(i)), expr: pk(["smile", "scheme", "neutral", "smug", "whistle"] as Expr[], i), facing: dir as -1 | 1, pose: i % 3 === 0 ? "cross" : undefined, pk: 1 });
    }
    for (let i = 0; i < 2; i++) { const [o, k] = german(i * 3 + 1); P(c, W_(o, 20 + i, k), 9 - i * 22, 0, 16 + i * 8, { mode: "stand", expr: i ? "stern" : "whistle", look: 1 }); }
    if (c.f > 150) { const a = act(c.t, [[150, null, "scheme"], [213, "point", "grin"]]); const [o, k] = raf(9); P(c, W_(o, 30, k), 1.6, 0, 6.4, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: "case" }); }
  } });
add({ a: 248, b: 280, set: "c11_stalag", light: "interior", dof: 10, cam: DL("c11_stalag", [-101.7, 1.55, 0.25], [-100, 0.7, 3.5], 0.003, 50),
  st: (c) => {
    // "Not one tunnel."
    const u = smooth((c.t - at(252)) / 0.8);
    for (let s = -1; s <= 1; s += 2) { const [o, k] = raf(s > 0 ? 2 : 5); P(c, W_(o, 40 + s, k), RX + s * 0.75, 0, 3.0 - 0.15 * u, { mode: "stand", expr: u > 0.2 ? "grin" : "scheme", pose: "armsUp", pk: q(0.4 + 0.6 * u, 10), facing: (-s) as -1 | 1 }); }
    const [o, k] = raf(7); P(c, W_(o, 43, k), RX - 2.1, 0, 1.7, { mode: "stand", expr: "nervous", pose: "collar", pk: 1, look: 1 });
  } });
add({ a: 280, b: 312, set: "c11_stalag", light: "grey", dof: 0, cam: DL("c11_stalag", [DX + 20, -2.2, -11], [DX + 20, -4.2, 0], -0.004, 52, 0, 0.0),
  st: (c) => tunnelFolk(c) });
const tunnelFolk = (c: Ctx, shush = false) => {
  ([[DX + 7.2, -3.0, "TOM"], [DX + 14.2, -5.0, "DICK"], [DX + 22.6, -7.4, "HARRY"]] as [number, number, string][]).forEach(([x, y], i) => {
    const [o, k] = raf(i + 1); const a = act(c.t, shush && i === 1 ? [[312, "point", "grin"], [430, "palms", "shock"]] : [[0, i === 0 ? "point" : null, pk(["grin", "scheme", "proud"] as Expr[], i)]]);
    P(c, W_(o, 50 + i, k), x, y, 0.85, { mode: "crouch", expr: a.expr, pose: a.pose, pk: a.pk, facing: 1 }, 0.8);
  });
};
add({ a: 312, b: 473, set: "c11_stalag", light: "grey", dof: 4, cam: TRK("c11_stalag", [DX + 5.0, -1.9, -5.0], [DX + 6.0, -2.4, 0.5], [0.095, -0.028, 0], 46),
  st: (c) => {
    // "They name them Tom, Dick, and Harry, so they never have to say the word "tunnel" out loud."
    tunnelFolk(c, true);
    stamp(c.out, c.t, at(436), "SHHH!", ...c.O(DX + 14.6, -3.2, -0.6), 1.7);
  } });
add({ a: 473, b: 644, set: "c11_stalag", light: "grey", dof: 8, cam: DL("c11_stalag", [-1.6, 0.75, -1.6], [0.4, 0.95, 8], 0.0016, 44),
  st: (c) => {
    // "They hide the sand in little bags inside their trousers and quietly shake it out while walking around the yard."
    for (let i = 0; i < 5; i++) {
      const [o, k] = raf(i + 2), x = -2.6 + i * 1.35 + hh(i) * 0.3, z = 10.5 - 0.5 * (c.t - at(473)) + (i % 2) * 1.5;
      const shake = c.t > at(555) && i % 2 === 0;
      P(c, W_(o, 60 + i, k), x, 0, z, { mode: "stroll", phase: ph(c.t, 0.9, hh(i, 1)), expr: shake ? "whistle" : pk(["smile_closed", "scheme", "neutral"] as Expr[], i), look: shake ? 1 : 0,
        pose: i === 1 ? "hips" : undefined, pk: 1 });
      if (shake) F(c, { key: `sand${q((c.t * 1.5 + i * 0.3) % 1, 8)}`, cw: 120, ch: 200, draw: (p) => fxSand(p, q((c.t * 1.5 + i * 0.3) % 1, 8)), x: x - 0.12, y: 0.2, z: z - 0.05, w: 0.22, h: 0.37 });
    }
    const [g, gk] = german(4); P(c, W_(g, 66, gk), 5.2, 0, 16, { mode: "stand", expr: talk(c.t, "whistle", "neutral") === "whistle" ? "whistle" : "neutral", look: -1, pose: "cross", pk: 1 });
  } });
add({ a: 644, b: 793, set: "c11_stalag", light: "grey", dof: 5, cam: TRK("c11_stalag", [DX + 19.5, -6.25, -3.4], [DX + 20.8, -6.8, 0.9], [0.165, 0, 0], 46),
  st: (c) => {
    // "Harry is over a hundred metres long, with lights, air pumps, and a tiny railway."
    const pump = Math.sin(c.t * 7) > 0;
    const [o, k] = raf(3); P(c, W_(o, 70, k), DX + 20.0, -7.4, 0.95, { mode: "crouch", expr: "exhausted", pose: pump ? "armsUp" : "palms", pk: 1 }, 0.8);
    const u = clamp01((c.t - at(745)) / 1.4);
    const [o2, k2] = raf(4); lie(c, o2, k2, DX + 27.0 + 4.0 * u, -7.4 + 0.3, 0.85, { expr: c.t > at(766) ? "grin" : "neutral", pose: "point", pk: 1 }, 0.62);
    const [o3, k3] = raf(6); P(c, W_(o3, 72, k3), DX + 31.5, -7.4, 0.9, { mode: "kneel", expr: "proud", pose: "point", pk: 1, facing: -1 }, 0.8);
    const [o4, k4] = raf(8); P(c, W_(o4, 73, k4), DX + 44.5, -7.4, 0.9, { mode: "crouch", expr: "smile", pose: "wave", pk: 1 }, 0.8);
  } });
add({ a: 793, b: 895, set: "c11_stalag", light: "night", night: true, dof: 8, cam: DL("c11_stalag", [4.2, 0.55, 51.4], [6.2, 0.35, 56.2], 0.0025, 46),
  st: (c) => {
    // "On a freezing night, seventy-six men crawl through it."
    const up = smooth((c.t - at(800)) / 1.2);
    const [o, k] = raf(5); P(c, W_(o, 80, k), HX, -1.75 + 1.0 * up, HZ, { mode: "stand", expr: "nervous", look: 1, pose: "palms", pk: 0.6 });
    for (let i = 0; i < 3; i++) { const [o2, k2] = raf(i + 6); P(c, W_(o2, 81 + i, k2), HX - 0.8 + i * 0.9, 0, HZ + 1.6 + i * 0.9 + 0.3 * (c.t - at(793)), { mode: "crouch", expr: pk(["fear", "dread", "nervous"] as Expr[], i) }); }
    fog(c, 4, -2, 14, 58, 62, 0.5, 8, "#aab8d0", 0.35);
  } });
add({ a: 895, b: 979, set: "c11_stalag", light: "night", night: true, dof: 3, cam: DL("c11_stalag", [-3.5, 2.6, 50.8], [7, 1.2, 56.5], 0.0015, 50),
  st: (c) => {
    // "But the tunnel comes up a few metres short of the forest..."
    for (let i = 0; i < 3; i++) { const [o, k] = raf(i + 6); P(c, W_(o, 81 + i, k), HX - 0.8 + i * 0.9, 0, HZ + 1.4 + i * 0.5, { mode: "crouch", expr: "dread" }); }
    const k = smooth((c.t - at(944)) / 0.5);
    if (k > 0) F(c, { key: `short${q(k, 10)}`, cw: 800, ch: 200, draw: (p) => fxLabel(p, "A FEW METRES SHORT!", 52), x: HX + 0.2, y: 2.3 + 0.2 * (1 - k), z: HZ + 1.6, w: 3.4 * k, h: 0.85 * k });
  } });
add({ a: 979, b: 1016, set: "c11_stalag", light: "night", night: true, dof: 12, cam: DL("c11_stalag", [11.4, 1.55, 49.6], [13, 1.5, 52.4], 0.004, 40, 0.04, 0.01),
  st: (c) => {
    // "...and a guard spots them."
    const [o, k] = german(2); const a = act(c.t, [[979, null, "neutral"], [991, "point", "shock"]], 0.1);
    P(c, W_(o, 90, k), 13, 0, 52.4, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: -1 });
  } });
add({ a: 1016, b: 1066, set: "c11_stalag", light: "night", night: true, dof: 6, cam: DL("c11_stalag", [6, 1.7, 50.2], [6, 1.2, 57], 0.003, 44),
  st: (c) => {
    // "Almost all of them are caught."
    for (let i = 0; i < 4; i++) { const [o, k] = raf(i + 5); P(c, W_(o, 100 + i, k), HX - 1.5 + i, 0, HZ + 1.8 + (i % 2) * 0.6, { mode: "stand", expr: pk(["fear", "shock", "dread", "sad"] as Expr[], i), pose: "armsUp", pk: 1 }); }
    for (let i = 0; i < 2; i++) { const [o, k] = german(i + 5); P(c, W_(o, 106 + i, k), HX - 2.6 + i * 5.2, 0, HZ + 0.5, { mode: "stand", expr: "angry", pose: "point", pk: 1, facing: (i ? -1 : 1) as -1 | 1 }); }
  } });
add({ a: 1066, b: 1108, set: "c11_wolfslair", light: "day", dof: 12, cam: DL("c11_wolfslair", [0.6, 1.45, -1.9], [0.3, 1.45, 0.05], 0.004, 40, -0.04, 0.01),
  st: (c) => {
    // "Hitler is furious,"
    const a = act(c.t, [[1066, "fist", "furious"], [1086, "fists", "yell"]], 0.1);
    P(c, W_(HITLER_WAR, 110, "hitw"), 0.3, 0, 0.05, { mode: "stand", expr: talk(c.t, a.expr, "furious"), pose: a.pose, pk: a.pk });
  } });
add({ a: 1108, b: 1161, set: "c11_stalag", light: "night", night: true, dof: 4, cam: DL("c11_stalag", [3.5, 1.1, 49.5], [6, 0.3, 56], 0.0012, 40),
  st: (c) => { fog(c, 5, -4, 16, 57, 63, 0.4, 9, "#9aa8c0", 0.4); } });   // "...and fifty of them are shot." (empty, quiet)
add({ a: 1161, b: 1226, set: "c11_stalag", light: "grey", dof: 7, cam: DL("c11_stalag", [-7.5, 1.55, 71], [-7.6, 1.3, 61], 0.002, 42),
  st: (c) => {
    // "Only three make it all the way home."
    for (let i = 0; i < 3; i++) {
      const [o, k] = civvy(i + 2); const z = 62 + 1.0 * (c.t - at(1161)) + (i % 2) * 0.6;
      P(c, W_(o, 120 + i, k), -8.9 + i * 1.3, 0, z, { mode: "stroll", phase: ph(c.t, 1.2, i * 0.3), expr: pk(["joy", "grin", "beam"] as Expr[], i), prop: i === 1 ? null : "case", wave: i === 1 ? q(Math.sin(c.t * 5), 10) : undefined });
    }
  } });
add({ a: 1226, b: 1298, set: "c11_stalag", light: "grey", dof: 2, cam: DL("c11_stalag", [2, 0.6, 38], [9, 4.0, 52], 0.002, 46, 0.03),
  st: (c) => {
    // "It becomes known as the Great Escape."
    const k = smooth((c.t - at(1258)) / 0.35);
    if (k > 0) F(c, { key: `title${q(k, 10)}`, cw: 800, ch: 200, draw: (p) => fxTitle(p, "THE GREAT ESCAPE"), x: 6.5, y: 4.4, z: 46, w: 7 * (1.4 - 0.4 * k), h: 1.75 * (1.4 - 0.4 * k) });
  } });

// ===== the fake army =====
const tableFolk = (c: Ctx, who: [Outfit, string, number, number, Beat[]][]) => who.forEach(([o, k, x, z, b], i) => {
  const a = act(c.t, b); P(c, W_(o, 130 + i, k), x, 0, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: a.pose === "point" ? (x > 0.5 ? -1 : 1) : 0 });
});
add({ a: 1298, b: 1421, set: "c11_maproom", light: "interior", dof: 6, cam: DL("c11_maproom", [0.4, 2.0, -1.1], [0.6, 1.0, 1.5], 0.0022, 44),
  st: (c) => {
    // "That same spring, the Allies are finally ready to invade France."
    tableFolk(c, [[EISENHOWER, "ike", 0.9, 2.95, [[1298, "hips", "grin"], [1384, "point", "determined"]]], [MONTGOMERY, "monty", -0.5, 2.95, [[1298, "cross", "stern"], [1396, "fist", "proud"]]],
      [officer("uk", 1)[0], "ofuk1", 2.7, 1.4, [[1298, "chin", "neutral"]]], [officer("us", 3)[0], "ofus3", -2.7, 0.8, [[1298, null, "neutral"], [1360, "point", "grin"]]]]);
    mapCard(c, "invade", smooth((c.t - at(1384)) / 1.0));
  } });
add({ a: 1421, b: 1465, set: "c11_normandy", light: "interior", dof: 9, cam: DL("c11_normandy", [-18.4, 25.5, 65.6], [-20, 25.1, 61], 0.003, 52),
  st: (c) => {
    // "The Germans know it's coming."
    const [o, k] = officer("de", 5); P(c, W_(o, 140, k), BX - 0.1, BY, BZ + 1.0, { mode: "stand", expr: "grim", prop: "binoc" });
    const [g, gk] = german(7); P(c, W_(g, 141, gk), BX - 1.6, BY, BZ + 2.4, { mode: "stand", expr: "worried", pose: "cross", pk: 1 });
  } });
add({ a: 1465, b: 1510, set: "c11_normandy", light: "interior", dof: 10, cam: DL("c11_normandy", [-19.8, 25.3, 65.8], [-17.6, 25.35, 64.1], 0.003, 46),
  st: (c) => {
    // "They just don't know where."
    const [o, k] = officer("de", 5); P(c, W_(o, 140, k), BX + 1.4, BY, BZ + 2.2, { mode: "stand", expr: "dazed", pose: "shrug", pk: 1 });
    ([[64.18, 25.62], [63.85, 25.33], [63.52, 25.15]] as [number, number][]).forEach(([z, y], i) => {
      const k2 = smooth((c.t - at(1480 + i * 6)) / 0.25);
      if (k2 > 0) F(c, { key: "qm", cw: 200, ch: 220, draw: fxQuestion, x: BX + 2.33, y, z, w: 0.3 * k2, h: 0.33 * k2 });
    });
  } });
add({ a: 1510, b: 1576, set: "c11_fields", light: "day", dof: 7, cam: DL("c11_fields", [-1.8, 1.25, -1.6], [-0.8, 1.0, 7.5], 0.0025, 44),
  st: (c) => {
    // "So the Allies build a fake army."
    const pumping = c.t > at(1512) && c.t < at(1576), down = Math.sin(c.t * 9) > 0;
    const [o, k] = gi(2); P(c, W_(o, 150, k), -3.85, 0, 5.9, { mode: "stand", expr: pumping ? "determined" : "neutral", pose: down ? "palms" : "armsUp", pk: q(down ? 0.6 : 0.9, 10), tilt: down ? 6 : 0 });
    const [o2, k2] = gi(5); P(c, W_(o2, 151, k2), 2.6, 0, 5.2, { mode: "stand", expr: c.t > at(1544) ? "laugh" : "grin", pose: "clap", pk: 1 });
  } });
add({ a: 1576, b: 1621, set: "c11_fields", light: "day", dof: 6, cam: DL("c11_fields", [-4.6, 1.0, 0.2], [-7.4, 1.7, 6.5], 0.003, 46, 0.03),
  st: (c) => {
    // "Inflatable tanks,"
    for (let i = 0; i < 4; i++) { const [o, k] = gi(i + 7); P(c, W_(o, 160 + i, k), -9.0 + i * 1.0, 0, 6.5 + (i % 2 ? 0.6 : -0.6), { mode: "stroll", phase: ph(c.t, 1.0, i * 0.25), expr: pk(["grin", "laugh", "smug", "joy"] as Expr[], i), pose: "armsUp", pk: 1 }); }
  } });
add({ a: 1621, b: 1656, set: "c11_fields", light: "day", dof: 4, cam: DL("c11_fields", [-12, 1.8, 38], [-4, 1.4, 51], 0.003, 46),
  st: (c) => {
    // "fake landing boats,"
    const [o, k] = gi(11); P(c, W_(o, 170, k), -6.0, 0, 44.0, { mode: "stand", expr: "shock", pose: "palms", pk: 1, facing: 1 });
    const [o2, k2] = gi(12); P(c, W_(o2, 171, k2), -8.0, 0, 43.4, { mode: "stand", expr: "laugh", pose: "point", pk: 1, facing: 1 });
  } });
add({ a: 1656, b: 1739, set: "c11_fields", light: "day", dof: 8, cam: DL("c11_fields", [6.0, 1.45, -1.4], [8.6, 1.4, 4.0], 0.0025, 44),
  st: (c) => {
    // "fake radio traffic, and a real, famous general,"
    const [o, k] = gi(13); P(c, W_(o, 180, k), 8.2, 0, 2.6, { mode: "chair", desk: "radio", expr: talk(c.t, "shout", "grin") });
    const msgs = ["TANKS! LOTS!", "MORE TANKS!", "CALAIS, OVER"];
    msgs.forEach((s, i) => { const t0 = at(1662 + i * 22); if (c.t > t0) F(c, { key: `bub${i}`, cw: 600, ch: 300, draw: (p) => fxBubble(p, s), x: 9.4 + i * 0.4 - 0.4, y: 2.3 + i * 0.55, z: 3.2, w: 1.5, h: 0.75 }); });
  } });
add({ a: 1739, b: 1799, set: "c11_fields", light: "day", dof: 10, cam: DL("c11_fields", [-6.6, 0.75, -1.9], [-7.0, 1.75, 1.0], 0.003, 40, -0.03),
  st: (c) => {
    // "George Patton, put in charge of it."
    const a = act(c.t, [[1739, "hips", "proud"], [1768, "point", "determined"]]);
    P(c, W_(PATTON, 190, "patton"), -7.0, 0, 1.0, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: a.pose === "point" ? -1 : 0, prop: "pistol" });
  } });
add({ a: 1799, b: 1911, set: "c11_maproom", light: "interior", dof: 10, cam: DL("c11_maproom", [0.75, 1.75, 0.05], [0.95, 0.93, 0.92], 0.003, 40),
  st: (c) => {
    // "All of it pointing at the narrowest part of the Channel, near Calais."
    mapCard(c, "calais", smooth((c.t - at(1818)) / 1.4));
    P(c, W_(PATTON, 190, "patton"), 1.4, 0, 2.9, { mode: "stand", expr: "smug", pose: "point", pk: 1, facing: 1 });
  } });
add({ a: 1911, b: 1981, set: "c11_normandy", light: "interior", dof: 10, cam: DL("c11_normandy", [-19.9, 25.35, 65.9], [-17.7, 25.3, 64.0], 0.003, 48),
  st: (c) => {
    // "The Germans fall for it completely."
    const a = act(c.t, [[1911, "point", "smug"], [1941, "fists", "laugh"]]);
    const [o, k] = officer("de", 5); P(c, W_(o, 140, k), BX + 1.5, BY, BZ + 2.7, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: 1 });
    const [o2, k2] = officer("de", 8); P(c, W_(o2, 142, k2), BX + 1.3, BY, BZ + 1.1, { mode: "stand", expr: c.t > at(1945) ? "laugh" : "smug", pose: "clap", pk: 1 });
    F(c, { key: "pinC", cw: 200, ch: 220, draw: (p) => { txt(p.g, "!", 100, 110, 180, "#c8202c", "#fbf8ef"); }, x: BX + 2.33, y: 25.62, z: 64.18, w: 0.3, h: 0.33 });
  } });

// ===== D-Day =====
const boatGIs = (c: Ctx, base = 200, expr?: Expr) => {
  for (let i = 0; i < 12; i++) {
    const [o, k] = gi(i + 14), x = 1.9 + (i % 4) * 0.75, z = -33.2 + Math.floor(i / 4) * 2.4;
    P(c, W_(o, base + i, k), x, 0.13, z, { mode: "stand", expr: expr ?? pk(["dread", "fear", "grim", "determined", "pained", "worried"] as Expr[], i), look: Math.round(hh(i, 3) * 2 - 1) });
  }
};
add({ a: 1981, b: 2080, set: "c11_normandy", light: "golden", dof: 0, cam: DL("c11_normandy", [-2, 27, 66], [2, 3, -220], 0.0012, 52),
  st: (c) => { /* "On the sixth of June 1944, D-Day," */ fog(c, 6, -120, 120, -120, -60, 2, 40, "#d8c8c0", 0.35); } });
add({ a: 2080, b: 2174, set: "c11_normandy", light: "golden", dof: 4, cam: DL("c11_normandy", [11.5, 3.8, -39.5], [3, 1.4, -28.5], 0.002, 46),
  st: (c) => { boatGIs(c); } });   // "more than one hundred and fifty thousand Allied soldiers"
add({ a: 2174, b: 2248, set: "c11_maproom", light: "interior", dof: 12, cam: DL("c11_maproom", [1.22, 1.45, 0.25], [1.2, 0.93, 0.74], 0.003, 34),
  st: (c) => { mapCard(c, "beaches", smooth((c.t - at(2186)) / 1.5)); } });   // "land on five beaches in Normandy."
add({ a: 2248, b: 2366, set: "c11_house", light: "interior", dof: 7, cam: DL("c11_house", [0.2, 1.5, -2.3], [0, 1.15, 1.5], 0.002, 46),
  st: (c) => {
    // "Rommel, now in charge of defending the coast, is at home in Germany."
    const a = act(c.t, [[2248, "hips", "proud"], [2329, "wave", "joy"]]);
    P(c, W_(ROMMEL, 220, "rommel"), -0.85, 0, 1.05, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk });
    const b = act(c.t, [[2248, "clap", "beam"]]); P(c, W_(WIFE, 221, "w3"), 0.85, 0, 1.1, { mode: "stand", expr: b.expr, pose: b.pose, pk: b.pk });
  } });
add({ a: 2366, b: 2413, set: "c11_house", light: "interior", dof: 12, cam: DL("c11_house", [0.25, 1.15, 0.05], [0.1, 1.05, 1.8], 0.003, 44, 0.03),
  st: (c) => {
    // "It's his wife's birthday."
    P(c, W_(ROMMEL, 220, "rommel"), -0.85, 0, 1.05, { mode: "stand", expr: talk(c.t, "laugh", "joy"), pose: "cheer", pk: 1 });
    P(c, W_(WIFE, 221, "w3"), 0.85, 0, 1.1, { mode: "stand", expr: "joy", pose: "clap", pk: 1 });
    F(c, { key: "confetti1", cw: 600, ch: 400, draw: (p) => fxConfetti(p, 3), x: 0, y: 1.9 - 0.3 * (c.t - at(2366)), z: 1.4, w: 2.6, h: 1.7, soft: true, opacity: 1 });
  } });
add({ a: 2413, b: 2518, set: "c11_house", light: "interior", dof: 8, cam: DL("c11_house", [40.2, 1.6, -1.3], [40, 1.35, 7.6], 0.002, 46),
  st: (c) => {
    // "And Hitler is asleep, and nobody wants to be the one to wake him up."
    const who: [string, number, Beat[]][] = [["de", 39.25, [[2413, null, "nervous"]]], ["de", 40.05, [[2413, "collar", "dread"], [2465, "point", "nervous"]]], ["de", 40.85, [[2413, "cross", "worried"], [2480, "point", "fear"]]]];
    who.forEach(([kk, x, b], i) => {
      const [o, k] = officer(kk as "de", i + 2); const a = act(c.t, b);
      P(c, W_(o, 230 + i, k), x, 0, 5.6 + (i % 2) * 0.6, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: i === 0 ? "phone" : null, facing: a.pose === "point" ? -1 : 0 });
    });
    F(c, { key: `zzz${q((c.t * 0.6) % 1, 10)}`, cw: 300, ch: 300, draw: (p) => fxZzz(p, q((c.t * 0.6) % 1, 10)), x: 40.0, y: 2.5, z: 8.2, w: 0.9, h: 0.9 });
  } });

// ===== Omaha =====
add({ a: 2518, b: 2634, set: "c11_normandy", light: "golden", dof: 6, cam: (a) => [
  { f: a, s: (f) => D("c11_normandy", [7.5, 1.3, -14.5], [3, 1.9, -28], f, a, 0.002, { fov: 44 }) },
  { f: 2597, cut: true, s: (f) => D("c11_normandy", [4.4, 1.6, -21.5], [3, 1.8, -30], f, 2597, 0.003, { fov: 46, roll: 0.05 }, 0.01) }],
  st: (c) => {
    // "On one beach, codenamed Omaha, things go horribly wrong."
    boatGIs(c, 200, c.t > at(2560) ? undefined : "grim");
    stamp(c.out, c.t, at(2561), "OMAHA", ...c.O(2.6, 3.2, -24.2), 2.6);
    if (c.t > at(2597)) for (let i = 0; i < 5; i++) { const u = (c.t * 2.6 + hh(i)) % 1; F(c, { key: "tracer", cw: 400, ch: 40, draw: fxTracer, x: -2 + 10 * u, y: 2.4 + i * 0.35, z: -24 + i * 0.6, w: 2.2, h: 0.2, rot: -0.1 }); }
  } });
add({ a: 2634, b: 2668, set: "c11_normandy", light: "golden", dof: 2, cam: DL("c11_normandy", [1, 1.8, 6], [0, 18, 90], 0.002, 50),
  st: (c) => {
    // "The bombs miss,"
    for (let i = 0; i < 3; i++) F(c, { key: "bomber", cw: 600, ch: 200, draw: fxBomber, x: -40 + i * 14 + 20 * (c.t - at(2634)), y: 46 + (i % 2) * 6, z: 120 + i * 8, w: 14, h: 4.6 });
    for (let i = 0; i < 4; i++) { const t0 = at(2645 + i * 5), u = clamp01((c.t - t0) / 0.9); if (u > 0 && u < 1) F(c, { key: `boom${q(u, 10)}`, cw: 600, ch: 600, draw: (p) => fxBoom(p, q(u, 10)), x: -30 + i * 20, y: 30, z: 140 + i * 10, w: 22, h: 22, glow: 1.4 }); }
  } });
add({ a: 2668, b: 2697, set: "c11_normandy", light: "golden", dof: 6, cam: DL("c11_normandy", [8.6, 1.0, -22.5], [13, 0.6, -16], 0.003, 42),
  st: (c) => {
    // "the tanks sink,"
    const [o, k] = gi(30); P(c, W_(o, 250, k), 13.0, 0.3 - 0.4 * clamp01((c.t - at(2668)) / 1), -16.2, { mode: "stand", expr: "panic", pose: "armsUp", pk: 1 });
    F(c, { key: `bubbles${q((c.t * 0.8) % 1, 8)}`, cw: 300, ch: 300, draw: (p) => fxBubbles(p, q((c.t * 0.8) % 1, 8)), x: 13.5, y: 0.6, z: -16.5, w: 2.0, h: 2.0, soft: true, opacity: 0.8 });
  } });
add({ a: 2697, b: 2782, set: "c11_normandy", light: "golden", dof: 7, cam: DL("c11_normandy", [1.6, 0.75, 3.6], [2.4, 1.4, 14], 0.0025, 46, -0.03),
  st: (c) => {
    // "and the soldiers are pinned down by machine guns."
    ([[-4.5, 11], [0.5, 9.5], [5.5, 12], [2.5, 17], [-7, 16]] as [number, number][]).forEach(([hx, hz], j) => {
      for (let s = 0; s < 2; s++) { const [o, k] = gi(j * 2 + s + 3); P(c, W_(o, 260 + j * 2 + s, k), hx - 0.4 + s * 0.8, NH(hx, hz - 0.8), hz - 0.8, { mode: "crouch", expr: pk(["fear", "dread", "pained", "grim"] as Expr[], j + s), look: s ? 1 : -1 }); }
    });
    for (let i = 0; i < 7; i++) { const u = (c.t * 2.2 + hh(i, 7)) % 1; F(c, { key: "tracer", cw: 400, ch: 40, draw: fxTracer, x: 6 - 14 * u, y: 1.6 + (i % 3) * 0.5, z: 30 - 18 * u, w: 2.0, h: 0.18, rot: 0.05 }); }
    const m = Math.floor(c.t * 12) % 2; if (m) F(c, { key: "muzzle1", cw: 400, ch: 200, draw: (p) => fxMuzzle(p, 1), x: 9.2, y: NH(9, 66) + 0.9, z: 64.2, w: 1.6, h: 0.8, glow: 2.2 });
    kickNow(c);
  } });
const kickNow = (_c: Ctx) => {};
add({ a: 2782, b: 2888, set: "c11_normandy", light: "golden", dof: 4, cam: DL("c11_normandy", [3.5, 3.2, 31], [5.2, 9, 52], 0.0018, 46),
  st: (c) => {
    // "But slowly, in small groups, they push up the cliffs."
    for (let g = 0; g < 3; g++) for (let s = 0; s < 3; s++) {
      const i = g * 3 + s, z = 40 + g * 5.5 + s * 1.1 + 0.55 * (c.t - at(2782)), x = 4 + s * 0.7 - g * 0.6;
      const [o, k] = gi(i + 40); P(c, W_(o, 280 + i, k), x, NH(x, z), z, { mode: "march", phase: ph(c.t, 1.3, i * 0.17), expr: pk(["determined", "grim", "exhausted"] as Expr[], i), lift: 50, pose: s === 0 && g === 0 ? "point" : undefined, pk: 1 });
    }
  } });
add({ a: 2888, b: 2983, set: "c11_normandy", light: "dusk", dof: 5, cam: DL("c11_normandy", [-7, 2.0, 2.5], [3, 1.6, 17], 0.0018, 46),
  st: (c) => {
    // "By the end of the day, the Allies are in France to stay."
    const [o, k] = gi(50); P(c, W_(o, 300, k), 0.5, NH(0.5, 12), 12, { mode: "stand", expr: "joy", prop: ["flag", "us"], flutter: ph(c.t, 1.4) });
    for (let i = 0; i < 6; i++) { const [o2, k2] = gi(i + 51); const x = -3 + i * 1.3, z = 9 + (i % 3) * 2.2; P(c, W_(o2, 301 + i, k2), x, NH(x, z), z, { mode: i % 3 === 2 ? "sit" : "stand", expr: pk(["exhausted", "joy", "grin", "relief"] as Expr[], i), pose: i % 3 === 0 ? "cheer" : undefined, pk: 1 }); }
  } });

// ===== Bagration =====
add({ a: 2983, b: 3134, set: "c11_warsaw", light: "golden", dof: 5, cam: DL("c11_warsaw", [2.6, 1.0, 1.0], [-0.5, 2.0, -16], -0.0012, 46, 0.03),
  st: (c) => {
    // "And while everyone remembers D-Day, the Soviets launch something even bigger a few weeks later."
    for (let i = 0; i < 4; i++) { const [o, k] = soviet(i); P(c, W_(o, 320 + i, k), -1.2 + (i % 2) * 2.2, 1.75, -13.2 - Math.floor(i / 2) * 1.6, { mode: "sit", expr: pk(["determined", "grin", "grim", "joy"] as Expr[], i), pose: i === 1 ? "point" : undefined, pk: 1 }); }
    for (let i = 0; i < 6; i++) { const [o, k] = soviet(i + 5); const z = -6 + (i % 3) * 2.4 + 0.9 * (c.t - at(2983)); P(c, W_(o, 330 + i, k), (i < 3 ? -3.1 : 3.2), 0, z - 8, { mode: "march", phase: ph(c.t, 1.6, i * 0.2), expr: pk(["determined", "grim", "stern"] as Expr[], i), lift: 60 }); }
  } });
add({ a: 3134, b: 3188, set: "c11_maproom", light: "interior", dof: 12, cam: DL("c11_maproom", [-1.2, 1.85, 0.2], [-1.25, 0.93, 1.3], 0.004, 42, 0, 0.008),
  st: (c) => { mapCard(c, "bagration", smooth((c.t - at(3134)) / 1.6) * 0.4); } });   // "Operation Bagration."
add({ a: 3188, b: 3378, set: "c11_maproom", light: "interior", dof: 8, cam: DL("c11_maproom", [-0.4, 1.8, -0.9], [-1.4, 1.0, 1.4], 0.0018, 46),
  st: (c) => {
    // "In just a few weeks, they destroy almost an entire German army group and push hundreds of kilometres west."
    mapCard(c, "bagration", 0.4 + 0.6 * smooth((c.t - at(3226)) / 4.2));
    const a = act(c.t, [[3188, "hips", "stern"], [3314, "point", "proud"]]);
    P(c, W_(ZHUKOV, 340, "zhukov"), -2.95, 0, 1.6, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: 1 });
    const [o, k] = officer("su", 3); P(c, W_(o, 341, k), -1.6, 0, 3.0, { mode: "stand", expr: c.t > at(3231) ? "grin" : "neutral", pose: "cross", pk: 1 });
  } });
add({ a: 3378, b: 3447, set: "c11_warsaw", light: "golden", dof: 5, cam: DL("c11_warsaw", [-6.5, 1.5, -24], [-7, 1.2, -32], 0.002, 44),
  st: (c) => {
    // "It's one of the worst defeats in German history,"
    for (let i = 0; i < 7; i++) { const [o, k] = german(i + 2); const z = -36 + (i % 4) * 1.1 + 0.6 * (c.t - at(3378)); P(c, W_(o, 350 + i, k), -6.4 + (i % 2) * 1.0 - (i > 3 ? 1.8 : 0), 0, z - (i > 3 ? 2.2 : 0), { mode: "stroll", phase: ph(c.t, 0.9, i * 0.3), expr: pk(["exhausted", "sorrow", "dread", "sad"] as Expr[], i), pose: "armsUp", pk: 0.8 }); }
  } });
add({ a: 3447, b: 3535, set: "c11_normandy", light: "dusk", dof: 10, cam: DL("c11_normandy", [-0.6, 1.5, 6.4], [0.4, 1.4, 10.6], 0.003, 40),
  st: (c) => {
    // "and most people in the West have never even heard of it."
    const a = act(c.t, [[3447, null, "neutral"], [3500, "shrug", "dazed"]]);
    const [o, k] = gi(55); P(c, W_(o, 360, k), 0.4, NH(0.4, 10.6), 10.6, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: a.pose ? null : "news" });
    if (c.t > at(3505)) F(c, { key: "bubBag", cw: 600, ch: 300, draw: (p) => fxBubble(p, "BAGRA-WHAT?"), x: 1.3, y: NH(0.4, 10.6) + 2.55, z: 10.4, w: 1.5, h: 0.75 });
  } });

// ===== the July plot =====
const OX = 100;
add({ a: 3535, b: 3645, set: "c11_wolfslair", light: "day", dof: 8, cam: DL("c11_wolfslair", [OX - 3.6, 1.45, -13], [OX - 1, 1.4, -7], 0.0022, 42),
  st: (c) => {
    // "Inside Germany, some officers realise the war is lost."
    ([[OX - 2.2, -6.8, [[3535, "chin", "worried"], [3604, "palms", "grim"]]], [OX - 1.0, -7.4, [[3535, "cross", "dread"]]], [OX + 0.2, -6.6, [[3535, "collar", "nervous"], [3588, "point", "grim"]]]] as [number, number, Beat[]][]).forEach(([x, z, b], i) => {
      const [o, k] = officer("de", 6 + i); const a = act(c.t, b); P(c, W_(o, 370 + i, k), x, 0, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, look: i === 1 ? Math.round(Math.sin(c.t * 1.3)) : 0, facing: a.pose === "point" ? -1 : 0 });
    });
  } });
add({ a: 3645, b: 3784, set: "c11_wolfslair", light: "day", dof: 6, cam: (a) => [{ f: a, s: (f) => Tr("c11_wolfslair", [OX - 3.0, 1.5, -15.5], [OX + 0.2, 1.4, -8.0], f, a, [0, 0, 0.045], { fov: 42 }) }],
  st: (c) => {
    // "So in July 1944, a colonel named Claus von Stauffenberg walks into a meeting with Hitler carrying a briefcase with a bomb inside."
    const z = -12 + 0.045 * (c.f - 3645) * 1.0;
    P(c, W_(STAUFFENBERG, 380, "stauf"), OX + 0.3, 0, Math.min(1.5, z), { mode: "march", phase: ph(c.t, 1.6), expr: c.t > at(3826) ? "grim" : "determined", prop: "case", lift: 40 });
    const [o, k] = german(9); P(c, W_(o, 381, k), OX - 10.6, 0, -5.4, { mode: "stand", expr: "stern" });
  } });
add({ a: 3784, b: 3891, set: "c11_wolfslair", light: "day", dof: 8, cam: DL("c11_wolfslair", [1.2, 1.7, -2.2], [0.3, 1.2, 0.6], 0.002, 46),
  st: (c) => {
    const a = act(c.t, [[3784, "point", "furious"], [3840, "fist", "shout"]]);
    P(c, W_(HITLER_WAR, 110, "hitw"), 0.3, 0, 0.05, { mode: "stand", expr: talk(c.t, a.expr, "angry"), pose: a.pose, pk: a.pk, facing: -1 });
    P(c, W_(STAUFFENBERG, 380, "stauf"), 1.75, 0, -0.35, { mode: "stand", expr: "grim", prop: "case" });
    for (let i = 0; i < 3; i++) { const [o, k] = officer("de", i + 9); P(c, W_(o, 390 + i, k), -1.3 - i * 1.1, 0, -0.1 - (i % 2) * 0.4, { mode: "stand", expr: pk(["stern", "worried", "neutral"] as Expr[], i), pose: i === 1 ? "cross" : undefined, pk: 1 }); }
  } });
add({ a: 3891, b: 3961, set: "c11_wolfslair", light: "day", dof: 10, cam: DL("c11_wolfslair", [1.25, 0.32, -0.75], [1.0, 0.25, 1.15], 0.002, 52),
  st: (c) => {
    // "He leaves it under the table and walks out."
    P(c, W_(HITLER_WAR, 110, "hitw"), 0.3, 0, 0.05, { mode: "stand", expr: "angry", pose: "point", pk: 1 });
    const out = c.t > at(3929), x = out ? 1.1 + 1.9 * (c.t - at(3929)) : 1.1;
    P(c, W_(STAUFFENBERG, 380, "stauf"), x, 0, -0.35, out ? { mode: "march", phase: ph(c.t, 1.8), expr: "grim", lift: 40 } : { mode: "stand", expr: "grim", prop: c.t < at(3905) ? "case" : null });
  } });
add({ a: 3961, b: 4012, set: "c11_wolfslair", light: "day", dof: 2, cam: DL("c11_wolfslair", [OX - 1.0, 1.7, -15], [OX, 2.2, 3], 0.003, 44, 0, 0.012),
  st: (c) => {
    // "The bomb goes off."
    const u = clamp01((c.t - at(3986)) / 1.2);
    if (u > 0) for (let i = 0; i < 3; i++) F(c, { key: `boom${q(clamp01(u * (1 + i * 0.2)), 12)}`, cw: 600, ch: 600, draw: (p) => fxBoom(p, q(clamp01(u * (1 + i * 0.2)), 12)), x: OX - 3.6 + i * 3.6, y: 2.2, z: 2.6, w: 6 + i, h: 6 + i, glow: 1.4 });
  } });
add({ a: 4012, b: 4133, set: "c11_wolfslair", light: "day", dof: 10, cam: DL("c11_wolfslair", [1.15, 0.32, -0.55], [1.7, 0.26, 1.15], 0.0015, 54),
  st: (c) => {
    // "But someone had moved the briefcase behind a thick wooden table leg."
    const [o, k] = officer("de", 11); P(c, W_(o, 395, k), 1.0 + 0.9 * smooth((c.t - at(4037)) / 0.8), 0, 0.55, { mode: "stand", expr: "neutral" });
    const k2 = smooth((c.t - at(4079)) / 0.4);
    if (k2 > 0) F(c, { key: `leg${q(k2, 10)}`, cw: 800, ch: 200, draw: (p) => fxLabel(p, "THICK WOODEN TABLE LEG", 46), x: 1.9, y: 0.68, z: 0.55, w: 1.25 * k2, h: 0.31 * k2 });
  } });
add({ a: 4133, b: 4245, set: "c11_wolfslair", light: "day", dof: 10, cam: DL("c11_wolfslair", [0.5, 1.4, -1.6], [0.35, 1.25, 0.05], 0.0025, 44, 0.04),
  st: (c) => {
    // "Hitler survives with burst eardrums and torn trousers."
    P(c, W_(HITLER_TORN, 111, "hitt"), 0.35, 0, 0.05, { mode: "stand", expr: c.t > at(4205) ? "shock" : "dazed", headTilt: 8, pose: c.t > at(4168) && c.t < at(4200) ? "head" : undefined, pk: 1 });
    F(c, { key: `stars${q((c.t * 0.8) % 1, 12)}`, cw: 420, ch: 220, draw: (p) => fxStars(p, q((c.t * 0.8) % 1, 12)), x: 0.35, y: 2.25, z: 0.0, w: 0.9, h: 0.47 });
    fog(c, 4, -2, 3, 0, 2, 1.0, 3, "#b8b0a0", 0.4);
  } });
add({ a: 4245, b: 4323, set: "street", light: "night", night: true, dof: 4, cam: DL("street", [0.6, 1.6, 14], [-1.0, 2.2, 32], 0.0012, 44) });   // "Stauffenberg is executed that night." (empty)

// ===== Warsaw =====
add({ a: 4323, b: 4462, set: "c11_warsaw", light: "dusk", dof: 3, cam: DL("c11_warsaw", [-2, 4.0, 30], [0, 8, 150], 0.0015, 50),
  st: (c) => {
    // "In August 1944, the Soviet army reaches the edge of Warsaw."
    for (let i = 0; i < 6; i++) { const [o, k] = soviet(i + 10); P(c, W_(o, 400 + i, k), -14 + i * 5.4, 0, 43.5 + (i % 2), { mode: "stand", expr: pk(["determined", "neutral", "grim"] as Expr[], i), pose: i === 2 ? "point" : undefined, pk: 1 }); }
  } });
add({ a: 4462, b: 4578, set: "c11_warsaw", light: "day", dof: 6, cam: DL("c11_warsaw", [2.2, 1.7, 177], [0, 2.6, 190], 0.002, 46),
  st: (c) => {
    // "Believing help is coming, the Polish resistance rises up against the Germans."
    for (let i = 0; i < 6; i++) {
      const [o, k] = i % 3 === 2 ? [{ ...WORKERS[(i * 3) % 10], hat: "stahl", helmCol: "#4c5448", scarf: "#c8202c" } as Outfit, `pw${i}`] : polish(i);
      const a = act(c.t, [[4462, null, "determined"], [4525 + i * 3, i % 2 ? "cheer" : "fist", i % 2 ? "joy" : "determined"]]);
      P(c, W_(o, 410 + i, k), -4.5 + i * 1.8, 0.3, 187.4 + (i % 2) * 0.8, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: i === 2 ? ["flag", "pl"] : null, flutter: ph(c.t, 1.3) });
    }
    for (let i = 0; i < 3; i++) { const [o, k] = polish(i + 7); P(c, W_(o, 420 + i, k), -14.5 + i * 1.6, 15.2, 204 + i, { mode: "stand", expr: "determined", pose: i === 1 ? "cheer" : undefined, pk: 1 }); }
  } });
add({ a: 4578, b: 4692, set: "c11_warsaw", light: "dusk", dof: 6, cam: DL("c11_warsaw", [4.5, 1.35, 36.5], [-1, 1.2, 46], 0.002, 46),
  st: (c) => {
    // "But the Soviet army stops on the other side of the river, and waits."
    const poses: [number, number, FrontOpts][] = [[-2.6, 43.3, { mode: "sit", expr: "neutral" }], [0.4, 43.6, { mode: "sit", expr: c.t > at(4667) ? "smug" : "neutral", prop: "stein" }],
      [2.0, 42.6, { mode: "stand", expr: "neutral", pose: "cross", pk: 1 }], [-4.2, 44.2, { mode: "stand", expr: "stern", pose: c.t > at(4663) ? "chin" : undefined, pk: 1 }]];
    poses.forEach(([x, z, fo], i) => { const [o, k] = soviet(i + 20); P(c, W_(o, 430 + i, k), x, 0, z, fo); });
  } });
add({ a: 4692, b: 4797, set: "c11_maproom", light: "interior", dof: 10, cam: DL("c11_maproom", [-0.4, 1.6, -0.8], [-0.95, 1.5, 0.9], 0.002, 40, 0.03),
  st: (c) => {
    // "Stalin doesn't want a free, independent Poland after the war,"
    const a = act(c.t, [[4692, "hips", "smug"], [4756, "point", "scheme"]]);
    P(c, W_(STALIN, 440, "stalin"), -1.0, 0, -0.75, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, facing: 1 });
  } });
add({ a: 4797, b: 4935, set: "c11_maproom", light: "interior", dof: 12, cam: DL("c11_maproom", [-0.62, 1.55, 0.35], [-0.83, 0.93, 1.14], 0.002, 40),
  st: (c) => { mapCard(c, "warsaw", 1); } });   // "...happy to let the Germans destroy the people who would lead it."
add({ a: 4935, b: 5034, set: "c11_warsaw", light: "gloom", dof: 8, cam: DL("c11_warsaw", [-2.5, 1.45, 181.5], [0, 1.5, 188], 0.002, 44),
  st: (c) => {
    // "The Poles fight alone for sixty-three days."
    for (let i = 0; i < 4; i++) { const [o, k] = polish(i + 3); P(c, W_(o, 450 + i, k), -3.6 + i * 2.2, 0.3, 187.6 + (i % 2) * 0.6, { mode: i % 2 ? "kneel" : "stand", expr: pk(["determined", "exhausted", "grim"] as Expr[], i), prop: i === 0 ? "grenade" : null }); }
    const n = Math.max(1, Math.min(63, Math.round(1 + 62 * clamp01((c.t - at(4978)) / 1.3))));
    F(c, { key: `day${n}`, cw: 400, ch: 240, draw: (p) => fxDay(p, n), x: 2.4, y: 3.2, z: 189, w: 1.4, h: 0.84 });
  } });
add({ a: 5034, b: 5247, set: "c11_warsaw", light: "grey", dof: 3, cam: DL("c11_warsaw", [80.5, 1.8, 160], [80, 4.2, 236], 0.0012, 48),
  st: (c) => {
    // "When it's over, up to two hundred thousand people are dead, and Hitler orders what's left of the city blown up, street by street."
    for (let i = 0; i < 4; i++) { const t0 = at(5181 + i * 14), u = clamp01((c.t - t0) / 1.0); if (u > 0 && u < 1) F(c, { key: `boom${q(u, 10)}`, cw: 600, ch: 600, draw: (p) => fxBoom(p, q(u, 10)), x: 80 + (i % 2 ? 9 : -9), y: 6, z: 250 - i * 12, w: 12, h: 12, glow: 1.3 }); }
    fog(c, 4, 70, 90, 180, 230, 2, 12, "#8a8478", 0.4);
  } });

// ===== Paris =====
add({ a: 5247, b: 5369, set: "c11_paris", light: "day", dof: 5, cam: DL("c11_paris", [-3.6, 1.0, 23.5], [2.2, 2.2, 34], 0.0022, 46, 0.03),
  st: (c) => {
    // "That same month, Paris rises up too, and this time help arrives."
    for (let i = 0; i < 3; i++) { const [o, k] = french(i); P(c, W_(o, 460 + i, k), 1.6 + i * 0.9, 1.75, 34.6 + (i % 2) * 0.6, { mode: "sit", expr: pk(["joy", "grin", "beam"] as Expr[], i), pose: i === 1 ? "wave" : undefined, pk: 1 }); }
    for (let i = 0; i < 22; i++) {
      const [o, k] = crowd(i), s = i % 2 ? 1 : -1, x = s * (5.6 + hh(i) * 4.5), z = 26 + hh(i, 2) * 18;
      const a = act(c.t, [[5247, pk(["cheer", "wave", "clap", "armsUp"] as Pose[], i), pk(["joy", "cheer", "laugh", "beam"] as Expr[], i)]]);
      P(c, W_(o, 470 + i, k), x, 0, z, { mode: "stand", expr: a.expr, pose: a.pose, pk: q(0.6 + 0.4 * Math.abs(Math.sin(c.t * 4 + i)), 5), prop: i % 7 === 3 ? ["flag", "fr"] : null, flutter: ph(c.t, 1.5, i * 0.1) });
    }
    F(c, { key: "confetti2", cw: 600, ch: 400, draw: (p) => fxConfetti(p, 7), x: 1, y: 6 - 0.6 * ((c.t - at(5247)) % 4), z: 30, w: 10, h: 6.7, soft: true, opacity: 1 });
  } });
add({ a: 5369, b: 5422, set: "c11_paris", light: "day", dof: 6, cam: DL("c11_paris", [0.4, 0.95, 44.5], [0, 2.4, 56], 0.0025, 44, -0.03),
  st: (c) => {
    // "Paris is liberated."
    P(c, W_(DEGAULLE, 500, "degaulle"), 0, 0, 51.5 - 0.7 * (c.t - at(5369)), { mode: "march", phase: ph(c.t, 1.0), expr: "proud", lift: 30 });
    for (let i = 0; i < 18; i++) { const [o, k] = crowd(i + 30), s = i % 2 ? 1 : -1; P(c, W_(o, 510 + i, k), s * (6 + hh(i) * 4), 0, 50 + hh(i, 3) * 14, { mode: "stand", expr: pk(["joy", "cheer", "laugh"] as Expr[], i), pose: pk(["cheer", "wave", "clap"] as Pose[], i), pk: 1 }); }
  } });

// ===== Market Garden =====
const BXN = 300;
add({ a: 5422, b: 5632, set: "c11_fields", light: "golden", dof: 0, cam: DL("c11_fields", [BXN - 6, 1.8, -6], [BXN + 4, 16, 60], 0.0012, 52),
  st: (c) => {
    // "In September, the Allies try to end the war by Christmas with a giant parachute drop into Holland, to grab a chain of bridges."
    const t = c.t - at(5422);
    for (let i = 0; i < 4; i++) F(c, { key: "dakota", cw: 600, ch: 200, draw: fxDakota, x: BXN - 70 + i * 22 + 11 * t, y: 52 + (i % 2) * 7, z: 110 + i * 12, w: 16, h: 5.3 });
    for (let i = 0; i < 26; i++) {
      const t0 = hh(i, 4) * 4, u = t - t0; if (u < 0) continue;
      const sw = q(Math.sin(c.t * 1.6 + i), 6);
      F(c, { key: `chute${sw}${i % 3}`, cw: 300, ch: 420, draw: (p) => fxChute(p, sw, pk(["#e8e2d0", "#d8ccb0", "#c8c8b8"], i)), x: BXN - 60 + hh(i) * 120 + 2.5 * u, y: Math.max(2, 46 - 3.2 * u - (i % 4) * 3), z: 70 + hh(i, 2) * 60, w: 6, h: 8.4 });
    }
  } });
add({ a: 5632, b: 5673, set: "c11_fields", light: "golden", dof: 6, cam: DL("c11_fields", [BXN + 0.6, 1.5, 22.4], [BXN, 1.7, 30], 0.003, 46),
  st: (c) => {
    // "They grab most of them."
    for (let i = 0; i < 4; i++) { const [o, k] = para(i); P(c, W_(o, 530 + i, k), BXN - 1.1 + i * 0.75, 0.9, 29.2 + (i % 2) * 0.8, { mode: "stand", expr: pk(["joy", "cheer", "grin", "laugh"] as Expr[], i), pose: i === 1 ? "cheer" : i === 3 ? "wave" : undefined, pk: 1 }); }
  } });
add({ a: 5673, b: 5740, set: "c11_fields", light: "golden", dof: 0, cam: DL("c11_fields", [BXN + 2, 3.2, 40], [BXN, 17, 230], 0.0018, 16) });   // "But not the last one, at Arnhem."
add({ a: 5740, b: 5838, set: "c11_fields", light: "golden", dof: 8, cam: DL("c11_fields", [BXN + 2.0, 1.55, 26.5], [BXN + 0.4, 1.9, 31], 0.002, 44),
  st: (c) => {
    // "It was, quite literally, a bridge too far."
    const a = act(c.t, [[5740, null, "neutral"], [5754, "shrug", "dazed"], [5807, "head", "shock"]]);
    const [o, k] = para(5); P(c, W_(o, 540, k), BXN + 0.3, 0.9, 31.2, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: a.pose ? null : "binoc" });
    stamp(c.out, c.t, at(5807), "TOO FAR", ...c.O(BXN - 1.4, 3.2, 33), 2.2);
  } });

// ===== the Bulge =====
add({ a: 5838, b: 5965, set: "c11_ardennes", light: "fog", dof: 4, cam: DL("c11_ardennes", [-1.8, 1.1, 6.5], [0.5, 2.2, 22], 0.0022, 46),
  st: (c) => {
    // "And in December 1944, Hitler throws his last reserves into a surprise attack through,"
    fog(c, 12, -10, 10, 16, 60, 1.2, 12, "#e2e8f0", 0.55);
    for (let i = 0; i < 6; i++) { const [o, k] = german(i + 12); const z = 18 - 0.8 * (c.t - at(5838)) + (i % 3) * 2.5; P(c, W_(o, 560 + i, k), (i % 2 ? 2.6 : -2.6) + hh(i) * 0.4, 0, z, { mode: "march", phase: ph(c.t, 1.5, i * 0.2), expr: pk(["grim", "determined", "stern"] as Expr[], i), lift: 50 }); }
  } });
add({ a: 5965, b: 6066, set: "c11_ardennes", light: "fog", dof: 6, cam: DL("c11_ardennes", [-6.2, 1.0, -0.6], [-1.5, 1.2, 8], 0.0025, 46),
  st: (c) => {
    // "you guessed it, the Ardennes forest again."
    ([-9, -4, 5, 10] as number[]).forEach((fx, i) => { const [o, k] = gi(i + 60); const a = act(c.t, [[5965, null, "neutral"], [5996 + i * 4, i % 2 ? "head" : "palms", i % 2 ? "panic" : "shock"]], 0.12); P(c, W_(o, 570 + i, k), fx, -0.95, 3.4, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk }); });
    fog(c, 8, -12, 12, 12, 40, 1.0, 12, "#e2e8f0", 0.5);
  } });
add({ a: 6066, b: 6120, set: "c11_maproom", light: "interior", dof: 12, cam: DL("c11_maproom", [0.75, 1.55, 0.2], [0.6, 0.93, 0.86], 0.003, 40, 0, 0.008),
  st: (c) => { mapCard(c, "bulge", smooth((c.t - at(6076)) / 0.9)); } });   // "It's the Battle of the Bulge."
add({ a: 6120, b: 6237, set: "c11_ardennes", light: "fog", dof: 6, cam: DL("c11_ardennes", [196.6, 1.5, -1.4], [200, 1.6, 28], 0.0018, 46),
  st: (c) => {
    // "In the town of Bastogne, surrounded American troops are told to surrender."
    for (let i = 0; i < 5; i++) { const [o, k] = gi(i + 70); const pos: [number, number][] = [[195, 10.8], [196.4, 11.2], [204.4, 14.8], [205.6, 15.1], [203, 41]]; P(c, W_(o, 580 + i, k), pos[i][0], 0, pos[i][1], { mode: "stand", expr: pk(["exhausted", "grim", "determined", "stern", "smug"] as Expr[], i), pose: i === 4 ? "cross" : undefined, pk: 1 }); }
    for (let i = 0; i < 2; i++) { const [o, k] = officer("de", i + 3); P(c, W_(o, 590 + i, k), 199.4 + i * 1.2, 0, 34 - 0.6 * (c.t - at(6120)), { mode: "march", phase: ph(c.t, 1.1, i * 0.5), expr: "smug", lift: 30, prop: i === 0 ? ["flag", "white"] : null, flutter: ph(c.t, 1.2) }); }
    fog(c, 6, 186, 214, 30, 70, 1.2, 12, "#e2e8f0", 0.45);
  } });
add({ a: 6237, b: 6327, set: "c11_ardennes", light: "interior", dof: 10, cam: DL("c11_ardennes", [-200.4, 1.55, 1.0], [-200, 1.15, 3.9], 0.0025, 46),
  st: (c) => {
    // "Their general sends back a reply with one word."
    P(c, W_(MCAULIFFE[0], 600, MCAULIFFE[1]), -200, 0, 4.15, { mode: "chair", desk: "papers", expr: c.t > at(6292) ? "smug" : "stern", chair: true });
    for (let i = 0; i < 2; i++) { const [o, k] = gi(i + 80); P(c, W_(o, 601 + i, k), -201.9 + i * 3.8, 0, 3.6, { mode: "stand", expr: i ? "grin" : "worried", pose: "cross", pk: 1 }); }
  } });
add({ a: 6327, b: 6358, set: "c11_ardennes", light: "interior", dof: 14, cam: DL("c11_ardennes", [-200, 1.35, 2.9], [-200, 0.8, 3.3], 0.004, 40, 0, 0.012),
  st: (c) => {
    // "Nuts."
    const k = 1 + 0.4 * (1 - smooth((c.t - at(6327)) / 0.15));
    F(c, { key: "nuts", cw: 400, ch: 300, draw: fxNuts, x: -200, y: 0.81, z: 3.3, w: 0.5 * k, h: 0.375 * k, flat: true, rot: Math.PI });
  } });
add({ a: 6358, b: 6426, set: "c11_ardennes", light: "fog", dof: 8, cam: DL("c11_ardennes", [200.6, 1.6, 30.6], [200, 1.55, 36], 0.0025, 44),
  st: (c) => {
    // "The Germans had no idea what it meant."
    for (let i = 0; i < 2; i++) { const [o, k] = officer("de", i + 3); P(c, W_(o, 590 + i, k), 199.4 + i * 1.3, 0, 35, { mode: "stand", expr: i ? "dazed" : "nervous", pose: i ? "shrug" : undefined, pk: 1, prop: i ? null : "paper" }); }
    ([0, 1] as number[]).forEach((i) => { const k2 = smooth((c.t - at(6379 + i * 8)) / 0.2); if (k2 > 0) F(c, { key: "qm", cw: 200, ch: 220, draw: fxQuestion, x: 199.4 + i * 1.3, y: 2.6, z: 34.9, w: 0.45 * k2, h: 0.5 * k2 }); });
  } });
add({ a: 6426, b: 6522, set: "c11_ardennes", light: "fog", dof: 8, cam: DL("c11_ardennes", [199.8, 1.55, 32.2], [199.6, 1.6, 35], 0.002, 40),
  st: (c) => {
    // "But they figured out it wasn't a yes."
    const a = act(c.t, [[6426, null, "dazed"], [6447, "chin", "grim"], [6471, "shrug", "sorrow"]]);
    const [o, k] = officer("de", 3); P(c, W_(o, 590, k), 199.4, 0, 35, { mode: "stand", expr: a.expr, pose: a.pose, pk: a.pk, prop: a.pose ? null : "paper" });
    const [o2, k2] = officer("de", 4); P(c, W_(o2, 591, k2), 200.7, 0, 35.3, { mode: "stand", expr: c.t > at(6457) ? "sneer" : "dazed", pose: "cross", pk: 1 });
  } });

// ---------------------------------------------------------------- assemble
const TOTAL = 6522;
SH.forEach((s, i) => { if (i + 1 < SH.length && SH[i + 1].a !== s.b) throw new Error(`ch11 gap at shot ${i + 1}`); });
if (SH[SH.length - 1].b !== TOTAL) throw new Error("ch11 total");
const shots = SH.map((s, i) => ({ id: i + 1, a: s.a, b: s.b, set: s.set, light: s.light, night: s.night }));
const cams: Record<number, Key[]> = {}, stage: Record<number, (c: Ctx) => void> = {};
const dof: Dof[] = [];
SH.forEach((s, i) => { cams[i + 1] = s.cam(s.a, s.b); if (s.st) stage[i + 1] = s.st; dof.push({ f: s.a, cInf: s.dof ?? 6 }); });
export const CH = makeChapter({
  total: TOTAL, shots, cams, dof, stage,
  xfade: { 7: 10, 15: 10, 25: 10, 28: 8, 31: 8, 37: 10, 42: 10, 49: 10, 50: 10, 56: 10, 57: 10, 59: 10, 63: 12 },
  cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER 11", "CLOSING IN", "1944"] }],
  kicks: [[2597 / FPS, 0.6], [2645 / FPS, 0.5], [3986 / FPS, 1.4], [6327 / FPS, 0.7], [5181 / FPS, 0.4], [5195 / FPS, 0.4]],
});
