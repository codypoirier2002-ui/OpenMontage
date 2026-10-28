# BUILD.md: builder contract for "How Fast Can Anything Go?" (Speed Ladder: video 13's ladder engine, re-dressed)

> **THE CLEAN WAVs ARE `assets/audio/narration/clean/s1.wav … s5.wav`** (+ `narration_full.wav`, `process_report.json`),
> made by `process_narration.py` from the assets' untrimmed takes: lead / tail trimmed, **ONE constant gain per section to
> −21.5 LUFS** (s5 true-peak-capped at −22.8; no loudnorm), and the **WIDENED section gaps 1.2 / 1.2 / 1.2 / 1.45 s** inside
> the files (lesson 48: 42.56 s raw vs 49.2 s planned). Nothing cut: every internal pause ≥ 0.2 s sits at punctuation except
> the 0.28 s `[awed]` breath after s4 'Light', KEPT on purpose (lesson 29 asserted with that one listed exception).
> Alignment, every OVERRIDE (section-local seconds), the premix and QA A's onset sweep use these files only (lesson 17). The
> lesson-30 lift on 'way' and the +1.3 dB s5 section gain are in the PREMIX, not in the clean WAVs (§5).

Atelier Remotion composition **`SpeedLadder`**: 1080×1920 @ 30 fps, **1478 frames (49.27 s)** = 0.50 s lead-in + 47.375 s of
narration (gaps inside) up to the release of "way." (**47.74 s, frame 1432**) + a fixed **1.50 s settle** (finished line,
chord at **f1437**). Plan: 49.2 s / 1476 f. Read `art-direction.md`, `scenes.md`, `artifacts/scene_plan.json` first.
**This file and `artifacts/props.json` hold the measured frames** (`scene_plan.json` scene times synced, schema-valid).
The engine is video 13's ladder (`projects/how-hot-can-it-get/`, QA passed: rail, rungs that seat with their numbers, the
zeros counter, the window) re-dressed in night ink + steel with ONE white-cyan accent and ONE red line; the pipeline is video
15's (`projects/how-a-cat-lands/`). No black-body colour, no camera: the rail never moves.

**TWO ASSETS ARE STILL PENDING** (assets_report: the full ElevenLabs connector was denied): the stills S1–S3 and the music
bed M1. The foundation runs without them (placeholder plates, a voice + SFX premix); §4 says exactly what to re-run when
they land. Nothing else changes.

## 1. Layout of the foundation

| path | what |
|---|---|
| `fetch_fonts.py` | Saira Condensed 600/700 (display), IBM Plex Mono 400/500 (data, SLASHED zeros asserted), Bricolage 800, Spline Sans Mono 600, fetched from fonts.gstatic.com (the package's own URLs; ESM asserted); every verified string + placard checked in all look faces (· ~ % : ( ) ' × ° = ok; → ≈ ✓ in no face: drawn); placard fit; writes `shared/metrics.generated.ts` |
| `process_narration.py` | THE CLEAN WAVs (above) + the film-length estimate (asserted ≥ 45.2 s) |
| `sweep_onsets.py` | onset sweep helper: candidates, `--strip`, `--png` spectrogram strips (1 px = 1 ms) |
| `align_narration.py` | faster-whisper small.en (decoded by ffmpeg to a 16 kHz float32 ARRAY: PyAV is broken here) → script words; **62 OVERRIDES + 44 CONFIRMED = all 106 words hand-measured** on 5 ms band tables (§10); anchors from `narration_by_scene`; scene windows = anchor onset − 2 f → `artifacts/timeline.json` (**`way_end_frame` / `way_end_seconds`**, the only `*_end_frame` key), `alignment_report.json`. Run with `HF_HUB_OFFLINE=1` |
| `build_soundtrack.py` | narration (+ lifts) + SFX (+ the level-evened, ducked bed when `assets/music/bed_raw.mp3` exists: its LAST TONIC found from the audio, landing at release + 0.15 s) → `public/audio/soundtrack.wav` (1478 × 1600 samples), `artifacts/soundtrack_report.json` (`ending.closing_min_margin_db` from the stems once the bed exists; null + note until then). **Owns the KEY FRAMES `K`** (`key_frames()` → `props.audio` → `T.sfx.*`) and the motion constants |
| `prepare_media.py` | S1 / S2 / S3 → `public/stills/` (**PLACEHOLDER cards now**, `placeholder: true` in `artifacts/media_report.json`), `renders/review/crops.jpg`; when the stills land: measured crops (lesson 9), feature points asserted inside (lesson 39) |
| `sync_scene_plan.py` | syncs `scene_plan.json`: times, safe areas as built, placard 3's lesson-32 rewording, still status, `foundation_changes`; jsonschema |
| `build_props.py` | caption pages (26; lesson-3 re-flows), meter, placards (5), **the ladder curves** (§6: the marker's climbs + the asymptotic creep, rungs, counter, window, YOU tag, beam, energy, nines, the lesson-42 exits) → `artifacts/props.json`, `props.generated.ts`. All asserts in §10 |
| `theme.ts` | `FONT`, palette `C` (marker white-cyan ONLY on the marker / streaks / beam; wall red ONLY on 'c'), `glass()`, `rgba()`, easings `E`, layout `L` (rail, win, counter, you, orbit, massLabel, energy, readout, gap, placard, tab, slab), `railY(L)` |
| `time.ts` | `useT()`: `at/end/word`, `scene/section`, `sfx.*`, `motion`, `ladder(f)`, `railY(L)`, `cY`, `rungs/rung(id)`, `counter(f)`, `win(f)`, `plate(id,f)`, `tagAt(f)`, `you(f)`, `beam(f)`, `energy(f)`, `nines(f)`, `mass(f)`, `orbit(f)`, `seat`, `driftFrame`, `loopFrame`; `prog`, `remap`, `lerp`, `sample` |
| `shared/` | ROOT: `Sky`, `Ladder` (rail, decade ticks, the red 'c', rung ticks + label CHIPS, the marker + streaks, the gap bracket), `Counter` (ZEROS), `Window` (`WindowView`, `WindowTags`; `WindowFrame` exported), `Grain`, and `Devices.YouTagLive` (root). ENGINE for units (in `Devices.tsx`): **`PressureRing`, `OrbitInset`, `LightBeamLive`, `MassLabelLive`, `EnergyLive`, `NinesReadoutLive`**; `Icons` (`Arrow`, `CurvedArrow`, `ArrowLabel`, `WalkerIcon`, `SeatedIcon`), `Type` (`measure`, `fitSize`, `Rich`, `Label`, `hatch`), `noise` |
| `overlay/` | kit: `Captions` (no tones: `CaptionTone = "plain"`), `HonestyTab`, `PlacardRail` (+ `SettleCta`, two-line CTA), `Tag` (`SceneTag`; the kit `DrawnTag` is NOT mounted: every drawing carries its own tag) |
| `scenes/` | `index.ts`, `_stub.tsx`, **`scenes/u1/`** (sc01–sc06) and **`scenes/u2/`** (sc07–sc12): one STUB per scene with the FOUNDATION DEMOS (the engine mounts) - replace the stub labels, keep the engine mounts (§7) |
| `contact_sheet2.py` | contact sheet 2 → `renders/foundation_sheet.jpg` |

Rebuild order after any narration change: `process_narration.py` → `align_narration.py` → `build_soundtrack.py` →
`sync_scene_plan.py` → `build_props.py` → tsc → stills (from the repo root, e.g. `HF_HUB_OFFLINE=1
python3 projects/how-fast-can-anything-go/align_narration.py`). `prepare_media.py [--force]` only when the plates change
(then `build_props.py`). `fetch_fonts.py` only for a new face / string. **After a scene edit that adds a literal, rerun
`build_props.py`** (its literal scan covers `scenes/u*/`).

Render **through the symlink** `remotion-composer/projects/how-fast-can-anything-go`. **The headless shell on this machine
is `/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`** (CHANNEL_FORMULA's
`…-1194/…/headless_shell` does not exist here; `stills.cjs` / `still.sh` already point at the 1243 one):

```bash
cd remotion-composer && npx remotion render projects/how-fast-can-anything-go/index.tsx SpeedLadder ../projects/how-fast-can-anything-go/renders/<raw>.mp4 \
  --config=projects/how-fast-can-anything-go/remotion.config.ts --props=../projects/how-fast-can-anything-go/artifacts/props.json \
  --concurrency=3 --crf=18 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell \
  --public-dir=../projects/how-fast-can-anything-go/public          # add --scale=0.25 --frames=a-b for segment / test renders
# stills (bundle once, deleted after): cd projects/how-fast-can-anything-go && node stills.cjs --frames 0,300 --scale 0.5 --out renders/review/<unit>
#                                      node stills.cjs --frames ... --layers picture   (no overlay plane)
```

Typecheck: `cd remotion-composer && npx tsc -p projects/how-fast-can-anything-go/tsconfig.json` (clean). Hooks: `cd
projects/how-fast-can-anything-go && python3 check_hooks.py scenes shared overlay` (0). Disk: 0.25-scale segments only,
stills at 0.5, delete your test renders, never leave `/tmp/remotion-webpack-bundle-*`.

## 2. Scene contract

```tsx
// scenes/u1/YouAreFast.tsx
export const mount: Mount = { pre: 0, post: 0, z: 1 };                     // frames mounted before from / after to; z
export const YouAreFast: React.FC<SceneProps> = ({ from, to }) => { ... }; // the PICTURE (above the rail, under window + counter)
export const Overlay: React.FC<SceneProps> = ({ from, to }) => { ... };    // OPTIONAL: labels / tags on the overlay plane
```

- **Build ONLY inside your own `scenes/uN/`.** Keep file names, export names and `mount`. Helper files in your folder are
  fine (never import across units). Root, `shared/`, `overlay/`, `time.ts`, `theme.ts`, `types.ts`, the Python scripts and
  `scenes/index.ts` are foundation-owned: **request changes through §7.** Delete `<StubLabel>`; KEEP the engine mounts the
  stubs show (they ARE the plan's devices; add emphasis around them).
- Scenes are mounted by **absolute** frame windows (no `<Sequence>`); `useCurrentFrame()` is the absolute frame.
- **ROOT vs UNIT.** **THE ROOT OWNS THE LADDER**: the sky, the rail with its decade ticks and numbers and 'km/h · log scale',
  the red 'c' line + 'c', every rung tick + label chip (seating with its number when the marker arrives), the MARKER and its
  streaks, the gap bracket + 'the gap', the YOU tag (`<YouTagLive/>`, root because it persists sc05 → sc12 across both units),
  the WINDOW (S1 / S2 / S3) and its ONE tag, the ZEROS counter, placards, tab, captions, CTA, grain. **UNITS OWN THE
  PER-SCENE ACTION**, built from the engine: the pressure ring (sc04), the orbit inset (sc05), the plate labels (sc06 'Parker
  Solar Probe · NASA', sc07 'falling toward the Sun' + arrow), the light beam (sc08–sc09), 'anything with mass' (sc09–sc10),
  the ENERGY NEEDED bar + curve (sc10), the LHC readout (sc11–sc12), and their own emphasis.
  Layer order: sky → ladder → YOU tag → **scene pictures** → window → counter → grain → overlay plane (window tag → scene
  Overlays → placards → tab → captions → CTA). **Your pictures are UNDER the window and the counter; anything that must
  sit over the window (the plate labels) goes in your `Overlay`.**
- **THE MARKER IS NEVER RE-AUTHORED IN A SCENE.** Its position is `props.ladder.markerL` (build_props.py; §6). You may draw
  around it (rings, arcs, labels with leaders). You may NOT move it, draw a second marker, or let anything touch the 'c'
  line. A position change = a §7 request (the asserts in §6 must keep holding).
- **Hooks at the top of every component, before ANY early return.** `check_hooks.py` (0) AND a real 0.25-scale render of
  your range before hand-back (lesson 1).
- **Every trigger goes through `useT()`** (`T.at("s2","thousand")`, `T.sfx.jumpStart`, `T.scene("sc05")`, `T.ladder(f)`).
  Never hard-code a frame or a second. A beat that needs a sound or a new key frame = a §7 request.
- **SFX on the visible frame (lessons 4, 14, 22, 41):** a key frame is the frame an element is **fully** landed / lit / seated;
  seat with `T.seat(f, T.sfx.xxx, T.motion.SEAT_F, dropPx)` (gravity ease-in, still moving on seat − 1). Check seat − 2 /
  seat − 1 / seat stills. The X1 whooshes sit on the FIRST MOVING frame of a climb (`climb*`, `jumpStart`, `railDraw`); X3
  ticks on counter steps / bar steps / digit landings; X2 on the SOUND seat; X5 on the beam's first frame; X6 on the gap.
- **Safe areas:** no text at y ≥ 1574 or x ≥ 929 (text ends ≤ 912), nothing above y 192 (the stub card there is temporary).
  Root-reserved: **rail x 180–320** (spine 250; decade numbers right-aligned at x 224, the longest reaching x 86), **rung
  chips x 280–572** at their rungs (WALK y 1026, CHEETAH 925, FALCON 879 + chip, SOUND 840 (de-overlapped up to ~793),
  EARTH 690, PARKER 627 (two-line), LIGHT 380), **WINDOW x 580–920 y 440–893** (sc02–sc03, sc06–sc07, with its tag
  bottom-right inside), **COUNTER x 640–920 y 220–340** (the chip right-aligned at 920), YOU tag x 120–224 at WALK then
  EARTH, 'km/h · log scale' x 140–370 y 1088–1112, placard rail y 1124–1204, tab y 1236–1290, slab x 140–940 y 1296–1488.
  Unit zones: **the window's column x 580–920 y 440–893 while the window is CLOSED** (sc01, sc04–sc05 (orbit inset x 600–920
  y 460–800), sc08–sc12 (energy curve x 690–920 y 440–640, readout x 600–920 y 460–600)); the energy bar x 600–650 from y 1080
  up; the mass label chip x 280–545 y 483–517 (fixed, with a dotted leader); right of the rail above PARKER (y 400–585,
  x 280–560) is free from sc08 (the beam / wall emphasis goes there).
- **Strings:** verbatim from `scene_plan.metadata.verified_on_screen_strings`, nothing from `forbidden_on_screen` ('faster
  than light', 'warp', 'fastest animal', 'snail', 'the falcon is the fastest', 'light speed is possible'). Route every
  on-screen string through a `text="…"` / `text: "…"` / `*TEXT|LINE|LABEL|NUM* = "…"` literal (build_props.py scans them) or
  through `T.labels.*` (axis, zeros, ai, drawn, c, you, gap, mass, energy, speed, energyAxis, lhc, nines, probe, falling,
  cited). No '→' glyph: `<ArrowLabel text="a -> b"/>` draws it; `<Arrow>`, `<CurvedArrow>`; '~' via `<Rich>`. Labels ≥ 28
  px, fine print ≥ 24 px (lesson 31). **Numbers on screen: only the rung chips, the decade ticks, the counter and the
  readout (root / engine); never write a number the brief does not hold.**
- **COLOUR RULES:** Marker white-cyan `C.marker` ONLY on the marker, its streaks and the light beam; Wall red `C.wall` ONLY
  on the 'c' line and its label. Everything else steel / bone / night ink / chip. No temperature colours, no gradients of
  colour. Captions: plain only.
- **No blend modes under fading parents** (lesson 24).
- **Honesty:** AI media only through the root window (tagged 'AI impression' by the root; PLACEHOLDER cards until the
  stills land). Every drawing carries 'drawn · not to scale' ≥ 24 px (the orbit inset and the energy curve do it
  themselves; add it to anything else you draw that depicts a thing). The FALCON rung carries the hatched PROBABLY chip
  'commonly cited' (root). Lesson 42: anything tied to one claim is gone ≥ 8 f before the next claim's tab page (§3 tab
  keys): the engine curves already do this for the orbit inset (gone 584 < PROBE page 592), the mass label and the energy
  bar (gone 1197 < LHC page 1205); your own additions must follow the same exits.

## 3. Frame table (measured; boundary = anchor onset − 2 f for EVERY scene after sc01)

| scene | component · unit | frames | dur | narration (word onset frames) |
|---|---|---|---|---|
| sc01 | Walk · U1 | 0–99 | 99 f · 3.30 s | You 16 · walk 21 · at 29 · about 32 · five 42 · kilometres 57 · an 67 · hour. 75 |
| sc02 | Cheetah · U1 | 99–169 | 70 f · 2.33 s | A 101 · cheetah 105 · sprints 119 · at 132 · about 134 · a 140 · hundred. 142 |
| sc03 | Falcon · U1 | 169–286 | 117 f · 3.90 s | A 171 · diving 175 · falcon 186 · hits 196 · nearly 210 · four 219 · hundred. 233 |
| sc04 | Sound · U1 | 286–393 | 107 f · 3.57 s | Sound 288 · outruns 300 · them 316 · all 325 · at 334 · over 338 · twelve 347 · hundred. 352 |
| sc05 | YouAreFast ★ · U1 | 393–590 | 197 f · 6.57 s | But 395 · sitting 399 · still, 405 · you're 436 · doing 441 · over 448 · a 453 · hundred 459 · thousand, 478 · riding 504 · Earth 517 · around 525 · the 535 · Sun. 536 |
| sc06 | Parker · U1 | 590–707 | 117 f · 3.90 s | The 592 · fastest 593 · thing 610 · we've 621 · ever 632 · built, 642 · the 660 · Parker 664 · Solar 675 · Probe, 684 |
| sc07 | Falling · U2 | 707–873 | 166 f · 5.53 s | reached 709 · nearly 719 · seven 730 · hundred 740 · thousand, 764 · falling 792 · toward 807 · the 815 · Sun. 818 |
| sc08 | Light · U2 | 873–952 | 79 f · 2.63 s | Light 875 · does 890 · over 899 · a 908 · billion. 920 |
| sc09 | Wall · U2 | 952–1025 | 73 f · 2.43 s | And 954 · nothing 958 · with 969 · mass 978 · can 993 · catch 997 · it: 1006 |
| sc10 | Energy · U2 | 1025–1203 | 178 f · 5.93 s | the 1027 · closer 1030 · you 1040 · get, 1046 · the 1062 · more 1067 · energy 1074 · each 1085 · step 1090 · costs, 1101 · without 1123 · end. 1141 |
| sc11 | LHC ★ · U2 | 1203–1358 | 155 f · 5.17 s | The 1205 · Large 1209 · Hadron 1221 · Collider 1235 · pushes 1253 · protons 1265 · to 1285 · within 1286 · a 1296 · hair 1299 · of 1315 · light 1322 · speed. 1329 |
| sc12 | NeverAllTheWay · U2 | 1358–1478 | 120 f · 4.00 s | Close. 1360 · But 1394 · never 1399 · all 1409 · the 1418 · way. 1420 (release **1432**; settle 1432–1478) |

Sections (files incl. their gaps): s1 15–287 · s2 287–591 · s3 591–874 · s4 874–1204 · s5 1204–1436.

**Key frames** (`T.sfx`; SFX already on them; **root** = the root draws it; **curves** = props.ladder etc.):

| scene | beats |
|---|---|
| sc01 | dim rail + the marker at WALK + counter '0' from **0** (root); the rail DRAWS bright from `railDraw` **16** (X1 onset; root); WALK chip + tick SEAT ON `walkSeat` **21** (root); **U1 demo: a walker icon beside the WALK chip** |
| sc02 | window first visible ON `windowOpen1` **99** (S1 placeholder, 'AI impression'; root); marker climbs from `climbCheetah` **106** (X1 onset) and ARRIVES ON `cheetahSeat` **142** (chip seats; root); counter 0 → 1 → 2 ON `cheetahTicks` **136 · 142** (X3; root) |
| sc03 | S1 → S2 crossfade 169–181 from `plateSwap` **169**, **tag hard cut at 175** (root); climb from `climbFalcon` **197** (X1) → `falconSeat` **233** (chip + hatched 'commonly cited'); window closes `windowClose1` 278 → 286 |
| sc04 | climb from `climbSound` **316** (X1) → `soundSeat` **352** (chip, X2 thump, counter 3); **U1: `<PressureRing from={T.sfx.soundSeat}/>`** (24 f) |
| sc05 ★ | YOU tag SEATS at WALK ON `youSeat` **405** (no SFX; root); **the tag + the marker JUMP from `jumpStart` 441 (X1 big) and ARRIVE at EARTH ON `earthSeat` 478** (chip; counter 4 → 5 ON `earthTicks` 472 · 478, X3); **U1: `<OrbitInset/>` in from `orbitIn` 504, out 572–584 (`orbitOut`)** + the jump's emphasis |
| sc06 | window ON `windowOpen2` **590** (S3 placeholder; X4 hum start-aligned, soft; root); marker holds at EARTH, YOU stays there; **U1 Overlay: 'Parker Solar Probe · NASA' (`T.labels.probe`) on the plate from `probeLabel` 664** |
| sc07 | climb from `climbParker` **728** (X1) → `parkerSeat` **764** (two-line chip); **U2 Overlay: `<Arrow>` on the plate + 'falling toward the Sun' from `fallArrow` 792**; window closes `windowClose2` 865 → 873 |
| sc08 | **U2: `<LightBeamLive/>`: the beam races the rail from `beamStart` 908 (X5 start) and reaches 'c' ON `lightSeat` 920**; LIGHT chip seats + the 'c' line lights red (`cLit`) ON 920 (root); counter 5 → 9 ON `lightTicks` 902 · 908 · 914 · 920 (X3); the beam fades 924–950 |
| sc09 | marker leaves PARKER ON `wallStart` **958** and climbs toward 'c', slowing (curves, no SFX); **U2: `<LightBeamLive/>` (tail) + `<MassLabelLive/>` from `massLabel` 958** |
| sc10 | marker inches up (curves); **U2: `<MassLabelLive/>` + `<EnergyLive/>`: in ON `energyIn` 1027, the bar grows from `barStart` 1074 (X3 ticks 1074 · 1099 · 1117 · 1129 · 1136 · 1141, accelerating) OFF the top ON `barOff` 1141; both out 1185–1197 (`energyOut` = `massOut` 1197)** |
| sc11 ★ | **U2: `<NinesReadoutLive/>` SEATS ON `readoutSeat` 1235 (no SFX); '99.9999991 %' lands one glyph per `digitTicks` 1253 · 1257 · … · 1289 (X3 ×10)**; the marker's creep ENDS + the gap bracket 'the gap' ON `creepEnd` = `gapBracket` **1299** (X6 tink; root) |
| sc12 | **NO SFX from 'But' (`closingStart` 1394)**; release `wayEndFrame` **1432**; chord `chordFrame` **1437**; CTA ON `ctaFrame` **1436** (root); tab IDLE from 1436; **every channel constant from 1432** |

Captions: 26 pages (`props.captionPages`). Placards: 2–286 (cheetah / falcon) · 292–590 (sound / Earth) · 596–873 (Parker)
· 879–1203 (c) · 1209–1432 (CERN). Honesty tab (lesson 3, page starts): IDLE 0 · MEASURED 16 (WALK) · pulse 101 (CHEETAH)
· **PROBABLY 171 (FALCON)** · MEASURED 288 (SOUND) · pulse 395 (ORBIT) · pulse 592 (PROBE) · pulse 875 (LIGHT) · pulse 954
(WALL) · pulse 1205 (LHC) · IDLE 1436 (the settle).

## 4. Assets and how they are used (and what is PENDING)

| asset | use |
|---|---|
| **S1** plate_cheetah | sc02 (window x 580–920 y 440–893); **PLACEHOLDER** card until generated |
| **S2** plate_falcon_dive | sc03, crossfades in over S1; **PLACEHOLDER** |
| **S3** plate_parker_probe | sc06–sc07; **PLACEHOLDER** |
| narration | §0; in the premix: s5 +1.3 dB constant (its TP-capped gain left it 1.3 dB under the others; voice-lane voiced RMS now s1 −19.9 · s2 −19.9 · s3 −20.0 · s4 −20.2 · s5 −20.5 dBFS), 'way.' +7 dB (§5) |
| music | **PENDING** (M1): the premix is voice + SFX; the bed is picked up automatically (below) |
| SFX | X1–X6, §11 |

**When the stills land** (`assets/images/plate_cheetah.png`, `plate_falcon_dive.png`, `plate_parker_probe.png`, 9:16 2K):
count legs / wings / tails at 4x (lesson 39), write the measured crop box (the window's 3:4 aspect; lesson 9) and the
feature points into `prepare_media.py PLATES`, then from the repo root:

```bash
python3 projects/how-fast-can-anything-go/prepare_media.py --force && python3 projects/how-fast-can-anything-go/build_props.py
# then re-render the sc02 / sc03 / sc06 / sc07 stills; nothing else moves
```

**When the bed lands** (`assets/music/bed_raw.mp3`; optionally `assets/music/music_qa.json` with `last_tonic_attack_s`
when the music QA measured it), from the repo root:

```bash
python3 projects/how-fast-can-anything-go/build_soundtrack.py && python3 projects/how-fast-can-anything-go/build_props.py
# the key frames do not change (no visual moves); build_props only re-checks soundtrack_report; then re-render
```

`build_soundtrack.py` then: finds the LAST TONIC from the audio (lesson 26), trims the head so it lands 0.15 s after
'way.' (snapped to a detected attack within ±0.4 s when that costs ≤ 8 cents, else an exact trim), evens the level on 2 s
windows, sets the bed to −19 LUFS, ducks −12 dB under speech, −13 dB more from 'But' (lesson 44), −5 dB more under 'way' +
a +3 dB 300–4000 Hz lift on the word, releases to the chord, lifts the ring-out +5 dB, enforces no 100 ms window under −42
dBFS (lesson 5), fades the last 0.6 s (lesson 43) and ASSERTS the closing sentence ≥ +12 dB over the bed in 300–4000 Hz on
every word, writing `ending.closing_min_margin_db` (lesson 49) and every SFX hit ≥ +4 dB over the bed in the phone band.

## 5. The ending (finished line)

- "Close. But never all the way." is released at **f1432** (47.74 s; the end of 'way'). **'way.' +7.0 dB** constant broadband
  on the voice lane (raised-cosine 40 ms in / 30 ms out, not a limiter): qa_auto's lesson-30 metric (loudest 100 ms of 'way'
  vs the median of its sentence's words) **9.5 → 2.5 dB under** (≤ 3 asserted). + −5 dB extra duck and a +3 dB 300–4000 Hz
  lift on 'way' (both live when the bed exists).
- **Closing duck −13 dB from 'But'** (lesson 44), ramped in from 'But' − 0.55 s and full from 'But' − 0.15 s.
- **Settle 1432–1478 (46 f):** chord at **47.89 s (f1437) = release + 0.15 s** (the bed's last tonic lands there once it
  exists; the end fade is applied to the bed, so the voice-only premix ends in silence by construction). **Every root channel
  is constant from 1432** (asserted); grain freezes on frame 0's seed. The picture: the full ladder with all seven chips, the
  marker 14 px under 'c' with the gap bracket + 'the gap', the YOU tag at EARTH, the counter at 9, the LHC readout; slab
  "What's the fastest thing / you've ridden?" (two lines); tab IDLE. **No unit element may change after 1432.** The last
  frame ≠ frame 0 (no loop export built).

## 6. Shared helper APIs (all frames absolute)

```tsx
const T = useT();
T.at("s2","thousand"); T.end("s5","way"); T.scene("sc05"); T.sfx.jumpStart; T.sfx.digitTicks[i]; T.motion.SEAT_F
T.ladder(f) -> { L, y, vis, streak, cLit, gap, railDraw }   // the marker: log10(km/h) + its screen y; T.railY(L); T.cY (380)
T.rungs / T.rung("earth") -> { name, num, lines, kmh, L, seat, probably, chip }   T.counter(f) -> { value, alpha }
T.you(f) -> { L, y, alpha }   T.beam(f) -> { progress, alpha, y }   T.energy(f) -> { vc, gamma, barH, alpha }
T.nines(f) -> { count, alpha, shown }   T.mass(f) / T.orbit(f) -> 0..1   T.win(f)   T.plate("S1"|"S2"|"S3", f)   T.tagAt(f)
T.seat(f, seatFrame, frames=8, dropPx=18) -> { k, y, opacity, seated, visible }
// ENGINE (shared/Devices.tsx; every state from the root curves, so two mounts always agree):
<PressureRing from={T.sfx.soundSeat}/>   <OrbitInset/>   <LightBeamLive/>   <MassLabelLive/>   <EnergyLive/>   <NinesReadoutLive/>
<Arrow/> <CurvedArrow/> <WalkerIcon/> <SeatedIcon/> (svg)   <ArrowLabel x y text="a -> b"/> (HTML)   <Label/> <Rich/> (Type)
<WindowFrame open>…</WindowFrame>   // the window look for YOUR drawings only (never AI media)
<SceneTag x y enter exit text variant/>  // in your Overlay
// ROOT ONLY (never mount in a scene): Sky Ladder YouTagLive WindowView WindowTags Counter Grain PlacardRail HonestyTab Captions SettleCta
```

**The ladder's curves, by construction (build_props.py, asserted):** the marker's L climbs rung by rung on sine eases that
START on `climb*` (the X1 onset) and END exactly ON each seat (WALK 0.699 → CHEETAH 2.0 → FALCON 2.591 → SOUND 3.092 → EARTH
5.029 → PARKER 5.840), then an out-cubic creep from `wallStart` to `creepEnd` toward **L_final = L_c − 14 px / ppd** (ppd =
77.49 px per decade): the marker moves 114 px through sc10 and still creeps ~5 px in sc11. **railY(markerL) ≥ cY + 14 on EVERY
frame** (the 6 px marker never touches the line; the gap is drawn, not to scale: 0.999999991 c is 4e-9 decades). The counter
equals floor(log10) of the seated rung on every seat. ZEROS steps 0→1→2 (136, 142), 3 (352), 4→5 (472, 478), 6→7→8→9
(902–920). The energy bar: γ(x) = 1 + 0.5(e^{4.8x} − 1), barH = 19.9 (γ − 1) px, strictly accelerating, OFF the top ON
'end'. The gap bracket spans cY → the marker (14 px) from 1299.

## 7. Unit split for 2 parallel scene builders and hand-offs

| unit | scenes | frames | owns (picture / overlay) |
|---|---|---|---|
| **U1 walk → cheetah → falcon → sound → YOU (HERO) → Parker window** | sc01–sc06 (`scenes/u1/`) | **0–707** | sc01 a walker beside WALK (demo) + rail-draw emphasis; sc02–sc03 climb emphasis (the plates are root; never redraw animals); sc04 `<PressureRing/>` ON `soundSeat` (demo) + a sound-wave hint; **sc05 HERO**: `<OrbitInset/>` (demo; keep) + the jump's emphasis (an arc / trail from WALK to EARTH between 441 and 478, a 'YOU' callout is root); sc06 Overlay `SceneTag` 'Parker Solar Probe · NASA' from `probeLabel` (demo; keep) |
| **U2 falling → light → wall → energy → LHC (HERO) → ending** | sc07–sc12 (`scenes/u2/`) | **707–1478** | sc07 Overlay: the `<Arrow>` on the plate + 'falling toward the Sun' from `fallArrow` (demo; refine the arrow's path to point at the Sun in the plate once S3 exists); sc08–sc09 `<LightBeamLive/>` (keep in both) + a 'c' wall flash emphasis ON 920 (red ONLY on the line); sc09–sc10 `<MassLabelLive/>`; sc10 `<EnergyLive/>` (keep); sc11–sc12 `<NinesReadoutLive/>` (keep in both), the creep's emphasis ON 1299; constant from 1432 |

Seams (agree with a shared still: compare `from − 1` vs `from`):

| seam | outgoing → incoming | both sides must match |
|---|---|---|
| **707** sc06 → sc07 | U1 → U2 | the window (S3) + its tag are root; the marker holds at EARTH (curves); U1's 'Parker Solar Probe · NASA' tag exits ON 707 (the demo's `exit={to}`), U2's own labels start at `fallArrow` 792 or later; nothing of U1 may show at 707 |
| **1203** sc10 → sc11 | U2 internal | the mass label + energy are already gone (1197); the readout seats 1235 |
| **1358** sc11 → sc12 | U2 internal | the readout: same component, same props at 1357 / 1358 |
| **0 / 1477** | — | NOT equal by design (§5) |

A scene drawing past its `to` (inside its `post`) draws ONLY its own outgoing elements. All `mount.post` are 0; ask (§7)
for one. Unit-internal seams: 99, 169, 286, 393, 590 (U1); 873, 952, 1025, 1203, 1358 (U2).

### §7 hand-off protocol (how to request a shared change)

1. Builders **never edit** `shared/`, `overlay/`, `time.ts`, `theme.ts`, `types.ts`, `Composition.tsx`, `Root.tsx`,
   `scenes/index.ts`, `props*.{json,ts}` or any Python script. Never touch the other unit's folder.
2. To request: send the lead ONE message headed `§7 REQUEST uN → foundation` with: what (a key frame, a curve change, a root
   channel, a glyph, a helper prop, a new verified string), why (the beat / the claim), the exact frames, and the still that
   shows the problem (`renders/review/uN/...`). Seam requests name both units.
3. The lead relays it (SendMessage) or applies it, reruns the chain (§1), tsc, `check_hooks.py`, re-renders the affected
   stills, and replies to every unit whose frames moved (lesson 19).
4. Until the answer lands, build against the current props.

## 8. Quality bar (each unit self-checks before hand-back)

- tsc clean; `check_hooks.py scenes shared overlay` = 0; `build_props.py` passes (literal scan); stills of ≥ 4 frames per
  scene + every seam's last / first frame, LOOKED at; seat − 2 / − 1 / seat stills for every seated element (lesson 22); one
  0.25-scale segment render of your range (`--frames=a-b`, exit 0); seam PSNRs reported.
- Every visual landing ON its `T.sfx` frame. Strings verbatim; no text at y ≥ 1574 / x ≥ 929; no '→' glyph; every drawing tagged.
- Colour rules on every frame; nothing of yours over the window or the counter except Overlay labels; nothing touches 'c'.
- `stills.cjs` cleans its bundle; delete your test renders (disk).

### §QA (after the render)

After the master (`docs/channel/scripts/finish_master.sh`), the orchestrator runs
**`python3 docs/channel/scripts/qa_auto.py projects/how-fast-can-anything-go`** first (it reads `timeline.json` `way_end_*`,
`props.json`, `soundtrack_report.json`; scipy was pip-installed for it in this container); fix every FAIL before any QA
agent. Until the bed lands, 'audio floor' FAILs and 'last word over bed' WARNs by construction (no bed).

## 9. Divergences from the scene plan

- Film **1478 f (49.27 s)**, not 1476: section gaps widened (1.2 / 1.2 / 1.2 / 1.45 s); all 12 windows re-timed.
- **ONE window box x 580–920, y 440–893** (portrait 3:4) instead of x 470–920 y 420–900 (it covered the EARTH / PARKER chips).
- **Rung labels are chips** (name Saira 700 + number Plex Mono 500, slashed zeros); **EARTH and PARKER are two-line chips**
  (name over number) so they fit beside the open window; the strings are the verified ones (asserted).
- **S1–S3 are placeholders and M1 is pending** (§4). The chain, the stills and the premix run without them.
- **Placard 3 reworded** (lesson 32): 'Parker Solar Probe: ~692,000 km/h (Dec 2024)' + fine print "NASA's figure as reported
  by Space.com · speed from falling toward the Sun" (the brief holds NASA's figure only through reports).
- Caption pages re-flowed (s1, s2, s4, s5) so every claim starts its own page; the CTA on two lines.
- **The YOU tag is root-owned** (persists sc05 → sc12 across both units); 'the gap' label sits under 'c' left of the rail.
- **ZEROS = floor(log10) of the rung's number** (the digits after the first: 1,235 → 3, as the plan's 'counter 3'); it steps
  on X3 ticks ending ON each seat; no X3 under the SOUND seat (X2 is there).
- **The gap under 'c' is drawn** (14 px marker-centre-to-line, asserted on every frame); the X6 tink sits on 'hair' (1299),
  1.4 s before the closing sentence, as the plan allowed.
- **'anything with mass' is a fixed chip** (x 280, y 500) with a dotted leader to the marker (riding the marker would collide
  with the PARKER / LIGHT chips).
- The s4 breath after 'Light' (0.28 s) is kept; nothing cut (lesson 29).
- The headless shell path differs from CHANNEL_FORMULA (§1).

## 10. Foundation build log: lessons applied

- **Hooks (1):** 0 violations (28 files); a full-length 0.25-scale test render passed (§12). **Onsets (2, 13, 17):** all 106
  words hand-measured on the clean WAVs (5 ms band tables, wider tables on every doubtful boundary); Whisper was off by up
  to 5.5 f: s4 'can' sat on the s of 'mass' (+5.3 f), s4 'over' on the z of 'does' (+4.0), s4 'you' on the s of 'closer'
  (+4.0), s2 'Earth' in 'riding' (+3.8), s3 'built,' in 'ever' (+3.8), s1 'nearly' on the t of 'hits' (+3.7), s3 'toward'
  in 'falling' (+3.4), s4 'costs,' in its own vowel (−3.4), s5 'to' on the s of 'protons' (+3.3), s3 'the' (2nd) in
  'toward' (+3.2), s3 'nearly' in the ch of 'reached' (+3.1), s4 'the' (1st) in the pause (+3.2). This voice re-attacks
  vowel-initial words with a glottal stop after a vowel ('over', 'Earth', 'energy', 'all'), breathes long h's ('hundred' ×2,
  'hair' ~250 ms), holds a 200 ms f on 'five' and devoices an initial w after a pause ('within', 'without'). Soft (±1–2 f):
  s1 'walk', s3 'we've', s4 'nothing', 'each' (merged vowels, midpoint), s5 'of' (±2 f). QA A must re-measure every onset
  (lesson 13).
- **Tab (3)** on page starts (asserted); **SFX on landings (4, 22, 41)**: onsets / peaks aligned, `T.seat` gravity drops.
- **Phone band (5):** X2 / X4 given harmonic layers (LF saturation), X3 / X5 (HF rectification) + 1–3 kHz bodies; the
  hit-over-bed assertion (≥ +4 dB on 30 ms) and the −42 dBFS floor run once the bed exists. **Slab (6):** butted pages.
- **Framing (9):** deferred to the stills (placeholders). **Fonts (10):** §1. **Grain (11).** **stills.cjs (12)** deletes its bundle (verified).
- **Wording (16, 20, 32):** root strings + scene literals asserted; placards credit only research-brief sources.
- **Last word (18, 30, 44):** §5. **Settle (25):** asserted constant. **Cadence (26):** from the audio (code ready; bed pending).
- **Labels (33 / 46):** rung chips seat ON the marker's arrival with their numbers; nothing numeric rolls.
- **Lesson 34:** frame 0 is not empty: the dim rail, the marker at WALK, the counter '0', the decade numbers.
- **Lesson 38:** one tag per visible frame, hard swap at 175 (asserted). **Lessons 31/42/47:** orbit inset, mass label and
  energy bar out ≥ 8 f before the next claim's page (asserted). **Lesson 43:** end fade (asserted once the bed exists).

## 11. Soundtrack (measured, `artifacts/soundtrack_report.json`) - VOICE + SFX ONLY until the bed lands

Stereo 48 kHz 16-bit, 2,364,800 samples = 1478 × 1600. **−14.1 LUFS, true peak −1.3 dBFS**, master gain +4.6 dB. No bed:
the 100 ms floor and the closing margin are deferred (reported, not asserted).

| SFX | frame(s) | landing | note |
|---|---|---|---|
| X1 whoosh (as is) | 16 · 106 · 197 · 316 · 441 (+6 dB) · 728 | its 10 %-of-peak onset (0.167 s) | the first moving frame of the rail draw / each climb / the jump |
| X2 boom (+ LF harmonics + 1–3 kHz body) | 352 | peak 0.221 s | the SOUND seat |
| X3 tick (one tick cut 0.258–0.306 + body + harmonics) | 136 · 142 · 472 · 478 · 902 · 908 · 914 · 920 · 1074 · 1099 · 1117 · 1129 · 1136 · 1141 · 1253 … 1289 (×10) | peak | counter steps, bar steps, digit landings |
| X4 hum (shaped 1.6 s + harmonics, −22 dB) | 590 | start | the S3 window's first visible frame |
| X5 shimmer (+ harmonics) | 908 | start | the beam's first frame |
| X6 tink (start = its attack) | 1299 | start | the gap bracket |

Nothing from 50 ms before 'But' (1394) to the end (asserted).

## 12. Contact sheet 2

`renders/foundation_sheet.jpg`: one stub frame per scene (all layers), the engine's states on the picture layer, the hero
frame (sc05) with the safe zones, the placeholder plates. Stills: `renders/review/foundation/sheet/`, `sheet_pic/`. A
full-length 0.25-scale test render (`renders/_test_q.mp4`, exit 0) was made and deleted; builders run 0.25-scale segment
renders of their ranges.
