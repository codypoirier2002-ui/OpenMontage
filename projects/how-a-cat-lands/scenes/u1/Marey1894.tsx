// sc03 · Marey1894 (U1). 'In 1894, that looked impossible.'
// ROOT: S1 -> the Marey strip crossfade (hard tag swap), the strip steps, the window closes windowClose1 -> catReset.
// U1: <CatLive/> (sc01's ghost, under the window, fades out 270-280 by the curves); the sc02 readouts (./readouts) hold
// through '1894' and are gone before the stamp's first visible frame; the 'IMPOSSIBLE?' <Stamp> FALLS (gravity ease-in,
// still moving on seat - 1) and is fully down ON stampImpossible (X3 thunk; 'impossible.' onset) in the OVERLAY (over the
// window's right edge), holds, and lifts off with the closing window, gone before catReset (the 288 UP pulse is the next
// claim). Stamp red only on the stamp. Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { CatLive } from "../../shared/Cat";
import { Stamp } from "../../shared/Stamp";
import { E } from "../../theme";
import { prog, useT } from "../../time";
import { Readouts } from "./readouts";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const STAMP_TEXT = "IMPOSSIBLE?";

export const Marey1894: React.FC<SceneProps> = () => {
  return (
    <>
      <CatLive />
      <Readouts />
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const s = T.seat(frame, T.sfx.stampImpossible, T.motion.SEAT_F, 0);
  // out with the window: starts as it starts closing, gone 2 f before the scene ends (= catReset)
  const out = 1 - prog(frame, T.sfx.windowClose1 - 2, to - 2, E.calm);
  if (!s.visible || out <= 0) return null;
  return <Stamp x={748} y={700} text={STAMP_TEXT} k={s.k} angle={-7} size={42} opacity={out} />;
};
