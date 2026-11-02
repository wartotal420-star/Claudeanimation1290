// WW2 part 1 world: sets are built lazily (sets.ts) and only the current shot's set is visible. Light rig as the
// shorts (camera-relative sun frozen per shot, two-tone uniforms), sky sphere + fog per light, plus the moving parts:
// dominoes, the unrolling bill, the growing cash pile, the bakery price tag.
import * as THREE from "three";
import { V, Kit } from "./build";
import { ctex, cloudHD } from "./paint";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, untone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, stage, DOMINO_T0, DOMINO_DT, tagAt } from "./cast";
import { FPS, SHOTS, camAt, ShotDef, smooth } from "./story";
import { buildSet, SetName, SetInfo, DOMINO_PATH, setOrigin } from "./sets";
import { drawTag } from "./toon";

export const loadKit = () => Promise.resolve({} as Kit);

export class World {
  root = new THREE.Group();
  private pool = new Pool();
  private actors: Actor[] = [];
  private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#000000", 25, 420);
  private sunCache = new Map<number, THREE.Vector3>();
  private clouds: THREE.Mesh[] = [];
  private cloudMaps: Record<string, THREE.Texture[]> = {};
  private sets = new Map<string, SetInfo>();
  private scroll: THREE.Mesh | null = null;
  private tagTex = new Map<string, THREE.Texture>();
  private frustum = new THREE.Frustum();
  private m4 = new THREE.Matrix4(); private v = new THREE.Vector3(); private sph = new THREE.Sphere();

  constructor(_kit: Kit) {
    const R = this.root;
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() }, c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el)); c = mix(c, c2, smoothstep(e.x, e.y, el)); c = mix(c, c3, smoothstep(e.y, e.z, el)); c = mix(c, c4, smoothstep(e.z, e.w, el));
          gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(2400, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK); R.add(this.sky);
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6);
    this.sun.castShadow = true; this.sun.shadow.mapSize.set(4096, 4096);
    R.add(this.hemi, this.sun, this.sun.target);
    for (const k of ["day", "dusk", "golden", "grey", "gloom"] as const) this.cloudMaps[k] = [0, 1, 2, 3].map((i) => cloudHD(i, LOOK[k].cloud));
    for (let i = 0; i < 12; i++) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], transparent: true, depthWrite: false, fog: false }));
      m.layers.set(NOINK); this.clouds.push(m); R.add(m);
    }
  }

  private set(n: SetName, night: boolean) {
    const key = n + (n === "street" && night ? "_n" : "");
    let s = this.sets.get(key);
    if (!s) {
      s = buildSet(n, night && n === "street");
      this.root.add(s.group); this.sets.set(key, s);
      if (n === "paris") {
        const tex = ctex("billLines", 256, 512, (g) => { g.fillStyle = "#f2ecdc"; g.fillRect(0, 0, 256, 512); g.fillStyle = "#6a6458"; for (let y = 10; y < 512; y += 22) g.fillRect(24, y, 150 + ((y * 7) % 60), 7); g.fillStyle = "#b8202c"; g.fillRect(200, 0, 6, 512); });
        const t2 = tex.clone(); t2.wrapT = THREE.RepeatWrapping; t2.needsUpdate = true;
        const m = new THREE.MeshLambertMaterial({ map: t2 });
        this.scroll = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1).rotateX(-Math.PI / 2).translate(0, 0, -0.5), m);
        this.scroll.receiveShadow = true; s.group.add(this.scroll);
      }
    }
    return s;
  }

  private shotSun(id: number, s: ShotDef, L: LightPreset) {
    let v = this.sunCache.get(id);
    if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) { const c = camAt(id, f), x = c.look[0] - c.pos[0], z = c.look[2] - c.pos[2], n = Math.hypot(x, z) || 1; fx += x / n; fz += z / n; }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(s.sunAz ?? L.az), el = THREE.MathUtils.degToRad(s.sunEl ?? L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    this.sunCache.set(id, v);
    return v;
  }
  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }
  private tag(text: string) {
    let t = this.tagTex.get(text);
    if (!t) { t = ctex("tag" + text, 768, 230, (g) => drawTag(g, text)); t.colorSpace = THREE.SRGBColorSpace; this.tagTex.set(text, t); }
    return t;
  }

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], L = LIGHTS[s.light], K = LOOK[s.light];
    const cur = this.set(s.set, !!s.night);
    for (const v of this.sets.values()) v.group.visible = v === cur;
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.04; cam.far = 3000; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    // ---- light rig ----
    const sunDir = this.shotSun(id, s, L);
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    const Rr = THREE.MathUtils.clamp(dist * 1.2 + 4, 4, 160);
    this.sun.position.copy(focus).addScaledVector(sunDir, 300); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera;
    sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 20; sc.far = 700; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * (Rr / 12);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad; CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    // ---- sky, fog, clouds ----
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg));
    su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    const [fn, ff] = s.fog ?? [L.fogNear, L.fogFar];
    untone(L.fog, this.fog.color); this.fog.near = fn; this.fog.far = ff; scene.fog = this.fog; scene.background = null;
    const cm = this.cloudMaps[s.light];
    this.clouds.forEach((m, i) => {
      m.visible = !!cm; if (!cm) return;
      const a = (i / 12) * Math.PI * 2 + 0.3, d = 1500 + (i % 3) * 150, w = 380 + (i % 4) * 80;
      m.position.set(cam.position.x + Math.cos(a) * d, 260 + (i % 4) * 70, cam.position.z + Math.sin(a) * d); m.scale.set(w, w / 2, 1);
      m.lookAt(cam.position.x, m.position.y, cam.position.z); (m.material as THREE.MeshBasicMaterial).map = cm[i % 4];
    });
    // ---- moving parts ----
    const dm = cur.dyn.dominos as THREE.InstancedMesh | undefined;
    if (dm) {
      const q = new THREE.Quaternion(), qy = new THREE.Quaternion(), qx = new THREE.Quaternion(), p = V(0, 0, 0), one = V(1, 1, 1), off = V(0, 0, 0);
      DOMINO_PATH.forEach((d, i) => {
        const nx = DOMINO_PATH[Math.min(i + 1, DOMINO_PATH.length - 1)], pv = DOMINO_PATH[Math.max(i - 1, 0)];
        const yaw = Math.atan2(nx.x - pv.x, nx.z - pv.z);
        const u = smooth((t - DOMINO_T0 - i * DOMINO_DT) / 0.12), ang = 1.2 * u;
        qy.setFromAxisAngle(V(0, 1, 0), yaw); qx.setFromAxisAngle(V(1, 0, 0), ang); q.copy(qy).multiply(qx);
        off.set(0, 0, 0.02).applyQuaternion(qy); // pivot at the front base edge
        const back = V(0, 0, -0.02).applyQuaternion(q);
        p.set(d.x, 0.02, d.z).add(off).add(back);
        dm.setMatrixAt(i, this.m4.compose(p, q, one));
      });
      dm.instanceMatrix.needsUpdate = true;
    }
    if (this.scroll) {
      this.scroll.visible = id === 12;
      const len = 0.01 + 24 * smooth((f - 1294) / 100);
      this.scroll.scale.set(1, 1, len); this.scroll.position.set(0, 0.022, 1.3);
      (this.scroll.material as THREE.MeshLambertMaterial).map!.repeat.set(1, len / 1.5);
    }
    const pile = cur.dyn.cashPile;
    if (pile) { const k = id === 13 ? 0.4 + 3.6 * smooth((f - 1560) / 110) : 2; pile.children.forEach((ch, i) => ch.scale.set(1, k * (0.6 + 0.4 * ((i * 7) % 5) / 4), 1)); }
    const tagM = cur.dyn.priceTag as THREE.Mesh | undefined;
    if (tagM) { const m = tagM.material as THREE.MeshBasicMaterial, tx = this.tag(tagAt(f)); if (m.map !== tx) { m.map = tx; m.color.setScalar(1.15); m.needsUpdate = true; } }
    // ---- cast + effects ----
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const st = stage(id, f, { pos: cam.position, right }, sunDir);
    this.frustum.setFromProjectionMatrix(this.m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    let ai = 0;
    const used: Actor[] = [];
    for (const pl of st.places) {
      const sc2 = pl.scale ?? 1;
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(pl.x, pl.y + 1.1 * sc2, pl.z), 3.5 * sc2))) continue;
      const a = this.actor(ai++), [w, h, k] = pl.size ?? [300, 500, 0.5];
      a.r = this.pool.req(pl.key, w, h, k, pl.draw);
      a.mesh.visible = true; a.mesh.position.set(pl.x, pl.y, pl.z);
      a.mesh.rotation.set(0, pl.yaw ?? Math.atan2(cam.position.x - pl.x, cam.position.z - pl.z), pl.roll ?? 0);
      a.mesh.scale.set(pl.mirror ? -sc2 : sc2, sc2, sc2); a.mesh.castShadow = L.actorShadow;
      used.push(a);
    }
    for (let i = ai; i < this.actors.length; i++) this.actors[i].mesh.visible = false;
    let fi = 0;
    const fused: Fx[] = [];
    for (const pl of st.fx) {
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(pl.x, pl.y, pl.z), Math.max(Math.abs(pl.w), pl.h)))) continue;
      const e2 = this.fx(fi++);
      e2.r = this.pool.req(pl.key, pl.cw, pl.ch, 1, pl.draw);
      e2.use(!!pl.soft, pl.glow ?? 1, pl.opacity ?? 1);
      e2.mesh.visible = true; e2.mesh.position.set(pl.x, pl.y, pl.z);
      if (pl.flat) e2.mesh.rotation.set(-Math.PI / 2, 0, pl.rot ?? 0);
      else { e2.mesh.quaternion.copy(cam.quaternion); e2.mesh.rotateZ(pl.rot ?? 0); }
      e2.mesh.scale.set(pl.w, pl.h, 1);
      fused.push(e2);
    }
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    this.pool.flush();
    for (const a of used) a.bind();
    for (const e3 of fused) e3.bind();
    return focus;
  }
}
void setOrigin;
