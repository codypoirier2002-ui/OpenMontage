# BUILD.md: builder contract for "How Heavy Can Anything Get?" (the Weight Column, video 18)

A copy of video 17 (`projects/how-small-can-anything-get/`, QA passed) with the visual layer rebuilt: the log ladder points UP
in kilograms. **Audio, narration, alignment and key frames are FIXED** (`build_soundtrack.py`, `align_narration.py`,
`process_narration.py`, `artifacts/timeline.json`, `public/audio/soundtrack.wav`): never edit them. **Every number** (frames,
chip boxes, placard windows, meter keys, counter steps) lives in the generated spec `artifacts/BUILD_SPEC.md` and in
`artifacts/props.json`; this file holds the rules only. Composition **`WeightColumn`**, 1080x1920 @ 30 fps.

## 1. Pipeline (repo root, in order)

```bash
python3 projects/how-heavy-can-anything-get/prepare_media.py --force   # S1-S3 crops (measured boxes, subject asserted inside)
python3 projects/how-heavy-can-anything-get/sync_scene_plan.py         # scene times, caption pages, placards, verified/forbidden strings
python3 projects/how-heavy-can-anything-get/build_props.py             # props.json + props.generated.ts, ALL asserts
(cd remotion-composer && npx tsc -p projects/how-heavy-can-anything-get/tsconfig.json)
(cd projects/how-heavy-can-anything-get && python3 check_hooks.py scenes shared overlay)
cd projects/how-heavy-can-anything-get && node stills.cjs --frames 42,157,... --scale 0.5 --out renders/review/<dir>
python3 projects/how-heavy-can-anything-get/contact_sheet2.py          # after its two stills.cjs runs (see its docstring)
python3 docs/channel/scripts/build_spec.py projects/how-heavy-can-anything-get
```
Headless shell: `/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`. Render
through the symlink `remotion-composer/projects/how-heavy-can-anything-get` (video 16's BUILD.md §1 has the render command,
with `WeightColumn`). 0.25-scale segments only for tests; delete test renders.

## 2. Ownership

- **ROOT** (Composition.tsx): `Sky`, `Ladder` (rail, powers every 3 decades, rung ticks + chips, marker), `RootDevices`
  (break, universe line, ordinary / dark matter bars), `WindowView` (S1 whale, S2 Eiffel Tower, S3 neutron star, the drawn
  black hole + Mercury's orbit), `Counter`, `Grain`, and the overlay plane (`WindowTags`, `OrbitNote`, `BarsTag`, placards,
  tab, captions, CTA).
- **SCENES** (`scenes/u1` sc01-sc06, `scenes/u2` sc07-sc12): emphasis only (rings, the rail-draw glint). Keep `mount` +
  `SceneProps`; hooks first (check_hooks 0); every trigger through `useT()`; never re-author the marker or a root device; no
  hard-coded frames.

## 3. Rules build_props.py asserts

- `props.audio == soundtrack_report.frames == build_soundtrack.key_frames(timeline)`; motion constants equal build_soundtrack's.
- Lesson 4: climbs' FIRST moving frame = `climb*`, landing ON `*Seat` (length CLIMB_F); the marker does not move for NEUTRON
  STAR or after SGR A*; window first visible frame = `windowOpen*`, first closing frame = `windowClose*`; the S1 -> S2 crossfade
  starts ON `plateSwap` with the tag swap at the midpoint; orbit, break, universe line, ordinary bar first visible ON their key
  frames; the dark bar lands ON `darkSeat` at 5.4 x the ordinary bar with '~5 : 1 · inferred' seating there.
- Counter = the power of ten of the active rung's kg ON every seat; steps ON every `*Ticks` frame; the Earth and spin runs
  accelerate (24 ON `earthSeat`, 53 ON `spinEnd`); hidden before `youSeat`.
- Chips (de-overlapped bottom-up) never under the open window, never overlapping, never above the universe line; the marker
  glow never reaches a label; nothing textual at x >= 929 / y >= 1574; fine print >= 24 px.
- Lesson 3: meter keys on the START of the page carrying the claim (grades in build_props.py CLAIMS). Pages <= 2 lines, 3-6 words.
- Lessons 42/52: window states / orbit note / placards gone >= 6 f before the next tab glide.
- Lesson 60: the marker dims to a ghost (0.3) from `universeIn`.
- Lesson 25: every channel constant from the release; the CTA swaps in ON `ctaFrame`.
- Lesson 20: literal scan of `scenes/u*/` against `verified_on_screen_strings`, no `forbidden_on_screen`, no video-17 devices.

## 4. Known deviations

- The OBSERVABLE UNIVERSE line sits above the SGR A* chip (not at ~y 320): NEUTRON STAR (3 rows) and SGR A* (2 rows) stack
  above SUN and fill the rail's top.
- Rung numbers are mono 26 px (names 28 px) so BLUE WHALE fits beside the open window in two rows; NEUTRON STAR's number is
  split in two rows.
- S2 crops the Eiffel Tower's legs (the full tower is taller than any full-width window crop); the tip is kept.
- `script.json` claim_tags are not used: the meter grades come from build_props.py CLAIMS (the brief).
