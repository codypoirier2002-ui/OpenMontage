// KIT TEMPLATE (docs/channel/kit, taken from video 14, QA passed). Copied by new_project.sh; the comments below describe
// video 14 - rewrite them for this video. Contract with theme.ts / time.ts / types.ts: docs/channel/kit/KIT.md.
// The placard rail (x 140-912, y 1124-1204): citations, verbatim (props.placards, build_props.py: scene_plan placards keyed
// to their scene ranges, entering 2 f into the first scene (never inside a caption page's first 4 f), leaving at the next
// range's first scene - the last one at the release of 'gone.' (gone before the settle); each held >= 1.2 s; one at a time).
// Smoked Night Ink glass at 70 %, IBM PLEX SANS CONDENSED 600 in Bone: the main line at the LARGEST size <= 26 px that fits
// the 716 px text width (measured in build_props.py), fine print >= 24 px (lesson 31) in steel. '~' is DRAWN tall by <Rich>.
// In over 6 f (slide 8 px), out over 6 f. Root overlay (scenes never mount it). Pattern of video 13's PlacardRail.
//
// <SettleCta /> (the finished-line ending): "Ever felt one land?" on the caption slab from props.cta.frame (= the last caption
// page's exit, 4 f after 'gone.' ends): the SLAB is up on its first frame (no blink from the last page: lesson 6), the text
// dissolves in from the last page's words (out 3 f, in 6 f), Bricolage Grotesque 800 52 px Bone, one line; to the last frame
// (constant from cta + 7: the settle is still).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, glass } from "../theme";
import { prog, useT } from "../time";
import type { CaptionPage, Placard } from "../types";
import { Rich } from "../shared/Type";
import { PageLines, slabBox } from "./Captions";

export const PlacardRail: React.FC<{ placards: Placard[] }> = ({ placards }) => {
  const frame = useCurrentFrame();
  const pl = placards.find((p) => frame >= p.enter && frame < p.exit);
  if (!pl) return null;
  const p = prog(frame, pl.enter, pl.enter + 6);
  const out = 1 - prog(frame, pl.exit - 6, pl.exit);
  const { x, y, w, h } = L.placard;
  const line: React.CSSProperties = { fontFamily: FONT.display, fontWeight: 600, color: C.bone, whiteSpace: "nowrap", lineHeight: 1.15 };
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
        <div style={{ ...line, fontSize: pl.fineSize ?? 24, color: C.steel, marginTop: 2 }}>
          <Rich text={pl.fine} size={pl.fineSize ?? 24} color={C.steel} />
        </div>
      ) : null}
    </div>
  );
};

// the CTA takes over from the last page's words with a short dissolve on the SAME slab (video 8 QA A fix)
export const SettleCta: React.FC<{ pages: CaptionPage[] }> = ({ pages }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < T.cta.frame) return null;
  const a = prog(frame, T.cta.frame, T.cta.frame + 3);   // KIT: 3 f swap so the settle is still from cta + 3 (video 16, lesson 25)
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
          <span key={i} style={{ fontFamily: FONT.caption, fontWeight: 800, fontSize: 52, lineHeight: 1.15, color: C.bone, opacity: a, textAlign: "center", whiteSpace: "nowrap" }}>
            {l}
          </span>
        ))}
      </div>
      {last && outA > 0 ? (
        <div style={{ ...slabBox(null), opacity: outA }}>
          <PageLines page={last} frame={frame} />
        </div>
      ) : null}
    </>
  );
};
