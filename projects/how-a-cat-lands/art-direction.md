# Art Direction: "How Does a Cat Always Land on Its Feet?"

Video 15. Concept C1 **Operating Theatre, reused** (video 14's engine, re-dressed as a test lab; approved). Lean build:
`new_project.sh` kit + video 14's per-video files; 2 scene builders; `qa_auto.py`, then 1 QA agent.
Companions: `scenes.md` (generated) and `artifacts/scene_plan.json` (source of truth).

## Design read

A deadpan test procedure on a falling cat: clean, exact and curious, with a dry twist at the end. No cat is ever shown hurt.

- **The rig.** A steel release clamp on a slate drape; the drawn cat hangs upside down under it. Header "PROCEDURE: LANDING".
- **The checklist is the signature device** (kept from video 14): 01 FIND UP · 02 BEND · 03 TUCK FRONT · 04 SWAP ·
  05 SPREAD · 06 LAND, beside an ELAPSED clock labelled "illustrative".
- **The two-half cat (hero, sc06).** A drawn silhouette split at the waist: FRONT half tinted amber, BACK half cyan, each
  with a dashed axis. Two dials, FRONT and BACK, show the halves turning in opposite directions (front a lot, back a little),
  and a readout "total spin: 0" that never changes. Dials show directions and relative size only, no exact angles.
- **The window** (all tagged): S1 the cat upside down in midair, the 1894 Marey strip (archival or a labelled drawn copy),
  S2 the landing.
- **The twist.** A "NOT ALWAYS" stamp; a short-drop demo that fades out before the floor; the ledger "132 cats · ~90%
  survived" with a hatched, empty column "never reached a vet: not counted".

**Colour rules:** amber appears only on the front half (and the word "front"), cyan only on the back half (and "back").

**Distinct from video 14:** slate drape instead of surgical green; no tray, no skin, no red.

## Palette

| Name | Hex | Use |
|---|---|---|
| Drape | #3B4A55 (deep #2C3740) | Ground |
| Steel | #C9D1D3 (edge #8E9A9D) | Rig, cat outline, dials |
| Shadow | #1C2B2A | Shadows, chips |
| FRONT | #E8A33D | ONLY the front half |
| BACK | #6CC6D9 | ONLY the back half |
| Ledger Paper | #F3F1EA | Checklist and ledger cards |
| Stamp red | #C8473B | Stamps only |
| Night Ink / Bone | #0A0B10 / #F4EFE6 | Channel caption slab and text |

## Type

As video 14: IBM Plex Sans Condensed 600/700 (headers, labels, stamps), Roboto Mono 400/500 (checklist, clock, dials,
ledger, tags), Bricolage Grotesque 800 captions, Spline Sans Mono 600 tab. Labels ≥ 28 px, fine print ≥ 24 px. Arrows are SVG.

## Layout

Field x 120–960, y 360–1000. Window x 160–920, y 360–900. Checklist x 640–920, y 220–600. Placard rail y 1124–1204,
tab y 1236–1290, caption slab x 140–940, y 1296–1488. No text at y ≥ 1574 or x ≥ 929.

## Motion

Motion intensity 4. The fall is a gravity ease-in; each half follows one smooth angle curve shared by its silhouette and
its dial (no rigid jumps). Checklist ticks land on their sounds. AI-tag swaps are hard cuts at crossfade midpoints (L38).

## Ending

"It only counted cats that reached the vet." ends complete. The checklist is complete and the ledger with its empty
column stays. The resolved chord lands about 0.15 s later, the picture holds 1.5 s, and the music fades over the last
0.6 s. The slab shows "Seen a cat do this?" with the tab idle.
