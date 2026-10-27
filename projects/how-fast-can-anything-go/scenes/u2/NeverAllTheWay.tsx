// sc12 · NeverAllTheWay · U2. NO SFX from closingStart. root: the full ladder, the marker just under 'c', the gap bracket, the YOU tag at EARTH, the counter at 9; release wayEndFrame, chord chordFrame, CTA ctaFrame, tab IDLE. U2: <NinesReadoutLive/> constant; NOTHING may change after wayEndFrame.
// FOUNDATION STUB: replace the <StubLabel> and the demo with the real scene; keep `mount`, the export names and the
// device mounts noted in BUILD.md §7. Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { StubLabel } from "../_stub";
import { NinesReadoutLive } from "../../shared/Devices";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const NeverAllTheWay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <NinesReadoutLive />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <StubLabel id="sc12" from={from} to={to} />
    </>
  );
};
