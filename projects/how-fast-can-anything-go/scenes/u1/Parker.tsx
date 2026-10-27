// sc06 · Parker · U1. root: window opens ON windowOpen2 (S3 placeholder; X4 soft hum); marker holds at EARTH, the YOU tag stays there. U1 Overlay: the label 'Parker Solar Probe · NASA' on the plate from probeLabel (the demo uses T.labels.probe).
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { useT } from "../../time";
import { SceneTag } from "../../overlay/Tag";
import { L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Parker: React.FC<SceneProps> = ({ from, to }) => {
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
      <StubLabel id="sc06" from={from} to={to} />
      <SceneTag x={L.win.x0 + 16} y={L.win.y0 + 16} enter={T.sfx.probeLabel} exit={to} text={T.labels.probe} />
    </>
  );
};
