// sc01 · Walk · U1. root: the dim rail + the marker at WALK from f0, the rail DRAWS on 'You' (railDraw, X1), the WALK chip SEATS on 'walk'. U1 demo: a walker icon beside the WALK rung.
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { WalkerIcon } from "../../shared/Icons";
import { useT } from "../../time";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Walk: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const w = T.rung("walk");
  const s = T.seat(frame, w.seat, T.motion.SEAT_F, 18);
  if (frame < from || frame >= to) return null;
  return (
    <>
      {s.visible ? (
        <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
          <WalkerIcon x={L.rail.labelX + 152} y={T.railY(w.L) + s.y} size={28} phase={(frame % 24) / 24} opacity={s.opacity} />
        </svg>
      ) : null}
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc01" from={from} to={to} />
    </>
  );
};
