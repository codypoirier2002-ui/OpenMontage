// KIT TEMPLATE (docs/channel/kit, taken from video 14, QA passed). Copied by new_project.sh; the comments below describe
// video 14 - rewrite them for this video. Contract with theme.ts / time.ts / types.ts: docs/channel/kit/KIT.md.
// Honesty / provenance tags (pattern of projects/how-hot-can-it-get/overlay/Tag.tsx, video 13): a small Tray-Shadow chip
// (82 %), Roboto Mono 400 24 px Bone (fine print >= 24 px, lesson 31).
//   ROOT (scenes never mount them): <DrawnTag/> - 'drawn · not to scale' under the tray / field (x 140, y 1086), from frame 0
//   to the end (the tray and the cross-section are drawings on every frame; constant, so the settle is still);
//   <WindowTags/> (shared/Window.tsx) - 'AI impression' on each OR-cam plate.
//   SCENES: <SceneTag x y enter exit text/> in their Overlay for their OWN drawings / claims (e.g. 'drawn · not to scale' on
//   the sheath diagram, the PROBABLY chip 'about half never found one · one lab study (mice)' with variant 'probably'). A tag
//   starts ON its graphic's first visible frame (lesson 31) and is gone before the next claim's tab state; inside x <= 912
//   and y < 1574, never under the placard rail / tab / slab. Every tag text must be in
//   scene_plan.metadata.verified_on_screen_strings (lesson 20; build_props.py scans your literals).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { hatch } from "../shared/Type";
import { prog, useT } from "../time";

export const tagBox = (size: number, variant: "plain" | "probably"): React.CSSProperties => ({
  position: "absolute", height: size + 14, padding: "0 12px", display: "flex", alignItems: "center", boxSizing: "border-box",
  backgroundColor: rgba(C.shadow, 0.82), border: variant === "probably" ? `1.5px solid ${C.bone}` : "none",
  backgroundImage: variant === "probably" ? hatch(C.bone, 0.16) : undefined, borderRadius: variant === "probably" ? 16 : 6,
  fontFamily: FONT.mono, fontWeight: 400, fontSize: size, letterSpacing: 0.2, color: C.bone, whiteSpace: "nowrap",
});

/** a scene's own tag (overlay plane; x/y = its top-left, or its top-right with anchor 'right'); fully visible ON `enter`
 *  (it shares its graphic's first frame), out over 6 f ending ON `exit` */
export const SceneTag: React.FC<{
  x: number; y: number; enter: number; exit: number; text: string; variant?: "plain" | "probably"; size?: number; opacity?: number; anchor?: "left" | "right";
}> = ({ x, y, enter, exit, text, variant = "plain", size = 24, opacity = 1, anchor = "left" }) => {
  const frame = useCurrentFrame();
  if (frame < enter || frame >= exit) return null;
  const out = 1 - prog(frame, exit - 6, exit);
  return (
    <div style={{ ...tagBox(size, variant), left: x, top: y, transform: anchor === "right" ? "translateX(-100%)" : undefined, opacity: out * opacity }}>
      {text}
    </div>
  );
};

/** ROOT: 'drawn · not to scale' for the tray and the skin cross-section (every frame) */
export const DrawnTag: React.FC = () => {
  const T = useT();
  return <div style={{ ...tagBox(24, "plain"), left: L.drawnTag.x, top: L.drawnTag.y }}>{T.labels.drawn}</div>;
};
