// Caption slab (channel standard): x 140-940, y 1296-1488, text x 168-912. Copied from
// projects/what-if-earth-stopped-spinning/overlay/Captions.tsx (video 12, QA passed; itself videos 9-11), incl. its QA fixes:
// back-to-back pages keep the slab up (lesson 6; build_props.py also butts pages closer than 11 f and pages ending inside a
// sentence), a page after a pause PRE-ROLLS, toned words STEP when lit (colour lift + glow).
// Accessibility subtitles: script text verbatim ('fifty-seven', 'four hundred sixty-five' - never digits); the plan's pages
// (the lesson-3 re-flows, build_props.py PAGES), line breaks precomputed (<= 2 lines, <= 6 words, 700 px line budget inside
// the 744 px text column, so nothing reaches x >= 929 or y >= 1574). Word states: upcoming 45 % · active 100 % lifted
// 3 px · spoken 82 %. Tones (art direction): 'heat' = a spoken NUMBER word takes the CURRENT black-body colour of the
// glow (T.glow(frame), lifted 30 % toward white for contrast on the slab; before the glow - sc01-sc04 - neutral
// Bone, QA B8); 'ice' = 'floor:' takes Ice; else Bone. The slab exists only while a page is up: empty on frame
// 0 and in pauses; from props.cta.frame (= the last page's exit) <SettleCta> owns it. Hooks: useCurrentFrame() / useT()
// BEFORE the early return. Every word onset is its measured voice onset (align_narration.py: the 109-word sweep).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, glass } from "../theme";
import { bbRgb, lighten } from "../shared/blackbody";
import { prog, useT } from "../time";
import type { CaptionPage } from "../types";

/** QA A: a page that follows a pause PRE-ROLLS: the slab and its words (upcoming 45 %) fade in over the CAPTION_PREROLL
 *  frames BEFORE the page start, so on the first word's onset frame the slab is fully up and that word is lit (100 %).
 *  Back-to-back pages (and the last page, which hands the slab to the CTA) keep the slab up: no fade, no blink. */
const lift = (css: string, k: number) => {
  const ch = css.startsWith("#")
    ? [1, 3, 5].map((i) => parseInt(css.slice(i, i + 2), 16))
    : (css.match(/[0-9.]+/g) ?? ["0", "0", "0"]).slice(0, 3).map(Number);
  const v = ch.map((c) => Math.round(c + (255 - c) * k));
  return `rgb(${v[0]},${v[1]},${v[2]})`;
};

export const CAPTION_PREROLL = 4;

/** the 'heat' tone colour at a frame: the glow's black-body colour (lifted 30 % for contrast), or before the glow the
 *  neutral Bone (QA B8: nothing warm before the glow) */
export const heatColour = (k: number, i: number): [number, number, number] => (i > 0.05 ? lighten(bbRgb(k), 0.3) : [244, 239, 230]);

/** The page's lines (no hooks: the caller passes the frame and the heat colour). Shared with <SettleCta>'s crossfade. */
export const PageLines: React.FC<{ page: CaptionPage; frame: number; heat: [number, number, number] }> = ({ page, frame, heat }) => {
  const lines = [0, 1].map((li) => page.words.filter((w) => w.line === li)).filter((l) => l.length);
  const heatCss = `rgb(${heat[0]},${heat[1]},${heat[2]})`;
  return (
    <>
      {lines.map((line, li) => (
        <div key={li} style={{ display: "flex", gap: "0 15px", whiteSpace: "nowrap", maxWidth: L.slab.textRight - L.slab.textX }}>
          {line.map((w, wi) => {
            const active = frame >= w.f0 && frame < w.f1;
            const spoken = frame >= w.f1;
            const color = w.tone === "heat" ? heatCss : w.tone === "ice" ? C.ice : C.bone;
            // toned words STEP when they light (upcoming 50 %, active 100 % + colour lift + glow, spoken 72 %) - video 11 QA A7
            const toned = w.tone !== "plain";
            const alpha = active ? 1 : toned ? (spoken ? 0.72 : 0.5) : spoken ? 0.82 : 0.45;
            const shown = toned && active ? lift(color, 0.35) : color;
            const glowRgb = w.tone === "ice" ? "159,201,218" : `${heat[0]},${heat[1]},${heat[2]}`;
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
                  textShadow: toned && active ? `0 0 18px rgba(${glowRgb},0.55), 0 2px 10px rgba(10,11,16,0.35)` : "0 2px 10px rgba(10,11,16,0.35)",
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
  const T = useT();
  const g = T.glow(frame);
  // a page is butted at f when another page starts / ends there (or the CTA takes the slab there)
  const buttedAt = (pg: CaptionPage, f: number) => f === ctaFrame || pages.some((p) => p !== pg && (p.exitFrame === f || p.startFrame === f));
  const page =
    pages.find((p) => frame >= p.startFrame && frame < p.exitFrame) ??
    pages.find((p) => frame >= p.startFrame - CAPTION_PREROLL && frame < p.startFrame && !buttedAt(p, p.startFrame));
  if (!page) return null;
  // QA (tickle A): back-to-back pages keep the slab up; only a page that follows / precedes a gap fades
  const fadeIn = buttedAt(page, page.startFrame) ? 1 : prog(frame, page.startFrame - CAPTION_PREROLL, page.startFrame);
  const fadeOut = buttedAt(page, page.exitFrame) ? 1 : 1 - prog(frame, page.exitFrame - 3, page.exitFrame);
  return (
    <div style={{ ...slabBox(glassAlpha), opacity: Math.min(fadeIn, fadeOut) }}>
      <PageLines page={page} frame={frame} heat={heatColour(g.k, g.i)} />
    </div>
  );
};
