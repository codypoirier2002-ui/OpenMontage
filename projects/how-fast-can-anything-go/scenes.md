# Scene Inventory: "How Fast Can Anything Go?"

Generated from `artifacts/scene_plan.json` (the source of truth). Goes with `art-direction.md`.

- 1080×1920 @ 30 fps, ~49.2 s (1476 frames) as planned, Remotion atelier, **12 scenes and no hard cuts**: one continuous speed-ladder frame.
- Times are estimates; each split is re-timed from the aligned narration at the foundation stage.
- Ends on the finished line 'Close. But never all the way.', then a resolved chord and a 1.5 s settle.
- ★ = hero beat.

| # | id · component | ~time (s) | sec | narration | type | on screen | source | tab | SFX |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sc01 · Walk | 0.00-3.61 | s1 | You walk at about five kilometres an hour. | animation | the speed ladder appears; a marker at walking pace | code | MEASURED | X1 soft whoosh as the rail draws |
| 2 | sc02 · Cheetah | 3.61-6.76 | s1 | A cheetah sprints at about a hundred. | broll | the marker climbs to ~100; a cheetah in the window | S1 | MEASURED | X1 whoosh on the climb; X3 digit tick on the counter |
| 3 | sc03 · Falcon | 6.76-9.92 | s1 | A diving falcon hits nearly four hundred. | broll | the marker climbs to ~390; a diving falcon | S2 | PROBABLY | X1 whoosh |
| 4 | sc04 · Sound | 9.92-13.54 | s2 | Sound outruns them all at over twelve hundred. | animation | the sound rung: a soft shock ring | code | MEASURED | X2 soft sonic thump on the rung seat |
| 5 | sc05 · YouAreFast ★ | 13.54-19.89 | s2 | But sitting still, you're doing over a hundred thousand, riding Earth around the Sun. | animation | HERO: 'YOU' jumps up the ladder to Earth's orbit | code | MEASURED | X1 big whoosh on the jump; X3 ticks on the counter |
| 6 | sc06 · Parker | 19.89-24.45 | s3 | The fastest thing we've ever built, the Parker Solar Probe, | broll | the Parker Solar Probe near the Sun | S3 | MEASURED | X4 low hum swells under the window (soft) |
| 7 | sc07 · Falling | 24.45-28.55 | s3 | reached nearly seven hundred thousand, falling toward the Sun. | animation | the marker climbs to ~692,000 | code + S3 | MEASURED | X1 whoosh |
| 8 | sc08 · Light | 28.55-30.82 | s4 | Light does over a billion. | animation | light at the top of the ladder | code | MEASURED | X5 high shimmer on the beam |
| 9 | sc09 · Wall | 30.82-33.99 | s4 | And nothing with mass can catch it: | animation | the wall: the marker can't reach c | code | MEASURED | none |
| 10 | sc10 · Energy | 33.99-39.43 | s4 | the closer you get, the more energy each step costs, without end. | diagram | an energy bar that grows without limit | code | MEASURED | X3 accelerating ticks as the bar grows |
| 11 | sc11 · LHC ★ | 39.43-45.08 | s5 | The Large Hadron Collider pushes protons to within a hair of light speed. | text_card | HERO 2: the nines fill; the gap stays | code | MEASURED | X3 tick per digit |
| 12 | sc12 · NeverAllTheWay | 45.08-49.20 | s5 | Close. But never all the way. | animation | the marker holds just under the wall; settle | code | MEASURED | X6 soft glass tink BEFORE the closing sentence if it fits, else none; resolved chord ~0.15 s after 'way' |

## Scenes

### sc01 · Walk (0.00-3.61 s)

**Narration:** You walk at about five kilometres an hour.

FRAME 0: night-ink sky (#070A12 -> #0D1424 vertical gradient, faint star dust), a vertical steel log-scale rail at x ~250 from y 1080 (1 km/h) to y 380 (10^9 km/h), decade ticks with small mono numbers (1, 10, 100, 1,000 ... 1,000,000,000), label 'km/h · log scale'. At the very top a short red line labelled 'c' (dim until s4). A white-cyan marker (#BFF6FF core, soft glow) sits at 5 km/h with a rung label 'WALK · ~5' and a tiny walker icon. ZEROS counter top right: '0'. MOTION: marker breathes; streaks length = log10(speed).

Overlays: rail label 'km/h · log scale'; rung 'WALK · ~5'; counter 'ZEROS 0'.

### sc02 · Cheetah (3.61-6.76 s)

**Narration:** A cheetah sprints at about a hundred.

The marker eases up to 100 (rung 'CHEETAH · ~100' seats with its number on arrival); the counter ticks to 2. A window (x 470-920, y 420-900) opens on S1: a cheetah at full sprint (AI impression).

Overlays: rung 'CHEETAH · ~100'; window tag 'AI impression'.

### sc03 · Falcon (6.76-9.92 s)

**Narration:** A diving falcon hits nearly four hundred.

Window swaps (hard tag swap at the crossfade midpoint, lesson 38) to S2: a peregrine falcon in a steep dive (AI impression). The marker climbs to ~390 (rung 'FALCON (dive) · ~390' with a hatched PROBABLY chip 'commonly cited').

Overlays: rung 'FALCON (dive) · ~390'; chip 'commonly cited'; window tag 'AI impression'.

### sc04 · Sound (9.92-13.54 s)

**Narration:** Sound outruns them all at over twelve hundred.

Window closes. The marker crosses 1,235 (rung 'SOUND · 1,235') with a soft circular pressure ring expanding once from the marker; counter 3.

Overlays: rung 'SOUND · 1,235'.

### sc05 · YouAreFast (13.54-19.89 s)

**Narration:** But sitting still, you're doing over a hundred thousand, riding Earth around the Sun.

HERO. A small 'YOU' tag (a seated figure icon) appears at the WALK rung and then jumps up the rail to 107,000 on 'hundred thousand' (rung 'EARTH (orbit) · ~107,000'); beside the rail a small drawn orbit diagram (Sun dot, Earth dot on a dashed circle, arrow) labelled 'drawn · not to scale'. Counter 5.

Overlays: tag 'YOU'; rung 'EARTH (orbit) · ~107,000'; inset tag 'drawn · not to scale'.

### sc06 · Parker (19.89-24.45 s)

**Narration:** The fastest thing we've ever built, the Parker Solar Probe,

Window opens on S3: a heat-shielded spacecraft close to the Sun (AI impression of the Parker Solar Probe). Label 'Parker Solar Probe · NASA'.

Overlays: label 'Parker Solar Probe · NASA'; window tag 'AI impression'.

### sc07 · Falling (24.45-28.55 s)

**Narration:** reached nearly seven hundred thousand, falling toward the Sun.

The marker climbs to 692,000 (rung 'PARKER (fastest built) · ~692,000'); counter 5. A small arrow on the window plate points toward the Sun: 'falling toward the Sun'.

Overlays: rung 'PARKER (fastest built) · ~692,000'; label 'falling toward the Sun'.

### sc08 · Light (28.55-30.82 s)

**Narration:** Light does over a billion.

Window closes. A thin beam races up the rail to the top (1,079,252,849) in a few frames; rung 'LIGHT · 1,079,252,849'; counter 9; the 'c' line at the top lights red.

Overlays: rung 'LIGHT · 1,079,252,849'; line 'c'.

### sc09 · Wall (30.82-33.99 s)

**Narration:** And nothing with mass can catch it:

The marker leaves PARKER and climbs toward 'c' but slows smoothly; label 'anything with mass' on the marker.

Overlays: label 'anything with mass'.

### sc10 · Energy (33.99-39.43 s)

**Narration:** the closer you get, the more energy each step costs, without end.

Beside the rail an 'ENERGY NEEDED' bar grows faster and faster as the marker inches up (a 1/sqrt(1-v^2/c^2) curve drawn small with axis labels 'speed' / 'energy', 'drawn · not to scale'); the bar runs off the top of the frame on 'without end'.

Overlays: label 'ENERGY NEEDED'; axis labels 'speed' / 'energy'; inset tag 'drawn · not to scale'.

### sc11 · LHC (39.43-45.08 s)

**Narration:** The Large Hadron Collider pushes protons to within a hair of light speed.

HERO 2. A mono readout card: 'LHC protons' then '99.9999991 %' types digit by digit (each 9 on a tick); the marker creeps to just under 'c' with a tiny bracket 'the gap'. Placard credits CERN.

Overlays: label 'LHC protons'; readout '99.9999991 %'; bracket 'the gap'.

### sc12 · NeverAllTheWay (45.08-49.20 s)

**Narration:** Close. But never all the way.

Everything settles: the full ladder visible, the marker steady just under 'c', the gap bracket stays. After 'way' a ~1.5 s still hold on the resolved chord; caption slab 'What's the fastest thing you've ridden?'; tab idle.

Overlays: settle caption 'What's the fastest thing you've ridden?'.

## Generated assets

**S1 · plate_cheetah** (used in sc02; clip -) - fallback: crop (lesson 39) or drawn icon only

```
Intended use: a vertical 9:16 window in a clean dark science graphic; keep the middle 60% of the frame the most interesting.

Wildlife photograph of a cheetah at full sprint across dry savanna grass, side view, body stretched, legs extended, dust kicked up, late golden light, sharp focus on the cheetah with a slightly blurred background suggesting speed. Natural, realistic. No people, no vehicles, no text, no watermark.
```

**S2 · plate_falcon_dive** (used in sc03; clip -) - fallback: crop or drawn icon only

```
Intended use: a vertical 9:16 window in a clean dark science graphic; keep the middle 60% of the frame the most interesting.

Wildlife photograph of a peregrine falcon in a steep high-speed dive (stoop), wings tucked tight against its body, head forward, against a clear blue sky, sharp focus, realistic plumage (slate-grey back, barred pale chest, dark moustache stripe). No other birds, no text, no watermark.
```

**S3 · plate_parker_probe** (used in sc06, sc07; clip -) - fallback: drawn probe icon + label

```
Intended use: a vertical 9:16 window in a clean dark science graphic; keep the middle 60% of the frame the most interesting.

Space illustration of a small spacecraft with a large flat white circular heat shield facing the Sun, its instruments in the shield's shadow, two small solar panels angled back, flying close to the enormous glowing Sun whose surface and corona fill the top of the frame, black space below. Realistic, NASA-style artist impression. No text, no logos, no watermark.
```
