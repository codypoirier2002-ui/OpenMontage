// CatLanding - root composition (atelier, 1080x1920 @ 30 fps, duration = props.timeline.total_frames).
// Copied from projects/how-a-mosquito-drinks/Composition.tsx (video 14, QA passed; itself videos 12-13), re-dressed.
//
// Scenes are mounted by ABSOLUTE frame windows (no <Sequence>): inside a scene, useCurrentFrame() is the absolute frame,
// so every trigger is keyed to a word / key frame / the root curves via useT(). A scene receives { from, to } = its
// boundary and the next scene's, and is mounted from `from - pre` to `to + post` (each scene file exports its own `mount`;
// hand-off contracts in BUILD.md §7). Higher z draws on top.
//
// Layers (THE ROOT OWNS THE TEST LAB): <Drape> (slate + static weave + the lab light) -> <RigView> (header 'PROCEDURE:
// LANDING', the steel rail, the release clamp, the floor line) -> scenes (picture: the units' per-scene action - THE CAT via
// <CatLive/>, the dials via <DialsLive/>, the insets, the ledger) -> <WindowView> (S1 / the Marey strip / S2, ONE box left of
// the card) -> <ChecklistCard> (the procedure checklist + ELAPSED clock) -> <Grain> (2 %, seed T.driftFrame(T.loopFrame(f)))
// -> the OVERLAY PLANE, bottom to top: root tags ('drawn · not to scale', the window's ONE tag) -> scene Overlays (stamps,
// labels, chips: above the window and the card) -> placard rail -> honesty tab -> captions -> the settle CTA.
// props.layers === "picture" renders the picture layer only. The soundtrack (narration + the ducked bed landing on its last
// tonic + SFX, -14 LUFS) is one premixed file (build_soundtrack.py).

import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, staticFile, useCurrentFrame } from "remotion";
import { Captions } from "./overlay/Captions";
import { HonestyTab } from "./overlay/HonestyTab";
import { PlacardRail, SettleCta } from "./overlay/PlacardRail";
import { SCENES } from "./scenes";
import { ChecklistCard } from "./shared/Checklist";
import { Drape } from "./shared/Drape";
import { Grain } from "./shared/Grain";
import { DrawnTagLive, RigView } from "./shared/Rig";
import { WindowTags, WindowView } from "./shared/Window";
import { C } from "./theme";
import { TimingProvider } from "./time";
import type { CatProps, SceneId } from "./types";

export const CatLanding: React.FC<CatProps> = (props) => {
  const frame = useCurrentFrame();
  const scenes = props.timeline.scenes;
  const total = props.timeline.total_frames;
  const live = scenes
    .map((s, i) => {
      const id = s.id as SceneId;
      const to = i + 1 < scenes.length ? scenes[i + 1].from : total;
      return { id, from: s.from, to, m: SCENES[id].mount };
    })
    .filter((s) => frame >= s.from - s.m.pre && frame < s.to + s.m.post)
    .sort((a, b) => a.m.z - b.m.z);
  const overlay = props.layers !== "picture";

  return (
    <TimingProvider props={props}>
      <AbsoluteFill style={{ backgroundColor: C.drape }}>
        <Drape />
        <RigView />
        {live.map((s) => {
          const Scene = SCENES[s.id].Component;
          return (
            <AbsoluteFill key={s.id}>
              <Scene from={s.from} to={s.to} />
            </AbsoluteFill>
          );
        })}
        <WindowView />
        <ChecklistCard />
        <Grain />
        {overlay ? (
          <AbsoluteFill style={{ pointerEvents: "none" }}>
            <DrawnTagLive />
            <WindowTags />
            {live.map((s) => {
              const Ov = SCENES[s.id].Overlay;
              return Ov ? <Ov key={`ov-${s.id}`} from={s.from} to={s.to} /> : null;
            })}
            <PlacardRail placards={props.placards} />
            <HonestyTab keys={props.meter} />
            <Captions pages={props.captionPages} ctaFrame={props.cta.frame} />
            <SettleCta pages={props.captionPages} />
          </AbsoluteFill>
        ) : null}
        <Audio src={staticFile(props.audio.soundtrack)} />
      </AbsoluteFill>
    </TimingProvider>
  );
};

export const calculateMetadata: CalculateMetadataFunction<CatProps> = async ({ props }) => ({
  durationInFrames: props.timeline.total_frames,
  fps: props.timeline.fps,
  width: props.timeline.width,
  height: props.timeline.height,
});
