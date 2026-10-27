// Honesty / provenance tags (pattern of projects/what-if-earth-stopped-spinning/overlay/Tag.tsx, video 12; re-skinned
// for the forge): a small Forge Black chip (78 %), IBM Plex Mono 400 24 px Bone (fine print >= 24 px, lesson 31).
//   ROOT (scenes never mount it): <WindowTags/> (shared/Window.tsx) - 'AI impression' (K1), 'AI impression · not a photo'
//   (S2), 'AI illustration' (K2, S4), 'false colour' (the K1 LUT): each tied to its plate's actual visibility.
//   SCENES: <SceneTag x y enter exit text/> in their Overlay for their OWN drawings ('drawn', 'drawn · illustrative',
//   'lead melts at 327 °C · drawn' ...). A tag starts ON its graphic's first visible frame (no wipe delay: lesson 31) and is
//   gone before the next claim's tab state; inside x <= 912 and y < 1574, never under the placard rail / tab / slab. Every
//   tag text must be in scene_plan.metadata.verified_on_screen_strings (lesson 20; build_props.py scans your literals).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, rgba } from "../theme";
import { hatch } from "../shared/Type";
import { prog } from "../time";

export const tagBox = (size: number, variant: "plain" | "probably"): React.CSSProperties => ({
  position: "absolute", height: size + 14, padding: "0 12px", display: "flex", alignItems: "center", boxSizing: "border-box",
  backgroundColor: rgba(C.forge, 0.78), border: variant === "probably" ? `1.5px solid ${C.bone}` : "none",
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
