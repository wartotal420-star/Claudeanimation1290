// WW2 long-form: the set library. Each set is built once into its own group at a far-apart origin (world.ts) and only
// shown while its shot plays. Everything is our own simple geometry with painted canvas textures and two-tone shading;
// lamps/windows/candles are HDR emissive (bloom) so every scene has a motivated light source.
import * as THREE from "three";
import { Batch, boxGeo, V } from "./build";
import { ctex, rng } from "./paint";
import { twoTone } from "./shade";
import { NOINK } from "./ink";

export type SetName = "void" | "front" | "jungle" | "warroom" | "paris" | "press" | "bakery" | "playroom" | "street" | "wallst" | "atelier" | "beerhall";
export const SET_NAMES: SetName[] = ["void", "front", "jungle", "warroom", "paris", "press", "bakery", "playroom", "street", "wallst", "atelier", "beerhall"];
/** world origin of each set (x, 0, 0) */
export const setOrigin = (n: SetName): [number, number, number] => [SET_NAMES.indexOf(n) * 600, 0, 0];

// ---------------- materials ----------------
const mats = new Map<string, THREE.Material>();
const L = (key: string, p: () => THREE.MeshLambertMaterialParameters) => {
  let m = mats.get(key);
  if (!m) { m = twoTone(new THREE.MeshLambertMaterial(p())); mats.set(key, m); }
  return m;
};
const C = (hex: string) => L("c" + hex, () => ({ color: hex }));
const T = (key: string, tex: () => THREE.Texture, rx = 1, ry = 1, color = "#ffffff") => L("t" + key + rx + ry + color, () => {
  const t = tex().clone(); t.repeat.set(rx, ry); t.needsUpdate = true; return { map: t, color };
});
/** HDR glow (lamps, windows, candles, fire): unlit, bloomed, no ink */
const GLOW = (r: number, g: number, b: number) => {
  const k = `g${r},${g},${b}`;
  let m = mats.get(k);
  if (!m) { m = new THREE.MeshBasicMaterial({ color: new THREE.Color(r, g, b), fog: false }); mats.set(k, m); }
  return m;
};
const WARM = () => GLOW(3.2, 2.2, 1.1), CANDLE = () => GLOW(4, 2.6, 1.2), COOLW = () => GLOW(1.4, 1.7, 2.4);

// ---------------- painted textures ----------------
const tx = (key: string, w: number, h: number, draw: (g: CanvasRenderingContext2D, r: () => number) => void) => () => ctex("ww2_" + key, w, h, draw);
export const wallpaper = (base: string, pat: string) => tx("wp" + base + pat, 256, 256, (g) => {
  g.fillStyle = base; g.fillRect(0, 0, 256, 256);
  g.fillStyle = pat;
  for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) { const cx = x * 64 + (y % 2) * 32 + 16, cy = y * 64 + 32; g.beginPath(); g.ellipse(cx, cy, 9, 15, 0, 0, 7); g.fill(); g.fillRect(cx - 1.5, cy - 26, 3, 52); }
  for (let x = 0; x < 256; x += 64) { g.fillStyle = "rgba(0,0,0,.08)"; g.fillRect(x, 0, 3, 256); }
});
export const parquet = (a: string, b: string) => tx("pq" + a + b, 256, 256, (g, r) => {
  for (let y = 0; y < 8; y++) for (let x = 0; x < 4; x++) {
    g.fillStyle = (x + y) % 2 ? a : b; g.fillRect(x * 64, y * 32, 64, 32);
    g.fillStyle = `rgba(0,0,0,${0.05 + r() * 0.08})`; g.fillRect(x * 64, y * 32, 64, 32);
    g.fillStyle = "rgba(30,15,10,.7)"; g.fillRect(x * 64, y * 32, 64, 2); g.fillRect(x * 64, y * 32, 2, 32);
  }
});
export const planksTex = (a: string) => tx("pl" + a, 256, 256, (g, r) => {
  for (let y = 0; y < 8; y++) { g.fillStyle = a; g.fillRect(0, y * 32, 256, 32); g.fillStyle = `rgba(0,0,0,${r() * 0.18})`; g.fillRect(0, y * 32, 256, 32);
    g.fillStyle = "rgba(25,12,8,.8)"; g.fillRect(0, y * 32 + 30, 256, 2); g.fillRect(((y * 97) % 256), y * 32, 2, 32); }
});
export const brickTex = (a: string) => tx("br" + a, 256, 256, (g, r) => {
  g.fillStyle = "#5a4a40"; g.fillRect(0, 0, 256, 256);
  for (let y = 0; y < 16; y++) for (let x = -1; x < 5; x++) {
    const c = new THREE.Color(a).offsetHSL(0, 0, (r() - 0.5) * 0.08);
    g.fillStyle = "#" + c.getHexString(); g.fillRect(x * 64 + (y % 2) * 32 + 2, y * 16 + 2, 60, 12);
  }
});
export const cobbleTex = tx("cobble", 256, 256, (g, r) => {
  g.fillStyle = "#4a4650"; g.fillRect(0, 0, 256, 256);
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) {
    g.fillStyle = ["#8b8794", "#7d7988", "#9894a0", "#85808c"][Math.floor(r() * 4)];
    g.beginPath(); g.ellipse(x * 32 + 16 + (y % 2) * 16, y * 32 + 16, 13, 12, r(), 0, 7); g.fill();
  }
});
export const carpetTex = (a: string, b: string) => tx("cp" + a + b, 256, 256, (g) => {
  g.fillStyle = a; g.fillRect(0, 0, 256, 256);
  g.strokeStyle = b; g.lineWidth = 10; g.strokeRect(14, 14, 228, 228);
  g.lineWidth = 3; g.strokeRect(34, 34, 188, 188);
  g.fillStyle = b; for (let k = 0; k < 4; k++) { g.beginPath(); g.ellipse(128, 128, 40 - k * 8, 22 - k * 4, (k * Math.PI) / 4, 0, 7); g.fill(); }
});
export const mapTex = tx("worldmap", 1024, 512, (g, r) => {
  g.fillStyle = "#2f5f86"; g.fillRect(0, 0, 1024, 512);
  for (let y = 0; y < 512; y += 32) { g.fillStyle = "rgba(255,255,255,.06)"; g.fillRect(0, y, 1024, 1); }
  for (let x = 0; x < 1024; x += 32) { g.fillStyle = "rgba(255,255,255,.06)"; g.fillRect(x, 0, 1, 512); }
  const land = (pts: [number, number][], col: string) => { g.fillStyle = col; g.strokeStyle = "#4a3a2a"; g.lineWidth = 3; g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath(); g.fill(); g.stroke(); };
  land([[90, 90], [250, 70], [330, 120], [300, 190], [250, 250], [210, 300], [170, 240], [120, 180]], "#d9c48e"); // N America
  land([[230, 300], [300, 300], [320, 360], [290, 450], [255, 470], [240, 380]], "#c8b47c"); // S America
  land([[470, 90], [560, 70], [600, 110], [560, 150], [500, 160], [470, 130]], "#e3cf98"); // Europe
  land([[480, 170], [580, 170], [600, 250], [570, 340], [520, 380], [480, 300], [460, 220]], "#cdb780"); // Africa
  land([[600, 70], [860, 60], [900, 140], [820, 220], [740, 250], [660, 230], [600, 160]], "#d6c08a"); // Asia
  land([[820, 340], [900, 330], [920, 390], [860, 420], [820, 390]], "#c9b37b"); // Australia
  land([[880, 140], [900, 150], [895, 190], [880, 180]], "#e0cc94"); // Japan
  for (let i = 0; i < 40; i++) { g.fillStyle = "rgba(70,50,30,.35)"; g.beginPath(); g.arc(470 + r() * 450, 80 + r() * 300, 2, 0, 7); g.fill(); }
});
export const paintingTex = (seed: number) => tx("paint" + seed, 256, 192, (g, r0) => {
  const r = rng(seed * 7 + 3);
  const sky = ["#9cc4e8", "#f2c28c", "#b8a0d0", "#9fd0c0"][seed % 4];
  g.fillStyle = sky; g.fillRect(0, 0, 256, 192);
  g.fillStyle = ["#6a9a4a", "#8a6a4a", "#4a7a6a", "#9a8a5a"][seed % 4]; g.beginPath(); g.moveTo(0, 130); for (let x = 0; x <= 256; x += 32) g.lineTo(x, 110 + r() * 40); g.lineTo(256, 192); g.lineTo(0, 192); g.fill();
  g.fillStyle = "#f6e9c4"; g.fillRect(90 + r() * 60, 80, 40, 50); g.fillStyle = "#b8463c"; g.beginPath(); g.moveTo(85 + 0, 80); g.lineTo(150, 80); g.lineTo(118, 55); g.fill();
  void r0;
});
export const posterTex = (seed: number) => tx("poster" + seed, 128, 192, (g) => {
  const cols = [["#c8323a", "#f2e6c8"], ["#2a4a7a", "#f2c84a"], ["#3a6a3a", "#f2e6c8"], ["#f2c84a", "#2a2630"]][seed % 4];
  g.fillStyle = cols[1]; g.fillRect(0, 0, 128, 192);
  g.fillStyle = cols[0]; g.fillRect(8, 8, 112, 110);
  g.fillStyle = cols[1]; g.beginPath(); g.arc(64, 60, 28, 0, 7); g.fill();
  for (let k = 0; k < 4; k++) { g.fillStyle = cols[0]; g.fillRect(16, 128 + k * 14, 96 - (k % 2) * 30, 7); }
});
export const booksTex = tx("books", 256, 128, (g, r) => {
  g.fillStyle = "#3a2618"; g.fillRect(0, 0, 256, 128);
  let x = 4;
  while (x < 250) { const w = 8 + r() * 12, h = 70 + r() * 50; g.fillStyle = ["#7a2a2a", "#2a4a6a", "#3a5a2a", "#8a6a2a", "#5a3a5a", "#c8b48a"][Math.floor(r() * 6)]; g.fillRect(x, 128 - h, w, h); g.fillStyle = "rgba(255,230,160,.5)"; g.fillRect(x + 2, 128 - h + 10, w - 4, 3); x += w + 1; }
});
export const facadeTex = (wall: string, night: boolean) => tx("fac" + wall + night, 512, 512, (g, r) => {
  g.fillStyle = wall; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 300; i++) { g.fillStyle = `rgba(0,0,0,${r() * 0.06})`; g.fillRect(r() * 512, r() * 512, 20, 8); }
  g.fillStyle = "rgba(0,0,0,.25)"; g.fillRect(0, 160, 512, 8); g.fillRect(0, 330, 512, 8);
  for (let fl = 0; fl < 3; fl++) for (let k = 0; k < 3; k++) {
    const x = 50 + k * 160, y = 20 + fl * 170;
    g.fillStyle = "#3a2a24"; g.fillRect(x - 6, y - 6, 92, 122);
    const lit = night ? r() < 0.75 : false;
    g.fillStyle = lit ? "#ffd27a" : "#5a7a9a"; g.fillRect(x, y, 80, 110);
    g.fillStyle = lit ? "#ffb04a" : "#7a9aba"; g.fillRect(x, y, 80, 30);
    g.fillStyle = "#3a2a24"; g.fillRect(x + 38, y, 4, 110); g.fillRect(x, y + 50, 80, 4);
    g.fillStyle = ["#7a3a2a", "#2a5a4a", "#4a4a7a"][k % 3]; g.fillRect(x - 22, y, 14, 110); g.fillRect(x + 88, y, 14, 110);
  }
});
export const shopfrontTex = (name: number, night: boolean) => tx("shop" + name + night, 512, 256, (g) => {
  g.fillStyle = ["#7a2a2a", "#2a4a3a", "#2a3a5a"][name % 3]; g.fillRect(0, 0, 512, 256);
  g.fillStyle = "#f2e2b2"; g.fillRect(40, 18, 432, 40);
  g.fillStyle = "#3a2618"; for (let k = 0; k < 8; k++) g.fillRect(70 + k * 48, 28, 30, 20);
  g.fillStyle = night ? "#ffcf78" : "#88a8c8"; g.fillRect(40, 80, 280, 160); g.fillStyle = "#3a2618"; g.fillRect(360, 80, 110, 176);
  g.fillStyle = night ? "#ffe2a8" : "#a8c8e0"; g.fillRect(60, 100, 240, 20);
});
export const chartBoardTex = tx("chartboard", 512, 320, (g) => {
  g.fillStyle = "#1c2a24"; g.fillRect(0, 0, 512, 320);
  g.strokeStyle = "rgba(200,230,210,.25)"; g.lineWidth = 2;
  for (let x = 40; x < 512; x += 52) { g.beginPath(); g.moveTo(x, 20); g.lineTo(x, 300); g.stroke(); }
  for (let y = 40; y < 320; y += 40) { g.beginPath(); g.moveTo(20, y); g.lineTo(500, y); g.stroke(); }
});
export const signTex = (text: string, bg: string, fg: string, w = 512, h = 128) => tx("sign" + text + bg, w, h, (g) => {
  g.fillStyle = bg; g.fillRect(0, 0, w, h); g.strokeStyle = fg; g.lineWidth = 8; g.strokeRect(8, 8, w - 16, h - 16);
  g.fillStyle = fg; g.font = `bold ${Math.round(h * 0.5)}px Georgia, serif`; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(text, w / 2, h / 2 + 4);
});
const leafTex = tx("leaves", 256, 256, (g, r) => {
  g.fillStyle = "#2f6a32"; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 120; i++) { g.fillStyle = ["#3f8a3a", "#2a5a2a", "#5aa04a", "#24502a"][Math.floor(r() * 4)]; g.beginPath(); g.ellipse(r() * 256, r() * 256, 14 + r() * 18, 6 + r() * 6, r() * 3, 0, 7); g.fill(); }
});

// ---------------- props ----------------
type P3 = [number, number, number];
const M4 = (x: number, y: number, z: number, yaw = 0, sx = 1, sy = sx, sz = sx) => new THREE.Matrix4().compose(V(x, y, z), new THREE.Quaternion().setFromAxisAngle(V(0, 1, 0), yaw), V(sx, sy, sz));
const box = (b: Batch, m: THREE.Material, x0: number, y0: number, z0: number, x1: number, y1: number, z1: number, tile = 0) => b.add(boxGeo(V(x0, y0, z0), V(x1, y1, z1), tile), m);
const cyl = (b: Batch, m: THREE.Material, x: number, y: number, z: number, r: number, h: number, r2 = r, seg = 14) => b.add(new THREE.CylinderGeometry(r2, r, h, seg).translate(x, y + h / 2, z), m);
const sph = (b: Batch, m: THREE.Material, x: number, y: number, z: number, r: number, sy = 1) => b.add(new THREE.SphereGeometry(r, 14, 10).scale(1, sy, 1).translate(x, y, z), m);
const plane = (g: THREE.Group, m: THREE.Material, x: number, y: number, z: number, w: number, h: number, yaw = 0, noink = false) => {
  const o = new THREE.Mesh(new THREE.PlaneGeometry(w, h), m); o.position.set(x, y, z); o.rotation.y = yaw; if (noink) o.layers.set(NOINK); o.receiveShadow = true; g.add(o); return o;
};
const glowSph = (g: THREE.Group, m: THREE.Material, x: number, y: number, z: number, r: number) => { const o = new THREE.Mesh(new THREE.SphereGeometry(r, 12, 8), m); o.position.set(x, y, z); o.layers.set(NOINK); g.add(o); };

export const table = (b: Batch, x: number, z: number, w: number, d: number, h = 0.78, top = C("#6a4228"), leg = C("#4a2c1a"), yaw = 0) => {
  const T0 = M4(x, 0, z, yaw);
  b.add(boxGeo(V(-w / 2, h - 0.06, -d / 2), V(w / 2, h, d / 2)), top, T0);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) b.add(boxGeo(V(sx * (w / 2 - 0.08) - 0.04, 0, sz * (d / 2 - 0.08) - 0.04), V(sx * (w / 2 - 0.08) + 0.04, h - 0.06, sz * (d / 2 - 0.08) + 0.04)), leg, T0);
};
export const chair = (b: Batch, x: number, z: number, yaw = 0, m = C("#5a3420")) => {
  const T0 = M4(x, 0, z, yaw);
  b.add(boxGeo(V(-0.22, 0.44, -0.22), V(0.22, 0.49, 0.22)), m, T0);
  b.add(boxGeo(V(-0.22, 0.49, 0.18), V(0.22, 1.0, 0.22)), m, T0);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) b.add(boxGeo(V(sx * 0.18 - 0.025, 0, sz * 0.18 - 0.025), V(sx * 0.18 + 0.025, 0.44, sz * 0.18 + 0.025)), m, T0);
};
/** table lamp: base, stem, shade, glowing bulb */
export const lamp = (b: Batch, g: THREE.Group, x: number, y: number, z: number, shade = "#2f6a4a") => {
  cyl(b, C("#b08a3a"), x, y, z, 0.09, 0.03); cyl(b, C("#b08a3a"), x, y, z, 0.015, 0.32);
  b.add(new THREE.CylinderGeometry(0.1, 0.16, 0.14, 14, 1, true).translate(x, y + 0.36, z), L("lampshade" + shade, () => ({ color: shade, side: THREE.DoubleSide })));
  glowSph(g, WARM(), x, y + 0.31, z, 0.045);
};
export const hangingLamp = (b: Batch, g: THREE.Group, x: number, y: number, z: number, top = 4) => {
  cyl(b, C("#2a2630"), x, y + 0.2, z, 0.01, top - y - 0.2);
  b.add(new THREE.ConeGeometry(0.28, 0.22, 16, 1, true).translate(x, y + 0.12, z), L("hlampshade", () => ({ color: "#2a3a2a", side: THREE.DoubleSide })));
  glowSph(g, WARM(), x, y + 0.02, z, 0.07);
};
export const chandelier = (b: Batch, g: THREE.Group, x: number, y: number, z: number) => {
  cyl(b, C("#c8a24a"), x, y, z, 0.02, 1.4);
  b.add(new THREE.TorusGeometry(0.6, 0.03, 6, 24).rotateX(Math.PI / 2).translate(x, y, z), C("#c8a24a"));
  for (let k = 0; k < 8; k++) { const a = (k / 8) * Math.PI * 2, cx = x + 0.6 * Math.cos(a), cz = z + 0.6 * Math.sin(a); cyl(b, C("#f2ead8"), cx, y, cz, 0.025, 0.12); glowSph(g, CANDLE(), cx, y + 0.17, cz, 0.04); }
};
/** tall window glowing (warm by night, cool by day) in a wall facing -z at z */
export const windowGlow = (b: Batch, g: THREE.Group, x: number, y: number, z: number, w: number, h: number, warm: boolean) => {
  box(b, C("#e8e0cc"), x - w / 2 - 0.1, y - 0.1, z - 0.06, x + w / 2 + 0.1, y + h + 0.1, z - 0.01);
  plane(g, warm ? WARM() : COOLW(), x, y + h / 2, z - 0.07, w, h, Math.PI, true);
  box(b, C("#5a4630"), x - 0.03, y, z - 0.1, x + 0.03, y + h, z - 0.07);
  box(b, C("#5a4630"), x - w / 2, y + h * 0.6, z - 0.1, x + w / 2, y + h * 0.6 + 0.05, z - 0.07);
};
export const shelfBooks = (b: Batch, x: number, z: number, w: number, h: number, yaw = 0) => {
  const T0 = M4(x, 0, z, yaw);
  b.add(boxGeo(V(-w / 2, 0, -0.18), V(w / 2, h, 0.18)), C("#4a2c1a"), T0);
  for (let k = 0; k < Math.floor(h / 0.45); k++) b.add(boxGeo(V(-w / 2 + 0.05, 0.1 + k * 0.45, -0.19), V(w / 2 - 0.05, 0.42 + k * 0.45, -0.17)), T("books", booksTex, Math.max(1, Math.round(w)), 1), T0);
};
export const frame = (b: Batch, g: THREE.Group, x: number, y: number, z: number, w: number, h: number, seed: number, yaw = Math.PI, gold = true) => {
  const T0 = M4(x, y, z, yaw);
  b.add(boxGeo(V(-w / 2 - 0.06, -h / 2 - 0.06, -0.02), V(w / 2 + 0.06, h / 2 + 0.06, 0.03)), C(gold ? "#c8a24a" : "#5a3a24"), T0);
  const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), T("paint" + seed, paintingTex(seed))); p.applyMatrix4(T0); p.position.add(V(0, 0, 0).set(-Math.sin(yaw) * 0.04, 0, -Math.cos(yaw) * 0.04)); g.add(p);
};
export const crate = (b: Batch, x: number, y: number, z: number, s = 0.6, yaw = 0) => b.add(boxGeo(V(-s / 2, 0, -s / 2), V(s / 2, s, s / 2), s), T("crate", planksTex("#a0784a"), 1, 1), M4(x, y, z, yaw));
export const barrel = (b: Batch, x: number, y: number, z: number, s = 1) => { cyl(b, C("#8a5a32"), x, y, z, 0.32 * s, 0.9 * s, 0.28 * s); for (const k of [0.12, 0.78]) cyl(b, C("#3a3a40"), x, y + k * s, z, 0.33 * s, 0.05 * s); };
export const stein = (b: Batch, x: number, y: number, z: number) => { cyl(b, C("#d8a43a"), x, y, z, 0.05, 0.16); cyl(b, C("#fff6e0"), x, y + 0.16, z, 0.055, 0.03); };
export const papers = (b: Batch, x: number, y: number, z: number, n = 3, seed = 1) => { const r = rng(seed); for (let k = 0; k < n; k++) b.add(boxGeo(V(-0.11, 0, -0.15), V(0.11, 0.004, 0.15)), C("#f2ecdc"), M4(x + (r() - 0.5) * 0.3, y + k * 0.004, z + (r() - 0.5) * 0.3, r() * 0.6)); };
export const cashStack = (b: Batch, x: number, y: number, z: number, h = 0.2, yaw = 0) => b.add(boxGeo(V(-0.16, 0, -0.08), V(0.16, h, 0.08)), T("cashstack", tx("cashside", 128, 64, (g) => { g.fillStyle = "#a8c89a"; g.fillRect(0, 0, 128, 64); g.fillStyle = "#7a9a6a"; for (let y = 0; y < 64; y += 6) g.fillRect(0, y, 128, 2); g.fillStyle = "#e8e0c0"; g.fillRect(52, 0, 24, 64); }), 1, 1), M4(x, y, z, yaw));
export const flagBanner = (b: Batch, g: THREE.Group, x: number, y: number, z: number, w: number, h: number, col: string, yaw = Math.PI) => {
  const m = L("banner" + col, () => ({ color: col, side: THREE.DoubleSide }));
  const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h, 6, 1), m); p.position.set(x, y, z); p.rotation.y = yaw; p.castShadow = true; g.add(p);
  cyl(b, C("#c8a24a"), x - w / 2 - 0.05, y + h / 2 - 0.02, z, 0.02, 0.04);
  b.add(boxGeo(V(x - w / 2 - 0.05, y + h / 2, z - 0.02), V(x + w / 2 + 0.05, y + h / 2 + 0.04, z + 0.02)), C("#c8a24a"));
};
const tank = (b: Batch, x: number, z: number, yaw: number, col = "#5a5e48") => {
  const T0 = M4(x, 0, z, yaw), m = C(col), dk = C("#2a2a2a");
  b.add(boxGeo(V(-2.8, 0.5, -1.4), V(2.8, 1.5, 1.4)), m, T0);
  for (const s of [-1, 1]) b.add(boxGeo(V(-3.0, 0, s * 1.4 - 0.45), V(3.0, 0.95, s * 1.4 + 0.45)), dk, T0);
  b.add(boxGeo(V(-1.2, 1.5, -0.95), V(1.0, 2.3, 0.95)), m, T0);
  const gun = new THREE.CylinderGeometry(0.1, 0.12, 3.2, 10); gun.rotateZ(Math.PI / 2); gun.translate(2.4, 1.95, 0); b.add(gun, dk, T0);
};
const tree = (b: Batch, x: number, z: number, h: number, kind: number) => {
  cyl(b, C(kind === 2 ? "#6a5a3a" : "#4a3220"), x, 0, z, 0.18 * h / 8, h * 0.75, 0.12 * h / 8);
  const lf = T("leaves", leafTex, 1, 1);
  if (kind === 1) { for (let k = 0; k < 6; k++) { const a = (k / 6) * Math.PI * 2; b.add(new THREE.ConeGeometry(0.5, 3.4, 5).rotateZ(Math.PI / 2 - 0.5).rotateY(a).translate(x + 1.4 * Math.cos(a), h * 0.75, z - 1.4 * Math.sin(a)), lf); } }
  else { sph(b, lf, x, h * 0.78, z, h * 0.22, 0.85); sph(b, lf, x + h * 0.15, h * 0.68, z + 0.3, h * 0.17, 0.85); sph(b, lf, x - h * 0.14, h * 0.7, z - 0.2, h * 0.16, 0.85); }
};
const fern = (b: Batch, x: number, z: number, s: number) => { const lf = T("leaves", leafTex, 1, 1); for (let k = 0; k < 5; k++) { const a = (k / 5) * Math.PI * 2; b.add(new THREE.ConeGeometry(0.18 * s, 1.2 * s, 4).rotateZ(Math.PI / 2 - 0.9).rotateY(a).translate(x + 0.45 * s * Math.cos(a), 0.3 * s, z - 0.45 * s * Math.sin(a)), lf); } };
const sandbags = (b: Batch, x: number, z: number, n: number, yaw = 0) => { for (let k = 0; k < n; k++) for (let row = 0; row < 3; row++) b.add(new THREE.SphereGeometry(0.32, 10, 6).scale(1.3, 0.55, 0.8).translate(-n * 0.38 + k * 0.76 + (row % 2) * 0.38, 0.17 + row * 0.3, 0), C("#a8956a"), M4(x, 0, z, yaw)); };
const ruin = (b: Batch, x: number, z: number, w: number, h: number, seed: number) => {
  const r = rng(seed), m = T("ruinbrick", brickTex("#8a6a5a"), 2, 2);
  box(b, m, x - w / 2, 0, z - 0.4, x + w / 2, h * (0.5 + 0.5 * r()), z + 0.4, 2);
  box(b, m, x - w / 2, 0, z - 0.4, x - w / 2 + w * 0.3, h, z + 0.4, 2);
  for (let k = 0; k < 6; k++) b.add(new THREE.DodecahedronGeometry(0.4 + r() * 0.5, 0).translate(x + (r() - 0.5) * w * 1.5, 0.2, z - 1 - r() * 3), C("#7a6a62"));
};

export type SetInfo = { group: THREE.Group; dyn: Record<string, THREE.Object3D> };

// ---------------- sets ----------------
/** black void, a dark map table with a long snaking line of dominoes (InstancedMesh, posed per frame in world.ts) */
const buildVoid = (g: THREE.Group, b: Batch): Record<string, THREE.Object3D> => {
  box(b, C("#1a1418"), -40, -0.2, -40, 40, 0, 40);
  box(b, T("map", mapTex, 1, 1), -6, 0, -3, 6, 0.02, 3);
  box(b, C("#3a2418"), -6.3, -0.4, -3.3, 6.3, 0.0, 3.3);
  const n = DOMINO_PATH.length;
  const geo = new THREE.BoxGeometry(0.12, 0.24, 0.04).translate(0, 0.12, 0);
  const dm = new THREE.InstancedMesh(geo, C("#f4efe4"), n); dm.castShadow = true; dm.receiveShadow = true; dm.frustumCulled = false; g.add(dm);
  return { dominos: dm };
};
/** domino positions on the map: a snake from Europe outward (local coords on the table top) */
export const DOMINO_PATH: { x: number; z: number; yaw: number }[] = (() => {
  const out: { x: number; z: number; yaw: number }[] = [];
  let x = 0.4, z = 1.5, a = 0;
  for (let i = 0; i < 160; i++) {
    a += 0.18 * Math.sin(i * 0.17) + (i % 37 === 20 ? 0.9 : 0);
    x += 0.075 * Math.cos(a); z -= 0.075 * Math.sin(a) * 0.7 + 0.012;
    if (Math.abs(x) > 5.5) a = Math.PI - a;
    out.push({ x, z, yaw: a });
  }
  return out;
})();
const buildFront = (g: THREE.Group, b: Batch) => {
  box(b, T("mud", tx("mud", 256, 256, (q, r) => { q.fillStyle = "#5a4a38"; q.fillRect(0, 0, 256, 256); for (let i = 0; i < 400; i++) { q.fillStyle = `rgba(${40 + r() * 50},${30 + r() * 40},${20 + r() * 30},.6)`; q.beginPath(); q.ellipse(r() * 256, r() * 256, 4 + r() * 14, 2 + r() * 6, r() * 3, 0, 7); q.fill(); } }), 40, 40), -200, -0.1, -100, 200, 0, 200, 0);
  for (const [x, z, y] of [[-6, 10, 0.4], [4, 16, -0.3], [-14, 24, 0.2], [10, 30, 0.6], [-2, 40, 0]] as const) tank(b, x, z, Math.PI / 2 + y);
  for (let k = 0; k < 10; k++) ruin(b, -40 + k * 9, 70 + (k % 3) * 6, 6 + (k % 3) * 2, 8 + (k % 4) * 4, k);
  for (let k = 0; k < 6; k++) sandbags(b, -20 + k * 7, 2 + (k % 2) * 3, 3, k * 0.4);
  for (let k = 0; k < 14; k++) { const r = rng(k + 3); b.add(new THREE.DodecahedronGeometry(0.3 + r() * 0.6, 0).translate(-30 + r() * 60, 0.1, r() * 60), C("#4a3e34")); }
  // fires glowing in the ruins
  for (const [x, z] of [[-18, 66], [6, 72], [22, 64], [-5, 50]] as const) glowSph(g, GLOW(5, 2.2, 0.6), x, 1.2, z, 1.4);
  // coast + sea far to the right, ships
  box(b, C("#2a4a6a"), 60, -0.05, -200, 400, 0.02, 400);
  for (const [x, z] of [[120, 60], [150, 120], [100, 160]] as const) { box(b, C("#5a6470"), x - 12, 0, z - 2.5, x + 12, 4, z + 2.5); box(b, C("#5a6470"), x - 3, 4, z - 1.5, x + 4, 8, z + 1.5); cyl(b, C("#3a3e44"), x - 1, 8, z, 0.8, 4); }
};
const buildJungle = (g: THREE.Group, b: Batch) => {
  box(b, T("jfloor", tx("jfloor", 256, 256, (q, r) => { q.fillStyle = "#3a4a24"; q.fillRect(0, 0, 256, 256); for (let i = 0; i < 300; i++) { q.fillStyle = ["#5a6a2a", "#2a3a1a", "#6a5a2a"][Math.floor(r() * 3)]; q.beginPath(); q.ellipse(r() * 256, r() * 256, 6 + r() * 10, 3 + r() * 4, r() * 3, 0, 7); q.fill(); } }), 20, 20), -60, -0.1, -60, 60, 0, 60);
  const r = rng(77);
  for (let k = 0; k < 70; k++) { const x = (r() - 0.5) * 60, z = r() * 50 - 5; if (Math.abs(x) < 2 && z < 6) continue; tree(b, x, z, 7 + r() * 9, r() < 0.5 ? 1 : 0); }
  for (let k = 0; k < 90; k++) { const x = (r() - 0.5) * 30, z = r() * 25 - 3; if (Math.abs(x) < 1.2 && z < 3) continue; fern(b, x, z, 0.7 + r() * 0.9); }
  for (let k = 0; k < 10; k++) cyl(b, C("#3a5a24"), (r() - 0.5) * 16, 0, 4 + r() * 12, 0.04, 9);
  // god rays: soft warm shafts through the canopy
  for (let k = 0; k < 4; k++) { const m = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.6, 1.5, 0.9), transparent: true, opacity: 0.12, depthWrite: false, side: THREE.DoubleSide, fog: false }); const p = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 16), m); p.position.set(-4 + k * 3, 7, 6 + k * 2); p.rotation.set(0, 0, 0.35); p.layers.set(NOINK); g.add(p); }
};
const buildWarroom = (g: THREE.Group, b: Batch) => {
  box(b, T("wrfloor", parquet("#5a3a24", "#4a2e1c"), 8, 8), -8, -0.1, -8, 8, 0, 8);
  for (const [x0, z0, x1, z1] of [[-8, 6, 8, 6.2], [-8, -8, -7.8, 8], [7.8, -8, 8, 8]] as const) box(b, T("wrwall", wallpaper("#3a3a4a", "#4a4a5e"), 4, 2), x0, 0, z0, x1, 4, z1, 2);
  table(b, 0, 1, 4.2, 2.6, 0.95, C("#3a2418"));
  box(b, T("map", mapTex, 1, 1), -1.95, 0.951, -0.2, 1.95, 0.955, 2.2);
  hangingLamp(b, g, 0, 2.3, 1, 4);
  // toy tanks, ships and planes on the map, flags pins, a ruler and pins, a WW1 helmet
  for (let k = 0; k < 12; k++) { const r = rng(k + 11); const x = -1.6 + r() * 3.2, z = 0 + r() * 2; box(b, C(k % 2 ? "#5a6a3a" : "#6a6a6a"), x - 0.05, 0.955, z - 0.035, x + 0.05, 0.99, z + 0.035); box(b, C("#3a3a3a"), x - 0.02, 0.99, z - 0.02, x + 0.025, 1.01, z + 0.02); }
  for (let k = 0; k < 16; k++) { const r = rng(k + 41); const x = -1.8 + r() * 3.6, z = -0.1 + r() * 2.2; cyl(b, C("#d8d0c0"), x, 0.955, z, 0.006, 0.12); sph(b, C(["#c8323a", "#2a4a8a", "#3a7a3a"][k % 3]), x, 1.08, z, 0.022); }
  sph(b, C("#5a5e48"), 1.2, 0.99, 1.7, 0.2, 0.45); box(b, C("#4a4e3a"), 0.95, 0.955, 1.68, 1.45, 0.97, 1.72);
  papers(b, -1.5, 0.955, 0.1, 4, 3); lamp(b, g, -1.8, 0.95, 2.1);
  shelfBooks(b, -5, 5.7, 3, 2.6); shelfBooks(b, 5, 5.7, 3, 2.6);
  frame(b, g, 0, 2.6, 6.0, 2.4, 1.2, 1); windowGlow(b, g, -3.2, 1.2, 6.0, 1.0, 2.0, true); windowGlow(b, g, 3.2, 1.2, 6.0, 1.0, 2.0, true);
  for (const x of [-2.4, 2.4]) chair(b, x, -0.6, Math.PI);
};
const buildParis = (g: THREE.Group, b: Batch) => {
  box(b, T("pfloor", parquet("#8a5a34", "#7a4a28"), 12, 12), -16, -0.1, -6, 16, 0, 22);
  box(b, T("pcarpet", carpetTex("#8a2a2a", "#c8a24a"), 3, 1), -1.6, 0.0, -2, 1.6, 0.012, 14);
  // walls: mirrors + gilded panels, tall windows on the left
  const wall = T("pwall", wallpaper("#d8c8a0", "#c8b48a"), 8, 3);
  box(b, wall, -16, 0, 14, 16, 7, 14.3, 2);
  box(b, wall, 8, 0, -6, 8.3, 7, 22, 2);
  box(b, wall, -8.3, 0, -6, -8, 7, 22, 2);
  for (let k = 0; k < 5; k++) { windowGlow(b, g, -6 + k * 3, 1.0, 14, 1.5, 4.2, true); }
  for (let k = 0; k < 6; k++) { const z = -3 + k * 3; box(b, C("#c8a24a"), 7.95, 0.9, z - 0.9, 8.0, 5.2, z + 0.9); plane(g, L("mirror", () => ({ color: "#a8b8c8" })), 7.94, 3.0, z, 1.6, 3.8, -Math.PI / 2); }
  for (let k = 0; k < 6; k++) { const z = -3 + k * 3; frame(b, g, -7.95, 3.0, z, 1.8, 1.3, k + 2, Math.PI / 2); }
  // the long table with green cloth, inkwells, papers, candles
  table(b, 0, 6, 2.2, 9, 0.8, T("baize", tx("baize", 128, 128, (q, r) => { q.fillStyle = "#2f5a3a"; q.fillRect(0, 0, 128, 128); for (let i = 0; i < 300; i++) { q.fillStyle = `rgba(0,0,0,${r() * 0.12})`; q.fillRect(r() * 128, r() * 128, 2, 2); } }), 2, 4));
  for (let k = 0; k < 6; k++) { const z = 2.5 + k * 1.4; for (const s of [-1, 1]) { chair(b, s * 1.45, z, s * Math.PI / 2, C("#7a2a2a")); papers(b, s * 0.6, 0.8, z, 2, k * 2 + (s > 0 ? 1 : 0)); cyl(b, C("#1a1a2a"), s * 0.85, 0.8, z + 0.3, 0.04, 0.06); } }
  for (const z of [3.2, 6, 8.8]) { cyl(b, C("#c8a24a"), 0, 0.8, z, 0.06, 0.32); glowSph(g, CANDLE(), 0, 1.18, z, 0.04); }
  for (const z of [2, 7, 12]) chandelier(b, g, 0, 4.6, z);
  for (const [x, z, c] of [[-3.5, 13.6, "#2a4a8a"], [-1.2, 13.6, "#f2f2f2"], [1.2, 13.6, "#c8323a"], [3.5, 13.6, "#2a5a3a"]] as const) flagBanner(b, g, x, 5.4, z, 1.6, 2.6, c);
  // the corner: a small stool and a side table for the German delegate
  chair(b, 6.6, -2.5, -Math.PI / 4, C("#5a4a3a")); table(b, 7.3, -1.2, 0.7, 0.7, 0.75); papers(b, 7.3, 0.75, -1.2, 2, 9);
  for (const x of [-6, 6]) { cyl(b, C("#e8dcc0"), x, 0, 13, 0.35, 7); }
};
const buildPress = (g: THREE.Group, b: Batch, dyn: Record<string, THREE.Object3D>) => {
  box(b, T("prfloor", planksTex("#6a5040"), 6, 6), -8, -0.1, -6, 8, 0, 10);
  box(b, T("prwall", brickTex("#9a5a44"), 6, 3), -8, 0, 8, 8, 5, 8.3, 2); box(b, T("prwall", brickTex("#9a5a44"), 6, 3), -8.3, 0, -6, -8, 5, 10, 2); box(b, T("prwall", brickTex("#9a5a44"), 6, 3), 8, 0, -6, 8.3, 5, 10, 2);
  // the press: frame, rollers, a big flywheel
  const ir = C("#3a3e46"), dk = C("#22242a");
  box(b, ir, -1.6, 0, 2, 1.6, 0.9, 4); box(b, ir, -1.4, 0.9, 2.2, -1.1, 2.6, 3.8); box(b, ir, 1.1, 0.9, 2.2, 1.4, 2.6, 3.8);
  for (const y of [1.3, 1.8, 2.3]) { const rl = new THREE.CylinderGeometry(0.22, 0.22, 2.5, 16); rl.rotateZ(Math.PI / 2); rl.translate(0, y, 3); b.add(rl, dk); }
  b.add(new THREE.TorusGeometry(0.9, 0.08, 8, 24).rotateY(Math.PI / 2).translate(1.7, 1.3, 3), C("#8a3a2a"));
  box(b, C("#e8e0c8"), -1.0, 0.9, 1.0, 1.0, 0.95, 2.0);
  // paper rolls, ink barrels, a crate of bills, lamps, shelves
  for (let k = 0; k < 4; k++) { const rl = new THREE.CylinderGeometry(0.35, 0.35, 1.2, 16); rl.rotateZ(Math.PI / 2); rl.translate(-5.5, 0.35 + (k > 1 ? 0.62 : 0), 3 + (k % 2) * 0.8); b.add(rl, C("#efe6d0")); }
  for (let k = 0; k < 3; k++) barrel(b, 5 + k * 0.8, 0, 6.5);
  for (let k = 0; k < 4; k++) crate(b, -6 + k * 0.7, 0, 7, 0.6, k * 0.3);
  hangingLamp(b, g, 0, 3.0, 2.5, 5); hangingLamp(b, g, -4, 3.2, 4, 5); hangingLamp(b, g, 4, 3.2, 4, 5);
  windowGlow(b, g, -3, 1.5, 8, 1.4, 2.2, true); windowGlow(b, g, 3, 1.5, 8, 1.4, 2.2, true);
  table(b, 3.8, 2, 2.2, 1.0, 0.9);
  // growing piles of cash on the table and floor (scaled in y per frame)
  const pile = new THREE.Group();
  for (let k = 0; k < 9; k++) { const pb = new Batch(); cashStack(pb, 0, 0, 0, 1, 0); const sub = new THREE.Group(); pb.build(sub); sub.position.set(-2.5 + (k % 3) * 0.45, 0, 0.3 + Math.floor(k / 3) * 0.3); pile.add(sub); }
  g.add(pile); dyn.cashPile = pile;
};
const buildBakery = (g: THREE.Group, b: Batch, dyn: Record<string, THREE.Object3D>) => {
  box(b, T("bkfloor", tx("tiles", 256, 256, (q) => { for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { q.fillStyle = (x + y) % 2 ? "#e8dcc4" : "#8a3a32"; q.fillRect(x * 32, y * 32, 32, 32); } }), 6, 6), -6, -0.1, -6, 6, 0, 6);
  box(b, T("bkwall", wallpaper("#e8c88a", "#d8b070"), 4, 2), -6, 0, 4, 6, 4, 4.2, 2); box(b, T("bkwall", wallpaper("#e8c88a", "#d8b070"), 4, 2), -6.2, 0, -6, -6, 4, 6, 2); box(b, T("bkwall", wallpaper("#e8c88a", "#d8b070"), 4, 2), 6, 0, -6, 6.2, 4, 6, 2);
  // counter, shelves full of loaves, baskets, scale, cash register, lamps
  box(b, C("#7a4a2a"), -3, 0, 1.6, 3, 1.0, 2.3); box(b, C("#e8dcc4"), -3.05, 1.0, 1.55, 3.05, 1.05, 2.35);
  for (let row = 0; row < 3; row++) { box(b, C("#6a3a20"), -4, 1.0 + row * 0.7, 3.7, 4, 1.05 + row * 0.7, 4.0); for (let k = 0; k < 12; k++) sph(b, C(["#c88a42", "#d89a52", "#b8783a"][k % 3]), -3.7 + k * 0.65, 1.15 + row * 0.7, 3.85, 0.13 + (k % 2) * 0.03, 0.6); }
  for (let k = 0; k < 3; k++) { cyl(b, C("#a07040"), -2.2 + k * 0.9, 1.05, 1.95, 0.22, 0.18, 0.18); for (let j = 0; j < 3; j++) sph(b, C("#d89a52"), -2.25 + k * 0.9 + j * 0.06, 1.28, 1.92 + (j - 1) * 0.08, 0.08, 0.7); }
  box(b, C("#2a2a30"), 2.0, 1.05, 1.75, 2.6, 1.45, 2.15); box(b, C("#c8a24a"), 2.05, 1.45, 1.8, 2.55, 1.55, 2.1);
  hangingLamp(b, g, -1.5, 2.7, 1.9, 4); hangingLamp(b, g, 1.5, 2.7, 1.9, 4);
  windowGlow(b, g, -4.8, 1.0, 4, 1.2, 2.0, true);
  // a big price tag on a stand on the counter (texture swapped per frame in world.ts)
  const tagM = new THREE.MeshBasicMaterial({ color: 0xffffff, fog: false });
  const tag = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.45), tagM); tag.position.set(0.0, 1.62, 1.7); tag.rotation.y = Math.PI; tag.layers.set(NOINK); g.add(tag);
  box(b, C("#3a2618"), -0.8, 1.05, 1.73, 0.8, 1.4, 1.76);
  dyn.priceTag = tag;
  // the customer's wheelbarrow full of cash, outside the counter
  const T0 = M4(-1.2, 0, -0.4, 0.5);
  b.add(boxGeo(V(-0.5, 0.35, -0.35), V(0.5, 0.75, 0.35)), C("#6a5a4a"), T0);
  for (let k = 0; k < 10; k++) b.add(boxGeo(V(-0.16, 0, -0.08), V(0.16, 0.12, 0.08)).translate(-0.3 + (k % 3) * 0.3, 0.75 + Math.floor(k / 3) * 0.1, -0.15 + (k % 2) * 0.3), C("#9fbf8a"), T0);
  const wh = new THREE.CylinderGeometry(0.25, 0.25, 0.08, 16); wh.rotateX(Math.PI / 2); wh.translate(0.6, 0.25, 0); b.add(wh, C("#3a3a3a"), T0);
  for (const s of [-1, 1]) b.add(boxGeo(V(-1.2, 0.5, s * 0.25 - 0.03), V(-0.5, 0.56, s * 0.25 + 0.03)), C("#5a3a20"), T0);
};
const buildPlayroom = (g: THREE.Group, b: Batch) => {
  box(b, T("plfloor", planksTex("#9a7050"), 5, 5), -5, -0.1, -5, 5, 0, 5);
  box(b, T("plcarpet", carpetTex("#3a5a8a", "#e8c84a"), 1, 1), -1.8, 0, -1, 1.8, 0.012, 2.2);
  box(b, T("plwall", wallpaper("#c8d8b0", "#a8bc8a"), 4, 2), -5, 0, 3.5, 5, 3.4, 3.7, 2); box(b, T("plwall", wallpaper("#c8d8b0", "#a8bc8a"), 4, 2), -5.2, 0, -5, -5, 3.4, 5, 2);
  windowGlow(b, g, 1.5, 1.0, 3.5, 1.2, 1.6, false); frame(b, g, -1.6, 2.0, 3.5, 0.9, 0.7, 5, Math.PI, false);
  shelfBooks(b, 3.6, 3.2, 1.6, 1.8); lamp(b, g, -3.2, 0.7, 2.6, "#c8642a"); table(b, -3.2, 2.6, 0.8, 0.6, 0.7);
  // a rocking horse, a toy train, a teddy, and cash bundles everywhere
  cyl(b, C("#c8323a"), 2.4, 0, 1.2, 0.12, 0.5); sph(b, C("#c8323a"), 2.4, 0.65, 1.2, 0.3, 0.6); sph(b, C("#c8323a"), 2.7, 0.85, 1.2, 0.14);
  for (let k = 0; k < 3; k++) box(b, C(["#2a5a8a", "#c8a24a", "#3a7a3a"][k]), -2.4 + k * 0.42, 0, -0.6, -2.05 + k * 0.42, 0.25, -0.35);
  sph(b, C("#a0703a"), 1.6, 0.25, 2.6, 0.25); sph(b, C("#a0703a"), 1.6, 0.6, 2.6, 0.17);
  for (let k = 0; k < 14; k++) { const r = rng(k + 5); cashStack(b, -1.5 + r() * 3, 0.012, -0.8 + r() * 2.6, 0.08, r() * 3); }
};
/** a street of tall townhouses with shopfronts, lamps, a square at the end with a balcony building */
const buildStreet = (g: THREE.Group, b: Batch, night: boolean) => {
  const sfx = night ? "n" : "d";
  box(b, T("cobble", cobbleTex, 30, 30), -30, -0.1, -20, 30, 0, 60);
  box(b, C("#8a8478"), -30, 0, -20, -6, 0.15, 60); box(b, C("#8a8478"), 6, 0, -20, 30, 0.15, 60);
  const walls = ["#c8a88a", "#9aa8b8", "#d8c49a", "#b88a7a", "#a8b89a"];
  for (let k = 0; k < 8; k++) for (const s of [-1, 1]) {
    const z = -12 + k * 7, x = s * 10, w = 7, h = 11 + ((k + (s > 0 ? 1 : 0)) % 3) * 2;
    const fm = T(`fac${k % 5}${sfx}`, facadeTex(walls[(k + (s > 0 ? 2 : 0)) % 5], night), 1, 1);
    box(b, fm, s > 0 ? x : x - 6, 3, z - w / 2, s > 0 ? x + 6 : x, 3 + h - 3, z + w / 2);
    box(b, T(`shop${k % 3}${sfx}`, shopfrontTex(k, night), 1, 1), s > 0 ? x : x - 6, 0, z - w / 2, s > 0 ? x + 6 : x, 3, z + w / 2);
    box(b, C("#5a3a3a"), s > 0 ? x - 0.3 : x, 3 + h - 3, z - w / 2, s > 0 ? x + 6 : x + 0.3, 3 + h - 2.6, z + w / 2);
    // awning
    b.add(boxGeo(V(0, 0, -w / 2 + 0.3), V(1.4, 0.08, w / 2 - 0.3)), C(["#c8323a", "#2a6a4a", "#e8c84a"][k % 3]), new THREE.Matrix4().makeTranslation(s > 0 ? x - 1.4 : x, 2.9, z).multiply(new THREE.Matrix4().makeRotationZ(s * 0.25)));
    if (night) for (let w2 = 0; w2 < 3; w2++) plane(g, WARM(), s > 0 ? x - 0.02 : x + 0.02, 1.5, z - 1.5 + w2 * 0.0, 2.6, 1.4, s > 0 ? -Math.PI / 2 : Math.PI / 2, true);
  }
  // the square's end building with a balcony
  box(b, T(`facEnd${sfx}`, facadeTex("#c8b48a", night), 2, 1), -12, 0, 46, 12, 16, 48);
  box(b, C("#e8dcc0"), -3, 6, 44.5, 3, 6.3, 46); for (let k = 0; k < 9; k++) box(b, C("#e8dcc0"), -2.9 + k * 0.72, 6.3, 44.55, -2.8 + k * 0.72, 7.2, 44.65); box(b, C("#e8dcc0"), -3, 7.2, 44.5, 3, 7.3, 44.7);
  for (let k = 0; k < 4; k++) flagBanner(b, g, -9 + k * 6, 11, 45.9, 1.8, 4.5, "#a82a2a");
  for (let k = 0; k < 6; k++) for (const s of [-1, 1]) { const z = -10 + k * 9; cyl(b, C("#2a2a30"), s * 5.6, 0.15, z, 0.07, 4.2); if (night) glowSph(g, WARM(), s * 5.6, 4.5, z, 0.22); else sph(b, C("#e8e0c8"), s * 5.6, 4.5, z, 0.2); }
  for (let k = 0; k < 8; k++) { const r = rng(k + 21); crate(b, (r() < 0.5 ? -1 : 1) * (6.4 + r() * 1.5), 0.15, -10 + r() * 40, 0.55, r() * 3); }
  for (let k = 0; k < 6; k++) barrel(b, (k % 2 ? -1 : 1) * 7.2, 0.15, -6 + k * 7, 0.8);
  // a factory gate with chains for the dole queue
  box(b, T("brick2", brickTex("#7a4a3a"), 2, 2), 6, 0, 22, 6.3, 5, 30); box(b, C("#2a2a30"), 6.05, 0, 24.5, 6.35, 3.6, 27.5);
  crate(b, 0, 0, 34.2, 0.55); // the speaker's crate
};
const buildWallst = (g: THREE.Group, b: Batch, dyn: Record<string, THREE.Object3D>) => {
  box(b, T("wsfloor", parquet("#6a4a34", "#5a3a28"), 8, 8), -8, -0.1, -6, 8, 0, 10);
  box(b, T("wswall", wallpaper("#5a6a5a", "#4a5a4a"), 6, 3), -8, 0, 7, 8, 5, 7.3, 2); box(b, T("wswall", wallpaper("#5a6a5a", "#4a5a4a"), 6, 3), -8.3, 0, -6, -8, 5, 10, 2); box(b, T("wswall", wallpaper("#5a6a5a", "#4a5a4a"), 6, 3), 8, 0, -6, 8.3, 5, 10, 2);
  // the big chart board (the line is a cast effect card in front of it)
  box(b, C("#3a2a1a"), -3.2, 1.2, 6.8, 3.2, 4.3, 7.0); plane(g, T("chartboard", chartBoardTex, 1, 1), 0, 2.75, 6.78, 6.0, 2.9, Math.PI);
  for (let k = 0; k < 4; k++) { table(b, -4.5 + k * 3, 2.5, 2.2, 1.0, 0.8); lamp(b, g, -5.2 + k * 3, 0.8, 2.7); papers(b, -4.2 + k * 3, 0.8, 2.4, 5, k); box(b, C("#1a1a1a"), -4.0 + k * 3, 0.8, 2.2, -3.7 + k * 3, 1.0, 2.4); chair(b, -4.5 + k * 3, 1.7, 0); }
  // ticker tape machine on a pedestal, a clock, a safe, a coat stand
  cyl(b, C("#3a2a1a"), 5.5, 0, 0.5, 0.15, 1.0); sph(b, L("glassdome", () => ({ color: "#c8d8e8" })), 5.5, 1.15, 0.5, 0.2);
  box(b, C("#2a2a30"), -7.4, 0, 4.5, -6.4, 1.3, 5.5); cyl(b, C("#c8a24a"), -6.4, 0.65, 5.0, 0.08, 0.04);
  cyl(b, C("#f2ead8"), 0, 4.6, 6.75, 0.35, 0.05); hangingLamp(b, g, -3, 3.2, 2.5, 5); hangingLamp(b, g, 3, 3.2, 2.5, 5);
  windowGlow(b, g, -5.5, 1.4, 7, 1.4, 2.4, false); windowGlow(b, g, 5.5, 1.4, 7, 1.4, 2.4, false);
  void dyn;
};
const buildAtelier = (g: THREE.Group, b: Batch) => {
  box(b, T("atfloor", planksTex("#8a6a4a"), 5, 5), -5, -0.1, -5, 5, 0, 5);
  box(b, T("atwall", wallpaper("#b8a888", "#a8987a"), 4, 2), -5, 0, 3.5, 5, 3.6, 3.7, 2); box(b, T("atwall", wallpaper("#b8a888", "#a8987a"), 4, 2), -5.2, 0, -5, -5, 3.6, 5, 2);
  windowGlow(b, g, -2.5, 1.0, 3.5, 1.6, 2.2, false);
  // easel, stacked canvases, a stool, paint table with jars, framed works leaning on the wall
  const wd = C("#8a5a32");
  for (const [dx, dz] of [[-0.35, 0], [0.35, 0], [0, 0.4]] as const) b.add(boxGeo(V(-0.03, 0, -0.03), V(0.03, 1.8, 0.03)).rotateX(dz ? -0.25 : 0).rotateZ(dx * 0.3).translate(0.4 + dx, 0, 0.8 + dz), wd);
  box(b, wd, -0.05, 0.75, 0.75, 0.85, 0.8, 0.85);
  table(b, 1.8, 1.0, 0.9, 0.6, 0.75); for (let k = 0; k < 5; k++) cyl(b, C(["#c8323a", "#2a4a8a", "#e8c84a", "#3a7a3a", "#f2f2f2"][k]), 1.5 + k * 0.14, 0.75, 1.0, 0.04, 0.12);
  for (let k = 0; k < 5; k++) frame(b, g, -4.4 + k * 0.25, 0.6, 2.4 - k * 0.5, 0.9, 0.7, 10 + k, Math.PI / 2 - 0.2, false);
  for (let k = 0; k < 3; k++) frame(b, g, 1.2 + k * 1.3, 2.3, 3.45, 0.9, 0.7, 20 + k, Math.PI, true);
  chair(b, -0.6, 0.3, 0.6); lamp(b, g, 1.5, 0.75, 1.2, "#c8a24a"); shelfBooks(b, 4.0, 3.2, 1.4, 2.0);
};
const buildBeerhall = (g: THREE.Group, b: Batch) => {
  box(b, T("bhfloor", planksTex("#6a4428"), 8, 8), -10, -0.1, -6, 10, 0, 14);
  const wall = T("bhwall", tx("bhwall", 256, 256, (q, r) => { q.fillStyle = "#d8c098"; q.fillRect(0, 0, 256, 256); q.fillStyle = "#6a4428"; q.fillRect(0, 150, 256, 106); for (let x = 0; x < 256; x += 32) { q.fillStyle = "#4a2c18"; q.fillRect(x, 150, 3, 106); } for (let i = 0; i < 200; i++) { q.fillStyle = `rgba(0,0,0,${r() * 0.06})`; q.fillRect(r() * 256, r() * 150, 8, 4); } }), 6, 1);
  box(b, wall, -10, 0, 12, 10, 5, 12.3, 0); box(b, wall, -10.3, 0, -6, -10, 5, 14, 0); box(b, wall, 10, 0, -6, 10.3, 5, 14, 0);
  for (let k = 0; k < 6; k++) box(b, C("#4a2c18"), -10, 4.2, -5 + k * 3.4, 10, 4.5, -4.6 + k * 3.4); // ceiling beams
  for (let row = 0; row < 3; row++) for (const s of [-1, 1]) {
    const x = s * 3.5, z = 1 + row * 3.6;
    table(b, x, z, 3.2, 1.0, 0.8, C("#7a5030"));
    for (let k = 0; k < 4; k++) { stein(b, x - 1.2 + k * 0.8, 0.8, z + (k % 2 ? 0.2 : -0.2)); }
    for (const dz of [-0.8, 0.8]) box(b, C("#5a3a20"), x - 1.6, 0.42, z + dz - 0.18, x + 1.6, 0.48, z + dz + 0.18);
  }
  for (let k = 0; k < 4; k++) hangingLamp(b, g, (k % 2 ? 3.5 : -3.5), 2.8, 1 + Math.floor(k / 2) * 5, 4.3);
  for (let k = 0; k < 6; k++) barrel(b, -9.2, 0, -3 + k * 1.4, 1);
  for (let k = 0; k < 3; k++) for (let j = 0; j < 2; j++) barrel(b, 9.2, j * 0.92, -2 + k * 1.4, 1);
  crate(b, 0, 0, 10.6, 0.55); // the beer crate (speaker stands on it)
  box(b, C("#5a3a20"), -1.2, 0, 11.2, 1.2, 1.1, 11.8); // podium
  for (let k = 0; k < 4; k++) frame(b, g, -6 + k * 4, 3.0, 12.0, 1.0, 0.8, 30 + k, Math.PI, false);
  for (let k = 0; k < 2; k++) flagBanner(b, g, -2.6 + k * 5.2, 3.2, 11.9, 1.4, 2.6, "#a82a2a");
  windowGlow(b, g, -7, 1.6, 12, 1.2, 1.6, true); windowGlow(b, g, 7, 1.6, 12, 1.2, 1.6, true);
};

/** build one set into a fresh group (origin = set origin) */
export const buildSet = (n: SetName, night = false): SetInfo => {
  const group = new THREE.Group(), b = new Batch(), dyn: Record<string, THREE.Object3D> = {};
  switch (n) {
    case "void": Object.assign(dyn, buildVoid(group, b)); break;
    case "front": buildFront(group, b); break;
    case "jungle": buildJungle(group, b); break;
    case "warroom": buildWarroom(group, b); break;
    case "paris": buildParis(group, b); break;
    case "press": buildPress(group, b, dyn); break;
    case "bakery": buildBakery(group, b, dyn); break;
    case "playroom": buildPlayroom(group, b); break;
    case "street": buildStreet(group, b, night); break;
    case "wallst": buildWallst(group, b, dyn); break;
    case "atelier": buildAtelier(group, b); break;
    case "beerhall": buildBeerhall(group, b); break;
  }
  b.build(group);
  group.traverse((o) => { const m = o as THREE.Mesh; if (m.isMesh && !(m.material instanceof THREE.MeshBasicMaterial)) { m.castShadow = true; m.receiveShadow = true; } });
  const [ox, oy, oz] = setOrigin(n);
  group.position.set(ox, oy, oz);
  return { group, dyn };
};
export type { P3 };
