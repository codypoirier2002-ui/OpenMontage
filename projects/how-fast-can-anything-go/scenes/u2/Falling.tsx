// sc07 · Falling · U2 (707-873). ROOT: the marker climbs EARTH -> PARKER from climbParker (X1 whoosh, streaks) and the
// two-line PARKER chip seats ON parkerSeat; the window (S3, 'AI impression') stays open and closes windowClose2 -> 873;
// the YOU tag holds at EARTH; counter 5. U2 OVERLAY (over the window): <FallArrow/>: an SVG arrow on the plate pointing at
// the Sun (the top of the plate), drawing on from fallArrow ('falling'), with the label 'falling toward the Sun' on the same
// first frame (lesson 31); both fade out 6 f ending ON windowClose2, 10 f before the LIGHT page (lessons 42 / 47).
// The picture layer draws nothing: the climb and the chip are the root's. At 707 nothing of ours shows (seam with sc06).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { FallArrow } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const Falling: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return <FallArrow />;
};
