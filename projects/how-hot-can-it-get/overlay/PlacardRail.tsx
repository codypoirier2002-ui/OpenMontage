// The placard rail (x 140-912, y 1124-1204): citations, verbatim (props.placards, build_props.py: scene_plan placards keyed
// to their scene ranges, entering 2 f into the first scene (never inside a caption page's first 4 f), leaving at the next
// scene's boundary - the last one at the release of 'know.' (gone before the settle); each held >= 1.2 s; one at a time).
// Smoked Night Ink glass at 70 %, SAIRA CONDENSED 700 (IBM Plex Mono cannot fit the KSTAR / Planck placards with >= 24 px
// fine print: fetch_fonts.py placard_fit, BUILD.md §9) in Bone: the main line at the LARGEST size <= 26 px that fits the
// 716 px text width (measured in build_props.py), fine print >= 24 px (lesson 31) in Ash-lit Bone. '≈' and the exponent
// of '10^32' are DRAWN by <Rich> (no face carries '≈'; '^' is never set). In over 6 f (slide 8 px), out over 6 f.
// Root overlay (scenes never mount it). Copied from projects/what-if-earth-stopped-spinning/overlay/PlacardRail.tsx (video 12).
//
// <SettleCta /> (the finished-line ending): "Floor or ceiling - which is stranger?" on the caption slab from props.cta.frame
// (= the last caption page's exit, 4 f after 'know.' ends): the SLAB is up on its first frame (no blink from the last page:
// lesson 6), the text dissolves in from the last page's words (out 3 f, in 6 f), Bricolage Grotesque 800 46 px in the
// settle glow's colour (lifted), on two lines (props.cta.lines); to the last frame (constant from cta + 7: the settle is still).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, glass } from "../theme";
import { prog, useT } from "../time";
import type { CaptionPage, Placard } from "../types";
import { Rich } from "../shared/Type";
import { PageLines, heatColour, slabBox } from "./Captions";

export const PlacardRail: React.FC<{ placards: Placard[] }> = ({ placards }) => {
  const frame = useCurrentFrame();
  const pl = placards.find((p) => frame >= p.enter && frame < p.exit);
  if (!pl) return null;
  const p = prog(frame, pl.enter, pl.enter + 6);
  const out = 1 - prog(frame, pl.exit - 6, pl.exit);
  const { x, y, w, h } = L.placard;
  const line: React.CSSProperties = { fontFamily: FONT.display, fontWeight: 700, color: C.bone, whiteSpace: "nowrap", lineHeight: 1.15 };
  return (
    <div
      style={{
        position: "absolute", left: x, top: y, width: w, height: h, borderRadius: 10, ...glass(0.7), boxSizing: "border-box",
        padding: "0 28px", display: "flex", flexDirection: "column", justifyContent: "center", opacity: p * out,
        transform: `translateY(${8 * (1 - p)}px)`, overflow: "hidden",
      }}
    >
      {pl.lines.map((l, i) => (
        <div key={i} style={{ ...line, fontSize: pl.size }}>
          <Rich text={l} size={pl.size} color={C.bone} />
        </div>
      ))}
      {pl.fine ? (
        <div style={{ ...line, fontSize: pl.fineSize ?? 24, color: C.ash, opacity: 1, marginTop: 2 }}>
          <Rich text={pl.fine} size={pl.fineSize ?? 24} color={C.ash} />
        </div>
      ) : null}
    </div>
  );
};

// the CTA takes over from the last page's words with a short dissolve on the SAME slab (video 8 QA A fix)
export const SettleCta: React.FC<{ pages: CaptionPage[] }> = ({ pages }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const g = T.glow(frame);
  if (frame < T.cta.frame) return null;
  const heat = heatColour(g.k, g.i);
  const ctaColour = `rgb(${heat[0]},${heat[1]},${heat[2]})`;
  const a = prog(frame, T.cta.frame + 1, T.cta.frame + 7);
  const outA = 1 - prog(frame, T.cta.frame, T.cta.frame + 3);
  const last = pages.find((p) => p.exitFrame === T.cta.frame);
  return (
    <>
      <div
        style={{
          position: "absolute", left: L.slab.x, top: L.slab.y, width: L.slab.w, height: L.slab.h, borderRadius: 24, ...glass(0.62),
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: `0 ${L.slab.textX - L.slab.x}px`, boxSizing: "border-box",
        }}
      >
        {T.cta.lines.map((l, i) => (
          <span key={i} style={{ fontFamily: FONT.caption, fontWeight: 800, fontSize: 46, lineHeight: 1.15, color: ctaColour, opacity: a, textAlign: "center", whiteSpace: "nowrap" }}>
            {l}
          </span>
        ))}
      </div>
      {last && outA > 0 ? (
        <div style={{ ...slabBox(null), opacity: outA }}>
          <PageLines page={last} frame={frame} heat={heat} />
        </div>
      ) : null}
    </>
  );
};
