// The Kiska cast as lit flat sprites in the 3D world (same machinery as the bridge short: canvas pool, yaw-only
// billboards shaded by cardShade(), contact blobs, unlit effect cards on the NOINK layer).
import * as THREE from "three";
import {
  Pen, bodyFront, bodySide, US, CA, JP, SAILOR, PJKID, army, dogSit, coatOnHook, fxBoom, fxMuzzle, fxMist, fxBomb, fxTracer, fxSplash,
  fxShadow, fxContact, aimTip, Outfit, Expr, FrontOpts, SideOpts, DogOpts,
} from "./toon";
import { FPS, SHOTS, V3, P, clamp01, smooth, FIELD, BEACH_X, BZ, P7, P8a, P8b, P12, ROOM, USS, PIER_X, PIER_END, LANE_X, DOGS_Z, WOUNDED_X } from "./story";
import { H, shoreZ, CAMP } from "./island";
import { NOINK } from "./ink";
import { cardShade, blobMaterial, CARD_K } from "./cardshade";

// ---------------- canvas pool ----------------
type Entry = { cv: HTMLCanvasElement; tex: THREE.CanvasTexture; w: number; h: number };
export type Req = { key: string; w: number; h: number; k: number; draw: (p: Pen) => void; tex?: THREE.CanvasTexture };
const makeEntry = (w: number, h: number): Entry => {
  const cv = document.createElement("canvas");
  cv.width = w; cv.height = h;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { cv, tex, w, h };
};
export class Pool {
  private live = new Map<string, Entry>();
  private free: Entry[] = [];
  private reqs: Req[] = [];
  req(key: string, w: number, h: number, k: number, draw: (p: Pen) => void) {
    const r: Req = { key: `${w}x${h}|${key}`, w, h, k, draw };
    this.reqs.push(r);
    return r;
  }
  flush() {
    const want = new Map<string, Req[]>();
    for (const r of this.reqs) { const l = want.get(r.key); if (l) l.push(r); else want.set(r.key, [r]); }
    for (const [key, e] of this.live) if (!want.has(key)) { this.live.delete(key); this.free.push(e); }
    for (const [key, rs] of want) {
      let e = this.live.get(key);
      if (!e) {
        const r = rs[0], i = this.free.findIndex((x) => x.w === r.w && x.h === r.h);
        e = i >= 0 ? this.free.splice(i, 1)[0] : makeEntry(r.w, r.h);
        const g = e.cv.getContext("2d")!;
        g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, e.w, e.h); g.setTransform(r.k, 0, 0, r.k, 0, 0);
        r.draw(new Pen(g));
        e.tex.needsUpdate = true;
        this.live.set(key, e);
      }
      for (const r of rs) r.tex = e.tex;
    }
    this.reqs = [];
  }
}

// ---------------- sprite meshes ----------------
const blank = (() => { const c = document.createElement("canvas"); c.width = c.height = 2; return new THREE.CanvasTexture(c); })();
export const SU = 0.00216; // metres per design unit: 1000 units = 2.16 m
const BODY = (() => { const g = new THREE.PlaneGeometry(600 * SU, 1000 * SU); g.translate(0, (975 - 500) * SU, 0); return g; })();
const CARD = new THREE.PlaneGeometry(1, 1);
export class Actor {
  mesh: THREE.Mesh; mat: THREE.MeshLambertMaterial; dmat: THREE.MeshDepthMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D, geo: THREE.BufferGeometry = BODY) {
    this.mat = cardShade(new THREE.MeshLambertMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide }));
    this.mat.alphaToCoverage = false;
    this.dmat = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mesh = new THREE.Mesh(geo, this.mat);
    this.mesh.customDepthMaterial = this.dmat;
    this.mesh.onBeforeRender = (r) => { const rt = r.getRenderTarget(); CARD_K.uPx.value = (rt ? rt.height : r.domElement.height) / 1920; };
    this.mesh.castShadow = false; this.mesh.receiveShadow = true; this.mesh.visible = false;
    this.mesh.rotation.order = "YXZ"; this.mesh.renderOrder = 1; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
  }
  bind() { const t = this.r?.tex; if (t) { this.mat.map = t; this.dmat.map = t; } }
}
export class Fx {
  mesh: THREE.Mesh; mat: THREE.MeshBasicMaterial; soft: THREE.MeshBasicMaterial; blob: THREE.MeshBasicMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D) {
    this.mat = new THREE.MeshBasicMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.soft = new THREE.MeshBasicMaterial({ map: blank, transparent: true, depthWrite: false, side: THREE.DoubleSide });
    this.blob = blobMaterial(blank);
    this.mesh = new THREE.Mesh(CARD, this.mat);
    this.mesh.visible = false; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
  }
  use(soft: boolean, glow: number) {
    this.mesh.material = soft ? this.soft : this.mat;
    const m = this.mesh.material as THREE.MeshBasicMaterial;
    m.color.setScalar(glow); m.fog = !glow || glow <= 1;
  }
  bind() {
    const t = this.r?.tex;
    if (!t) return;
    if (this.r!.key.includes("|blob|")) {
      if (t.generateMipmaps) { t.generateMipmaps = false; t.minFilter = THREE.LinearFilter; t.needsUpdate = true; }
      this.blob.map = t; this.mesh.material = this.blob; this.mesh.renderOrder = 0.5;
    } else { this.mat.map = t; this.soft.map = t; this.mesh.renderOrder = (this.mesh.material as THREE.Material).transparent ? 2 : 0; }
  }
}

// ---------------- placements ----------------
export type Place = {
  key: string; draw: (p: Pen) => void; x: number; y: number; z: number;
  scale?: number; mirror?: boolean; yaw?: number; roll?: number; size?: [number, number, number];
};
/** glow > 1: HDR colour multiplier (bloom), not fogged */
export type FxPlace = { key: string; cw: number; ch: number; draw: (p: Pen) => void; x: number; y: number; z: number; w: number; h: number; flat?: boolean; rot?: number; soft?: boolean; glow?: number };
export type CamInfo = { pos: THREE.Vector3; right: THREE.Vector3; sun?: THREE.Vector3 };
export type Stage = { places: Place[]; fx: FxPlace[] };

const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
const q = (v: number, n = 120) => Math.round(v * n) / n;
const OUT: Record<string, Outfit[]> = {
  us: [0, 1, 2, 3].map((v) => army(US, v)), ca: [0, 1, 2, 3].map((v) => army(CA, v)), jp: [0, 1, 2, 3].map((v) => army(JP, v)),
};
const seedOf = (i: number) => ((i * 5 + 3) % 7) + 1;
const tier = (d: number): [number, number, number] =>
  d < 3.2 ? [1800, 3000, 3.0] : d < 6.5 ? [1080, 1800, 1.8] : d < 16 ? [480, 800, 0.8] : [240, 400, 0.4];

// ---------------- light ----------------
const SUN = new THREE.Vector3(0.5, 0.75, -0.4).normalize();
const tmp = new THREE.Vector3();
let LNAME = "day";
const light2D = (cam: CamInfo, mirror: boolean) => {
  const sx = SUN.dot(cam.right) * (mirror ? -1 : 1), sy = -SUN.y;
  return Math.round(Math.atan2(sy, sx) / (Math.PI / 4)) * (Math.PI / 4);
};

// ---------------- life ----------------
const LEAD = 2 / FPS;
const LID = [0.5, 1, 1, 0.5];
const lidAt = (t: number, i: number) => {
  const f = Math.round(t * FPS);
  let s = Math.round(-60 * hh(i, 9));
  for (let n = 0; s <= f && n < 400; n++) {
    const k = f - s;
    if (k >= 0 && k < 4) return LID[k];
    s += Math.round(15 + 54 * hh(i * 31 + n, 13));
  }
  return 0;
};
const fkey = (o: object) => JSON.stringify(o, (_k, v) => (typeof v === "number" ? q(v) : v));

type Army = "us" | "ca" | "jp";
type Who = { i: number; o: Outfit; okey: string };
const who = (a: Army, i: number): Who => ({ i, o: OUT[a][i % 4], okey: `${a}${i % 4}` });
/** one character drawing; side view faces screen-right unless mirrored */
const person = (cam: CamInfo, w: Who, x: number, y: number, z: number, side: boolean, mirror: boolean, fo: FrontOpts, so: SideOpts, scale = 1): Place => {
  const d = cam.pos.distanceTo(tmp.set(x, y + 1.2, z)) / scale;
  const [cw, ch, k] = tier(d);
  const m = side && mirror, light = light2D(cam, m), seed = seedOf(w.i);
  const f2: FrontOpts = { ...fo, light, seed }, s2: SideOpts = { ...so, light, seed };
  const key = side ? `S|${w.okey}|${fkey(s2)}` : `F|${w.okey}|${fkey(f2)}`;
  return { key, x, y, z, scale, mirror: m, draw: (p) => (side ? bodySide(p, w.o, s2) : bodyFront(p, w.o, f2)), size: [cw, ch, k] };
};
/** does facing world direction (dx, dz) read as screen-left (mirror the side view)? */
const mirrorFor = (cam: CamInfo, dx: number, dz: number) => dx * cam.right.x + dz * cam.right.z < 0;

const CONTACT: [number, number, number] = [0.22, 0.23, 0.33];
const TAIL: [number, number, number] = [0.42, 0.44, 0.62];
const toSrgb = (v: number) => { const c = clamp01(v); return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055; };
const hexOf = (c: [number, number, number], k: number) => "#" + c.map((v) => Math.round(255 * toSrgb(1 - (1 - v) * k)).toString(16).padStart(2, "0")).join("");
const blob = (out: Stage, x: number, y: number, z: number, sc = 1, k = 1) => {
  const hl = Math.hypot(SUN.x, SUN.z) || 1, ox = -SUN.x / hl, oz = -SUN.z / hl, rot = Math.atan2(-ox, -oz);
  if (LNAME === "day") {
    const el = Math.asin(Math.min(0.99, Math.max(0.1, SUN.y)));
    const len = Math.min(2.4, Math.max(0.5, 1.6 / Math.tan(el))) * sc, h = len + 0.55 * sc, c = 0.3 * h;
    const tc = hexOf(TAIL, k);
    out.fx.push({ key: `blob|shadow|${tc}`, cw: 128, ch: 256, draw: (p) => fxShadow(p, tc), x: x + ox * c, y: y + 0.03, z: z + oz * c, w: 0.72 * sc, h, flat: true, rot });
  }
  const cc = hexOf(CONTACT, LNAME === "fog" ? 0.7 * k : k);
  out.fx.push({ key: `blob|contact|${cc}`, cw: 128, ch: 128, draw: (p) => fxContact(p, cc), x, y: y + 0.035, z, w: 0.52 * sc, h: 0.4 * sc, flat: true, rot });
};
const gy = (x: number, z: number) => H(x, z);

// ---------------- effects helpers ----------------
const mist = (out: Stage, x: number, y: number, z: number, w: number, t: number, i: number, col = "#e6ecf2") => {
  const dx = 0.25 * Math.sin(t * 0.35 + i * 1.7);
  out.fx.push({ key: `mist${col}`, cw: 512, ch: 256, draw: (p) => fxMist(p, col), x: x + dx, y, z, w, h: w * 0.5, soft: true });
};
const boom = (out: Stage, t: number, t0: number, x: number, y: number, z: number, size: number) => {
  const u = (t - t0) / 1.1;
  if (u < 0 || u >= 1) return;
  const qu = q(u, 30);
  out.fx.push({ key: `boom${qu}`, cw: 600, ch: 600, draw: (p) => fxBoom(p, qu), x, y: y + size * 0.42, z, w: size, h: size, glow: u < 0.3 ? 1.6 : 1 });
};
/** muzzle flash at an aiming soldier's rifle tip (side view; mirror = facing screen-left) */
const flash = (out: Stage, cam: CamInfo, o: Outfit, i: number, x: number, y: number, z: number, mirror: boolean, k: number) => {
  const [tx, ty] = aimTip(o, seedOf(i), 0.6), s = mirror ? -1 : 1;
  const ox = (tx - 300) * SU * s, oy = (975 - ty) * SU;
  const L = 0.62 + 0.3 * k;
  out.fx.push({ key: `muzzle${q(k, 4)}`, cw: 300, ch: 200, draw: (p) => fxMuzzle(p, q(k, 4)), x: x + cam.right.x * (ox + s * L * 0.45), y: y + oy, z: z + cam.right.z * (ox + s * L * 0.45),
    w: L * s, h: L * 0.66, glow: 2.2 });
};
/** a shot: recoil pose 0..1 and flash strength for the 4 frames after t0 */
const fire = (t: number, t0: number) => { const n = Math.floor((t - t0) * FPS + 1e-6); return n >= 0 && n < 4 ? [1, 0.7, 0.35, 0.15][n] : 0; };

// ---------------- shots ----------------
const [FX, FZ] = FIELD;
/** soldiers standing in the fog field (hook) / packed crowd (shot 11) */
const fieldCrowd = (cam: CamInfo, t: number, out: Stage, n: number, R: number, tight: boolean) => {
  const after = t > 117 / FPS - LEAD;
  for (let i = 0; i < n; i++) {
    let x: number, z: number;
    if (!tight && i < 2) { x = FX + 0.1 + (i ? 0.62 : -0.55); z = FZ - 3.6 + (i ? 0.15 : 0); }
    else { const a = hh(i, 1) * Math.PI * 2, r = R * Math.sqrt(hh(i, 2)); x = FX + r * Math.cos(a); z = FZ + 1 + r * Math.sin(a) * 1.3; }
    const y = gy(x, z), a: Army = i % 2 ? "ca" : "us", w = who(a, i);
    const kind = tight ? i % 3 : i < 2 ? 0 : i % 4 === 1 ? 1 : i % 4 === 3 ? 2 : 0;
    let expr: Expr = tight ? (["nervous", "shock", "dazed"] as Expr[])[i % 3] : after ? (i % 3 === 0 ? "shock" : "nervous") : "stern";
    const look = Math.round(Math.sin(t * 1.3 + i * 2.1) * 1.2);
    if (kind === 0) {
      out.places.push(person(cam, w, x, y, z, false, false, { mode: "stand", expr, look: Math.max(-1, Math.min(1, look)), blink: lidAt(t, i), facing: (i % 3 - 1) as -1 | 0 | 1 }, {}));
    } else {
      const dirx = kind === 1 ? 1 : -1, m = mirrorFor(cam, dirx * -cam.right.z || dirx, dirx * cam.right.x);
      out.places.push(person(cam, w, x, y, z, true, kind === 2, {}, { mode: "aim", expr, blink: lidAt(t, i), pose: 0 }));
      void m;
    }
    blob(out, x, y, z);
  }
};

const stage1 = (cam: CamInfo, t: number, out: Stage) => {
  fieldCrowd(cam, t, out, 14, 6.5, false);
  for (let i = 0; i < 9; i++) mist(out, FX - 7 + (i % 5) * 3.6, gy(FX, FZ) + 0.35, FZ - 5 + Math.floor(i / 5) * 5 + hh(i, 4) * 2, 6, t, i);
};
const stage2 = (cam: CamInfo, t: number, out: Stage) => {
  if (t < 244 / FPS - 0.3) return;
  for (let i = 0; i < 6; i++) {
    const x = CAMP[0] - 3 + (i % 3) * 2.2 + (hh(i) - 0.5) * 0.6, z = CAMP[2] - 4.5 + Math.floor(i / 3) * 2.4 + hh(i, 2) * 0.5;
    const shiver = 0.012 * Math.sin(t * 47 + i * 3);
    out.places.push(person(cam, who("jp", i + 20), x + shiver, gy(x, z), z, false, false, { mode: "stand", expr: i % 2 ? "nervous" : "stern", blink: lidAt(t, i + 20), facing: 0 }, {}));
    blob(out, x, gy(x, z), z);
  }
};
const stage3 = (cam: CamInfo, t: number, out: Stage) => {
  if (t < 425 / FPS - 0.3) return;
  const t0 = 425 / FPS;
  for (let i = 0; i < 14; i++) {
    const z = -61 + (i >> 1) * 1.4 - 1.4 * (t - t0), x = PIER_X + (i % 2 ? 0.55 : -0.55);
    if (z < PIER_END + 1) continue;
    const ph = q((((t - t0) * 1.0 + (i % 2) * 0.5) % 1 + 1) % 1, 60);
    out.places.push(person(cam, who("jp", i + 30), x, 1.45, z, true, mirrorFor(cam, 0, -1), {}, { mode: "march", phase: ph, expr: i % 3 ? "neutral" : "nervous", blink: lidAt(t, i + 30), stomp: 0.7, stride: 0.9 }));
    blob(out, x, 1.45, z);
  }
  for (let i = 0; i < 5; i++) mist(out, PIER_X + 2 - i * 1.5, 1.2, -52 - i * 6, 7, t, i);
};
const stage4 = (cam: CamInfo, t: number, out: Stage) => {
  const x = USS[0] + 17, z = USS[2] + 4.5;
  out.places.push(person(cam, { i: 50, o: SAILOR, okey: "sailor" }, x, 4.02, z, false, false, { mode: "stand", expr: "neutral", prop: "binoc", blink: 0 }, {}));
  blob(out, x, 4.02, z);
  for (let i = 0; i < 4; i++) mist(out, x - 6 + i * 4, 4.6 + (i % 2) * 1.2, z - 6 - i * 2, 9, t, i);
};
export const BOOMS: [number, number, number][] = [[602, CAMP[0] - 20, CAMP[2] + 22], [614, CAMP[0] + 18, CAMP[2] + 34], [627, CAMP[0] - 30, CAMP[2] + 4], [640, CAMP[0] + 30, CAMP[2] + 22]];
const stage5 = (cam: CamInfo, t: number, out: Stage) => {
  for (const [f0, x, z] of BOOMS) {
    // bomb falls for 0.9 s before it lands
    const u = (t - (f0 / FPS - 0.9)) / 0.9;
    if (u >= 0 && u < 1) out.fx.push({ key: "bomb", cw: 200, ch: 100, draw: fxBomb, x, y: gy(x, z) + 45 * (1 - u * u), z, w: 1.6, h: 0.8, rot: -Math.PI / 2 });
    boom(out, t, f0 / FPS, x, gy(x, z), z, 16);
    const s = (t - f0 / FPS - 0.6) / 4;
    if (s > 0 && s < 1) out.fx.push({ key: "smoke#7a7680", cw: 512, ch: 256, draw: (p) => fxMist(p, "#7a7680"), x, y: gy(x, z) + 8 + 10 * s, z, w: 18 + 10 * s, h: 9 + 5 * s, soft: true });
  }
};
const stage6 = (cam: CamInfo, t: number, out: Stage) => {
  const hero = t > 763 / FPS - 0.2;
  const t0 = 651 / FPS;
  for (let i = 0; i < 30; i++) {
    const craft = [38, 50, 62][i % 3], start = t0 - 1.2 + (i / 3) * 0.32, run = t - start;
    if (run < 0) continue;
    let x = craft + (hh(i) - 0.5) * 3.2, z = BZ - 2.8 + run * 3.0;
    // up the beach, then peel off to the sides before they reach the lens
    if (z > BZ + 6.5) { const side = x >= BEACH_X + 2.5 ? 1 : -1; x += side * (z - (BZ + 6.5)) * 1.2; z = BZ + 6.5; }
    if (Math.abs(x - BEACH_X) > 16) continue;
    if (hero && Math.abs(x - BEACH_X) < 1.6 && Math.abs(z - (BZ + 11.5)) < 4) x += 2.4 * Math.sign(x - BEACH_X || 1);
    const ph = q(((run * 1.5 + hh(i, 2)) % 1 + 1) % 1, 60), y = Math.max(0.05, gy(x, z));
    out.places.push(person(cam, who(i % 2 ? "ca" : "us", i), x, y, z, false, false, { mode: "march", phase: ph, expr: i % 3 ? "stern" : "grin", lift: 70, blink: lidAt(t, i) }, {}));
    if (y > 0.06) blob(out, x, y, z);
  }
  if (hero) {
    const x = BEACH_X, z = BZ + 11.5, y = gy(x, z);
    out.places.push(person(cam, who("us", 1), x, y, z, false, false, { mode: "stand", expr: "stern", blink: lidAt(t, 60), facing: 0 }, {}));
    blob(out, x, y, z);
  }
  for (let i = 0; i < 6; i++) mist(out, BEACH_X - 12 + i * 5, 0.6, BZ - 5 - hh(i, 5) * 4, 8, t, i);
};
const stage7 = (cam: CamInfo, t: number, out: Stage) => {
  const [x, z] = P7, y = gy(x, z), down = t > 855 / FPS;
  out.places.push(person(cam, who("us", 3), x, y, z, false, false, { mode: "stand", expr: down ? "nervous" : "stern", look: 0, headTilt: down ? 6 : 0, blink: lidAt(t, 3) }, {}));
  // ground mist swallows the boots
  for (let i = 0; i < 5; i++) mist(out, x - 1.2 + i * 0.6, y + 0.18 + (i % 2) * 0.1, z - 0.35 - (i % 3) * 0.3, 1.8 + (i % 2), t, i);
  for (let i = 0; i < 6; i++) mist(out, x - 6 + i * 2.5, y + 0.5, z + 2 + (i % 3) * 2, 5, t, i + 5);
};
const stage8 = (cam: CamInfo, t: number, out: Stage) => {
  const second = t >= 955 / FPS;
  const [x, z] = second ? P8b : P8a, y = gy(x, z), i = second ? 7 : 2, w = who(second ? "ca" : "us", i), mirror = second;
  const tHear = 913 / FPS - LEAD, tAim = second ? 962 / FPS : 926 / FPS, tShot = second ? 985 / FPS : 940 / FPS;
  const k = fire(t, tShot);
  const expr: Expr = second ? (t < tShot ? "stern" : "shock") : t < tHear ? "neutral" : "shock";
  if (t < tAim) out.places.push(person(cam, w, x, y, z, false, false, { mode: "stand", expr, look: second ? 0 : t > tHear ? 1 : 0, blink: lidAt(t, i), facing: t > tHear && !second ? 1 : 0 }, {}));
  else {
    out.places.push(person(cam, w, x, y, z, true, mirror, {}, { mode: "aim", expr, blink: 0, pose: q(k, 4) }));
    if (k > 0) flash(out, cam, w.o, i, x, y, z, mirror, k);
  }
  blob(out, x, y, z);
  for (let j = 0; j < 6; j++) mist(out, x - 5 + j * 2, y + 0.3 + (j % 2) * 0.4, z + 1.5 + (j % 3) * 1.6, 4, t, j);
};
/** two groups on two low ridges trading fire all night; then the two soldiers who meet */
const stage9 = (cam: CamInfo, t: number, out: Stage) => {
  if (t < 1075 / FPS) {
    for (let i = 0; i < 12; i++) {
      const left = i < 6, x = left ? 52 + (i % 3) * 1.2 : 59.6 + (i % 3) * 1.2, z = 24 + Math.floor((i % 6) / 3) * 2.5 + hh(i) * 0.8, y = gy(x, z);
      const dir = left ? 1 : -1, m = mirrorFor(cam, dir, 0), w = who(left ? "us" : "ca", i);
      const period = 0.9 + hh(i, 3) * 0.8, ph = (t + hh(i, 4) * 3) % period, k = ph < 4 / FPS ? [1, 0.7, 0.35, 0.15][Math.floor(ph * FPS)] : 0;
      out.places.push(person(cam, w, x, y, z, true, m, {}, { mode: "aim", expr: "stern", blink: 0, pose: q(k, 4) }));
      if (k > 0) flash(out, cam, w.o, i, x, y, z, m, k);
      if (ph < 0.25) { // tracer crossing the gap
        const u = ph / 0.25, tx = left ? x + 1.5 + u * 6 : x - 1.5 - u * 6;
        out.fx.push({ key: "tracer", cw: 400, ch: 40, draw: fxTracer, x: tx, y: y + 1.4, z, w: 1.6 * (left ? -1 : 1), h: 0.12, glow: 2.5 });
      }
    }
    for (let j = 0; j < 6; j++) mist(out, 47 + j * 4, gy(57, 22) + 1.4, 21 + (j % 3) * 3, 7, t, j, "#33416a");
    return;
  }
  const same = t > 1102 / FPS - LEAD;
  for (const [x, a, dir, i] of [[56.15, "us", 1, 1], [57.85, "ca", -1, 2]] as const) {
    const z = 30, y = gy(x, z), m = mirrorFor(cam, dir, 0), w = who(a, i);
    const k = !same ? fire(t, (1080 + i * 7) / FPS) + fire(t, (1092 + i * 4) / FPS) : 0;
    out.places.push(person(cam, w, x, y, z, true, m, {}, { mode: "aim", expr: same ? "shock" : "stern", blink: 0, pose: q(Math.min(1, k), 4) }));
    if (k > 0) flash(out, cam, w.o, i, x, y, z, m, Math.min(1, k));
    blob(out, x, y, z);
  }
  for (let j = 0; j < 5; j++) mist(out, 53 + j * 2, gy(57, 31) + 0.3, 31.5 + (j % 2), 4, t, j, "#3c4a70");
};
const stage11 = (cam: CamInfo, t: number, out: Stage) => {
  fieldCrowd(cam, t, out, 22, 3.6, true);
  for (let i = 0; i < 8; i++) mist(out, FX - 6 + (i % 4) * 4, gy(FX, FZ) + 0.3, FZ - 3 + Math.floor(i / 4) * 5, 6, t, i);
};
const stage12 = (cam: CamInfo, t: number, out: Stage) => {
  if (t < 1296 / FPS) {
    const [x, z] = P12, y = gy(x, z);
    out.places.push(person(cam, who("ca", 5), x, y, z, false, false, { mode: "stand", expr: "nervous", blink: 0.55, look: Math.round(Math.sin(t * 2)) }, {}));
  } else for (let i = 0; i < 6; i++) mist(out, P12[0] - 8 + i * 3.4, gy(P12[0], P12[1] + 8) + 0.6, P12[1] + 5 + (i % 3) * 4, 7, t, i);
};
const stage13 = (cam: CamInfo, t: number, out: Stage) => {
  const R = ROOM, scared = t > 1394 / FPS - LEAD;
  out.places.push(person(cam, { i: 70, o: PJKID, okey: "kid" }, R[0] - 3.05, 0.05, R[2] - 1.2, false, false, { mode: "stand", expr: scared ? "shock" : "neutral", blink: scared ? 0 : lidAt(t, 70) }, {}, 0.72));
  coat(out);
};
const coat = (out: Stage) => out.places.push({ key: "coat", x: ROOM[0] + 1.4, y: 0.22, z: ROOM[2] + 2.93, yaw: Math.PI, draw: (p) => coatOnHook(p), size: [1080, 1800, 1.8] });
const stage14 = (cam: CamInfo, t: number, out: Stage) => {
  const R = ROOM;
  coat(out);
  const men: [number, number, Army, number, number][] = [[-0.9, 1.2, "us", 1, 0], [0.9, -0.2, "ca", -1, 0.4], [-1.6, -1.0, "us", 1, -0.6], [1.7, 1.0, "ca", -1, 0.8]];
  men.forEach(([dx, dz, a, dir, dzd], i) => {
    const x = R[0] + dx, z = R[2] + dz, m = mirrorFor(cam, dir, dzd);
    out.places.push(person(cam, who(a, i + 80), x, 0.05, z, true, m, {}, { mode: "aim", expr: i % 2 ? "shock" : "nervous", blink: lidAt(t, i + 80) }));
    blob(out, x, 0.05, z);
  });
};
const stage15 = (cam: CamInfo, t: number, out: Stage) => {
  if (t < 1556 / FPS) {
    const tb = 1546 / FPS;
    for (let i = 0; i < 5; i++) {
      const x = 52 + i * 1.5 + 0.9 * Math.min(t - 1505 / FPS, tb - 1505 / FPS), z = -4 + (i % 2) * 1.2, y = gy(x, z);
      const hit = t > tb && i >= 1 && i <= 3;
      if (!hit) out.places.push(person(cam, who(i % 2 ? "ca" : "us", i + 90), x, y, z, true, mirrorFor(cam, 1, 0), {}, { mode: "march", phase: q((t * 0.9 + i * 0.3) % 1, 60), expr: t > tb ? "shock" : "stern", stomp: 0.6, blink: lidAt(t, i) }));
      else {
        const u = clamp01((t - tb) / 0.3);
        out.places.push(person(cam, who(i % 2 ? "ca" : "us", i + 90), x + (i - 2) * 0.6 * u, y + 0.5 * Math.sin(Math.PI * u), z, false, false, { mode: u < 1 ? "fall" : "sit", expr: u < 1 ? "shock" : "dazed", tilt: (i - 2) * 30 * u }, {}));
      }
      blob(out, x, y, z);
    }
    boom(out, t, tb, 55, gy(55, -3), -3, 4.5);
    for (let j = 0; j < 5; j++) mist(out, 50 + j * 3, gy(55, 0) + 0.4, 0 + (j % 2) * 3, 6, t, j);
    return;
  }
  if (t < 1606 / FPS) {
    const tm = 1589 / FPS, u = (t - tm) / 1.4;
    if (u >= 0 && u < 1) {
      const qu = q(u, 30);
      out.fx.push({ key: `splash${qu}`, cw: 800, ch: 800, draw: (p) => fxSplash(p, qu), x: USS[0] - 12, y: 14, z: USS[2] + 6.5, w: 36, h: 36 });
    }
    boom(out, t, tm, USS[0] - 12, 2, USS[2] + 6.5, 14);
    return;
  }
  const zs = shoreZ(WOUNDED_X);
  for (let i = 0; i < 9; i++) {
    const x = WOUNDED_X - 4 + (i % 3) * 2.6 + hh(i) * 0.8, z = zs + 14 + Math.floor(i / 3) * 2.4 + hh(i, 2), y = gy(x, z);
    out.places.push(person(cam, who(i % 2 ? "ca" : "us", i + 100), x, y, z, false, false, { mode: "sit", expr: (["pained", "dazed", "neutral"] as Expr[])[i % 3], blink: lidAt(t, i + 100) }, {}));
    blob(out, x, y, z, 1.05, 0.8);
  }
};
const dogs: { dx: number; dz: number; d: Omit<DogOpts, "wag" | "expr" | "lid"> }[] = [
  { dx: -0.1, dz: 0, d: { coat: "#f2ede2", patch: "#9a6a3c", ear: "#8a5a32", cap: true } }, // Explosion
  { dx: -0.7, dz: -0.9, d: { coat: "#3a3030", ear: "#2a2222" } },
  { dx: -0.4, dz: 1.0, d: { coat: "#c88a4a", ear: "#9a5a2a" } },
  { dx: -1.0, dz: 1.9, d: { coat: "#e8dcc4", patch: "#3a3030", ear: "#3a3030" } },
];
const stageDogs = (cam: CamInfo, t: number, out: Stage, id: number) => {
  dogs.forEach((g, i) => {
    const x = LANE_X + g.dx, z = DOGS_Z + g.dz, y = gy(x, z);
    const wag = q(0.5 + 0.5 * Math.sin(t * (9 + i * 1.3) + i), 12), lid = lidAt(t, i + 120);
    const tilt = id === 17 && i === 0 ? 14 * smooth((t - 1906 / FPS) / 0.25) : 0;
    const d: DogOpts = { ...g.d, wag, expr: i === 0 ? (tilt > 7 ? "happy" : "pant") : i % 2 ? "happy" : "pant", lid, tilt: q(tilt, 2) };
    const dist = cam.pos.distanceTo(tmp.set(x, y + 0.4, z));
    const [cw, ch, k] = tier(dist / 0.45);
    out.places.push({ key: `dog${i}|${fkey(d)}`, x, y, z, scale: 0.45, draw: (p) => dogSit(p, d), size: [cw, ch, k] });
    blob(out, x, y, z, 0.6);
  });
};
const stage16 = (cam: CamInfo, t: number, out: Stage) => {
  if (t < 1748 / FPS) {
    const t0 = 1685 / FPS;
    for (let i = 0; i < 7; i++) {
      const x = LANE_X + (i % 3 - 1) * 1.5 + hh(i) * 0.4, z = 7 + (t - t0) * 0.9 - Math.floor(i / 3) * 1.8, y = gy(x, z);
      out.places.push(person(cam, who(i % 2 ? "ca" : "us", i + 110), x, y, z, false, false, { mode: "stroll", phase: q(((t - t0) * 0.65 + hh(i, 2)) % 1, 60), expr: i % 3 ? "stern" : "nervous", look: Math.round(Math.sin(t + i * 2)), blink: lidAt(t, i + 110) }, {}));
      blob(out, x, y, z);
    }
    return;
  }
  const seen = t > 1813 / FPS - LEAD;
  for (let i = 0; i < 4; i++) {
    const x = LANE_X - 0.6 - i * 0.9, z = DOGS_Z + 3.0 + (i % 3) * 0.6, y = gy(x, z);
    out.places.push(person(cam, who(i % 2 ? "ca" : "us", i + 110), x, y, z, true, mirrorFor(cam, 0, -1), {}, { mode: "aim", expr: seen ? (i % 2 ? "dazed" : "shock") : "stern", blink: lidAt(t, i + 110) }));
    blob(out, x, y, z);
  }
  stageDogs(cam, t, out, 16);
};

/** everything with a face in shot `id` at time t */
export const stage = (id: number, t: number, cam: CamInfo, sun: THREE.Vector3): Stage => {
  const out: Stage = { places: [], fx: [] };
  LNAME = SHOTS[id - 1].light;
  SUN.copy(sun);
  switch (id) {
    case 1: stage1(cam, t, out); break;
    case 2: stage2(cam, t, out); break;
    case 3: stage3(cam, t, out); break;
    case 4: stage4(cam, t, out); break;
    case 5: stage5(cam, t, out); break;
    case 6: stage6(cam, t, out); break;
    case 7: stage7(cam, t, out); break;
    case 8: stage8(cam, t, out); break;
    case 9: stage9(cam, t, out); break;
    case 11: stage11(cam, t, out); break;
    case 12: stage12(cam, t, out); break;
    case 13: stage13(cam, t, out); break;
    case 14: stage14(cam, t, out); break;
    case 15: stage15(cam, t, out); break;
    case 16: stage16(cam, t, out); break;
    case 17: stageDogs(cam, t, out, 17); break;
  }
  return out;
};
export { FPS, P };
