// sc03 · DeathValley · U1. The root opens the window on K1 ('AI impression'), seats the DV rung tick ON T.sfx.dvSeat (X7)
// and fades in the labelled false colour on T.sfx.lutOn. U1 draws the HERO label '56.7 °C' + 'Death Valley · 1913 · air'
// (strings from the props) on a Forge Black card inside the window's lower left (above the root 'false colour' tag,
// y 846-884), with a leader to the rung tick (y ~907, just under the window). It falls with the tick (T.seat gravity
// drop, fully down ON dvSeat) and is gone by the scene end (the root compact number takes over from 328; the Venus claim
// pulses the tab at 330). No glow, no warm halo: 56.7 °C does not glow. Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import { prog, useT } from "../../time";
import type { Mount, SceneProps } from "../../types";
import { HeroCard } from "./parts";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

/** card position inside the window (number centre line); the card's bottom stays above the window's bottom tags */
const CARD = { x: 250, y: 722 };

export const DeathValley: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const r = T.rung("dv");
  const s = T.seat(frame, T.sfx.dvSeat, 8, 18);
  const out = 1 - prog(frame, to - 8, to);
  const tickY = T.railY(r.L, frame);
  if (frame < from || frame >= to || !s.visible) return null;
  return <HeroCard x={CARD.x} y={CARD.y} num={r.num} label={r.label} tickY={tickY} dy={s.y} opacity={s.opacity * out} />;
};
