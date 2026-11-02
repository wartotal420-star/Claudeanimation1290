# Working preferences

- When the user sends a new message (a question or status check) while work is in progress, answer it briefly and
  keep going with the work that was running. A new message is not a request to stop. Only stop when the user
  explicitly says to stop or cancel.
- Keep answers short.
- Work autonomously toward the finished video: make the best decision yourself and keep going. Don't ask the user
  for choices or permission on things you can decide; only involve them for what only they can do (record voice,
  render on their Mac, review).
- Working Remotion setup and known fixes: see `setup/README.md`. Read it before setting up a project.

# Lessons from the first video (Kiska) - apply to every new video
- Dense sets: 10-20 props in every close shot (lamps, signs, clutter); never empty grass or bare rooms.
- Saturated colour and deep darks; fog/haze only as accents (wisps), never washing out whole shots.
- Every scene gets a motivated light source (lamp, window, fire, sunset) with warm/cool contrast and rim light.
- Camera close: mostly close-ups and medium shots, characters fill the frame, low angles, foreground props framing.
- Distinct main characters (outfits, colours, props) that act out every line; no rows of identical standing extras.
- Hook = punchy close-up of the most absurd moment in the first frame.
- Captions: none in long-form (YouTube auto-captions). For Shorts, ask the user.
- Workflow: user records voice (Fish Audio) and renders on their Mac (`projects/<name>/render_mac.sh`, ~1-2 min).
  Have the user render an early preview and send screenshots before the final; check terrain/height functions
  for clamps (a max(h, 0) bug lifted the sea bed to the water line in Kiska).

# Lessons from WW2 part 1 review (user: "way off on detail, quality, lighting")
- Reference quality bar (see user screenshots, RicksClips): richly detailed painted environments (signs with text,
  posters, boards, clutter, worn textures, real architecture), warm multi-source lighting with soft shadows and bounce,
  detailed characters (patterned clothes: plaid, vests, bow ties, scarves; varied hats; props like cigars; varied body
  shapes; expressive faces). Primitive boxes + one two-tone sun light are far below this bar.
- Never: blank box ruins, glowing balls as fire, flat slab ships, blob props (helmet), unreadable maps, crude continents.
- Characters must act on every line (gestures, walking, pointing, reacting); crowds need varied bodies/poses/views.
- Camera: vary moves (tracks, low angles, quick cuts on punchlines); never glide through empty space.
- Frame check: no heads cut at frame bottom, main character never a dot, text never clipped.
- Review every shot with a frame sweep (one frame per 1.5 s) BEFORE asking the user to render.
- Before pushing any script the user will run: compile-check it (python3 -m py_compile / tsc) and run it once here.
- User's Mac: Blender 4.5 (EEVEE engine id is BLENDER_EEVEE_NEXT there); find Blender via ls /Applications/Blender*.app
  or mdfind; scripts must stay compatible with 4.5 (cloud preview uses bpy 5.2).
- Mac speed test (bakery, 1080p): Cycles 64 spp 35 s/frame, EEVEE 15 s/frame (both incl. startup). Prefer Cycles
  (user picked its look); use low spp + denoise + persistent data to get ~6-10 s/frame.
