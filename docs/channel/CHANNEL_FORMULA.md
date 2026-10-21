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

Mirror the most recent delivered project's layout. `projects/why-cant-you-tickle-yourself/` is the newest; if
`projects/` is gone, rebuild from this description.

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

## Utility scripts (`docs/channel/scripts/`)

- `finish_master.sh`: the mastering chain described above. Run it as `P=... RAW=... OUT=... bash finish_master.sh`.
- `make_ending_version.py`: turns an old loop-ending video into a finished-line "ending" version without re-rendering. It replays the opening line, continues the music from its matching point in `bed_raw.mp3`, then fades the music out and fades the picture to black.
