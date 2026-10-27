# Scene Inventory: "How Hot Can It Get?"

Generated from `artifacts/scene_plan.json` (the source of truth). Goes with `art-direction.md`.

- 1080×1920 @ 30 fps, ~50.5 s (1515 frames) as planned, Remotion atelier, **13 scenes and no hard cuts**: one continuous forge frame.
- Times are estimates; each split is re-timed from the aligned narration at the foundation stage.
- Ends on the finished line 'So heat may have no ceiling, just an edge to what we know.', then a resolved chord and a 1.5 s settle.
- ★ = hero beat.

| # | id · component | ~time (s) | sec | narration | type | on screen | source | tab | SFX |
|---|---|---|---|---|---|---|---|---|---|
| 1 | sc01 · FloorLine | 0.00-2.74 | s1 | Cold has a floor: absolute zero. | animation | a dark forge frame; the cold floor from video 11 sits at the bottom | code | MEASURED | X1 low ember crackle bed fades up from frame 0; X7 digit tick on the label seat (contact-1) |
| 2 | sc02 · CeilingQuestion | 2.74-7.31 | s1 | So how hot can it get? Is there a ceiling? | animation | the question: the frame looks up toward an unknown top | code | idle | X3 filament ignition (soft) as the '?' draws |
| 3 | sc03 · DeathValley | 7.31-10.96 | s2 | Death Valley's air once hit nearly fifty-seven degrees. | broll | a heat-shimmer window on a salt flat; the first rung is barely warm | S1 -> K1 | MEASURED | X2 heat hiss under the window; X7 tick on the rung seat |
| 4 | sc04 · Venus | 10.96-15.97 | s2 | Venus sits about four hundred sixty-five, hot enough to melt lead. | broll | Venus: hot enough to melt lead, yet still not hot enough to glow | S2 | MEASURED | X7 tick on the rung seat; X2 hiss continues low |
| 5 | sc05 · GlowSweep ★ | 15.97-19.16 | s3 | The Sun's core reaches about fifteen million. | animation | HERO 1: the frame finally glows - through every colour heat can make - and then the colour stops changing | code | MEASURED | X4 glow swell building under the sweep, cresting on the rung seat; X7 tick on the seat |
| 6 | sc06 · Reactor | 19.16-25.55 | s3 | Yet a fusion reactor in Korea held a hundred million degrees for forty-eight seconds. | broll | on Earth, a reactor holds a plasma hotter than the Sun's core | S3 -> K2 | MEASURED | X5 reactor hum under the window; X7 tick on the rung seat |
| 7 | sc07 · Collider | 25.55-30.08 | s4 | The hottest we've ever made: lead atoms smashed at CERN, | broll | the record: a particle collider | S4 | PROBABLY | X6 collider thump on the beam flash (contact-1) |
| 8 | sc08 · FiveTrillion | 30.08-31.90 | s4 | over five trillion degrees. | text_card | the rung jumps off the colour scale: the zeros take over as the meter | code | PROBABLY | X7 ticks on the digit seats (light), last one louder |
| 9 | sc09 · QuarkSoup | 31.90-36.43 | s4 | So hot that protons melt into a soup of quarks. | diagram | protons come apart into a soup of quarks | code | MEASURED | X2 soft hiss rising |
| 10 | sc10 · PlanckTemperature | 36.43-39.04 | s5 | Beyond that waits the Planck temperature, | animation | far above everything: one last mark | code | MEASURED | X3 filament ignition (soft) on the mark |
| 11 | sc11 · ThirtyTwoZeros ★ | 39.04-43.39 | s5 | roughly a one with thirty-two zeros, where our physics breaks. | text_card | HERO 2: the zeros counter runs to 32 | code | MEASURED | X7 accelerating ticks; none on 'breaks' |
| 12 | sc12 · NoCeiling | 43.39-46.00 | s5 | So heat may have no ceiling, | animation | there may be no lid at all | code | PROBABLY | none under the closing sentence |
| 13 | sc13 · EdgeOfKnowing | 46.00-50.50 | s5 | just an edge to what we know. | animation | calm: the ladder stands, the top unknown | code | PROBABLY | none; resolved chord ~0.15 s after 'know' |

## Scenes

### sc01 · FloorLine (0.00-2.74 s)

**Narration:** Cold has a floor: absolute zero.

FRAME 0: Forge Black #0B0907 ground with a faint iron grain (code, 3% luma, warm). At y 1060 a thin ice-blue hairline 'the floor' draws left to right on 'floor' (callback to video 11's FLOOR line), with '0 K = -273.15 °C' (IBM Plex Mono 500, 44 px, Ice #9FC9DA) seating above it on 'absolute zero'. The rest of the frame is unlit iron. MOTION: hairline draws over ~12 f; label drop seats on its tick.

Overlays: label '0 K = -273.15 °C'; label 'the floor'.

### sc02 · CeilingQuestion (2.74-7.31 s)

**Narration:** So how hot can it get? Is there a ceiling?

The view tilts up (code camera drift ~120 px, eased); the floor line slides toward the bottom edge. A warm glowing '?' (filament-stroke SVG, black-body 1,800 K colour) draws itself near the top of the frame on 'ceiling'. A vertical dashed rail (the ladder's spine, Iron #2A211B, 2 px) appears from floor to '?'.

Overlays: glowing '?'.

### sc03 · DeathValley (7.31-10.96 s)

**Narration:** Death Valley's air once hit nearly fifty-seven degrees.

A heat-shimmer window (rounded 28 px, x 160-920, y 360-900, soft iron frame) opens on K1: Death Valley salt flat with rippling heat haze (AI impression). Beside the rail the first rung marker seats at its log-scale position: '56.7 °C' (Saira Condensed 700, 96 px) + 'Death Valley · 1913 · air' (IBM Plex Mono 400, 34 px). The window carries a thermal false-colour tint toggle (code LUT over the clip, labelled 'false colour') that fades in on 'degrees' to show the heat, because nothing this cool glows.

Overlays: window tag 'AI impression'; tag 'false colour'; rung '56.7 °C · Death Valley · 1913 · air'.

### sc04 · Venus (10.96-15.97 s)

**Narration:** Venus sits about four hundred sixty-five, hot enough to melt lead.

The window crossfades to S2 Venus surface (AI impression · not a photo), slow code push 1.04x. Rung 2 seats higher on the rail: '~464 °C' + 'Venus surface'. A small drawn lead ingot (code, Iron grey) beside it slumps into a puddle on 'melt lead' ('lead melts at 327 °C · drawn'). A faint dashed line 'first visible glow ~525 °C' sits just above the Venus rung on the rail - Venus is below it.

Overlays: window tag 'AI impression · not a photo'; rung '~464 °C · Venus surface'; label 'lead melts at 327 °C · drawn'; rail mark 'first visible glow ~525 °C'.

### sc05 · GlowSweep (15.97-19.16 s)

**Narration:** The Sun's core reaches about fifteen million.

HERO 1. The window closes. As the rung number rolls from 464 up to 15,000,000, the whole frame's ambient light sweeps through the computed black-body ramp (CIE-correct, from code): first dull red past 'first visible glow ~525 °C', orange ~1,500 °C, yellow-white at a small mark 'Sun's surface ~5,500 °C', blue-white by ~30,000 °C. Then a mark 'colour stops changing past ~40,000 K' - the glow holds the same blue-white while the number keeps climbing. Rung 3 seats: '~15,000,000 °C · Sun's core'. A colour chip on the rail shows the current black-body swatch, labelled 'black-body colour'.

Overlays: rail marks 'Sun's surface ~5,500 °C' / 'colour stops changing past ~40,000 K'; rung '~15,000,000 °C · Sun's core'; chip 'black-body colour'.

### sc06 · Reactor (19.16-25.55 s)

**Narration:** Yet a fusion reactor in Korea held a hundred million degrees for forty-eight seconds.

The window reopens on K2: a violet plasma ring inside a doughnut-shaped reactor (AI illustration). Rung 4 seats ABOVE the Sun's core: '100,000,000 °C' + 'KSTAR · Korea · 48 s · 2024'. A thin 48-second timer arc draws around the rung marker on 'forty-eight seconds'. The glow does not change (already blue-white) - the rail is now the only meter.

Overlays: window tag 'AI illustration'; rung '100,000,000 °C · KSTAR · Korea · 48 s · 2024'.

### sc07 · Collider (25.55-30.08 s)

**Narration:** The hottest we've ever made: lead atoms smashed at CERN,

The window crossfades to S4: a huge cylindrical detector in a cavern (AI illustration, no logos). Two thin drawn beam lines converge at its centre and flash on 'smashed' (drawn).

Overlays: window tag 'AI illustration'; label 'drawn' on beam lines.

### sc08 · FiveTrillion (30.08-31.90 s)

**Narration:** over five trillion degrees.

The rail compresses (log scale re-spaces with an eased squash) and rung 5 seats far above: '> 5,000,000,000,000 K' (Saira Condensed 700, 88 px, digits seating left to right, each with a tick) + 'LHC · CERN · 2012 · record estimate'. A ZEROS counter chip appears beside it: '12 zeros'.

Overlays: rung '> 5,000,000,000,000 K · LHC · CERN · 2012 · record estimate'; chip '12 zeros'.

### sc09 · QuarkSoup (31.90-36.43 s)

**Narration:** So hot that protons melt into a soup of quarks.

Inside the window, a drawn proton (three coloured quark dots in a glowing bag, code) loosens and its quarks drift free among others into a shimmering 'soup' (seeded particles, black-body blue-white). Tag 'drawn · illustrative'. Label 'quark-gluon plasma'.

Overlays: tag 'drawn · illustrative'; label 'quark-gluon plasma'.

### sc10 · PlanckTemperature (36.43-39.04 s)

**Narration:** Beyond that waits the Planck temperature,

The window closes; the camera drifts up the rail into darkness above the LHC rung. A final, thin rung mark appears near the top under the old '?': 'Planck temperature'. The '?' dims to half.

Overlays: mark 'Planck temperature'.

### sc11 · ThirtyTwoZeros (39.04-43.39 s)

**Narration:** roughly a one with thirty-two zeros, where our physics breaks.

HERO 2. The zeros chip counts 12 -> 32 (ticks accelerate then settle), and the number writes out as '1.4 × 10^32 K' (Saira Condensed 700, 104 px) on the Planck mark. On 'breaks' the rail line above the mark frays into a dashed, broken stroke and fades: 'where known physics stops working'.

Overlays: chip '32 zeros'; rung '1.4 × 10^32 K'; label 'where known physics stops working'.

### sc12 · NoCeiling (43.39-46.00 s)

**Narration:** So heat may have no ceiling,

The '?' at the top fades out completely; the rail beyond the Planck mark is open, dashed into darkness. Small note: 'not a proven limit'.

Overlays: note 'not a proven limit'.

### sc13 · EdgeOfKnowing (46.00-50.50 s)

**Narration:** just an edge to what we know.

Full view of the ladder from floor to Planck mark, the frame in its last warm blue-white glow at low intensity. After 'know' the picture settles: ~1.5 s hold on the resolved chord; caption slab shows 'Floor or ceiling - which is stranger?'; tab idle. All channels constant through the settle (lesson 25).

Overlays: settle caption 'Floor or ceiling - which is stranger?'.

## Generated assets

**S1 · plate_death_valley** (used in sc03; clip K1) - fallback: code: white gradient plain + shimmer noise

```
Intended use: a vertical 9:16 window plate in a dark science graphic; keep the middle 60% of the frame the most interesting.

Death Valley's Badwater salt flat at midday in summer: a vast cracked white salt crust stretching to a level horizon at about 45% of the height, brown bare mountains along the horizon, a pale washed-out sky, strong heat haze rippling over the ground in the distance, harsh overhead sunlight and very short shadows. Photographic, documentary, natural colours, sharp. No people, no figures, no animals, no vehicles, no roads, no signs, no buildings. Absolutely no text, letters, numbers, logos, watermark, signature, border or user-interface elements anywhere.
```

**S2 · plate_venus_surface** (used in sc04; clip -) - fallback: code: orange haze gradient + dark slab silhouettes

```
Intended use: a vertical 9:16 window plate in a dark science graphic; keep the middle 60% of the frame the most interesting.

The surface of Venus as a scientific impression based on the Soviet Venera lander images: flat slabs of dark basalt rock and gravel stretching to a near horizon at about 40% of the height, under a thick, uniform, dim yellow-orange overcast sky; diffuse orange light, no sun visible, no shadows, heavy hazy air. The rocks do NOT glow. Realistic, muted, photographic. No spacecraft, no lander, no people, no lava, no fire. Absolutely no text, letters, numbers, logos, watermark, signature, border or user-interface elements anywhere.
```

**S3 · plate_reactor_plasma** (used in sc06; clip K2) - fallback: code: violet torus ring glow on dark

```
Intended use: a vertical 9:16 window plate in a dark science graphic; keep the middle 60% of the frame the most interesting.

Inside the doughnut-shaped vacuum chamber of a tokamak fusion reactor: curved metal wall tiles receding in a ring, and floating in the middle of the chamber a thin, faint, glowing violet-pink plasma ring that follows the curve of the doughnut, softly lighting the tiles. Dark, technical, photographic, high detail. No people, no logos. Absolutely no text, letters, numbers, logos, watermark, signature, border or user-interface elements anywhere.
```

**S4 · plate_collider_detector** (used in sc07, sc09; clip -) - fallback: code: concentric detector rings

```
Intended use: a vertical 9:16 window plate in a dark science graphic; keep the middle 60% of the frame the most interesting.

A gigantic cylindrical particle detector seen end-on in an underground cavern: concentric rings of red, blue and silver detector modules and cables around a central beam pipe, steel scaffolding and walkways around it, cool industrial lighting, a sense of huge scale. Photographic, high detail. No people, no logos, no signs. Absolutely no text, letters, numbers, logos, watermark, signature, border or user-interface elements anywhere.
```

**K1** from S1 (sc03): Heat haze ripples and shimmers steadily over the distant salt flat and the base of the mountains; the ground itself stays still. Camera locked off on a tripod, no pan, no zoom, no tilt, real-time speed. No people, no vehicles, no text. Negative: person, vehicle, camera movement, pan, zoom, tilt, flicker, fire, smoke, text. Fallback: code shimmer displacement over S1.

**K2** from S3 (sc06): The thin violet plasma ring flows and swirls slowly around the doughnut-shaped chamber, flickering gently and softly lighting the wall tiles; very slow, smooth push-in. No people, no text. Negative: person, explosion, sparks, fire, fast camera, flicker, text. Fallback: code ring shimmer over S3.
