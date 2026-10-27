// TEMPORARY stub label (foundation stage): every stub scene shows a labelled card in the TOP UI band (y 14-...) on the
// OVERLAY plane with its id, unit, frames and subject. Builders delete the <StubLabel> from their scenes; delete this file
// when the last stub is gone. Hooks at the top (lesson 1).

import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, rgba } from "../theme";
import type { SceneId } from "../types";

export const INFO: Record<SceneId, { name: string; unit: string; subject: string }> = {
  sc01: { name: "Walk", unit: "U1", subject: "root: the dim rail + the marker at WALK from f0, the rail DRAWS on 'You' (railDraw, X1), the WALK chip SEATS on 'walk'. U1 demo: a walker icon beside the WALK rung." },
  sc02: { name: "Cheetah", unit: "U1", subject: "root: the window opens ON windowOpen1 (S1 placeholder until the still lands; 'AI impression'); the marker climbs from climbCheetah (X1) and the CHEETAH chip seats on cheetahSeat; counter 0->2 (X3 x2). U1: emphasis only (the plate is root)." },
  sc03: { name: "Falcon", unit: "U1", subject: "root: S1 -> S2 crossfade from plateSwap (hard tag swap at the midpoint); climb from climbFalcon (X1), FALCON chip + hatched 'commonly cited' on falconSeat (PROBABLY tab); window closes windowClose1. U1: emphasis only." },
  sc04: { name: "Sound", unit: "U1", subject: "root: window closed; climb from climbSound (X1), SOUND chip ON soundSeat (X2 thump); counter 3. U1: <PressureRing from={T.sfx.soundSeat}/> (the demo) - one soft ring from the marker." },
  sc05: { name: "YouAreFast", unit: "U1", subject: "HERO. root: the YOU tag seats at WALK on youSeat, JUMPS with the marker from jumpStart (X1 big) to EARTH on earthSeat (chip seats, counter 4->5 X3 x2). U1: <OrbitInset/> (drawn Sun / Earth / arrow + 'drawn · not to scale', alpha from orbitIn, gone before the PROBE page) + your emphasis on the jump." },
  sc06: { name: "Parker", unit: "U1", subject: "root: window opens ON windowOpen2 (S3 placeholder; X4 soft hum); marker holds at EARTH, the YOU tag stays there. U1 Overlay: the label 'Parker Solar Probe · NASA' on the plate from probeLabel (the demo uses T.labels.probe)." },
  sc07: { name: "Falling", unit: "U2", subject: "root: climb from climbParker (X1), PARKER chip (two lines) ON parkerSeat; the window (S3) stays open and closes windowClose2. U2 Overlay: an SVG <Arrow> on the plate pointing toward the Sun + the label 'falling toward the Sun' from fallArrow (the demo uses T.labels.falling)." },
  sc08: { name: "Light", unit: "U2", subject: "root: window closed; the LIGHT chip seats ON lightSeat, the 'c' line lights red (cLit), counter 5->9 (X3 x4). U2: <LightBeamLive/> (the beam races the rail beamStart -> lightSeat; X5 shimmer; fades after) - keep it mounted in sc09 too." },
  sc09: { name: "Wall", unit: "U2", subject: "root: the marker leaves PARKER on wallStart and climbs toward 'c', slowing (no SFX). U2: <LightBeamLive/> (its fade-out tail) + <MassLabelLive/> ('anything with mass', fixed chip + leader to the marker; gone before the LHC page)." },
  sc10: { name: "Energy", unit: "U2", subject: "root: the marker inches up (asymptotic creep). U2: <MassLabelLive/> + <EnergyLive/> ('ENERGY NEEDED' bar growing from barStart, OFF the top ON barOff (X3 accelerating ticks), the drawn gamma curve 'speed' / 'energy' + 'drawn · not to scale'; everything gone before the LHC page)." },
  sc11: { name: "LHC", unit: "U2", subject: "HERO 2. root: the marker creeps to its final stop ON creepEnd and the gap bracket 'the gap' appears (X6 tink). U2: <NinesReadoutLive/> (card seats ON readoutSeat; '99.9999991 %' lands one glyph per digitTick, X3 x10) - keep it mounted in sc12." },
  sc12: { name: "NeverAllTheWay", unit: "U2", subject: "NO SFX from closingStart. root: the full ladder, the marker just under 'c', the gap bracket, the YOU tag at EARTH, the counter at 9; release wayEndFrame, chord chordFrame, CTA ctaFrame, tab IDLE. U2: <NinesReadoutLive/> constant; NOTHING may change after wayEndFrame." },
};

export const StubLabel: React.FC<{ id: SceneId; from: number; to: number }> = ({ id, from, to }) => {
  const frame = useCurrentFrame();
  const i = INFO[id];
  if (frame < from || frame >= to) return null;
  const row: React.CSSProperties = { fontFamily: FONT.mono, fontWeight: 400, fontSize: 17, color: C.bone, lineHeight: 1.22 };
  return (
    <div style={{ position: "absolute", left: 40, top: 14, width: 1000, padding: "6px 16px", boxSizing: "border-box", backgroundColor: rgba(C.nightInk, 0.9), border: `2px dashed ${C.steel}`, borderRadius: 4 }}>
      <div style={{ fontFamily: FONT.mono, fontWeight: 500, fontSize: 17, letterSpacing: "0.04em", color: C.steel }}>
        STUB · {id} · {i.unit} · f {from}–{to} · {to - from} f · {((to - from) / 30).toFixed(2)} s
      </div>
      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 26, color: C.bone, lineHeight: 1.15 }}>{i.name}</div>
      <div style={row}>{i.subject}</div>
    </div>
  );
};
