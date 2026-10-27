# BUILD.md: builder contract for "How Does a Cat Always Land on Its Feet?" (Operating Theatre, re-dressed as a test lab)

> **THE CLEAN WAVs ARE `assets/audio/narration/clean/s1.wav … s5.wav`** (+ `narration_full.wav`, `process_report.json`),
> made by `process_narration.py` from the assets' untrimmed takes: lead / tail trimmed, **s4's end click CUT** (4.20 s + 20 ms
> fade, last 20 ms −84.6 dB re. peak), **ONE constant gain per section to −21.5 LUFS** (s4 true-peak-capped at −23.7 LUFS; no
> loudnorm), and the **WIDENED section gaps 1.2 / 1.2 / 1.2 / 1.45 s** inside the files (the read is short: 38.6 s raw vs 48 s
> planned). No baked-in pause existed (lesson 29, asserted: every internal pause ≥ 0.2 s sits at punctuation): nothing cut.
> Alignment, every OVERRIDE (section-local seconds), the premix and QA A's onset sweep use these files only (lesson 17). The
> lesson-30 lifts ('all four', 'reached the vet') are in the PREMIX, not in the clean WAVs (§5).

Atelier Remotion composition **`CatLanding`**: 1080×1920 @ 30 fps, **1360 frames (45.33 s)** = 0.50 s lead-in + 43.46 s of
narration (gaps inside) up to the release of "vet." (**43.81 s, frame 1314**) + a fixed **1.50 s settle** (finished line,
chord at **f1319**). Plan: 49.6 s / 1488 f. Read `art-direction.md`, `scenes.md`, `artifacts/scene_plan.json` first.
**This file and `artifacts/props.json` hold the measured frames** (`scene_plan.json` scene times synced, schema-valid).
The engine is video 14's (`projects/how-a-mosquito-drinks/`, QA passed): kit overlay, Checklist, Window, Drape, Grain, the
Python chain - re-dressed (slate drape, steel, FRONT amber / BACK cyan, stamp red). No tray / skin / blood / saliva remain.

## 1. Layout of the foundation

| path | what |
|---|---|
| `fetch_fonts.py` | all four faces COPIED from video 14 (IBM Plex Sans Condensed 600/700, Roboto Mono 400/500, Bricolage 800, Spline Sans Mono 600; ESM asserted); every verified string + placard checked in all look faces (É ° · ~ % ? ok; → ≈ ✓ in no face: drawn); placard fit; writes `shared/metrics.generated.ts` |
| `process_narration.py` | THE CLEAN WAVs (above) + the film-length estimate (asserted ≥ 45.2 s) |
| `sweep_onsets.py` | onset sweep helper: candidates, `--strip`, `--png` spectrogram strips (1 px = 1 ms) |
| `align_narration.py` | faster-whisper small.en → script words; **63 OVERRIDES + 44 CONFIRMED = all 107 words hand-measured** on spectrogram strips + band tables (§10); anchors from `narration_by_scene`; scene windows = anchor onset − 2 f → `artifacts/timeline.json` (**`vet_end_frame` / `vet_end_seconds`**, the only `*_end_frame` key), `alignment_report.json` |
| `build_soundtrack.py` | narration (+ lifts) + the level-evened, ducked bed (its LAST TONIC at film 43.962 s = release + 0.152 s) + SFX → `public/audio/soundtrack.wav` (1360 × 1600 samples), `artifacts/soundtrack_report.json`. **Owns the KEY FRAMES `K`** (`key_frames()` → `props.audio` → `T.sfx.*`) and the motion constants |
| `prepare_media.py` | S1 / S2 crops (measured, every paw / tail / ear asserted inside), the Marey cells 3–10 (hands cropped: each cut ≥ hand bottom + 4 px, asserted; no bright pixel above it) → `public/stills/`, `artifacts/media_report.json`, `renders/review/crops.jpg` |
| `sync_scene_plan.py` | syncs `scene_plan.json`: times, A1 tag 'engraving after É.-J. Marey, 1894' + 'UP' ADDED to `verified_on_screen_strings` ('É.-J. Marey, 1894' / 'drawn after …' REMOVED), safe areas as built, `foundation_changes`; jsonschema |
| `build_props.py` | caption pages (24; lesson-3 re-flows), meter, placards (5), **the cat curves** (§6), dials, rig, checklist + clock, window plates → `artifacts/props.json`, `props.generated.ts`, `artifacts/cat_turns.json`. All asserts in §10 |
| `theme.ts` | `FONT`, palette `C`, `glass()`, `rgba()`, easings `E`, layout `L` (header, rig, field, card, win, dials, ledger, drawnTag, placard, tab, slab), `AMBIENT` |
| `time.ts` | `useT()`: `at/end/word`, `scene/section`, `sfx.*`, `motion`, `rig(f)`, `check(f)`, `clock(f)`, `win(f)`, `plate(id,f)`, `tagAt(f)`, `strip(f)`, `cat(f)`, `dials(f)`, `seat`, `driftFrame`, `loopFrame`; `prog`, `remap`, `lerp`, `sample` |
| `shared/` | ROOT: `Drape`, `Rig` (`RigView`, `DrawnTagLive`, `ClampJaws`), `Checklist` (`ChecklistCard`), `Window` (`WindowView`, `WindowTags`; `WindowFrame` exported), `Strip` (`MareyStrip`, used by Window), `Grain`. ENGINE for units: **`Cat` (`CatLive`, `Cat`, `CAT`)**, **`Dials` (`DialsLive`, `Dial`)**, **`Ledger`**, **`Skater`**, **`Stamp`**, `Icons` (`Arrow`, `CurvedArrow`, `CheckMark`, **`InnerEarIcon`**, **`ArrowLabel`**), `Type` (`measure`, `fitSize`, `Rich`, `Label`, `hatch`), `noise` |
| `overlay/` | kit: `Captions` (tones front / back set at the KIT point), `HonestyTab`, `PlacardRail` (+ `SettleCta`), `Tag` (`SceneTag`; the kit `DrawnTag` is NOT mounted - `DrawnTagLive` replaces it) |
| `scenes/` | `index.ts`, `_stub.tsx`, **`scenes/u1/`** (sc01–sc06) and **`scenes/u2/`** (sc07–sc12): one STUB per scene; FOUNDATION DEMOS in sc03 (stamp), sc04 (inner ear), **sc06 (the two-half turn)**, sc07 (skater), sc10 (stamp), sc11–sc12 (ledger) - replace them |
| `contact_sheet2.py` | contact sheet 2 → `renders/foundation_sheet.jpg` |

Rebuild order after any narration change: `process_narration.py` → `align_narration.py` → `build_soundtrack.py` →
`sync_scene_plan.py` → `build_props.py` → tsc → stills (from the repo root, e.g. `HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1
python3 projects/how-a-cat-lands/align_narration.py`). `prepare_media.py [--force]` only when the crops change (then
`build_props.py`). `fetch_fonts.py` only for a new face / string. **After a scene edit that adds a literal, rerun
`build_props.py`** (its literal scan covers `scenes/u*/`).

Render **through the symlink** `remotion-composer/projects/how-a-cat-lands`:

```bash
cd remotion-composer && npx remotion render projects/how-a-cat-lands/index.tsx CatLanding ../projects/how-a-cat-lands/renders/<raw>.mp4 \
  --config=projects/how-a-cat-lands/remotion.config.ts --props=../projects/how-a-cat-lands/artifacts/props.json \
  --concurrency=3 --crf=18 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
  --public-dir=../projects/how-a-cat-lands/public          # add --scale=0.25 --frames=a-b for segment / test renders
# stills (bundle once, deleted after): cd projects/how-a-cat-lands && node stills.cjs --frames 0,300 --scale 0.5 --out renders/review/<unit>
#                                      node stills.cjs --frames ... --layers picture   (no overlay plane)
```

Typecheck: `cd remotion-composer && npx tsc -p projects/how-a-cat-lands/tsconfig.json` (clean). Hooks: `cd
projects/how-a-cat-lands && python3 check_hooks.py scenes shared overlay` (0). **Disk is tight (~4.8 GB free on `/`):**
0.25-scale segments only, stills at 0.5, delete your test renders, never leave `/tmp/remotion-webpack-bundle-*`.

## 2. Scene contract

```tsx
// scenes/u1/TuckFront.tsx
export const mount: Mount = { pre: 0, post: 0, z: 1 };                    // frames mounted before from / after to; z
export const TuckFront: React.FC<SceneProps> = ({ from, to }) => { ... };  // the PICTURE (above the rig, under window + card)
export const Overlay: React.FC<SceneProps> = ({ from, to }) => { ... };    // OPTIONAL: stamps / labels / tags on the overlay plane
```

- **Build ONLY inside your own `scenes/uN/`.** Keep file names, export names and `mount`. Helper files in your folder are
  fine (never import across units). Root, `shared/`, `overlay/`, `time.ts`, `theme.ts`, `types.ts`, the Python scripts and
  `scenes/index.ts` are foundation-owned: **request changes through §7.** Delete `<StubLabel>` and the FOUNDATION DEMOS.
- Scenes are mounted by **absolute** frame windows (no `<Sequence>`); `useCurrentFrame()` is the absolute frame.
- **ROOT vs UNIT.** **THE ROOT OWNS THE TEST LAB**: the drape, the header 'PROCEDURE: LANDING', the rail + release clamp
  (opens ON `clampOpen`) + the floor line (sc09–sc10), the checklist card (seated from frame 0, ticks, the ELAPSED clock +
  'illustrative'), the WINDOW (S1, the Marey strip, S2, their motion) and its ONE tag, 'drawn · not to scale' (frame 0 →
  the ledger), placards, tab, captions, CTA. **UNITS OWN THE PER-SCENE ACTION**, built from the engine: **the cat (mount
  `<CatLive/>` in EVERY scene you own while `T.cat(f).vis > 0`: sc01–sc10)**, the dials (`<DialsLive/>` sc05–sc10), the
  readouts (sc02), stamps (sc03, sc10, in your Overlay), the inner ear + UP arrow (sc04), labels, the skater (sc07), the
  short-drop label (sc10), the ledger (sc11–sc12) and their own tags.
  Layer order: drape → rig → **scene pictures** → window → checklist card → grain → overlay plane (root tags → scene Overlays
  → placards → tab → captions → CTA). **Your pictures are UNDER the window and the card; anything that must sit over them
  (the stamps) goes in your `Overlay`.**
- **THE CAT IS NEVER RE-AUTHORED IN A SCENE.** Its pose (position, the two roll angles, legs, bend, arch, flex, vis, ghost)
  is `props.cat` (build_props.py). You may: choose `axes` (dashed roll axes), add your own drawings around it (arcs,
  highlights, insets), add a whole-cat opacity ≤ 1. You may NOT translate / rotate / scale it or draw another cat. A pose
  change = a §7 request (the asserts in §6 must keep holding).
- **Hooks at the top of every component, before ANY early return.** `check_hooks.py` (0) AND a real 0.25-scale render of
  your range before hand-back (lesson 1).
- **Every trigger goes through `useT()`** (`T.at("s3","front",2)`, `T.sfx.turnStart`, `T.scene("sc06")`, `T.cat(f)`).
  Never hard-code a frame or a second. A beat that needs a sound or a new key frame = a §7 request.
- **SFX on the visible frame (lessons 4, 14, 22, 41):** the key frame is the frame an element is **fully** down / landed;
  seat with `T.seat(f, T.sfx.xxx, T.motion.SEAT_F, dropPx)` (gravity ease-in, still moving on seat − 1). Check seat − 2 /
  seat − 1 / seat stills. X5 creaks fire on the FIRST MOVING frame of a twist (`bendStart`, `turnStart`, `swapStart`).
- **Safe areas:** no text at y ≥ 1574 or x ≥ 929 (text ends ≤ 912), nothing above y 192 (the stub card there is
  temporary). Root-reserved: header x 140–~520 y 232–268; rail y 303–321 (x 140–600) + clamp to y ~392; **CARD x 640–920
  y 220–600**; **WINDOW x 160–620 y 360–1000** (when open) with its tag bottom-right inside, or **under it at x 160–~660,
  y 1010–1048 for the Marey credit**; 'drawn · not to scale' x 140–~420 y 1066–1104 (until f1148); placard rail y 1124–1204,
  tab y 1236–1290, slab x 140–940 y 1296–1488. Unit zones: cat field x 120–620 y 360–1000 (the cat itself from the curves),
  **dials x 640–920 y 620–860** (`L.dials`), right column below the dials y 870–1050 free (skater, readouts in sc02 at
  y 620–780 before the dials exist), **ledger x 140–920 y 630–1010** (`L.ledger`). Floor line y 960 (`L.field.floorY`).
- **Strings:** verbatim from `scene_plan.metadata.verified_on_screen_strings` (incl. the new 'UP'), nothing from
  `forbidden_on_screen` ('always lands', '60 mph', 'pushes off', 'physics was wrong', 'nine lives', 'dead'). Route every
  on-screen string through a `text="…"` / `text: "…"` / `*TEXT|LINE|LABEL|NUM* = "…"` literal (build_props.py scans them).
  No '→' / '≈' / '✓' glyphs: `<ArrowLabel text="legs in → spins fast"/>` draws the arrow, `<Arrow>`, `<CheckMark>`; '~' via
  `<Rich>`. Labels ≥ 28 px, fine print ≥ 24 px (lesson 31). Numbers on screen: none except the root clock and the ledger's
  verified strings; **the dials carry NO degree numbers** (lesson 33).
- **COLOUR RULES:** FRONT amber `C.front` ONLY on the front half (its tint, dial, 'FRONT'); BACK cyan `C.back` ONLY on the
  back half (tint, dial, 'BACK'); Stamp red `C.stamp` ONLY on the stamps. Everything else steel / bone / ink / paper / slate.
  Captions: both s3 'front' amber, ONLY s3's 'back' ('the back half') cyan; **s4 'back arched' is the spine: plain**.
- **No blend modes under fading parents** (lesson 24).
- **Honesty:** AI / archival media only through the root window (tagged by the root: 'AI impression', 'engraving after
  É.-J. Marey, 1894'). The drawn cat + rig are covered by the root 'drawn · not to scale' until the ledger; your separate
  diagrams (sc04 inner-ear inset, sc07 skater) carry their own `SceneTag` 'drawn · not to scale'. PROBABLY claims (sc10 short
  drops, sc12 'not counted') use the PROBABLY grammar where you tag them (`variant="probably"` / `Label variant="probably"`).
  Lesson 42: anything tied to one claim is gone before the next claim's tab state (§3 tab keys).

## 3. Frame table (measured; boundary = anchor onset − 2 f for EVERY scene after sc01)

| scene | component · unit | frames | dur | narration (word onset frames) |
|---|---|---|---|---|
| sc01 | CatDrop · U1 | 0–106 | 106 f · 3.53 s | Drop 16 · a 24 · cat 27 · upside 34 · down, 46 · and 63 · it 67 · flips 69 · over 81 · in 87 · midair 93 |
| sc02 | NothingToPush · U1 | 106–162 | 56 f · 1.87 s | with 108 · nothing 112 · to 122 · push 131 · on. 138 |
| sc03 | Marey1894 · U1 | 162–286 | 124 f · 4.13 s | In 164 · 1894, 168 · that 209 · looked 214 · impossible. 220 |
| sc04 | FindUp · U1 | 286–389 | 103 f · 3.43 s | First, 288 · its 311 · inner 318 · ear 327 · finds 336 · which 349 · way 358 · is 362 · up. 367 |
| sc05 | Bend · U1 | 389–540 | 151 f · 5.03 s | Then 391 · it 402 · bends 410 · in 420 · the 423 · middle, 424 · so 443 · each 451 · half 457 · can 470 · turn 475 · on 483 · its 486 · own. 491 |
| sc06 | TuckFront ★ · U1 | 540–651 | 111 f · 3.70 s | It 542 · tucks 547 · its 555 · front 559 · legs, 569 · and 588 · the 592 · front 594 · half 602 · spins 611 · fast, 625 |
| sc07 | Skater · U2 | 651–722 | 71 f · 2.37 s | like 653 · a 657 · skater 660 · pulling 679 · in 688 · her 691 · arms. 696 |
| sc08 | Swap · U2 | 722–835 | 113 f · 3.77 s | Then 724 · it 729 · swaps, 732 · and 756 · the 760 · back 763 · half 769 · follows. 778 |
| sc09 | Land · U2 | 835–1007 | 172 f · 5.73 s | Legs 837 · out, 847 · back 871 · arched, 878 · it 913 · lands 918 · on 930 · all 936 · four. 941 |
| sc10 | NotAlways · U2 | 1007–1133 | 126 f · 4.20 s | But 1009 · not 1013 · always. 1021 · Short 1055 · drops 1066 · leave 1078 · no 1084 · time 1092 · to 1101 · turn. 1104 |
| sc11 | TheStudy · U2 | 1133–1245 | 112 f · 3.73 s | And 1135 · that 1138 · famous 1142 · study 1156 · where 1166 · ninety 1171 · percent 1185 · survived 1196 · high 1209 · falls? 1216 |
| sc12 | NotCounted · U2 | 1245–1360 | 115 f · 3.83 s | It 1247 · only 1251 · counted 1258 · cats 1271 · that 1286 · reached 1289 · the 1299 · vet. 1301 (release **1314**; settle 1314–1360) |

Sections (files incl. their gaps): s1 15–287 · s2 287–542 · s3 542–836 · s4 836–1005 · s5 1005–1319.

**Key frames** (`T.sfx`; SFX already on them; **root** = the root draws it; **curves** = props.cat / dials):

| scene | beats |
|---|---|
| sc01 | rig + header + card + 'drawn · not to scale' from **0** (root); clamp FULLY OPEN ON `clampOpen` **16** (X1 click; root); the cat (curves) hangs → falls (gravity) and flips feet-down as a quick preview (front tucks 16–22, turns 22–46; legs swap 48–56; back turns 56–84) by `previewFlipEnd` **93**; becomes a ghost outline 96–106, fades 270–280 under the window |
| sc02 | window first visible ON `windowOpen1` **106** (S1 'AI impression', X2 slide; root); **U1 readouts 'push: none' ON `readouts[0]` 112 / 'starting spin: 0' ON `readouts[1]` 131** (right column, no SFX) |
| sc03 | S1 → Marey strip crossfade 162–174, **tag swaps by a hard cut at 169** (root); strip steps ON `stripSteps` **176 · 190 · 204 · 218 · 232 · 246 · 260** (root); **U1 'IMPOSSIBLE?' stamp SEATED ON `stampImpossible` 220 (X3; Overlay)**; window closes `windowClose1` 278 → 286 |
| sc04 | cat reset upside down at the top, fades in 286–296 (curves); clock starts on `clockStart` **288** (root); **U1 inner ear glows from `innerEar` 318; UP arrow + label 'inner ear: which way is up'**; '01 FIND UP' ON `tick01` **367** (X4; root) |
| sc05 | **the waist bends from `bendStart` 410 (X5) to `bendSeat` 424** (curves); dials in on `dialsIn` **451**, 'total spin: 0' on `totalSeat` **475** (curves; `<DialsLive/>`); '02 BEND' ON `tick02` **491** (X4; root) |
| sc06 ★ | front legs tuck `tuckStart` 547 → `tuckSeat` **569**; **FRONT turns +200° (fast) / BACK −20° (the other way) from `turnStart` 594 (X5) to `turnEnd` 646** (curves); '03 TUCK FRONT' ON `tick03` **625** (X4; root) |
| sc07 | the cat holds (curves); **U2 skater: arms in on `armsIn` 679** (no SFX) |
| sc08 | legs swap `swapStart` **732** (X5) → 744 (back tucked, front out); **BACK turns +200° / FRONT −20° from `backTurnStart` 763 to `swapEnd` 795** → both 180° = feet down (curves); '04 SWAP' ON `tick04` **778** (X4; root) |
| sc09 | floor line in from `floorIn` **835** (root); legs out + '05 SPREAD' ON `tick05` **847** (X4); bend → 0 by 847; arch ON `arch` 878; drop (gravity) 900 → **paws ON the floor ON `land` 936 (X6 thump)**, flex 936–956 (curves); '06 LAND' + clock STOPS ON `tick06` **947** (X4; root, 0.64 s illustrative); window S2 ON `windowOpen2` **960** (X2; root), cat hidden under it 975–985; S2 closes `windowClose2` 999 → 1007 |
| sc10 | dials + 'total spin: 0' OUT 990–1004 (before the 'But' page 1009; curves); **U2 'NOT ALWAYS' SEATED ON `stampNotAlways` 1021 (X3; Overlay, across the card)**; short-drop GHOST (outline) in 1055–1063, front tucks 1058–1066, **FRONT turns only +70° (back −7°) from `shortTurn` 1066**, fades out 1092 → `shortGone` **1104**, never reaching the floor (asserted ≥ 60 px above); the FRONT dial alone 1063–1102 (curves); floor out 1112–1124 (root); **U2 label 'short drop: no time to turn' (PROBABLY grammar)** |
| sc11 | 'drawn · not to scale' out 1142–1148 (root); **U2 ledger SEATED ON `ledgerSeat` 1156 (X7)**, bar fills `barFrom` **1171** → `barTo` **1196**, '~90% survived' with it |
| sc12 | **NO SFX from 'It' (1247)**; **U2 ghost column from `ghostColumn` 1251, 'not counted' on `notCounted` 1258, bracket 'of cats brought in' on `bracket` 1271**; release `vetEndFrame` **1314**; chord `chordFrame` **1319**; CTA 'Seen a cat do this?' ON `ctaFrame` **1318** (root); tab IDLE from 1318; **every channel constant from 1314** |

Captions: 24 pages (`props.captionPages`). Placards: 2–286 (Marey) · 292–540 (inner ear) · 546–835 (Kane & Scher) ·
841–1007 (kittens) · **1139–1314 (Whitney & Mehlhaff: enters on the study's own page, not under SHORT)**. Honesty tab
(lesson 3, page starts): IDLE 0 · MEASURED 16 (MAREY) · pulse 288 (UP) · pulse 391 (BEND) · pulse 542 (TUCK) · pulse 653
(SKATER) · pulse 724 (TUCK, swap) · pulse 837 (SPREAD) · **PROBABLY 1009 (SHORT)** · **MEASURED 1135 (HIGHRISE)** ·
**PROBABLY 1247 (BIAS)** · IDLE 1318 (the settle).

## 4. Assets and how they are used

| asset | use |
|---|---|
| **S1** plate_cat_midair | crop px 80–1122 × 180–1630 → 460×640, every paw / tail tip / both ears inside (asserted); head-down, belly to camera ("upside down"); push 1 → 1.03; sc02 |
| **A1** marey_1894.jpg | an ENGRAVING after Marey (two strips); the TOP strip's cells 3–10 (cells 1–2 dropped: paws held in the hands), each cut below its hand (+4 px, feather 8) → 325×406 tiles → a vertical film strip (`shared/Strip.tsx`) stepping one cell per 14 f; tag 'engraving after É.-J. Marey, 1894' (UNDER the window: wider than it); sc03 |
| **S2** plate_cat_landing | crop px 8–1144 × 70–1650 → 460×640 (4 paws on the floor; the occluded far hind paw never zoomed); push 1 → 1.03; sc09 landing beat |
| narration | §0; in the premix: s4 +2.2 dB constant (its TP-capped gain left it 2.2 dB under the others; voice-lane voiced RMS now s1 −20.5 · s2 −20.6 · s3 −20.6 · s4 −19.9 · s5 −20.9 dBFS), 'all four' +4 dB more, 'reached the vet' +5 dB (§5) |
| music | G major 96 BPM; V → I then the tonic re-struck at src 52.81 = **the chord** (no IV–V–I; none claimed) |
| SFX | X1–X7, §11 |

## 5. The ending (finished line)

- "It only counted cats that reached the vet." is released at **f1314** (43.81 s; the t release of 'vet'). **'reached the
  vet.' +5.0 dB** constant broadband on the voice lane (raised-cosine 40 ms in / 30 ms out, not a limiter): qa_auto's
  lesson-30 metric (loudest 100 ms of 'vet' vs the median of its sentence's words) **5.1 → 1.8 dB under** (≤ 3 asserted).
  + −6 dB extra duck and a +4 dB 300–4000 Hz lift on 'vet'. Closing sentence over the bed in 300–4000 Hz: **≥ +12.8 dB
  on every word** (asserted ≥ +12).
- **Closing duck −13 dB from 'It'** (lesson 44), ramped in from 'It' − 0.55 s and full from 'It' − 0.15 s, because the bed's
  V → I arrival (src 50.40) lands at film 41.55 s, 30 ms before 'It' (41.58 s); no floor lift may reach into the sentence.
- **Settle 1314–1360 (46 f):** the bed's last tonic at **43.962 s (f1319) = release + 0.152 s**, its ring-out lifted +5 dB,
  a cos² fade over the last 0.6 s to −36 dB then a 10 ms ramp: last 50 ms −59.1 dBFS, last 20 ms −62.0 (qa_auto: ≤ −30 /
  ≤ −33). **Every root channel is constant from 1314** (asserted); grain freezes on frame 0's seed. The picture: the rig, the
  completed checklist with the stopped clock (0.64 s), the ledger with its ghost column + bracket; slab 'Seen a cat do this?';
  tab IDLE. **No unit element may change after 1314.** The last frame ≠ frame 0 (no loop export built).

## 6. Shared helper APIs (all frames absolute)

```tsx
const T = useT();
T.at("s3","front",2); T.end("s5","vet"); T.scene("sc06"); T.sfx.turnStart; T.sfx.stripSteps[i]; T.motion.SEAT_F
T.cat(f) -> { x, y, front, back, frontTuck, backTuck, bend, arch, flex, vis, ghost, scale }   // roll deg: 0 upside down, 180 feet down
T.dials(f) -> { front, back, total }   T.rig(f) -> { clamp, floor, floorY, drawnTag }   T.check(f)  T.clock(f) -> { seconds, text, stopped }
T.win(f)  T.plate("S1"|"A1"|"S2", f)  T.tagAt(f)  T.strip(f)  T.seat(f, seatFrame, frames=8, dropPx=18) -> { k, y, opacity, seated, visible }
// ENGINE:
<CatLive axes={0..1} opacity/>      // the cat from the curves (full-frame svg). <Cat pose axes/> = the pure drawing (inside your <svg>)
<DialsLive/>                        // FRONT + BACK dials + labels + 'total spin: 0' from the curves.  <Dial cx cy r angle color vis/> (svg)
<Stamp x y text k angle size/>      // red stamp (HTML; in your Overlay)
<Ledger k dropY title rows bar barLabel ghost ghostHeader notCounted notCountedText bracket bracketText/>   // HTML, L.ledger
<Skater x y arms phase scale/>      // svg
<InnerEarIcon x y size glow/> <Arrow/> <CurvedArrow/> (svg)   <ArrowLabel x y text size/> (HTML, draws '→')   <Label/> <Rich/> (Type)
<WindowFrame box open>…</WindowFrame>   // the window look for YOUR drawings only (never AI / archival media)
<SceneTag x y enter exit text variant/>  // in your Overlay
// ROOT ONLY (never mount in a scene): Drape RigView DrawnTagLive ChecklistCard WindowView WindowTags MareyStrip Grain PlacardRail HonestyTab Captions SettleCta
```

**The cat's physics, by construction (build_props.py `cat_curves`, asserted):** each half has a moment I = 1 with legs out,
0.1 tucked; on every frame I_front·dFront + I_back·dBack = 0, so **'total spin: 0' is literally true of the drawing**. The
tucked half is the driven one (sine-eased); the other is derived and turns the OTHER way, 10× less. Turns (`artifacts/cat_turns.json`):
sc01 preview front +200 / back −20, then back +200 / front −20; **sc06 front +200 / back −20 (594–646)**; **sc08 back +200 /
front −20 (763–795)** → both 180°; sc10 front +70 / back −7. Asserted on every moving frame of each turn: opposite signs, the
tucked half turns MORE; ≤ 15°/frame and ≤ 3°/frame² while visible (smooth eased curves, no rigid jumps; pose resets only
while hidden). The research says "up to ~90° / ~10°" (exact angles PROBABLY): the dials show direction + relative size only.
**Count: 4 legs, 1 tail, 2 ears on every frame** (shared/Cat.tsx): keep it so in anything you add (lessons 39/40).

## 7. Unit split for 2 parallel scene builders and hand-offs

| unit | scenes | frames | owns (picture / overlay) |
|---|---|---|---|
| **U1 drop → Marey → find up → bend → TUCK (HERO)** | sc01–sc06 (`scenes/u1/`) | **0–651** | `<CatLive/>` in all six scenes (vis > 0 except 280–286); sc02 readouts 'push: none' / 'starting spin: 0' (x 640–920, y 620–780; ON `readouts`); sc03 'IMPOSSIBLE?' `<Stamp>` SEATED ON 220 in the Overlay (the demo: centre x 748 y 700, size 42 → measured x 588–906; never past x 912); sc04 `<InnerEarIcon>` on the cat's head (glow from 318) + an SVG UP arrow seated ON 367 + label 'inner ear: which way is up' (+ its own 'drawn · not to scale' if drawn as an inset); sc05 axes (`<CatLive axes/>`), `<DialsLive/>` from 443; **sc06 HERO**: the two-half turn (the demo shows it from the curves), emphasis arcs / motion lines in the halves' colours, `<ArrowLabel>` 'legs in → spins fast' / 'legs out → turns slowly' (field y 860–990) |
| **U2 skater → swap → land → not always → ledger (ending)** | sc07–sc12 (`scenes/u2/`) | **651–1360** | `<CatLive/>` sc07–sc10 + `<DialsLive/>` sc07–sc10; sc07 `<Skater>` inset (right column y ~870–1050 or field bottom) + 'smaller → spins faster' + its 'drawn · not to scale' `SceneTag`; sc08 the swap's emphasis (the curves do the motion); sc09 the landing emphasis around `land` 936 (no picture change on 935 that reads as contact); sc10 `<Stamp>` 'NOT ALWAYS' ON 1021 (Overlay; across the card is fine; the demo: centre x 758 y 420, size 42 → ~x 608–910) + 'short drop: no time to turn' (PROBABLY grammar) during 1055–1104; sc11–sc12 ONE `<Ledger>` across the 1245 seam (seated ON 1156, bar 1171–1196, ghost from 1251, 'not counted' 1258, bracket 1271), constant from 1314 |

Seams (agree with a shared still: compare `from − 1` vs `from`):

| seam | outgoing → incoming | both sides must match |
|---|---|---|
| **651** sc06 → sc07 | U1 → U2 | the cat + dials are the curves (identical by construction); **axes: `axes={1}` on BOTH sides at 650 / 651** (U2 fades them later, after `swapEnd`, if wanted); U1's hero labels / arcs gone by **641** (the demo fades 641–651: finish by 650); caption page 'and the front half spins fast,' exits 653 |
| **1245** sc11 → sc12 | U2 internal | the ledger: same component, same props at 1244 / 1245 |
| **0 / 1359** | — | NOT equal by design (§5) |

A scene drawing past its `to` (inside its `post`) draws ONLY its own outgoing elements. All `mount.post` are 0; ask (§7)
for one. Unit-internal seams: 106, 162, 286, 389, 540 (U1); 722, 835, 1007, 1133, 1245 (U2).

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
- Colour rules on every frame; 4 legs / 1 tail / 2 ears; nothing of yours over the card or the window except Overlay stamps.
- `stills.cjs` cleans its bundle; delete your test renders (disk).

### §QA (after the render)

After the master (`docs/channel/scripts/finish_master.sh`), the orchestrator runs
**`python3 docs/channel/scripts/qa_auto.py projects/how-a-cat-lands`** first (it reads `timeline.json` `vet_end_*`,
`props.json`, `soundtrack_report.json`); fix every FAIL before any QA agent.

## 9. Divergences from the scene plan

- Film **1360 f (45.33 s)**, not 1488: the read is short; section gaps widened (1.2 / 1.2 / 1.2 / 1.45 s); all 12 windows re-timed.
- **ONE window box x 160–620, y 360–1000** (portrait, left of the card) instead of x 160–920 y 360–900 (it covered the card);
  the Marey tag sits under the window (wider than it).
- **A1 downloaded** (an engraving after Marey): film strip of cells 3–10, hands cropped; tag 'engraving after É.-J. Marey,
  1894' (verified strings synced; the two unused variants removed); 'UP' added.
- Caption pages re-flowed (s2, s3, s5): every claim starts its own page; the closing sentence 'It only counted cats' / 'that
  reached the vet.' (no 2-word orphan). The study placard enters on 'And that famous study where' (not under SHORT).
- The S2 photo shows in the landing beat AFTER 'four.' (960–1007), so the drawn landing on 'all' stays visible.
- The clock reads '0.00 s' → '0.64 s' (illustrative), not m:ss.
- Checklist card seated from frame 0 (no slide-in); header on the stage, not on the card.
- 'all four': s4 +2.2 dB (section) + 4 dB on the words (+6.2 total) + a −6 dB extra bed duck over them: plain +4 sat under the bed and X6 in 300–4000 Hz (now voice over X6 +4.3 dB, over the bed (voiced median) +8.1 vs film median +8.5).
- **Placard 5's fine print '132 cats; only cats brought in were counted' shows from 1139 under the HIGHRISE (MEASURED) tab - deliberately:** it DEFINES the sample the ~90 % is of (lesson 32: word a number by what it is), so '~90% survived' (ledger, from 1171) is never on screen without its caveat (lesson 16); the survivorship INFERENCE ('It only counted cats that reached the vet') goes PROBABLY at 1247. Not a lesson-42 slip.

## 10. Foundation build log: lessons applied

- **Hooks (1):** 0 violations (33 files). **Onsets (2, 13, 17):** all 107 words hand-measured on the clean WAVs (spectrogram
  strips + band tables); Whisper was off up to 7 f: s1 'impossible.' −7.0 f (it sat on the p of 'possible'), s5 'It' +5.0,
  'that' +5.0, 'percent' +4.5, s4 'on' +4.5, s2 'can' +4.2, s3 'fast,' +4.1, s1 'down,' +4.2. Soft (±1–2 f): s1 'it' 'in'
  'midair' 'with', s2 'is' 'the' 'half', s3 'the' ×2 'her' 'follows.', s5 'that' (1st) 'study' 'reached'; s5 'But' at its
  burst after a 55 ms voice bar. QA A must re-measure every onset (lesson 13).
- **Tab (3)** on page starts (asserted); **SFX on landings (4, 22, 41)**: peaks / first clicks aligned, `T.seat` gravity drops.
- **Phone band (5):** every hit ≥ +4.6 dB over the bed in 300–4000 Hz on 30 ms (asserted ≥ +4); X4 / X5 1–3 kHz bodies +
  harmonics, X6 a 1–3 kHz contact layer; **0 windows < −42 dBFS** (min −35.6). **Slab (6):** butted pages.
- **Framing (9):** crops from measured points. **Fonts (10):** §1. **Grain (11).** **stills.cjs (12)** deletes its bundle (verified).
- **Wording (16, 20, 32):** root strings + scene literals asserted; placards credit only research-brief sources.
- **Last word (18, 30, 44):** §5. **Settle (25):** asserted constant. **Cadence (26):** from the audio (no IV–V–I).
- **Labels (33):** the dials have no numbers. **Lesson 38:** one tag per visible frame, hard swap at 169 (asserted).
- **Lessons 31/42:** dials + 'total spin: 0' out before the 'But' page (asserted); the study placard waits for its page.
- **Lesson 43:** end fade (asserted). **Lesson 39/40:** S1 / S2 passed the anatomy gate; the drawn cat has 4 / 1 / 2.

## 11. Soundtrack (measured, `artifacts/soundtrack_report.json`)

Stereo 48 kHz 16-bit, 2,176,000 samples = 1360 × 1600. **−14.1 LUFS, true peak −1.2 dBFS**; min 100 ms window −35.6 dBFS; last 50 / 20 ms −59.1 / −62.0 dBFS. Bed −19 LUFS before the duck,
2 s-window level evening; head on the 8th grid (src 8.750 s), resampled **+4.04 cents**; last tonic **src 52.81 → film
43.962 s**. Duck −12 dB under the voice (median −12.0); −13 dB closing duck (§5).

| SFX | frame(s) | landing | hit over bed, 300–4000 Hz, 30 ms |
|---|---|---|---|
| X1 clamp click (+ 1–3 kHz edge) | 16 | peak 0.145 s | +4.7 |
| X2 window slide (texture) | 106 · 960 | start | 50 ms max +10.5 / +9.5 |
| X3 stamp (one hit 2.44–2.62 s + harmonics) | 220 · 1021 | peak | +16.7 · +4.6 |
| X4 tick (one tick 1.38–1.50 s + body + harmonics) | 367 · 491 · 625 · 778 · 847 · 947 | peak | +9.5 · +11.4 · +15.0 · +5.4 · +14.7 · +10.2 |
| X5 creak (0.03–0.32 s, −4 st, first click accented) | 410 · 594 · 732 | first click | +15.4 · +12.9 · +8.0 |
| X6 paw thump (+ 1–3 kHz contact layer) | 936 | peak 0.255 s | +20.0 |
| X7 ledger slide | 1156 | peak 0.448 s | +11.6 |

Nothing from 50 ms before 'It' (1247) to the end (asserted).

## 12. Contact sheet 2

`renders/foundation_sheet.jpg`: one stub frame per scene (all layers), the engine's states on the picture layer, the hero
frame with the safe zones, the media crops. Stills: `renders/review/foundation/sheet/`, `sheet_pic/`. No full render was
made at the foundation stage (disk); builders run 0.25-scale segment renders of their ranges.
