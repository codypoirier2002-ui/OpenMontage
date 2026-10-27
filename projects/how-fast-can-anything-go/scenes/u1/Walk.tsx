// sc01 · Walk · U1. root: the dim rail + the marker at WALK from f0, the rail DRAWS bright on 'You' (railDraw, X1), the
// WALK chip + tick SEAT on 'walk' (walkSeat). U1: a walker icon that seats beside the WALK chip WITH the chip (T.seat on
// walkSeat, same gravity drop), legs on the loop clock; a bone glint riding the draw head while the rail draws (never
// reaching 'c'). The walker is tied to the WALK claim: gone 8 f before the CHEETAH page (lesson 42).
// Hooks at the top, before any early return (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import type { Mount, SceneProps } from "../../types";
import { WalkerIcon } from "../../shared/Icons";
import { measure } from "../../shared/Type";
import { prog, useT } from "../../time";
import { L } from "../../theme";
import { RailGlint } from "./_fx";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const LABEL_PX = 28;
const CHIP_PAD = 12;

export const Walk: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const w = T.rung("walk");
  const s = T.seat(frame, w.seat, T.motion.SEAT_F, 18);
  if (frame < from || frame >= to) return null;
  // the WALK chip's width (shared/Ladder.tsx's chip rule) so the walker stands just right of it
  const [name, num] = w.lines[0].split(" · ");
  const chipW = measure(name, "display", LABEL_PX) + measure(" · ", "display", LABEL_PX) + measure(num, "monoMed", LABEL_PX) + 2 * CHIP_PAD;
  const nextPage = T.at("s1", "a"); // the CHEETAH page (tab pulse) starts ON 'A' (cheetah)
  const gone = 1 - prog(frame, nextPage - 16, nextPage - 8);
  const alpha = s.opacity * gone;
  const phase = (T.loopFrame(frame) % 24) / 24;
  return (
    <>
      <RailGlint />
      {s.visible && alpha > 0 ? (
        <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
          <WalkerIcon x={L.rail.labelX + chipW + 22} y={T.railY(w.L) + s.y} size={30} phase={phase} opacity={alpha} />
        </svg>
      ) : null}
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame >= to) return null;
  return null;
};
