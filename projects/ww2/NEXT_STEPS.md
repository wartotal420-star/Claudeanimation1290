# WW2 long-form: status and next steps (2026-11-02)

"The ENTIRE History of WW2 [No AI]": 16:9, 1920x1080, 30 fps, about 28 minutes in total
(part 1 is 2:01, chapters 2-14 are 25:47). Rendered in Blender (Cycles) on the Mac.

## Done
- **Pipeline:** three.js code directs the shots (`src/videos/ww2`). `scripts/export_ww2.ts` exports cameras and
  character cards per shot (`PART=chNN` for chapters), Blender renders them (`blender/render_shot.py` plus
  `blender/sets/*.py`), and `blender/assemble.py` adds crossfades, title cards and sound, then writes the mp4.
- **Part 1 (cold open + chapter 1):**
  - 28 shots on 12 detailed Blender sets.
  - Upgraded characters (patterned outfits, faces, gestures timed to the narration).
  - Sound mixed (`audio/mix_part1.wav`).
  - Every shot was checked one frame per 1.5 s, and cameras were fixed (no cut-off heads, no tiny main characters).
- **Mac script:** `render_blender_mac.sh` has three modes: `stills`, `preview` (EEVEE, half size) and `final` (Cycles,
  16 spp). It renders `part1`, a single chapter (`chNN`) or `all`, which joins every part into one video. Tested end to
  end here with a stand-in Blender: install, export, render, assemble, mp4 with sound.
- **Narration for chapters 2-14:**
  - `tools/align_long.py` timed all 436 sentences word by word.
  - `tools/chapters.py` cut the narration into chapter voice files with a 2 s lead-in for each chapter card.
  - Word timings are in `voice/chNN_words.json` and `voice/chNN_lines.json`; lengths are in `voice/chapters.json`.
- **Cast for chapters 2-14:** leaders (Churchill, Stalin, Roosevelt, Mussolini, Chamberlain, de Gaulle, Hitler 1940
  and 1945, Truman, Eisenhower, MacArthur, Montgomery, Zhukov, Tojo, Rommel, ...), every army, officers, pilots,
  sailors, nurses, Rosies, codebreakers, civilians, refugees, plus new poses, props, expressions and flags. See
  `docs/CAST2_NOTE.md`.
- **Chapter sound generator:** `audio/chapter_audio.py`. Score from per-sentence mood maps (serious for the
  Holocaust and the atomic bombs; no sting on chapter 10), ambience from each shot's set, explosions on camera kicks,
  mixed to -15 LUFS with peaks at or below -1.2 dBTP. Tested on chapter 2.
- **Fixes along the way:**
  - camera roll bug;
  - stale character drawings (card ids now include a hash of the drawing code);
  - exporter memory (4.2 GB down to 0.45 GB per shot);
  - Blender 5 video output.

## In progress (parallel builders, following `docs/CHAPTER_BRIEF.md`)
| Chapters | State |
|---|---|
| 2, 3, 4 | Chapter 2 drafted; sets for 2 and 4 in progress |
| 5, 6, 8 | Chapters 5 and 6 drafted, many sets built; 8 not started |
| 7, 13 | Both drafted, Pacific sets built |
| 9, 10, 12 | Chapters 9 and 10 drafted, sets for 9, 10 and 12 built |
| 11, 14 | Chapter 11 drafted with its sets; 14 not started |

- Draft chapter modules are in `src/videos/ww2/ch_wip/`. The Mac script ignores that folder.
- A chapter moves to `src/videos/ww2/ch/` once it's reviewed (frame sweep, fixes).
- New Blender sets (`blender/sets/c02_*` ... `c13_*`) and period maps (`blender/maps/c*_*`) are committed as they stand.

## Left to do
1. **Finish the chapters:** let the builders finish chapters 3, 4, 8, 12 and 14 and their sweeps.
2. **Review each chapter:** a frame sweep at one frame per 1.5 s. Check that no heads are cut off, main characters
   aren't tiny, sets are dense and well lit, maps are readable, and the serious chapters (10, the bombs in 13) stay
   serious. Fix, then move the chapter from `ch_wip/` to `ch/`.
3. **Chapter sound:** run `audio/chapter_audio.py chNN <voiceDir> <exportDir> audio/mix_chNN.m4a` once each chapter's
   picture is final (it reads that chapter's shots and kicks). Save as `.m4a` (AAC 320k) to keep the repo small.
   - The chapter voice wavs are not in git (about 150 MB). Rebuild them with
     `python3 tools/chapters.py SCRIPT.md <voiceDir>` from the original v1/v2/v3 recordings.
4. **Mac check:** run `./render_blender_mac.sh stills part1` and send stills plus the timing. That confirms the look
   and gives the real seconds per frame.
5. **Render budget:** the full video is about 50,000 frames.
   - At an estimated 7 s/frame (Cycles 16 spp, M4) that is about 4 days of rendering.
   - Once the real speed is measured, tune the samples, bounces and denoiser to the fastest setting with no visible
     loss, and/or render chapter by chapter overnight.
6. **Final:** `./render_blender_mac.sh final all` (resumable; chapter by chapter also works), then watch the whole
   video and fix anything that slipped through.
7. **Shorts:** cut the Shorts listed at the end of `SCRIPT.md` (ask the user about captions for Shorts).

## Commands (on the Mac, in `projects/ww2`)
```bash
./render_blender_mac.sh stills part1      # quick look, one frame per 1.5 s
./render_blender_mac.sh preview ch05      # fast EEVEE check of one chapter
./render_blender_mac.sh final all         # everything, joined into out/WW2_full_final.mp4
```
