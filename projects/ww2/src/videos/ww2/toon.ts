// Our own flat 2D cartoon cast (riflemen, officer, townsfolk, kid, parent) + 2D effects, drawn on a canvas.
// Construction v2 (characters.md, our own cast): superellipse heads (pointed crown 1.75 / full jaw 2.3, chin taper,
// seeded side bulge + tilt), bean torsos, single-stroke limbs with ink-dot hands, a thick-thin plum outline weighted
// away from the light, soft painted crescents, deadpan lidded eyes, no blush, no catchlights.
// Design space 600 x 1000 units (soles at y = 975); the canvas transform scales it.
export const INK = "#241726";
export const SKIN = "#ffe2c2";
const WHITE = "#ffffff";
const MOUTH = "#5a1e28";
const TONGUE = "#e86e78";
type C3 = [number, number, number];
const SH_SKIN: C3 = [0.96, 0.86, 0.84]; // measured shadow/lit ratio on skin heads
const SH_CLOTH: C3 = [0.64, 0.66, 0.74]; // torsos: lit side -> far side ~0.65
const SH_FELT: C3 = [0.62, 0.62, 0.7];

export type Build = "adult" | "stout" | "kid" | "thin" | "short" | "fat" | "tall";
export type Outfit = {
  jacket: string; pants: string; boots: string; hat?: string | null; belt?: string | null; buttons?: string; rifle?: boolean;
  sash?: string; sword?: boolean; moustache?: string; skin?: string; head?: number; cap?: string; hair?: string; dress?: string;
  build?: Build; star?: boolean; glasses?: boolean; part?: boolean; sweat?: boolean;
  pattern?: "plaid" | "stripes" | "check" | "pinstripe" | "dots" | "bars"; patCol?: string; vest?: string; bowtie?: string; tie?: string; scarf?: string; apron?: string; pocket?: boolean | string;
  /** hat colour (bowler, fedora, top hat, cloche, flat cap falls back to cap), hat band, cloche flower */
  hatCol?: string; band?: string; flower?: string;
  /** moustache style (colour stays in `moustache`) */
  stache?: "walrus" | "handlebar" | "pencil" | "plain";
  brows?: string; bushy?: boolean; nose?: "button" | "round" | "big" | "long"; cheeks?: boolean; freckles?: boolean; noEars?: boolean; tufts?: boolean;
  cigar?: boolean; lapels?: boolean; shirt?: string; braces?: string; waist?: string; watch?: boolean; pearls?: boolean;
  /** shirt-sleeve colour (vest outfits), rolled-up sleeves, shirt cuffs, short trousers + socks, a knee patch */
  sleeves?: string; rolled?: boolean; cuffs?: boolean; shorts?: boolean; socks?: string; patch?: string;
  /** dress print, drop-waist sash, round collar */
  dressPat?: "dots" | "stripes" | "check"; dressCol2?: string; sashW?: string; pcollar?: string; bow?: string;
  /** soldiers: field tunic (collar, breast pockets), webbing colour (belt, pouches, braces), canteen, puttees / tall boots,
   *  helmet netting, cap neck flaps, worn + patched kit, rifle bayonet, stubble, a cheek scar, a head bandage */
  tunic?: boolean; webbing?: string; canteen?: boolean; puttees?: string; tallBoots?: boolean; net?: boolean; flaps?: boolean; worn?: boolean;
  bayonet?: boolean; stubble?: boolean; scar?: boolean; bandage?: boolean; helmCol?: string;
  // ---- WW2 figures (chapters 2-14) ----
  /** pipe in the mouth, long cigarette holder, pince-nez, dark aviator glasses, eye patch */
  pipe?: "briar" | "corncob"; holder?: boolean; pince?: boolean; aviators?: boolean; eyepatch?: boolean;
  /** jutting square jaw, round jowly face, haggard (eye bags, lines), frost on brows and moustache */
  jaw?: boolean; jowls?: boolean; haggard?: boolean; frost?: boolean;
  /** peaked caps / kepi: visor colour, gold braid on the visor + chin cord, small cap badge colour, high-fronted crown */
  visor?: string; braid?: boolean; badge?: string; saddle?: boolean; starCol?: string;
  /** letter painted on a helmet (air-raid warden "W") */
  helmMark?: string;
  /** medal count (ribbon bars + hanging medals on the left breast), shoulder-board colour, gold cuff rings (navy) */
  medals?: number; boards?: string; rings?: number;
  /** long greatcoat (skirt colour), cape over the shoulders (colour), ragged snow cape, fur collar colour */
  coat?: string; cape?: string; snow?: boolean; fur?: string;
  /** coverall bib colour, sailor's square collar colour, wing collar, a red cross on the bib/cap */
  bib?: string; sailorCollar?: string; wing?: boolean; redcross?: boolean;
  /** evacuee luggage label, gas-mask box on a string, a furled umbrella in the left hand, a sub-machine gun */
  tag?: boolean; gasbox?: boolean; umbrella?: boolean; smg?: "ppsh" | "smg";
  /** trouser stripes (prison uniform), hair under a hat (pilotka, beret, bandana, nurse cap) */
  pantsPat?: "bars"; hairUnder?: boolean; tieDots?: string;
  /** leather flying helmet: goggles on the forehead (default true) */
  goggles?: boolean;
  /** eyelashes (women in trousers / uniform) */
  lashes?: boolean;
};
type P2 = [number, number];

const rad = (d: number) => (d * Math.PI) / 180;
const clamp = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x));
export const mul = (c: string, m: C3) => {
  const n = parseInt(c.slice(1), 16);
  const ch = (v: number, k: number) => Math.min(255, Math.round(v * k)).toString(16).padStart(2, "0");
  return `#${ch((n >> 16) & 255, m[0])}${ch((n >> 8) & 255, m[1])}${ch(n & 255, m[2])}`;
};
export const shade = (c: string, k: number) => mul(c, [k, k, k]);
export const mix = (a: string, b: string, t: number) => {
  const A = parseInt(a.slice(1), 16), B = parseInt(b.slice(1), 16);
  const ch = (s: number) => Math.round(((A >> s) & 255) * (1 - t) + ((B >> s) & 255) * t).toString(16).padStart(2, "0");
  return `#${ch(16)}${ch(8)}${ch(0)}`;
};
/** deterministic per-character random in [0, 1) */
const rnd = (seed: number, k: number) => { const x = Math.sin(seed * 127.1 + k * 311.7) * 43758.5453; return x - Math.floor(x); };
const rotPts = (pts: P2[], a: number, cx: number, cy: number): P2[] =>
  pts.map(([x, y]) => [cx + (x - cx) * Math.cos(a) - (y - cy) * Math.sin(a), cy + (x - cx) * Math.sin(a) + (y - cy) * Math.cos(a)]);
const rotAbout = (q: P2, a: number, c: P2): P2 => rotPts([q], a, c[0], c[1])[0];
const lerp2 = (a: P2, b: P2, t: number): P2 => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
/** smooth curve from a through (near) k to b, as a polyline */
const curve = (a: P2, k: P2, b: P2, n = 10): P2[] => {
  const c: P2 = [2 * k[0] - (a[0] + b[0]) / 2, 2 * k[1] - (a[1] + b[1]) / 2], out: P2[] = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, s = 1 - t;
    out.push([s * s * a[0] + 2 * s * t * c[0] + t * t * b[0], s * s * a[1] + 2 * s * t * c[1] + t * t * b[1]]);
  }
  return out;
};

export const RIFLEMAN: Outfit = { jacket: "#357650", pants: "#3d4440", boots: INK, hat: "shako", belt: "#f1efe6", buttons: "#d9dde0", rifle: true };
export const OFFICER: Outfit = { ...RIFLEMAN, hat: "shako_tall", buttons: "#e8c45a", sash: "#c0353a", sword: true, moustache: "#4a3020", rifle: false, belt: null, build: "stout" };
export const KID: Outfit = { jacket: "#f08a2c", pants: "#3b5b9a", boots: "#f4f1ea", hat: "cap", cap: "#e2453c", build: "kid" };
export const PARENT: Outfit = { jacket: "#7b5ac9", pants: "#3b3f52", boots: "#5a3b2a", hat: "hair", hair: "#5a3b2a" };
export const SKINS = [SKIN, "#f5c9a0", "#ecd0b6", "#c99067"];
// ---- Kiska 1943 cast (our own designs): US M1 helmet olive drab, Canadian Brodie helmet khaki battledress, Japanese
// khaki field cap with a yellow star, a US Navy lookout in a white cap, a kid in pyjamas
export const US: Outfit = { jacket: "#727048", pants: "#5e5c42", boots: "#4a3426", hat: "m1", belt: null, buttons: "#4a4630", rifle: true,
  tunic: true, webbing: "#a49a68", canteen: true, puttees: "#b8ac80", net: true };
export const CA: Outfit = { jacket: "#86704a", pants: "#74603f", boots: "#2e2620", hat: "brodie", belt: null, buttons: "#5a4a30", rifle: true,
  tunic: true, webbing: "#c8bc8c", canteen: true, puttees: "#6a583a" };
/** continental field grey with a flared steel helmet: plain, no insignia */
export const GE: Outfit = { jacket: "#5e6658", pants: "#565c50", boots: "#221c1c", hat: "stahl", helmCol: "#4c5448", belt: null, buttons: "#8a8c80", rifle: true,
  tunic: true, webbing: "#2e2824", canteen: true, tallBoots: true };
/** Japanese field cap with a cloth neck flap; no badge */
export const JP: Outfit = { jacket: "#b3a262", pants: "#a29152", boots: "#5a4030", hat: "cap", cap: "#a8955a", flaps: true, belt: null, buttons: "#6a5a30", rifle: true,
  tunic: true, webbing: "#6a5a3a", canteen: true, puttees: "#9a8a52" };
export const SAILOR: Outfit = { jacket: "#2e4270", pants: "#2a3350", boots: INK, hat: "sailor", belt: null, buttons: "#c9ccd2" };
export const PJKID: Outfit = { jacket: "#86b8e6", pants: "#86b8e6", boots: "#f4f1ea", hat: "hair", hair: "#5a3b2a", build: "kid", buttons: "#ffffff" };
export const army = (base: Outfit, v = 0, extra: Partial<Outfit> = {}): Outfit => {
  const o: Outfit = { ...base, skin: base === JP ? ["#f5d3ac", "#ecc69b", "#f0cfa6", "#e3b98c"][v % 4] : SKINS[v % 4],
    build: (["adult", "stout", "thin", "adult", "short", "adult"] as Build[])[v % 6], stubble: v % 3 === 2, scar: v % 5 === 3, bayonet: v % 2 === 0,
    nose: (["button", "round", "long", "big"] as const)[v % 4], bandage: v % 7 === 5 };
  if (base !== JP && v % 4 === 1) o.moustache = "#4a3426";
  return { ...o, ...extra };
};

export const soldier = (v = 0, extra: Partial<Outfit> = {}): Outfit => {
  const o: Outfit = { ...RIFLEMAN, skin: SKINS[v % 4] };
  if (v % 4 === 1) o.moustache = "#4a3426";
  if (v % 4 === 3) o.moustache = "#2a201a";
  return { ...o, ...extra };
};

export const townsfolk = (v = 0): Outfit => {
  const coats = ["#3f6fb5", "#8c3b4a", "#5d7a3a", "#b5653f", "#2f5f6a", "#7b5ac9"];
  const o: Outfit = { jacket: coats[v % 6], pants: "#3b3f52", boots: "#4a3426", skin: SKINS[v % 4] };
  return v % 2 ? { ...o, hat: "bonnet", dress: ["#d9a441", "#c25a7a", "#5a8fc2"][v % 3] } : { ...o, hat: "tophat" };
};

export class Pen {
  g: CanvasRenderingContext2D;
  ol = 12;
  /** [angle, cx, cy] rotation about (cx, cy), optional post-translation [.., dx, dy] */
  rot: number[] | null = null;
  constructor(g: CanvasRenderingContext2D) { this.g = g; }
  P(x: number, y: number): P2 {
    if (!this.rot) return [x, y];
    const r = this.rot, a = r[0], cx = r[1], cy = r[2], dx = r.length > 3 ? r[3] : 0, dy = r.length > 4 ? r[4] : 0, c = Math.cos(a), s = Math.sin(a);
    return [cx + (x - cx) * c - (y - cy) * s + dx, cy + (x - cx) * s + (y - cy) * c + dy];
  }
  path(pts: P2[], close: boolean) {
    const g = this.g;
    g.beginPath();
    pts.forEach((p, i) => { const [x, y] = this.P(p[0], p[1]); if (i) g.lineTo(x, y); else g.moveTo(x, y); });
    if (close) g.closePath();
  }
  /** filled shape with an ink outline; fill=null draws the outline only */
  poly(pts: P2[], fill: string | null, ol?: number) {
    const g = this.g, w = ol ?? this.ol;
    this.path(pts, true);
    if (fill) { g.fillStyle = fill; g.fill(); }
    if (w) { g.lineWidth = w; g.strokeStyle = INK; g.lineJoin = "round"; g.stroke(); }
  }
  ell(cx: number, cy: number, rx: number, ry: number, fill: string | null, ol?: number, a0 = 0, a1 = 360, rot = 0) {
    this.poly(ellPts(cx, cy, rx, ry, a0, a1, rot), fill, ol);
  }
  /** thick round-capped limb with an ink rim (effects, rope) */
  line(pts: P2[], fill: string, w: number, ink = true) {
    const g = this.g;
    g.lineCap = "round"; g.lineJoin = "round";
    if (ink) { this.path(pts, false); g.strokeStyle = INK; g.lineWidth = w + 2 * this.ol * 0.9; g.stroke(); }
    this.path(pts, false); g.strokeStyle = fill; g.lineWidth = w; g.stroke();
  }
  stroke(pts: P2[], w: number, fill = INK) {
    const g = this.g;
    g.lineCap = "round"; g.lineJoin = "round";
    this.path(pts, false); g.strokeStyle = fill; g.lineWidth = w; g.stroke();
  }
  arc(cx: number, cy: number, rx: number, ry: number, a0: number, a1: number, w: number, fill = INK) {
    const pts: P2[] = [];
    for (let i = 0; i <= 24; i++) pts.push([cx + rx * Math.cos(rad(a0 + ((a1 - a0) * i) / 24)), cy + ry * Math.sin(rad(a0 + ((a1 - a0) * i) / 24))]);
    this.stroke(pts, w, fill);
  }
  dot(cx: number, cy: number, r: number, fill = INK) {
    const [x, y] = this.P(cx, cy);
    this.g.beginPath(); this.g.arc(x, y, r, 0, Math.PI * 2); this.g.fillStyle = fill; this.g.fill();
  }
  /** draw with a closed shape as clip */
  clip(pts: P2[], fn: () => void) { const g = this.g; g.save(); this.path(pts, true); g.clip(); fn(); g.restore(); }
  /** flat fill + soft crescent on the side away from the light (light = canvas angle the light comes FROM).
   *  Radial ramp centred `shift` R toward the light: flat out to ~0.6 R on the far side, full shadow by ~0.8 R. */
  shadedFill(pts: P2[], base: string, shadow: string, light: number, R: number, shift = 0.45, r0 = 1.05, r1 = 1.25) {
    const g = this.g, n = pts.length;
    let cx = 0, cy = 0;
    for (const [x, y] of pts) { cx += x / n; cy += y / n; }
    const [gx, gy] = this.P(cx + Math.cos(light) * shift * R, cy + Math.sin(light) * shift * R);
    const gr = g.createRadialGradient(gx, gy, 0, gx, gy, r1 * R);
    gr.addColorStop(0, base); gr.addColorStop(r0 / r1, base); gr.addColorStop(1, shadow);
    this.path(pts, true); g.fillStyle = gr; g.fill();
  }
  /** broad gradient across a shape along the light: lit edge = base, far edge = shadow (torsos, coats) */
  gradFill(pts: P2[], base: string, shadow: string, light: number, flat = 0.22) {
    const g = this.g, dx = Math.cos(light), dy = Math.sin(light), n = pts.length;
    let cx = 0, cy = 0, lo = Infinity, hi = -Infinity;
    for (const [x, y] of pts) { cx += x / n; cy += y / n; const d = x * dx + y * dy; lo = Math.min(lo, d); hi = Math.max(hi, d); }
    const dc = cx * dx + cy * dy;
    const [ax, ay] = this.P(cx + dx * (hi - dc), cy + dy * (hi - dc)), [bx, by] = this.P(cx + dx * (lo - dc), cy + dy * (lo - dc));
    const gr = g.createLinearGradient(ax, ay, bx, by);
    gr.addColorStop(0, base); gr.addColorStop(flat, base); gr.addColorStop(1, shadow);
    this.path(pts, true); g.fillStyle = gr; g.fill();
  }
  /** thick-thin ink ring: w(θ) = w0 (1 + k cos(θ − thick)), θ from the contour centroid (canvas angles) */
  inkRing(pts: P2[], w0: number, thick: number, k = 0.45, col = INK) {
    const n = pts.length;
    let cx = 0, cy = 0;
    for (const [x, y] of pts) { cx += x / n; cy += y / n; }
    const out: P2[] = [], inn: P2[] = [];
    pts.forEach((q, i) => {
      const a = pts[(i + n - 1) % n], b = pts[(i + 1) % n];
      let nx = b[1] - a[1], ny = a[0] - b[0]; // outward normal for clockwise-on-screen contours
      const l = Math.hypot(nx, ny) || 1; nx /= l; ny /= l;
      const h = 0.5 * w0 * (1 + k * Math.cos(Math.atan2(q[1] - cy, q[0] - cx) - thick));
      out.push([q[0] + nx * h, q[1] + ny * h]); inn.push([q[0] - nx * h, q[1] - ny * h]);
    });
    const g = this.g;
    const trace = (r: P2[]) => { r.forEach(([x0, y0], i) => { const [x, y] = this.P(x0, y0); if (i) g.lineTo(x, y); else g.moveTo(x, y); }); g.closePath(); };
    g.beginPath(); trace(out); trace(inn.reverse());
    g.fillStyle = col; g.fill("evenodd");
  }
  /** flat strap with a thin ink rim (cross belts, sash, rifle, handles) */
  band(pts: P2[], fill: string, w: number, rim: number, cap: CanvasLineCap = "butt") {
    const g = this.g; g.lineCap = cap; g.lineJoin = "round";
    this.path(pts, false); g.strokeStyle = INK; g.lineWidth = w + 2 * rim; g.stroke();
    this.path(pts, false); g.strokeStyle = fill; g.lineWidth = w; g.stroke();
    g.lineCap = "round";
  }
}

const ellPts = (cx: number, cy: number, rx: number, ry: number, a0 = 0, a1 = 360, rot = 0, n = 48): P2[] => {
  const r = rad(rot), pts: P2[] = [];
  for (let i = 0; i <= n; i++) {
    const a = rad(a0 + ((a1 - a0) * i) / n), x = rx * Math.cos(a), y = ry * Math.sin(a);
    pts.push([cx + x * Math.cos(r) - y * Math.sin(r), cy + x * Math.sin(r) + y * Math.cos(r)]);
  }
  return pts;
};

const rrect = (x0: number, y0: number, x1: number, y1: number, r: number, n = 8): P2[] => {
  const pts: P2[] = [];
  for (const [cx, cy, a] of [[x1 - r, y0 + r, -90], [x1 - r, y1 - r, 0], [x0 + r, y1 - r, 90], [x0 + r, y0 + r, 180]])
    for (let i = 0; i <= n; i++) pts.push([cx + r * Math.cos(rad(a + (90 * i) / n)), cy + r * Math.sin(rad(a + (90 * i) / n))]);
  return pts;
};

/** tapered stroke, thick end at a: brows, moustache halves */
const taper = (p: Pen, a: P2, b: P2, wa: number, wb: number, col = INK) => {
  const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
  p.poly([[a[0] + nx * wa / 2, a[1] + ny * wa / 2], [b[0] + nx * wb / 2, b[1] + ny * wb / 2],
    [b[0] - nx * wb / 2, b[1] - ny * wb / 2], [a[0] - nx * wa / 2, a[1] - ny * wa / 2]], col, 0);
  p.dot(a[0], a[1], wa / 2, col); p.dot(b[0], b[1], wb / 2, col);
};

// ---------------- contours ----------------
export type Blob = { a: number; b: number; nTop: number; nBot: number; egg: number; asym: number; rot: number; noise: number; seed: number };

/** superellipse "bean": separate crown / jaw exponents, egg taper (neg = narrower chin), one-side bulge, soft noise.
 *  Points run right -> down -> left -> up (clockwise on screen). */
export const blobPts = (cx: number, cy: number, B: Blob, n = 72): P2[] => {
  const ph = [rnd(B.seed, 11), rnd(B.seed, 12), rnd(B.seed, 13)].map((v) => v * Math.PI * 2);
  const pts: P2[] = [];
  for (let i = 0; i < n; i++) {
    const t = (i / n) * Math.PI * 2, c = Math.cos(t), s = Math.sin(t), e = 2 / (s < 0 ? B.nTop : B.nBot);
    let X = Math.sign(c) * Math.abs(c) ** e;
    const Y = Math.sign(s) * Math.abs(s) ** e;
    X *= (1 + B.egg * Y) * (1 + B.asym * Math.sign(X));
    const r = 1 + B.noise * (Math.cos(2 * t + ph[0]) + 0.7 * Math.cos(3 * t + ph[1]) + 0.5 * Math.cos(4 * t + ph[2]));
    const x = B.a * X * r, y = B.b * Y * r;
    pts.push([cx + x * Math.cos(B.rot) - y * Math.sin(B.rot), cy + x * Math.sin(B.rot) + y * Math.cos(B.rot)]);
  }
  return pts;
};

/** measured head: H/W 0.94, slightly pointed crown (1.75), fuller jaw (2.3), chin taper -0.12, 8 % bulge to the facing side */
export const headBlob = (seed: number, a = 118, facing = 0): Blob => ({
  a, b: a * (0.94 + 0.08 * (rnd(seed, 1) - 0.5)),
  nTop: 1.75 + 0.3 * (rnd(seed, 2) - 0.5), nBot: 2.3 + 0.3 * (rnd(seed, 3) - 0.5),
  egg: -0.12 + 0.06 * (rnd(seed, 4) - 0.5),
  asym: (0.06 + 0.04 * rnd(seed, 5)) * (facing || (rnd(seed, 6) < 0.5 ? -1 : 1)),
  rot: rad(8 * (rnd(seed, 7) - 0.5)), noise: 0.008, seed,
});

/** WW2 caricature heads: a jutting square jaw, or a round jowly face */
const headMod = (o: Outfit, H: Blob): Blob => o.jaw ? { ...H, nBot: 3.6, egg: 0.06, b: H.b * 1.05 } : o.jowls ? { ...H, nBot: 2.8, egg: 0.1, a: H.a * 1.05 } : H;
/** headgear that covers the ears */
const EARLESS: Record<string, boolean> = { ushanka: true, leather: true, headscarf: true };

/** thickest outline direction: away from the light, pulled toward the ground (64 deg measured for upper-left light) */
export const thickAngle = (light: number) => Math.atan2(-Math.sin(light) + 0.8, -Math.cos(light));
const DEF_LIGHT = rad(-120);

// ---------------- faces ----------------
export type Expr = "neutral" | "stern" | "grin" | "laugh" | "whistle" | "nervous" | "shock" | "relief" | "relief_open" | "dazed"
  | "pained" | "smile" | "smile_closed" | "lick" | "shout" | "sad" | "smug" | "angry"
  | "yell" | "cheer" | "panic" | "scheme" | "proud" | "gasp" | "furious" | "worried" | "beam" | "sneer" | "weep"
  // war: fear, grief (eyes shut, tears), exhausted (heavy lids, bags), determined (set jaw), sorrow (quiet, eyes down),
  // joy (laughing tears: VE day), grim (tight-lipped), dread (wide eyes, tight mouth)
  | "fear" | "grief" | "exhausted" | "determined" | "sorrow" | "joy" | "grim" | "dread";
type EyeK = "dot" | "small" | "lid" | "slit" | "happy" | "dash" | "squeeze" | "shock" | "shockHalf" | "spiral" | "wide" | "glare" | "shut" | "low";
type MouthK = "dash" | "frown" | "smirk" | "smile" | "smileWide" | "grin" | "laugh" | "o" | "O" | "wave" | "teeth" | "lick"
  | "yell" | "gape" | "grimace" | "toothy" | "sneer" | "small" | "tight";
/** eyes [back, front], brows [inner, outer] offsets in u (+ = down), mouth kind */
const FACE: Record<Expr, { eye: [EyeK, EyeK]; brow: [number, number]; mouth: MouthK }> = {
  neutral: { eye: ["lid", "lid"], brow: [0, -1], mouth: "dash" },
  stern: { eye: ["lid", "lid"], brow: [5, -3], mouth: "frown" },
  grin: { eye: ["happy", "happy"], brow: [-4, -4], mouth: "toothy" },
  laugh: { eye: ["squeeze", "squeeze"], brow: [-5, -5], mouth: "laugh" },
  whistle: { eye: ["dash", "dash"], brow: [-2, -4], mouth: "o" },
  nervous: { eye: ["wide", "wide"], brow: [-6, 2], mouth: "wave" },
  shock: { eye: ["shock", "shock"], brow: [-7, -6], mouth: "O" },
  relief: { eye: ["happy", "happy"], brow: [-2, 1], mouth: "smileWide" },
  relief_open: { eye: ["happy", "happy"], brow: [-2, 1], mouth: "grin" },
  dazed: { eye: ["spiral", "spiral"], brow: [-3, 2], mouth: "wave" },
  pained: { eye: ["squeeze", "lid"], brow: [-4, 3], mouth: "grimace" },
  smile: { eye: ["dot", "dot"], brow: [-1, -2], mouth: "smileWide" },
  smile_closed: { eye: ["happy", "happy"], brow: [-1, -2], mouth: "smile" },
  lick: { eye: ["dot", "dot"], brow: [0, -1], mouth: "lick" },
  shout: { eye: ["glare", "glare"], brow: [8, -4], mouth: "yell" },
  sad: { eye: ["dot", "dot"], brow: [-6, 4], mouth: "frown" },
  smug: { eye: ["lid", "lid"], brow: [-1, -6], mouth: "smirk" },
  angry: { eye: ["glare", "glare"], brow: [8, -3], mouth: "teeth" },
  yell: { eye: ["wide", "wide"], brow: [6, -6], mouth: "yell" },
  cheer: { eye: ["happy", "happy"], brow: [-6, -6], mouth: "gape" },
  panic: { eye: ["shock", "shock"], brow: [-8, -1], mouth: "grimace" },
  scheme: { eye: ["lid", "lid"], brow: [7, -6], mouth: "toothy" },
  proud: { eye: ["happy", "happy"], brow: [-1, -6], mouth: "smirk" },
  gasp: { eye: ["wide", "wide"], brow: [-9, -7], mouth: "O" },
  furious: { eye: ["glare", "glare"], brow: [10, -3], mouth: "yell" },
  worried: { eye: ["dot", "dot"], brow: [-8, 3], mouth: "grimace" },
  beam: { eye: ["happy", "happy"], brow: [-5, -5], mouth: "gape" },
  sneer: { eye: ["glare", "lid"], brow: [7, -3], mouth: "sneer" },
  weep: { eye: ["squeeze", "squeeze"], brow: [-7, 4], mouth: "gape" },
  fear: { eye: ["wide", "wide"], brow: [-10, 1], mouth: "small" },
  grief: { eye: ["shut", "shut"], brow: [-9, 4], mouth: "frown" },
  exhausted: { eye: ["slit", "slit"], brow: [-2, 5], mouth: "small" },
  determined: { eye: ["glare", "glare"], brow: [7, -2], mouth: "tight" },
  sorrow: { eye: ["low", "low"], brow: [-8, 3], mouth: "frown" },
  joy: { eye: ["squeeze", "squeeze"], brow: [-6, -5], mouth: "laugh" },
  grim: { eye: ["lid", "lid"], brow: [6, 0], mouth: "tight" },
  dread: { eye: ["wide", "wide"], brow: [-8, 2], mouth: "tight" },
};
/** expressions that draw tears / tired eye bags */
const TEARS: Partial<Record<Expr, boolean>> = { grief: true, joy: true };
const BAGS: Partial<Record<Expr, boolean>> = { exhausted: true, grief: true };
const halfLid = (k: EyeK): EyeK => (k === "dot" || k === "small" || k === "wide" ? "lid" : k === "lid" || k === "glare" ? "slit" : k === "shock" ? "shockHalf" : k);
const eyeKind = (k: EyeK, lid: number): EyeK =>
  lid >= 1 && k !== "happy" && k !== "squeeze" && k !== "spiral" ? "dash" : lid > 0 ? halfLid(k) : k;
const lidOf = (b: boolean | number | undefined) => (b === true ? 1 : Number(b) || 0);

const eye = (p: Pen, kind: EyeK, x: number, ey: number, u: number, side: number, look: number, skin: string) => {
  const lx = x + look * 3 * u, lw = 3.8 * u;
  switch (kind) {
    case "dot": p.ell(lx, ey, 3.8 * u, 5.5 * u, INK, 0); break;
    case "small": p.ell(lx, ey, 3 * u, 4.4 * u, INK, 0); break;
    case "lid": p.ell(lx, ey - u, 7 * u, 6 * u, INK, 0, 0, 180); p.stroke([[x - 9 * u, ey - u], [x + 9 * u, ey - u]], lw); break;
    case "slit": p.ell(lx, ey, 7 * u, 2.6 * u, INK, 0, 0, 180); p.stroke([[x - 9 * u, ey], [x + 9 * u, ey]], lw); break;
    case "happy": p.arc(x, ey + 3 * u, 8 * u, 6 * u, 200, 340, lw); break;
    case "dash": p.stroke([[x - 8.5 * u, ey], [x + 8.5 * u, ey]], lw); break;
    case "shut": p.arc(x, ey - 2 * u, 8 * u, 5 * u, 20, 160, lw); break;
    case "low": p.ell(lx, ey + 1.5 * u, 6.5 * u, 4.5 * u, INK, 0, 0, 180); p.stroke([[x - 9 * u, ey + 1.5 * u], [x + 9 * u, ey + 1.5 * u]], lw); break;
    case "squeeze": p.stroke([[x + 6 * u * side, ey - 5 * u], [x - 6 * u * side, ey], [x + 6 * u * side, ey + 5 * u]], lw); break;
    case "wide": p.ell(x, ey, 8.5 * u, 10 * u, WHITE, 2.4 * u); p.dot(lx - side * 0.5 * u, ey + 1.5 * u, 3.6 * u); break;
    case "glare": {
      // white eye cut by a slanted lid, low on the inner side
      const ix = x - side * 9.5 * u, ox = x + side * 9.5 * u;
      p.clip([[ix, ey - 1 * u], [ox, ey - 7 * u], [ox, ey + 12 * u], [ix, ey + 12 * u]], () => {
        p.ell(x, ey, 8.5 * u, 8.5 * u, WHITE, 2.4 * u); p.dot(lx - side * u, ey + 2 * u, 3.4 * u);
      });
      p.stroke([[ix, ey - 0.5 * u], [ox, ey - 7.5 * u]], 3.4 * u);
      break;
    }
    case "shock": case "shockHalf":
      p.ell(x, ey, 11 * u, 11 * u, WHITE, 2.6 * u); p.dot(lx - side * 1.5 * u, ey + 1.5 * u, 3 * u);
      if (kind === "shockHalf") { p.ell(x, ey, 11 * u, 11 * u, skin, 0, 180, 360); p.stroke([[x - 11 * u, ey], [x + 11 * u, ey]], 2.6 * u); }
      break;
    default: {
      const s: P2[] = [];
      for (let t = 1; t < 15; t++) s.push([x + Math.cos(t * 0.9) * t * 0.55 * u, ey + Math.sin(t * 0.9) * t * 0.55 * u]);
      p.stroke(s, 2.4 * u);
    }
  }
};

/** open "D" mouth with a white teeth band (+ tongue) */
const dmouth = (p: Pen, mx: number, y: number, rx: number, ry: number, u: number, tongue = false, teeth = 3) => {
  p.ell(mx, y, rx, ry, MOUTH, 0, 0, 180);
  p.clip([[mx - rx, y], [mx + rx, y], [mx + rx, y + teeth * u], [mx - rx, y + teeth * u]], () => p.ell(mx, y, rx, ry, WHITE, 0, 0, 180));
  if (tongue) p.ell(mx + 2 * u, y + 0.68 * ry, 0.42 * rx, 0.3 * ry, TONGUE, 0);
  p.ell(mx, y, rx, ry, null, 3 * u, 0, 180);
};

const mouth = (p: Pen, kind: MouthK, mx: number, my: number, u: number, k = 1) => {
  const mw = 4 * u;
  switch (kind) {
    case "dash": p.stroke([[mx - 5.5 * u * k, my], [mx + 5.5 * u * k, my - 0.8 * u]], mw); break;
    case "frown": p.arc(mx, my + 4 * u, 8 * u * k, 4.5 * u, 200, 340, mw); break;
    case "smirk": p.arc(mx + 2 * u, my - 3 * u, 9 * u * k, 5 * u, 10, 150, mw); p.stroke([[mx + 10.5 * u * k, my - 3.5 * u], [mx + 12.5 * u * k, my - 5.5 * u]], 2.6 * u); break;
    case "smile": p.arc(mx, my - 3 * u, 9 * u * k, 5 * u, 20, 160, mw); break;
    case "smileWide": p.arc(mx, my - 4 * u, 12 * u * k, 7 * u, 15, 165, mw); break;
    case "grin": dmouth(p, mx, my - u, 12 * u * k, 8 * u, u); break;
    case "laugh": dmouth(p, mx, my - 2 * u, 17 * u * k, 14 * u, u, true, 4); break;
    case "gape": dmouth(p, mx, my - 2 * u, 14 * u * k, 16 * u, u, true, 3.5); break;
    case "toothy": {
      dmouth(p, mx, my - 2 * u, 15 * u * k, 9 * u, u, false, 5);
      for (const j of [-2, -1, 0, 1, 2]) p.stroke([[mx + j * 5 * u * k, my - 2 * u], [mx + j * 5 * u * k, my + 2.6 * u]], 1.1 * u);
      break;
    }
    case "yell": {
      // big trapezoid shout: top teeth band, tongue, slight downturn
      const pts: P2[] = [[mx - 13 * u * k, my - 5 * u], [mx + 13 * u * k, my - 5 * u], [mx + 9 * u * k, my + 13 * u], [mx - 9 * u * k, my + 13 * u]];
      const sm = curve(pts[0], [mx, my - 7 * u], pts[1], 8).concat(curve(pts[1], [mx + 13 * u * k, my + 7 * u], pts[2], 6).slice(1), curve(pts[2], [mx, my + 16 * u], pts[3], 8).slice(1), curve(pts[3], [mx - 13 * u * k, my + 7 * u], pts[0], 6).slice(1));
      p.poly(sm, MOUTH, 0);
      p.clip(sm, () => { p.g.fillStyle = WHITE; p.poly([[mx - 16 * u, my - 9 * u], [mx + 16 * u, my - 9 * u], [mx + 16 * u, my - 1 * u], [mx - 16 * u, my - 1 * u]], WHITE, 0); p.ell(mx + 1 * u, my + 13 * u, 8 * u * k, 5 * u, TONGUE, 0); });
      p.poly(sm, null, 3 * u);
      break;
    }
    case "grimace": {
      const r = rrect(mx - 14 * u * k, my - 5 * u, mx + 14 * u * k, my + 5 * u, 4 * u, 4);
      p.poly(r, WHITE, 3 * u);
      p.stroke([[mx - 13 * u * k, my], [mx + 13 * u * k, my]], 1.4 * u);
      for (const j of [-2, -1, 0, 1, 2]) p.stroke([[mx + j * 5 * u * k, my - 5 * u], [mx + j * 5 * u * k, my + 5 * u]], 1.2 * u);
      break;
    }
    case "sneer": {
      p.poly([[mx - 10 * u * k, my + 1 * u], [mx + 2 * u, my - 1 * u], [mx + 11 * u * k, my - 7 * u], [mx + 9 * u * k, my - 1 * u], [mx + 2 * u, my + 3 * u]], WHITE, 2.6 * u);
      p.stroke([[mx + 3 * u, my - 1 * u], [mx + 3 * u, my + 2.5 * u]], 1 * u);
      break;
    }
    case "o": p.ell(mx + 4 * u, my, 3.5 * u, 4 * u, MOUTH, 2.8 * u); break;
    case "O": p.ell(mx, my + 2 * u, 9 * u * k, 11 * u, MOUTH, 3.2 * u); p.ell(mx, my + 8 * u, 5 * u * k, 3.5 * u, TONGUE, 0); break;
    case "wave": { const s: P2[] = []; for (let i = 0; i <= 12; i++) s.push([mx - 9 * u * k + i * 1.5 * u * k, my + 1.5 * u * Math.sin(i * 1.3)]); p.stroke(s, 3 * u); break; }
    case "teeth":
      p.poly([[mx - 12 * u * k, my - 4 * u], [mx + 12 * u * k, my - 4 * u], [mx + 11 * u * k, my + 4 * u], [mx - 11 * u * k, my + 4 * u]], WHITE, 3 * u);
      for (const j of [-1, 0, 1]) p.stroke([[mx + j * 6 * u * k, my - 4 * u], [mx + j * 6 * u * k, my + 4 * u]], 1.5 * u);
      break;
    case "lick": p.arc(mx, my - 3 * u, 8 * u * k, 4.5 * u, 20, 160, mw); p.ell(mx + 6 * u * k, my + 3 * u, 3.6 * u, 4.6 * u, TONGUE, 2.4 * u); break;
    case "small": p.ell(mx, my + 1 * u, 5.5 * u * k, 4.5 * u, MOUTH, 2.8 * u); break;
    case "tight": p.stroke([[mx - 8 * u * k, my + 1 * u], [mx - 3 * u * k, my - 0.5 * u], [mx + 3 * u * k, my - 0.5 * u], [mx + 8 * u * k, my + 1 * u]], 4.2 * u); break;
  }
};

/** brow: tapered stroke; bushy coloured brows get an ink rim */
const brow = (p: Pen, a: P2, b: P2, u: number, col: string, bushy: boolean) => {
  if (bushy) { taper(p, a, b, 10 * u, 6 * u); taper(p, a, b, 7 * u, 3.5 * u, col); }
  else taper(p, a, b, 6 * u, 3 * u, col);
};

/** moustache by style; mx = mouth centre, cy = eye line */
const stacheDraw = (p: Pen, o: Outfit, mx: number, cy: number, u: number) => {
  const m = o.moustache!;
  if (m.startsWith("brush:")) { p.poly([[mx - 6 * u, cy + 10 * u], [mx + 6 * u, cy + 10 * u], [mx + 5.5 * u, cy + 16 * u], [mx - 5.5 * u, cy + 16 * u]], m.slice(6), 1.2 * u); return; }
  const st = o.stache ?? (o.build === "stout" ? "walrus" : "plain");
  if (st === "walrus") {
    const top = curve([mx - 23 * u, cy + 25 * u], [mx, cy + 7 * u], [mx + 23 * u, cy + 25 * u], 12), bot: P2[] = [];
    for (let i = 0; i <= 8; i++) { const x = mx + 23 * u - (46 * u * i) / 8; bot.push([x, cy + 19 * u - 3 * u * Math.cos(((x - mx) / (23 * u)) * 1.4) + (i % 2 ? 3.5 * u : 0)]); }
    const sh = [...top, ...bot];
    p.poly(sh, m, 2 * u);
    for (const d of [-12, -5, 2, 9]) p.stroke([[mx + d * u, cy + 13 * u], [mx + (d - 1.5) * u, cy + 19 * u]], 1.1 * u, shade(m, 0.78));
  } else if (st === "handlebar") {
    for (const pass of [0, 1]) for (const s of [-1, 1]) {
      const e = pass ? 0 : 3 * u, c = pass ? m : INK;
      taper(p, [mx + s * 1.5 * u, cy + 12.5 * u], [mx + s * 15 * u, cy + 15 * u], 6 * u + e, 3 * u + e, c);
      taper(p, [mx + s * 15 * u, cy + 15 * u], [mx + s * 21 * u, cy + 8 * u], 3 * u + e, 1.4 * u + e, c);
    }
  } else if (st === "pencil") {
    p.stroke([[mx - 10 * u, cy + 14 * u], [mx - 1 * u, cy + 12.5 * u]], 2.2 * u, m); p.stroke([[mx + 1 * u, cy + 12.5 * u], [mx + 10 * u, cy + 14 * u]], 2.2 * u, m);
  } else for (const s of [-1, 1]) taper(p, [mx + s * 1.5 * u, cy + 12.5 * u], [mx + s * 15 * u, cy + 15 * u], 4.5 * u, 1.6 * u, m);
};

const noseDraw = (p: Pen, o: Outfit, nx: number, ny: number, u: number, skin: string, facing: number) => {
  const k = o.nose ?? "button", tint = mul(skin, [0.98, 0.84, 0.8]);
  if (k === "button") { p.arc(nx, ny + 1 * u, 4.5 * u, 3 * u, 20, 160, 2.6 * u); return; }
  if (k === "long") {
    const s = facing || 1;
    p.poly([[nx - s * 3 * u, ny - 12 * u], [nx + s * 9 * u, ny + 4 * u], [nx - s * 3 * u, ny + 5 * u]], tint, 0);
    p.stroke([[nx - s * 3 * u, ny - 12 * u], [nx + s * 9 * u, ny + 4 * u], [nx - s * 3 * u, ny + 5 * u]], 2.6 * u);
    return;
  }
  const rx = (k === "big" ? 10 : 7) * u, ry = (k === "big" ? 8.5 : 6) * u;
  p.ell(nx, ny, rx, ry, k === "big" ? mul(skin, [1, 0.78, 0.74]) : tint, 0);
  p.arc(nx, ny, rx, ry, 10, 170, 2.6 * u);
  p.arc(nx, ny, rx, ry, 190, 260, 1.8 * u);
  p.ell(nx - 0.3 * rx, ny - 0.35 * ry, 0.25 * rx, 0.2 * ry, "rgba(255,255,255,0.55)", 0);
};

/** face v3 (front / 3-4). u = 1 % of the head path width W. Eyes 26u apart on the centre line, brows 20u up, mouth 20u
 *  down, nose between, everything slid toward the facing side. Optional cheeks, freckles, cigar, styled moustache. */
const faceFront = (p: Pen, cx: number, cy: number, W: number, expr: Expr, facing: number, look: number, lid: number, brim: boolean,
  skin: string, o: Outfit) => {
  const u = W / 100, F = FACE[expr], fx = cx + 7 * u * facing;
  if (o.cheeks) for (const s of [-1, 1]) p.ell(fx + s * 25 * u, cy + 13 * u, 8 * u, 5 * u, "rgba(236,96,104,0.38)", 0);
  if (o.stubble) {
    p.ell(cx + 6 * u * facing, cy + 27 * u, 30 * u, 15 * u, "rgba(70,60,70,0.16)", 0, 0, 180);
    p.ell(cx + 6 * u * facing, cy + 27 * u, 30 * u, 6 * u, "rgba(70,60,70,0.16)", 0, 180, 360);
    for (let k = 0; k < 34; k++) { const a = rnd(k, 3) * Math.PI, r = 0.55 + 0.45 * rnd(k, 4); p.dot(cx + 6 * u * facing + Math.cos(a) * 28 * u * r, cy + 26 * u + Math.sin(a) * 14 * u * r - 3 * u, 0.8 * u, "rgba(40,30,40,0.55)"); }
  }
  if (o.scar) { const sx = fx - 24 * u; p.stroke([[sx - 4 * u, cy + 4 * u], [sx + 5 * u, cy + 17 * u]], 1.6 * u, mul(skin, [0.86, 0.58, 0.58])); for (const k of [0.3, 0.6, 0.9]) { const x = sx - 4 * u + 9 * u * k, y = cy + 4 * u + 13 * u * k; p.stroke([[x - 3 * u, y + 1.5 * u], [x + 3 * u, y - 1.5 * u]], 1 * u, mul(skin, [0.86, 0.6, 0.6])); } }
  if (o.freckles) for (const s of [-1, 1]) for (const [dx, dy] of [[19, 9], [25, 12], [22, 15], [28, 8]]) p.dot(fx + s * dx * u, cy + dy * u, 1.1 * u, "#b5683e");
  const ex = (F.eye[0] === "shock" ? 12 : 13) * u, ey = cy;
  for (const side of [-1, 1]) {
    const x = fx + side * ex;
    const kind = eyeKind(F.eye[(facing ? side === facing : side > 0) ? 1 : 0], lid);
    eye(p, kind, x, ey, u, side, look, skin);
    const [dI, dO] = F.brow, by = ey - (brim ? 17 : 20) * u - (kind === "wide" ? 3 * u : 0);
    if (kind === "shock" || kind === "shockHalf") p.arc(x, by - 6 * u, 9 * u, 3 * u, 200, 340, (o.bushy ? 6 : 4) * u, o.brows ?? INK);
    else brow(p, [x - side * 8.5 * u, by + dI * u], [x + side * 8.5 * u, by + dO * u], u, o.frost ? "#eef6ff" : o.brows ?? INK, !!o.bushy || !!o.frost);
    if (o.lashes && kind !== "shock" && kind !== "shockHalf" && kind !== "wide") for (const k of [0, 1]) p.stroke([[x + side * (7 + k * 2) * u, ey - (1 + k * 3) * u], [x + side * (11 + k * 2.5) * u, ey - (4 + k * 3.5) * u]], 1.8 * u);
    if (BAGS[expr] || o.haggard) { const bc = mul(skin, [0.78, 0.62, 0.66]); p.arc(x, ey + 7 * u, 8 * u, 4 * u, 25, 155, 1.8 * u, bc); if (o.haggard) p.arc(x, ey + 10 * u, 7 * u, 4 * u, 35, 145, 1.2 * u, bc); }
    if (TEARS[expr]) { p.ell(x + side * 4 * u, ey + 11 * u, 2.6 * u, 4.2 * u, "#9fd4ff", 1.6 * u); p.ell(x + side * 6 * u, ey + 21 * u, 2.2 * u, 3.6 * u, "#9fd4ff", 1.6 * u); }
  }
  if (o.eyepatch) { // over the far eye, strap across the brow
    const s = -(facing || 1), x = fx + s * ex;
    p.stroke([[x - 30 * u * s, ey - 30 * u], [x + 22 * u * s, ey + 2 * u]], 2.4 * u);
    p.ell(x, ey + 1 * u, 11 * u, 9.5 * u, "#1a1418", 1.6 * u);
  }
  if (o.haggard) for (const k of [0, 1]) p.arc(fx, cy - 31 * u + k * 5 * u, 15 * u - k * 3 * u, 2.5 * u, 200, 340, 1.3 * u, mul(skin, [0.78, 0.64, 0.66]));
  if (o.jowls) for (const s of [-1, 1]) p.arc(fx + s * 25 * u, cy + 30 * u, 7 * u, 9 * u, s < 0 ? 100 : -10, s < 0 ? 190 : 80, 1.6 * u, mul(skin, [0.82, 0.68, 0.68]));
  if (o.jaw) { p.stroke([[fx + 1 * u, cy + 40 * u], [fx + 1 * u, cy + 45 * u]], 1.6 * u, mul(skin, [0.8, 0.66, 0.66])); p.arc(fx, cy + 36 * u, 22 * u, 6 * u, 20, 160, 1.4 * u, mul(skin, [0.84, 0.7, 0.7])); }
  const mx = cx + 8 * u * facing, my = cy + 21 * u;
  mouth(p, F.mouth, mx, my, u);
  if (o.moustache) stacheDraw(p, o, mx, cy, u);
  noseDraw(p, o, cx + 10 * u * facing, cy + 8 * u, u, skin, facing);
  if (o.cigar) {
    const s = facing || 1, a: P2 = [mx + s * 9 * u, my + 1 * u], b: P2 = [mx + s * 30 * u, my + 7 * u];
    p.band([a, b], "#8a4f2a", 5.5 * u, 1.2 * u, "round");
    p.band([lerp2(a, b, 0.2), lerp2(a, b, 0.3)], "#c8a040", 5.5 * u, 0.6 * u);
    p.ell(b[0], b[1], 2.6 * u, 2.8 * u, "#ff8a3a", 0);
    const g = p.g; g.save(); g.globalAlpha = 0.5;
    const sm: P2[] = []; for (let i = 0; i <= 10; i++) sm.push([b[0] + s * 2 * u + 3 * u * Math.sin(i * 0.9), b[1] - 4 * u - i * 3 * u]);
    p.stroke(sm, 2 * u, "#e8e4ec"); g.restore();
  }
  if (o.frost && o.moustache) for (const d of [-12, -6, 0, 6, 12]) p.poly([[mx + d * u - 2 * u, cy + 15 * u], [mx + d * u + 2 * u, cy + 15 * u], [mx + d * u, cy + 21 * u]], "#eef6ff", 0.8 * u);
  if (o.pipe) {
    // briar: short curved stem, round bowl; corncob: long straight stem, tall yellow bowl
    const s = facing || 1, a: P2 = [mx + s * 6 * u, my + 1 * u], corn = o.pipe === "corncob";
    const b: P2 = corn ? [mx + s * 30 * u, my + 12 * u] : [mx + s * 22 * u, my + 10 * u];
    p.band([a, lerp2(a, b, 0.5), b], corn ? "#3a2a20" : "#2a1e18", 3.2 * u, 1 * u, "round");
    const bw = corn ? 8 * u : 7 * u, bh = corn ? 18 * u : 11 * u, bx = b[0] + s * bw * 0.6, top = b[1] - bh * (corn ? 0.75 : 0.5);
    p.poly(rrect(bx - bw, top, bx + bw, top + bh, corn ? 2.5 * u : 5 * u, 4), corn ? "#e0b860" : "#6a3a22", 1.6 * u);
    if (corn) for (let k = 1; k < 5; k++) p.stroke([[bx - bw + 1.5 * u, top + (k * bh) / 5], [bx + bw - 1.5 * u, top + (k * bh) / 5]], 0.8 * u, "#b08838");
    else p.ell(bx - 2 * u, top + 4 * u, 2.5 * u, 3 * u, "rgba(255,230,200,0.35)", 0);
    p.ell(bx, top, bw, 2.2 * u, "#2a1a14", 1 * u);
    const g = p.g; g.save(); g.globalAlpha = 0.45;
    const sm: P2[] = []; for (let i = 0; i <= 10; i++) sm.push([bx + 3 * u * Math.sin(i * 0.9), top - 3 * u - i * 3 * u]);
    p.stroke(sm, 2 * u, "#e8e4ec"); g.restore();
  }
  if (o.holder) { // long cigarette holder tilted jauntily up
    const s = facing || 1, a: P2 = [mx + s * 6 * u, my + 1 * u], b: P2 = [mx + s * 40 * u, my - 14 * u], c: P2 = [mx + s * 50 * u, my - 18.5 * u];
    p.band([a, b], "#1e1a1e", 2.6 * u, 0.9 * u, "round");
    p.band([b, c], "#f4f0e6", 3.6 * u, 0.9 * u, "butt"); p.ell(c[0], c[1], 1.8 * u, 1.8 * u, "#ff8a3a", 0);
    const g = p.g; g.save(); g.globalAlpha = 0.45;
    const sm: P2[] = []; for (let i = 0; i <= 10; i++) sm.push([c[0] + s * 2 * u + 3 * u * Math.sin(i * 0.9), c[1] - 3 * u - i * 3 * u]);
    p.stroke(sm, 2 * u, "#e8e4ec"); g.restore();
  }
  if (expr === "nervous" || expr === "panic" || expr === "worried") p.ell(cx + 40 * u * (facing || 1), cy - 22 * u, 3 * u, 5 * u, "#9fd4ff", 2 * u);
  if (o.bandage) { const bx = fx + 26 * u, by = cy + 12 * u; p.poly([[bx - 9 * u, by - 3 * u], [bx + 9 * u, by - 7 * u], [bx + 10 * u, by - 2 * u], [bx - 8 * u, by + 2 * u]], "#efe0c0", 1.2 * u); p.poly([[bx - 3 * u, by - 10 * u], [bx + 2 * u, by - 10 * u], [bx + 4 * u, by + 6 * u], [bx - 1 * u, by + 6 * u]], "#efe0c0", 1.2 * u); }
  if (expr === "weep") for (const s of [-1, 1]) { p.ell(fx + s * 17 * u, cy + 11 * u, 2.8 * u, 4.5 * u, "#9fd4ff", 1.6 * u); p.ell(fx + s * 20 * u, cy + 22 * u, 2.4 * u, 3.8 * u, "#9fd4ff", 1.6 * u); }
};

/** profile face (facing screen-right): one eye, brow, nose tick, mouth near the front edge; no skin bump nose, no ear */
const faceSide = (p: Pen, hx: number, hy: number, W: number, expr: Expr, lid: number, brim: boolean, skin: string, o: Outfit) => {
  const u = W / 100, F = FACE[expr], ex = hx + 27 * u, ey = hy, moustache = o.moustache, stout = o.build === "stout";
  const kind = eyeKind(F.eye[1], lid);
  eye(p, kind, ex, ey, u, 1, 0.6, skin);
  const by = ey - (brim ? 17 : 20) * u, [dI, dO] = F.brow;
  if (kind === "shock" || kind === "shockHalf") p.arc(ex, by - 6 * u, 9 * u, 3 * u, 200, 340, 4 * u);
  else taper(p, [ex + 8 * u, by + dI * u], [ex - 7 * u, by - u + dO * u], 5 * u, 2.5 * u, o.brows ?? INK);
  p.stroke([[hx + 44 * u, hy + 4 * u], [hx + 47.5 * u, hy + 9 * u], [hx + 43 * u, hy + 10 * u]], 3 * u);
  mouth(p, F.mouth, hx + 33 * u, hy + 21 * u, u, 0.62);
  if (moustache) taper(p, [hx + 41 * u, hy + 13.5 * u], [hx + 25 * u, hy + (stout ? 11.5 : 16) * u], stout ? 5.5 * u : 4.5 * u, 1.6 * u, moustache.replace("brush:", ""));
  if (expr === "nervous") p.ell(hx - 30 * u, hy - 24 * u, 3 * u, 5 * u, "#9fd4ff", 2 * u);
  if (o.aviators) { p.poly([[ex - 9 * u, hy - 7 * u], [ex + 10 * u, hy - 8 * u], [ex + 8 * u, hy + 8 * u], [ex - 4 * u, hy + 9 * u]], "#26323e", 2 * u); p.stroke([[ex - 9 * u, hy - 6 * u], [hx - 20 * u, hy - 6 * u]], 1.8 * u, "#c8a24a"); }
  if (o.pipe || o.holder) {
    const a: P2 = [hx + 38 * u, hy + 22 * u], corn = o.pipe === "corncob";
    if (o.holder) { p.band([a, [hx + 66 * u, hy + 8 * u]], "#1e1a1e", 2.6 * u, 0.9 * u, "round"); p.band([[hx + 66 * u, hy + 8 * u], [hx + 76 * u, hy + 3 * u]], "#f4f0e6", 3.6 * u, 0.9 * u); }
    else {
      const b: P2 = [hx + (corn ? 62 : 54) * u, hy + 30 * u], bw = corn ? 7 * u : 6.5 * u, bh = corn ? 17 * u : 11 * u;
      p.band([a, b], "#2a1e18", 3 * u, 1 * u, "round");
      p.poly(rrect(b[0] - bw, b[1] - bh * 0.8, b[0] + bw, b[1] + bh * 0.2, corn ? 2 * u : 4.5 * u, 4), corn ? "#e0b860" : "#6a3a22", 1.6 * u);
    }
  }
};

// ---------------- hats ----------------
const BONNET = "#e9cf8f", BONNET_BRIM = "#d6b46a";
/** parts of a hat that sit behind the head (bonnet) */
const hatBehind = (p: Pen, o: Outfit, H: Blob, cx: number, hc: number, light: number, thick: number, ow: number, side: boolean) => {
  const W = 2 * H.a, HH = 2 * H.b, u = W / 100;
  if ((o.hat === "bald" || o.tufts) && o.hair && !side) {
    for (const s of [-1, 1]) {
      const tuft: P2[] = [];
      const big = o.hat !== "bald", r0 = big ? 0.96 : 0.9, rx = big ? 15 : 11, ry = big ? 24 : 15, yc = hc + (big ? 0.06 : -0.06) * HH;
      for (let i = 0; i <= 12; i++) { const t = i / 12, a = rad(-80 + 170 * t); tuft.push([cx + s * (H.a * r0 + rx * u * Math.cos(a) + (i % 2 ? 3.5 * u : 0)), yc + ry * u * Math.sin(a)]); }
      if (s < 0) tuft.reverse();
      p.poly(tuft, o.hair, ow * 0.7);
    }
  }
  if (o.hat === "cloche" && o.hair) {
    const bb = [...ellPts(cx, hc, H.a * 1.16, H.b * 1.08, 180, 360, 0, 32), [cx + H.a * 1.14, hc + 0.5 * H.b], [cx + H.a * 0.86, hc + 0.66 * H.b], [cx + H.a * 0.4, hc + 0.5 * H.b],
      [cx - H.a * 0.4, hc + 0.5 * H.b], [cx - H.a * 0.86, hc + 0.66 * H.b], [cx - H.a * 1.14, hc + 0.5 * H.b]] as P2[];
    p.shadedFill(bb, o.hair, mul(o.hair, SH_FELT), light, H.a * 1.16);
    p.poly(bb, null, ow * 0.85);
  }
  if (o.flaps && !side) { // cloth neck flap hanging from the cap, visible at both sides of the face
    const col = o.cap ?? "#a8955a", top = hc - 0.18 * HH, bot = hc + 0.42 * HH;
    const fl: P2[] = [[cx - H.a * 0.9, top - 0.06 * HH], [cx + H.a * 0.9, top - 0.06 * HH], [cx + H.a * 1.06, top + 0.04 * HH], [cx + H.a * 1.14, bot], [cx + H.a * 0.75, bot + 4 * u], [cx - H.a * 0.75, bot + 4 * u], [cx - H.a * 1.14, bot], [cx - H.a * 1.06, top + 0.04 * HH]];
    p.shadedFill(fl, col, mul(col, SH_FELT), light, H.a * 1.1, 0.3);
    p.poly(fl, null, ow * 0.8);
    for (const s of [-1, 1]) for (const k of [0.3, 0.6]) p.stroke([[cx + s * H.a * 1.05, top + (bot - top) * k], [cx + s * H.a * 1.14, top + (bot - top) * (k + 0.25)]], 1.2 * u, shade(col, 0.7));
  }
  if (o.hat !== "bonnet") return;
  const bb = blobPts(cx - (side ? 12 : 0) * (H.a / 50), hc - 0.07 * 2 * H.b, { ...H, a: H.a * 1.17, b: H.b * 1.13, asym: 0, egg: 0.04, seed: H.seed + 3 });
  p.shadedFill(bb, BONNET, mul(BONNET, SH_CLOTH), light, H.a * 1.17);
  p.inkRing(bb, ow * 0.85, thick);
};

const hatOn = (p: Pen, o: Outfit, hp: P2[], H: Blob, cx: number, hc: number, light: number, seed: number, facing: number, side: boolean) => {
  const W = 2 * H.a, HH = 2 * H.b, u = W / 100, crown = hc - H.b, ow = 0.85 * 5 * u;
  const a = H.rot + rad(4 * (rnd(seed, 20) - 0.5)); // tilt with the head, +-2 deg extra
  const R = (pts: P2[]) => rotPts(pts, a, cx, hc);
  const sag = (yb: number, wb: number): P2[] => {
    const base: P2[] = [];
    for (let i = 0; i <= 12; i++) { const t = i / 12; base.push([cx + wb * (2 * t - 1), yb + 3 * u * (1 - (2 * t - 1) ** 2)]); }
    return base;
  };
  if (o.hat === "shako" || o.hat === "shako_tall") {
    const tall = o.hat === "shako_tall", yb = crown + 0.25 * HH, ht = (tall ? 0.66 : 0.56) * HH, wb = 46 * u, wt = 52 * u;
    const body = R([...sag(yb, wb).reverse(), [cx - wt, yb - ht], [cx + wt, yb - ht]]);
    p.shadedFill(body, "#3a3d47", "#24262d", light, wt, 0.4);
    if (tall) p.clip(body, () => p.band(R([[cx - wt - 5 * u, yb - ht + 0.07 * HH], [cx + wt + 5 * u, yb - ht + 0.07 * HH]]), "#e8c45a", 0.06 * HH, 1.5 * u));
    p.poly(body, null, ow);
    const deg = (a * 180) / Math.PI;
    if (side) {
      p.poly(R([[cx + 36 * u, yb - 1 * u], [cx + 60 * u, yb + 8 * u], [cx + 34 * u, yb + 6 * u]]), "#16171b", 2.5 * u);
      const [tx, ty] = R([[cx + 24 * u, yb - ht - 6 * u]])[0];
      p.ell(tx, ty, 7 * u, 7 * u, "#2b7a4b", 2.5 * u);
    } else {
      const [px, py] = R([[cx + 3 * u * facing, yb + 3 * u]])[0];
      p.ell(px, py, 34 * u, 0.045 * HH, "#16171b", 2.5 * u, 0, 180, deg); // peak
      const [bx, by] = R([[cx, yb - 0.45 * ht]])[0];
      p.ell(bx, by, 7 * u, 6 * u, tall ? "#e8c45a" : "#c9ccd2", 2 * u, 0, 360, deg); // badge plate
      p.arc(bx, by, 3.5 * u, 2.8 * u, 200, 500, 1.6 * u);
      const [tx, ty] = R([[cx, yb - ht - 6 * u]])[0];
      p.ell(tx, ty, 7 * u, 7 * u, "#2b7a4b", 2.5 * u); // green tuft
    }
  } else if (o.hat === "cap" || o.hat === "hair") {
    const cut = crown + (o.hat === "cap" ? 0.3 : 0.42) * HH;
    const keep = (x: number, y: number) => y < cut || (side && o.hat === "hair" && x < cx - 6 * u && y < hc + 0.42 * H.b);
    // start the arc at the first kept point after a dropped one, so the kept run is contiguous and the cut closes it
    const n = hp.length, startIdx = Math.max(0, hp.findIndex(([x, y], i) => keep(x, y) && !keep(hp[(i + n - 1) % n][0], hp[(i + n - 1) % n][1])));
    const arc = [...hp.slice(startIdx), ...hp.slice(0, startIdx)].filter(([x, y]) => keep(x, y))
      .map(([x, y]) => [cx + (x - cx) * 1.03, hc + (y - hc) * 1.03] as P2);
    if (arc.length < 3) return;
    if (o.hat === "hair") { // scalloped lower edge
      const [x0, y0] = arc[arc.length - 1], [x1, y1] = arc[0];
      for (let i = 1; i < 6; i++) arc.push([x0 + ((x1 - x0) * i) / 6, y0 + ((y1 - y0) * i) / 6 + (i % 2 ? 4 * u : 0)]);
    }
    const col = o.hat === "cap" ? o.cap! : o.hair!;
    p.shadedFill(arc, col, mul(col, SH_FELT), light, H.a, 0.35);
    p.poly(arc, null, ow);
    if (o.hat === "hair") {
      const s = side ? -1 : facing || 1;
      p.stroke([[cx + s * 10 * u, cut - 30 * u], [cx + s * 2 * u, cut - 12 * u]], 1.2 * u);
      if (o.tufts) for (const d of [-26, -12, 16, 30]) p.stroke(R(curve([cx + d * u, cut - 34 * u], [cx + (d + 6) * u, cut - 20 * u], [cx + (d + 2) * u, cut - 6 * u], 6)), 1.4 * u, shade(o.hair!, 0.72));
      if (o.bow) { // hair bow on the far side of the crown
        const [bx, by] = R([[cx - s * 0.3 * W, crown + 0.08 * HH]])[0];
        for (const d of [-1, 1]) p.poly([[bx, by], [bx + d * 13 * u, by - 8 * u], [bx + d * 13 * u, by + 8 * u]], o.bow, 1.6 * u);
        p.ell(bx, by, 3.5 * u, 3.5 * u, o.bow, 1.4 * u);
      }
    }
    if (o.hat === "cap" && o.star && !side) {
      const [sx, sy] = R([[cx + (facing || 0) * 4 * u, cut - 0.1 * HH]])[0], st: P2[] = [];
      for (let i = 0; i < 10; i++) { const r = (i % 2 ? 0.42 : 1) * 6.5 * u, an = -Math.PI / 2 + (i * Math.PI) / 5; st.push([sx + r * Math.cos(an), sy + r * Math.sin(an)]); }
      p.poly(st, "#f2c43a", 1.2 * u);
    }
    if (o.hat === "cap") {
      const deg = (a * 180) / Math.PI;
      if (side) p.poly(R([[cx + 40 * u, cut - 2 * u], [cx + 74 * u, cut + 4 * u], [cx + 40 * u, cut + 6 * u]]), shade(col, 0.8), ow);
      else {
        const s = facing || (rnd(seed, 21) < 0.5 ? -1 : 1), [px, py] = R([[cx + s * 4 * u, cut + 1.5 * u]])[0];
        p.ell(px, py, 32 * u, 0.06 * HH, shade(col, 0.8), ow, 0, 180, deg);
      }
    }
  } else if (o.hat === "m1" || o.hat === "brodie" || o.hat === "sailor") {
    const deg = (a * 180) / Math.PI;
    if (o.hat === "m1") {
      // M1: deep olive dome over the top ~45 % of the head, thin rim, chin strap
      const col = "#5f6a3c", yb = crown + 0.42 * HH, rx = 0.6 * W, ry = 0.5 * HH, ox = side ? -4 * u : 0;
      const dome = R(ellPts(cx + ox, yb, rx, ry, 180, 360, 0, 40));
      p.shadedFill(dome, col, mul(col, SH_FELT), light, rx, 0.4);
      p.poly(dome, null, ow);
      const [rx0, ry0] = R([[cx + ox, yb]])[0];
      if (o.net) p.clip(dome, () => {
        const g = p.g; g.save(); g.globalAlpha = 0.45;
        for (let k = -8; k <= 8; k++) { p.stroke(R([[cx + k * 9 * u, yb - ry], [cx + k * 9 * u + 0.5 * ry, yb]]), 1.1 * u, "#3a3a22"); p.stroke(R([[cx + k * 9 * u, yb - ry], [cx + k * 9 * u - 0.5 * ry, yb]]), 1.1 * u, "#3a3a22"); }
        g.restore();
        for (const [dx, dy] of [[-0.3, -0.25], [0.12, -0.38], [0.36, -0.12]]) p.ell(...R([[cx + dx * W, yb + dy * HH]])[0], 5 * u, 2.5 * u, "#6a7a3a", 0.8 * u, 0, 360, 20);
      });
      p.ell(rx0, ry0, rx + (side ? 9 : 5) * u, 0.05 * HH, shade(col, 0.82), ow * 0.8, 0, 360, deg);
      if (!side) for (const sd of [-1, 1]) p.stroke(R([[cx + sd * 0.55 * W, yb + 2 * u], [cx + sd * 0.42 * W, hc + 0.8 * H.b]]), 1.6 * u, "#3b3a28");
    } else if (o.hat === "brodie") {
      // Brodie: shallow dome with a wide flat brim (reads instantly different from the M1)
      const col = o.helmCol ?? "#7a7550", yb = crown + 0.3 * HH, rx = 0.44 * W, ry = 0.33 * HH;
      const dome = R(ellPts(cx + (side ? -2 * u : 0), yb, rx, ry, 180, 360, 0, 32));
      p.shadedFill(dome, col, mul(col, SH_FELT), light, rx, 0.4);
      p.poly(dome, null, ow);
      const [bx, by] = R([[cx, yb + 1 * u]])[0];
      p.ell(bx, by, (side ? 0.82 : 0.78) * W, 0.07 * HH, shade(col, 0.9), ow * 0.9, 0, 360, deg);
      if (!side) for (const sd of [-1, 1]) p.stroke(R([[cx + sd * 0.4 * W, yb + 4 * u], [cx + sd * 0.42 * W, hc + 0.8 * H.b]]), 1.6 * u, "#3b3a28");
    } else {
      // US Navy white cap, brim turned up
      const yb = crown + 0.26 * HH;
      const top = R(ellPts(cx, yb, 0.36 * W, 0.24 * HH, 180, 360, 0, 28));
      p.shadedFill(top, "#f4f4f2", "#c9cdd8", light, 0.36 * W, 0.4);
      p.poly(top, null, ow);
      const band = R([[cx - 0.46 * W, yb - 0.08 * HH], [cx + 0.46 * W, yb - 0.08 * HH], [cx + 0.42 * W, yb + 0.05 * HH], [cx - 0.42 * W, yb + 0.05 * HH]]);
      p.poly(band, "#ffffff", ow * 0.8);
    }
  } else if (o.hat === "stahl") {
    // flared steel helmet: deep dome, skirt flaring over the ears, short visor lip; plain (no decals)
    const col = o.helmCol ?? "#4c5448", yb = crown + 0.33 * HH, deg = (a * 180) / Math.PI;
    const dome = ellPts(cx, yb, 0.56 * W, 0.44 * HH, 180, 360, 0, 32);
    const shell = R([[cx - 0.66 * W, yb + 0.2 * HH], [cx - 0.6 * W, yb + 0.04 * HH], ...dome, [cx + 0.6 * W, yb + 0.04 * HH], [cx + 0.66 * W, yb + 0.2 * HH],
      [cx + 0.5 * W, yb + 0.16 * HH], [cx + 0.42 * W, yb + 0.05 * HH], [cx, yb + 0.07 * HH], [cx - 0.42 * W, yb + 0.05 * HH], [cx - 0.5 * W, yb + 0.16 * HH]]);
    p.shadedFill(shell, col, mul(col, SH_FELT), light, 0.6 * W, 0.4);
    p.poly(shell, null, ow);
    p.stroke(R(curve([cx - 0.5 * W, yb - 0.02 * HH], [cx, yb + 0.03 * HH], [cx + 0.5 * W, yb - 0.02 * HH], 10)), 1.4 * u, shade(col, 0.7));
    const [hx0, hy0] = R([[cx - 0.24 * W, yb - 0.3 * HH]])[0]; p.ell(hx0, hy0, 0.12 * W, 0.05 * HH, "rgba(255,255,255,0.22)", 0, 0, 360, deg - 25);
    if (!side) for (const sd of [-1, 1]) p.stroke(R([[cx + sd * 0.5 * W, yb + 0.12 * HH], [cx + sd * 0.38 * W, hc + 0.8 * H.b]]), 1.6 * u, "#2a2420");
  } else if (o.hat === "chef") {
    const yb = crown + 0.2 * HH;
    const band = R([[cx - 0.36 * W, yb], [cx + 0.36 * W, yb], [cx + 0.34 * W, yb - 0.2 * HH], [cx - 0.34 * W, yb - 0.2 * HH]]);
    for (const [dx, dy, r] of [[-0.2, -0.32, 0.2], [0.2, -0.32, 0.2], [0, -0.42, 0.24]] as const) { const [qx, qy] = R([[cx + dx * W, yb + dy * HH]])[0]; p.ell(qx, qy, r * W, r * W * 0.8, "#fbfbfb", ow); }
    p.poly(band, "#ffffff", ow);
  } else if (o.hat === "bowler") {
    const yb = crown + 0.24 * HH, col = o.hatCol ?? "#2a2630";
    const dome = R(ellPts(cx, yb, 0.36 * W, 0.3 * HH, 180, 360, 0, 28));
    p.shadedFill(dome, col, mul(col, SH_FELT), light, 0.36 * W, 0.4);
    p.poly(dome, null, ow);
    const [bx, by] = R([[cx, yb]])[0];
    p.ell(bx, by, 0.5 * W, 0.05 * HH, "#1d1b22", ow, 0, 360, (a * 180) / Math.PI);
  } else if (o.hat === "tophat") {
    const yb = crown + 0.22 * HH, ht = 0.8 * HH, wb = 0.31 * W, wt = 0.33 * W, col = o.hatCol ?? "#2e2a36";
    const body = R([...sag(yb, wb).reverse(), [cx - wt, yb - ht], [cx + wt, yb - ht]]);
    p.shadedFill(body, col, mul(col, SH_FELT), light, wt, 0.4);
    p.clip(body, () => p.band(R([[cx - wt - 4 * u, yb - 0.13 * HH], [cx + wt + 4 * u, yb - 0.13 * HH]]), shade(o.jacket, 0.9), 0.14 * HH, 0.8 * u));
    p.poly(body, null, ow);
    const [bx, by] = R([[cx, yb + 1 * u]])[0];
    p.ell(bx, by, 0.45 * W, 0.05 * HH, "#1d1b22", ow, 0, 360, (a * 180) / Math.PI);
  } else if (o.hat === "bald") {
    const [sx, sy] = R([[cx - 0.17 * W, crown + 0.13 * HH]])[0];
    p.ell(sx, sy, 0.12 * W, 0.05 * HH, "rgba(255,255,255,0.6)", 0, 0, 360, -24);
    p.stroke(R([[cx + 0.06 * W, crown + 0.2 * HH], [cx + 0.16 * W, crown + 0.22 * HH]]), 1.4 * u, mul(o.skin ?? SKIN, [0.85, 0.72, 0.7]));
  } else if (o.hat === "fedora") {
    const col = o.hatCol ?? "#5a4a3a", yb = crown + 0.24 * HH, ht = 0.42 * HH, wb = 0.36 * W, wt = 0.31 * W, deg = (a * 180) / Math.PI;
    const [bx, by] = R([[cx, yb + 1 * u]])[0];
    p.ell(bx, by, 0.62 * W, 0.085 * HH, shade(col, 0.82), ow, 0, 360, deg);
    const body = R([...sag(yb, wb).reverse(), [cx - wt, yb - ht + 0.08 * HH], [cx - 0.14 * W, yb - ht], [cx, yb - ht + 0.08 * HH], [cx + 0.14 * W, yb - ht], [cx + wt, yb - ht + 0.08 * HH]]);
    p.shadedFill(body, col, mul(col, SH_FELT), light, wt, 0.4);
    p.clip(body, () => p.band(R([[cx - wb - 4 * u, yb - 0.07 * HH], [cx + wb + 4 * u, yb - 0.07 * HH]]), o.band ?? "#2a2228", 0.1 * HH, 0.8 * u));
    p.poly(body, null, ow);
    p.stroke(R([[cx, yb - ht + 0.1 * HH], [cx + 2 * u, yb - 0.2 * HH]]), 1.4 * u, shade(col, 0.7));
  } else if (o.hat === "flatcap") {
    const col = o.cap ?? o.hatCol ?? "#5a5048", s = side ? 1 : facing || (rnd(seed, 21) < 0.5 ? -1 : 1), yb = crown + 0.3 * HH, deg = (a * 180) / Math.PI;
    const dome = R(ellPts(cx + s * 4 * u, yb, 0.57 * W, 0.34 * HH, 180, 360, 0, 32));
    p.shadedFill(dome, col, mul(col, SH_FELT), light, 0.57 * W, 0.4);
    p.clip(dome, () => { const g = p.g; g.save(); g.globalAlpha = 0.25; for (let k = -6; k <= 6; k++) p.stroke(R([[cx + k * 9 * u, yb - 0.4 * HH], [cx + k * 9 * u + 6 * u, yb + 2 * u]]), 1.2 * u, shade(col, 0.6)); g.restore(); });
    p.poly(dome, null, ow);
    p.stroke(R(curve([cx - 0.32 * W, yb - 0.05 * HH], [cx + s * 6 * u, yb - 0.3 * HH], [cx + 0.34 * W, yb - 0.06 * HH], 10)), 1.4 * u, shade(col, 0.65));
    const [tx, ty] = R([[cx + s * 6 * u, yb - 0.33 * HH]])[0]; p.ell(tx, ty, 4.5 * u, 2.8 * u, shade(col, 0.8), 1.4 * u);
    if (side) p.poly(R([[cx + 40 * u, yb - 2 * u], [cx + 72 * u, yb + 5 * u], [cx + 40 * u, yb + 7 * u]]), shade(col, 0.75), ow);
    else { const [px, py] = R([[cx + s * 4 * u, yb + 1 * u]])[0]; p.ell(px, py, 0.4 * W, 0.065 * HH, shade(col, 0.75), ow, 0, 180, deg); }
  } else if (o.hat === "cloche") {
    const col = o.hatCol ?? "#8a3a4a", yb = crown + 0.21 * HH, deg = (a * 180) / Math.PI;
    const dome = R(ellPts(cx, yb, 0.55 * W, 0.4 * HH, 180, 360, 0, 32));
    p.shadedFill(dome, col, mul(col, SH_FELT), light, 0.55 * W, 0.4);
    p.clip(dome, () => p.band(R([[cx - 0.6 * W, yb - 0.07 * HH], [cx + 0.6 * W, yb - 0.07 * HH]]), o.band ?? shade(col, 0.6), 0.08 * HH, 0.8 * u));
    p.poly(dome, null, ow);
    const [bx, by] = R([[cx, yb]])[0];
    p.ell(bx, by, 0.6 * W, 0.06 * HH, shade(col, 0.85), ow * 0.8, 0, 180, deg);
    const fs = side ? -1 : -(facing || 1), [fx0, fy0] = R([[cx + fs * 0.38 * W, yb - 0.08 * HH]])[0], fc = o.flower ?? "#f2e2a8";
    for (let k = 0; k < 5; k++) { const an = (k * Math.PI * 2) / 5; p.ell(fx0 + 4.5 * u * Math.cos(an), fy0 + 4.5 * u * Math.sin(an), 3.6 * u, 3.6 * u, fc, 1.2 * u); }
    p.ell(fx0, fy0, 2.6 * u, 2.6 * u, "#e8a030", 1 * u);
  } else if (o.hat === "bonnet") {
    const [bx, by] = R([[cx + (side ? 6 * u : 0), crown + 0.16 * HH]])[0];
    p.arc(bx, by, 0.5 * W, 0.2 * HH, 200, 340, 7 * u, BONNET_BRIM);
    p.arc(bx, by, 0.5 * W + 3.5 * u, 0.2 * HH + 3.5 * u, 200, 340, 1.2 * u);
    const cy = hc + H.b * 0.98;
    p.stroke([[cx - 14 * u, cy - 4 * u], [cx, cy + 2 * u], [cx + 14 * u, cy - 4 * u]], 2 * u, BONNET_BRIM);
  }
  hatWW2(p, o, hp, H, cx, hc, light, seed, facing, side);
};
// ---------------- WW2 headgear (chapters 2-14) ----------------
/** fur tufts along an edge from a to b */
const furEdge = (p: Pen, a: P2, b: P2, u: number, col: string, n = 7) => {
  for (let i = 0; i <= n; i++) { const q = lerp2(a, b, i / n); p.stroke([[q[0] - 2.5 * u, q[1] - 3 * u], [q[0], q[1] + 2.5 * u], [q[0] + 2.5 * u, q[1] - 3 * u]], 1.2 * u, col); }
};
const hatWW2 = (p: Pen, o: Outfit, hp: P2[], H: Blob, cx: number, hc: number, light: number, seed: number, facing: number, side: boolean) => {
  const W = 2 * H.a, HH = 2 * H.b, u = W / 100, crown = hc - H.b, ow = 0.85 * 5 * u, h = o.hat ?? "";
  const a = H.rot + rad(4 * (rnd(seed, 20) - 0.5)), deg = (a * 180) / Math.PI;
  const R = (pts: P2[]) => rotPts(pts, a, cx, hc);
  const sag = (yb: number, wb: number): P2[] => { const b: P2[] = []; for (let i = 0; i <= 12; i++) { const t = i / 12; b.push([cx + wb * (2 * t - 1), yb + 3 * u * (1 - (2 * t - 1) ** 2)]); } return b; };
  const fill = (pts: P2[], col: string, sh = 0.4) => { p.shadedFill(pts, col, mul(col, SH_FELT), light, W * 0.5, sh); p.poly(pts, null, ow); };
  const star = (x: number, y: number, r: number, col: string) => { const [sx, sy] = R([[x, y]])[0], st: P2[] = []; for (let i = 0; i < 10; i++) { const rr = (i % 2 ? 0.42 : 1) * r, an = -Math.PI / 2 + (i * Math.PI) / 5; st.push([sx + rr * Math.cos(an), sy + rr * Math.sin(an)]); } p.poly(st, col, 1 * u); };
  if (o.hairUnder && o.hair && h !== "hair") hatOn(p, { ...o, hat: "hair", bow: undefined, tufts: false, hairUnder: false }, hp, H, cx, hc, light, seed, facing, side);
  const vs = side ? 1 : facing; // visor / face side offset
  if (h === "brodie" && o.helmMark && !side) {
    const [mx, my] = R([[cx, crown + 0.12 * HH]])[0], g = p.g, [X, Y] = p.P(mx, my);
    g.save(); g.fillStyle = "#f4f4f2"; g.font = `bold ${Math.round(0.17 * HH)}px Georgia, serif`; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(o.helmMark, X, Y); g.restore();
  } else if (h === "homburg") {
    const col = o.hatCol ?? "#2a2a30", yb = crown + 0.24 * HH, ht = 0.42 * HH, wb = 0.34 * W, wt = 0.3 * W, ox = side ? -4 * u : 0;
    const [bx, by] = R([[cx + ox, yb + 1 * u]])[0];
    p.ell(bx, by, 0.6 * W, 0.08 * HH, shade(col, 0.85), ow, 0, 360, deg);
    for (const s of [-1, 1]) { const [ex, ey] = R([[cx + ox + s * 0.55 * W, yb - 0.015 * HH]])[0]; p.ell(ex, ey, 0.08 * W, 0.04 * HH, shade(col, 0.95), ow * 0.6, 0, 360, deg - s * 22); }
    const body = R([...sag(yb, wb).reverse(), [cx - wt, yb - ht + 0.06 * HH], [cx - 0.1 * W, yb - ht], [cx, yb - ht + 0.05 * HH], [cx + 0.1 * W, yb - ht], [cx + wt, yb - ht + 0.06 * HH]].map(([x, y]) => [x + ox, y] as P2));
    p.shadedFill(body, col, mul(col, SH_FELT), light, wt, 0.4);
    p.clip(body, () => p.band(R([[cx - wb - 4 * u, yb - 0.07 * HH], [cx + wb + 4 * u, yb - 0.07 * HH]]), o.band ?? shade(col, 0.55), 0.11 * HH, 0.8 * u));
    p.poly(body, null, ow);
    p.stroke(R([[cx + ox, yb - ht + 0.07 * HH], [cx + ox + 1 * u, yb - 0.2 * HH]]), 1.6 * u, shade(col, 0.6));
    const [kx, ky] = R([[cx + ox - 0.24 * W, yb - 0.07 * HH]])[0]; p.ell(kx, ky, 5 * u, 3.5 * u, o.band ?? shade(col, 0.55), 1.2 * u);
  } else if (h === "peaked") {
    // officer's peaked cap: wide flat crown, coloured band, black visor; saddle = high front (continental style)
    const col = o.cap ?? "#7a6a48", bandC = o.band ?? shade(col, 0.72), vis = o.visor ?? "#1e1a1e", ox = side ? -5 * u : 0;
    const yb = crown + 0.27 * HH, bt = yb - 0.13 * HH, top = crown - (o.saddle ? 0.12 : 0.04) * HH, ry = (o.saddle ? 0.2 : 0.12) * HH;
    const cr = R([[cx + ox - 0.46 * W, bt + 1 * u], [cx + ox - 0.6 * W, top + ry * 0.6], ...ellPts(cx + ox, top + ry * 0.55, 0.62 * W, ry, 185, 355, 0, 24), [cx + ox + 0.6 * W, top + ry * 0.6], [cx + ox + 0.46 * W, bt + 1 * u]]);
    fill(cr, col);
    p.stroke(R(ellPts(cx + ox, top + ry * 0.55, 0.58 * W, ry * 0.7, 15, 165, 0, 16)), 1.4 * u, shade(col, 0.72));
    const band = R([[cx + ox - 0.47 * W, bt], [cx + ox + 0.47 * W, bt], [cx + ox + 0.46 * W, yb], [cx + ox - 0.46 * W, yb]]);
    p.poly(band, bandC, ow * 0.8);
    if (o.braid) { p.stroke(R([[cx + ox - 0.44 * W, yb - 0.025 * HH], [cx + ox + 0.44 * W, yb - 0.025 * HH]]), 2.6 * u, "#e8c45a"); for (const s of [-1, 1]) p.ell(...R([[cx + ox + s * 0.4 * W, yb - 0.025 * HH]])[0], 2.6 * u, 2.6 * u, "#e8c45a", 1 * u); }
    if (!side && (o.badge || o.star)) { const [bx, by] = R([[cx + vs * 3 * u, bt - 0.06 * HH]])[0]; if (o.star) star(cx + vs * 3 * u, bt - 0.06 * HH, 6.5 * u, o.starCol ?? "#c8202c"); else { p.ell(bx, by, 7 * u, 6 * u, o.badge!, 1.4 * u); p.ell(bx, by, 3 * u, 2.6 * u, shade(o.badge!, 0.7), 0.8 * u); } }
    if (side) { p.poly(R([[cx + ox + 0.38 * W, yb - 1 * u], [cx + ox + 0.7 * W, yb + 0.07 * HH], [cx + ox + 0.38 * W, yb + 0.06 * HH]]), vis, ow * 0.8); }
    else {
      const [vx, vy] = R([[cx + vs * 3 * u, yb]])[0];
      p.ell(vx, vy, 0.44 * W, 0.09 * HH, vis, ow * 0.8, 0, 180, deg);
      p.ell(vx - 0.12 * W, vy + 0.03 * HH, 0.12 * W, 0.015 * HH, "rgba(255,255,255,0.35)", 0, 0, 360, deg);
      if (o.braid) { const z: P2[] = []; for (let i = 0; i <= 14; i++) { const t = i / 14 - 0.5; z.push([vx + t * 0.7 * W, vy + 0.04 * HH * (1 - 4 * t * t) + (i % 2 ? 2.5 * u : -1 * u)]); } p.stroke(z, 1.8 * u, "#e8c45a"); }
    }
  } else if (h === "kepi") {
    const col = o.cap ?? "#8a7a58", yb = crown + 0.24 * HH, ht = 0.5 * HH, wb = 0.36 * W, wt = 0.32 * W, lean = side ? -8 * u : 0;
    const body = R([...sag(yb, wb).reverse(), [cx - wt + lean, yb - ht], [cx + wt + lean, yb - ht]]);
    fill(body, col);
    p.clip(body, () => {
      p.band(R([[cx - wb - 4 * u, yb - 0.07 * HH], [cx + wb + 4 * u, yb - 0.07 * HH]]), o.band ?? "#c8a24a", 0.12 * HH, 0.8 * u);
      for (const s of [-1, 1]) p.stroke(R([[cx + s * 0.18 * W, yb - 0.13 * HH], [cx + s * 0.16 * W + lean, yb - ht]]), 1.2 * u, shade(col, 0.7));
    });
    p.poly(body, null, ow);
    p.ell(...R([[cx + lean, yb - ht]])[0], wt, 0.04 * HH, shade(col, 1.12), ow * 0.8, 0, 360, deg);
    if (!side) for (const d of [-1, 1]) p.ell(...R([[cx + d * 0.07 * W, yb - 0.28 * HH]])[0], 3 * u, 3 * u, "#e8c45a", 1 * u);
    if (side) p.poly(R([[cx + 0.3 * W, yb - 1 * u], [cx + 0.62 * W, yb + 0.06 * HH], [cx + 0.3 * W, yb + 0.05 * HH]]), "#1e1a1e", ow * 0.8);
    else { const [vx, vy] = R([[cx + vs * 3 * u, yb]])[0]; p.ell(vx, vy, 0.36 * W, 0.07 * HH, "#1e1a1e", ow * 0.8, 0, 180, deg); }
  } else if (h === "ushanka") {
    const col = o.cap ?? "#7a6450", yb = crown + 0.36 * HH, dk = shade(col, 0.66);
    const dome = R(ellPts(cx, yb, 0.6 * W, 0.46 * HH, 180, 360, 0, 32));
    fill([...dome], o.hatCol ?? col);
    p.stroke(R([[cx, yb - 0.44 * HH], [cx, yb - 0.1 * HH]]), 1.2 * u, dk);
    for (const s of side ? [-1] : [-1, 1]) {
      const fl = R(rrect(cx + (s < 0 ? -0.68 : 0.46) * W, yb - 0.06 * HH, cx + (s < 0 ? -0.46 : 0.68) * W, hc + 0.44 * HH, 9 * u));
      fill(fl, col, 0.3);
      for (let k = 1; k < 5; k++) { const y = yb + k * 0.09 * HH; p.stroke(R([[cx + s * 0.52 * W, y], [cx + s * 0.6 * W, y + 3 * u]]), 1.1 * u, dk); }
      p.stroke(R([[cx + s * 0.57 * W, hc + 0.44 * HH], [cx + s * 0.55 * W, hc + 0.6 * HH]]), 1.2 * u, "#3a2a20");
    }
    const ff = side ? R(rrect(cx - 0.1 * W, yb - 0.24 * HH, cx + 0.62 * W, yb + 0.03 * HH, 10 * u)) : R(rrect(cx - 0.58 * W, yb - 0.22 * HH, cx + 0.58 * W, yb + 0.04 * HH, 12 * u));
    fill(ff, shade(col, 1.08), 0.3);
    furEdge(p, R([[cx - (side ? 0.05 : 0.5) * W, yb + 0.02 * HH]])[0], R([[cx + (side ? 0.56 : 0.5) * W, yb + 0.02 * HH]])[0], u, dk, side ? 7 : 11);
    if (o.star && !side) star(cx + vs * 3 * u, yb - 0.1 * HH, 6 * u, o.starCol ?? "#c8202c");
  } else if (h === "pilotka") {
    const col = o.cap ?? "#8a7a50", yb = crown + 0.17 * HH;
    const cap = rotPts(R([[cx - 0.42 * W, yb + 0.05 * HH], [cx - 0.36 * W, yb - 0.14 * HH], [cx - 0.1 * W, yb - 0.24 * HH], [cx + 0.18 * W, yb - 0.22 * HH], [cx + 0.4 * W, yb - 0.1 * HH], [cx + 0.44 * W, yb + 0.06 * HH]]), rad(side ? -4 : 7), cx, yb);
    fill(cap, col);
    p.stroke(rotPts(R([[cx - 0.4 * W, yb - 0.03 * HH], [cx, yb - 0.05 * HH], [cx + 0.42 * W, yb - 0.02 * HH]]), rad(side ? -4 : 7), cx, yb), 1.4 * u, shade(col, 0.66));
    if (o.star && !side) { const [sx, sy] = rotPts(R([[cx + vs * 4 * u - 0.12 * W, yb + 0.0 * HH]]), rad(7), cx, yb)[0]; const st: P2[] = []; for (let i = 0; i < 10; i++) { const rr = (i % 2 ? 0.42 : 1) * 5.5 * u, an = -Math.PI / 2 + (i * Math.PI) / 5; st.push([sx + rr * Math.cos(an), sy + rr * Math.sin(an)]); } p.poly(st, o.starCol ?? "#c8202c", 1 * u); }
  } else if (h === "fez") {
    const col = o.hatCol ?? "#1e1a20", yb = crown + 0.2 * HH, ht = 0.46 * HH, wb = 0.36 * W, wt = 0.27 * W;
    const body = R([...sag(yb, wb).reverse(), [cx - wt, yb - ht], [cx + wt, yb - ht]]);
    fill(body, col);
    p.ell(...R([[cx, yb - ht]])[0], wt, 0.04 * HH, shade(col, 1.25), ow * 0.8, 0, 360, deg);
    const t0 = R([[cx, yb - ht]])[0], t1 = R([[cx + 0.4 * W, yb - 0.28 * HH]])[0];
    p.stroke(curve(t0, [(t0[0] + t1[0]) / 2 + 6 * u, t0[1] - 4 * u], t1, 8), 2 * u, "#141016");
    for (let k = -3; k <= 3; k++) p.stroke([t1, [t1[0] + k * 1.6 * u, t1[1] + 0.22 * HH]], 1.6 * u, "#141016");
  } else if (h === "beret") {
    const col = o.hatCol ?? "#1e1c24", yb = crown + 0.24 * HH, s = side ? 1 : facing || 1;
    const disc = rotPts(R(ellPts(cx - s * 0.12 * W, yb - 0.17 * HH, 0.64 * W, 0.2 * HH, 0, 360, 0, 36)), -s * rad(9), cx, yb);
    p.shadedFill(disc, col, mul(col, SH_FELT), light, 0.6 * W, 0.4); p.poly(disc, null, ow);
    p.band(R(curve([cx - 0.46 * W, yb], [cx, yb + 0.04 * HH], [cx + 0.46 * W, yb], 10)), shade(col, 0.82), 0.07 * HH, 1.2 * u);
    if (o.badge) for (const k of [0, 1]) p.ell(...R([[cx + s * (0.2 + k * 0.13) * W, yb - 0.09 * HH - k * 2 * u]])[0], 4.5 * u, 5 * u, k ? "#e8c45a" : o.badge, 1.2 * u);
  } else if (h === "leather") {
    const col = o.hatCol ?? "#6a4028", yb = crown + 0.33 * HH;
    const dome = R(ellPts(cx, yb, 0.56 * W, 0.4 * HH, 180, 360, 0, 32));
    fill([...dome, ...R([[cx + 0.56 * W, yb + 0.02 * HH], [cx - 0.56 * W, yb + 0.02 * HH]])], col);
    p.stroke(R([[cx, yb - 0.38 * HH], [cx, yb]]), 1.2 * u, shade(col, 0.66));
    for (const s of side ? [-1] : [-1, 1]) {
      const ep = R(rrect(cx + (s < 0 ? -0.62 : 0.4) * W, yb - 0.04 * HH, cx + (s < 0 ? -0.4 : 0.62) * W, hc + 0.36 * HH, 8 * u));
      fill(ep, col, 0.3);
      p.ell(...R([[cx + s * 0.51 * W, hc + 0.08 * HH]])[0], 0.08 * W, 0.1 * HH, shade(col, 0.8), 1.4 * u);
      if (!side) p.stroke(R([[cx + s * 0.44 * W, hc + 0.34 * HH], [cx + s * 0.2 * W, hc + 0.5 * HH]]), 2 * u, shade(col, 0.6));
    }
    if (o.goggles !== false) {
      p.band(R(curve([cx - 0.56 * W, yb - 0.16 * HH], [cx, yb - 0.24 * HH], [cx + 0.56 * W, yb - 0.16 * HH], 10)), "#3a2a20", 4 * u, 1 * u);
      for (const s of side ? [1] : [-1, 1]) {
        const [gx, gy] = R([[cx + (side ? 0.3 : s * 0.17) * W, yb - 0.2 * HH]])[0];
        p.ell(gx, gy, 0.13 * W, 0.1 * HH, "#8a8e96", 1.6 * u); p.ell(gx, gy, 0.095 * W, 0.07 * HH, "#9cc8e0", 1.2 * u);
        p.ell(gx - 0.03 * W, gy - 0.02 * HH, 0.03 * W, 0.015 * HH, "rgba(255,255,255,0.7)", 0, 0, 360, -30);
      }
    }
  } else if (h === "bandana") {
    const col = o.cap ?? "#c8202c", yb = crown + 0.3 * HH;
    const cov = R([...ellPts(cx, yb, 0.58 * W, 0.42 * HH, 180, 360, 0, 32), [cx + 0.58 * W, yb + 0.03 * HH], [cx - 0.58 * W, yb + 0.03 * HH]]);
    p.shadedFill(cov, col, mul(col, SH_FELT), light, 0.58 * W, 0.4);
    p.clip(cov, () => fabric(p, "dots", o.patCol ?? "#ffffff", cx - 0.7 * W, cx + 0.7 * W, crown - 0.2 * HH, yb + 0.1 * HH, u));
    p.poly(cov, null, ow);
    if (o.hair && !side) for (let k = 0; k < 5; k++) p.ell(...R([[cx - 0.3 * W + k * 0.15 * W, yb + 0.05 * HH]])[0], 0.08 * W, 0.045 * HH, o.hair, 1.3 * u);
    const [kx, ky] = R([[cx + (side ? 0.2 * W : 0), crown + 0.02 * HH]])[0];
    for (const s of [-1, 1]) p.poly([[kx, ky], [kx + s * 16 * u, ky - 13 * u], [kx + s * 20 * u, ky + 2 * u]], col, 1.6 * u);
    p.ell(kx, ky, 5 * u, 5 * u, shade(col, 0.85), 1.4 * u);
  } else if (h === "nurse") {
    const yb = crown + 0.14 * HH;
    const cap = R([[cx - 0.34 * W, yb], [cx - 0.28 * W, yb - 0.2 * HH], [cx + 0.28 * W, yb - 0.2 * HH], [cx + 0.34 * W, yb]]);
    fill(cap, "#fbfbf8");
    p.stroke(R([[cx - 0.33 * W, yb - 0.05 * HH], [cx + 0.33 * W, yb - 0.05 * HH]]), 1.2 * u, "#c8ccd4");
    if (o.redcross && !side) { const [rx, ry] = R([[cx, yb - 0.12 * HH]])[0]; p.poly([[rx - 2 * u, ry - 6 * u], [rx + 2 * u, ry - 6 * u], [rx + 2 * u, ry - 2 * u], [rx + 6 * u, ry - 2 * u], [rx + 6 * u, ry + 2 * u], [rx + 2 * u, ry + 2 * u], [rx + 2 * u, ry + 6 * u], [rx - 2 * u, ry + 6 * u], [rx - 2 * u, ry + 2 * u], [rx - 6 * u, ry + 2 * u], [rx - 6 * u, ry - 2 * u], [rx - 2 * u, ry - 2 * u]], "#c8202c", 0); }
  } else if (h === "jphelm" || h === "m33") {
    const it = h === "m33", col = o.helmCol ?? (it ? "#5e6248" : "#6a6a3e"), yb = crown + (it ? 0.38 : 0.4) * HH, rx = (it ? 0.56 : 0.58) * W, ry = (it ? 0.5 : 0.48) * HH, ox = side ? -3 * u : 0;
    const domeE = ellPts(cx + ox, yb, rx, ry, 180, 360, 0, 36);
    const dome = R(it ? [[cx + ox - 0.62 * W, yb + 0.07 * HH], ...domeE, [cx + ox + 0.62 * W, yb + 0.07 * HH], [cx + ox + 0.42 * W, yb + 0.04 * HH], [cx + ox - 0.42 * W, yb + 0.04 * HH]] : domeE);
    fill(dome, col);
    if (o.net) p.clip(dome, () => { const g = p.g; g.save(); g.globalAlpha = 0.45; for (let k = -8; k <= 8; k++) { p.stroke(R([[cx + k * 9 * u, yb - ry], [cx + k * 9 * u + 0.5 * ry, yb]]), 1.1 * u, "#3a3a22"); p.stroke(R([[cx + k * 9 * u, yb - ry], [cx + k * 9 * u - 0.5 * ry, yb]]), 1.1 * u, "#3a3a22"); } g.restore(); });
    if (!it) p.ell(...R([[cx + ox, yb]])[0], rx + 4 * u, 0.045 * HH, shade(col, 0.82), ow * 0.8, 0, 360, deg);
    else for (const s of [-1, 1]) p.dot(...R([[cx + ox + s * 0.4 * W, yb - 0.12 * HH]])[0], 2 * u, shade(col, 0.6));
    const [hx0, hy0] = R([[cx - 0.22 * W, yb - 0.32 * HH]])[0]; p.ell(hx0, hy0, 0.1 * W, 0.04 * HH, "rgba(255,255,255,0.2)", 0, 0, 360, deg - 25);
    if (!side) for (const s of [-1, 1]) p.stroke(R([[cx + s * 0.5 * W, yb + 0.04 * HH], [cx + s * 0.4 * W, hc + 0.8 * H.b]]), 1.6 * u, "#3b3a28");
  } else if (h === "adrian") {
    // French Adrian helmet: dome with a front-to-back crest and a brim
    const col = o.helmCol ?? "#5a6a7a", yb = crown + 0.32 * HH, rx = 0.46 * W, ry = 0.36 * HH;
    const dome = R(ellPts(cx, yb, rx, ry, 180, 360, 0, 32));
    fill(dome, col);
    const crest = R([[cx - 0.06 * W, yb - 0.12 * HH], [cx - 0.07 * W, yb - ry - 0.04 * HH], [cx - 0.03 * W, yb - ry - 0.13 * HH], [cx + 0.03 * W, yb - ry - 0.13 * HH], [cx + 0.07 * W, yb - ry - 0.04 * HH], [cx + 0.06 * W, yb - 0.12 * HH]]);
    p.poly(crest, shade(col, 1.12), ow * 0.7); p.stroke(R([[cx, yb - ry - 0.1 * HH], [cx, yb - 0.14 * HH]]), 1.2 * u, shade(col, 0.7));
    p.ell(...R([[cx, yb]])[0], 0.66 * W, 0.06 * HH, shade(col, 0.88), ow * 0.85, 0, 360, deg);
    if (!side) p.ell(...R([[cx, yb - 0.16 * HH]])[0], 5 * u, 6 * u, shade(col, 0.8), 1.2 * u);
  } else if (h === "rogatywka") {
    // Polish square-topped field cap with a visor
    const col = o.cap ?? "#6a6a48", yb = crown + 0.26 * HH, bt = yb - 0.14 * HH, top = crown - 0.08 * HH;
    const cr = R([[cx - 0.44 * W, bt], [cx - 0.62 * W, top + 0.02 * HH], [cx, top - 0.06 * HH], [cx + 0.62 * W, top + 0.02 * HH], [cx + 0.44 * W, bt]]);
    fill(cr, col);
    p.stroke(R([[cx, top - 0.05 * HH], [cx, bt]]), 1.2 * u, shade(col, 0.66));
    p.poly(R([[cx - 0.46 * W, bt], [cx + 0.46 * W, bt], [cx + 0.45 * W, yb], [cx - 0.45 * W, yb]]), shade(col, 0.85), ow * 0.8);
    if (!side) { const [vx, vy] = R([[cx + vs * 3 * u, yb]])[0]; p.ell(vx, vy, 0.4 * W, 0.08 * HH, "#1e1a1e", ow * 0.8, 0, 180, deg); }
    else p.poly(R([[cx + 0.36 * W, yb - 1 * u], [cx + 0.66 * W, yb + 0.06 * HH], [cx + 0.36 * W, yb + 0.05 * HH]]), "#1e1a1e", ow * 0.8);
  } else if (h === "stripecap") {
    const col = o.cap ?? "#d0d4dc", yb = crown + 0.22 * HH;
    const cap = R([...sag(yb, 0.42 * W).reverse(), [cx - 0.4 * W, yb - 0.2 * HH], [cx + 0.4 * W, yb - 0.2 * HH]]);
    p.shadedFill(cap, col, mul(col, SH_FELT), light, 0.42 * W, 0.4);
    p.clip(cap, () => { p.g.fillStyle = o.patCol ?? "#4a5878"; fabric(p, "bars", o.patCol ?? "#4a5878", cx - 0.5 * W, cx + 0.5 * W, yb - 0.3 * HH, yb + 0.05 * HH, u); });
    p.poly(cap, null, ow);
  } else if (h === "headscarf") {
    const col = o.hatCol ?? "#8a4a3a", fx = cx + (side ? 10 : facing * 4) * u;
    const outer = R(ellPts(cx - (side ? 4 * u : 0), hc - 0.02 * HH, 0.6 * W, 0.6 * HH, 0, 360, 0, 40)), inner = R(ellPts(fx, hc + 0.1 * HH, side ? 0.3 * W : 0.41 * W, 0.43 * HH, 0, 360, 0, 40));
    const g = p.g; g.save(); g.beginPath();
    for (const ring of [outer, inner.slice().reverse()]) { ring.forEach(([x, y], i) => { const [X, Y] = p.P(x, y); if (i) g.lineTo(X, Y); else g.moveTo(X, Y); }); g.closePath(); }
    g.fillStyle = col; g.fill("evenodd"); g.lineWidth = ow * 0.8; g.strokeStyle = INK; g.stroke(); g.restore();
    p.stroke(R(curve([cx - 0.5 * W, hc - 0.2 * HH], [cx, crown + 0.02 * HH], [cx + 0.5 * W, hc - 0.2 * HH], 10)), 1.3 * u, shade(col, 0.7));
    if (o.patCol) p.clip(outer, () => { for (let k = 0; k < 14; k++) { const an = (k / 14) * Math.PI * 2, [qx, qy] = R([[cx + 0.52 * W * Math.cos(an), hc + 0.52 * HH * Math.sin(an)]])[0]; p.dot(qx, qy, 2.4 * u, o.patCol!); } });
    const [kx, ky] = R([[fx, hc + 0.58 * HH]])[0];
    p.poly([[kx - 8 * u, ky - 4 * u], [kx + 8 * u, ky - 4 * u], [kx + 4 * u, ky + 14 * u], [kx - 5 * u, ky + 12 * u]], col, 1.4 * u);
    p.ell(kx, ky - 3 * u, 6 * u, 5 * u, shade(col, 0.85), 1.4 * u);
  } else if (h === "swept") {
    // full hair combed straight back from a high hairline (no fringe): a raised wavy top, forehead clear, greying temples
    const col = o.hair ?? "#5a4a3a", ox = side ? -6 * u : 0, top = crown - 0.11 * HH;
    const outline: P2[] = [];
    for (let i = 0; i <= 18; i++) { const t = i / 18, an = Math.PI * (1.04 + 0.92 * t), r = 1 + 0.045 * Math.sin(t * Math.PI * 8); outline.push([cx + ox + 0.56 * W * r * Math.cos(an), crown + 0.2 * HH + 0.31 * HH * r * Math.sin(an)]); }
    const hair = R([...outline, [cx + ox + 0.5 * W, crown + 0.27 * HH], [cx + ox + 0.38 * W, crown + 0.17 * HH], [cx + ox + 0.2 * W, crown + 0.11 * HH], [cx + ox + 0.02 * W, crown + 0.13 * HH],
      [cx + ox - 0.16 * W, crown + 0.1 * HH], [cx + ox - 0.36 * W, crown + 0.16 * HH], [cx + ox - 0.5 * W, crown + 0.27 * HH]]);
    p.shadedFill(hair, col, mul(col, SH_FELT), light, 0.56 * W, 0.35); p.poly(hair, null, ow);
    const hl = mix(col, "#ffffff", 0.32), dk = shade(col, 0.68);
    p.clip(hair, () => { for (const d of [-0.34, -0.18, -0.03, 0.12, 0.27, 0.4]) {
      const x0 = cx + ox + d * W, y0 = crown + (0.14 + 0.12 * Math.abs(d)) * HH;
      p.stroke(R(curve([x0, y0], [x0 + d * 0.25 * W, top + 0.1 * HH], [x0 + d * 0.45 * W, top - 0.02 * HH], 8)), 1.5 * u, Math.abs(d) < 0.15 ? hl : dk);
    } });
    p.ell(...R([[cx + ox - 0.12 * W, top + 0.08 * HH]])[0], 0.13 * W, 0.035 * HH, "rgba(255,255,255,0.25)", 0, 0, 360, deg - 10);
    for (const s of side ? [-1] : [-1, 1]) p.poly(R([[cx + ox + s * 0.49 * W, crown + 0.24 * HH], [cx + ox + s * 0.54 * W, crown + 0.36 * HH], [cx + ox + s * 0.5 * W, crown + 0.38 * HH], [cx + ox + s * 0.46 * W, crown + 0.27 * HH]]), mix(col, "#c8c8c8", 0.4), 1 * u);
  }
};

// ---------------- bodies ----------------
/** bolt-action rifle from butt A to muzzle B: shaped wooden stock + forend, steel barrel and bolt, a sling, optional bayonet */
const rifleDraw = (p: Pen, A: P2, B: P2, u: number, bayonet: boolean, sling = "#7a6a44") => {
  const dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, nx = -uy, ny = ux;
  const at = (t: number, w: number): P2 => [A[0] + dx * t + nx * w * u, A[1] + dy * t + ny * w * u];
  const WOOD = "#8a5530", STEEL = "#6c727a";
  // sling bowing away from the stock
  p.stroke([at(0.2, 0), at(0.42, -9), at(0.66, 0)], 2.6 * u + 2.4 * u, INK); p.stroke([at(0.2, 0), at(0.42, -9), at(0.66, 0)], 2.6 * u, sling);
  p.poly([at(0.82, 1.6), at(1, 1.4), at(1, -1.4), at(0.82, -1.6)], STEEL, 1.2 * u); // barrel
  const stock: P2[] = [at(0, 6.5), at(0.06, 7), at(0.24, 3.4), at(0.33, 4.2), at(0.84, 3), at(0.84, -3), at(0.33, -3.6), at(0.24, -2.6), at(0.06, -5), at(0, -5)];
  p.poly(stock, WOOD, 1.6 * u);
  p.stroke([at(0.36, 1.2), at(0.8, 1.2)], 1.2 * u, "rgba(255,230,190,0.35)"); // grain highlight
  p.poly([at(0.01, 6.6), at(0.035, 6.8), at(0.035, -5), at(0.01, -5)], "#3a2a20", 0); // butt plate
  for (const t of [0.5, 0.74]) p.poly([at(t - 0.012, 3.4), at(t + 0.012, 3.4), at(t + 0.012, -3.4), at(t - 0.012, -3.4)], STEEL, 0.8 * u); // bands
  p.poly([at(0.33, -3.6), at(0.4, -3.6), at(0.4, -6), at(0.33, -6)], STEEL, 1 * u); // receiver
  p.stroke([at(0.38, -5.5), at(0.37, -10)], 1.8 * u, INK); p.dot(...at(0.37, -10.5), 2.2 * u, STEEL); // bolt handle
  if (bayonet) p.poly([at(0.97, -1.6), at(1.2, -0.6), at(1.2, 0.3), at(0.97, 1)], "#c8ccd4", 1.1 * u);
};

export type Arms = [P2[], P2[]];
/** held prop; for the hammer the number is the strike 0 (raised) .. 1 (struck) */
export type Prop = null | "icecream" | "shako" | "binoc" | "paper" | "cash" | "stein" | "brush" | "bread" | "case" | "cane" | "news" | "torch" | ["hammer", number]
  // WW2 (chapters 2-14): sub-machine guns held at port, pistol aimed, telephone handset at the ear, map held open, crate or
  // bundle carried in both arms, furled umbrella (left hand), grenade, presented sword (Onoda), candle, framed photo,
  // rivet gun, a flag on a pole (plain national colours), a microphone stand in front (hands stay free)
  | "ppsh" | "smg" | "pistol" | "phone" | "map" | "crate" | "bundle" | "umbrella" | "grenade" | "sword" | "candle" | "photo" | "rivet" | "mic" | ["flag", Nation];
/** plain national flags (no emblems except a small star on the Soviet one) */
export type Nation = "uk" | "fr" | "us" | "su" | "jp" | "it" | "pl" | "cn" | "nl" | "be" | "no" | "white" | "red";
/** arm gestures (front view). Single-arm gestures use the arm on the facing side (right when facing 0).
 *  WW2 additions: salute (hand to the brow, military), wave (hand up by the head), throw (arm cocked back over the head),
 *  cry (hands over the face), hug (both arms out toward the facing side), clap, pray (hands together at the chest) */
export type Pose = "point" | "pointUp" | "armsUp" | "hips" | "shrug" | "fist" | "fists" | "cheer" | "cross" | "head" | "chin" | "palms" | "collar" | "torch"
  | "salute" | "wave" | "throw" | "cry" | "hug" | "clap" | "pray";

const BUILD: Record<Build, { a: number; torso: number; legs: number; tw: number }> = {
  adult: { a: 118, torso: 1.1, legs: 1.4, tw: 0.8 },
  stout: { a: 118, torso: 1.15, legs: 1.32, tw: 0.92 },
  kid: { a: 112, torso: 0.85, legs: 1.0, tw: 0.72 },
  thin: { a: 110, torso: 1.2, legs: 1.55, tw: 0.62 },
  short: { a: 114, torso: 1.0, legs: 1.12, tw: 0.84 },
  fat: { a: 122, torso: 1.2, legs: 1.15, tw: 1.1 },
  tall: { a: 106, torso: 1.32, legs: 1.78, tw: 0.66 },
};

export type FrontOpts = {
  phase?: number; expr?: Expr; look?: number; blink?: boolean | number; lift?: number;
  /** chair = seated on a chair (realistic seat height; draws a wooden chair unless chair: false); kneel = on one knee;
   *  crouch = squatting behind cover; run = fast run with pumping arms */
  mode?: "march" | "stroll" | "stand" | "sit" | "fall" | "chair" | "kneel" | "crouch" | "run";
  /** desk in front of a seated figure (forces mode "chair"): typewriter (hands on the keys), telephone, radio set, papers, map */
  desk?: "type" | "phone" | "radio" | "papers" | "map"; chair?: boolean;
  /** flag flutter phase (prop ["flag", nation]) */
  flutter?: number;
  prop?: Prop; tilt?: number; headTilt?: number; wave?: number;
  /** gesture and how far into it (0 = arms at rest, 1 = full pose) */
  pose?: Pose; pk?: number;
  /** canvas angle the key light comes FROM (painted crescent + thick outline side) */
  light?: number; facing?: -1 | 0 | 1; seed?: number;
};

const footStroke = (p: Pen, a: P2, b: P2, w: number, col: string) => {
  if (col !== INK) p.stroke([a, b], w + 3, INK);
  p.stroke([a, b], w, col);
};
const ease = (x: number) => { const t = clamp(x, 0, 1); return t * t * (3 - 2 * t); };
const SHIRT = "#f4f0e6";
type HandK = "dot" | "fist" | "open" | "point" | "up" | "grip";

/** fabric print inside the current clip, over the box x0..x1, y0..y1 */
const fabric = (p: Pen, kind: string, col: string, x0: number, x1: number, y0: number, y1: number, u: number) => {
  const g = p.g;
  g.save(); g.globalAlpha = kind === "pinstripe" ? 0.5 : 0.55; g.strokeStyle = col; g.fillStyle = col;
  const line = (a: P2, b: P2) => { const A = p.P(a[0], a[1]), B = p.P(b[0], b[1]); g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.stroke(); };
  if (kind === "bars") { // wide prison-uniform stripes
    g.globalAlpha = 0.85;
    for (let x = x0; x < x1; x += 22 * u) { const A = p.P(x, y0), B = p.P(x + 10 * u, y0), C = p.P(x + 10 * u, y1), D = p.P(x, y1); g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.lineTo(C[0], C[1]); g.lineTo(D[0], D[1]); g.closePath(); g.fill(); }
  } else if (kind === "dots") {
    const st = 13 * u;
    for (let y = y0, r = 0; y < y1; y += st, r++) for (let x = x0 + (r % 2) * st / 2; x < x1; x += st) p.dot(x, y, 2.6 * u, col);
  } else {
    const step = (kind === "check" ? 9 : kind === "pinstripe" ? 8 : 11) * u;
    g.lineWidth = kind === "plaid" ? 3.2 * u : kind === "pinstripe" ? 0.9 * u : 2.4 * u;
    for (let x = x0; x < x1; x += step) line([x, y0], [x, y1]);
    if (kind === "plaid" || kind === "check") for (let y = y0; y < y1; y += step) line([x0, y], [x1, y]);
    if (kind === "plaid") { g.globalAlpha = 0.35; g.strokeStyle = "#f2e2a8"; g.lineWidth = 1.2 * u; for (let x = x0 + step / 2; x < x1; x += step * 2) line([x, y0], [x, y1]); for (let y = y0 + step / 2; y < y1; y += step * 2) line([x0, y], [x1, y]); }
  }
  g.restore();
};

// ---------------- WW2 props (chapters 2-14) ----------------
/** sub-machine gun from butt A to muzzle B. ppsh: wooden stock, drum magazine, perforated barrel jacket; smg: generic
 *  stick-magazine gun (Thompson / Sten / MP40 read) */
const smgDraw = (p: Pen, A: P2, B: P2, u: number, kind: "ppsh" | "smg") => {
  const dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, nx = -uy, ny = ux;
  const at = (t: number, w: number): P2 => [A[0] + dx * t + nx * w * u, A[1] + dy * t + ny * w * u];
  const WOOD = kind === "ppsh" ? "#7a4a28" : "#8a5a34", STEEL = "#4e545c";
  if (kind === "ppsh") {
    p.poly([at(0, 5.5), at(0.08, 6), at(0.3, 3), at(0.56, 3.4), at(0.56, -3.4), at(0.3, -3.2), at(0.08, -4.5), at(0, -4.5)], WOOD, 1.5 * u); // stock
    p.stroke([at(0.12, 1), at(0.5, 1)], 1.1 * u, "rgba(255,230,190,0.35)");
    p.poly([at(0.54, 3.6), at(1, 3), at(1, -3), at(0.54, -3.6)], STEEL, 1.4 * u); // jacket
    for (let k = 0; k < 5; k++) p.ell(...at(0.62 + k * 0.075, 0), 1.6 * u, 1.4 * u, "#1e2024", 0);
    const [mx, my] = at(0.46, 9); p.ell(mx, my, 9 * u, 9 * u, "#3a3e44", 1.6 * u); p.ell(mx, my, 4 * u, 4 * u, "#5a6068", 1 * u); // drum
    p.poly([at(1, 1.6), at(1.06, 1.4), at(1.06, -1.4), at(1, -1.6)], "#2a2e34", 1 * u);
  } else {
    p.poly([at(0, 5), at(0.05, 5.5), at(0.28, 2.6), at(0.42, 3), at(0.42, -3), at(0.28, -2.6), at(0.05, -4), at(0, -4)], WOOD, 1.5 * u);
    p.poly([at(0.4, 3.4), at(0.8, 3.2), at(0.8, -3.2), at(0.4, -3.4)], STEEL, 1.4 * u); // receiver
    p.poly([at(0.8, 1.4), at(1.04, 1.4), at(1.04, -1.4), at(0.8, -1.4)], "#3a3e44", 1 * u); // barrel
    p.poly([at(0.56, 3), at(0.66, 3), at(0.66, 16), at(0.56, 16)], "#2e3238", 1.2 * u); // magazine
    p.poly([at(0.44, 3), at(0.5, 3), at(0.5, 8), at(0.44, 8)], WOOD, 1 * u); // grip
  }
};
/** pistol in a hand at H, pointing along s (+1 right / -1 left) */
const pistolDraw = (p: Pen, H: P2, s: number, u: number) => {
  const [x, y] = H;
  p.poly([[x - s * 3 * u, y - 6 * u], [x + s * 24 * u, y - 6 * u], [x + s * 24 * u, y - 1 * u], [x + s * 5 * u, y - 1 * u], [x + s * 2 * u, y + 9 * u], [x - s * 5 * u, y + 9 * u], [x - s * 3 * u, y - 1 * u]], "#2e3238", 1.4 * u);
  p.stroke([[x + s * 2 * u, y - 4.5 * u], [x + s * 20 * u, y - 4.5 * u]], 1 * u, "#6a7078");
};
/** furled umbrella from the hand H down to the ground y, crook handle */
const umbrellaDraw = (p: Pen, H: P2, gy: number, u: number) => {
  const [x, y] = H, tip: P2 = [x - 5 * u, gy];
  p.poly([[x - 2 * u, y + 14 * u], [x + 2 * u, y + 14 * u], [x + 4.5 * u, y + 30 * u], [tip[0] + 1.6 * u, gy - 26 * u], [tip[0] - 1.6 * u, gy - 26 * u], [x - 6.5 * u, y + 30 * u]], "#1e1c24", 1.4 * u);
  for (const k of [0.35, 0.6]) { const yy = y + 30 * u + (gy - 26 * u - y - 30 * u) * k; p.stroke([[x - 4 * u - 2 * k * u, yy], [x + 2 * u - 2 * k * u, yy + 6 * u]], 1 * u, "#4a4654"); }
  p.band([[tip[0], gy - 26 * u], tip], "#8a8e96", 1.6 * u, 0.8 * u, "round");
  p.band([[x, y + 15 * u], [x, y - 2 * u]], "#5a3a22", 3.6 * u, 1.2 * u, "round");
  p.arc(x + 6 * u, y - 2 * u, 6 * u, 6 * u, 180, 360, 3.6 * u + 2.4 * u); p.arc(x + 6 * u, y - 2 * u, 6 * u, 6 * u, 180, 360, 3.6 * u, "#5a3a22");
};
/** a band polygon from a to b, half width d (units of the box height), in a w x h box mapped to the unit square */
const bandUnit = (a: P2, b: P2, d: number, w: number, h: number): P2[] => {
  const ax = a[0] * w, ay = a[1] * h, bx = b[0] * w, by = b[1] * h, l = Math.hypot(bx - ax, by - ay) || 1, nx = (-(by - ay) / l) * d * h, ny = ((bx - ax) / l) * d * h;
  return [[(ax + nx) / w, (ay + ny) / h], [(bx + nx) / w, (by + ny) / h], [(bx - nx) / w, (by - ny) / h], [(ax - nx) / w, (ay - ny) / h]];
};
const starUnit = (cx: number, cy: number, r: number, asp: number): P2[] => {
  const st: P2[] = [];
  for (let i = 0; i < 10; i++) { const rr = (i % 2 ? 0.42 : 1) * r, an = -Math.PI / 2 + (i * Math.PI) / 5; st.push([cx + rr * Math.cos(an) * asp, cy + rr * Math.sin(an)]); }
  return st;
};
/** national flag in unit coords (x from the hoist), drawn into the box: hoist at (x0, y0), extends `dir` (+1 right / -1
 *  left) by w, height h, rippling with phase ph (the fly end moves most) */
export const flagCloth = (p: Pen, nation: Nation, x0: number, y0: number, w: number, h: number, ph = 0, dir = 1, ol = 6) => {
  const amp = 0.07 * h;
  const map = (x: number, y: number): P2 => [x0 + dir * x * w * (1 - 0.03 * Math.sin(ph * 1.3 + y * 3)), y0 + y * h + amp * x * Math.sin(ph + x * 5.5)];
  const warp = (pts: P2[]): P2[] => { const out: P2[] = []; pts.forEach((a, i) => { const b = pts[(i + 1) % pts.length]; for (let k = 0; k < 8; k++) out.push(map(a[0] + ((b[0] - a[0]) * k) / 8, a[1] + ((b[1] - a[1]) * k) / 8)); }); return out; };
  const R = (x0u: number, y0u: number, x1u: number, y1u: number): P2[] => [[x0u, y0u], [x1u, y0u], [x1u, y1u], [x0u, y1u]];
  const F = (pts: P2[], col: string) => p.poly(warp(pts), col, 0);
  const outline = warp(R(0, 0, 1, 1)), asp = h / w;
  p.clip(outline, () => {
    const vert = (c: string[]) => c.forEach((col, i) => F(R(i / c.length, -0.1, (i + 1) / c.length + 0.01, 1.1), col));
    const hor = (c: string[]) => c.forEach((col, i) => F(R(-0.1, i / c.length, 1.1, (i + 1) / c.length + 0.01), col));
    switch (nation) {
      case "uk": {
        F(R(-0.1, -0.1, 1.1, 1.1), "#22336e");
        for (const [a, b] of [[[0, 0], [1, 1]], [[0, 1], [1, 0]]] as [P2, P2][]) { F(bandUnit(a, b, 0.11, w, h), "#ffffff"); F(bandUnit(a, b, 0.04, w, h), "#c8202c"); }
        F(R(-0.1, 0.33, 1.1, 0.67), "#ffffff"); F(R(0.5 - 0.17 * asp, -0.1, 0.5 + 0.17 * asp, 1.1), "#ffffff");
        F(R(-0.1, 0.4, 1.1, 0.6), "#c8202c"); F(R(0.5 - 0.1 * asp, -0.1, 0.5 + 0.1 * asp, 1.1), "#c8202c");
        break;
      }
      case "fr": vert(["#25408f", "#ffffff", "#d0283a"]); break;
      case "it": vert(["#1f8a4a", "#ffffff", "#ce2b37"]); break;
      case "be": vert(["#1e1a1e", "#f6d43a", "#d0283a"]); break;
      case "nl": hor(["#c8202c", "#ffffff", "#24408a"]); break;
      case "pl": hor(["#ffffff", "#d4213d"]); break;
      case "no": F(R(-0.1, -0.1, 1.1, 1.1), "#c8202c"); F(R(-0.1, 0.36, 1.1, 0.64), "#ffffff"); F(R(0.3, -0.1, 0.3 + 0.28 * asp, 1.1), "#ffffff");
        F(R(-0.1, 0.42, 1.1, 0.58), "#24408a"); F(R(0.3 + 0.08 * asp, -0.1, 0.3 + 0.2 * asp, 1.1), "#24408a"); break;
      case "us": {
        for (let i = 0; i < 13; i++) F(R(-0.1, i / 13, 1.1, (i + 1) / 13 + 0.005), i % 2 ? "#ffffff" : "#c8202c");
        F(R(-0.1, -0.1, 0.42, 7 / 13), "#2a3670");
        for (let r = 0; r < 9; r++) for (let c = 0; c < (r % 2 ? 5 : 6); c++) { const [sx, sy] = map((c + (r % 2 ? 1 : 0.5)) * (0.4 / 6), (r + 0.6) * (7 / 13 / 9.4)); p.dot(sx, sy, Math.max(0.6, 0.018 * h), "#ffffff"); }
        break;
      }
      case "su": F(R(-0.1, -0.1, 1.1, 1.1), "#c41e26"); F(starUnit(0.16, 0.2, 0.09, asp), "#f2c43a"); break;
      case "jp": { F(R(-0.1, -0.1, 1.1, 1.1), "#fbfbf6"); const c: P2[] = []; for (let i = 0; i < 40; i++) { const a = (i / 40) * Math.PI * 2; c.push([0.5 + 0.3 * asp * Math.cos(a), 0.5 + 0.3 * Math.sin(a)]); } F(c, "#c8202c"); break; }
      case "cn": {
        F(R(-0.1, -0.1, 1.1, 1.1), "#c41e26"); F(R(-0.1, -0.1, 0.5, 0.5), "#1e2e7a");
        const sun: P2[] = []; for (let i = 0; i < 24; i++) { const r = i % 2 ? 0.1 : 0.19, a = (i / 24) * Math.PI * 2; sun.push([0.25 + r * asp * Math.cos(a), 0.25 + r * Math.sin(a)]); }
        F(sun, "#ffffff"); const c: P2[] = []; for (let i = 0; i < 24; i++) { const a = (i / 24) * Math.PI * 2; c.push([0.25 + 0.085 * asp * Math.cos(a), 0.25 + 0.085 * Math.sin(a)]); } F(c, "#1e2e7a");
        const c2: P2[] = []; for (let i = 0; i < 24; i++) { const a = (i / 24) * Math.PI * 2; c2.push([0.25 + 0.07 * asp * Math.cos(a), 0.25 + 0.07 * Math.sin(a)]); } F(c2, "#ffffff");
        break;
      }
      case "white": F(R(-0.1, -0.1, 1.1, 1.1), "#f6f4ee"); break;
      default: F(R(-0.1, -0.1, 1.1, 1.1), "#c41e26");
    }
    // folds: soft shading bands following the ripple
    const g = p.g; g.save(); g.globalAlpha = 0.16;
    for (let k = 0; k < 4; k++) { const x = 0.15 + k * 0.24; F(R(x, -0.1, x + 0.08, 1.1), "#000000"); }
    g.restore();
  });
  p.poly(outline, null, ol);
};
/** flag on a 600 x 400 canvas (hoist at the left, pole stub), for set dressing; ph = flutter phase */
export const fxFlag = (p: Pen, nation: Nation, ph = 0) => {
  p.band([[28, 10], [28, 396]], "#6a4a2a", 12, 5, "round");
  p.ell(28, 10, 12, 12, "#e8c45a", 5);
  flagCloth(p, nation, 36, 28, 540, 330, ph, 1, 8);
};
/** open map held in two hands: parchment, rolled ends, coastlines, a red arrow */
const mapSheet = (p: Pen, x0: number, y0: number, x1: number, y1: number, u: number) => {
  const sh: P2[] = [[x0, y0 + 3 * u], [x1, y0], [x1, y1], [x0, y1 + 3 * u]];
  p.poly(sh, "#ead9ac", 2 * u);
  p.clip(sh, () => {
    p.poly([[x0 + 0.1 * (x1 - x0), y0 + 0.2 * (y1 - y0)], [x0 + 0.45 * (x1 - x0), y0 + 0.1 * (y1 - y0)], [x0 + 0.6 * (x1 - x0), y0 + 0.45 * (y1 - y0)], [x0 + 0.4 * (x1 - x0), y0 + 0.8 * (y1 - y0)], [x0 + 0.15 * (x1 - x0), y0 + 0.7 * (y1 - y0)]], "#b8c48a", 1.2 * u);
    p.poly([[x0 + 0.66 * (x1 - x0), y0 + 0.15 * (y1 - y0)], [x0 + 0.95 * (x1 - x0), y0 + 0.2 * (y1 - y0)], [x0 + 0.9 * (x1 - x0), y0 + 0.75 * (y1 - y0)], [x0 + 0.7 * (x1 - x0), y0 + 0.6 * (y1 - y0)]], "#c8b47a", 1.2 * u);
    p.stroke([[x0 + 0.25 * (x1 - x0), y0 + 0.5 * (y1 - y0)], [x0 + 0.55 * (x1 - x0), y0 + 0.38 * (y1 - y0)], [x0 + 0.78 * (x1 - x0), y0 + 0.42 * (y1 - y0)]], 3 * u, "#c8202c");
    const ax = x0 + 0.78 * (x1 - x0), ay = y0 + 0.42 * (y1 - y0);
    p.poly([[ax + 6 * u, ay], [ax - 3 * u, ay - 6 * u], [ax - 3 * u, ay + 6 * u]], "#c8202c", 0);
    for (let k = 1; k < 4; k++) p.stroke([[x0 + (k * (x1 - x0)) / 4, y0], [x0 + (k * (x1 - x0)) / 4, y1]], 0.6 * u, "rgba(90,70,40,0.35)");
  });
  for (const x of [x0, x1]) p.poly(rrect(x - 5 * u, Math.min(y0, y1) - 4 * u, x + 5 * u, Math.max(y0, y1) + 7 * u, 4 * u), "#d8c490", 1.6 * u);
};
const crateDraw = (p: Pen, x0: number, y0: number, x1: number, y1: number, u: number) => {
  p.poly(rrect(x0, y0, x1, y1, 2 * u), "#a87a48", 2.2 * u);
  for (let k = 1; k < 3; k++) p.stroke([[x0 + 2 * u, y0 + ((y1 - y0) * k) / 3], [x1 - 2 * u, y0 + ((y1 - y0) * k) / 3]], 1.4 * u, "#6a4a28");
  p.band([[x0 + 3 * u, y1 - 3 * u], [x1 - 3 * u, y0 + 3 * u]], "#b88a58", 5 * u, 1.2 * u);
  for (const [x, y] of [[x0 + 5 * u, y0 + 5 * u], [x1 - 5 * u, y0 + 5 * u], [x0 + 5 * u, y1 - 5 * u], [x1 - 5 * u, y1 - 5 * u]]) p.dot(x, y, 1.6 * u, INK);
  p.poly(rrect((x0 + x1) / 2 - 10 * u, (y0 + y1) / 2 - 4 * u, (x0 + x1) / 2 + 10 * u, (y0 + y1) / 2 + 4 * u, 1 * u), "#e8d8b0", 1 * u);
};
const bundleDraw = (p: Pen, cx: number, cy: number, r: number, u: number, col = "#8a5a6a") => {
  const b = blobPts(cx, cy, { a: r, b: r * 0.8, nTop: 2.2, nBot: 2.6, egg: 0.1, asym: 0.05, rot: 0, noise: 0.04, seed: 9 });
  p.poly(b, col, 2 * u);
  p.clip(b, () => fabric(p, "check", shade(col, 0.7), cx - r, cx + r, cy - r, cy + r, u));
  p.poly(b, null, 2 * u);
  for (const s of [-1, 1]) p.poly([[cx, cy - r * 0.7], [cx + s * 12 * u, cy - r * 0.7 - 12 * u], [cx + s * 6 * u, cy - r * 0.7 + 2 * u]], col, 1.6 * u);
  p.ell(cx, cy - r * 0.68, 5 * u, 4 * u, shade(col, 0.85), 1.4 * u);
  for (const k of [-0.5, 0.2]) p.stroke([[cx + k * r, cy - 0.5 * r], [cx + (k + 0.15) * r, cy + 0.4 * r]], 1.2 * u, shade(col, 0.6));
};
/** katana in its scabbard, held horizontally (presented) */
const swordDraw = (p: Pen, x0: number, x1: number, y: number, u: number) => {
  p.poly(rrect(x0 + 34 * u, y - 4 * u, x1, y + 4 * u, 4 * u), "#2a1e1e", 1.4 * u); // scabbard
  p.poly(rrect(x1 - 10 * u, y - 4.5 * u, x1 - 2 * u, y + 4.5 * u, 2 * u), "#c8a24a", 1 * u);
  p.ell(x0 + 34 * u, y, 3 * u, 8 * u, "#c8a24a", 1.4 * u); // guard
  p.poly(rrect(x0, y - 3.5 * u, x0 + 32 * u, y + 3.5 * u, 3 * u), "#e8e0d0", 1.4 * u); // wrapped hilt
  for (let k = 1; k < 6; k++) p.stroke([[x0 + k * 5.5 * u, y - 3 * u], [x0 + k * 5.5 * u + 3 * u, y + 3 * u]], 1.2 * u, "#3a2a30");
};
const candleDraw = (p: Pen, x: number, y: number, u: number) => {
  const g = p.g, [gx, gy] = p.P(x, y - 30 * u), gr = g.createRadialGradient(gx, gy, 0, gx, gy, 40 * u);
  gr.addColorStop(0, "rgba(255,220,140,0.55)"); gr.addColorStop(1, "rgba(255,200,120,0)"); g.fillStyle = gr; g.beginPath(); g.arc(gx, gy, 40 * u, 0, Math.PI * 2); g.fill();
  p.poly(rrect(x - 5 * u, y - 22 * u, x + 5 * u, y + 8 * u, 2 * u), "#f4ecd8", 1.4 * u);
  p.stroke([[x, y - 22 * u], [x, y - 26 * u]], 1 * u);
  p.poly([[x, y - 40 * u], [x + 4 * u, y - 29 * u], [x, y - 25 * u], [x - 4 * u, y - 29 * u]], "#ffb43a", 0);
  p.poly([[x, y - 35 * u], [x + 2 * u, y - 29 * u], [x, y - 27 * u], [x - 2 * u, y - 29 * u]], "#fff2b0", 0);
};
const photoDraw = (p: Pen, x: number, y: number, u: number) => {
  p.poly(rrect(x - 16 * u, y - 40 * u, x + 16 * u, y + 2 * u, 2 * u), "#5a3a22", 1.6 * u);
  p.poly(rrect(x - 12 * u, y - 36 * u, x + 12 * u, y - 2 * u, 1 * u), "#d8ccb0", 1 * u);
  p.ell(x, y - 24 * u, 5 * u, 6 * u, "#8a7a68", 0); p.ell(x, y - 8 * u, 9 * u, 7 * u, "#8a7a68", 0, 180, 360);
};
const rivetDraw = (p: Pen, x: number, y: number, s: number, u: number) => {
  p.poly(rrect(x - 6 * u, y - 12 * u, x + 22 * u * s + (s < 0 ? 0 : 0), y - 2 * u, 3 * u).map(([a, b]) => [s > 0 ? a : 2 * x - a, b] as P2), "#7a8088", 1.4 * u);
  p.poly([[x - 4 * u, y - 4 * u], [x + 4 * u, y - 4 * u], [x + 3 * u, y + 12 * u], [x - 3 * u, y + 12 * u]], "#3a3e44", 1.2 * u);
  p.band([[x + 22 * u * s, y - 7 * u], [x + 30 * u * s, y - 7 * u]], "#a8aeb6", 2.4 * u, 0.8 * u);
  p.stroke([[x - 6 * u, y + 6 * u], [x - 14 * u, y + 30 * u]], 1.8 * u, "#2a2a30");
};
const grenadeDraw = (p: Pen, x: number, y: number, u: number) => {
  p.ell(x, y - 8 * u, 8 * u, 10 * u, "#5a6640", 1.4 * u);
  for (const k of [-4, 0, 4]) p.stroke([[x - 7 * u, y - 8 * u + k * u], [x + 7 * u, y - 8 * u + k * u]], 0.8 * u, "#3a4428");
  p.poly(rrect(x - 3 * u, y - 22 * u, x + 3 * u, y - 16 * u, 1 * u), "#8a8e96", 1 * u);
  p.arc(x + 5 * u, y - 19 * u, 4 * u, 4 * u, 0, 300, 1.2 * u, "#8a8e96");
};
/** 1940s ribbon microphone on a floor stand: head at (x, y), base at the floor gy */
const micDraw = (p: Pen, x: number, y: number, gy: number, u: number) => {
  p.band([[x, y + 10 * u], [x, gy - 6 * u]], "#8a8e96", 3 * u, 1 * u, "round");
  p.poly([[x - 22 * u, gy], [x + 22 * u, gy], [x + 10 * u, gy - 8 * u], [x - 10 * u, gy - 8 * u]], "#3a3e44", 1.4 * u);
  p.poly(rrect(x - 9 * u, y - 14 * u, x + 9 * u, y + 10 * u, 6 * u), "#c8ccd4", 1.6 * u);
  for (let k = -2; k <= 2; k++) p.stroke([[x - 6 * u, y - 2 * u + k * 4 * u], [x + 6 * u, y - 2 * u + k * 4 * u]], 1 * u, "#6a7078");
  p.arc(x, y - 2 * u, 13 * u, 15 * u, 0, 360, 1.6 * u, "#5a6068");
};
/** telephone handset from ear E to mouth M */
const handsetDraw = (p: Pen, E: P2, M: P2, u: number) => {
  p.band([E, M], "#1e1c22", 5 * u, 1.2 * u, "round");
  p.ell(E[0], E[1], 7 * u, 6 * u, "#2a2830", 1.4 * u); p.ell(M[0], M[1], 7 * u, 6 * u, "#2a2830", 1.4 * u);
};
/** wooden desk front in front of a seated figure (top at y), with its business on top */
const deskDraw = (p: Pen, kind: NonNullable<FrontOpts["desk"]>, top: number, sole: number, W: number, u: number) => {
  const x0 = 300 - 0.95 * W, x1 = 300 + 0.95 * W, wood = "#7a4a2c";
  // items behind the front edge
  if (kind === "type") {
    p.poly(rrect(300 - 0.2 * W, top - 46 * u, 300 + 0.2 * W, top - 12 * u, 2 * u), "#f6f2e6", 1.4 * u); // paper
    for (let k = 0; k < 4; k++) p.stroke([[300 - 0.15 * W, top - 40 * u + k * 6 * u], [300 + 0.12 * W, top - 40 * u + k * 6 * u]], 1 * u, "#8a8478");
    p.poly(rrect(300 - 0.3 * W, top - 18 * u, 300 + 0.3 * W, top - 8 * u, 4 * u), "#2a2830", 1.6 * u); // platen
    p.poly([[300 - 0.34 * W, top - 10 * u], [300 + 0.34 * W, top - 10 * u], [300 + 0.4 * W, top + 6 * u], [300 - 0.4 * W, top + 6 * u]], "#2e2c34", 1.8 * u);
    for (let r = 0; r < 3; r++) for (let c = 0; c < 9 - r; c++) p.ell(300 - 0.3 * W + (r * 0.035 + c * 0.075) * W, top - 5 * u + r * 4 * u, 2.2 * u, 1.6 * u, "#e8e4da", 0.6 * u);
  } else if (kind === "radio") {
    p.poly(rrect(300 - 0.42 * W, top - 44 * u, 300 + 0.42 * W, top + 2 * u, 3 * u), "#5a3a22", 1.8 * u);
    p.poly(rrect(300 - 0.36 * W, top - 38 * u, 300 - 0.02 * W, top - 6 * u, 2 * u), "#e8d8a8", 1.2 * u);
    for (let k = 0; k < 6; k++) p.stroke([[300 - 0.33 * W + k * 0.055 * W, top - 30 * u], [300 - 0.33 * W + k * 0.055 * W, top - 24 * u]], 0.8 * u, "#5a4a30");
    p.stroke([[300 - 0.2 * W, top - 34 * u], [300 - 0.16 * W, top - 12 * u]], 1.2 * u, "#c8202c");
    for (const [dx, dy] of [[0.12, -26], [0.26, -26], [0.12, -10], [0.26, -10]]) p.ell(300 + dx * W, top + dy * u, 5 * u, 5 * u, "#1e1c22", 1 * u);
  } else if (kind === "phone") {
    const px = 300 + 0.55 * W;
    p.poly([[px - 12 * u, top + 2 * u], [px + 12 * u, top + 2 * u], [px + 7 * u, top - 6 * u], [px - 7 * u, top - 6 * u]], "#1e1c22", 1.4 * u);
    p.band([[px, top - 6 * u], [px, top - 44 * u]], "#1e1c22", 4 * u, 1 * u);
    p.ell(px, top - 46 * u, 6 * u, 4 * u, "#2a2830", 1.2 * u);
    p.poly(rrect(300 - 0.5 * W, top - 10 * u, 300 - 0.1 * W, top + 1 * u, 1 * u), "#f2ecd8", 1 * u);
  } else if (kind === "map") {
    p.poly([[300 - 0.6 * W, top - 6 * u], [300 + 0.62 * W, top - 8 * u], [300 + 0.66 * W, top + 2 * u], [300 - 0.64 * W, top + 2 * u]], "#e2cf9c", 1.4 * u);
    p.stroke([[300 - 0.3 * W, top - 3 * u], [300 + 0.2 * W, top - 4 * u]], 1.6 * u, "#c8202c");
  } else {
    for (let k = 0; k < 3; k++) p.poly(rrect(300 - 0.5 * W + k * 3 * u, top - 8 * u - k * 4 * u, 300 - 0.12 * W + k * 3 * u, top + 1 * u - k * 4 * u, 1 * u), "#f2ecd8", 1 * u);
    p.ell(300 + 0.42 * W, top - 5 * u, 6 * u, 5 * u, "#2a3a5a", 1.2 * u); p.stroke([[300 + 0.42 * W, top - 8 * u], [300 + 0.48 * W, top - 30 * u]], 1.4 * u, "#e8e4da");
  }
  // the desk: top slab + front panel with drawers
  p.poly(rrect(x0 - 8 * u, top, x1 + 8 * u, top + 10 * u, 2 * u), shade(wood, 1.15), 2 * u);
  const fp: P2[] = [[x0, top + 10 * u], [x1, top + 10 * u], [x1, sole + 4 * u], [x0, sole + 4 * u]];
  p.gradFill(fp, wood, shade(wood, 0.7), rad(-120)); p.poly(fp, null, 2 * u);
  for (const [a, b] of [[x0 + 8 * u, 300 - 0.32 * W], [300 + 0.32 * W, x1 - 8 * u]]) {
    for (let k = 0; k < 3; k++) { const y = top + 18 * u + k * ((sole - top - 26 * u) / 3); p.poly(rrect(a, y, b, y + (sole - top - 34 * u) / 3, 2 * u), shade(wood, 1.06), 1.2 * u); p.poly(rrect((a + b) / 2 - 6 * u, y + 6 * u, (a + b) / 2 + 6 * u, y + 9 * u, 1 * u), "#c8a24a", 0.8 * u); }
  }
  p.poly(rrect(300 - 0.26 * W, top + 18 * u, 300 + 0.26 * W, top + 34 * u, 2 * u), shade(wood, 0.6), 1.2 * u);
};
/** simple wooden chair seen from the front, behind a seated figure (seat at y) */
const chairDraw = (p: Pen, seat: number, chin: number, sole: number, W: number, u: number) => {
  const wood = "#6a4028", x = 0.56 * W;
  for (const s of [-1, 1]) {
    p.band([[300 + s * x, chin + 0.12 * W], [300 + s * x, sole]], wood, 7 * u, 1.4 * u);
    p.ell(300 + s * x, chin + 0.12 * W, 5 * u, 5 * u, shade(wood, 1.2), 1.4 * u);
  }
  p.band([[300 - x, chin + 0.22 * W], [300 + x, chin + 0.22 * W]], shade(wood, 1.1), 8 * u, 1.4 * u);
  p.poly(rrect(300 - x - 6 * u, seat, 300 + x + 6 * u, seat + 9 * u, 2 * u), shade(wood, 1.15), 1.6 * u);
  for (const s of [-1, 1]) p.band([[300 + s * (x - 4 * u), seat + 9 * u], [300 + s * (x - 2 * u), sole]], shade(wood, 0.85), 6 * u, 1.4 * u);
};
/** medal ribbons (rows of 3) + hanging medals on the left breast (screen right) at (x, y) */
const medalsDraw = (p: Pen, n: number, x: number, y: number, u: number) => {
  const RIB = ["#c8202c", "#e8c45a", "#2a5aa8", "#3a8a4a", "#e86a3a", "#8a3a8a", "#f4f0e6", "#5a8ac8"];
  const bars = Math.min(n, 9), rows = Math.ceil(bars / 3);
  for (let i = 0; i < bars; i++) {
    const r = Math.floor(i / 3), c = i % 3, bx = x - 11 * u + c * 11 * u, by = y - (rows - 1 - r) * 5.5 * u;
    p.poly(rrect(bx - 5 * u, by - 2.5 * u, bx + 5 * u, by + 2.5 * u, 0.6 * u), RIB[(i * 3) % 8], 0.8 * u);
    p.stroke([[bx - 1.5 * u, by - 2.5 * u], [bx - 1.5 * u, by + 2.5 * u]], 1 * u, RIB[(i * 3 + 2) % 8]);
  }
  const hang = Math.max(0, Math.min(n - 9, 5));
  for (let i = 0; i < hang; i++) {
    const hx = x - 12 * u + i * 7 * u, hy = y + 8 * u;
    p.poly([[hx - 2.5 * u, hy - 3 * u], [hx + 2.5 * u, hy - 3 * u], [hx + 2 * u, hy + 4 * u], [hx - 2 * u, hy + 4 * u]], RIB[(i * 5 + 1) % 8], 0.7 * u);
    p.ell(hx, hy + 7.5 * u, 3.4 * u, 3.4 * u, i % 2 ? "#e8c45a" : "#c8ccd4", 0.9 * u);
  }
};

export const bodyFront = (p: Pen, o: Outfit, opts: FrontOpts) => {
  const { phase = 0, expr = "neutral", mode: mode0 = "march", look = 0, blink = false, lift = 60, prop = null, tilt = 0, headTilt = 0, wave,
    light = DEF_LIGHT, facing = 0, seed = 1 } = opts;
  const mode = opts.desk ? "chair" : mode0, low = mode === "chair" || mode === "kneel" || mode === "crouch";
  const Bd = BUILD[o.build ?? "adult"], skin = o.skin ?? SKIN, two = Math.PI * 2, lid = lidOf(blink);
  const H = headMod(o, headBlob(seed, Bd.a, facing)), W = 2 * H.a, HH = 2 * H.b, u = W / 100;
  const tall = (1 + Bd.torso + Bd.legs) * HH, sole = 975;
  // body bob 5 % (march) / 3 % (stroll) of the height, lowest at contact (phase 0 and 0.5)
  const bob = mode === "run" ? 0.035 * tall * Math.cos(2 * two * phase) : mode === "march" ? 0.025 * tall * Math.cos(2 * two * phase) : mode === "stroll" ? 0.015 * tall * Math.cos(2 * two * phase) : 0;
  const torsoBot = mode === "sit" ? sole - 0.2 * HH : mode === "chair" ? sole - 0.66 * Bd.legs * HH : mode === "kneel" ? sole - 0.64 * Bd.legs * HH
    : mode === "crouch" ? sole - 0.5 * Bd.legs * HH : sole - Bd.legs * HH + bob;
  const chin = torsoBot - Bd.torso * HH, hc = chin - H.b, crown = hc - H.b, hipY = torsoBot - 0.12 * HH;
  const thick = thickAngle(light), ow = 5 * u, kid = o.build === "kid";
  const footCol = o.boots;
  const legW = (kid ? 10 : o.build === "fat" ? 14 : o.build === "thin" ? 9 : 11.5) * u, hipX = (o.build === "fat" ? 20 : o.build === "stout" ? 17 : 15) * u;
  const rim = 2.2 * u;
  const limb = (pts: P2[], col: string, w: number) => { p.stroke(pts, w + 2 * rim, INK); p.stroke(pts, w, col); };
  const shoe = (a: P2, b: P2) => {
    const cx = (a[0] + b[0]) / 2, cy = (a[1] + b[1]) / 2, rx = Math.hypot(b[0] - a[0], b[1] - a[1]) / 2 + (kid ? 3 : 5) * u;
    const deg = (Math.atan2(b[1] - a[1], b[0] - a[0]) * 180) / Math.PI, dg = Math.abs(deg) > 90 ? deg - 180 : deg;
    p.ell(cx, cy - 1.5 * u, rx, (kid ? 5.5 : 6.5) * u, footCol, rim, 0, 360, dg);
    p.ell(cx + (b[0] - a[0]) * 0.18, cy - 4 * u, rx * 0.35, 1.4 * u, "rgba(255,255,255,0.32)", 0, 0, 360, dg);
  };
  const pantsCol = o.dress && low ? o.socks ?? mix(skin, "#b08870", 0.25) : o.pants;
  const leg = (pts: P2[], side: number) => {
    if (o.shorts) {
      const n = pts.length, half = pts.slice(Math.floor(n * 0.42));
      limb(half, skin, legW * 0.62);
      limb(pts.slice(Math.floor(n * 0.78)), o.socks ?? "#f4f1ea", legW * 0.7);
      limb(pts.slice(0, Math.floor(n * 0.5)), pantsCol, legW * 1.08);
    } else {
      limb(pts, side < 0 ? pantsCol : mul(pantsCol, [0.93, 0.93, 0.97]), legW);
      if (o.pantsPat) for (const k of [-0.3, 0.3]) p.stroke(pts.map(([x, y]) => [x + k * legW, y] as P2), 0.2 * legW, o.patCol ?? shade(pantsCol, 0.6));
      if (o.puttees || o.tallBoots) {
        const low = pts.slice(Math.floor(pts.length * (o.tallBoots ? 0.5 : 0.62))), col = o.tallBoots ? o.boots : o.puttees!;
        limb(low, col, legW * (o.tallBoots ? 1.08 : 0.96));
        if (o.tallBoots) p.stroke([low[1], low[low.length - 2]], 1.6 * u, "rgba(255,255,255,0.25)");
        else for (let k = 1; k < low.length - 1; k++) { const q0 = low[k]; p.stroke([[q0[0] - legW * 0.45, q0[1] + 1.5 * u], [q0[0] + legW * 0.45, q0[1] - 2.5 * u]], 1.1 * u, shade(col, 0.72)); }
      }
      if (o.patch && side > 0) { const k = pts[Math.floor(pts.length * 0.55)]; p.poly(rrect(k[0] - 4.5 * u, k[1] - 4.5 * u, k[0] + 4.5 * u, k[1] + 4.5 * u, 1.2 * u), o.patch, 1.2 * u); }
    }
  };
  // ---- legs + feet (not rotated) ----
  p.rot = null;
  if (mode === "chair" && opts.chair !== false) chairDraw(p, torsoBot - 0.02 * HH, chin, sole, W, u);
  if (mode === "chair") {
    for (const side of [-1, 1]) {
      const h: P2 = [300 + side * hipX, hipY], k: P2 = [300 + side * (hipX + 5 * u), torsoBot + 0.16 * HH], f: P2 = [300 + side * (hipX + 7 * u), sole - 4 * u];
      leg([h, lerp2(h, k, 0.5), k, lerp2(k, f, 0.33), lerp2(k, f, 0.66), f], side);
      shoe([f[0] - side * 3 * u, f[1]], [f[0] + side * 11 * u, f[1] + 0.5 * u]);
    }
  } else if (mode === "kneel") {
    // screen-left knee on the ground (boot sole showing behind it), screen-right foot planted with the knee up
    const hl: P2 = [300 - hipX, hipY], kl: P2 = [300 - hipX - 6 * u, sole - 8 * u];
    shoe([kl[0] - 6 * u, sole - 10 * u], [kl[0] - 22 * u, sole - 16 * u]);
    leg([hl, lerp2(hl, kl, 0.33), lerp2(hl, kl, 0.66), kl], -1);
    const hr: P2 = [300 + hipX, hipY], kr: P2 = [300 + hipX + 14 * u, hipY + 0.06 * HH], fr: P2 = [300 + hipX + 16 * u, sole - 4 * u];
    leg([hr, lerp2(hr, kr, 0.5), kr, lerp2(kr, fr, 0.33), lerp2(kr, fr, 0.66), fr], 1);
    shoe([fr[0] - 3 * u, fr[1]], [fr[0] + 11 * u, fr[1] + 0.5 * u]);
  } else if (mode === "crouch") {
    for (const side of [-1, 1]) {
      const h: P2 = [300 + side * hipX, hipY], k: P2 = [300 + side * (hipX + 24 * u), hipY + 0.02 * HH], f: P2 = [300 + side * (hipX + 10 * u), sole - 4 * u];
      leg([h, lerp2(h, k, 0.5), k, lerp2(k, f, 0.33), lerp2(k, f, 0.66), f], side);
      shoe([f[0] - side * 3 * u, f[1]], [f[0] + side * 11 * u, f[1] + 0.5 * u]);
    }
  } else if (mode === "sit") {
    for (const side of [-1, 1]) {
      const h: P2 = [300 + side * hipX, hipY], k: P2 = [300 + side * 36 * u, hipY + 0.2 * HH], f: P2 = [300 + side * 44 * u, sole - 8 * u];
      leg(curve(h, k, f), side);
      shoe([f[0] - side * 2 * u, f[1]], [f[0] + side * 12 * u, f[1] - 5 * u]);
    }
  } else if (mode === "fall") {
    const legs: [P2, P2, P2][] = [
      [[300 - hipX, hipY], [300 - 46 * u, hipY + 0.5 * HH], [300 - 70 * u, hipY + 0.72 * HH]],
      [[300 + hipX, hipY], [300 + 50 * u, hipY + 0.45 * HH], [300 + 76 * u, hipY + 0.22 * HH]],
    ];
    legs.forEach(([h, k, f], i) => {
      leg(curve(h, k, f), i ? 1 : -1);
      shoe(f, [f[0] + (i ? 14 : -14) * u, f[1] + (i ? -6 : 4) * u]);
    });
  } else if (o.dress) {
    for (const side of [-1, 1]) {
      const fx = 300 + side * 12 * u, fy = sole - 4 * u;
      limb([[fx, sole - 0.45 * HH], [fx + side * u, fy]], o.socks ?? mix(skin, "#b08870", 0.25), 6.5 * u);
      shoe([fx - side * 3 * u, fy], [fx + side * 10 * u, fy + u]);
    }
  } else {
    const L = mode === "run" ? lift * 2.4 : mode === "march" ? lift * 1.25 : mode === "stroll" ? lift * 0.55 : 0;
    for (const [side, ph] of [[-1, 0], [1, 0.5]] as const) {
      const up = Math.max(0, Math.sin(two * (phase + ph))) * L;
      const hx = 300 + side * hipX, fx = 300 + side * (hipX + 7 * u), fy = sole - 4 * u - up;
      const k: P2 = [(hx + fx) / 2 + side * (1.5 * u + up * 0.16), (hipY + fy) / 2 - up * 0.08];
      leg(curve([hx, hipY], k, [fx, fy]), side);
      shoe([fx - side * 3 * u, fy], [fx + side * 11 * u, fy + 0.5 * u]);
    }
  }
  // ---- upper body: rotates about the hips (tilt + a small weight-shift sway on every step) ----
  const sway = mode === "run" ? 2.4 * Math.sin(two * phase) : mode === "march" ? 1.6 * Math.sin(two * phase) : mode === "stroll" ? 1.0 * Math.sin(two * phase) : 0;
  const A = tilt + sway;
  p.rot = A ? [rad(A), 300, hipY] : null;
  const dress = !!o.dress && mode !== "sit" && mode !== "fall" && !low;
  const T: Blob = { a: ((Bd.tw / 2) * W) / 1.06, b: 0.5 * (torsoBot - (chin - 0.25 * HH)), nTop: 2.2, nBot: 2.6,
    egg: o.build === "fat" ? 0.24 : o.build === "stout" ? 0.17 : 0.12, asym: 0.04 * facing, rot: 0, noise: 0.006, seed: seed + 7 };
  const tcx = 300 + 3 * u * facing, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
  const sh = (side: number): P2 => [tcx + side * 0.85 * T.a, chin + 0.12 * HH];
  const hang = (side: number, fwd: number): [P2, P2, P2] => {
    const S = sh(side), ex = tcx + side * (1.12 * T.a + 4 * u);
    const hx = ex + side * 3 * u - side * 6 * u * Math.max(0, fwd) + side * 4 * u * Math.max(0, -fwd);
    return [S, [ex, S[1] + 0.48 * HH], [hx, chin + 1.04 * HH - Math.abs(fwd) * 9 * u]];
  };
  const sw = mode === "march" || mode === "stroll" || mode === "run" ? Math.sin(two * phase) : 0;
  // rifle at the order: butt by the right hip, held by the hanging right hand, muzzle past the crown
  const R0: P2 = [300 + 47 * u, torsoBot + 0.12 * HH], R1: P2 = [300 + 64 * u, crown - 0.32 * HH];
  const rifleAny = !!o.rifle && (mode === "march" || mode === "stand" || mode === "stroll" || mode === "run" || mode === "kneel" || mode === "crouch");
  // WW2: a gesture or a hand-held WW2 prop slings the rifle across the back instead of holding it at the order
  const busy = !!opts.pose || !!opts.desk || (Array.isArray(prop) && prop[0] === "flag") || (typeof prop === "string" && ["ppsh", "smg", "pistol", "phone", "map", "crate", "bundle", "umbrella",
    "grenade", "sword", "candle", "photo", "rivet"].includes(prop));
  const rifle = rifleAny && !busy, slung = rifleAny && busy;
  type Arm = { pts: [P2, P2, P2]; front: boolean; over?: boolean; hand: HandK; side: number; holds?: boolean };
  const hammer = Array.isArray(prop) && prop[0] === "hammer" ? prop : null, flag = Array.isArray(prop) && prop[0] === "flag" ? prop[1] : null;
  const handProp = prop === "paper" || prop === "cash" || prop === "stein" || prop === "brush" || prop === "bread" || prop === "case" || prop === "icecream" || prop === "news" || prop === "torch" || !!hammer
    || prop === "grenade" || prop === "rivet";
  // WW2: held sub-machine gun (prop, or the outfit's own when no prop / gesture), two-handed props, desk
  const fd = facing || 1, deskTop = torsoBot - 0.36 * HH;
  const gun = prop === "ppsh" || prop === "smg" ? prop : o.smg && !prop && !opts.pose && !opts.desk && mode !== "sit" && mode !== "fall" && mode !== "chair" ? o.smg : null;
  const gunA: P2 = [tcx + fd * 0.9 * T.a, torsoBot - 0.1 * HH], gunB: P2 = [tcx - fd * 1.3 * T.a, chin - 0.08 * HH];
  const twoHand = !!gun || prop === "map" || prop === "crate" || prop === "bundle" || prop === "sword" || prop === "candle" || prop === "photo" || opts.desk === "type";
  const umb = prop === "umbrella" || (!!o.umbrella && !twoHand && !prop && mode !== "sit" && mode !== "fall" && mode !== "chair");
  // ---- default arms (rest / props / rifle / wave) ----
  const defArm = (side: number): Arm => {
    const S = sh(side), A3 = (e: P2, h: P2, hand: HandK, front = false, holds = false): Arm => ({ pts: [S, e, h], front, hand, side, holds });
    if (mode === "sit") return A3([tcx + side * (1.1 * T.a + 6 * u), S[1] + 0.4 * HH], [tcx + side * (1.2 * T.a + 10 * u), torsoBot + 0.04 * HH], "dot");
    if (mode === "fall") return A3([tcx + side * (1.15 * T.a + 12 * u), S[1] - 0.25 * HH], [tcx + side * (1.3 * T.a + 24 * u), S[1] - 0.68 * HH], "open");
    if (prop === "binoc") return A3([tcx + side * (1.0 * T.a + 6 * u), S[1] + 0.32 * HH], [300 + side * 0.2 * W, chin - 0.02 * HH], "grip", true);
    if (gun) return A3([tcx + side * (1.1 * T.a + 6 * u), S[1] + (side === fd ? 0.46 : 0.3) * HH], lerp2(gunA, gunB, side === fd ? 0.28 : 0.66), "grip", true, true);
    if (prop === "map") return A3([tcx + side * (1.18 * T.a + 8 * u), S[1] + 0.38 * HH], [tcx + side * (1.0 * T.a + 4 * u), chin + 0.42 * HH], "grip", true, true);
    if (prop === "crate") return A3([tcx + side * (1.2 * T.a + 8 * u), S[1] + 0.4 * HH], [tcx + side * (1.05 * T.a + 10 * u), torsoBot - 0.22 * HH], "grip", true, true);
    if (prop === "bundle") return A3([tcx + side * (1.15 * T.a + 6 * u), S[1] + 0.42 * HH], [tcx + side * 0.62 * T.a, torsoBot - 0.28 * HH], "grip", true, true);
    if (prop === "sword") return A3([tcx + side * (1.12 * T.a + 6 * u), S[1] + 0.42 * HH], [tcx + side * 0.6 * T.a, chin + 0.36 * HH], "grip", true, true);
    if (prop === "candle") return A3([tcx + side * (1.06 * T.a + 4 * u), S[1] + 0.44 * HH], [tcx + side * 0.16 * T.a, chin + 0.46 * HH], "grip", true, true);
    if (prop === "photo") return A3([tcx + side * (1.06 * T.a + 4 * u), S[1] + 0.44 * HH], [tcx + side * 0.5 * T.a, chin + 0.5 * HH], "grip", true, true);
    if (opts.desk === "type") return A3([tcx + side * (1.12 * T.a + 8 * u), S[1] + 0.44 * HH], [300 + side * 0.17 * W, deskTop - 3 * u], "dot", true, true);
    if (prop === "phone" && side === fd) return { pts: [S, [S[0] + side * 0.36 * HH, S[1] + 0.24 * HH], [300 + side * 0.44 * W + 5 * u * facing, hc + 0.12 * HH]], front: false, over: true, hand: "grip", side, holds: true };
    if (prop === "pistol" && side === fd) return A3([S[0] + side * 0.4 * HH, S[1] - 0.02 * HH], [S[0] + side * 0.8 * HH, S[1] - 0.07 * HH], "grip", false, true);
    if (flag && side > 0) return A3([tcx + 1.15 * T.a + 14 * u, S[1] + 0.38 * HH], [tcx + 1.2 * T.a + 26 * u, chin + 0.22 * HH], "grip", false, true);
    if (opts.desk) return A3([tcx + side * (1.14 * T.a + 8 * u), S[1] + 0.42 * HH], [300 + side * 0.42 * W, deskTop + 1 * u], "dot", true);
    if (mode === "run" && !(side > 0 && (rifle || handProp || prop === "pistol" || prop === "phone")) && !(side < 0 && (umb || prop === "cane" || prop === "shako"))) {
      const k = Math.sin(two * phase) * side;
      return A3([S[0] + side * 0.16 * HH, S[1] + 0.36 * HH + 0.05 * HH * k], [S[0] + side * 0.04 * HH, S[1] + 0.22 * HH - 0.2 * HH * k], "fist");
    }
    if (side < 0) {
      if (prop === "shako") { const h = hang(-1, 0); return A3(h[1], h[2], "grip"); }
      if (prop === "cane" || umb) return A3([tcx - 1.12 * T.a - 8 * u, S[1] + 0.42 * HH], [tcx - 1.2 * T.a - 22 * u, chin + 0.86 * HH], "grip", true, umb);
      const h = hang(-1, -sw); return A3(h[1], h[2], "dot");
    }
    if (rifle) return A3([tcx + 1.12 * T.a + 5 * u, S[1] + 0.45 * HH], lerp2(R0, R1, 0.1), "grip");
    if (wave !== undefined) return A3([tcx + 1.1 * T.a + 10 * u + 3 * u * wave, S[1] - 0.22 * HH], [tcx + 1.18 * T.a + 16 * u + 12 * u * wave, S[1] - 0.6 * HH], "open");
    if (prop === "case") return A3([tcx + 1.12 * T.a + 5 * u, S[1] + 0.48 * HH], [tcx + 1.2 * T.a + 6 * u, chin + 1.02 * HH], "grip", true, true);
    if (prop === "torch") return A3([Math.max(S[0], 455) + 0.16 * HH, (S[1] + 330) / 2 + 0.06 * HH], [455, 330], "grip", false, true);
    if (prop === "icecream") return A3([tcx + 1.05 * T.a + 4 * u, S[1] + 0.45 * HH], [tcx + 0.5 * T.a, S[1] + 0.4 * HH], "grip", true, true);
    if (hammer) {
      const k = clamp(hammer[1], 0, 1);
      const E = lerp2([tcx + 1.1 * T.a + 10 * u, S[1] - 0.15 * HH], [tcx + 1.2 * T.a + 10 * u, S[1] + 0.3 * HH], k);
      const Hd = lerp2([tcx + 1.15 * T.a + 14 * u, S[1] - 0.55 * HH], [tcx + 1.45 * T.a + 22 * u, S[1] + 0.35 * HH], k);
      return A3(E, Hd, "grip", true, true);
    }
    if (handProp) return A3([tcx + 1.05 * T.a + 6 * u, S[1] + 0.42 * HH], [tcx + 0.62 * T.a, S[1] + 0.34 * HH], "grip", true, true);
    const h = hang(1, sw); return A3(h[1], h[2], "dot");
  };
  // ---- gesture arms ----
  const pose = opts.pose, pk = ease(opts.pk ?? 1), dir = facing || 1;
  const poseArm = (side: number): Omit<Arm, "side"> | null => {
    const S = sh(side), s = side, me = side === dir;
    const A3 = (e: P2, h: P2, hand: HandK, front = false, over = false) => ({ pts: [S, e, h] as [P2, P2, P2], front, over, hand });
    const hips = () => A3([S[0] + s * 0.44 * HH, S[1] + 0.3 * HH], [tcx + s * 0.98 * T.a, torsoBot - 0.34 * HH], "fist", true);
    const fist = () => A3([S[0] + s * 0.5 * HH, S[1] - 0.04 * HH], [S[0] + s * 0.5 * HH, S[1] - 0.58 * HH], "fist");
    switch (pose) {
      case "point": return me ? A3([S[0] + s * 0.4 * HH, S[1] - 0.05 * HH], [S[0] + s * 0.8 * HH, S[1] - 0.13 * HH], "point") : hips();
      case "pointUp": return me ? A3([S[0] + s * 0.4 * HH, S[1] - 0.06 * HH], [S[0] + s * 0.42 * HH, S[1] - 0.6 * HH], "up") : null;
      case "armsUp": return A3([S[0] + s * 0.34 * HH, S[1] - 0.3 * HH], [S[0] + s * 0.5 * HH, S[1] - 0.8 * HH], "open");
      case "hips": return hips();
      case "shrug": return A3([S[0] + s * 0.3 * HH, S[1] + 0.36 * HH], [S[0] + s * 0.64 * HH, S[1] + 0.14 * HH], "open");
      case "fist": return me ? fist() : null;
      case "fists": return fist();
      case "cheer": return me ? A3([S[0] + s * 0.36 * HH, S[1] - 0.26 * HH], [S[0] + s * 0.46 * HH, S[1] - 0.78 * HH], "fist") : null;
      case "cross": return A3([tcx + s * 1.08 * T.a, S[1] + 0.36 * HH], [tcx - s * 0.5 * T.a, S[1] + 0.24 * HH], "fist", true);
      case "head": return A3([S[0] + s * 0.5 * HH, S[1] - 0.12 * HH], [300 + s * 0.47 * W, hc + 0.18 * HH], "open", false, true);
      case "chin": return me ? A3([S[0] + s * 0.3 * HH, S[1] + 0.38 * HH], [300 + s * 0.1 * W + 7 * u * facing, chin + 0.04 * HH], "fist", false, true) : A3([tcx + s * 1.08 * T.a, S[1] + 0.36 * HH], [tcx - s * 0.5 * T.a, S[1] + 0.24 * HH], "fist", true);
      case "palms": return A3([S[0] + s * 0.36 * HH, S[1] + 0.32 * HH], [S[0] + s * 0.5 * HH, S[1] - 0.04 * HH], "open");
      case "collar": return me ? A3([S[0] + s * 0.32 * HH, S[1] + 0.38 * HH], [tcx + s * 0.22 * T.a, chin + 0.03 * HH], "grip", true) : null;
      case "torch": return null;
      // military salute: the right hand (screen left in front / 3-4 views) flat at the brow, elbow out
      case "salute": return side < 0 ? A3([S[0] - 0.46 * HH, S[1] - 0.1 * HH], [300 - 0.3 * W + 7 * u * facing, hc - 0.21 * HH], "open", false, true) : null;
      case "wave": return me ? A3([S[0] + s * 0.42 * HH, S[1] - 0.12 * HH], [S[0] + s * (0.5 + 0.16 * (wave ?? 0.5)) * HH, S[1] - 0.66 * HH], "open") : null;
      case "throw": return me ? A3([S[0] + s * 0.36 * HH, S[1] - 0.34 * HH], [S[0] + s * 0.08 * HH, crown - 0.1 * HH], "fist") : A3([S[0] + s * 0.4 * HH, S[1] + 0.02 * HH], [S[0] + s * 0.76 * HH, S[1] - 0.1 * HH], "open");
      case "cry": return A3([S[0] + s * 0.22 * HH, S[1] + 0.32 * HH], [300 + s * 0.15 * W + 7 * u * facing, hc + 0.08 * HH], "open", false, true);
      case "hug": return me ? A3([S[0] + s * 0.42 * HH, S[1] + 0.06 * HH], [S[0] + s * 0.8 * HH, S[1] - 0.02 * HH], "open")
        : A3([tcx + s * 0.4 * T.a, S[1] + 0.34 * HH], [tcx + dir * (1.2 * T.a + 0.3 * HH), S[1] + 0.12 * HH], "open", true);
      case "clap": return A3([tcx + s * (1.12 * T.a + 6 * u), S[1] + 0.36 * HH], [tcx + s * 5 * u, chin + 0.3 * HH], "open", true);
      case "pray": return A3([tcx + s * (1.04 * T.a + 4 * u), S[1] + 0.44 * HH], [tcx + s * 4 * u, chin + 0.26 * HH], "open", true);
      default: return null;
    }
  };
  // single-arm gestures and raised poses carry a held prop up with the hand; the others leave the holding hand alone
  const carries = pose === "fist" || pose === "cheer" || pose === "point" || pose === "pointUp" || pose === "armsUp" || pose === "fists" || pose === "shrug"
    || pose === "wave" || pose === "throw";
  const arms: Arm[] = [-1, 1].map((side) => {
    const d = defArm(side);
    if (!pose || rifle || mode === "sit" || mode === "fall" || prop === "binoc" || prop === "torch" || (d.holds && (!carries || twoHand)) || (side < 0 && (prop === "cane" || umb))) return d;
    const pa = poseArm(side);
    if (!pa) return d;
    const pts = d.pts.map((q, i) => lerp2(q, pa.pts[i], pk)) as [P2, P2, P2];
    return { ...pa, pts, side, holds: d.holds, front: pk > 0.5 ? pa.front : d.front, over: pk > 0.5 && pa.over, hand: d.holds ? "grip" : pk > 0.5 ? pa.hand : d.hand };
  });
  const sleeve = o.sleeves ?? o.jacket, armW = (kid ? 9 : o.build === "fat" ? 12.5 : o.build === "thin" ? 8.5 : 10.5) * u;
  const drawHand = (at: P2, from: P2, kind: HandK) => {
    const hr = (kid ? 6.2 : 7) * u, dx = at[0] - from[0], dy = at[1] - from[1], l = Math.hypot(dx, dy) || 1, ux = dx / l, uy = dy / l;
    if (kind === "point" || kind === "up") {
      const fd: P2 = kind === "up" ? [0.15, -1] : [ux, uy], tip: P2 = [at[0] + fd[0] * 17 * u, at[1] + fd[1] * 17 * u];
      p.stroke([at, tip], 4.8 * u + 2 * 1.6 * u, INK); p.stroke([at, tip], 4.8 * u, skin);
    }
    if (kind === "open") {
      const deg = (Math.atan2(uy, ux) * 180) / Math.PI;
      p.ell(at[0] + ux * 2 * u, at[1] + uy * 2 * u, hr * 1.25, hr * 0.95, skin, 1.8 * u, 0, 360, deg);
      p.ell(at[0] - uy * hr * 0.8, at[1] + ux * hr * 0.8, hr * 0.42, hr * 0.32, skin, 1.6 * u, 0, 360, deg - 40);
      for (const k of [-0.35, 0.05, 0.42]) p.stroke([[at[0] + ux * hr * 0.6 - uy * hr * k, at[1] + uy * hr * 0.6 + ux * hr * k], [at[0] + ux * hr * 1.45 - uy * hr * k, at[1] + uy * hr * 1.45 + ux * hr * k]], 1.1 * u);
      return;
    }
    p.ell(at[0], at[1], hr, hr * 0.92, skin, 1.8 * u);
    if (kind === "fist" || kind === "grip") p.arc(at[0] + ux * 2 * u, at[1] + uy * 2 * u, hr * 0.55, hr * 0.42, 200, 340, 1.2 * u);
  };
  const drawArm = (a: Arm) => {
    const c = curve(a.pts[0], a.pts[1], a.pts[2], 12), col = a.front || a.over ? sleeve : mul(sleeve, [0.84, 0.84, 0.9]);
    if (o.rolled) {
      limb(c.slice(6), skin, armW * 0.74);
      limb(c.slice(0, 7), col, armW);
      p.stroke([c[6], c[7]], armW * 1.12 + 2 * rim, INK); p.stroke([c[6], c[7]], armW * 1.12, shade(col, 0.92));
    } else {
      limb(c, col, armW);
      if (o.cuffs ?? !!o.lapels) { p.stroke([c[10], c[11]], armW * 0.96, SHIRT); }
      if (o.rings) for (let k = 0; k < o.rings; k++) { const a0 = lerp2(c[9], c[10], 0.1 + k * 0.28); p.stroke([a0, lerp2(c[9], c[10], 0.22 + k * 0.28)], armW * 1.02, "#e0b84a"); }
      if (o.pattern === "bars") p.stroke(c.slice(0, 11).map(([x, y]) => [x + 0.1 * armW, y] as P2), 0.3 * armW, o.patCol ?? shade(col, 0.6));
    }
    drawHand(a.pts[2], c[10], a.hand);
  };
  // behind the body: rifle, sword, arms
  if (rifle) rifleDraw(p, R0, R1, u, !!o.bayonet, o.webbing);
  if (slung) rifleDraw(p, [tcx + 0.75 * T.a, torsoBot + 0.02 * HH], [tcx - 0.95 * T.a, crown - 0.05 * HH], u, false, o.webbing);
  if (flag) {
    const hd = arms[1].pts[2], top = 24, fw = Math.min(hd[0] - 40, 270, (crown - 40) / 0.62), fh = 0.62 * fw;
    flagCloth(p, flag, hd[0] - 2 * u, top + 3 * u, fw, fh, opts.flutter ?? 0, -1, 2.4 * u);
    p.band([[hd[0] + 1 * u, hd[1] + 0.42 * HH], [hd[0] - 1 * u, top]], "#6a4a2a", 4.5 * u, 1.4 * u, "round");
    p.ell(hd[0] - 1 * u, top, 4.5 * u, 4.5 * u, "#e8c45a", 1.4 * u);
  }
  if (o.smg && !gun && mode !== "sit" && mode !== "fall") smgDraw(p, [tcx - 0.7 * T.a, torsoBot - 0.05 * HH], [tcx + 1.05 * T.a, chin - 0.42 * HH], u, o.smg);
  const skirt = o.coat ?? (o.dress && low ? o.dress : null);
  if (skirt && mode !== "sit" && mode !== "fall") {
    const y0 = torsoBot - 0.25 * HH, y1 = mode === "chair" ? torsoBot + 0.2 * HH : low ? torsoBot + 0.3 * HH : torsoBot + (o.coat ? 0.66 : 0.4) * Bd.legs * HH;
    const fl = (mode === "march" || mode === "run" ? 16 : 9) * u, vx = tcx + 3 * u * facing;
    const sk: P2[] = [[tcx - 0.95 * T.a, y0], [tcx + 0.95 * T.a, y0], [tcx + 1.08 * T.a + fl, y1], [vx + 0.3 * T.a, y1 + 2 * u], [vx - 0.3 * T.a, y1 + 2 * u], [tcx - 1.08 * T.a - fl, y1]];
    p.gradFill(sk, skirt, mul(skirt, SH_CLOTH), light, 0.3); p.poly(sk, null, ow * 0.8);
    if (o.coat) { p.stroke([[vx, y0 + 0.3 * (y1 - y0)], [vx, y1]], 1.6 * u, shade(skirt, 0.6)); p.stroke([[tcx - 1.0 * T.a - fl * 0.8, y1 - 5 * u], [tcx + 1.0 * T.a + fl * 0.8, y1 - 5 * u]], 1.2 * u, shade(skirt, 0.7)); }
    if (o.snow) for (let k = 0; k < 7; k++) { const x = tcx - 1.0 * T.a - fl + k * ((2 * T.a + 2 * fl) / 6); p.poly([[x - 7 * u, y1 - 2 * u], [x + 7 * u, y1 - 2 * u], [x, y1 + 9 * u]], skirt, 1.2 * u); }
  }
  if (o.sword && mode !== "sit") {
    const s0: P2 = [tcx - 0.75 * T.a, torsoBot - 0.2 * HH];
    p.band([s0, [s0[0] - Math.sin(rad(25)) * 0.8 * HH, s0[1] + Math.cos(rad(25)) * 0.8 * HH]], "#c9ccd2", 3 * u, 1.2 * u, "round");
  }
  if (prop === "torch") { // stick behind the raised arm, its tip under the flame card (design 462, 238)
    const hd = arms[1].pts[2], tip: P2 = [462, 238], b: P2 = [hd[0] - (tip[0] - hd[0]) * 0.45, hd[1] - (tip[1] - hd[1]) * 0.45];
    p.band([b, tip], "#7a4b2a", 5 * u, 1.4 * u, "round");
    p.ell(tip[0], tip[1] + 6 * u, 8 * u, 11 * u, "#3a2a20", 1.6 * u);
  }
  for (const a of arms) if (!a.front && !a.over) drawArm(a);
  // torso / dress: shaded fill -> clothing clipped to it -> thick-thin ink ring
  if (dress) {
    const D: Blob = { a: 0.5 * W * (o.build === "fat" || o.build === "stout" ? 1.12 : o.build === "thin" ? 0.86 : 0.98), b: 0.5 * ((sole - 0.35 * HH) - (chin - 0.2 * HH)), nTop: 2.0, nBot: 3.0, egg: 0.35, asym: 0.03 * facing, rot: 0, noise: 0.006, seed: seed + 9 };
    const dcy = sole - 0.35 * HH - D.b, dp = blobPts(300, dcy, D);
    p.gradFill(dp, o.dress!, mul(o.dress!, SH_CLOTH), light);
    p.clip(dp, () => {
      if (o.dressPat) fabric(p, o.dressPat, o.dressCol2 ?? shade(o.dress!, 0.75), 300 - D.a * 1.3, 300 + D.a * 1.3, dcy - D.b, dcy + D.b, u);
      if (o.sashW) p.band([[300 - D.a * 1.3, dcy + 0.12 * D.b], [300 + D.a * 1.3, dcy + 0.12 * D.b]], o.sashW, 0.09 * HH, 1.5 * u);
      // hem trim
      p.band([[300 - D.a * 1.3, dcy + 0.86 * D.b], [300 + D.a * 1.3, dcy + 0.86 * D.b]], o.dressCol2 ?? shade(o.dress!, 0.72), 0.05 * HH, 1.2 * u);
    });
    if (o.sashW) { const bx = 300 + 0.45 * D.a * (facing || 1), by = dcy + 0.12 * D.b; p.ell(bx - 7 * u, by, 7 * u, 4.5 * u, o.sashW, 1.4 * u); p.ell(bx + 7 * u, by, 7 * u, 4.5 * u, o.sashW, 1.4 * u); p.ell(bx, by, 3 * u, 3 * u, o.sashW, 1.4 * u); }
    p.inkRing(dp, ow, thick);
    const Sw: Blob = { a: 0.37 * W * (o.build === "fat" || o.build === "stout" ? 1.12 : o.build === "thin" ? 0.88 : 1), b: 0.3 * HH, nTop: 2.2, nBot: 2.4, egg: 0.1, asym: 0, rot: 0, noise: 0.006, seed: seed + 8 };
    const sp = blobPts(300, chin + 0.12 * HH, Sw);
    p.gradFill(sp, o.jacket, mul(o.jacket, SH_CLOTH), light);
    p.clip(sp, () => { if (o.pattern) fabric(p, o.pattern, o.patCol ?? shade(o.jacket, 0.72), 300 - Sw.a * 1.2, 300 + Sw.a * 1.2, chin - 0.3 * HH, chin + 0.5 * HH, u); });
    p.inkRing(sp, ow * 0.9, thick);
    if (o.apron) { // pinafore apron over the dress (nurses), optional red cross on the bib
      const ap: P2[] = [[300 - 0.3 * D.a, chin + 0.2 * HH], [300 + 0.3 * D.a, chin + 0.2 * HH], [300 + 0.36 * D.a, dcy - 0.25 * D.b], [300 + 0.66 * D.a, dcy - 0.2 * D.b], [300 + 0.6 * D.a, dcy + 0.78 * D.b], [300 - 0.6 * D.a, dcy + 0.78 * D.b], [300 - 0.66 * D.a, dcy - 0.2 * D.b], [300 - 0.36 * D.a, dcy - 0.25 * D.b]];
      p.gradFill(ap, o.apron, mul(o.apron, [0.86, 0.86, 0.92]), light, 0.4); p.poly(ap, null, 2.2 * u);
      if (o.redcross) { const rx = 300, ry = chin + 0.42 * HH; p.poly([[rx - 3 * u, ry - 9 * u], [rx + 3 * u, ry - 9 * u], [rx + 3 * u, ry - 3 * u], [rx + 9 * u, ry - 3 * u], [rx + 9 * u, ry + 3 * u], [rx + 3 * u, ry + 3 * u], [rx + 3 * u, ry + 9 * u], [rx - 3 * u, ry + 9 * u], [rx - 3 * u, ry + 3 * u], [rx - 9 * u, ry + 3 * u], [rx - 9 * u, ry - 3 * u], [rx - 3 * u, ry - 3 * u]], "#c8202c", 0); }
    }
    if (o.pcollar) for (const s of [-1, 1]) p.ell(300 + s * 9 * u, chin + 0.05 * HH, 11 * u, 7 * u, o.pcollar, 1.6 * u, s < 0 ? 270 : -90, s < 0 ? 450 : 90);
    if (o.scarf) { p.band([[300 - 0.62 * Sw.a, chin + 0.06 * HH], [300 + 0.62 * Sw.a, chin + 0.06 * HH]], o.scarf, 0.11 * HH, 1.8 * u, "round"); p.poly([[300 + 0.3 * Sw.a, chin + 0.08 * HH], [300 + 0.5 * Sw.a, chin + 0.08 * HH], [300 + 0.56 * Sw.a, chin + 0.62 * HH], [300 + 0.28 * Sw.a, chin + 0.58 * HH]], o.scarf, 1.8 * u); }
    if (o.pearls) for (let i = 0; i <= 8; i++) { const t = i / 8 - 0.5, x = 300 + t * 30 * u, y = chin + 0.04 * HH + (0.25 - t * t) * 30 * u; p.ell(x, y, 2.6 * u, 2.6 * u, "#fbf6ee", 0.9 * u); }
  } else {
    p.gradFill(tp, o.jacket, mul(o.jacket, SH_CLOTH), light);
    p.clip(tp, () => {
      if (o.belt) {
        for (const s of [-1, 1]) p.band([[tcx - s * 0.75 * T.a, chin - 0.05 * HH], [tcx + s * 0.8 * T.a, torsoBot - 0.1 * HH]], o.belt!, 5.5 * u, 1.8 * u);
        const xc = tcx + 0.025 * T.a, yc = chin - 0.05 * HH + (torsoBot - 0.1 * HH - (chin - 0.05 * HH)) * (0.75 / 1.55);
        p.poly([[xc - 3.5 * u, yc - 3.5 * u], [xc + 3.5 * u, yc - 3.5 * u], [xc + 3.5 * u, yc + 3.5 * u], [xc - 3.5 * u, yc + 3.5 * u]], "#d9dde0", 1.5 * u);
      }
      if (o.sash) p.band([[tcx - 1.3 * T.a, torsoBot - 0.32 * HH], [tcx + 1.3 * T.a, torsoBot - 0.32 * HH]], o.sash, 0.13 * HH, 1.8 * u);
      clothDetail(p, o, tcx, chin, torsoBot, T.a, HH, u, facing);
    });
    if (o.scarf) { p.band([[tcx - 0.62 * T.a, chin + 0.06 * HH], [tcx + 0.62 * T.a, chin + 0.06 * HH]], o.scarf, 0.11 * HH, 1.8 * u, "round"); p.poly([[tcx + 0.3 * T.a, chin + 0.08 * HH], [tcx + 0.46 * T.a, chin + 0.08 * HH], [tcx + 0.52 * T.a, chin + 0.5 * HH], [tcx + 0.3 * T.a, chin + 0.46 * HH]], o.scarf, 1.8 * u); }
    if (o.sash) { const s = facing || 1; p.poly([[tcx + s * 0.55 * T.a, torsoBot - 0.3 * HH], [tcx + s * 0.75 * T.a, torsoBot + 0.05 * HH], [tcx + s * 0.45 * T.a, torsoBot + 0.02 * HH]], o.sash, 1.6 * u); }
    p.inkRing(tp, ow, thick);
    if (o.tunic) { const vx = tcx + 3 * u * facing; for (const s of [-1, 1]) p.poly([[vx + s * 1 * u, chin + 0.04 * HH], [vx + s * 15 * u, chin - 0.04 * HH], [vx + s * 13 * u, chin + 0.12 * HH]], shade(o.jacket, 0.88), 1.4 * u); }
    if (o.webbing) { // ammo pouches either side of the buckle
      const y = torsoBot - 0.2 * HH, vx = tcx + 3 * u * facing;
      for (const s of [-1, 1]) for (const k of [0.36, 0.66]) {
        const px = vx + s * k * T.a;
        p.poly(rrect(px - 0.13 * T.a, y - 0.06 * HH, px + 0.13 * T.a, y + 0.1 * HH, 2 * u), mul(o.webbing, [0.92, 0.92, 0.9]), 1.4 * u);
        p.stroke([[px - 0.13 * T.a, y - 0.01 * HH], [px + 0.13 * T.a, y - 0.01 * HH]], 1 * u, shade(o.webbing, 0.7)); p.dot(px, y + 0.02 * HH, 1.3 * u, "#8a8470");
      }
    }
    if (o.canteen) { // hanging at the left hip
      const cx0 = tcx - 0.92 * T.a, cy0 = torsoBot - 0.02 * HH;
      p.ell(cx0, cy0, 0.15 * T.a + 4 * u, 0.12 * HH, "#5a6a48", 1.6 * u); p.ell(cx0 - 2 * u, cy0 - 0.03 * HH, 0.06 * T.a, 0.04 * HH, "rgba(255,255,255,0.25)", 0);
      p.poly(rrect(cx0 - 3 * u, cy0 - 0.15 * HH, cx0 + 3 * u, cy0 - 0.1 * HH, 1 * u), "#3a3a30", 1 * u);
    }
    // shirt collar points over the neck seam
    if (o.lapels || o.vest || o.tie || o.bowtie) {
      const vx = tcx + 3 * u * facing;
      for (const s of [-1, 1]) p.poly([[vx + s * 1 * u, chin + 0.03 * HH], [vx + s * 13 * u, chin - 0.02 * HH], [vx + s * 10 * u, chin + 0.1 * HH]], o.shirt ?? SHIRT, 1.4 * u);
      if (o.wing) for (const s of [-1, 1]) p.poly([[vx + s * 6 * u, chin - 0.03 * HH], [vx + s * 15 * u, chin - 0.05 * HH], [vx + s * 9 * u, chin + 0.01 * HH]], o.shirt ?? SHIRT, 1.2 * u);
      if (o.bowtie) { const bx = vx, by = chin + 0.05 * HH; p.poly([[bx, by], [bx - 10 * u, by - 6 * u], [bx - 10 * u, by + 6 * u]], o.bowtie, 1.6 * u); p.poly([[bx, by], [bx + 10 * u, by - 6 * u], [bx + 10 * u, by + 6 * u]], o.bowtie, 1.6 * u); p.ell(bx, by, 3 * u, 3 * u, o.bowtie, 1.4 * u);
        if (o.tieDots) for (const s of [-1, 1]) for (const d of [-3, 3]) p.dot(bx + s * 6 * u, by + d * u, 1.2 * u, o.tieDots); }
    }
    if (o.apron) {
      const ax = tcx + 2 * u * facing, wy = torsoBot - 0.38 * HH, by = torsoBot + 0.3 * HH;
      const ap: P2[] = [[ax - 0.42 * T.a, chin + 0.16 * HH], [ax + 0.42 * T.a, chin + 0.16 * HH], [ax + 0.5 * T.a, wy], [ax + 0.86 * T.a, wy + 4 * u], [ax + 0.8 * T.a, by], [ax - 0.8 * T.a, by], [ax - 0.86 * T.a, wy + 4 * u], [ax - 0.5 * T.a, wy]];
      p.gradFill(ap, o.apron, mul(o.apron, [0.86, 0.86, 0.92]), light, 0.4); p.poly(ap, null, 2.2 * u);
      p.poly(rrect(ax - 0.28 * T.a, wy + 0.08 * HH, ax + 0.28 * T.a, wy + 0.24 * HH, 2 * u), null, 1.4 * u);
      for (const s of [-1, 1]) p.stroke([[ax + s * 0.42 * T.a, chin + 0.16 * HH], [ax + s * 0.3 * T.a, chin + 0.02 * HH]], 2.2 * u, shade(o.apron, 0.8));
    }
  }
  // ---- WW2 extras over the torso: coat buttons, cape, fur collar, shoulder boards, medals, evacuee tag, gas-mask box ----
  {
    const vx = tcx + 3 * u * facing;
    if (o.coat && !dress) {
      for (const s of [-1, 1]) p.poly([[vx + s * 1 * u, chin + 0.02 * HH], [vx + s * 0.62 * T.a, chin + 0.02 * HH], [vx + s * 0.5 * T.a, chin + 0.24 * HH], [vx + s * 0.12 * T.a, chin + 0.3 * HH]], shade(o.coat, 0.84), 1.4 * u);
      for (let i = 0; i < 4; i++) for (const s of [-1, 1]) { const y = chin + 0.36 * HH + i * 0.17 * HH; if (y < torsoBot - 0.05 * HH) { p.dot(vx + s * 0.32 * T.a, y, 3 * u); p.dot(vx + s * 0.32 * T.a, y, 2.2 * u, o.buttons ?? shade(o.coat, 0.7)); } }
    }
    if (o.cape) {
      const c = o.cape, hem = torsoBot + (o.snow ? 0.32 : 0.2) * HH, gap = o.snow ? 0.04 : 0.32;
      for (const s of [-1, 1]) {
        const half: P2[] = [[vx + s * 0.22 * T.a, chin - 0.04 * HH], [tcx + s * 0.9 * T.a, chin + 0.04 * HH], [tcx + s * 1.22 * T.a, chin + 0.3 * HH], [tcx + s * (1.36 * T.a + 8 * u), hem],
          [vx + s * (gap + 0.2) * T.a, hem + 4 * u], [vx + s * gap * T.a, chin + 0.36 * HH], [vx + s * 0.08 * T.a, chin + 0.12 * HH]];
        p.gradFill(half, c, mul(c, SH_CLOTH), light, 0.35); p.poly(half, null, ow * 0.8);
        p.stroke(curve([tcx + s * 0.8 * T.a, chin + 0.3 * HH], [tcx + s * 1.0 * T.a, chin + 0.7 * HH], [tcx + s * 1.05 * T.a, hem - 4 * u], 8), 1.4 * u, shade(c, 0.72));
        if (o.snow) for (let k = 0; k < 3; k++) { const x = vx + s * ((gap + 0.3) * T.a + k * 0.38 * T.a); p.poly([[x - 6 * u, hem - 2 * u], [x + 6 * u, hem - 2 * u], [x, hem + 9 * u]], c, 1.2 * u); }
      }
      if (!o.snow) { p.stroke([[vx - 0.12 * T.a, chin + 0.14 * HH], [vx, chin + 0.18 * HH], [vx + 0.12 * T.a, chin + 0.14 * HH]], 1.6 * u, "#e8c45a"); for (const s of [-1, 1]) p.ell(vx + s * 0.13 * T.a, chin + 0.14 * HH, 2.6 * u, 2.6 * u, "#e8c45a", 1 * u); }
      for (const s of [-1, 1]) p.poly([[vx + s * 2 * u, chin - 0.06 * HH], [vx + s * 0.48 * T.a, chin - 0.1 * HH], [vx + s * 0.42 * T.a, chin + 0.08 * HH], [vx + s * 0.1 * T.a, chin + 0.1 * HH]], shade(c, 0.86), 1.4 * u);
    }
    if (o.fur) { // sheepskin shawl collar: shaggy edge, curly texture
      for (const sd of [-1, 1]) {
        const key: P2[] = [[vx + sd * 0.12 * T.a, chin - 0.06 * HH], [tcx + sd * 0.92 * T.a, chin + 0.02 * HH], [tcx + sd * 0.8 * T.a, chin + 0.2 * HH], [vx + sd * 0.34 * T.a, chin + 0.46 * HH], [vx + sd * 0.06 * T.a, chin + 0.22 * HH]];
        const pts: P2[] = [];
        key.forEach((q, k) => { const r = key[(k + 1) % key.length]; for (let m = 0; m < 6; m++) { const t = m / 6, j = (m % 2 ? 2.6 : -1) * u; pts.push([q[0] + (r[0] - q[0]) * t + j, q[1] + (r[1] - q[1]) * t + j]); } });
        const fp = sd < 0 ? pts.reverse() : pts;
        p.gradFill(fp, o.fur, shade(o.fur, 0.78), light, 0.3); p.poly(fp, null, 1.8 * u);
        for (let k = 0; k < 6; k++) { const q = lerp2(lerp2(key[0], key[2], 0.2 + 0.13 * k), lerp2(key[1], key[3], 0.2 + 0.13 * k), 0.45); p.arc(q[0], q[1], 3 * u, 2.4 * u, 160, 380, 1.1 * u, shade(o.fur, 0.68)); }
      }
    }
    if (o.boards) for (const s of [-1, 1]) { const bx = tcx + s * 0.66 * T.a, by = chin + 0.03 * HH; p.poly(rotPts(rrect(bx - 13 * u, by - 3.5 * u, bx + 13 * u, by + 3.5 * u, 1.5 * u), s * rad(18), bx, by), o.boards, 1.2 * u); p.dot(bx + s * 4 * u, by + s * 1 * u, 1.6 * u, "#e8c45a"); }
    if (o.medals) medalsDraw(p, o.medals, tcx + 0.45 * T.a + 4 * u * facing, chin + 0.3 * HH, u);
    if (o.tag) {
      const tx = tcx - 0.42 * T.a, ty = chin + 0.36 * HH, tg: P2[] = rotPts(rrect(tx - 13 * u, ty, tx + 13 * u, ty + 17 * u, 2 * u), rad(-8), tx, ty);
      p.stroke([[tcx - 0.2 * T.a, chin + 0.18 * HH], [tx + 2 * u, ty + 2 * u]], 1 * u, "#f4ecd8");
      p.poly(tg, "#efe2b8", 1.2 * u); p.dot(tx + 1.5 * u, ty + 3 * u, 1.4 * u, INK);
      for (let k = 0; k < 2; k++) p.stroke([[tx - 9 * u, ty + 8 * u + k * 4.5 * u], [tx + 8 * u, ty + 6.5 * u + k * 4.5 * u]], 1 * u, "#5a5068");
    }
    if (o.gasbox) {
      const bx = tcx - 1.02 * T.a, by = torsoBot - 0.3 * HH;
      p.band([[tcx + 0.55 * T.a, chin + 0.0 * HH], [bx + 4 * u, by]], "#d8c8a0", 2 * u, 0.8 * u);
      p.poly(rrect(bx - 13 * u, by - 2 * u, bx + 13 * u, by + 20 * u, 2 * u), "#b8946a", 1.6 * u);
      p.stroke([[bx - 13 * u, by + 5 * u], [bx + 13 * u, by + 5 * u]], 1.1 * u, "#7a5a3a");
    }
    // two-handed props sit under the hands
    const L = arms[0].pts[2], Rr = arms[1].pts[2];
    if (gun) smgDraw(p, gunA, gunB, u, gun);
    else if (prop === "map") mapSheet(p, L[0] - 4 * u, chin + 0.22 * HH, Rr[0] + 4 * u, chin + 0.62 * HH, u);
    else if (prop === "crate") crateDraw(p, L[0] - 2 * u, torsoBot - 0.5 * HH, Rr[0] + 2 * u, torsoBot + 0.04 * HH, u);
    else if (prop === "bundle") bundleDraw(p, tcx, torsoBot - 0.32 * HH, 0.95 * T.a, u, o.patCol && o.patCol !== o.jacket ? "#8a5a6a" : "#7a5a4a");
    else if (prop === "candle") candleDraw(p, tcx, chin + 0.44 * HH, u);
    else if (prop === "photo") photoDraw(p, tcx, chin + 0.58 * HH, u);
    if (opts.desk) deskDraw(p, opts.desk, deskTop, sole, W, u);
  }
  // in front of the body: hands holding props
  for (const a of arms) if (a.front && !a.over) drawArm(a);
  const ra = arms[1], [hx, hy] = ra.pts[2];
  if (prop === "paper") { p.poly([[hx - 16 * u, hy - 30 * u], [hx + 14 * u, hy - 34 * u], [hx + 17 * u, hy + 6 * u], [hx - 13 * u, hy + 9 * u]], "#f4efe2", 2 * u);
    for (let k = 0; k < 4; k++) p.stroke([[hx - 9 * u, hy - 22 * u + k * 7 * u], [hx + 9 * u, hy - 24 * u + k * 7 * u]], 1.4 * u, "#8a8478"); drawHand([hx, hy], ra.pts[1], "grip"); }
  else if (prop === "news") {
    p.poly([[hx - 20 * u, hy - 34 * u], [hx + 18 * u, hy - 38 * u], [hx + 22 * u, hy + 10 * u], [hx - 16 * u, hy + 14 * u]], "#ece4cc", 2 * u);
    p.poly([[hx - 16 * u, hy - 29 * u], [hx + 15 * u, hy - 32 * u], [hx + 15.5 * u, hy - 24 * u], [hx - 15.5 * u, hy - 21 * u]], "#3a3438", 0);
    for (let k = 0; k < 4; k++) p.stroke([[hx - 13 * u, hy - 14 * u + k * 6 * u], [hx + (k % 2 ? 2 : 14) * u, hy - 15.5 * u + k * 6 * u]], 1.3 * u, "#8a8478");
    p.poly(rrect(hx + 4 * u, hy - 15 * u, hx + 15 * u, hy - 3 * u, 1 * u), "#b8b0a0", 0.9 * u);
    drawHand([hx, hy], ra.pts[1], "grip");
  }
  else if (prop === "cash") { for (let k = 0; k < 4; k++) p.poly(rrect(hx - 18 * u, hy - 14 * u - k * 6 * u, hx + 18 * u, hy - 6 * u - k * 6 * u, 2 * u), "#9fbf8a", 1.6 * u); drawHand([hx, hy], ra.pts[1], "grip"); }
  else if (prop === "stein") { p.poly(rrect(hx - 11 * u, hy - 30 * u, hx + 11 * u, hy + 6 * u, 3 * u), "#e8b84a", 2 * u); for (const k of [-5, 0, 5]) p.stroke([[hx + k * u, hy - 24 * u], [hx + k * u, hy]], 1 * u, "#c8902a"); p.ell(hx, hy - 31 * u, 12 * u, 6 * u, "#fffaf0", 2 * u); p.ell(hx - 6 * u, hy - 35 * u, 6 * u, 4 * u, "#fffaf0", 1.6 * u); p.arc(hx + 14 * u, hy - 12 * u, 7 * u, 10 * u, -80, 80, 3 * u); drawHand([hx, hy], ra.pts[1], "grip"); }
  else if (prop === "brush") { p.band([[hx - 4 * u, hy + 10 * u], [hx + 16 * u, hy - 34 * u]], "#9a6a3c", 3.5 * u, 1.2 * u, "round"); p.ell(hx + 18 * u, hy - 39 * u, 4 * u, 7 * u, "#c8323a", 1.2 * u); drawHand([hx, hy], ra.pts[1], "grip"); }
  else if (prop === "bread") { p.ell(hx, hy - 8 * u, 24 * u, 12 * u, "#d39a52", 2 * u); p.ell(hx - 4 * u, hy - 12 * u, 14 * u, 4 * u, "rgba(255,240,200,0.5)", 0); for (const k of [-12, -2, 8]) p.stroke([[hx + k * u - 3 * u, hy - 15 * u], [hx + k * u + 3 * u, hy - 4 * u]], 1.6 * u, "#9a6a34"); drawHand([hx, hy], ra.pts[1], "grip"); }
  else if (prop === "case") { p.poly(rrect(hx - 22 * u, hy + 2 * u, hx + 22 * u, hy + 34 * u, 4 * u), "#7a4a2a", 2.2 * u); p.stroke([[hx - 22 * u, hy + 14 * u], [hx + 22 * u, hy + 14 * u]], 1.4 * u, "#4a2a16"); p.stroke([[hx - 8 * u, hy + 2 * u], [hx - 8 * u, hy - 4 * u], [hx + 8 * u, hy - 4 * u], [hx + 8 * u, hy + 2 * u]], 2.4 * u, "#3a2416"); drawHand([hx, hy], ra.pts[1], "grip"); }
  else if (prop === "icecream") {
    p.poly([[hx - 8 * u, hy - 12 * u], [hx + 8 * u, hy - 12 * u], [hx, hy + 7 * u]], "#e0a35a", 1.8 * u);
    p.ell(hx, hy - 19 * u, 11 * u, 10 * u, "#f7c6d9", 2.2 * u);
    drawHand([hx, hy], ra.pts[1], "grip");
  } else if (prop === "grenade") { grenadeDraw(p, hx, hy, u); drawHand([hx, hy], ra.pts[1], "grip"); }
  else if (prop === "rivet") { rivetDraw(p, hx, hy, fd, u); drawHand([hx, hy], ra.pts[1], "grip"); }
  else if (hammer) {
    const ang = rad(-70 + 105 * clamp(hammer[1], 0, 1));
    const Rh = (pts: P2[]) => rotPts(pts, ang, hx, hy);
    p.band(Rh([[hx, hy + 12 * u], [hx, hy - 44 * u]]), "#8a5a34", 5 * u, 1.5 * u, "round");
    p.poly(Rh([[hx - 12 * u, hy - 58 * u], [hx + 20 * u, hy - 58 * u], [hx + 20 * u, hy - 42 * u], [hx - 12 * u, hy - 42 * u]]), "#7d848c", 2.2 * u);
    drawHand([hx, hy], ra.pts[1], "grip");
  }
  if (prop === "shako") { // carried by the left hand
    const [lx, ly] = arms[0].pts[2];
    p.poly([[lx - 14 * u, ly + 3 * u], [lx + 14 * u, ly + 3 * u], [lx + 16 * u, ly + 30 * u], [lx - 16 * u, ly + 30 * u]], "#3a3d47", 2.2 * u);
    p.ell(lx, ly + 31 * u, 3.5 * u, 3.5 * u, "#2b7a4b", 1.5 * u);
    drawHand([lx, ly], arms[0].pts[1], "grip");
  }
  if (prop === "sword") { swordDraw(p, tcx - 1.25 * T.a - 26 * u, tcx + 1.25 * T.a + 26 * u, chin + 0.36 * HH, u); for (const a of arms) drawHand(a.pts[2], a.pts[1], "grip"); }
  if (prop === "pistol") { const a = arms[fd > 0 ? 1 : 0]; pistolDraw(p, a.pts[2], fd, u); drawHand(a.pts[2], a.pts[1], "grip"); }
  if (umb) { const [lx, ly] = arms[0].pts[2]; umbrellaDraw(p, [lx, ly], sole - 2 * u, u); drawHand([lx, ly], arms[0].pts[1], "grip"); }
  if (prop === "cane") { // left hand on the crook, tip on the ground
    const [lx, ly] = arms[0].pts[2], gy = sole - 2 * u - (p.rot ? 0 : 0);
    p.band([[lx, ly - 2 * u], [lx - 4 * u, gy]], "#4a2c1a", 4 * u, 1.3 * u, "round");
    p.arc(lx + 7 * u, ly - 2 * u, 7 * u, 7 * u, 180, 360, 4 * u + 2.6 * u); p.arc(lx + 7 * u, ly - 2 * u, 7 * u, 7 * u, 180, 360, 4 * u, "#4a2c1a");
    p.ell(lx - 4 * u, gy, 2.6 * u, 1.6 * u, "#c8b070", 0.8 * u);
    drawHand([lx, ly], arms[0].pts[1], "grip");
  }
  // ---- head: rotates with the body, plus its own tilt about the chin ----
  const Ah = A + headTilt, [cpx, cpy] = rotAbout([300, chin], rad(A), [300, hipY]);
  p.rot = Ah ? [rad(Ah), 300, chin, cpx - 300, cpy - chin] : null;
  hatBehind(p, o, H, 300, hc, light, thick, ow, false);
  if (!o.noEars && !o.flaps && o.hat !== "bonnet" && o.hat !== "cloche" && !EARLESS[o.hat ?? ""]) for (const s of [-1, 1]) {
    const exx = 300 + s * H.a * 0.94 + facing * 5 * u, eyy = hc + 5 * u;
    p.ell(exx, eyy, 9 * u, 12.5 * u, skin, ow * 0.7);
    p.arc(exx - s * 1 * u, eyy, 4.5 * u, 7 * u, s < 0 ? 100 : -80, s < 0 ? 260 : 80, 1.6 * u, mul(skin, [0.85, 0.7, 0.68]));
  }
  const hp = blobPts(300, hc, H);
  p.shadedFill(hp, skin, mul(skin, SH_SKIN), light, H.a);
  p.inkRing(hp, ow, thick);
  hatOn(p, o, hp, H, 300, hc, light, seed, facing, false);
  const brim = !!o.hat && o.hat !== "hair" && o.hat !== "bonnet" && o.hat !== "cap" && o.hat !== "bald" && o.hat !== "flatcap";
  faceFront(p, 300, hc, W, expr, facing, look, lid, brim, skin, o);
  if (o.part && o.hair) {
    // side-parted fringe swept across the brow
    const fr: P2[] = [[300 - 0.47 * W, crown + 0.3 * HH], [300 - 0.36 * W, crown + 0.06 * HH], [300 + 0.12 * W, crown + 0.0 * HH], [300 + 0.44 * W, crown + 0.14 * HH],
      [300 + 0.2 * W, crown + 0.16 * HH], [300 - 0.12 * W, crown + 0.3 * HH], [300 - 0.36 * W, crown + 0.44 * HH]];
    p.poly(fr, o.hair, ow * 0.7);
    for (const [a0, a1] of [[[0.3, 0.06], [-0.3, 0.3]], [[0.18, 0.1], [-0.36, 0.38]], [[0.05, 0.16], [-0.2, 0.3]]] as [P2, P2][])
      p.stroke(curve([300 + a0[0] * W, crown + a0[1] * HH], [300 + ((a0[0] + a1[0]) / 2) * W, crown + ((a0[1] + a1[1]) / 2 - 0.02) * HH], [300 + a1[0] * W, crown + a1[1] * HH], 8), 1.6 * u, mix(o.hair, "#ffffff", 0.28));
  }
  if (o.glasses) {
    const fx = 300 + 7 * u * facing;
    for (const sd of [-1, 1]) { p.ell(fx + sd * 13 * u, hc, 10 * u, 9 * u, "rgba(220,236,255,0.25)", 2.6 * u); p.stroke([[fx + sd * 23 * u, hc - 2 * u], [fx + sd * 40 * u, hc - 5 * u]], 2 * u); }
    p.stroke([[fx - 3 * u, hc - 1 * u], [fx + 3 * u, hc - 1 * u]], 2.2 * u);
  }
  if (o.pince) {
    const fx = 300 + 7 * u * facing;
    for (const sd of [-1, 1]) p.ell(fx + sd * 12 * u, hc + 1 * u, 7.5 * u, 7 * u, "rgba(220,236,255,0.3)", 1.8 * u);
    p.arc(fx, hc - 1 * u, 4.5 * u, 3 * u, 200, 340, 1.8 * u);
    p.stroke(curve([fx - 19 * u, hc + 2 * u], [fx - 30 * u, hc + 30 * u], [fx - 26 * u, chin + 0.06 * HH], 10), 1 * u, "#2a2228");
  }
  if (o.aviators) {
    const fx = 300 + 7 * u * facing;
    for (const sd of [-1, 1]) {
      const lens: P2[] = [[fx + sd * 3 * u, hc - 7 * u], [fx + sd * 23 * u, hc - 8 * u], [fx + sd * 24 * u, hc + 2 * u], [fx + sd * 17 * u, hc + 11 * u], [fx + sd * 9 * u, hc + 11 * u], [fx + sd * 3 * u, hc + 2 * u]];
      p.poly(sd < 0 ? lens.reverse() : lens, "#26323e", 2 * u);
      p.stroke([[fx + sd * 8 * u, hc - 4 * u], [fx + sd * 13 * u, hc - 5 * u]], 1.6 * u, "rgba(255,255,255,0.5)");
      p.stroke([[fx + sd * 23 * u, hc - 6 * u], [fx + sd * 40 * u, hc - 6 * u]], 1.8 * u, "#c8a24a");
    }
    p.stroke([[fx - 3 * u, hc - 7 * u], [fx + 3 * u, hc - 7 * u]], 1.8 * u, "#c8a24a");
  }
  if (prop === "phone") { const a = arms[fd > 0 ? 1 : 0].pts[2]; handsetDraw(p, [a[0] + fd * 2 * u, hc - 0.02 * HH], [300 + fd * 0.22 * W + 5 * u * facing, hc + 0.32 * HH], u); }
  if (o.sweat) for (const [dx, dy] of [[-44, -18], [46, -26], [40, 4], [-40, 10]] as const) { p.ell(300 + dx * u, hc + dy * u, 3.4 * u, 5.8 * u, "#9fd4ff", 1.8 * u); p.dot(300 + dx * u - u, hc + dy * u + 1.5 * u, 1 * u, "#ffffff"); }
  if (prop === "binoc") {
    for (const sd of [-1, 1]) {
      p.poly(rrect(300 + sd * 0.17 * W - 0.12 * W, hc - 0.12 * HH, 300 + sd * 0.17 * W + 0.12 * W, hc + 0.1 * HH, 6 * u), "#2c3036", ow * 0.8);
      p.ell(300 + sd * 0.17 * W, hc - 0.12 * HH, 0.1 * W, 0.03 * HH, "#4a5058", 1.5 * u);
      p.dot(300 + sd * 0.2 * W, chin - 0.02 * HH, 5.5 * u);
    }
    p.band([[300 - 0.06 * W, hc - 0.02 * HH], [300 + 0.06 * W, hc - 0.02 * HH]], "#2c3036", 3 * u, 1 * u);
  }
  // arms reaching over the head (hands on head / chin)
  p.rot = A ? [rad(A), 300, hipY] : null;
  for (const a of arms) if (a.over) drawArm(a);
  p.rot = null;
  if (prop === "mic") micDraw(p, 300 + fd * 0.34 * W, chin + 0.08 * HH, sole - 2 * u, u);
};

export type SideOpts = {
  phase?: number; expr?: Expr; mode?: "march" | "stand" | "swing" | "push" | "aim" | "run"; blink?: boolean | number; stomp?: number; pose?: number;
  /** aim mode: down on one knee (behind cover) */
  kneel?: boolean;
  /** step length as a multiple of 0.8 m (370 units): matches 1.6 m/s at 2 steps/s; scale by the view's foreshortening */
  stride?: number; light?: number; seed?: number;
  /** push mode: where the hands land at pose 1, in final canvas units (e.g. the swing kid's back) */
  hand?: [number, number];
};

/** two-bone leg, knee bending forward (+x) */
const ik = (hip: P2, ank: P2, l1: number, l2: number): P2 => {
  const dx = ank[0] - hip[0], dy = ank[1] - hip[1], d = clamp(Math.hypot(dx, dy), 1, l1 + l2 - 0.01);
  const A = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)), k = Math.atan2(dy, dx) - A;
  return [hip[0] + l1 * Math.cos(k), hip[1] + l1 * Math.sin(k)];
};

/** hip height of the seated kid in `swing` mode (design units); swingKid seats the torso bottom on the plank */
const SWING_HIP = 733;

/** fabric pattern, braces, open jacket with lapels, vest, belt, tie, pocket square, watch chain, buttons: drawn inside the
 *  torso clip (front view) */
const clothDetail = (p: Pen, o: Outfit, tcx: number, chin: number, bot: number, Ta: number, HH: number, u: number, facing: number) => {
  const top = chin - 0.3 * HH, vx = tcx + 3 * u * facing, shirt = o.shirt ?? SHIRT;
  if (o.pattern) fabric(p, o.pattern, o.patCol ?? shade(o.jacket, 0.72), tcx - 1.3 * Ta, tcx + 1.3 * Ta, top, bot + 10 * u, u);
  if (o.tunic) {
    for (const s of [-1, 1]) {
      const px = vx + s * 0.48 * Ta, py = chin + 0.22 * HH;
      p.poly(rrect(px - 0.22 * Ta, py, px + 0.22 * Ta, py + 0.22 * HH, 2 * u), mul(o.jacket, [0.92, 0.92, 0.96]), 1.4 * u);
      p.poly([[px - 0.24 * Ta, py - 1 * u], [px + 0.24 * Ta, py - 1 * u], [px + 0.22 * Ta, py + 0.07 * HH], [px, py + 0.09 * HH], [px - 0.22 * Ta, py + 0.07 * HH]], shade(o.jacket, 0.86), 1.4 * u);
      p.dot(px, py + 0.06 * HH, 1.8 * u, o.buttons ?? INK);
      p.poly(rrect(px - 0.2 * Ta, bot - 0.42 * HH, px + 0.2 * Ta, bot - 0.26 * HH, 2 * u), null, 1.2 * u);
    }
    if (o.worn) for (const [dx, dy, c] of [[0.2, 0.52, "#6a5a38"], [-0.5, 0.74, "#d0c08a"], [0.62, 0.86, "#7a6a48"]] as const) {
      const qx = tcx + dx * Ta, qy = chin + dy * HH;
      p.poly(rrect(qx - 0.16 * Ta, qy - 0.06 * HH, qx + 0.16 * Ta, qy + 0.06 * HH, 1.5 * u), c, 1.1 * u);
      for (let k = -2; k <= 2; k++) p.stroke([[qx + k * 0.06 * Ta, qy - 0.075 * HH], [qx + k * 0.06 * Ta, qy - 0.05 * HH]], 0.7 * u, INK);
    }
  }
  if (o.webbing) {
    for (const s of [-1, 1]) p.band([[vx + s * 0.42 * Ta, top], [vx + s * 0.34 * Ta, bot - 0.2 * HH]], o.webbing, 4.2 * u, 1 * u);
    const y = bot - 0.2 * HH;
    p.band([[tcx - 1.3 * Ta, y], [tcx + 1.3 * Ta, y]], o.webbing, 0.08 * HH, 1.2 * u);
    p.poly(rrect(vx - 5.5 * u, y - 5 * u, vx + 5.5 * u, y + 5 * u, 1.2 * u), "#a8a490", 1.3 * u);
  }
  if (o.braces) for (const s of [-1, 1]) p.band([[vx + s * 0.5 * Ta, top], [vx + s * 0.38 * Ta, bot + 4 * u]], o.braces, 3.6 * u, 1 * u);
  if (o.bib) { // coverall bib with straps, buckles and a chest pocket
    const by0 = chin + 0.3 * HH;
    for (const s of [-1, 1]) p.band([[vx + s * 0.56 * Ta, top], [vx + s * 0.4 * Ta, by0 + 4 * u]], o.bib, 6 * u, 1.2 * u);
    p.poly([[vx - 0.46 * Ta, by0], [vx + 0.46 * Ta, by0], [vx + 0.5 * Ta, bot + 10 * u], [vx - 0.5 * Ta, bot + 10 * u]], o.bib, 1.8 * u);
    for (const s of [-1, 1]) p.poly(rrect(vx + s * 0.4 * Ta - 4 * u, by0 - 2 * u, vx + s * 0.4 * Ta + 4 * u, by0 + 6 * u, 1 * u), "#c8ccd4", 1 * u);
    p.poly(rrect(vx - 0.24 * Ta, by0 + 0.08 * HH, vx + 0.24 * Ta, by0 + 0.22 * HH, 2 * u), shade(o.bib, 0.88), 1.2 * u);
    p.stroke([[vx - 0.5 * Ta, by0 + 0.02 * HH], [vx - 0.5 * Ta, bot]], 1 * u, "#e8c45a"); p.stroke([[vx + 0.5 * Ta, by0 + 0.02 * HH], [vx + 0.5 * Ta, bot]], 1 * u, "#e8c45a");
  }
  if (o.sailorCollar) { // square collar with three tapes, neckerchief knot
    const sc = o.sailorCollar;
    p.poly([[vx - 0.72 * Ta, top], [vx + 0.72 * Ta, top], [vx + 0.7 * Ta, chin + 0.14 * HH], [vx, chin + 0.44 * HH], [vx - 0.7 * Ta, chin + 0.14 * HH]], sc, 1.6 * u);
    for (const k of [0.6, 0.66, 0.72]) p.stroke([[vx - k * Ta, chin + 0.12 * HH * (k / 0.72)], [vx, chin + 0.44 * HH * (k / 0.72) - 0.02 * HH], [vx + k * Ta, chin + 0.12 * HH * (k / 0.72)]], 1.1 * u, "#f4f4f2");
    p.poly([[vx - 0.2 * Ta, chin + 0.04 * HH], [vx + 0.2 * Ta, chin + 0.04 * HH], [vx, chin + 0.3 * HH]], o.shirt ?? "#f4f4f2", 1.2 * u);
    p.poly([[vx - 7 * u, chin + 0.36 * HH], [vx + 7 * u, chin + 0.36 * HH], [vx + 5 * u, chin + 0.62 * HH], [vx, chin + 0.56 * HH], [vx - 5 * u, chin + 0.62 * HH]], o.tie ?? "#1e1c24", 1.2 * u);
  }
  const vBot = chin + (o.lapels ? 0.62 : 0.42) * HH;
  if (o.lapels) {
    // open jacket: V of vest (or shirt), notched lapels in a darker jacket shade
    const V: P2[] = [[vx - 0.44 * Ta, top], [vx, vBot], [vx + 0.44 * Ta, top]];
    p.poly(V, o.vest ?? shirt, 1.6 * u);
    if (o.vest) {
      p.poly([[vx - 0.2 * Ta, top], [vx, chin + 0.3 * HH], [vx + 0.2 * Ta, top]], shirt, 1.2 * u);
      for (let i = 0; i < 3; i++) p.dot(vx, chin + 0.36 * HH + i * 0.08 * HH, 1.8 * u, shade(o.vest, 0.6));
      if (o.watch) p.arc(vx - 0.18 * Ta, chin + 0.42 * HH, 0.18 * Ta, 0.06 * HH, 10, 170, 1.3 * u, "#e8c45a");
    }
    for (const s of [-1, 1]) {
      const lp: P2[] = [[vx + s * 0.44 * Ta, top], [vx + s * 0.46 * Ta, chin + 0.06 * HH], [vx + s * 0.62 * Ta, chin + 0.1 * HH], [vx + s * 0.5 * Ta, chin + 0.2 * HH], [vx + s * 2 * u, vBot - 2 * u], [vx, vBot]];
      p.poly(lp, mul(o.jacket, [0.82, 0.82, 0.88]), 1.6 * u);
    }
  } else if (o.vest) {
    p.poly([[vx - 0.62 * Ta, chin + 0.02 * HH], [vx - 0.08 * Ta, chin + 0.42 * HH], [vx, chin + 0.32 * HH], [vx + 0.08 * Ta, chin + 0.42 * HH], [vx + 0.62 * Ta, chin + 0.02 * HH],
      [vx + 0.72 * Ta, bot + 4 * u], [vx - 0.72 * Ta, bot + 4 * u]], o.vest, 2.2 * u);
    p.poly([[vx - 0.2 * Ta, chin + 0.02 * HH], [vx, chin + 0.3 * HH], [vx + 0.2 * Ta, chin + 0.02 * HH]], shirt, 1.6 * u);
    for (const s of [-1, 1]) p.poly([[vx + s * 0.5 * Ta, chin + 0.62 * HH], [vx + s * 0.22 * Ta, chin + 0.62 * HH], [vx + s * 0.22 * Ta, chin + 0.68 * HH], [vx + s * 0.5 * Ta, chin + 0.68 * HH]], shade(o.vest, 0.75), 1 * u);
    if (o.watch) p.arc(vx - 0.18 * Ta, chin + 0.56 * HH, 0.2 * Ta, 0.07 * HH, 10, 170, 1.3 * u, "#e8c45a");
  }
  if (o.waist) {
    const y = bot - 0.2 * HH;
    p.band([[tcx - 1.3 * Ta, y], [tcx + 1.3 * Ta, y]], o.waist, 0.07 * HH, 1.4 * u);
    p.poly(rrect(vx - 5 * u, y - 4.5 * u, vx + 5 * u, y + 4.5 * u, 1.2 * u), "#e8c45a", 1.4 * u);
  }
  if (o.tie) {
    const tb = o.lapels ? vBot + 0.06 * HH : chin + 0.62 * HH;
    p.poly([[vx - 3 * u, chin + 0.02 * HH], [vx + 3 * u, chin + 0.02 * HH], [vx + 5.5 * u, tb - 0.1 * HH], [vx, tb], [vx - 5.5 * u, tb - 0.1 * HH]], o.tie, 1.6 * u);
    p.poly([[vx - 4 * u, chin + 0.0 * HH], [vx + 4 * u, chin + 0.0 * HH], [vx + 3 * u, chin + 0.07 * HH], [vx - 3 * u, chin + 0.07 * HH]], shade(o.tie, 0.85), 1.4 * u);
  }
  if (o.pocket) p.poly([[tcx + 0.42 * Ta, chin + 0.22 * HH], [tcx + 0.48 * Ta, chin + 0.17 * HH], [tcx + 0.54 * Ta, chin + 0.21 * HH], [tcx + 0.6 * Ta, chin + 0.16 * HH], [tcx + 0.64 * Ta, chin + 0.24 * HH], [tcx + 0.44 * Ta, chin + 0.26 * HH]], typeof o.pocket === "boolean" ? "#f4f0e6" : o.pocket, 1.2 * u);
  if (o.lapels) for (const s of [-1, 1]) p.stroke([[tcx + s * 0.5 * Ta, bot - 0.32 * HH], [tcx + s * 0.85 * Ta, bot - 0.33 * HH]], 1.4 * u, shade(o.jacket, 0.6));
  // buttons: below the V on an open jacket, on the vest for shirt-sleeve outfits, else down the front
  const by0 = o.lapels ? vBot + 0.08 * HH : o.vest ? chin + 0.46 * HH : chin + 0.12 * HH, n = o.coat && !o.lapels ? 0 : o.lapels ? 2 : 4;
  for (let i = 0; i < n; i++) {
    const y = by0 + i * (o.lapels ? 0.16 : 0.2) * HH;
    if (y > bot - 0.05 * HH) break;
    if (o.sash && Math.abs(y - (bot - 0.32 * HH)) < 0.08 * HH) continue;
    p.dot(vx, y, 2.2 * u + 0.8 * u, INK); p.dot(vx, y, 2.2 * u, o.buttons ?? shade(o.jacket, 0.7));
  }
};

/** aiming rifle line (butt, muzzle) from the shoulder point S, in canvas units */
const aimLine = (S: P2, HH: number): [P2, P2] => [[S[0] - 0.18 * HH, S[1] + 0.02 * HH], [S[0] + 1.45 * HH, S[1] - 0.05 * HH]];
/** muzzle of an aiming soldier in design units (600 x 1000, soles at 975), for placing the muzzle flash */
export const aimTip = (o: Outfit, seed: number, pose = 0): [number, number] => {
  const Bd = BUILD[o.build ?? "adult"], H = headBlob(seed, Bd.a, 1), W = 2 * H.a, HH = 2 * H.b, u = W / 100;
  const legLen = (Bd.legs + 0.12) * HH - 4 * u, ankY = 975 - 4 * u, hipY = ankY - 0.94 * legLen;
  const torsoBot = hipY + 0.12 * HH, chin = torsoBot - Bd.torso * HH;
  const Ta = (o.build === "stout" ? 0.36 : 0.31) * W, S: P2 = [300 + 2 * u + 0.05 * Ta, chin + 0.14 * HH];
  const tip = aimLine(S, HH)[1];
  return rotAbout(tip, rad(6 - 8 * pose), [300, hipY]);
};

/** side view facing screen-right; march footfalls land at phase 0 (near foot) and 0.5 (far foot), like the front view.
 *  The stance foot is planted: it slides back at exactly the walking speed while the hip rises and falls over it. */
export const bodySide = (p: Pen, o: Outfit, opts: SideOpts) => {
  const { phase = 0, expr = "neutral", mode = "march", blink = false, stomp = 1, pose = 0, stride = 1, light = DEF_LIGHT, seed = 1 } = opts;
  const Bd = BUILD[o.build ?? "adult"], skin = o.skin ?? SKIN, two = Math.PI * 2, lid = lidOf(blink);
  const H: Blob = headMod(o, { ...headBlob(seed, Bd.a, 1), asym: 0.12, rot: rad(3 + 3 * (rnd(seed, 7) - 0.5)) });
  const W = 2 * H.a, HH = 2 * H.b, u = W / 100, sole = 975, ankY = sole - 4 * u;
  const thick = thickAngle(light), ow = 5 * u;
  const legLen = (Bd.legs + 0.12) * HH - 4 * u, l1 = legLen / 2, l2 = legLen / 2;
  const nearCol = mix(o.pants, INK, 0.55), farCol = mix(o.pants, INK, 0.75), footCol = o.boots;
  type LegS = { ank: P2; pitch: number; near: boolean; knee?: P2 };
  const legs: LegS[] = [];
  let hipY = ankY - legLen * 0.995, lean = 0, nearFwd = 0;
  const run = mode === "run";
  if (mode === "march" || run) {
    const S = 370 * stride * (run ? 1.5 : 1), liftH = run ? 80 : Math.max(22, 40 + 70 * (stomp - 1));
    const st = (ph: number) => {
      const c = (((phase + ph) % 1) + 1) % 1;
      if (c < 0.5) { const s = c / 0.5; return { x: S / 2 - S * s, h: 0, stance: true, s }; }
      const s = (c - 0.5) / 0.5; // swing: cycloid in world space, so the foot leaves and lands at zero ground speed
      return { x: -S / 2 + S * s - (S / Math.PI) * Math.sin(2 * Math.PI * s), h: liftH * Math.sin(Math.PI * s), stance: false, s };
    };
    const nL = st(0), fL = st(0.5), stance = nL.stance ? nL : fL;
    const Leff = legLen * (1 - 0.035 * Math.sin(Math.PI * stance.s));
    hipY = ankY - Math.sqrt(Math.max(1, Leff * Leff - stance.x * stance.x));
    for (const [L, near] of [[fL, false], [nL, true]] as const)
      legs.push({ ank: [300 + L.x, ankY - L.h], pitch: L.stance ? 0 : rad(35 * Math.sin(Math.PI * L.s) * (1 - 1.6 * L.s)), near });
    lean = 4 + 3 * Math.cos(2 * two * phase) + (run ? 8 : 0); // 7 deg at contact, 1 deg at passing
    nearFwd = nL.x / (S / 2);
  } else if (mode === "push") {
    hipY = ankY - 0.87 * legLen;
    legs.push({ ank: [300 - 0.5 * legLen, ankY], pitch: rad(-8), near: false }, { ank: [300 + 0.32 * legLen, ankY], pitch: 0, near: true });
    lean = 14 * pose;
  } else if (mode === "swing") {
    hipY = SWING_HIP;
    const a = rad(60 * pose);
    for (const [dx, near] of [[-6, false], [0, true]] as const) {
      const knee: P2 = [300 + l1 * 0.98 + dx * u, hipY + 6 * u];
      legs.push({ ank: [knee[0] + l2 * Math.sin(a), knee[1] + l2 * Math.cos(a)], pitch: -a * 0.5, near });
    }
  } else if (mode === "aim" && opts.kneel) {
    hipY = ankY - 0.56 * legLen;
    legs.push({ ank: [300 - 0.5 * legLen, ankY - 6 * u], pitch: rad(-70), near: false, knee: [300 - 0.02 * legLen, ankY - 4 * u] },
      { ank: [300 + 0.42 * legLen, ankY], pitch: 0, near: true });
    lean = 4 - 8 * pose;
  } else if (mode === "aim") {
    hipY = ankY - 0.94 * legLen;
    legs.push({ ank: [300 - 0.3 * legLen, ankY], pitch: 0, near: false }, { ank: [300 + 0.24 * legLen, ankY], pitch: 0, near: true });
    lean = 6 - 8 * pose; // pose = recoil 0..1 (rocks back on the shot)
  } else {
    legs.push({ ank: [300 - 4 * u, ankY], pitch: 0, near: false }, { ank: [300 + 4 * u, ankY], pitch: 0, near: true });
  }
  const torsoBot = hipY + 0.12 * HH, chin = torsoBot - Bd.torso * HH, hc = chin - H.b, crown = hc - H.b, hip: P2 = [300, hipY];
  p.rot = null;
  for (const L of legs) {
    const knee = L.knee ?? (mode === "swing" ? ([300 + l1 * 0.98 + (L.near ? 0 : -6 * u), hipY + 6 * u] as P2) : ik(hip, L.ank, l1, l2));
    const hp0: P2 = [300 + (L.near ? 0 : -5 * u), hipY];
    p.stroke([hp0, knee, L.ank], 5.8 * u, L.near ? nearCol : farCol);
    const c = Math.cos(L.pitch), s = Math.sin(L.pitch);
    footStroke(p, [L.ank[0] - 3 * u * c, L.ank[1] - 3 * u * s], [L.ank[0] + 13 * u * c, L.ank[1] + 13 * u * s + 0.5 * u],
      7.5 * u, L.near ? footCol : footCol === INK ? INK : shade(footCol, 0.82));
  }
  // ---- upper body leans about the hip ----
  p.rot = lean ? [rad(lean), 300, hipY] : null;
  const T: Blob = { a: (o.build === "stout" ? 0.36 : 0.31) * W, b: 0.5 * (torsoBot - (chin - 0.25 * HH)), nTop: 2.2, nBot: 2.5, egg: 0.1, asym: 0.06,
    rot: 0, noise: 0.006, seed: seed + 7 };
  const tcx = 300 + 2 * u, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
  const armCol = mix(o.jacket, INK, 0.5), farArm = mix(o.jacket, INK, 0.68);
  const S: P2 = [tcx + 0.05 * T.a, chin + 0.14 * HH], aLen = 0.95 * HH;
  const swingArm = (ang: number): [P2, P2, P2] => {
    const e: P2 = [S[0] + Math.sin(ang) * aLen * 0.5, S[1] + Math.cos(ang) * aLen * 0.5], a2 = ang + rad(16) * Math.sign(ang || 1);
    return [S, e, [e[0] + Math.sin(a2) * aLen * 0.5, e[1] + Math.cos(a2) * aLen * 0.5]];
  };
  const rifle = !!o.rifle && (mode === "march" || mode === "stand" || run);
  const B0: P2 = [tcx + 0.72 * T.a, chin + 0.58 * HH], B1: P2 = [tcx - 0.95 * T.a - 22 * u, crown - 0.4 * HH];
  let near: [P2, P2, P2], far: [P2, P2, P2] | null;
  if (mode === "swing") { near = [S, [S[0] + 12 * u, S[1] - 0.16 * HH], [300 + 6 * u, chin - 0.3 * HH]]; far = [S, [S[0] + 8 * u, S[1] - 0.18 * HH], [300 + 2 * u, chin - 0.36 * HH]]; }
  else if (mode === "push") {
    const reach = 0.55 * HH + 0.45 * HH * pose;
    let hN: P2 = [S[0] + reach, S[1] + 0.06 * HH];
    if (opts.hand) {
      // target is in final canvas units; the arm is drawn inside the lean rotation, so undo it
      const th = -rad(lean), dx = opts.hand[0] - 300, dy = opts.hand[1] - hipY;
      const tg: P2 = [300 + dx * Math.cos(th) - dy * Math.sin(th), hipY + dx * Math.sin(th) + dy * Math.cos(th)];
      hN = [hN[0] + (tg[0] - hN[0]) * pose, hN[1] + (tg[1] - hN[1]) * pose];
    }
    near = [S, [(S[0] + hN[0]) / 2, (S[1] + hN[1]) / 2 + 0.06 * HH], hN];
    far = [S, [(S[0] + hN[0]) / 2 - 4 * u, (S[1] + hN[1]) / 2 - 0.02 * HH], [hN[0] - 6 * u, hN[1] - 0.08 * HH]];
  } else if (mode === "aim") {
    const [Ab, At] = aimLine(S, HH);
    const g1 = lerp2(Ab, At, 0.2), g2 = lerp2(Ab, At, 0.55);
    near = [S, [S[0] + 0.05 * HH, S[1] + 0.3 * HH], [g1[0], g1[1] + 3 * u]];
    far = [S, [S[0] + 0.4 * HH, S[1] + 0.28 * HH], [g2[0], g2[1] + 3 * u]];
  } else if (rifle) { near = [S, [S[0] - 4 * u, S[1] + 0.42 * HH], B0]; far = mode === "march" || run ? swingArm(rad(run ? 50 : 30) * nearFwd) : swingArm(0); }
  else if (run) { // bent, pumping arms
    const arm = (k: number): [P2, P2, P2] => { const e: P2 = [S[0] + k * 0.3 * HH, S[1] + 0.36 * HH]; return [S, e, [e[0] + 0.22 * HH, e[1] - 0.08 * HH - k * 0.2 * HH]]; };
    near = arm(-nearFwd); far = arm(nearFwd);
  }
  else { near = swingArm(rad(-30) * nearFwd); far = mode === "march" ? swingArm(rad(30) * nearFwd) : null; }
  if (far) { p.stroke(curve(far[0], far[1], far[2]), 5.2 * u, farArm); p.dot(far[2][0], far[2][1], 5.5 * u); }
  p.gradFill(tp, o.jacket, mul(o.jacket, SH_CLOTH), light);
  p.clip(tp, () => {
    if (o.belt) p.band([[tcx - 0.65 * T.a, chin - 0.05 * HH], [tcx + 0.75 * T.a, torsoBot - 0.1 * HH]], o.belt!, 5.5 * u, 1.8 * u);
    if (o.sash) p.band([[tcx - 1.3 * T.a, torsoBot - 0.32 * HH], [tcx + 1.3 * T.a, torsoBot - 0.32 * HH]], o.sash, 0.13 * HH, 1.8 * u);
    if (!o.dress) for (let i = 0; i < 3; i++) { const y = chin + 0.16 * HH + i * 0.24 * HH; p.dot(tcx + 0.8 * T.a, y, 3 * u, INK); p.dot(tcx + 0.8 * T.a, y, 2.2 * u, o.buttons ?? shade(o.jacket, 0.7)); }
  });
  p.inkRing(tp, ow, thick);
  if (rifle) {
    p.band([B0, B1], "#7a4b2a", 5 * u, 1.5 * u, "round");
    p.band([lerp2(B0, B1, 0.6), B1], "#8d949c", 2.4 * u, 1.2 * u, "round");
  }
  if (mode === "aim" && o.smg && !o.rifle) { const [Ab, At] = aimLine(S, HH); smgDraw(p, Ab, lerp2(Ab, At, 0.72), u, o.smg); }
  if (mode === "aim" && o.rifle) {
    const [Ab, At] = aimLine(S, HH);
    p.band([Ab, lerp2(Ab, At, 0.62)], "#7a4b2a", 6 * u, 1.5 * u, "round");
    p.band([lerp2(Ab, At, 0.5), At], "#8d949c", 2.6 * u, 1.2 * u, "round");
  }
  p.stroke(curve(near[0], near[1], near[2]), 5.2 * u, armCol); p.dot(near[2][0], near[2][1], 5.5 * u);
  // ---- head ----
  const hx = 300 + 4 * u;
  hatBehind(p, o, H, hx, hc, light, thick, ow, true);
  const hp = blobPts(hx, hc, H);
  p.shadedFill(hp, skin, mul(skin, SH_SKIN), light, H.a);
  p.inkRing(hp, ow, thick);
  hatOn(p, o, hp, H, hx, hc, light, seed, 1, true);
  const brim = !!o.hat && o.hat !== "hair" && o.hat !== "bonnet" && o.hat !== "cap";
  faceSide(p, hx, hc, W, expr, lid, brim, skin, o);
  p.rot = null;
};

/** rope + seat + seated kid on a 700 x 2300 canvas; the pivot is design (350, 20); kid drawn at 0.92 scale */
export const swingKid = (p: Pen, o: Outfit, kick: number, expr: Expr, light = DEF_LIGHT, blink: number = 0) => {
  const rope = 1830, k = 1.1, HH = 2 * headBlob(5, BUILD[o.build ?? "adult"].a, 1).b;
  // two ropes from the pivot to the ends of a wide plank, the kid framed between them: a single rope behind the kid
  // ended at the cap and read as a hanging. Far rope behind the kid, near rope drawn over (clear of the face).
  const seat = rope + 18, x0 = 150, x1 = 550;
  p.line([[350, 20], [x0 + 16, seat + 4]], "#a07a4c", 10);
  p.poly(rrect(x0, seat, x1, seat + 36, 10), "#b5653f", 9);
  const g = p.g;
  g.save();
  g.translate(350 - 300 * k, rope + 18 - (SWING_HIP + 0.12 * HH) * k);
  g.scale(k, k);
  bodySide(new Pen(g), o, { expr, mode: "swing", pose: kick, light, seed: 5, blink });
  g.restore();
  p.line([[350, 20], [x1 - 16, seat + 4]], "#a07a4c", 10);
};

// ---------------- effects ----------------
export const fxNote = (p: Pen, kind: number, col = "#1f2a44") => {
  p.ell(70, 200, 46, 34, col, 8, 0, 360, -20);
  p.stroke([[110, 190], [110, 40]], 14);
  if (kind === 0) p.poly([[110, 40], [170, 70], [170, 110], [110, 82]], col, 8);
  else {
    p.ell(150, 170, 40, 30, col, 8, 0, 360, -20);
    p.stroke([[186, 160], [186, 20]], 14);
    p.poly([[110, 40], [186, 20], [186, 50], [110, 70]], col, 8);
  }
};

/** spark / impact star on a 500 x 500 canvas; t in 0..1 */
export const fxBurst = (p: Pen, t: number, col = "#fff3b0", rays = 10, r0 = 40, r1 = 230) => {
  const c = 250, e = 1 - (1 - t) ** 3;
  for (let i = 0; i < rays; i++) {
    const a = rad((i * 360) / rays + 7 * (i % 2)), ra = r0 + (r1 - r0) * e * (0.75 + 0.25 * (i % 2));
    p.poly([[c + r0 * 0.5 * Math.cos(a + 0.18), c + r0 * 0.5 * Math.sin(a + 0.18)], [c + ra * Math.cos(a), c + ra * Math.sin(a)],
      [c + r0 * 0.5 * Math.cos(a - 0.18), c + r0 * 0.5 * Math.sin(a - 0.18)]], col, Math.max(3, 8 * (1 - t)));
  }
  if (t < 0.5) p.ell(c, c, r0 * (1.4 - t), r0 * (1.4 - t), WHITE, 8);
};

/** water splash crown on an 800 x 800 canvas; t in 0..1 */
export const fxSplash = (p: Pen, t: number) => {
  const c = 400, size = 800, rise = Math.sin(Math.min(1, t * 1.3) * Math.PI);
  const blue = "#bfe8ff", deep = "#6cc0f0";
  if (rise > 0.02) {
    const pts: P2[] = [];
    for (let i = 0; i < 19; i++) {
      const h = (i % 2 ? 260 : 130) * rise * (0.7 + 0.3 * Math.sin(i * 1.7));
      pts.push([c - 330 + (660 * i) / 18, size - 120 - h]);
    }
    p.poly([...pts, [c + 330, size - 90], [c - 330, size - 90]], blue, 10);
    p.ell(c, size - 100, 360, 46, deep, 10);
  }
  for (let i = 0; i < 8; i++) {
    const a = rad(200 + i * 18), d = 120 + 380 * t, y = size - 160 + d * Math.sin(a) + 520 * t * t, r = 26 * (1 - t) + 6;
    if (t > 0.08 && y < size - 40) p.ell(c + d * Math.cos(a), y, r, r * 1.25, blue, 7);
  }
};

/** dust puff on a 300 x 300 canvas; t in 0..1 */
export const fxPuff = (p: Pen, t: number) => {
  for (let i = 0; i < 5; i++) {
    const a = rad(160 + i * 55), d = 40 + 70 * t, r = (34 + 20 * (i % 2)) * (1 - 0.6 * t);
    p.ell(150 + d * Math.cos(a), 180 + d * 0.45 * Math.sin(a), r, r * 0.8, `rgba(238,225,205,${(1 - t).toFixed(3)})`, 0);
  }
};

/** circling stars on a 420 x 210 canvas */
export const fxStars = (p: Pen, t: number) => {
  for (let i = 0; i < 4; i++) {
    const a = t * Math.PI * 2 + (i * Math.PI) / 2, x = 210 + 150 * Math.cos(a), y = 110 + 40 * Math.sin(a), pts: P2[] = [];
    for (let k = 0; k < 10; k++) { const r = k % 2 ? 14 : 34, b = rad(k * 36 - 90); pts.push([x + r * Math.cos(b), y + r * Math.sin(b)]); }
    p.poly(pts, "#ffd84a", 6);
  }
};

/** three jittering strain ticks on a 300 x 300 canvas */
export const fxCreak = (p: Pen, t: number) => {
  const j = 6 * Math.sin(t * 40);
  for (const a of [-30, 0, 30]) {
    const b = rad(a - 90);
    p.stroke([[150 + 70 * Math.cos(b) + j, 230 + 70 * Math.sin(b)], [150 + 100 * Math.cos(b) + 10 + j, 230 + 100 * Math.sin(b)],
      [150 + 130 * Math.cos(b) + j, 230 + 130 * Math.sin(b)]], 10);
  }
};

/** flat water ring (drawn top-down) on a 600 x 600 canvas; t in 0..1 */
export const fxRing = (p: Pen, t: number) => {
  // thin light water rings (white crest, pale blue trailing rings), thinning as they spread
  const g = p.g;
  for (let k = 0; k < 3; k++) {
    const u = t - k * 0.22;
    if (u <= 0 || u >= 1) continue;
    g.beginPath(); g.ellipse(300, 300, 60 + 230 * u, 60 + 230 * u, 0, 0, Math.PI * 2);
    g.strokeStyle = k === 0 ? "#f6fcff" : "#cfe8fa"; g.lineWidth = 9 * (1 - u) + 3; g.stroke();
  }
};

/** text-free sign on a 700 x 520 canvas: "no marching in step on the bridge". A bridge (deck + arch + piers), four
 *  identical pairs of marching legs in the same stride (in step), a bold red X over all of it. */
export const fxSign = (p: Pen) => {
  const g = p.g, RED = "#d42f2f";
  p.poly(rrect(14, 14, 686, 506, 40), "#f6ecd2", 0);
  p.poly(rrect(14, 14, 686, 506, 40), null, 14);
  // bridge: deck, stone arch underneath, two piers
  p.poly(rrect(70, 352, 630, 384, 8), "#8a5a3a", 9);
  g.beginPath(); g.moveTo(112, 470); g.quadraticCurveTo(350, 300, 588, 470);
  g.strokeStyle = INK; g.lineWidth = 16; g.lineCap = "round"; g.stroke();
  for (const x of [88, 612]) p.poly(rrect(x - 16, 384, x + 16, 470, 4), "#8a5a3a", 9);
  // four identical soldiers' legs mid-stride: same leg forward on every one = in step
  for (const x of [150, 278, 406, 534]) {
    p.poly(rrect(x - 30, 150, x + 30, 214, 14), "#357650", 9);                  // coat hem
    p.stroke([[x - 8, 210], [x + 34, 262], [x + 46, 338]], 15, INK);           // front leg
    p.stroke([[x + 6, 210], [x - 12, 274], [x - 36, 336]], 15, INK);           // back leg
    p.poly(rrect(x + 30, 330, x + 74, 350, 9), INK, 0);                          // boots point forward
    p.poly(rrect(x - 52, 328, x - 8, 348, 9), INK, 0);
  }
  // big red X
  for (const [a, b] of [[[96, 70], [604, 452]], [[604, 70], [96, 452]]] as [[number, number], [number, number]][]) {
    p.stroke([a, b], 58, "#ffffff");
    p.stroke([a, b], 42, RED);
  }
};

/** soft cartoon cloud on a 600 x 300 canvas */
export const fxCloud = (p: Pen, seed: number) => {
  const blobs: [number, number, number][] = [[150, 190, 80], [250, 150, 105], [360, 160, 95], [450, 195, 70], [300, 210, 90]];
  for (const [x, y, r] of blobs) p.ell(x + ((seed * 37) % 20) - 10, y, r, r * 0.8, "#ffffff", 0);
  p.ell(300, 235, 230, 40, "#ffffff", 0);
};

/** cast shadow on a 128 x 256 canvas: dark soft contact pool at the feet (y 205) and a softer tail that runs up the
 *  canvas = away from the sun, fading with distance; multiply colour (sRGB-encoded linear ratio), white = no change */
export const fxShadow = (p: Pen, col: string) => {
  const g = p.g;
  g.fillStyle = WHITE; g.fillRect(0, 0, 128, 256);
  g.save(); g.filter = "blur(9px)";
  const lg = g.createLinearGradient(0, 205, 0, 22);
  lg.addColorStop(0, mix(col, WHITE, 0.08)); lg.addColorStop(0.55, mix(col, WHITE, 0.3)); lg.addColorStop(1, mix(col, WHITE, 0.85));
  g.fillStyle = lg;
  g.beginPath(); g.moveTo(40, 205); g.bezierCurveTo(36, 120, 46, 50, 64, 30); g.bezierCurveTo(82, 50, 92, 120, 88, 205); g.closePath(); g.fill();
  g.fillStyle = col; g.beginPath(); g.ellipse(64, 205, 30, 17, 0, 0, Math.PI * 2); g.fill();
  g.restore();
};

/** tight contact shadow right under the feet on a 128 x 128 canvas: dark core, short fall-off (multiply colour) */
export const fxContact = (p: Pen, col: string) => {
  const g = p.g;
  g.fillStyle = WHITE; g.fillRect(0, 0, 128, 128);
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  for (const [r, k] of [[0, 0], [0.32, 0.02], [0.5, 0.22], [0.66, 0.58], [0.82, 0.88], [1, 1]] as const) gr.addColorStop(r, mix(col, WHITE, k));
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
};

/** floating wooden plank, side-on, on a 320 x 110 canvas */
export const fxPlank = (p: Pen) => {
  p.poly(rrect(14, 30, 306, 78, 10), "#a8744a", 9);
  p.line([[40, 46], [150, 44], [270, 50]], "#7d5234", 4);
  p.line([[60, 62], [200, 64], [284, 60]], "#7d5234", 4);
  p.dot(36, 54, 5, INK); p.dot(284, 54, 5, INK);
};

/** floating marching drum (no text) on a 260 x 240 canvas: white shell, red hoops, ink zig-zag cord */
export const fxDrum = (p: Pen) => {
  p.poly(rrect(40, 70, 220, 190, 16), "#f1ece0", 9);
  p.poly(rrect(32, 58, 228, 86, 12), "#c9373a", 8);
  p.poly(rrect(32, 176, 228, 204, 12), "#c9373a", 8);
  p.line([[52, 88], [82, 172], [112, 88], [142, 172], [172, 88], [202, 172]], INK, 6);
  p.ell(130, 58, 98, 18, "#f7f3ea", 8);
};

/** soft ground contact blob on a 128 x 128 canvas, multiply colour (sRGB-encoded linear ratio) in the centre */
export const fxBlob = (p: Pen, col: string) => {
  const g = p.g;
  g.fillStyle = WHITE; g.fillRect(0, 0, 128, 128);
  // soft contact shadow: flat core, then a long smooth (roughly gaussian) fall-off to white = no change
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  for (const [r, k] of [[0, 0], [0.5, 0.04], [0.64, 0.18], [0.76, 0.42], [0.87, 0.72], [0.95, 0.92], [1, 1]] as const) gr.addColorStop(r, mix(col, WHITE, k));
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
};

// ---------------- Kiska extras ----------------
export type DogOpts = { coat: string; patch?: string; ear: string; expr: "pant" | "happy" | "alert"; wag: number; cap?: boolean; lid?: number; tilt?: number };
/** sitting dog, front view, on the 600 x 1000 character canvas (paws at y 975, ~1.45 m at scale 1: place at ~0.45) */
export const dogSit = (p: Pen, d: DogOpts) => {
  const o = 12, C = d.coat, Sh = mul(C, SH_CLOTH);
  // tail (behind): wags left-right
  const ta = rad(-30 + 60 * d.wag);
  p.line([[372, 900], [372 + 150 * Math.sin(ta + 0.9), 900 - 150 * Math.cos(ta + 0.9) + 40]], C, 26);
  // haunches + chest
  p.ell(220, 900, 95, 75, Sh, o); p.ell(380, 900, 95, 75, Sh, o);
  const chest = ellPts(300, 760, 120, 190, 0, 360, 0, 48);
  p.gradFill(chest, C, Sh, rad(-120));
  if (d.patch) p.clip(chest, () => p.ell(250, 700, 70, 90, d.patch!, 0));
  p.poly(chest, null, o);
  p.ell(300, 790, 60, 110, mix(C, "#ffffff", 0.35), 0); // light bib
  // front legs + paws
  for (const x of [255, 345]) { p.line([[x, 820], [x, 950]], C, 46); p.ell(x, 960, 34, 20, mix(C, "#ffffff", 0.2), 9); }
  // head (tilt in degrees)
  const g = p.g; g.save(); g.translate(300, 520); g.rotate(rad(d.tilt ?? 0)); g.translate(-300, -520);
  // ears (floppy)
  for (const s of [-1, 1]) p.poly(rrect(300 + s * 135 - 42, 420, 300 + s * 135 + 42, 600, 40), d.ear, o);
  const head = ellPts(300, 500, 135, 120, 0, 360, 0, 48);
  p.gradFill(head, C, Sh, rad(-120));
  if (d.patch) p.clip(head, () => p.ell(230, 470, 70, 80, d.patch!, 0));
  p.poly(head, null, o);
  // muzzle, nose, mouth
  p.ell(300, 580, 72, 52, mix(C, "#ffffff", 0.45), 9);
  p.ell(300, 552, 26, 18, INK, 0);
  if (d.expr === "pant") {
    p.poly([[268, 592], [332, 592], [322, 650], [300, 668], [278, 650]], TONGUE, 8);
    p.stroke([[300, 600], [300, 640]], 4, "#c2485a");
  } else p.stroke(curve([262, 600], [300, d.expr === "happy" ? 622 : 606], [338, 600]), 8);
  // eyes (blink lid 0..1)
  const lid = d.lid ?? 0;
  for (const s of [-1, 1]) {
    if (lid > 0.7) p.stroke([[300 + s * 52 - 14, 480], [300 + s * 52 + 14, 480]], 8);
    else if (d.expr === "happy") p.arc(300 + s * 52, 486, 16, 12, 200, 340, 8);
    else p.ell(300 + s * 52, 480, 13, 16 * (1 - lid * 0.6), INK, 0);
  }
  // white US Navy cap, brim turned up, tipped on the head
  if (d.cap) {
    p.poly(ellPts(318, 398, 66, 46, 180, 360, -12, 24), "#f4f4f2", 9);
    p.poly([[244, 404], [392, 372], [396, 398], [250, 430]], "#ffffff", 9);
  }
  g.restore();
};

/** a long coat and a hat on a door hook: in the dark it reads as a person (on the 600 x 1000 canvas) */
export const coatOnHook = (p: Pen, col = "#4a4038") => {
  const Sh = shade(col, 0.7);
  p.stroke([[300, 150], [300, 205]], 12, "#7d848c"); // hook
  // hat
  p.ell(300, 205, 120, 18, shade(col, 0.6), 10);
  p.poly(ellPts(300, 205, 78, 78, 180, 360, 0, 24), shade(col, 0.75), 10);
  // shoulders + long coat
  const coat: P2[] = [[300, 215], [410, 270], [440, 330], [430, 900], [170, 900], [160, 330], [190, 270]];
  p.gradFill(coat, col, Sh, rad(-120));
  p.poly(coat, null, 12);
  p.stroke([[300, 240], [300, 900]], 6, Sh);
  for (const y of [380, 470, 560]) p.dot(318, y, 9, "#2a2420");
  p.poly([[300, 228], [258, 300], [300, 330], [342, 300]], shade(col, 0.6), 8); // collar
  // sleeves hanging
  for (const s of [-1, 1]) p.line([[300 + s * 130, 320], [300 + s * 140, 640]], col, 44);
};

/** fireball (bomb / shell), t 0..1 on a 600 x 600 canvas: white-hot core grows into orange, then grey smoke */
export const fxBoom = (p: Pen, t: number) => {
  const r = 80 + 200 * Math.sqrt(t), smoke = Math.max(0, (t - 0.35) / 0.65);
  const pts: [number, number, number][] = [[300, 330, 1], [210, 300, 0.7], [390, 300, 0.75], [260, 220, 0.65], [350, 210, 0.7], [300, 400, 0.6]];
  for (const [x, y, k] of pts) p.ell(300 + (x - 300) * (r / 220), 330 + (y - 330) * (r / 220) - 60 * smoke, k * r * 0.62, k * r * 0.58, mix("#ff8a2a", "#5d5866", smoke), 8);
  if (t < 0.6) for (const [x, y, k] of pts.slice(0, 4)) p.ell(300 + (x - 300) * (r / 300), 340 + (y - 330) * (r / 300), k * r * 0.4, k * r * 0.36, mix("#ffe36a", "#ff9a3a", t / 0.6), 0);
  if (t < 0.25) p.ell(300, 340, r * 0.3, r * 0.28, "#fffbe0", 0);
};
/** muzzle flash, side-on, pointing +x on a 300 x 200 canvas */
export const fxMuzzle = (p: Pen, k: number) => {
  const L = 140 + 120 * k;
  p.poly([[20, 100], [20 + L * 0.45, 40], [20 + L * 0.6, 80], [20 + L, 100], [20 + L * 0.6, 120], [20 + L * 0.45, 160]], "#ffb03a", 7);
  p.poly([[30, 100], [30 + L * 0.35, 70], [30 + L * 0.6, 100], [30 + L * 0.35, 130]], "#fff6c8", 0);
};
/** drifting fog wisp (soft, see-through card) on a 512 x 256 canvas */
export const fxMist = (p: Pen, col = "#e6ecf2") => {
  const g = p.g; g.save(); g.filter = "blur(18px)";
  for (const [x, y, rx, ry, a] of [[256, 150, 200, 55, 0.85], [150, 135, 110, 45, 0.7], [370, 140, 120, 48, 0.75], [256, 118, 120, 40, 0.6]] as const) {
    g.globalAlpha = a; g.fillStyle = col; g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2); g.fill();
  }
  g.restore();
};
/** falling bomb, side-on on a 200 x 100 canvas */
export const fxBomb = (p: Pen) => {
  p.poly(rrect(30, 32, 150, 68, 18), "#3d4248", 7);
  p.poly([[150, 50], [185, 22], [185, 78]], "#2d3136", 7);
};
/** dashed tracer streak (night fire) on a 400 x 40 canvas */
export const fxTracer = (p: Pen) => { p.line([[10, 20], [390, 20]], "#ffd36a", 10, false); p.line([[200, 20], [390, 20]], "#fff8d8", 5, false); };


// ---------------- WW2 effects ----------------
/** dark bomber silhouette, side-on, nose right, on a 600 x 200 canvas */
export const fxBomber = (p: Pen) => {
  const c = "#2a2630";
  p.poly([[40, 100], [470, 86], [560, 96], [470, 112], [60, 112]], c, 0);
  p.poly([[230, 96], [300, 20], [340, 20], [300, 98]], c, 0); p.poly([[230, 104], [300, 180], [340, 180], [300, 104]], c, 0);
  p.poly([[40, 100], [70, 40], [95, 40], [90, 100]], c, 0);
  for (const x of [270, 310]) for (const y of [52, 146]) p.ell(x, y, 16, 9, c, 0);
};
/** mushroom cloud, far away: glowing stem and cap, on a 512 x 640 canvas; t 0..1 growth */
export const fxMushroom = (p: Pen, t: number) => {
  const k = 0.55 + 0.45 * t, g = p.g;
  const gr = g.createRadialGradient(256, 200, 10, 256, 200, 260 * k);
  gr.addColorStop(0, "rgba(255,240,200,.9)"); gr.addColorStop(1, "rgba(255,160,90,0)"); g.fillStyle = gr; g.fillRect(0, 0, 512, 640);
  p.poly([[226, 640], [232, 300], [280, 300], [286, 640]], "#e8c8a8", 0);
  for (const [x, y, r] of [[256, 230, 130], [180, 250, 80], [332, 250, 80], [256, 170, 100], [200, 190, 70], [312, 190, 70]] as const) p.ell(256 + (x - 256) * k, 300 - (300 - y) * k, r * k, r * k * 0.7, "#f2d8b8", 0);
  for (const [x, y, r] of [[256, 240, 90], [220, 215, 50], [296, 215, 50]] as const) p.ell(256 + (x - 256) * k, 300 - (300 - y) * k, r * k, r * k * 0.6, "#ffe8c0", 0);
  p.ell(256, 320, 120 * k, 26 * k, "#d8b8a0", 0);
};
/** rubber stamp text (e.g. PAID / REJECTED), rotated, on a 600 x 260 canvas; k = 0..1 slam (scale down to 1) */
export const fxStamp = (p: Pen, text: string, col = "#c8202c") => {
  const g = p.g; g.save(); g.translate(300, 130); g.rotate(-0.14);
  g.strokeStyle = col; g.lineWidth = 14; g.strokeRect(-270, -95, 540, 190); g.lineWidth = 5; g.strokeRect(-250, -77, 500, 154);
  g.fillStyle = col; g.font = "bold 92px Georgia, serif"; g.textAlign = "center"; g.textBaseline = "middle";
  const lines = text.split("\n");
  lines.forEach((l, i) => { g.font = `bold ${lines.length > 1 ? 70 : 92}px Georgia, serif`; g.fillText(l, 0, (i - (lines.length - 1) / 2) * 72 + 4); });
  g.restore();
};
/** banknote on a 300 x 150 canvas */
export const fxBanknote = (p: Pen, seed = 0) => {
  p.poly(rrect(6, 6, 294, 144, 8), ["#a8c89a", "#c8b88a", "#9ab8c8"][seed % 3], 5);
  p.poly(rrect(22, 22, 278, 128, 4), null, 2);
  p.ell(150, 75, 34, 40, "#e8e0c0", 3);
  p.g.fillStyle = "#3a4a3a"; p.g.font = "bold 34px Georgia, serif"; p.g.textAlign = "center"; p.g.fillText("1000", 66, 88); p.g.fillText("1000", 236, 88);
};
/** stock chart line on a 1024 x 512 canvas: rises to x = 0.7, then (crash 0..1) falls off a cliff */
export const fxChart = (p: Pen, prog: number, crash: number) => {
  const g = p.g, pts: P2[] = [];
  const n = Math.floor(70 * prog);
  for (let i = 0; i <= n; i++) { const x = i / 70; pts.push([60 + x * 900, 440 - 330 * Math.pow(x / 0.72, 1.3) - 18 * Math.sin(i * 1.7)]); }
  if (crash > 0) { const [x0, y0] = pts[pts.length - 1]; pts.push([x0 + 30 * crash, y0 + 380 * crash]); }
  g.lineCap = "round"; g.lineJoin = "round";
  g.strokeStyle = "rgba(0,0,0,.5)"; g.lineWidth = 22; g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.stroke();
  g.strokeStyle = crash > 0 ? "#ff5a4a" : "#7aff9a"; g.lineWidth = 12; g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.stroke();
};
/** price tag text on a 768 x 230 canvas */
export const drawTag = (g: CanvasRenderingContext2D, text: string) => {
  g.fillStyle = "#f6efdc"; g.fillRect(0, 0, 768, 230); g.strokeStyle = "#3a2618"; g.lineWidth = 14; g.strokeRect(7, 7, 754, 216);
  g.fillStyle = "#3a2618"; g.font = "bold 40px Georgia, serif"; g.textAlign = "center"; g.fillText("1 BROT", 384, 60);
  g.fillStyle = "#b8202c"; let px = 92; g.font = `bold ${px}px Georgia, serif`; while (g.measureText(text).width > 700 && px > 40) { px -= 4; g.font = `bold ${px}px Georgia, serif`; } g.fillText(text, 384, 170);
};
/** padlock + chain across a door, on a 400 x 400 canvas */
export const fxPadlock = (p: Pen) => {
  for (let k = 0; k < 9; k++) p.ell(40 + k * 40, 150 + Math.sin(k * 0.7) * 8, 22, 13, null, 8);
  p.arc(200, 210, 46, 52, 180, 360, 16, "#8a8e96");
  p.poly(rrect(140, 210, 260, 330, 14), "#c8a24a", 9);
  p.ell(200, 260, 12, 14, INK, 0); p.poly([[194, 266], [206, 266], [210, 300], [190, 300]], INK, 0);
};
/** newspaper; censor = 0..1 black bars sweeping over the columns, on a 400 x 520 canvas */
export const fxNewspaper = (p: Pen, censor: number) => {
  p.poly(rrect(10, 10, 390, 510, 4), "#efe8d6", 5);
  p.g.fillStyle = "#2a2630"; p.g.font = "bold 46px Georgia, serif"; p.g.textAlign = "center"; p.g.fillText("ZEITUNG", 200, 70);
  p.stroke([[30, 92], [370, 92]], 4);
  for (let c = 0; c < 3; c++) for (let l = 0; l < 16; l++) {
    const x0 = 30 + c * 118, y = 116 + l * 24, w = 100 - ((l * 7 + c * 3) % 4) * 8;
    p.stroke([[x0, y], [x0 + w, y]], 5, "#8a8478");
    if ((l + c) % 3 !== 1 && censor * 16 > l) p.poly([[x0 - 4, y - 9], [x0 + w + 4, y - 9], [x0 + w + 4, y + 9], [x0 - 4, y + 9]], "#121014", 0);
  }
};
/** torch flame (unlit card, glows), t = flicker phase, on a 160 x 320 canvas */
export const fxFlame = (p: Pen, t: number) => {
  const w = 1 + 0.12 * Math.sin(t * 9), h = 1 + 0.15 * Math.sin(t * 13 + 1);
  p.stroke([[80, 320], [80, 200]], 14, "#4a2c18");
  p.poly([[80, 200 - 150 * h], [120 * w, 150], [104, 210], [56, 210], [40 / w, 150]], "#ff8a2a", 0);
  p.poly([[80, 200 - 100 * h], [100, 165], [90, 205], [70, 205], [60, 165]], "#ffe07a", 0);
};
/** map of Germany as a blob; k = 0..1 the border pieces slide away, on a 512 x 512 canvas */
export const fxMapCut = (p: Pen, k: number) => {
  p.poly([[110, 120], [300, 90], [420, 160], [400, 330], [300, 420], [150, 400], [90, 260]], "#d8c08a", 8);
  const pieces: [P2[], number, number][] = [
    [[[300, 90], [420, 160], [395, 210], [320, 150]], 90, -60], [[[90, 260], [150, 400], [175, 340], [130, 270]], -90, 50], [[[110, 120], [180, 108], [160, 170], [100, 190]], -70, -70],
  ];
  for (const [pts, dx, dy] of pieces) { const o = pts.map(([x, y]) => [x + dx * k, y + dy * k] as P2); p.poly(pts, "#2f5f86", 0); p.poly(o, "#c8a46a", 7); }
  p.stroke([[240, 120], [270, 380]], 3, "rgba(60,40,30,.4)");
};
