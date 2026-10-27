// sc12 · NeverAllTheWay · U2 (1358-1478). The finished-line ending. NO SFX from closingStart ('But'). ROOT: the full ladder
// with all seven chips, the marker steady 14 px under 'c' with the gap bracket + 'the gap', the YOU tag at EARTH, the
// counter at 9; release wayEndFrame (1432), chord chordFrame, CTA ctaFrame, tab IDLE; every root channel constant from 1432.
// U2 PICTURE: <NinesReadoutLive/> only (engine; count 10 and alpha 1 are constant from 1289 / 1235: the SAME component with
// the SAME props at 1357 / 1358 and on every frame through the settle). NOTHING of ours changes after wayEndFrame (lesson 25).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { NinesReadoutLive } from "../../shared/Devices";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const NeverAllTheWay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return <NinesReadoutLive />;
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
