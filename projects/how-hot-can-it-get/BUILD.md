# BUILD.md: builder contract for "How Hot Can It Get?" (Black-Body)

> **THE CLEAN WAVs ARE `assets/audio/narration/clean/s1.wav … s5.wav`** (+ `narration_full.wav`, `process_report.json`),
> made by `process_narration.py` from the assets' untrimmed takes: **s3's baked-in pause between 'held' and 'a hundred'
> cut (raw 5.505–5.672 s removed in one piece incl. a ~−50 dBFS breath hump, 10 ms crossfade, both splice sides < −60 dBFS;
> the pause left is 0.043 s under −45 dBFS)** (lesson 29), lead / tail trimmed, loudnorm −16 LUFS, the script's
> `pause_after` (0.35 / 0.4 / 0.45 / 0.45 / 0 s) appended. No beat pause trimmed. Alignment, every OVERRIDE
> (section-local seconds), the premix and QA A's onset sweep use these files and nothing else (lesson 17). The raw
> `assets/audio/narration/sN.wav` are NOT clean WAVs. 'know.' is NOT lifted in the clean WAVs (the premix lifts it, §5).

Atelier Remotion composition **`HowHot`**: 1080×1920 @ 30 fps, **1507 frames (50.23 s)** = a 0.50 s lead-in (the ember
crackle, the dark forge) + 48.315 s of narration (s1–s5 back to back) up to the release of "know." (**48.71 s, frame
1461**) + a fixed **1.50 s settle** (finished-line ending, no loop splice). The plan estimated 50.5 s / 1515 f.
Read `art-direction.md`, `scenes.md` and `artifacts/scene_plan.json` (the look) before you author a scene. **This file
and `artifacts/props.json` hold the measured frames** (`scene_plan.json` scene times were updated to match, schema-valid;
planned values kept in `metadata.planned_total_*`). Layout and conventions mirror `projects/what-if-earth-stopped-spinning/`
(video 12, delivered).

## 1. Layout of the foundation

| path | what |
|---|---|
| `fetch_fonts.py` | self-hosted woff2: **Saira Condensed 700, IBM Plex Mono 400/500** (fetched; ESM `dist/esm/*.mjs` asserted), Bricolage 800 + Spline Sans Mono 600 (copied from video 12). Asserts every character of every verified string + placard in Saira AND both Plex weights: `× ° · ~ > - , ' :` + digits present; `→ ≈` in no face (drawn); `−` (U+2212) present but **not used** (the verified strings use ASCII `-`). `^` is never set: the exponent is drawn. Measures the placards (`fonts.manifest.json placard_fit`): Plex Mono cannot fit the KSTAR / Planck placards with ≥ 24 px fine print → placards are Saira. Writes `shared/metrics.generated.ts` |
| `process_narration.py` | THE CLEAN WAVs (above) + the 'know' span on the clean s5 (10.245–10.65 s) |
| `prepare_media.py` | stages `public/clips/K1_30.mp4` (f0–f150, 756×1344, the assets' frame-blended 30 fps copy), `K2_30.mp4` (f0–f150, 778×1382), `public/stills/S2.jpg`, `S4.jpg` (756×1344), `public/frames/K1_first.jpg`, `K2_first.jpg`, `K2_last.jpg`; MEASURES the fits from pixels (lesson 9): K1 horizon 30.8 % → 45 % of the window (shows source y 12.7–52.9 %: the 1.9 px/f near ground is cropped out), S2 horizon 37.3 % → 42 %, K2 violet-loop centroid (48.7 %, 45.0 %) → window centre, S4 red ring centre (49.7 %, 45.8 %) → window centre → `artifacts/media_report.json` |
| `sweep_onsets.py` | caption-onset sweep helper (band envelopes + flux candidates, zoom views) → `artifacts/onset_sweep.json` |
| `align_narration.py` | faster-whisper small.en → script-text words; **67 OVERRIDES + 42 CONFIRMED = all 109 words hand-measured** (§10); scene windows = anchor onset − 2 f → `artifacts/timeline.json`, `alignment_report.json` |
| `build_soundtrack.py` | narration + the level-evened, ducked bed (head on the 16th grid k 11, −2.16 cents, **its final C attack at film 48.862 s = 'know.' release + 0.152 s, f1466**) + SFX → `public/audio/soundtrack.wav` (2,411,200 samples = 1507 × 1600), `artifacts/soundtrack_report.json`. **Owns the KEY FRAMES `K`** (→ `props.audio` → `T.sfx.*`) and the motion constants |
| `build_props.py` | caption pages (24 + the settle CTA; lesson-3 re-flows), honesty meter, **the black-body world** (`props.glow`, `props.rail`, `props.rungs`, `props.marks`, `props.zeros`, `props.window`), placards (5), root labels → `artifacts/props.json` + `props.generated.ts`. Asserts: no glow before the sweep / below the Draper point, every seated rung on the rail, marks crossed in order, theme.ts FITS / window / rail == the measurements, the settle still (lesson 25), every root string + scene literal in `verified_on_screen_strings`, nothing from `forbidden_on_screen`, no 'NASA' (lesson 32) |
| `theme.ts` | `FONT` (display / mono / caption / tab), palette `C`, `glass()`, `rgba()`, easings `E`, layout `L` (rail, '?', chip, window, overlay), `FITS` (measured), `AMBIENT` |
| `time.ts` | `useT()`: `at/end/word`, `scene/section`, `sfx.*`, `glow(f)`, `rail(f)`, `railY(L,f)`, `railYK(K,f)`, `floorY(f)`, `rung(id)`, `mark(id)`, `zeros(f)`, `win(f)`, `media(id)`, `seat`, `driftFrame`, `loopFrame`; `prog`, `remap`, `lerp` |
| `shared/` | **`blackbody.ts` (THE ENGINE) + `blackbody.test.mts`**, `GlowField` (`Forge`, `GlowField` root), `Ladder` (root), `Window` (`WindowView`, `WindowTags` root; `WindowFrame`, `mediaAlpha` exported), `FilamentStroke` (`Filament`, `FilamentQ`), `Type` (`measure`, `fitSize`, `Rich`, `Sci`, `Label`, `RungLabel`, `hatch`), `Icons` (`Arrow`, `CurvedArrow`), `Grain`, `noise` |
| `overlay/` | `Captions` (+ `heatColour`), `HonestyTab`, `PlacardRail` (+ `SettleCta`), `Tag` (`SceneTag` for scenes) |
| `check_hooks.py` | `python3 check_hooks.py scenes shared overlay` → **0 violations** |
| `scenes/` | `index.ts` (registry), `_stub.tsx`, **`scenes/u1/` … `u4/`**: one STUB per scene (name = scenes.md component). sc03 / sc05 stubs carry a FOUNDATION DEMO (`RungLabel`; replace it) |
| `stills.cjs`, `still.sh` | batch stills (bundle dir created up front, **deleted in a `finally`**, lesson 12) / one-off stills |
| `contact_sheet2.py` | contact sheet 2 → `renders/foundation_sheet.jpg` |

Rebuild order after any narration change: `process_narration.py` → `align_narration.py` → `build_soundtrack.py` →
`build_props.py` → tsc → stills (run from the repo root, e.g. `HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1 python3
projects/how-hot-can-it-get/align_narration.py`). `prepare_media.py [--force]` only when the assets / fits change (then
`build_props.py`). `fetch_fonts.py` only for a new face / string. Engine test:
`node --experimental-strip-types projects/how-hot-can-it-get/shared/blackbody.test.mts` (ALL PASS).

Render **through the symlink** `remotion-composer/projects/how-hot-can-it-get -> ../../projects/how-hot-can-it-get`:

```bash
cd remotion-composer && npx remotion render projects/how-hot-can-it-get/index.tsx HowHot ../projects/how-hot-can-it-get/renders/<raw>.mp4 \
  --config=projects/how-hot-can-it-get/remotion.config.ts --props=../projects/how-hot-can-it-get/artifacts/props.json \
  --concurrency=3 --crf=18 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
  --public-dir=../projects/how-hot-can-it-get/public          # add --scale=0.25 for segment / test renders (--frames=a-b)
# stills (bundle once): node projects/how-hot-can-it-get/stills.cjs --frames 0,300 --scale 0.5 --out renders/review/<unit>
#                       node projects/how-hot-can-it-get/stills.cjs --scenes ... --layers picture   (no overlay plane)
```

Typecheck: `cd remotion-composer && npx tsc -p projects/how-hot-can-it-get/tsconfig.json` (clean). **Fonts:** only the
four families in `theme.ts`. **Disk is tight (~6.4 GB free on `/`):** render 0.25-scale segments only, review stills at
0.5, delete your test renders, never leave `/tmp/remotion-webpack-bundle-*`.

## 2. Scene contract

```tsx
// scenes/u2/GlowSweep.tsx
export const mount: Mount = { pre: 0, post: 0, z: 1 };                    // frames mounted before from / after to; z
export const GlowSweep: React.FC<SceneProps> = ({ from, to }) => { ... };  // the PICTURE (above window + rail)
export const Overlay: React.FC<SceneProps> = ({ from, to }) => { ... };    // OPTIONAL: tags on the overlay plane
```

- **Build ONLY inside your own `scenes/uN/`.** Keep the scene files' names and export names. Add helper files in your
  folder freely (never import across units). Root, `shared/`, `overlay/`, `time.ts`, `theme.ts`, `types.ts`, the Python
  scripts and `scenes/index.ts` are foundation-owned: **request changes through §7, never edit them.** Delete your
  `<StubLabel>` (and the demos in sc03 / sc05).
- Scenes are mounted by **absolute** frame windows (no `<Sequence>`); `useCurrentFrame()` is the absolute frame.
- **THE ROOT OWNS THE BLACK-BODY WORLD** (mounted once): the forge, **the glow** (colour computed from `glow.k` by the
  engine; intensity `glow.i`), **the whole ladder rail** (the ice floor + its two labels, the spine, 'log scale', decade
  ticks, every rung tick, the compact rung numbers, the three marks, the sweep cursor, the '?', the fray + its label,
  the 'black-body colour' chip, the zeros counter chip), **the window** (all four AI plates, the false-colour view, the
  dim, the frame) and **its AI tags**, placards, tab, captions, CTA. Scenes never redraw or move these; they change only
  through `build_props.py` / `build_soundtrack.py K` (request it, §7).
- What a scene draws: the **hero rung labels** (big number + description at the rung's intro; `RungLabel`, `Sci`), the
  rolling number of sc05 (**read `T.glow(f).k`** so it is the glow's temperature), the lead ingot (sc04), the 48-second
  timer arc (sc06), the beam lines + flash (sc07), the LHC digit groups (sc08), the proton → quark soup inside the dimmed
  window (sc09), '1.4 × 10^32 K' (sc11), 'not a proven limit' (sc12), and their own tags (`SceneTag` in `Overlay`).
  Layer order: forge → glow → window → ladder → **scene pictures** → grain → overlay plane (window tags → scene Overlays →
  placards → tab → captions → CTA).
- **Hooks at the top of every component, before ANY early return** (never in a condition, loop or `.map`). Run
  `python3 check_hooks.py scenes shared overlay` (0) AND a real 0.25-scale render of your range before hand-back (lesson 1).
- **Every trigger goes through `useT()`**: a word (`T.at("s2","fifty-seven")`), a scene edge, a key frame (`T.sfx.*`), a
  root schedule (`T.glow(f)`, `T.railY(L,f)`, `T.win(f)`). Never hard-code a frame or second. A beat that needs a sound or
  a new key frame = a §7 request.
- **SFX on the visible frame (lessons 4, 14, 22):** an element is **fully seated ON its seat frame** with
  `T.seat(f, T.sfx.xxx, frames, dropPx)` (gravity ease-in: still moving several px on seat − 1; the SFX peak is ON the
  seat frame). Check seat − 2 / seat − 1 / seat stills. The root rung ticks use the same seat, so your hero label and
  the tick land together.
- **Safe areas:** no text at y ≥ 1574 or x ≥ 929 (text ends ≤ 912), nothing above y 192 (the stub card there is
  temporary). Reserved: the rail band x 140–214 (and compact labels from x 214 while no window is open), the '?' (x 140–220,
  y 190–315), the chip (x 248–~520, y 210–254), the zeros chip (x 214–~400, 40 px under its rung), the floor band y
  1000–1070, placard rail y 1124–1204, tab y 1236–1290, slab x 140–940 y 1296–1488. Stage y 320–1100; **WINDOW x 220–920,
  y 360–900** (its tags sit inside its bottom corners, y ~846–884).
- **Strings:** verbatim from `scene_plan.metadata.verified_on_screen_strings`, nothing from `forbidden_on_screen`
  (`build_props.py` asserts every `text="…"` / `text: "…"` / `*TEXT|LINE|LABEL|NUM* = "…"` literal in `scenes/u*/`; route
  your on-screen strings through such literals, or take them from the props: `T.rung("dv").num`, `.label`). **Never set
  '^'**: write '1.4 × 10^32 K' through `<Rich text=…/>` / `<Sci mantissa="1.4 × 10" exp="32" unit=" K"/>` (the raised
  smaller '32'). No '→' / '≈' glyphs (`<Arrow>`, `<Rich>`). Display text may overhang its box ~16 px (lesson 15).
- **No blend modes under fading parents** (lesson 24). The root uses none; keep your fills plain colour + opacity.
- **Honesty:** nothing below the Draper point glows (DV, Venus: no glow, no orange halo on their labels — the caption
  'heat' tone is the 1,800 K filament amber there, that is typography, not light); AI media only through the root window
  (tagged by the root); every drawing gets 'drawn' / 'drawn · illustrative' while it carries data. Never name the
  detector in S4 (it resembles a real one; the tag is the generic 'AI illustration').

## 3. Frame table (measured; boundary = anchor onset − 2 f for EVERY scene after sc01)

| scene | component · unit | frames | dur | narration (word onset frames) |
|---|---|---|---|---|
| sc01 | FloorLine · U1 | 0–107 | 107 f · 3.57 s | Cold 16 · has 26 · a 32 · floor: 34 · absolute 62 · zero. 79 |
| sc02 | CeilingQuestion · U1 | 107–210 | 103 f · 3.43 s | So 109 · how 125 · hot 132 · can 140 · it 143 · get? 148 · Is 169 · there 173 · a 176 · ceiling? 179 |
| sc03 | DeathValley · U1 | 210–328 | 118 f · 3.93 s | Death 212 · Valley's 218 · air 233 · once 242 · hit 250 · nearly 256 · fifty-seven 266 · degrees. 297 |
| sc04 | Venus · U1 | 328–481 | 153 f · 5.10 s | Venus 330 · sits 344 · about 352 · four 358 · hundred 369 · sixty-five, 380 · hot 418 · enough 426 · to 435 · melt 437 · lead. 449 |
| sc05 | GlowSweep ★ · U2 | 481–583 | 102 f · 3.40 s | The 483 · Sun's 486 · core 500 · reaches 510 · about 522 · fifteen 530 · million. 552 |
| sc06 | Reactor · U2 | 583–770 | 187 f · 6.23 s | Yet 585 · a 591 · fusion 593 · reactor 612 · in 625 · Korea 630 · held 640 · a 647 · hundred 652 · million 671 · degrees 687 · for 703 · forty-eight 710 · seconds. 733 |
| sc07 | Collider · U3 | 770–932 | 162 f · 5.40 s | The 772 · hottest 777 · we've 797 · ever 807 · made: 814 · lead 846 · atoms 857 · smashed 872 · at 899 · CERN, 903 |
| sc08 | FiveTrillion · U3 | 932–1013 | 81 f · 2.70 s | over 934 · five 942 · trillion 963 · degrees. 980 |
| sc09 | QuarkSoup · U3 | 1013–1141 | 128 f · 4.27 s | So 1015 · hot 1024 · that 1040 · protons 1046 · melt 1064 · into 1077 · a 1084 · soup 1086 · of 1099 · quarks. 1105 |
| sc10 | PlanckTemperature · U4 | 1141–1219 | 78 f · 2.60 s | Beyond 1143 · that 1155 · waits 1168 · the 1178 · Planck 1181 · temperature, 1192 |
| sc11 | ThirtyTwoZeros ★ · U4 | 1219–1348 | 129 f · 4.30 s | roughly 1221 · a 1233 · one 1236 · with 1244 · thirty-two 1252 · zeros, 1271 · where 1298 · our 1302 · physics 1306 · breaks. 1317 |
| sc12 | NoCeiling · U4 | 1348–1411 | 63 f · 2.10 s | So 1350 · heat 1359 · may 1369 · have 1374 · no 1381 · ceiling, 1386 |
| sc13 | EdgeOfKnowing · U4 | 1411–1507 | 96 f · 3.20 s | just 1413 · an 1420 · edge 1426 · to 1438 · what 1440 · we 1446 · know. 1449 (release **1461**; settle 1461–1507) |

Sections: s1 15–209 · s2 209–482 · s3 482–771 · s4 771–1142 · s5 1142–1464 (files incl. their tail pauses).

**Key frames** (`T.sfx`, `build_soundtrack.py K`; SFX already on them; **root** = the root draws it):

| scene | beats |
|---|---|
| sc01 | X1 ember bed fades up from **0**; ice floor hairline draws **34 → 46** (`floorDraw`, root); '0 K = -273.15 °C' SEATED **62** (`floorLabelSeat`, X7 PEAK; root); 'the floor' with the hairline (root) |
| sc02 | camera tilt **107 → 167** (`camTilt`: the floor slides down 40 px; back to 0 over 210–230; root); filament '?' draws **179 → 197** (`qStart`, X3 PEAK on 179; root); dashed spine draws **182 → 202** (`spineStart`, root) |
| sc03 | WINDOW opens **210–218** onto K1 (forward; 'AI impression'; X2 hiss texture to ~487; root); DV tick SEATED **266** (`dvSeat`, X7; root) — **U1 hero label on 266**; false colour fades in **297–305** (`lutOn`, 'false colour' tag; root) |
| sc04 | plate crossfade K1 → S2 **328–336** (`venusXfade`; false colour clears; 'AI impression · not a photo'; root); Venus tick SEATED **358** (`venusSeat`, X7) — **U1 label on 358**; Draper mark 'first visible glow ~525 °C' **418** (`draperMark`, root); **U1 lead ingot slumps from `leadMelt` 437** |
| sc05 ★ | window closes **481–489** (root); **glow sweep `sweepStart` 483 → `sunCoreSeat` 552** (piecewise in log10 T, coordinator fix round): 737 K → the Draper point (525 °C) ON **490**; a SLOW log-linear DWELL 798 K → 40,000 K over **490–545** (red ~490–500, orange ~500–510, yellow-white ~512–524, blue-white ~527–545: 1.83 s); a fast ease-in roll 40,000 K → 15 million °C over **545–552**; marks "Sun's surface ~5,500 °C" **518**, 'colour stops changing past ~40,000 K' **545** (root); cursor bead rides the rail (root); 'black-body colour' chip from **483** (root); Sun's-core tick SEATED **552** (X4 swell CREST + X7) — **U2's rolling number = `T.glow(f).k − 273.15` until 552, then '~15,000,000 °C' + "Sun's core"** |
| sc06 | window opens **583–591** onto K2 (forward to its last frame ~734, then held; push 1.00 → 1.03; X5 hum; root); rail re-scales 583–607; KSTAR tick SEATED **652** (`kstarSeat`, X7) — **U2 label on 652**; **U2 48-second timer arc from `timerArc` 710** |
| sc07 | plate crossfade K2 → S4 **770–778** ('AI illustration'; root); **U3 beams meet + FLASH ON `beamFlash` 872** (X6 thump PEAK there) + 'drawn' |
| sc08 | rail compresses **932–942** (`compress`); window dims to 0.55 (932–942); **U3 '> 5,000,000,000,000 K' digit groups SEAT on `lhcGroupSeats` 942 · 950 · 957 · 964 · 971** (X7 light), **' K' + 'LHC · CERN · 2012 · record estimate' + LHC tick SEATED `lhcSeat` 980** (X7 loud); zeros chip '12 zeros' SEATED 980 (root) |
| sc09 | window dims to 0.8 **1013–1023** (`soupStart`; X2 soft rising hiss); **U3 proton → quark soup, melting on `protonMelt` 1064** + 'drawn · illustrative' + 'quark-gluon plasma' |
| sc10 | window closes **1141–1149**; camera drifts to the Planck view **1141–1181** (`drift`; every compact number shows; root); Planck tick + 'Planck temperature' **1181** (`planckMark`, X3 soft; root); '?' dims to half 1181–1196; zeros chip moves to the Planck rung 1181–1201 |
| sc11 ★ | zeros chip 12 → 32 on **`zeroTicks` 1221 · 1226 · 1230 · 1233 · 1236 · 1238 · … · 1254 · 1256 · 1259 · 1262 · 1265 · 1268 · 1271** (X7 ×20, 32 ON 'zeros' 1271; root); **U4 '1.4 × 10^32 K' from `sciWrite` 1271**; rail frays **1317–1331** + 'where known physics stops working' (`fray`, NO SFX; root) |
| sc12 | NO SFX from 'So' (1350, asserted); glow eases to its settle intensity **1350–1395** (root); '?' fades out **1386–1406** (`qFade`, root); **U4 'not a proven limit' (on 'ceiling' 1386)** |
| sc13 | NO SFX; release **1461** (`knowEndFrame`); duck released 48.71 → 48.84 s; **chord 1466** (`chordFrame`); CTA **1465** (`ctaFrame`); tab IDLE 1459 → 1465; every root channel constant from 1461 |

Captions: 24 pages (`props.captionPages`), **'heat'** on fifty-seven, four, hundred, sixty-five, fifteen, million ×2,
hundred, forty-eight, five, trillion, one, thirty-two (the glow's current black-body colour, lifted; amber before the
glow), **'ice'** on 'floor:'. Placards: 2–210 · 216–481 · 487–770 · 776–1141 · 1147–1461. Honesty tab (lesson 3, keyed
to page starts): IDLE 0 · MEASURED 16 · IDLE 109 (the question) · MEASURED 212 · (pulse) 330 · (pulse) 483 · (pulse) 585 ·
PROBABLY 772 · MEASURED 1015 · (pulse) 1143 · PROBABLY 1350 · IDLE 1465. Keep each claim's visual on screen while its
state shows; any element tied to one claim is gone before the next claim's state (lesson 31).

## 4. Known asset issues and the chosen workaround (assets_report quality_concerns)

| asset | issue | workaround | scenes |
|---|---|---|---|
| **s3 narration** | 0.22 s baked-in pause 'held [ ] a hundred' | cut to 0.043 s (process_narration.py); QA A: listen | sc06 |
| **'know.'** | 6.2 dB (7.0 measured on the clean s5) under its sentence | +5.5 dB constant broadband lift on the voice lane (§5) | sc13 |
| **music** | C major (asked D), NO IV–V–I, ~+11 dB staircase (src 19.0 / 32.0 / 44.5 s) + dip 39.5–44.5 s | the final strong attack (src 51.207 s) IS the chord, landing 0.152 s after 'know.'; head on the grid (k 11, src 2.408 s), −2.16 cents; level evening ±7 dB, 0.6 s smoothing (bed 1 s RMS flat −21.3 ± 0.5 dB pre-mix) | all |
| **K1** | Kling forward glide (near ground 1.9 px/f) | FORWARD only, no ping-pong; the fit crops the near ground (window shows source y 12.7–52.9 %); 126 of 151 frames used | sc03 |
| **K2** | slow push-in, clip 151 f < the 195 f window span | forward, then the last frame holds (from ~734) under a code push 1.00 → 1.03 | sc06 |
| **S1 framing** | horizon 30.8 % (plan 45 %) | measured fit puts it at 45 % of the window | sc03 |
| **S2** | very saturated orange | kept as generated: rocks sky-lit, no glow added (honesty) | sc04 |
| **S4** | resembles a real detector | generic 'AI illustration' only; never named. Placard 4 changed (coordinator) to 'CERN LHC · lead-ion collisions · Aug 2012 · Guinness World Records' (no experiment named; fine print unchanged; scene_plan updated, schema-valid) | sc07–sc09 |
| **SFX phone band** | X1–X6 almost entirely outside 300–4000 Hz; X7 = 8-click ratchet | every SFX gets `with_harmonics` and/or a band-limited body; X7 = ONE click cut 0.128–0.192 s (transient 0.158 s) + 1–3 kHz body; table §11 | — |

## 5. The ending (finished line) and the loop rule

- "So heat may have no ceiling, just an edge to what we know." is released at **f1461** (48.71 s, the last voiced
  10 ms of s5). 'know.' (clean s5 10.245–10.64 s: /n/ onset where 2–6 kHz drops with LF steady) gets a smooth BROADBAND
  gain of **+5.5 dB** on the voice (raised-cosine in over 40 ms before its onset, out over 30 ms ending at the release;
  constant over the word, the falling cadence kept; the limiter does 0.0 dB on it): voiced RMS 'know' − sentence
  −7.0 dB → **−0.1 dB** in the final premix (know −14.7 vs sentence −14.5 dBFS). Then −12 dB extra duck + 4 dB 300–4000 Hz lift on
  the word: **voice over bed in 300–4000 Hz +26.0 (n+o) / +25.7 (o) / +19.1 (breathy tail) dB** (asserted ≥ +12).
- **Settle 1461–1507 (46 f):** the bed's final C attack at **48.862 s (f1466) = release + 0.152 s**, at its own level
  (duck released before it), ringing naturally (~5 s decay; 1.37 s in film), last 0.1 s faded. **Every root channel is
  constant from 1461** (asserted in `build_props.py`: glow k / i, rail lo / ppd / camY / floor / spine / fray / q / qAlpha
  / cursor / chip / compactVis, window, zeros); grain freezes on frame 0's seed (`T.loopFrame`). The full ladder (floor →
  Planck) stands in the low blue-white glow (i 0.42); slab: "Floor or ceiling - which is stranger?" (two lines,
  Bricolage 46 px in the glow's lifted colour); tab IDLE. **No unit element may change after 1461.**
- **The last picture frame ≠ frame 0** (frame 0 is the dark forge; the end is the lit ladder): a loop export would need
  its own tail — not built (the channel's rule: finished line; loop optional only).

## 6. Shared helper APIs (all frames absolute)

```tsx
const T = useT();
T.at("s2","fifty-seven"); T.end("s5","know"); T.scene("sc08"); T.section("s4"); T.sfx.dvSeat; T.sfx.lhcGroupSeats[i]
T.glow(f) -> { k, i, rgb, css(alpha) }        // k = glow temperature (K); rgb = bbRgb(k) (computed); i = intensity
T.rail(f) -> { lo, ppd, camY, floor, spine, fray, q, qAlpha, cursor, chip, compactVis }
T.railY(L, f) / T.railYK(kelvin, f) / T.floorY(f)   // screen y on the ladder (L = log10 kelvin), incl. the camera
T.rung("dv"|"venus"|"suncore"|"kstar"|"lhc"|"planck") -> { kelvin, L, num, label, seat, compactFrom, glows }
T.mark("draper"|"sunsurface"|"converge") -> { kelvin, L, text, at };  T.zeros(f) -> { value, alpha, L }
T.win(f) -> { open, dim, lut };  T.media("K1"|"S2"|"K2"|"S4") -> the plate schedule
T.seat(f, seatFrame, frames=8, dropPx=18) -> { k, y, opacity, seated, visible }   // gravity drop, fully down ON seatFrame
T.loopFrame(f)  T.driftFrame(f)  prog / remap / lerp
// shared/blackbody.ts (pure): bbRgb(K) bbHex(K) bbCss(K, a) bbXYZ(K) bbUV(K) lighten(rgb, k) DRAPER_K SUN_SURFACE_K CONVERGE_K C_TO_K
<RungLabel x y num label size=96 labelSize=34 color dy opacity anchor/>   // hero label; num via <Rich> (draws ^NN, ≈)
<Sci mantissa="1.4 × 10" exp="32" unit=" K" size color/>   <Rich text size color/>   <Label x y text size variant/>
<Filament d q kelvin width opacity/> (inside your <svg>)   <FilamentQ .../> (root's '?')   <Arrow/> <CurvedArrow/>
<WindowFrame open>…</WindowFrame>   // the frame look for your OWN drawings only (AI plates go through props.window)
<SceneTag x y enter exit text variant/>   // in your Overlay
measure(text, "display"|"mono"|"monoMed", size) / fitSize(...) / vmetrics(...)
FONT / C / E / L / FITS / AMBIENT
// ROOT ONLY (never mount in a scene): Forge GlowField WindowView Ladder Grain WindowTags PlacardRail HonestyTab Captions SettleCta
```

**The black-body engine** (`shared/blackbody.ts`): Planck's law × the CIE 1931 2° CMFs (the published 5 nm 380–780 nm
table, from colour-science) → XYZ → linear sRGB (IEC D65 matrix, no adaptation) → negatives clipped → max channel = 1
→ sRGB gamma; Rayleigh–Jeans form above c2/(λT) < 1e-7 (finite at 1.4e32 K); cached per 0.001 decade. **Unit test
(`blackbody.test.mts`): 28/28 PASS** — 16 points within 2 levels of an independent 1 nm 360–830 nm integration
(800 K #FF0000, 1,000 K #FF1700, 1,500 K #FF6600, 3,000 K #FFB86D, 5,800 K #FFF1EA, 10,000 K #CDD9FF, 40,000 K #9EB8FF,
1e9 K #94B1FF), 1,000 K deep orange-red, 5,800 K ≥ 225 every channel, ≥ 40,000 K blue-white, 40,000 K within 12 levels /
du'v' 0.0095 of the limit, 1e5 K within 4, 1e6 K = 1e9 K, the Sun's core and Planck == the limit, the ramp monotone.
**The glow** (`GlowField`): a bright core in the colour lifted 45 % toward white at the top centre + a broad halo (the
lower frame stays forge-dark, so blue-white reads as light, not a blue night), a faint floor bounce, a static colour
dither; masked to ~40 % from the tab (y 1236) down. **The rail** (`Ladder`): y = 990 + camY − (L − 2.42)·ppd; views:
sc03–sc04 top 3.18 (ppd 842: Venus y 613, Draper y 584), the sweep zooms out keeping the cursor 0.3 decade under the top
(ppd 127 at 552), KSTAR top 8.40 (ppd 107), LHC top 13.1 (ppd 60), Planck top 32.55 (ppd 21.2; Planck y 358). Mark labels
thin out under ppd 70 and hide behind the window except during their own first 3 s; all labels de-overlap bottom-up
with leaders.

**Measured cost:** full-length 0.25-scale render (1507 f, 270×480, concurrency 3): **1 min 21 s, exit 0, strict decode
OK, 1507 frames** (deleted after the check). Stills at 0.5: ~0.5 s each.

## 7. Unit split for 4 parallel scene builders (contiguous; heroes in different units) and hand-offs

| unit | scenes | frames | owns (picture / overlay) |
|---|---|---|---|
| **U1 the floor → the question → Death Valley → Venus** | sc01–sc04 (`scenes/u1/`) | **0–481** (481 f; sc01–sc02 are mostly root) | optional cold / dark accents in sc01–sc02 (NO glow, nothing warm but the root '?'); DV hero label '56.7 °C' + 'Death Valley · 1913 · air' SEATED **266** beside its rung (replace the demo; keep clear of the window's bottom-left 'false colour' tag x 236–~420 y 846–884 and the 'AI impression' tag bottom-right); Venus '~464 °C' + 'Venus surface' SEATED **358**; the drawn lead ingot (Iron grey, unlit) slumping into a puddle from **437** + 'lead melts at 327 °C · drawn' (a label; `SceneTag` or `Label`); everything out by **481** (the root compact numbers fade in 481–489 as the window closes) |
| **U2 the sweep (HERO 1) → the reactor** | sc05–sc06 (`scenes/u2/`) | **481–770** (289 f, hero) | the rolling number driven by `T.glow(f).k` (°C = K − 273.15; your rounding / digit roll, Saira, coloured by the glow) landing as '~15,000,000 °C' + "Sun's core" ON **552** (replace the demo; keep clear of the rail labels x 140–~560 near the bottom and the chip); optional emphasis of the colour stopping (the root marks + chip carry it); out by **583** (window opens); KSTAR '100,000,000 °C' + 'KSTAR · Korea · 48 s · 2024' SEATED **652**; a thin 48-second timer arc around the KSTAR label from **710** (no SFX planned; §7 if you want one); out by **770** |
| **U3 the collider → five trillion → quark soup** | sc07–sc09 (`scenes/u3/`) | **770–1141** (371 f) | two drawn beam lines converging on the detector centre (window centre 570, 630) and FLASHING ON **872** + 'drawn' (`SceneTag`); '> 5,000,000,000,000 K' (Saira, ~88 px: fit it — ~21 chars) with digit groups seated on **942 / 950 / 957 / 964 / 971** and ' K' + 'LHC · CERN · 2012 · record estimate' on **980** (over the window dimmed 0.55; keep clear of the zeros chip, x 214–~400, ~40 px under the LHC rung y ~374); the proton (3 quark dots in a glowing bag, blue-white = the glow colour) loosening into a seeded quark soup inside the dimmed window, melting from **1064**, + 'drawn · illustrative' + 'quark-gluon plasma'; everything out by **1141** (window closes 1141–1149) |
| **U4 Planck (HERO 2) → no ceiling → the edge → settle** | sc10–sc13 (`scenes/u4/`) | **1141–1507** (366 f) | optional sc10 accent (the drift, the Planck mark and '?' dimming are root); '1.4 × 10^32 K' via `<Sci>` (Saira ~104 px) writing out from **1271** near the Planck mark (y ~358; keep clear of 'Planck temperature' / the zeros chip at x 214–~430, y 330–420 and the fray label y ~296–326); 'not a proven limit' on **1386** (sc12); nothing of yours may change after **1461**; your sci number may stay to the end (constant) |

Seams (agree each with a shared still before building; compare `from − 1` vs `from`):

| seam | outgoing → incoming | both sides must match |
|---|---|---|
| **481** sc04 → sc05 | U1 → U2 | U1's labels / ingot gone by **481**; the window close + compact numbers are root; U2 draws nothing before 481 (its number starts at 483) |
| **770** sc06 → sc07 | U2 → U3 | U2's KSTAR label / arc gone by **770**; the K2 → S4 crossfade is root |
| **1141** sc09 → sc10 | U3 → U4 | U3's soup / LHC label gone by **1141** (the window closes 1141–1149, root); U4 draws nothing before 1143 |
| **0 / 1506** | U1 / U4 | NOT equal by design (§5) |

A scene drawing past its `to` (inside its `post`) draws ONLY its own outgoing elements (fading), never anything of the
incoming unit's. All `mount.post` are 0 now; ask (§7) if you need one. Unit-internal seams: 107, 210, 328 (U1); 583
(U2); 932, 1013 (U3); 1219, 1348, 1411 (U4).

### §7 hand-off protocol (how to request a shared change)

1. Builders **never edit** `shared/`, `overlay/`, `time.ts`, `theme.ts`, `types.ts`, `Composition.tsx`, `Root.tsx`,
   `scenes/index.ts`, `props*.{json,ts}` or any Python script; not even "a one-liner". Never touch another unit's folder.
2. To request: send the lead ONE message headed `§7 REQUEST uN → foundation` with: what (a key frame, a schedule change,
   a rail / glow / window channel, a label position, a font/glyph, a helper prop, a new verified string), why (the beat /
   the claim), the exact frames, and the still that shows the problem (`renders/review/uN/...`). Seam requests name both units.
3. The lead relays it (SendMessage) to the foundation owner or applies it, reruns the chain (§1 rebuild order), tsc,
   `check_hooks.py`, re-renders the affected seam stills, and replies to every unit whose frames moved (lesson 19:
   after any global timing change, every unit re-sweeps its collisions).
4. Until the answer lands, build against the current props; never fork a copy of a shared helper to work around it
   (copy-and-adapt inside your folder is fine only for unit-local helpers).

## 8. Quality bar (each unit self-checks before hand-back)

- tsc clean; `python3 check_hooks.py scenes shared overlay` = 0; stills of ≥ 4 frames per scene + every seam's
  first/middle/last frame, LOOKED at; **seat − 2 / seat − 1 / seat stills for every seated element** (lesson 22); one
  0.25-scale segment render of your range (`--frames=a-b`, exit 0); seam PSNRs (`from − 1` vs `from`) reported.
- Every visual landing ON its `T.sfx` frame (still moving on the frame before). Strings verbatim; `build_props.py` passes
  (its literal check scans your folder); no text at y ≥ 1574 / x ≥ 929; no '^' / '→' / '≈' glyphs; every drawing tagged.
- Nothing below the Draper point glows; nothing of yours overlaps the root rail labels / chips / window tags.
- `stills.cjs` cleans its bundle; never leave `/tmp/remotion-webpack-bundle-*`; delete your test renders (disk).

## 9. Divergences from the scene plan

- Film **1507 f (50.23 s)**, not 1515; all 13 windows re-timed (anchor − 2 f); `scene_plan.json` updated (schema-valid).
- The window is x 220–920 (safe_areas), not scenes.md's 'x 160–920' (the rail sits at x 180).
- **Placards in Saira Condensed 700** (IBM Plex Mono can't fit KSTAR / Planck with ≥ 24 px fine print); '≈' and the
  exponent drawn by `<Rich>`.
- The sc05 sweep is piecewise (Draper ON 490, a 55-frame log-linear dwell to 40,000 K at 545, then a 7-frame roll to the
  seat 552), not the planned smooth roll, so the visible colours span ≥ 1.8 s; the colour is always bbRgb(the displayed number).
- The camera tilt in sc02 is 40 px (plan ~120): more would push the floor and its labels under the placard rail.
- Rung labels: the units' hero intros + root COMPACT numbers (no descriptions) while no window is open; the Planck rung's
  number is U4's ('Planck temperature' is the root label).
- Caption pages re-flowed in s1, s2, s3, s5 so every claim starts its own page (lesson 3).
- Music: no IV–V–I; the bed's own final strong attack is the chord (§4). X8 settle tone unused.
- The zeros chip's values '12 zeros' … '32 zeros' are ALL in `verified_on_screen_strings` (added '13 zeros' … '31 zeros'; asserted).
- The planned 'black-body colour' chip sits in the top band (x 248, y 210), not on the rail; it stays to the end.

## 10. Foundation build log: lessons applied

- **Hooks (1):** every hook at the top; `useId` unconditional (Forge, GlowField, Filament, WindowView, Grain). 0
  violations. Full-length 0.25 render exit 0 (§6).
- **Caption onsets (2, 13, 17): all 109 words hand-measured on THE CLEAN WAVs** (1 ms 3-band profiles, 7-band 10.7 ms
  profiles, 5 ms-hop spectrograms; whisper medium.en as a third opinion). Whisper small.en was badly off: s1 'absolute'
  (+16 f: it sat in 'floor'), 'how' (+6.5 f), s3 'in' (+3.5 f), 'hundred' (+5 f h-onset vs whisper), s4 'we've' (+6 f),
  'lead' (−7.6 f), 'at' (+6.8 f), s5 'that' (+4.1), 'waits' (+5), 'the' (+5), 'edge' (+2), 'to' (+4.4). **67 OVERRIDES / 42
  CONFIRMED**; soft (±1–2 f): s1 'zero.' 'a'#2, s2 'Valley's' 'once' 'sits' 'melt', s3 'reaches' 'million.' 'held'
  'degrees', s4 'hot' 'into', s5 'with' 'our'; **s3 'hundred' (a glottal release + aspiration burst 5.68–5.72 s into a 0.3 s breathy, voiced 'hun', whisper +5 f
  later) is the one to listen to; re-checked on a 0.5 ms spectrogram: the /h/ noise starts at ~5.68–5.69, kept 5.690.** QA A must re-measure every onset independently (lesson 13).
- **Honesty tab (3):** keyed to page starts from `script.json claim_tags` (asserted per claim); IDLE on the question and
  the settle. **SFX on the landing (4, 14, 22):** peaks aligned (X7 0.158 → 0.030 s in the cut, X4 crest 1.109 s, X6
  0.007 s, X3 0.062 s); `T.seat` gravity drops; root ticks and SFX share the key frames.
- **Phone band + no dead air (5):** §11; **0 windows < −42 dBFS** (min −37.9 stereo / −40.4 mono fold).
- **Back-to-back pages (6):** butted ≤ 11 f and inside sentences (≤ 21 f); the CTA continues the slab.
- **Banding (7):** glow core + halo + static dither + grain; encode-side dither at mastering. **Kling (8, 27):** K1 forward
  only, K2 forward + hold. **Framing (9):** §1. **Fonts (10):** §1. **Grain seed (11):** `T.driftFrame(T.loopFrame(f))`.
  **stills.cjs (12)** deletes its bundle (verified: none left). **Overhang (15):** labels never clipped.
- **Wording (16, 20, 32):** every root string + scene literal asserted against `verified_on_screen_strings`;
  `forbidden_on_screen` + placards checked; no 'NASA'. **Last word (18, 30):** §5. **Blend modes (24):** none in the root.
  **Settle (25):** asserted constant. **Final cadence (26):** measured from the audio.

## 11. Soundtrack (measured, `artifacts/soundtrack_report.json`)

Stereo 48 kHz 16-bit, 2,411,200 samples = 1507 × 1600. **−14.0 LUFS, true peak −1.6 dBFS.** Bed −19 LUFS before the duck,
level-evened (gain −3.6 … +6.9 dB); head on the grid (k 11 → src 2.389, refined to the attack at **src 2.408 s**),
resampled **−2.16 cents**; final attack **src 51.207 s → film 48.862 s (f1466) = release + 0.152 s** (measured on the
premix bed). Duck **−12 dB** under the voice (median −14.0 incl. the texture dips, p10–p90 −15.0 … −11.9; voice over bed
in 300–4000 Hz median +18.0 dB), released linearly 48.71 → 48.84 s; −4 dB sidechain under each hit, −2 dB under textures.

| SFX | frame | landing | sfx − bed, 300–4000 Hz (150 ms / 30 ms) |
|---|---|---|---|
| X1 ember bed (+harm, body) | 0 → | start (0.6 s fade-in) | +3.5 (50 ms max +8.3) |
| X7 tick (floor label) | 62 | peak | +4.3 / +9.4 |
| X3 filament ('?') | 179 | peak | +10.9 / +12.8 |
| X2 hiss (window, texture) | 210 → ~487 | start | texture, under speech; 50 ms max +12.0 |
| X7 ticks (DV, Venus) | 266 · 358 | peak | +7.4 / +13.2 · +7.5 / +14.2 |
| X4 swell (crest) + X7 (louder) | 552 | peak | +13.5 / +16.7 |
| X5 hum (window, texture) | 583 → ~776 | start | texture; 50 ms max +12.9 |
| X7 tick (KSTAR) | 652 | peak | +8.5 / +15.7 |
| X6 thump (+shimmer tail) | 872 | peak | +11.1 / +14.8 |
| X7 ticks (LHC groups, light) | 942 · 950 · 957 · 964 · 971 | peak | +2.3…+4.2 / +8.0…+11.3 |
| X7 tick (LHC, louder) | 980 | peak | +6.9 / +12.0 |
| X2 hiss (soup, rising) | 1013 → ~1147 | start | texture, mostly under speech (50 ms max −2.9) |
| X3 filament (Planck, softer) | 1181 | peak | +9.1 / +10.5 |
| X7 ×20 (zeros 13 … 32) | 1221 … 1271 | peak | −0.9…+7.8 / +5.3…+15.2 |

Nothing from 50 ms before 'So' (s5, 45.00 s) to the end (asserted); no SFX on 'breaks'.

## 12. Test render and contact sheet 2

Full-length 0.25-scale render (1507 f, 270×480, concurrency 3): **exit 0, 1 min 21 s, strict decode OK, 1507 frames**
(deleted after the check: disk). Contact sheet 2: **`renders/foundation_sheet.jpg`** (one stub frame per scene; the glow
engine's states on the picture layer: dark forge, the false-colour window, first glow ~975 K (f493), orange ~1,650 K (f501),
yellow-white ~3,400 K (f511), converged ≥ 40,000 K (f545), the compressed rail, the Planck view + fray, the settle; sc06 with the safe
zones). Review stills: `renders/review/foundation/sheet/`, `sheet_pic/`.

## 13. Fix round (coordinator, after the units)

| item | change |
|---|---|
| sc05 sweep | piecewise: Draper ON 490, log-linear dwell to 40,000 K over 490–545, roll to 552 (marks 518 / 545) |
| placard 4 | 'CERN LHC · lead-ion collisions · Aug 2012 · Guinness World Records' (no experiment named) |
| zeros chip | '13 zeros' … '31 zeros' added to verified strings |
| honesty: cursor + chip below the Draper point | the sweep bead and the 'black-body colour' swatch are UNLIT Iron while T.glow(f).k < DRAPER_K (f483–489); lit from 490 (the displayed number ≥ 525 °C) — no red beside the Venus value |
| lesson 31: root labels | 'Planck temperature' fully visible ON its seat 1181 (fade 1173 → 1181); the three mark labels fully visible ON their `at` (fade over the 8 f before); compact numbers reach full by `compactFrom`; the fray label full ON 1317 |
| placard 5 fine print | 'where gravity needs a quantum theory' (u4's 'not a proven limit' note is the only one) |

### §13b QA fix round (qa_a / qa_b / qa_c) — SFX key frames unchanged

| item | change (frames) |
|---|---|
| A-M1 / B1 "Sun's core" | U2 GlowSweep: the label appears ON the seat 552 (no drop, no pre-fade); nothing under an intermediate number (545–551 clean) |
| A-m2 rolling number | hidden until the Venus plate is gone: 0 on 488, 50 % on 489, full ON 490 (Draper, '~525 °C') |
| B3 opening | the floor hairline (dim Ice) + 'the floor' (30 px) + '0 K = -273.15 °C' (54 px, ONE copy: dim from f0, lights over 56–62, full ON 62 + X7) visible from frame 0; a faint unlit spine from f4; an UNLIT iron '?' outline from f10–30; the filament '?' track starts 178 so its first lit pixels land ON 179 (X3); nothing warm before 490 except the '?' |
| B8 | caption 'heat' words are neutral Bone until the glow exists (i ≤ 0.05) |
| B9 | `glowLum(T)` (shared/blackbody.ts): luminance 0.35 at the Draper point → 1 by ~1,500 K (log ramp), hue unchanged; applied to `T.glow().css()` (chip swatch, bead, KSTAR leader / number) and to U2's number (floored 0.55 for legibility). 490 reads dim dull red |
| B7 | the false-colour view: everything above the ridge takes the LUT's cool end (solid to window-y 100, fading out by 170); the ground stays hot; still tagged 'false colour' |
| B4 | AI tags CUT at the crossfade midpoint (one slot, one text, a tag on every frame an AI plate is visible): 'AI impression' to 331, 'AI impression · not a photo' from 332; same slot at 774 for K2 → S4 (both 'AI illustration') |
| B10 / C-m3 | window open: out-quad over 6 f from `windowOpen − 1` (first visible frame ON the hiss / hum: 210 = 31 %, 211 56 %, 212 75 %, full 215; same at 583); close: ease-in-out over 8 f (481–489, 1141–1149); WindowFrame no longer adds a second ease |
| B5 | `rail.compactVis = clip(1 − open / 0.35)`: compact numbers and mark labels are hidden while a plate is up (gone by 211 / 584) and return only once the closing plate is mostly gone (~486–489, ~1146–1149); the Draper label keeps its intro over the Venus plate |
| B6 / A-m3 zeros chip | fades out 1159–1167 under the LHC rung, jumps (unseen) to the Planck rung at 1169, fades back in 1181–1189; never crosses the LHC compact number |
| B2 | '~' in rail / compact labels is a drawn tall tilde (shared/Type.tsx `Tilde`) |
| B11 | the fray: Ash, 3.5 px, opacity 0.95 → 0.7; 'where known physics stops working' Bone 85 %, 500 weight, 25 px on a 0.78 slab |
| B12 | U2 Reactor timer dial: r 30 → 46, arc 5 → 8 px, hand / ticks thicker |
| A-m1 | mark → 'colour barely changes past ~40,000 K' (scene_plan verified strings ×4; research_brief data point [CONVERGE]: Planckian locus → limiting chromaticity, + our computation: 40,000 K is du'v' 0.0095 from the T → ∞ limit; 20,000 K 0.0207; 6,500 K 0.0731); both artifacts schema-valid |
| A-m6 | BUTT_GAP 11 → 13: the s1 gap ('zero.' → 'So', 94–109) is now butted (slab stays up) |
| A-m8 | the KSTAR placard enters with sc06 (589 after the page guard), not 485 |
| A-m4 | X5 hum: + a 300–3000 Hz body, −19 → −14 dB peak; X2 soup hiss −18 → −14 dB. SFX-lane 300–4000 Hz level vs before: hum +3.8 / +4.5 dB, soup +4.0 dB (ducked under speech as before) |
| A-m5 | final fade 0.1 → 0.4 s: cos² to −8 dB (`FINAL_FADE_FLOOR_DB`), then a 10 ms ramp to 0; new assert: mono-fold windows ≥ −41 over the whole premix (1 dB margin for AAC) |
| C-m2 | verified: from 1461 the grain / drift are constant (1461→1462 mean |d| 0.011, only the planned meter → IDLE fade at y 1244–1281 before the CTA 1465) |

## 14. Final render and master (QA fix round)

- Contracts builders read: `WindowFrame` no longer eases (`open` is used linearly; the ease is in `props.window.open`);
  `rail.compactVis = clip(1 − open / 0.35, 0, 1)` (0 while a plate is more than ~1/3 visible).
- Checks: build_soundtrack (all asserts) → build_props (full scan, settle still from 1461) → tsc 0 → check_hooks 0 →
  black-body test ALL PASS → review stills `renders/review/fix3/` (0–180, 209–214, 300–336, 481–556, 582–625, 720, 770–777,
  1141–1201, 1317, 1400; settle 1459–1466 diffed at full res).
- Full-res render `renders/how_hot_raw.mp4`: exit 0, 3 min 25 s, 1507 f.
- Master `renders/how_hot_master.mp4` (finish_master.sh): 19.3 MB, 1080×1920, 50.233 s, 1507 f, strict decode clean,
  **−14.0 LUFS, TP −1.7 dBTP, LRA 3.2 LU**, no silence > 0.7 s; per-second video peak 7.29 Mbps (s26).
  100 ms windows on the master (10 ms hop, whole film): stereo min −37.9 (48.69 s), mono-fold min −40.5 (15.72 s), 0 below −42;
  last 100 ms windows (end-aligned, 50 ms steps) stereo −35.2, −32.2, −30.0, −29.1 …; mono −40.3, −36.6, −33.8 ….
- Contact sheet 3: `renders/master_sheet.jpg` (65 % of each scene, sc13 at T−3, 360×640, 7 columns, title row).
