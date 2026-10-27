// sc07 · Falling · U2. root: climb from climbParker (X1), PARKER chip (two lines) ON parkerSeat; the window (S3) stays open and closes windowClose2. U2 Overlay: an SVG <Arrow> on the plate pointing toward the Sun + the label 'falling toward the Sun' from fallArrow (the demo uses T.labels.falling).
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { useT } from "../../time";
import { SceneTag } from "../../overlay/Tag";
import { Arrow } from "../../shared/Icons";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Falling: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc07" from={from} to={to} />
      {frame >= T.sfx.fallArrow ? (
        <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
          <Arrow x1={L.win.x0 + 170} y1={L.win.y1 - 130} x2={L.win.x0 + 170} y2={L.win.y0 + 120} width={4} head={14} />
        </svg>
      ) : null}
      <SceneTag x={L.win.x0 + 16} y={L.win.y0 + 16} enter={T.sfx.fallArrow} exit={to} text={T.labels.falling} />
    </>
  );
};
