// THE DIALS (engine; NEW for video 15): two protractor dials, FRONT (amber) and BACK (cyan), whose needles read the SAME
// angle curves as the cat's halves (T.cat(frame).front / .back: one curve per half, the silhouette and the dial share it), and
// the readout 'total spin: 0' (constant: the curves conserve spin by construction, build_props.py asserts it).
// Lesson 33: the dials show DIRECTION and RELATIVE SIZE only - an arc in the half's colour from the start mark to the needle,
// an arrowhead on its end - and NO degree numbers or tick labels.
// Layout L.dials (x 640-920, y 620-860). Visibility per dial from T.dials(frame) (root curves: in on 'each', 'total spin: 0'
// on 'turn', all out before the 'But not always.' page (lesson 42); the FRONT dial returns alone for sc10's short drop).
//   <Dial cx cy r angle color label vis/>   pure svg (inside your <svg>)
//   <DialsLive/>                             the pair + the labels + the readout, live (hooks at the top). Mount it in every
//                                            scene of yours where the dials show (sc05-sc10).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, L, rgba } from "../theme";
import { useT } from "../time";

const rad = (d: number) => (d * Math.PI) / 180;
const pt = (cx: number, cy: number, r: number, a: number) => [cx + r * Math.sin(rad(a)), cy - r * Math.cos(rad(a))];

/** one protractor: start mark at 12 o'clock (= the half's roll 0, upside down); the needle at `angle` (clockwise +) */
export const Dial: React.FC<{ cx: number; cy: number; r: number; angle: number; color: string; vis: number }> = ({ cx, cy, r, angle, color, vis }) => {
  if (vis <= 0) return null;
  const ra = r * 0.78;
  const a = Math.max(-359, Math.min(359, angle));
  const [ex, ey] = pt(cx, cy, ra, a);
  const [sx, sy] = pt(cx, cy, ra, 0);
  const large = Math.abs(a) > 180 ? 1 : 0;
  const sweep = a >= 0 ? 1 : 0;
  const arc = Math.abs(a) > 0.5 ? `M ${sx} ${sy} A ${ra} ${ra} 0 ${large} ${sweep} ${ex} ${ey}` : "";
  const tang = a + (a >= 0 ? 90 : -90); // the arc's travel direction at its end
  const [nx, ny] = pt(cx, cy, r * 0.92, a);
  return (
    <g opacity={vis}>
      <circle cx={cx} cy={cy} r={r} fill={rgba(C.drapeDeep, 0.88)} stroke={C.steel} strokeWidth={3} />
      {Array.from({ length: 24 }, (_, i) => {
        const [x0, y0] = pt(cx, cy, r - 2, i * 15);
        const [x1, y1] = pt(cx, cy, r - (i % 6 === 0 ? 12 : 7), i * 15);
        return <line key={i} x1={x0} y1={y0} x2={x1} y2={y1} stroke={rgba(C.steelEdge, 0.9)} strokeWidth={i % 6 === 0 ? 2.5 : 1.5} />;
      })}
      <line x1={cx} y1={cy - r - 6} x2={cx} y2={cy - r + 14} stroke={C.steelLit} strokeWidth={4} strokeLinecap="round" />
      {arc ? <path d={arc} stroke={color} strokeWidth={7} fill="none" strokeLinecap="round" /> : null}
      {Math.abs(a) > 8 ? (
        <path d={`M ${ex + 11 * Math.sin(rad(tang - 150))} ${ey - 11 * Math.cos(rad(tang - 150))} L ${ex + 4 * Math.sin(rad(tang))} ${ey - 4 * Math.cos(rad(tang))} L ${ex + 11 * Math.sin(rad(tang + 150))} ${ey - 11 * Math.cos(rad(tang + 150))}`}
          stroke={color} strokeWidth={5} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      ) : null}
      <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={C.steelLit} strokeWidth={4} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={6} fill={C.steel} />
    </g>
  );
};

/** FRONT + BACK dials, their labels and 'total spin: 0', live from T.cat / T.dials */
export const DialsLive: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const v = T.dials(frame);
  const pose = T.cat(frame);
  if (v.front <= 0 && v.back <= 0 && v.total <= 0) return null;
  const D = L.dials;
  const lab = (x: number, text: string, color: string, op: number): React.ReactNode =>
    op > 0 ? (
      <div style={{ position: "absolute", left: x, top: D.labelY, transform: "translate(-50%, -50%)", fontFamily: FONT.display, fontWeight: 700, fontSize: 30,
        letterSpacing: 2, color, opacity: op, whiteSpace: "nowrap" }}>{text}</div>
    ) : null;
  return (
    <>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
        <Dial cx={D.frontX} cy={D.cy} r={D.r} angle={pose.front} color={C.front} vis={v.front} />
        <Dial cx={D.backX} cy={D.cy} r={D.r} angle={pose.back} color={C.back} vis={v.back} />
      </svg>
      {lab(D.frontX, T.labels.front, C.front, v.front)}
      {lab(D.backX, T.labels.back, C.back, v.back)}
      {v.total > 0 ? (
        <div style={{ position: "absolute", left: (D.x0 + D.x1) / 2, top: D.readoutY, transform: "translate(-50%, -50%)", padding: "4px 14px", borderRadius: 8,
          backgroundColor: rgba(C.shadow, 0.82), fontFamily: FONT.mono, fontWeight: 500, fontSize: 28, color: C.bone, opacity: v.total, whiteSpace: "nowrap" }}>
          {T.labels.total}
        </div>
      ) : null}
    </>
  );
};
