// KIT TEMPLATE (docs/channel/kit, taken from video 14, QA passed). Copied by new_project.sh; the comments below describe
// video 14 - rewrite them for this video. Contract with theme.ts / time.ts / types.ts: docs/channel/kit/KIT.md.
// Caption slab (channel standard): x 140-940, y 1296-1488, text x 168-912. Copied from
// projects/how-hot-can-it-get/overlay/Captions.tsx (video 13, QA passed; itself videos 9-12), incl. its QA fixes:
// back-to-back pages keep the slab up (lesson 6; build_props.py also butts pages closer than 13 f and pages ending inside a
// sentence), a page after a pause PRE-ROLLS, toned words STEP when lit (colour lift + glow).
// Accessibility subtitles: script text verbatim; the plan's pages (the lesson-3 re-flows, build_props.py PAGES), line breaks
// precomputed (<= 2 lines, <= 6 words, 700 px line budget inside the 744 px text column, so nothing reaches x >= 929 or
// y >= 1574). Word states: upcoming 45 % · active 100 % lifted 3 px · spoken 82 %. Tones (art direction): 'blood' = the
// word 'blood' in Vessel red lightened for the dark slab; 'saliva' = the word 'saliva' in Saliva cyan (the colour rules: red
// only for blood, cyan only for saliva - the caption names them); else Bone. The slab exists only while a page is up: empty
// on frame 0 and in pauses; from props.cta.frame (= the last page's exit) <SettleCta> owns it. Hooks: useCurrentFrame()
// BEFORE the early return. Every word onset is its measured voice onset (align_narration.py: the 106-word sweep).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, glass } from "../theme";
import { prog } from "../time";
import type { CaptionPage, CaptionTone } from "../types";

const lift = (hex: string, k: number) => {
  const ch = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  const v = ch.map((c) => Math.round(c + (255 - c) * k));
  return `rgb(${v[0]},${v[1]},${v[2]})`;
};
// KIT: one entry per CaptionTone in types.ts (the video's colour rules), e.g. video 14: blood: C.vesselLit, saliva: C.saliva
// with GLOW blood: "224,90,96", saliva: "159,216,230". The plain tone is the channel standard.
const TONE: Record<CaptionTone, string> = { plain: C.bone };
const GLOW: Record<CaptionTone, string> = { plain: "244,239,230" };

export const CAPTION_PREROLL = 4;

/** The page's lines (no hooks: the caller passes the frame). Shared with <SettleCta>'s crossfade. */
export const PageLines: React.FC<{ page: CaptionPage; frame: number }> = ({ page, frame }) => {
  const lines = [0, 1].map((li) => page.words.filter((w) => w.line === li)).filter((l) => l.length);
  return (
    <>
      {lines.map((line, li) => (
        <div key={li} style={{ display: "flex", gap: "0 15px", whiteSpace: "nowrap", maxWidth: L.slab.textRight - L.slab.textX }}>
          {line.map((w, wi) => {
            const active = frame >= w.f0 && frame < w.f1;
            const spoken = frame >= w.f1;
            const toned = w.tone !== "plain";
            const color = TONE[w.tone];
            // toned words STEP when they light (upcoming 50 %, active 100 % + colour lift + glow, spoken 72 %) - video 11 QA A7
            const alpha = active ? 1 : toned ? (spoken ? 0.72 : 0.5) : spoken ? 0.82 : 0.45;
            const shown = toned && active ? lift(color, 0.25) : color;
            return (
              <span
                key={wi}
                style={{
                  position: "relative",
                  fontFamily: FONT.caption,
                  fontWeight: 800,
                  fontSize: 58,
                  lineHeight: 1.12,
                  color: shown,
                  opacity: alpha,
                  transform: `translateY(${active ? -3 : 0}px)`,
                  textShadow: toned && active ? `0 0 18px rgba(${GLOW[w.tone]},0.5), 0 2px 10px rgba(10,11,16,0.35)` : "0 2px 10px rgba(10,11,16,0.35)",
                }}
              >
                {w.text}
              </span>
            );
          })}
        </div>
      ))}
    </>
  );
};

/** the slab box (position, glass, the text column) - Captions and SettleCta's crossfade share it */
export const slabBox = (glassAlpha: number | null): React.CSSProperties => ({
  position: "absolute",
  left: L.slab.x,
  top: L.slab.y,
  width: L.slab.w,
  height: L.slab.h,
  borderRadius: 24,
  ...(glassAlpha === null ? {} : glass(glassAlpha)),
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  paddingLeft: L.slab.textX - L.slab.x,
  boxSizing: "border-box",
});

export const Captions: React.FC<{ pages: CaptionPage[]; ctaFrame?: number; glassAlpha?: number }> = ({ pages, ctaFrame, glassAlpha = 0.62 }) => {
  const frame = useCurrentFrame();
  // a page is butted at f when another page starts / ends there (or the CTA takes the slab there)
  const buttedAt = (pg: CaptionPage, f: number) => f === ctaFrame || pages.some((p) => p !== pg && (p.exitFrame === f || p.startFrame === f));
  const page =
    pages.find((p) => frame >= p.startFrame && frame < p.exitFrame) ??
    pages.find((p) => frame >= p.startFrame - CAPTION_PREROLL && frame < p.startFrame && !buttedAt(p, p.startFrame));
  if (!page) return null;
  // back-to-back pages keep the slab up; only a page that follows / precedes a gap fades
  const fadeIn = buttedAt(page, page.startFrame) ? 1 : prog(frame, page.startFrame - CAPTION_PREROLL, page.startFrame);
  const fadeOut = buttedAt(page, page.exitFrame) ? 1 : 1 - prog(frame, page.exitFrame - 3, page.exitFrame);
  return (
    <div style={{ ...slabBox(glassAlpha), opacity: Math.min(fadeIn, fadeOut) }}>
      <PageLines page={page} frame={frame} />
    </div>
  );
};
