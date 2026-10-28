// sc12 · Settle. root: the dark bar has landed; the finished line, the release, the CTA on ctaFrame; every channel constant from the release (lesson 25). Here: a ring on the dark bar's landing, gone before the release.
// The ladder, chips, counter, window and the root devices are ROOT-owned (Composition.tsx); a scene adds emphasis only, keyed
// through useT(). Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { Ping } from "../../shared/Devices";
import { useT } from "../../time";
import { C, L } from "../../theme";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Settle: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  return (
    <>
      <Ping at={T.sfx.darkSeat} x={(L.bars.darkX0 + L.bars.darkX1) / 2} y={L.bars.base - L.bars.ordH * T.dev.bars.ratio} r0={10} r1={60} frames={18} color={C.dark} strength={0.6} />
    </>
  );
};
