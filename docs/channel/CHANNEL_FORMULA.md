# The channel formula

How this channel's videos get made: what the user expects, the process, prices, and the lessons from the first seven
videos. A new session should read this before starting a video, **after** `AGENT_GUIDE.md` (that still governs the
pipeline). Where the two differ on the channel's own conventions, the user's rules here win.

## The user's standing rules

| Rule | Detail |
|---|---|
| **Gates** | Proposal → script → scene plan each need the user's explicit approval. Nothing paid is generated before the scene plan is approved. After that, run end to end to delivery unless the user asks to pause. |
| **Budget** | Ask for a cap each time; the default offer is **$4, minimal takes**. One generation per asset; retake only when automated QA fails (narration at most 2 retakes); never re-roll images or clips — use the code fallback instead. Run `estimate_only` before every paid run and give the generating agent a hard limit (~$2). |
| **Ending** | **End on a finished line.** The last sentence is complete; then ~1.5 s of settle with the music on a resolved chord and a calm frame. No mid-sentence loop cut (the user found the loop endings "cut off"). A loop version is an optional second export only; keep the last picture frame equal to frame 0 so it stays possible. |
| **Screenshots** | Send three contact sheets along the way (free): 1. generated assets (images + clip frames, unusable ranges marked), 2. foundation layout, 3. one frame per scene from the rendered master. Then the final video. |
| **Delivery** | Send the 1080x1920 master with SendUserFile. No 720p unless asked. |
| **Honesty** | Every claim gets a MEASURED / PROBABLY / MAYBE tab. AI imagery is tagged ("AI impression" / "AI illustration"); drawn diagrams say "drawn" / "illustrative". Visuals must never contradict the facts (e.g. 180 °C rock does not glow — regraded as a labelled thermal false-colour view). |
| **Spend reporting** | Report spend against the cap at each milestone. Paid spend or provider changes beyond the approved plan need approval. |
| **Never** | Paste the Apify token in chat; publish anything outside the container; send the user's email to any service. |

## Series styles (the user can ask for "the style of video N")

| # | Title | Look | Spend |
|---|---|---|---|
| 1 | Why Isn't the Sky Violet? | flat sky vectors, explainer | — |
| 2 | 3 Skies You'd Never Survive | painted sky plates, ranked 3 | $1.86 |
| 3 | Falling to the Bottom of the Ocean | "Light Dies on the Way Down": one POV fall, painted plates, depth-gauge HUD, 4 AI creature clips | $4.92 / $8 |
| 4 | 3 Animals That Cheat Death | **"Loophole Cabinet"**: specimen cards, ink line drawings, red stamps, catalogue-tag chip flipping No. 3 → 2 → 1, one Kling clip per animal, deadpan twist ("It can still get eaten") | $2.42 / $6 |
| 5 | What If the Moon Vanished? | "Missing-Piece Almanac": gold engraving on indigo, Moon cut out as a hole that media plays through | $1.72 / $4 |
| 6 | How Deep Can a Human Dig? | "Core Shed": core trays read row by row, stencil type, survey tape, hi-vis orange; depth shown sideways | $1.71 / $4 |
| 7 | Why Can't You Tickle Yourself? | "Misregistration": two-ink riso zine, blue = prediction, pink = touch, overprint when in register | $1.68 / $4 |
| 8 | 3 Animals Older Than the Dinosaurs | Video 4's cabinet style plus a "Deep-Time Tape" that reels out each animal's age; finished-line ending | $2.39 / $4 |
| 9 | What If You Never Slept? | "Night Shift Chart": one sleep-lab chart strip feeding up the screen, cream paper, green grid, six ink pens, grease-pencil notes, HOURS AWAKE counter, AI clips only in a taped window | $2.37 / $4 |
| 10 | How Loud Can a Sound Get? | "Pressure Column": ~6,000 warm dots of air on night blue, amber squeeze / blue stretch bands, lift-indicator dB rail; vacuum gaps go pure black at 194 and snap into a shock wall; drawn mercury U-tube gauge | $2.38 / $4 |
| 11 | How Cold Can It Get? | "Frost Pane": one night window that frosts over (8% → 95%) as the meter; code-grown herringbone ferns; numbers scraped in by fingertip (Sora + DM Mono, slashed zeros); places seen through melted patches; a scraped FLOOR line nothing ever touches; breath-fog circle finale | $1.74 / $4 |
| 12 | What If Earth Stopped Spinning? | "Stopped Forecast": a deadpan 1990s TV weather wall with no presenter; one orthographic globe from real Natural Earth coastlines (world-atlas + d3-geo) that brakes to 0 on the Atlantic view and only turns again at the end; orange = sudden stop, teal = slow stop, broadcast blue = the real world; "LIVE CAM" insets for AI places; drawn schematic of the Esri/Fraczek ocean model (Archivo Black + Barlow Condensed) | $1.70 / $4 |
| 13 | How Hot Can It Get? | "Black-Body" (partner to video 11): the frame's light is the meter — computed black-body colour (Planck × CIE 1931 → sRGB, unit-tested) of each rung; nothing glows below the Draper point (~525 °C), so Death Valley and Venus sit in a labelled false-colour window; one sweep red → orange → yellow-white → blue-white that "barely changes past ~40,000 K", then a zeros counter (12 → 32) carries a log-scale ladder from video 11's cold floor to the Planck temperature, where the rail frays (Saira Condensed + IBM Plex Mono) | $1.73 / $4 |
| 14 | How a Mosquito Drinks Your Blood | "Operating Theatre": a deadpan surgical procedure on surgical-green drape; a steel tray of the six stylets, labelled; a six-step checklist (01 INCISE … 06 EXIT) ticking beside an "illustrative" ELAPSED clock; a drawn skin cross-section where the drinking tube bends and gropes; a drawn silhouette weight gauge (100% → ~250%) with "water out" drips; blood red only for blood, saliva cyan only for saliva; AI plates as tight crops with code motion (IBM Plex Sans Condensed + Roboto Mono) | $0.44 / $4 |

Each project's `art-direction.md`, `scenes.md`, `BUILD.md` and `artifacts/` define its look (they live under the
gitignored `projects/` folder, so they exist only in the container that built them).

## Format

- 9:16, 1080x1920, 30 fps, ~45–55 s, about 100–106 narrated words (Bella reads ~2.0–2.3 words/s; plan with slack).
- **Five script sections:** a hook, three beats, and a closing line. Countdown videos go "Number three / two / one", then the twist.
- **Captions:** word-highlight captions burned in. The slab sits at x 140–940, y ~1296–1488, clear of TikTok's bottom ~350 px and right ~120 px.
- **Honesty tab and placard rail:** the tab is keyed to each claim's caption line, and there is a placard rail for citations.
- **Audio:** a music bed ducked about 12 dB under the voice, plus 3–4 SFX. Master to −14 LUFS, true peak ≤ −1 dBTP.

## Providers, IDs and prices (as billed, Oct 2026)

- **ElevenLabs MCP flows:** one flow per video.
  - Load the tools with ToolSearch.
  - Before any paid run, call `creative_run_flow_nodes` with `estimate_only` first.
  - Poll `creative_get_flow_run_status`.
  - To use a still as a clip's start or end frame, pin it with `creative_add_flow_asset_node`.
  - `content_url` links expire after 2 h, so download promptly.
- **Narration:** voice **Bella `hpp4J3VqNfWAUOO0d1Us`**, model eleven_v4 with audio tags (`delivery_cues.provider_text`). About $0.013–0.034 per section.
- **Images:** gpt-image-2.5-sunburst at 2K, 9:16, about $0.05 each. Edits are about $0.094.
  - Check each node's aspect and size before running; one defaulted to 16:9 1K.
- **Clips:** kling-3-pro, 5 s, 1080p, about $0.617.
  - **Set `generate_audio=false`**, because it defaults to true.
  - Clips come out at 24 fps; convert them to 30.
  - They are often clean for only 2–3 s, so check every ~6th frame and use only the clean range.
- **Music:** eleven_music, about $0.15–0.16. Ask for a steady bed with a resolved final cadence.
  - Beds can fade or drop out mid-track; analyse the level profile.
  - For finished-line endings, find the final chord, trim the head on a downbeat (or nudge the speed by a few cents) so the chord lands ~0.15 s after the last word, and release the duck before it.
- **SFX:** about $0.003 each. They usually need trimming.
- **Research:** WebSearch works; WebFetch often fails on DNS. Cross-check every fact across at least 2 sources. The PubMed MCP sometimes works.

## Build process (Remotion "atelier")

Mirror the most recent delivered project's layout. `projects/how-a-mosquito-drinks/` is the newest (its
`BUILD.md` is the fullest builder contract; video 12's is the cleaner template for map/graphics looks); if `projects/` is gone, rebuild from this description.

1. **Research brief.** Write `artifacts/research_brief.json` with roughly 15–20 data points, each with its tag. List the myths and say which claims were dropped and why.
2. **Proposal.** Write `artifacts/proposal_packet.json` with four concept options, the hook, a five-beat outline, the look, the asset plan and costs, and `pending_user_choices`.
3. **Decision log.** Record the concept, budget, style and ending decisions in `decision_log.json`.
   - **GATE:** the user approves.
4. **Script.** Write `artifacts/script.json`: five sections with eleven_v4 tags, `metadata.claim_tags`, and `metadata.wording_changes_from_outline`, keeping the wording fact-exact.
   - **GATE:** the user approves.
5. **Scene plan.** Write `art-direction.md`, `scenes.md` and `artifacts/scene_plan.json`: about 13–14 scenes, 1–2 hero beats, per-asset prompts, code fallbacks and risks, and `metadata.lessons_applied`.
   - **GATE:** the user approves.
6. **Assets agent.** Generate everything on one flow and Whisper-QA the takes. Write `assets/assets_report.json` with `quality_concerns`, plus contact sheet 1.
7. **Foundation agent.** It writes:
   - `align_narration.py` (with OVERRIDES), `timeline.json` and `build_props.py` (METER and captions);
   - `build_soundtrack.py`, the frame-aligned premix in `public/audio/soundtrack.wav`;
   - `prepare_media.py`, `theme.ts`, `time.ts` (`useT()`, `driftFrame`, `loopFrame`), the `shared/` helpers and the overlay;
   - the composition with stub scenes, and `BUILD.md`, which includes a unit split for four builders and §7 hand-offs;
   - `stills.cjs` (it deletes its webpack bundle in a `finally`), `check_hooks.py`, and contact sheet 2.
8. **Four scene builders in parallel**, one unit each, building only inside their own `scenes/uN/`. Relay their hand-off requests between units with SendMessage. Each builder:
   - runs tsc and `check_hooks.py scenes shared overlay`;
   - renders a 0.25-scale segment of its range;
   - checks stills and seam PSNRs.
9. **Render.** Run this from `remotion-composer/`:

   ```
   npx remotion render projects/<id>/index.tsx <CompId> ../projects/<id>/renders/<raw>.mp4 \
     --config=projects/<id>/remotion.config.ts --props=../projects/<id>/artifacts/props.json \
     --concurrency=3 --crf=18 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
     --public-dir=../projects/<id>/public
   ```

   The project must be symlinked as `remotion-composer/projects/<id>`.
10. **Master** with `docs/channel/scripts/finish_master.sh`:
    - It converts BT.601 full range to BT.709 tv range, encodes x264 crf 18 with VBV `maxrate 20M` / `bufsize 25M`, High@4.0, g 60, faststart.
    - Audio comes from the **premix**, not Remotion's AAC, which has a 42.7 ms lag. It gets one constant gain to −14 LUFS, then the limiter, then AAC 192k at 48 kHz.
    - Its checks: strict decode, ebur128, the AAC packet histogram, and silences.
    - Make contact sheet 3 from the master.
11. **Three independent QA agents.**
    - **A: transcript, captions, mix, facts and ending.** Caption onsets must be measured from the clean WAVs with a 5 ms envelope and spectrograms, not from Whisper, and must be within ±3 frames.
    - **B: picture, colour, text** (contact sheets, seams, TikTok zones, honesty tags).
    - **C: playback, spec and A/V sync.** It uses matched filters of each cue rebuilt exactly as `build_soundtrack.py` makes it, aiming for ±1 frame of the visible landing.
    - Fix every blocker and major issue, re-render, then have an independent agent re-check before sending.
12. **Records.** Write `asset_manifest.json`, `edit_decisions.json`, the assets/edit/compose checkpoints, `render_report.json` and `final_review.json`, all schema-valid.

## Lessons (each cost a QA round once — bake them into every plan)

1. **No React hook after an early return**, in any component. A conditional `useId` in `Engrave` crashed a full render with React #310, and stills never catch this. Run `check_hooks.py` with the directories as arguments, and do a full-length 0.25-scale test render.
2. **Caption onsets.**
   - Whisper hands pauses and closures to the *following* word, and gives a long-vowel word like "By" only 2 frames, which pushes the next word early.
   - Sweep every word on the clean section WAVs and put the fixes in section-local OVERRIDES.
   - Convention: a stop's onset is its burst; a fricative, nasal or /h/ starts at its own noise.
   - Captions take their words from `script.json`, never from Whisper ("forty", not "40%").
3. **The honesty tab** keys on the start of the caption line that carries the claim. A later claim keyed to the same caption line overrides the earlier one on its first frame. Show a tab state only while its claim is on screen.
4. **SFX land on the visible landing or contact frame.** Stamp thunks placed 2 frames after contact failed the sync check; place them on contact−1, when the stamp is fully down. Tag and card thunks belong where the card seats, not where its slide starts.
5. **Phone-band audibility:** measure every SFX in 300–4000 Hz against the bed, and add harmonic layers (`with_harmonics`) where needed. Also keep every 100 ms window of the premix above about −42 dBFS, so there is no dead air.
6. **Back-to-back caption pages:** keep the slab up and don't fade it out and in, or it blinks.
7. **Dense animated textures** such as riso halftone can peak at ~38 Mbps, so use the VBV cap. A light luma dither (`noise=c0s=2:c0f=t`) helps flat-gradient banding only on clean, smooth looks.
8. **Kling** clips morph after a few seconds: hands close, rock turns to lava, metal warps. Plan holds and ping-pongs inside the clean range.
9. **AI stills** often frame wrongly. Measure positions from pixels and reframe in code.
10. **Fonts:** confirm each `@remotion/google-fonts` font imports from the package's ES-module build; BigShouldersStencilDisplay and SairaStencilOne don't. Check the glyphs too: most fonts lack →, so draw arrows as SVG.
11. **Grain seed:** `T.driftFrame(T.loopFrame(frame))`, in that order.
12. **`stills.cjs` must delete its webpack bundle.** Leftover bundles once filled /tmp with 16 GB.
13. **Don't trust a builder's own caption sweep.** On video 8 the foundation reported every word within 0.85 frames, but independent QA found 13 words 4–22 frames early ("by" 0.73 s early). A tie-breaking re-measure then found 10 more that both had missed. QA A must always measure onsets independently. When the two disagree, a fix agent re-measures every disputed word and then re-sweeps all of them.
14. **Eased moves that end hidden.** If a move finishes inside a mask or case, as with the tape reel-in on video 8, its sound belongs on the last **visible** step, not on the move's end frame.
15. **Hand-lettered fonts like Caveat overhang their advance box.** A text reveal that clips at the box edge cuts the last glyph; on video 8 the "?" was cut in half. Let a fully revealed text overhang its box by about 16 px.
16. Facts get the most careful wording: "nearly forty percent" (the true figure is 38%), "less tickly" (not "barely"), "longer, not deeper" (Kola vs oil wells), and "lab vs home".
17. **Count script words as spoken.** Numbers like "nineteen sixty-four" and "two hundred sixty-four" added ~5 words on video 9 and pushed the read ~4 s past plan. Plan the length from the spoken form; if the read still runs long, trim the middle of sentence pauses (short crossfades, keep beat pauses ~0.55 s) before alignment, and treat the trimmed WAVs as the only clean WAVs for alignment, OVERRIDES, premix and QA A.
18. **Check the last word on phone speakers.** The music's build into the final chord can bury the closing word in 300–4000 Hz even when the duck is right (video 9: +7 dB). Aim for ≥ +12 dB over the bed on every syllable of the last word: duck the bed a further ~5 dB under it and lift the word ~3 dB in that band.
19. **Retiming the paper or feed moves every mark.** On video 9 a feed change for one scene shifted all the marks across the film and created new overlaps. After any global timing change, re-sweep the whole film for collisions.
20. **Absolute honesty tags need the same fact-check as narration.** On video 10, "AI impression · no photographs exist" was false (a photo of Krakatoa's May 1883 phase exists); it became "no photographs of the climax exist". Check every "no/never/only" on screen against the research brief before the scene-plan gate.
21. **Dense particle fields cost bitrate.** Video 10's 6,000 moving dots averaged ~11 Mbps (peaks 25) under the same crf 18 + VBV chain, putting the master at ~72 MB, right at TikTok's Android-app upload limit. For heavy-texture looks, also export an upload copy with maxrate ~12M / bufsize ~15M (~63 MB) and keep the master as is.

22. **Shared reveal helpers can land visuals early.** On video 11, an ease-out card seat was sub-pixel from seat−3, and a scrape reveal's round cap uncovered glyphs 2–3 frames ahead, so cards and digits read as landed before their SFX. Use an ease-in (gravity) drop that still moves several px on seat−1, put the reveal edge exactly at the progress point, and check seat−2 / seat−1 / seat stills.
23. **A texture that acts as a meter must only ever get denser.** Video 11's brightness cap at high frost coverage made the frost look thinner late in the film, so the meter seemed to recede. Measure a texture-only band (luma mean / std) at several frames and require it to hold or rise. Model code textures on a real reference (the frost first read as twigs, then steel wool, until rebuilt as herringbone ferns).
24. **Blend modes under a fading parent flash.** A `mix-blend-mode: multiply` fill inside an element with opacity below 1 is isolated and showed as a flat colour for a frame (video 11, frame 772). Keep the blend element unfaded and fade its colour toward white (a white multiply does nothing), or tie it to the plate's own mask.
25. **Envelopes that end at the last frame break the still ending.** Two frost-clearing masks with `to = total_frames` faded out over the final 8 frames, so the frost crept back as the film ended. Let end-running elements end after the film (T + 8), and assert in `build_props.py` that every channel is constant through the settle.
26. **Generated music may ignore the requested key** (video 11 asked for E major, got A). Find the final cadence from the audio, not the prompt.
27. **Kling "camera locked off" can still pan.** Video 12's K1 panned right ~2.7 px/frame, so the planned ping-pong would have shown the pan reversing; K2 was locked but nearly static. Measure camera motion and subject motion in every clip before planning ping-pong or holds. Convert 24 → 30 fps with frame blending, not frame duplication, or panning clips judder on every 5th frame.
28. **Brisk deadpan reads run fast.** Bella read video 12's 104 words in ~42 s (~2.5 w/s, not 2.15), so the film came in at 45.3 s, the bottom of the window. For a quick, newsy delivery, plan at ~2.4 w/s or write ~110 words.
29. **eleven_v4 can bake a pause into the text.** "Stop it suddenly," came out with 0.32 s of dead air after "Stop it" on both takes, so a retake doesn't help. Cut the silence at the edit (it is clean) or reword before generation.
30. **A falling last word can be too soft for phones.** Video 12's closing "time" sat ~10 dB under "very long" even though it cleared the bed in 300–4000 Hz. Lesson 18's band margin isn't enough: also check the last word's broadband level against the rest of its sentence, and lift it with a constant gain (~+5 dB, not a limiter) so the cadence shape stays.
31. **Honesty tags start with their graphic, and exits finish before the next claim.** QA found a drawn tag fading in 5–12 frames after its graphic, and the drained-ocean map still clearing under the "REAL" banner and MEASURED tab. A tag shares its graphic's first frame; any element tied to one claim is fully gone before the next claim's tab state. Keep honesty fine print ≥ 24 px.
32. **Don't credit a source the brief doesn't hold.** A placard said "NASA: tides ~2.3 ms/century" when only secondary reports of NASA's figure were in the research brief. Credit only sources listed in `research_brief.json`, and word ranges by what each number is (e.g. "observed ~1.7 ms · tidal ~2.3 ms").
33. **A label must never sit under a number it doesn't describe.** On video 13 the "Sun's core" label faded in under a rolling number still reading 44,900–3,110,000 °C, so a paused frame said the Sun's core was 64,600 °C (both QA A and B flagged it as major). Labels for a rolling value appear only on the seat frame, together with the final number.
34. **A meter that is honest can start too empty.** Video 13's opening was black for ~6 s because nothing glows below ~525 °C, and it read as a broken frame. Keep the honesty but give the eye something cold and unlit from frame 0: the floor and its label, the spine, an unlit outline of what will light later.
35. **Physical colour needs physical brightness too.** The first visible glow was drawn as saturated bright red; real first glow is dim and dull. Scale luminance with temperature near a threshold, not only hue.
36. **False-colour views must map the right quantity.** A brightness-based LUT turned the sky hot orange; a thermal view shows clear sky cold. Mask or model the quantity the label claims.
37. **Words like "stops changing" are absolutes too** (lesson 20): black-body colour only converges, so the mark became "colour barely changes past ~40,000 K", with a source added to the brief before it went on screen.
38. **Cross-fading two AI plates cross-fades their tags into garbled text.** Swap the tag with a hard cut at the plate crossfade's midpoint, so exactly one tag shows on every frame a plate is visible.
39. **Count an AI insect's legs before you animate it.** Both video 14 mosquito stills had 7 legs (a 3-way junction, extra knees), so the Kling clips were skipped. Count limbs and joints at 4x before spending on a clip; when a still fails, crop tightly to the parts that are right, assert in a script that every bad junction sits outside the crop, and retouch any stray limb left inside.
40. **In a drawn silhouette, any thin line from the body reads as a limb.** A long proboscis drawn down toward the feet made the six-leg gauge silhouette read as seven legs. Keep mouthparts short, curved and clearly off the head, ending well above the feet, and check the count at phone scale.
41. **A drip sound plays on the frame the drop detaches.** The drip SFX fired while the drops still hung from the body. Release each drop (attached bead → free teardrop) on its sound's frame, including drops in photo plates.
42. **A meter for one claim leaves before the next claim's tab** (lesson 31 again). The weight gauge's "~250%" was still on screen under the PROBABLY tab for peeing. Fade every gauge mark and label out before the next tab state, and check placard fine print the same way.
43. **Fade the final chord; never let the film end cut it.** The settle chord was cut in ~10 ms at about −22 dBFS on the last frame. Give the end a smooth decay over the last ~0.6 s to ≤ −35 dB, with no click in the last 20 ms.
44. **Start the closing duck at the closing sentence.** Lifting just the last word wasn't enough while the bed swelled into the final cadence; duck deeper (−13 dB) from the first word of the closing sentence, then lift the last word (lesson 30).

## Utility scripts (`docs/channel/scripts/`)

- `finish_master.sh`: the mastering chain described above. Run it as `P=... RAW=... OUT=... bash finish_master.sh`.
- `make_ending_version.py`: turns an old loop-ending video into a finished-line "ending" version without re-rendering. It replays the opening line, continues the music from its matching point in `bed_raw.mp3`, then fades the music out and fades the picture to black.
