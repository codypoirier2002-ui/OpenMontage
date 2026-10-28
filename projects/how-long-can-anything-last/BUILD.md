# BUILD.md: builder contract for "How Long Can Anything Last?" (the Lifespan Column, video 19)

Video 18's ascending ladder engine (`projects/how-heavy-can-anything-get/`) re-dressed in years. **Audio, narration, alignment and
key frames are FIXED** (`build_soundtrack.py`, `align_narration.py`, `process_narration.py`, `artifacts/timeline.json`,
`public/audio/soundtrack.wav`): never edit them. **Every number** (frames, chip boxes, placard windows, meter keys, counter steps)
lives in the generated spec `artifacts/BUILD_SPEC.md` (`python3 docs/channel/scripts/build_spec.py projects/how-long-can-anything-last`)
and in `artifacts/props.json`; this file holds the rules only. Composition **`LifespanColumn`**, 1080x1920 @ 30 fps.

## 1. Pipeline (repo root, in order; python3 = the system one with fontTools, the .venv for build_soundtrack.py)

```bash
python3 projects/how-long-can-anything-last/prepare_media.py --force   # S1-S3 crops (measured boxes, subject asserted in the middle 60 %)
python3 projects/how-long-can-anything-last/sync_scene_plan.py         # scene times, caption pages, placards, verified/forbidden strings
python3 projects/how-long-can-anything-last/build_props.py             # props.json + props.generated.ts, ALL asserts
(cd remotion-composer && npx tsc -p projects/how-long-can-anything-last/tsconfig.json)
(cd projects/how-long-can-anything-last && python3 check_hooks.py scenes shared overlay)
cd projects/how-long-can-anything-last && node stills.cjs --frames 68,139,... --scale 0.5 --out renders/review/<dir>
python3 projects/how-long-can-anything-last/contact_sheet2.py          # after its two stills.cjs runs (see its docstring)
```
Headless shell: `/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`. Render through the
symlink `remotion-composer/projects/how-long-can-anything-last` (CHANNEL_FORMULA step 9, composition `LifespanColumn`). 0.25-scale
segments only for tests; delete test renders.

## 2. Ownership

- **ROOT** (Composition.tsx): `Sky`, `Ladder` (rail, powers every 3 decades, rung ticks + chips, the open PROTON rung, marker),
  `RootDevices` (break, 'forever?' line, readout card), `WindowView` (S1 tortoise, S2 shark, S3 pine, the drawn Sun + red dwarf, the
  drawn detector tank), `Counter`, `Grain`, and the overlay plane (`WindowTags`, placards, tab, captions, CTA).
- **SCENES** (`scenes/u1` sc01-sc06, `scenes/u2` sc07-sc12): emphasis only (rings, the rail-draw glint). Keep `mount` + `SceneProps`;
  hooks first (check_hooks 0); every trigger through `useT()`; never re-author the marker or a root device; no hard-coded frames.

## 3. Rules build_props.py asserts

- `props.audio == soundtrack_report.frames == build_soundtrack.key_frames(timeline)`; motion constants equal build_soundtrack's.
- Lesson 4: climbs' FIRST moving frame = `climb*`, landing ON `*Seat` (<= CLIMB_F); window first visible frame = `windowOpen*`, first
  closing frame = `windowClose*`; the S1 -> S2 -> S3 crossfades start ON `plateSwap*` with the tag swap at the midpoint; break first
  visible ON `breakDraw`; the 'forever?' line first visible ON `foreverDraw`, its label seats ON `foreverSeat` (no SFX: the closing
  sentence is SFX-free); readout first glyph ON `readoutStart`, last ON `readoutEnd`.
- Counter = the power of ten of the active rung's years ON every seat (MAYFLY 0, SHARK stays 2); steps ON every `*Ticks` frame; the
  run 12 -> 33 accelerates and lands 33 ON `protonSeat`; hidden before `mayflySeat`.
- Chips (de-overlapped bottom-up) never under the open window, never overlapping; nothing textual at x >= 912 / y >= 1574; fine
  print >= 24 px. The PROTON is an OPEN (dashed, arrow) rung with 'lower limit' in its chip.
- Lesson 3: meter keys on the START of the page carrying the claim (grades in build_props.py CLAIMS; sublabel 'lower limit' on the
  PROTON and ZEROS keys; FOREVER MAYBE to the end of s5; IDLE at the CTA). Pages <= 2 lines, 3-6 words.
- Lessons 42/52: window states / readout / placards gone >= 6 f before the next tab glide.
- Lesson 60: the marker dims to a ghost (0.3) from `foreverDraw`. Lesson 25: every channel constant from the release.
- Lesson 20: literal scan of `scenes/u*/` against `verified_on_screen_strings`, no `forbidden_on_screen`, no video-16/17/18 devices.

## 4. Known deviations

- The marker barely moves for YOU -> TORTOISE -> SHARK (6 and 4 px on the log scale); the chips stack upward with leaders.
- `script.json` claim_tags are the build's grades; build_props.py keys the meter from its own CLAIMS.
- Mono fold / closing numbers: see `artifacts/soundtrack_report.json` (ending.closing_min_margin_db).
