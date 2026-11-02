// Chapter modules (ch/chNN.ts) describe one chapter of the long-form video for the Blender pipeline:
// shots (local frames from 0, voice = ~/ww2/voice/chNN.wav, words = chNN_words.json, 2.0 s lead-in for the card),
// cameras, lens, kicks and per-shot staging. scripts/export_ww2.ts exports them with PART=chNN.
import * as THREE from "three";
import { FPS, camFrom, kicker, dofFrom } from "./story";
import type { Key, Dof, ShotDef } from "./story";
import { stageWith } from "./cast";
import type { Ctx, CamInfo } from "./cast";
import { setOrigin } from "./sets";
import type { SetName } from "./sets";

export type ChShot = Omit<ShotDef, "set"> & { set: string };
export type ChapterDef = {
  total: number;                                  // frames (= chNN.wav length * 30)
  shots: ChShot[];                                // contiguous: shots[0].a = 0, last.b = total
  xfade?: Record<number, number>;                 // shot id -> crossfade frames into that shot
  cards: { a: number; b: number; kind: "title" | "chapter"; lines: string[] }[];
  cams: Record<number, Key[]>;                    // per shot camera keys (frames are chapter-local)
  dof: Dof[];                                     // lens table (frame-sorted)
  kicks?: [number, number][];                     // [seconds, strength] camera shakes on impacts
  stage: Record<number, (c: Ctx) => void>;        // per shot staging (set-local coordinates)
};
export const makeChapter = (d: ChapterDef) => {
  const kick = kicker(d.kicks ?? []), dofAt = dofFrom(d.dof);
  const byId = new Map(d.shots.map((s) => [s.id, s]));
  return {
    TOTAL: d.total, SHOTS: d.shots, XFADE: d.xfade ?? {}, CARDS: d.cards, FPS, KICKS: d.kicks ?? [],
    camAt: (id: number, f: number) => camFrom(d.cams[id], f, kick),
    dofAt,
    stage: (id: number, f: number, cam: CamInfo, sun: THREE.Vector3) => {
      const s = byId.get(id)!;
      return stageWith(d.stage[id], s.light, setOrigin(s.set as SetName), f, cam, sun);
    },
  };
};
/** frame of the first spoken word matching `w` at or after second `from` (chapter-local words list) */
export const wordAt = (words: { w: string; s: number }[], w: string, from = 0) => {
  const x = words.find((o) => o.s >= from && o.w.toLowerCase() === w.toLowerCase());
  if (!x) throw new Error(`word ${w} after ${from}s not found`);
  return Math.round(x.s * FPS);
};
