# Art Direction: "How Fast Can Anything Go?"

Video 16. Concept C1 **Speed Ladder** (video 13's ladder / counter / window engine, re-dressed; approved). Lean build:
`new_project.sh` kit + video 13's engine + video 15's pipeline scripts; 2 scene builders; `qa_auto.py`, then 1 QA agent.
Companions: `scenes.md` (generated) and `artifacts/scene_plan.json` (source of truth).

## Design read

A calm climb up one speed ladder, from walking pace to light, ending at a wall that never moves.

- **The rail.** One vertical steel log-scale rail in km/h (1 to 10^9) at x ~250, labelled "km/h · log scale", with
  decade ticks (each tick is 10×). At the top, a red line "c".
- **The marker is the signature device.** A single white-cyan glowing marker climbs rung by rung; each rung's label
  seats WITH its number when the marker arrives (lessons 33/46). Speed streaks behind it, length = log10(speed). A ZEROS
  counter (0 → 9) ticks top right.
- **Rungs:** WALK · ~5 · CHEETAH · ~100 · FALCON (dive) · ~390 (hatched "commonly cited", PROBABLY) · SOUND · 1,235 ·
  EARTH (orbit) · ~107,000 · PARKER (fastest built) · ~692,000 · LIGHT · 1,079,252,849.
- **Hero 1 (sc05).** A small "YOU" tag jumps from WALK to Earth's orbit, with a drawn orbit inset.
- **The wall (sc08–sc10).** A light beam races to the top; the marker climbs toward "c" but slows; an "ENERGY NEEDED"
  bar grows without limit beside a small drawn curve.
- **Hero 2 (sc11).** "LHC protons · 99.9999991 %" types digit by digit; the marker creeps to just under "c" with a
  bracket "the gap" that stays to the end. The marker never touches "c" (asserted).
- **Windows** (tagged "AI impression"): cheetah, falcon dive, Parker Solar Probe near the Sun.

**Colour rules:** white-cyan only for the marker and the light beam; red only for the "c" line. No temperature colours
(not black-body), so it reads differently from video 13.

## Palette

| Name | Hex | Use |
|---|---|---|
| Night Ink | #070A12 → #0D1424 | Sky |
| Steel | #AEB8C2 | Rail, ticks, labels |
| Marker | #BFF6FF | ONLY the marker and the light beam |
| Wall red | #E5484D | ONLY the c line |
| Chip / card | #141B2B | Chips, readout card |
| Bone | #F4EFE6 | Text |

## Type

Video 13's display and mono faces (slashed zeros for numbers); Bricolage Grotesque 800 captions; Spline Sans Mono 600
tab. Labels ≥ 28 px, fine print ≥ 24 px. Arrows are SVG.

## Layout

Rail x 180–320, y 380–1080. Window x 470–920, y 420–900. Counter x 640–920, y 220–340. Placard rail y 1124–1204, tab
y 1236–1290, caption slab x 140–940, y 1296–1488. No text at y ≥ 1574 or x ≥ 929.

## Ending

"Close. But never all the way." ends complete. The full ladder, the marker just under "c" and the gap bracket hold; the
resolved chord lands ~0.15 s after "way", the picture holds 1.5 s, the music fades over the last 0.6 s. The slab shows
"What's the fastest thing you've ridden?" with the tab idle.
