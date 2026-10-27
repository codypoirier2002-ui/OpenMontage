// sc02 · NothingToPush (U1). 'with nothing to push on.'
// ROOT: the window opens ON windowOpen1 (S1 'AI impression', X2 slide) over the ghost of sc01's cat.
// U1: <CatLive/> (the ghost outline, under the window) + the two drawn readouts in the right column, each seated ON its
// word ('push: none' ON readouts[0] = 'nothing', 'starting spin: 0' ON readouts[1] = 'push'; no SFX). The readouts are the
// shared U1 helper (./readouts), also mounted by sc03, so the 161 / 162 seam is identical. Hooks at the top (lesson 1).

import React from "react";
import type { Mount, SceneProps } from "../../types";
import { CatLive } from "../../shared/Cat";
import { Readouts } from "./readouts";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const NothingToPush: React.FC<SceneProps> = () => {
  return (
    <>
      <CatLive />
      <Readouts />
    </>
  );
};
