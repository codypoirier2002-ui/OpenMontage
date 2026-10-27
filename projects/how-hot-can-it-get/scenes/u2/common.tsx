// U2 helpers (unit-local; no hooks: pure components fed with frame-derived values).
//   Odometer  a Saira Condensed 700 number whose DIGITS sit in fixed-width cells, so the rolling value never jitters
//             sideways while its digits change (the right end only grows when a digit group is added).
//   HALO      the dark text halo that keeps a black-body-coloured number legible on the bright glow (Forge Black, plain
//             colour + opacity: no blend modes, lesson 24).
//   rollText  the rolling value formatted exactly like the verified rung strings ('~464 °C', '~15,000,000 °C').

import React from "react";
import { FONT } from "../../theme";

/** digit cell width in em (Saira Condensed 700's widest digit '8' is 0.487 em) */
const CELL = 0.5;

export const HALO = [
  "0 0 2px rgba(11,9,7,0.95)",
  "0 0 6px rgba(11,9,7,0.85)",
  "0 3px 14px rgba(11,9,7,0.8)",
  "0 6px 34px rgba(11,9,7,0.7)",
].join(", ");

/** en-US digit grouping without Intl (deterministic in any render browser) */
export const group = (n: number) => {
  const s = String(Math.round(Math.abs(n)));
  let out = "";
  for (let i = 0; i < s.length; i++) {
    if (i > 0 && (s.length - i) % 3 === 0) out += ",";
    out += s[i];
  }
  return out;
};

/** round to 3 significant figures (integers below 1,000 stay whole degrees) */
export const sig3 = (v: number) => {
  if (v < 1000) return Math.round(v);
  const p = Math.pow(10, Math.floor(Math.log10(v)) - 2);
  return Math.round(v / p) * p;
};

/** '~N,NNN °C': the same form as the verified rung strings '~464 °C' / '~15,000,000 °C' */
export const rollText = (degC: number) => `~${group(sig3(Math.max(0, degC)))} °C`;

export const Odometer: React.FC<{ text: string; size: number; color: string; shadow?: string }> = ({ text, size, color, shadow = HALO }) => (
  <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: size, lineHeight: 1, color, whiteSpace: "nowrap", textShadow: shadow }}>
    {[...text].map((ch, i) =>
      /[0-9]/.test(ch) ? (
        <span key={i} style={{ display: "inline-block", width: `${CELL}em`, textAlign: "center" }}>
          {ch}
        </span>
      ) : (
        <React.Fragment key={i}>{ch}</React.Fragment>
      ),
    )}
  </span>
);
