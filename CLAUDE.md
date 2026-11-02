# Working preferences

- When the user sends a new message (a question or status check) while work is in progress, answer it briefly and
  keep going with the work that was running. A new message is not a request to stop. Only stop when the user
  explicitly says to stop or cancel.
- Keep answers short.
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
