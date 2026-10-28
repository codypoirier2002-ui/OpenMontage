// ScaleWell - root composition (atelier, 1080x1920 @ 30 fps, duration = props.timeline.total_frames).
// Pattern of projects/how-a-cat-lands/Composition.tsx (video 15, QA passed) + projects/how-hot-can-it-get/Composition.tsx.
//
// Scenes are mounted by ABSOLUTE frame windows (no <Sequence>): inside a scene, useCurrentFrame() is the absolute frame,
// so every trigger is keyed to a word / key frame / the root curves via useT(). A scene receives { from, to } = its
// boundary and the next scene's, and is mounted from `from - pre` to `to + post` (each scene file exports its own `mount`;
// hand-off contracts in BUILD.md §7). Higher z draws on top.
//
// Layers (THE ROOT OWNS THE SCALE WELL): <Sky> (ink darkening downward) -> <Ladder> (the rail, decade powers, the reference
// lines + veil, the rung ticks + label chips, the marker) -> <RootDevices> (the electron bracket, the break, the Planck line,
// the readout) -> scenes (picture: per-scene emphasis) -> <WindowView> (S1 / S2 / S3 / the drawn atom) -> <Counter> (ZEROS)
// -> <Grain> -> the OVERLAY PLANE, bottom to top: the window's tag + the atom note -> scene Overlays -> placard rail ->
// honesty tab -> captions -> the settle CTA.
// props.layers === "picture" renders the picture layer only. The soundtrack (narration + the ducked bed landing on its last
// tonic + SFX) is one premixed file (build_soundtrack.py).

import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, staticFile, useCurrentFrame } from "remotion";
import { Captions } from "./overlay/Captions";
import { HonestyTab } from "./overlay/HonestyTab";
import { PlacardRail, SettleCta } from "./overlay/PlacardRail";
import { SCENES } from "./scenes";
import { Counter } from "./shared/Counter";
import { AtomNote, RootDevices } from "./shared/Devices";
import { Grain } from "./shared/Grain";
import { Ladder } from "./shared/Ladder";
import { Sky } from "./shared/Sky";
import { WindowTags, WindowView } from "./shared/Window";
import { C } from "./theme";
import { TimingProvider } from "./time";
import type { SceneId, ScaleProps } from "./types";

export const ScaleWell: React.FC<ScaleProps> = (props) => {
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
      <AbsoluteFill style={{ backgroundColor: C.skyTop }}>
        <Sky />
        <Ladder />
        <RootDevices />
        {live.map((s) => {
          const Scene = SCENES[s.id].Component;
          return (
            <AbsoluteFill key={s.id}>
              <Scene from={s.from} to={s.to} />
            </AbsoluteFill>
          );
        })}
        <WindowView />
        <Counter />
        <Grain />
        {overlay ? (
          <AbsoluteFill style={{ pointerEvents: "none" }}>
            <WindowTags />
            <AtomNote />
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

export const calculateMetadata: CalculateMetadataFunction<ScaleProps> = async ({ props }) => ({
  durationInFrames: props.timeline.total_frames,
  fps: props.timeline.fps,
  width: props.timeline.width,
  height: props.timeline.height,
});
