// TEMPORARY stub label (foundation stage): every stub scene shows a labelled card in the TOP UI band (y 18-...) on the
// OVERLAY plane with its id, unit, frames and subject. Builders delete the <StubLabel> from their scenes; delete this file
// when the last stub is gone. Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, rgba } from "../theme";
import type { SceneId } from "../types";

export const INFO: Record<SceneId, { name: string; unit: string; subject: string }> = {
  sc01: { name: "FloorLine", unit: "U1", subject: "root: forge dark, ember bed, ice floor hairline on 'floor', '0 K = -273.15 °C' SEATED floorLabelSeat (X7). U1: optional cold accents only (no glow)" },
  sc02: { name: "CeilingQuestion", unit: "U1", subject: "root: camera tilt (floor slides down 40 px), filament '?' on qStart (X3), dashed spine from spineStart. U1: optional 'looking up' accents" },
  sc03: { name: "DeathValley", unit: "U1", subject: "root: window opens on K1 (forward) + 'AI impression', false colour on lutOn; DV tick SEATED dvSeat (X7). U1: hero label '56.7 °C' + 'Death Valley · 1913 · air' on dvSeat" },
  sc04: { name: "Venus", unit: "U1", subject: "root: window -> S2 + 'AI impression · not a photo'; Venus tick SEATED venusSeat (X7); Draper mark on draperMark. U1: '~464 °C' + 'Venus surface'; drawn lead ingot slumps on leadMelt + 'lead melts at 327 °C · drawn'" },
  sc05: { name: "GlowSweep", unit: "U2", subject: "HERO 1 root: window closes; glow sweeps 737 K -> 15e6 degC sweepStart -> sunCoreSeat (X4 crest + X7); cursor + marks + 'black-body colour' chip. U2: the rolling number (T.glow(f).k) -> '~15,000,000 °C' + \"Sun's core\"" },
  sc06: { name: "Reactor", unit: "U2", subject: "root: window opens on K2 (forward, then held) + 'AI illustration'; KSTAR tick SEATED kstarSeat (X7). U2: '100,000,000 °C' + 'KSTAR · Korea · 48 s · 2024'; 48-second timer arc from timerArc" },
  sc07: { name: "Collider", unit: "U3", subject: "root: window -> S4 + 'AI illustration'. U3: two drawn beam lines converge, FLASH ON beamFlash (X6) + tag 'drawn'" },
  sc08: { name: "FiveTrillion", unit: "U3", subject: "root: rail compresses (compress), window dims 0.55, zeros chip '12 zeros' SEATED lhcSeat. U3: '> 5,000,000,000,000 K' digit groups SEAT on lhcGroupSeats (X7 x5), ' K' + 'LHC · CERN · 2012 · record estimate' on lhcSeat (X7 loud)" },
  sc09: { name: "QuarkSoup", unit: "U3", subject: "root: window dims 0.8 (soupStart), X2 hiss. U3: drawn proton (3 quarks in a glowing bag) melts on protonMelt into a quark soup inside the window; 'drawn · illustrative', 'quark-gluon plasma'" },
  sc10: { name: "PlanckTemperature", unit: "U4", subject: "root: window closes, camera drifts to the Planck view (drift), Planck tick + 'Planck temperature' on planckMark (X3), '?' dims to half, all compact rung numbers show. U4: optional" },
  sc11: { name: "ThirtyTwoZeros", unit: "U4", subject: "HERO 2 root: zeros chip counts 12 -> 32 on zeroTicks (X7 x20); rail frays on fray + 'where known physics stops working'. U4: '1.4 × 10^32 K' (Sci, raised '32') writes out from sciWrite on the Planck mark" },
  sc12: { name: "NoCeiling", unit: "U4", subject: "NO SFX. root: '?' fades out from qFade; glow eases to settle from closingStart. U4: note 'not a proven limit' (on 'ceiling')" },
  sc13: { name: "EdgeOfKnowing", unit: "U4", subject: "NO SFX. root: the whole ladder floor -> Planck in the low blue-white glow; release knowEndFrame, chord chordFrame, CTA ctaFrame; tab IDLE. U4: nothing may change after knowEndFrame" },
};

export const StubLabel: React.FC<{ id: SceneId; from: number; to: number }> = ({ id, from, to }) => {
  const frame = useCurrentFrame();
  const i = INFO[id];
  if (frame < from || frame >= to) return null;
  const row: React.CSSProperties = { fontFamily: FONT.mono, fontWeight: 400, fontSize: 17, color: C.bone, lineHeight: 1.22 };
  return (
    <div style={{ position: "absolute", left: 40, top: 14, width: 1000, padding: "6px 16px", boxSizing: "border-box", backgroundColor: rgba(C.nightInk, 0.9), border: `2px dashed ${C.filament}`, borderRadius: 4 }}>
      <div style={{ fontFamily: FONT.mono, fontWeight: 500, fontSize: 17, letterSpacing: "0.04em", color: C.filament }}>
        STUB · {id} · {i.unit} · f {from}–{to} · {to - from} f · {((to - from) / 30).toFixed(2)} s
      </div>
      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 26, color: C.bone, lineHeight: 1.15 }}>{i.name}</div>
      <div style={row}>{i.subject}</div>
    </div>
  );
};
