# BUILD.md: builder contract for "How Small Can Anything Get?" (the Scale Well, video 17)

A copy of video 16 (`projects/how-fast-can-anything-go/`, QA passed) with the visual layer rebuilt. **Audio, narration,
alignment and key frames are FIXED** (`build_soundtrack.py`, `align_narration.py`, `process_narration.py`,
`artifacts/timeline.json`, `public/audio/soundtrack.wav`): never edit them. **Every number** (frames, chip boxes, placard
windows, meter keys, counter steps) lives in the generated spec `artifacts/BUILD_SPEC.md` and in `artifacts/props.json`; this
file holds the rules only. Composition **`ScaleWell`**, 1080x1920 @ 30 fps.

## 1. Pipeline (repo root, in order)

```bash
python3 projects/how-small-can-anything-get/prepare_media.py --force   # S1-S3 crops (measured boxes, subject asserted inside)
python3 projects/how-small-can-anything-get/sync_scene_plan.py         # scene times, caption pages, placards, verified/forbidden strings
python3 projects/how-small-can-anything-get/build_props.py             # props.json + props.generated.ts, ALL asserts
(cd remotion-composer && npx tsc -p projects/how-small-can-anything-get/tsconfig.json)
(cd projects/how-small-can-anything-get && python3 check_hooks.py scenes shared overlay)
cd projects/how-small-can-anything-get && node stills.cjs --frames 29,115,... --scale 0.5 --out renders/review/<dir>
python3 projects/how-small-can-anything-get/contact_sheet2.py          # after its two stills.cjs runs (see its docstring)
```
Headless shell: `/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`. Render
through the symlink `remotion-composer/projects/how-small-can-anything-get` (video 16's BUILD.md §1 has the render command,
with `ScaleWell`). 0.25-scale segments only for tests; delete test renders.

## 2. Ownership

- **ROOT** (Composition.tsx): `Sky`, `Ladder` (rail, decade powers, reference lines + veil, rung ticks + chips, marker),
  `RootDevices` (electron bracket, break, Planck line, readout), `WindowView` (S1/S2/S3 + the drawn atom), `Counter`, `Grain`,
  and the overlay plane (`WindowTags`, `AtomNote`, placards, tab, captions, CTA).
- **SCENES** (`scenes/u1` sc01-sc06, `scenes/u2` sc07-sc12): emphasis only (rings, the rail-draw glint). Keep `mount` +
  `SceneProps`; hooks first (check_hooks 0); every trigger through `useT()` (`T.sfx.*`, `T.rung()`, `T.dev`); never re-author
  the marker or a root device; no hard-coded frames.

## 3. Rules build_props.py asserts

- `props.audio == soundtrack_report.frames == build_soundtrack.key_frames(timeline)`; motion constants equal build_soundtrack's.
- Lesson 4: each SFX on its visual frame: descents' FIRST moving frame = `descend*`, landing ON `*Seat`; window first visible
  frame = `windowOpen*`, first closing frame = `windowClose*`; crossfades start ON `plateSwap*` with the tag swap at the midpoint;
  reference lines fully drawn ON `eyeLine` / `lightLine`; electron in from `electronIn`; break from `breakDraw`; Planck ON
  `planckIn`, glow ON `floorGlow`; readout first glyph ON `readoutStart`, last ON `readoutEnd`.
- Counter = zeros after the decimal point of the active rung's metres ON every seat; steps ON every atom / proton / spin tick;
  the spin 15..34 accelerates and lands 34 ON `spinEnd`; hidden before `sandSeat`.
- Chips never under the open window, never overlapping each other or the electron labels; the readout never covers the marker,
  the Planck line or a chip; nothing textual at x >= 912 / y >= 1574; fine print >= 24 px (superscripts drawn >= 24 px).
- Lesson 3: meter keys on the START of the page carrying the claim (SAND, HAIR MEASURED; EYE PROBABLY; CELL, VIRUS, ATOM,
  PROTON, ELECTRON MEASURED; PLANCK MAYBE to the end of s5; IDLE at the CTA). Pages <= 2 lines, 3-6 words.
- Lessons 42/52: window states / atom note / placards gone >= 6 f before the next tab glide.
- Lesson 25: every channel constant from the release; the CTA swaps in ON `ctaFrame`.
- Lesson 20: literal scan of `scenes/u*/` against `verified_on_screen_strings`, no `forbidden_on_screen`, no video-16 devices.

## 4. Known deviations

- `script.json` claim_tags are still video 16's: the meter grades come from build_props.py CLAIMS (the brief).
- 'And that's about where your eyes give up.' is two pages (8 words); PROBABLY keys on the first.
- Reference labels sit LEFT of the rail; the decade powers they would collide with are hidden while they show.
