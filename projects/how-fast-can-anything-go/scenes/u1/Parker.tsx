// sc06 · Parker · U1. root: window opens ON windowOpen2 (S3 placeholder; X4 soft hum); marker holds at EARTH, the YOU tag
// stays there. U1 Overlay: the label 'Parker Solar Probe · NASA' (T.labels.probe, verbatim) on the plate from probeLabel,
// out over 6 f ending ON `to` (the §7 seam 707: nothing of U1 shows at 707). The verified string is 384 px wide at 24 px
// (the window is 340 px wide, text must end <= x 912), so the chip WRAPS it on two lines inside the plate's top-left:
// 'Parker Solar Probe' / '· NASA' (the literal is unchanged; the SceneTag demo overflowed to x ~980).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { prog, useT } from "../../time";
import { tagBox } from "../../overlay/Tag";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Parker: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};

const TAG_PX = 24;
const TAG_W = 300; // 'Parker Solar Probe' (259 px + 0.2 px tracking) fits the first line; '· NASA' wraps under it; ends at x 896 < 920

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  const enter = T.sfx.probeLabel;
  if (frame < enter) return null;
  const out = 1 - prog(frame, to - 6, to);
  return (
    <div style={{ ...tagBox(TAG_PX, "plain"), left: L.win.x0 + 16, top: L.win.y0 + 16, width: TAG_W, height: "auto", padding: "6px 12px", whiteSpace: "normal",
      lineHeight: "30px", display: "block", opacity: out }}>
      {T.labels.probe}
    </div>
  );
};
