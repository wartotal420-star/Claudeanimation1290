# Chapter builder brief: "The ENTIRE History of WW2 [No AI]" (long-form, 16:9, 1920x1080, 30 fps)

Part 1 (cold open + chapter 1) is finished. You build whole chapters (2-14) to the same quality. Read first:
- /home/user/Claudeanimation1290/CLAUDE.md: project lessons. Quality bar: dense, detailed sets, motivated warm/cool
  light, close cameras, characters acting on every line.
- /home/user/Claudeanimation1290/projects/ww2/SCRIPT.md: the script. Your chapter's section has [visual] notes; follow
  them where they're good.

## How a chapter is made
1. **Voice:** `/home/user/ww2/voice/chNN.wav` (already cut). Timings are in `chNN_words.json` ({w, s, e, line}, seconds)
   and `chNN_lines.json` (sentences). The frame count is in `/home/user/ww2/voice/chapters.json`. Frames 0-60 are a
   2.0 s lead-in for the chapter card.
2. **Chapter module:** `/home/user/shorts/src/videos/ww2/ch/chNN.ts`, exporting `CH = makeChapter({...})` (see `chapter.ts`).
   - **Shots:** contiguous, frames local to the chapter (`shots[0].a = 0`, last `.b = total`). Typically 2-6 s each;
     cut on sentences. Use quick cuts on punchlines and slower shots for serious lines.
   - **Card:** `cards: [{ a: 0, b: 60, kind: "chapter", lines: ["CHAPTER N", "TITLE IN CAPS", "years"] }]`, with the
     first shot as an establishing shot under it.
   - **Cameras:** `cams` use `D(set, pos, look, f, f0, rate, {fov, roll}, punch)` (dolly) and `Tr(...)` (track) from
     `story.ts`. Coordinates are set-local three.js: y up, z forward from the camera. Part 1's `CAMS` in `story.ts`
     are the reference for the camera grammar. Vary the moves: low angles, push-ins, tracks, foreground framing.
   - **Lens and shake:** `dof` table (`cInf` 4-16 = blur strength), `kicks` [seconds, strength] on impacts.
   - **Staging:** `stage[id] = (c) => {...}` with `P(c, W_(outfit, i, key), x, y, z, frontOpts, scale)` for
     characters and `F(c, fx)` for effect cards (`fxBomber`, `fxFlame`, `fxStamp`, `fxNewspaper`, `fxMapCut` etc. in
     `toon.ts`). Use `act(t, beats)` for gestures and expressions timed to words (use `wordAt` from `chapter.ts`, or
     the words json), and `talk()` for speaking mouths. Crowds use `crowd(i)` and `trooper(i)` (all varied);
     outfits are in `cast.ts` (MEN, WOMEN, WORKERS, KIDS, OFFICIAL, SOLDIER, HITLER, ...). Part 1's `s1..s28` in
     `cast.ts` are the reference: copy their patterns.
   - **New outfits:** define them in your chapter file from existing `Outfit` fields (`toon.ts`). A character
     builder is adding WW2 figures and features to `toon.ts` (and possibly `cast.ts`) right now: leaders (Churchill,
     Stalin, Roosevelt, Mussolini, Chamberlain, de Gaulle, Truman, Eisenhower, a Japanese PM/general), officer peaked
     caps, Soviet ushanka and pilotka, pilot leather cap with goggles, sailor and navy officer, nurse, a factory
     worker with a bandana, gas mask, Japanese and Soviet soldiers, and new poses (salute-free). Grep `toon.ts` and
     `cast.ts` for them when you stage; if a feature isn't there yet, use what exists. Never edit `toon.ts`,
     `cast.ts`, `story.ts`, `chapter.ts` or `sets.ts`.
   - **Lights:** shot `light` must be one of day, golden, grey, fog, night, interior, void, dusk, gloom. `night: true`
     marks night shots.
3. **Blender sets:** `/home/user/ww2/blender/sets/<name>.py`, one module per set.
   - The shot's `set` string must equal the module name. Prefix every new set with your chapters, e.g. `c02_munich`.
   - Reuse the existing sets (street, front, jungle, warroom, paris, press, bakery, playroom, wallst, atelier,
     beerhall, void) where they fit. Import and read them, but don't edit them.
   - Read `lib.py`, `render_shot.py`, and the kits `ikit.py`, `kit_sbpw.py` and `void.py`'s prop kit (read-only;
     copy helpers into your own files if you need changes).
   - `build(M, D)` returns `{"update": fn(f)}` for per-frame changes (see `paris.py` scroll, `press.py` cash).
   - Coordinates: `lib.T(x, y, z)` maps three (y up) to Blender. Document the layout anchors at the top of each set.
   - Quality bar: as `paris.py`, `bakery.py` and `street.py` (rich props, readable signs, motivated lights, no boxy
     placeholders, no glowing balls as fire, ships and vehicles with real shapes). Must work in Blender 4.5 (preview
     here uses bpy 5.2; avoid 5.x-only API).
4. **Export and check:**
   - Typecheck: `cd /home/user/shorts && npx tsc --noEmit -p . 2>&1 | grep ww2` must print nothing.
   - Export: `PART=chNN npx tsx scripts/export_ww2.ts /home/user/ww2/exp_chNN all 1`.
   - Preview one frame per 1.5 s with a manifest that keeps every 45th frame (see `/home/user/ww2/sweep/sweep.sh`
     for the pattern):
     `nice -n 10 python3 /home/user/ww2/blender/render_shot.py -- <manifest> /home/user/ww2/exp_chNN/cards <out> 8 30`
   - Look at contact sheets (`/home/user/ww2/sweep/sheet.py` shows how). Fix before reporting:
     - heads cut at the frame edge, or main characters as tiny dots;
     - empty or boxy sets, cameras inside walls or crowds;
     - unreadable maps or text, dead time.

## Tone and content rules
- Funny, punchy, RicksClips-style elsewhere. Chapter 10 (Holocaust) and the atomic bombs (chapter 13) are serious:
  no jokes, slow respectful shots, no gore, no cartoon victims played for laughs. For those, use empty spaces,
  railway tracks, piles of shoes and suitcases, candles, photographs, sorrowful faces.
- No swastikas, SS runes or other Nazi symbols anywhere (plain red banners are fine). No Rising Sun war flag (the
  plain Japanese national flag is fine). No saluting poses that read as a Nazi salute.
- Historically sensible: right uniforms, places and years at the level of a pop-history video. Maps must be readable
  and correct (`/home/user/ww2/blender/maps/make_map2.py` and `ne_50m_countries.geojson` can draw period maps).

## Machine
4 CPU cores and 15 GB RAM, shared by 6 builders. Run at most one Blender render at a time, under `nice -n 10`, at
pct 25-30 and 8 samples. Delete big temporary outputs you no longer need. Don't git commit or push; the lead
integrates. Finish with a short report: what you built, which files, the contact-sheet paths, and known issues.
