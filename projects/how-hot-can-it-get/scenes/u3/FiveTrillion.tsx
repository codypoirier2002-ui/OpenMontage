// sc08 · FiveTrillion · U3. Root: the rail compresses (T.sfx.compress), the window dims to 0.55, the LHC tick + the zeros
// chip '12 zeros' SEAT on T.sfx.lhcSeat (the chip sits just under the rung, x 214-~390, y ~393-435). U3 draws the hero
// rung label INSIDE the dimmed window, stacked under the chip: '> 5,000,000,000,000 K' (Saira Condensed 700, fitted)
// whose digit groups ('> 5' ',000' x4) each FALL and SEAT on T.sfx.lhcGroupSeats[i] (X7 light ticks), then ' K' + the
// description seat on T.sfx.lhcSeat (X7 loud), together with the root tick and chip. Strings come from the props
// (T.rung('lhc').num / .label: verified). Group x positions are fixed from the face metrics (measure) so nothing shifts as
// later groups land. Out by the scene end (the MEASURED tab for the quark claim starts on 'So', lesson 31). Hooks at the top.
import React from "react";
import { useCurrentFrame } from "remotion";
import { lighten } from "../../shared/blackbody";
import { fitSize, measure } from "../../shared/Type";
import { C, FONT, L, rgba } from "../../theme";
import { prog, useT } from "../../time";
import type { Mount, SceneProps } from "../../types";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

const X0 = L.window.x0 + 18; // 238
const MAX_W = L.textRight - X0; // 674
const NUM_Y = 492; // the number's centre line (under the zeros chip, inside the dimmed window)
const DESC_PX = 30;

/** '> 5,000,000,000,000 K' -> ['> 5', ',000', ',000', ',000', ',000', ' K'] (asserted to rejoin to the verified string) */
const splitGroups = (num: string): string[] => {
  const m = num.match(/^([^,]+)((?:,\d{3})+)(\D*)$/);
  if (!m) return [num];
  const parts = [m[1], ...(m[2].match(/,\d{3}/g) ?? []), m[3]].filter((s) => s.length > 0);
  if (parts.join("") !== num) throw new Error("FiveTrillion: digit groups do not rejoin to the verified number");
  return parts;
};

export const FiveTrillion: React.FC<SceneProps> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const T = useT();
  if (frame < from || frame >= to) return null;
  const rung = T.rung("lhc");
  const groups = splitGroups(rung.num);
  const seats = T.sfx.lhcGroupSeats;
  // seat of each group: the first five on the group seats, anything after them (' K') on the LHC seat
  const seatOf = (i: number) => (i < seats.length ? seats[i] : T.sfx.lhcSeat);
  if (frame <= seatOf(0) - 8) return null;
  const size = fitSize(rung.num, "display", 88, MAX_W);
  const out = 1 - prog(frame, to - 8, to);
  const g = T.glow(frame);
  const shade = rgba(C.forge, 0.85);
  const glowShadow = `0 0 22px rgba(${g.rgb[0]},${g.rgb[1]},${g.rgb[2]},0.45)`;
  const numColor = lighten(g.rgb, 0.82);
  const panelA = prog(frame, seatOf(0) - 8, seatOf(0)) * out;
  const descSeat = T.seat(frame, T.sfx.lhcSeat, 8, 14);
  const numW = measure(rung.num, "display", size);
  const descW = measure(rung.label, "mono", DESC_PX);

  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: L.W, height: L.H, opacity: out }}>
      {/* a soft Forge backing so the number reads over the dimmed plate */}
      <div style={{ position: "absolute", left: X0 - 14, top: NUM_Y - size * 0.62, width: Math.max(numW, descW) + 28, height: size * 1.24 + DESC_PX * 1.5 + 18,
        borderRadius: 14, backgroundColor: rgba(C.forge, 0.55), boxShadow: `0 0 36px 14px ${rgba(C.forge, 0.5)}`, opacity: panelA }} />
      {groups.map((txt, i) => {
        const s = T.seat(frame, seatOf(i), 8, 18);
        if (!s.visible) return null;
        const left = X0 + measure(groups.slice(0, i).join(""), "display", size);
        return (
          <div key={i} style={{ position: "absolute", left, top: NUM_Y - size * 0.6 + s.y, fontFamily: FONT.display, fontWeight: 700, fontSize: size, lineHeight: 1.2,
            color: `rgb(${numColor[0]},${numColor[1]},${numColor[2]})`, opacity: s.opacity, whiteSpace: "pre", textShadow: `0 3px 12px ${shade}, ${glowShadow}` }}>
            {txt}
          </div>
        );
      })}
      {descSeat.visible ? (
        <div style={{ position: "absolute", left: X0, top: NUM_Y + size * 0.62 + descSeat.y, fontFamily: FONT.mono, fontWeight: 400, fontSize: DESC_PX, lineHeight: 1.2,
          color: C.bone, opacity: 0.92 * descSeat.opacity, whiteSpace: "nowrap", textShadow: `0 2px 8px ${shade}` }}>
          {rung.label}
        </div>
      ) : null}
    </div>
  );
};
