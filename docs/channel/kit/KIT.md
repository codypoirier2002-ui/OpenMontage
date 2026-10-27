# Channel kit

The kit holds the parts of an atelier build that are the same on every video. Copy them; don't rewrite them.
`bash docs/channel/scripts/new_project.sh <id> <CompName>` copies `template/` into `projects/<id>/`, substitutes the id
and composition name, creates the folder layout and the `remotion-composer/projects/<id>` symlink.

The kit is **copy-then-edit templates**, not a shared library: each video's `theme.ts` / `time.ts` / `types.ts` differ,
so the overlay imports them from the project. Taken from video 14 (QA passed).

## What the kit gives you (do not rebuild)

| file | what |
|---|---|
| `index.tsx`, `Root.tsx` | entry + `<Composition id=<CompName>>` (duration from `props.timeline.total_frames`) |
| `remotion.config.ts`, `tsconfig.json` | render / typecheck through the symlink |
| `stills.cjs`, `still.sh` | batch stills (bundle deleted in a `finally`, lesson 12) / one-off stills |
| `check_hooks.py` | rules-of-hooks check: `python3 check_hooks.py scenes shared overlay` |
| `overlay/Captions.tsx` | the channel caption slab (x 140–940, y 1296–1488), word states, pre-roll, slab held across gaps (L6) |
| `overlay/HonestyTab.tsx` | MEASURED / PROBABLY / MAYBE tab + sublabel, keyed on caption page starts (L3) |
| `overlay/PlacardRail.tsx` | citation placards (y 1124–1204) + `<SettleCta>` for the finished-line ending |
| `overlay/Tag.tsx` | `DrawnTag` / `SceneTag` honesty and provenance chips (≥ 24 px, L31) |
| `shared/Type.tsx` | `measure`, `fitSize`, `Rich` (drawn tall `~`), `Label`, `hatch` |
| `shared/noise.ts` | deterministic `rnd` / `noise1` / `flicker` (never `Math.random`) |

## What the foundation agent still writes per video

`theme.ts`, `time.ts`, `types.ts`, `Composition.tsx`, the `shared/` engines (the look's devices), `fetch_fonts.py`
(writes `shared/metrics.generated.ts`), `process_narration.py`, `align_narration.py`, `build_soundtrack.py`,
`build_props.py`, `prepare_media.py`, `sync_scene_plan.py`, the scene stubs and `BUILD.md`. Copy the newest project's
versions as a starting point when `projects/` still exists.

## Contract the overlay expects

**`theme.ts` exports**
- `FONT`: `caption` (Bricolage Grotesque 800), `tab` (Spline Sans Mono 600), `display`, `mono`.
- `C`: `bone`, `nightInk`, `steel` (fine print), `shadow` (tag chips), plus one colour per caption tone; `Type.tsx` also uses `paper`, `paperInk`.
- `L`: `slab {x, y, w, h, textX, textRight}`, `tab {x, y, w, h}`, `sublabel {x, y, w, h}`, `placard {…}`, `drawnTag {x, y}`.
- `E.meter` (the tab's easing), `glass(alpha)`, `rgba(hex, a)`.

**`time.ts` exports** `prog(frame, a, b, ease?)` and `useT()`, whose result has at least `cta` (`props.cta`).

**`types.ts` exports** `CaptionTone` (`"plain"` + the video's tones), `CaptionWord`, `CaptionPage`, `MeterState`,
`MeterKey`, `Placard` (shapes as in video 14).

**Per-video edit points** (marked `KIT:` in the files): the caption `TONE` / `GLOW` maps (one entry per tone), and
the header comments, which describe video 14.

**`props.json` keys every tool relies on** (build_props.py must emit them; `qa_auto.py` and `records.py` read them):
`timeline` (`fps`, `total_frames`, `sections`, `scenes`, `words` in film seconds), `captionPages`, `meter`,
`placards`, `cta`, `settle.chordFrame`, `audio` (key frames). `artifacts/timeline.json` must carry
`<lastword>_end_frame` / `_end_seconds`, and `soundtrack_report.json` the `sfx[]` rows (`frame`, `placed_at_s`,
`landing_offset_in_sample_s`) and `frames`.
