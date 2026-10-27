# Art Direction: "How Hot Can It Get?"

Video 13, the partner to video 11. Concept C1 **Black-Body** (d-007, approved), Remotion atelier (d-008, d-009, approved).
Companions: `scenes.md` (per-scene inventory, generated) and `artifacts/scene_plan.json` (source of truth).

## Design read

A youth science short in warm, building wonder. In video 11 the frost was the meter; here **the light is the meter**. One dark forge-iron frame takes on the computed black-body colour of the current rung, so the screen glows the real colour of each temperature, until colour itself runs out.

- **Low rungs don't glow.** Death Valley (56.7 °C) and Venus (~464 °C) sit below the first visible glow at about 525 °C, so the frame stays dark. Their windows use a labelled thermal "false colour" view. Visuals never contradict facts.
- **sc05 is the sweep (hero 1).** As the number rolls up to the Sun's core, the light passes through every colour heat makes: dull red, orange, yellow-white (marked "Sun's surface ~5,500 °C"), then blue-white. Then it **stops changing** ("colour stops changing past ~40,000 K"). From the reactor on, the colour holds, and a **zeros counter** and the log-scale **ladder rail** become the meter.
- **sc11 is hero 2.** The zeros counter runs 12 → 32 to "1.4 × 10^32 K · Planck temperature". The rail above it frays into a broken dashed line: "where known physics stops working". The "?" fades and the top stays open ("not a proven limit").
- **The cold floor from video 11** (an ice-blue hairline at y 1060, "0 K = −273.15 °C") is the one cool element and anchors the bottom of the ladder.

**Distinctness:** this is warm light, not blue night (videos 10–11), and there is no paper (videos 6, 7, 9) and no weather graphics (video 12). Saira Condensed and IBM Plex Mono are new to the channel.

## Materials

| Layer | Source | Notes |
|---|---|---|
| Glow field, black-body ramp, ladder rail, rungs, zeros counter, filament "?", lead ingot, beam lines, quark soup | code | Colours computed from temperature (Planck × CIE 1931 → sRGB), unit-tested |
| Death Valley (sc03) | S1 → K1 | "AI impression" plus the "false colour" view |
| Venus (sc04) | S2 still with a code push | "AI impression · not a photo"; the rocks must not glow |
| Reactor plasma ring (sc06) | S3 → K2 | "AI illustration" |
| Collider detector (sc07–sc09) | S4 still | "AI illustration", no logos |

## Palette

| Name | Value | Use |
|---|---|---|
| Forge Black | #0B0907 | Ground |
| Iron | #2A211B | Rail, window frames |
| Ice | #9FC9DA | ONLY the cold-floor callback |
| Black-body ramp | computed per frame | All glow; captions' number colour (clamped for contrast) |
| False-colour LUT | inferno-style | sc03–sc04 windows only, always labelled |
| Night Ink / Bone | #0A0B10 / #F4EFE6 | Channel caption slab and text |

## Type

- **Saira Condensed 700** for rung numbers; **IBM Plex Mono 400/500** for labels, tags and chips.
- **Captions:** Bricolage Grotesque 800 at 58 px. **Tab:** Spline Sans Mono 600. Both are the channel standard.
- Check × ° · ~ > − at the foundation stage. Draw the exponent "32" in code if the font has no superscript, and draw arrows as SVG. Fine print is at least 24 px (lesson 31).

## Layout (channel lower stack)

- **Rail** at x 180, y 340–1060 (log scale, labelled "log scale"). **Windows** x 220–920, y 360–900.
- **Placard rail** y 1124–1204, **honesty tab** y 1236–1290, **caption slab** x 140–940, y 1296–1488.
- **No text** at y ≥ 1574 or x ≥ 929. Glow under the slab and tab is clamped to about 40%.

## Motion

- Motion intensity is 3: slow camera drifts up the rail in sc02 and sc10.
- Rungs seat with ease-in drops on their ticks (lesson 22). The glow sweep is continuous; the counter ticks accelerate then settle.

## Ending

The closing line "So heat may have no ceiling, just an edge to what we know." ends complete. The resolved chord lands about 0.15 s later, found from the audio. The whole ladder is visible from the floor to the Planck mark in a low, warm blue-white glow. Hold 1.5 s with every channel constant. The slab shows "Floor or ceiling - which is stranger?" with the tab idle.
