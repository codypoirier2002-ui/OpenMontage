// sc04 · Venus · U1. The root crossfades the window K1 -> S2 ('AI impression · not a photo') on T.sfx.venusXfade, seats
// the Venus rung tick ON T.sfx.venusSeat (X7) and fades in the Draper mark 'first visible glow ~525 °C' (just ABOVE the
// Venus rung) on T.sfx.draperMark. U1 draws:
//   - the HERO label '~464 °C' + 'Venus surface' (props strings) on a Forge Black card just UNDER the Venus rung (clear of
//     the Draper label above it), falling with the tick, fully down ON venusSeat;
//   - a drawn lead ingot (lead grey, UNLIT) that drops in on 'hot' and slumps into a puddle from T.sfx.leadMelt, with the
//     tag 'lead melts at 327 °C · drawn' (Overlay; it shares the ingot's first visible frame, lesson 31).
// Honesty: Venus (~464 °C) and molten lead (327 °C) are below the first visible glow: no glow, no orange, no halo.
// Everything is out by the scene end (481: the window closes, the sweep starts). Hooks at the top (lesson 1).
import React from "react";
import { useCurrentFrame } from "remotion";
import { E } from "../../theme";
import { SceneTag } from "../../overlay/Tag";
import { prog, useT } from "../../time";
import type { Mount, SceneProps } from "../../types";
import { HeroCard, Ingot } from "./parts";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const LEAD_LABEL = "lead melts at 327 °C · drawn";
const CARD = { x: 236, y: 680 };
/** the ingot's base centre, right of the card; its tag right-aligned under it (above the window's bottom tags) */
const INGOT = { cx: 750, by: 748 };
const TAG = { x: 904, y: 790 };
const MELT_FRAMES = 26;
const OUT_FRAMES = 8;

/** the ingot drops in landing ON 'hot' (no SFX: a quiet arrival); first visible frame = landing - 7 */
const ingotLand = (T: ReturnType<typeof useT>) => T.at("s2", "hot");

export const Venus: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  const r = T.rung("venus");
  const s = T.seat(frame, T.sfx.venusSeat, 8, 18);
  const ing = T.seat(frame, ingotLand(T), 8, 14);
  const melt = prog(frame, T.sfx.leadMelt, T.sfx.leadMelt + MELT_FRAMES, E.calm);
  const out = 1 - prog(frame, to - OUT_FRAMES, to);
  const tickY = T.railY(r.L, frame);
  if (frame < from || frame >= to) return null;
  return (
    <>
      {s.visible ? <HeroCard x={CARD.x} y={CARD.y} num={r.num} label={r.label} tickY={tickY} dy={s.y} opacity={s.opacity * out} /> : null}
      {ing.visible ? <Ingot cx={INGOT.cx} by={INGOT.by} melt={melt} dy={ing.y} opacity={ing.opacity * out} /> : null}
    </>
  );
};

export const Overlay: React.FC<SceneProps> = ({ to }) => {
  const T = useT();
  const enter = ingotLand(T) - 7;
  return <SceneTag x={TAG.x} y={TAG.y} enter={enter} exit={to} text={LEAD_LABEL} anchor="right" />;
};
