// THE SKY (ROOT ONLY): the night-ink vertical gradient (#070A12 -> #0D1424) + faint deterministic star dust (noise.ts rnd,
// never Math.random); the dust twinkles on a loop clock (T.loopFrame) so the settle is still. Hooks at the top (lesson 1).

import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { AMBIENT, C } from "../theme";
import { useT } from "../time";
import { rnd } from "./noise";

const STARS = Array.from({ length: 140 }, (_, i) => ({
  x: rnd("star-x", i) * 1080,
  y: 100 + rnd("star-y", i) * 1700,
  r: 0.6 + rnd("star-r", i) * 1.1,
  a: 0.25 + rnd("star-a", i) * 0.55,
  ph: rnd("star-ph", i) * Math.PI * 2,
}));

export const Sky: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const f = T.driftFrame(T.loopFrame(frame));
  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.skyTop} 0%, ${C.skyBottom} 100%)` }}>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        {STARS.map((s, i) => (
          <circle key={i} cx={s.x} cy={s.y} r={s.r} fill={C.bone} opacity={AMBIENT.stars * s.a * (0.75 + 0.25 * Math.sin(s.ph + f / 37))} />
        ))}
      </svg>
    </AbsoluteFill>
  );
};
