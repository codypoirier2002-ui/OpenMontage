// ScaleWell - root composition (atelier, 1080x1920 @ 30 fps, duration = props.timeline.total_frames).
// Pattern of projects/how-a-cat-lands/Composition.tsx (video 15, QA passed) + projects/how-hot-can-it-get/Composition.tsx.
//
// Scenes are mounted by ABSOLUTE frame windows (no <Sequence>): inside a scene, useCurrentFrame() is the absolute frame,
// so every trigger is keyed to a word / key frame / the root curves via useT(). A scene receives { from, to } = its
// boundary and the next scene's, and is mounted from `from - pre` to `to + post` (each scene file exports its own `mount`;
// hand-off contracts in BUILD.md §7). Higher z draws on top.
//
// Layers (THE ROOT OWNS THE SPEED LADDER): <Sky> (night ink + star dust) -> <Ladder> (the rail, decade ticks, the red 'c'
// line, the rung ticks + label chips, the marker + streaks, the gap bracket) -> <YouTagLive> (the YOU tag, root: it must
// persist sc05 -> sc12 across both units) -> scenes (picture: the units' per-scene action
// and the DEVICES from shared/Devices.tsx, above the rail) -> <WindowView> (S1 / S2 / S3, ONE box right of the rung labels)
// -> <Counter> (ZEROS) -> <Grain> (2 %, seed T.driftFrame(T.loopFrame(f))) -> the OVERLAY PLANE, bottom to top: the window's
// AI tag -> scene Overlays (labels, tags) -> placard rail -> honesty tab -> captions -> the settle CTA.
// props.layers === "picture" renders the picture layer only. The soundtrack (narration + the ducked bed landing on its last
// tonic + SFX, -14 LUFS; voice + SFX only until the bed lands) is one premixed file (build_soundtrack.py).

import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, staticFile, useCurrentFrame } from "remotion";
import { Captions } from "./overlay/Captions";
import { HonestyTab } from "./overlay/HonestyTab";
import { PlacardRail, SettleCta } from "./overlay/PlacardRail";
import { SCENES } from "./scenes";
import { Counter } from "./shared/Counter";
import { YouTagLive } from "./shared/Devices";
import { Grain } from "./shared/Grain";
import { Ladder } from "./shared/Ladder";
import { Sky } from "./shared/Sky";
import { WindowTags, WindowView } from "./shared/Window";
import { C } from "./theme";
import { TimingProvider } from "./time";
import type { SceneId, SpeedProps } from "./types";

export const ScaleWell: React.FC<SpeedProps> = (props) => {
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
        <YouTagLive />
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

export const calculateMetadata: CalculateMetadataFunction<SpeedProps> = async ({ props }) => ({
  durationInFrames: props.timeline.total_frames,
  fps: props.timeline.fps,
  width: props.timeline.width,
  height: props.timeline.height,
});
