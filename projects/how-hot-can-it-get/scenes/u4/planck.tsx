// U4 unit-local helpers (sc11-sc13). Pure functions of the absolute frame, so sc11 / sc12 / sc13 each mount the SAME
// elements inside their own windows and the 1348 / 1411 seams are pixel-identical (mount.post stays 0).
//   <PlanckSci/>   HERO 2: '1.4 × 10^32 K' (shared <Sci>: the '32' is DRAWN raised and smaller, '^' is never set), Saira
//                  Condensed 700 104 px, stacked under the root's 'Planck temperature' label and the '32 zeros' chip. It
//                  WRITES OUT left -> right from T.sfx.sciWrite (the X7 click of '32 zeros' ON 'zeros'): nothing on
//                  sciWrite - 1, the first glyph ON sciWrite, the reveal edge exactly at the progress point (lesson 22), a
//                  hot band in the glow's lifted colour riding the edge and cooling out by ~sciWrite + 20. Constant after.
//   <ProvenNote/>  'not a proven limit' in the PROBABLY grammar (outline + hatch; the tab turns PROBABLY on 'So'), fully in
//                  ON 'ceiling' (s5): a calm rise ending on the word. Constant after (it stays through the settle).
// Nothing here changes after ~1386, so the settle from 1461 is still (lesson 25). Hooks at the top (lesson 1). No blend
// modes (lesson 24): plain colour + opacity + clip-path only.

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, E, rgba } from "../../theme";
import { prog, useT } from "../../time";
import { lighten } from "../../shared/blackbody";
import { Label, Sci, measure } from "../../shared/Type";

/** the hero number, verbatim from verified_on_screen_strings (build_props.py scans this literal) */
export const SCI_NUM = "1.4 × 10^32 K";
/** the sc12 note, verbatim */
export const NOTE_TEXT = "not a proven limit";

const [MANT, REST] = SCI_NUM.split("^");
const EXP = (REST.match(/^[0-9]+/) ?? [""])[0];
const UNIT = REST.slice(EXP.length);

/** layout (1080x1920): left edge aligned with the rail labels' text (x 226); the number's line box top at y 440, i.e. the
 *  raised '32' tops out ~443 and the caps ~457, clear of the '32 zeros' chip (y ~377-419); baseline ~528 */
export const SCI = { x: 226, top: 440, size: 104, write: 15 } as const;
export const NOTE = { x: 226, y: 600, size: 28 } as const;
const SCI_W = measure(SCI_NUM, "display", SCI.size) + 48; // + the display overhang (lesson 15) + the K's glow-shadow tail

export const PlanckSci: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const start = T.sfx.sciWrite;
  if (frame < start) return null;
  // p = 1/write ON sciWrite (the first glyph), 1 on sciWrite + write - 1; a gentle ease-out (quick first strokes)
  const lin = Math.min(1, (frame - start + 1) / SCI.write);
  const p = 1 - (1 - lin) * (1 - lin); // ease-out quad: exactly 1 at lin = 1
  const edge = p * SCI_W;
  const g = T.glow(frame);
  const hot = lighten(g.rgb, 0.6);
  const hotCss = `rgb(${hot[0]},${hot[1]},${hot[2]})`;
  // the hot band behind the edge cools out over the 8 f after the write completes
  const hotA = 1 - prog(frame, start + SCI.write - 2, start + SCI.write + 6, E.calm);
  const band = 70;
  // the reveal edge in px (continuous every frame; at p = 1 it clears the K and its shadow tail)
  const clip = (x0: number, x1: number) => `inset(-30px ${Math.max(0, SCI_W + 40 - x1)}px -30px ${x0}px)`;
  const box: React.CSSProperties = { position: "absolute", left: SCI.x, top: SCI.top, width: SCI_W + 40, height: SCI.size, lineHeight: 1, whiteSpace: "nowrap" };
  return (
    <>
      <div style={{ ...box, clipPath: clip(-40, edge), textShadow: `0 4px 18px ${rgba(C.forge, 0.75)}, 0 0 28px ${g.css(0.35)}` }}>
        <Sci mantissa={MANT} exp={EXP} unit={UNIT} size={SCI.size} color={C.bone} />
      </div>
      {hotA > 0 ? (
        <div style={{ ...box, clipPath: clip(Math.max(-40, edge - band), edge), opacity: hotA, textShadow: `0 0 14px ${g.css(0.95)}, 0 0 30px ${g.css(0.7)}` }}>
          <Sci mantissa={MANT} exp={EXP} unit={UNIT} size={SCI.size} color={hotCss} />
        </div>
      ) : null}
    </>
  );
};

export const ProvenNote: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const on = T.at("s5", "ceiling");
  const k = prog(frame, on - 6, on, E.drop); // ease-in: still arriving on on - 1, fully in ON 'ceiling' (lesson 22)
  if (k <= 0) return null;
  return <Label x={NOTE.x} y={NOTE.y + 12 * (1 - k)} text={NOTE_TEXT} size={NOTE.size} variant="probably" opacity={k} color={C.bone} />;
};
