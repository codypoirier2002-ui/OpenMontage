# HyperFrames Skills — Provenance

The 7 HyperFrames-family skills under `.agents/skills/` are vendored from the upstream HyperFrames monorepo:

- **Source**: https://github.com/heygen-com/hyperframes
- **Vendored commit**: `5e4f5ae` (`main`, 2026-10-30)
- **Nearest tag**: `v0.8.222`
- **Vendor date**: 2026-10-31
- **Previous vendor**: `3351fb1a` / `v0.7.17` (2026-06-27)

The HyperFrames CLI itself is not pinned: `hyperframes_compose` runs `npx hyperframes`, which resolves to the latest npm release. Keep these skills close to upstream so they teach the CLI that actually runs.

## What's vendored

| Skill | Notes |
|---|---|
| `hyperframes` | Entry point. In 0.8 it absorbed the 0.7 split skills: the render contract is in `SKILL.md`, everything else in `references/` (see the map below). |
| `hyperframes-cli` | CLI by job: `init`, `check`, `snapshot`, `timeline`, `history`, `preview`, `render`, `capture`, `beats`, `publish`, cloud render, failure recovery. |
| `hyperframes-registry` | ~450 blocks/components installed as editable source via `hyperframes add`. |
| `media-use` | Media for any HyperFrames video. The `resolve` verb now ships in the CLI as `npx hyperframes media-use resolve`; also `generate`, `media-treatment`, grading, mixing, bundled offline SFX. |
| `remotion-to-hyperframes` | Migration — used ONLY when the user explicitly asks to port a Remotion (or Motion Canvas, Lottie, Three.js, …) source. |
| `figma` | Figma → HyperFrames assets, tokens and storyboard frames. Vendored because the `hyperframes` router links to `/figma`. |
| `slideshow` | Live-presented decks via `hyperframes present`. Vendored because the router links to `/slideshow`; not an OpenMontage pipeline. |

## Where the removed 0.7 skills went

These were separate skills at v0.7.17 and no longer exist upstream. Their content now lives in:

| v0.7.17 skill | v0.8 location |
|---|---|
| `hyperframes-core` | `hyperframes/SKILL.md` (Contract, Keep it editable) + `hyperframes/references/format.md` |
| `hyperframes-creative` | `hyperframes/references/look.md`, `story.md`, `spec.md`, `storyboard.md` |
| `hyperframes-media` | `media-use/` (+ `hyperframes/references/sound.md`, `captions.md`) |
| `hyperframes-animation` | `hyperframes/references/motion.md`, `runtimes.md` (GSAP, Lottie, Three.js, canvas adapters) |
| `motion-graphics` | `hyperframes/references/types/launch.md`, `film.md` (kinetic type, title cards) |
| `music-to-video` | `hyperframes/references/types/music.md` (+ `npx hyperframes beats`) |
| `website-to-video` | `hyperframes/references/film.md` (+ `npx hyperframes capture <url>`) |

## Intentionally NOT vendored

- `reverse-any-video` — marked `internal: true` upstream, and its job ("recreate, replicate or copy a video") conflicts with OpenMontage's reference-video rule (`skills/meta/video-reference-analyst.md`: produce differentiated concepts, not a carbon copy).

## OpenMontage-local patches

Re-apply these after every re-vendor. Each is fenced with `<!-- OpenMontage-local patch -->` comments.

| File | Patch |
|---|---|
| `media-use/audio/references/tts.md` | "Expressive narration contract" section, inserted after "When to use which provider". Carried over from `hyperframes-media/references/tts.md` at v0.7.17. |

## Re-sync instructions

```bash
git clone --depth 50 https://github.com/heygen-com/hyperframes.git /tmp/hfup
# In OpenMontage:
cp .agents/skills/hyperframes/PROVENANCE.md /tmp/PROVENANCE.md
for d in hyperframes hyperframes-cli hyperframes-registry media-use \
         remotion-to-hyperframes figma slideshow; do
  rm -rf ".agents/skills/$d"
  cp -r "/tmp/hfup/skills/$d" ".agents/skills/$d"
done
cp /tmp/PROVENANCE.md .agents/skills/hyperframes/PROVENANCE.md
# Re-apply the OpenMontage-local patches above, check `ls /tmp/hfup/skills`
# for added/removed skills, then update the commit/tag/date at the top of this file.
python -m pytest tests/contracts/test_agent_skill_pointers.py
```
