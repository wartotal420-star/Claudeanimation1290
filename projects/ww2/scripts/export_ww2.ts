// Export WW2 shots for Blender: per frame the camera, lens, and every character / effect card (set-local three.js
// coordinates), plus each unique drawing as a PNG (Node canvas). Usage:
//   npx tsx scripts/export_ww2.ts <outDir> [shotIds comma list | all] [step=1]
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { createCanvas } from "@napi-rs/canvas";

// minimal DOM shim: cast.ts makes tiny placeholder canvases at load time
(globalThis as any).document = { createElement: () => createCanvas(2, 2) };
(globalThis as any).window = globalThis;

const [outDir, which = "all", stepS = "1"] = process.argv.slice(2);
const step = Number(stepS);
const THREE = await import("three");
const story = await import("../src/videos/ww2/story");
const cast = await import("../src/videos/ww2/cast");
const sets = await import("../src/videos/ww2/sets");
const lights = await import("../src/videos/ww2/lights");
const { Pen } = await import("../src/videos/ww2/toon");

fs.mkdirSync(path.join(outDir, "cards"), { recursive: true });
const done = new Set(fs.readdirSync(path.join(outDir, "cards")).map((f) => f.replace(".png", "")));
const hashOf = (key: string, w: number, h: number) => crypto.createHash("sha1").update(`${w}x${h}|${key}`).digest("hex").slice(0, 16);
const draw = (key: string, w: number, h: number, k: number, fn: (p: any) => void) => {
  const id = hashOf(key, w, h);
  if (!done.has(id)) {
    const c = createCanvas(w, h), g = c.getContext("2d") as any;
    g.setTransform(k, 0, 0, k, 0, 0);
    fn(new Pen(g));
    fs.writeFileSync(path.join(outDir, "cards", id + ".png"), c.toBuffer("image/png"));
    done.add(id);
  }
  return id;
};
/** camera-relative sun as world.ts shotSun (mean view direction turned by az, lifted by el) */
const sunCache = new Map<number, InstanceType<typeof THREE.Vector3>>();
const shotSun = (s: any) => {
  let v = sunCache.get(s.id); if (v) return v;
  let fx = 0, fz = 0;
  for (let f = s.a; f < s.b; f += 3) { const c = story.camAt(s.id, f), x = c.look[0] - c.pos[0], z = c.look[2] - c.pos[2], n = Math.hypot(x, z) || 1; fx += x / n; fz += z / n; }
  const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
  const L = (lights.LIGHTS as any)[s.light];
  const az = THREE.MathUtils.degToRad(s.sunAz ?? L.az), el = THREE.MathUtils.degToRad(s.sunEl ?? L.el);
  const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
  v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize(); sunCache.set(s.id, v); return v;
};

const ids = which === "all" ? story.SHOTS.map((s: any) => s.id) : which.split(",").map(Number);
const r3 = (v: number) => Math.round(v * 1000) / 1000;
for (const id of ids) {
  const s = story.SHOTS[id - 1], o = sets.setOrigin(s.set), x = story.XFADE[id] ?? 0, xn = story.XFADE[id + 1] ?? 0;
  const f0 = Math.max(0, s.a - Math.ceil(x / 2)), f1 = Math.min(story.TOTAL, s.b + Math.ceil(xn / 2));
  const frames: any[] = [];
  for (let f = f0; f < f1; f += step) {
    const c = story.camAt(id, f);
    const pos = new THREE.Vector3(...c.pos), look = new THREE.Vector3(...c.look);
    const fwd = look.clone().sub(pos).normalize(), right = fwd.clone().cross(new THREE.Vector3(0, 1, 0)).normalize();
    const st = cast.stage(id, f, { pos, right }, shotSun(s));
    const L = (v: number[]) => [r3(v[0] - o[0]), r3(v[1] - o[1]), r3(v[2] - o[2])];
    const d = story.dofAt(f);
    const places = st.places.map((p: any) => {
      const [w, h, k] = p.size ?? [300, 500, 0.5];
      return { h: draw(p.key, w, h, k, p.draw), p: L([p.x, p.y, p.z]), s: r3(p.scale ?? 1), m: p.mirror ? 1 : 0, yaw: p.yaw ?? null, roll: p.roll ?? 0 };
    });
    const fx = st.fx.filter((e: any) => !e.key.startsWith("blob|")).map((e: any) => ({
      h: draw(e.key, e.cw, e.ch, 1, e.draw), p: L([e.x, e.y, e.z]), w: r3(e.w), hh: r3(e.h), flat: e.flat ? 1 : 0, rot: r3(e.rot ?? 0), glow: e.glow ?? 1, soft: e.soft ? 1 : 0, op: e.opacity ?? 1,
    }));
    frames.push({ f, cam: { pos: L(c.pos), look: L(c.look), fov: r3(c.fov), roll: r3(c.roll) }, dof: { c: r3(d.cInf), focus: d.focus ? L(d.focus(f)) : null }, places, fx });
  }
  fs.writeFileSync(path.join(outDir, `shot${String(id).padStart(2, "0")}.json`), JSON.stringify({ id, set: s.set, night: !!s.night, light: s.light, a: s.a, b: s.b, f0, f1, frames }));
  console.log(`shot ${id}: ${frames.length} frames, ${done.size} cards total`);
}
