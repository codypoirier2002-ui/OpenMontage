// HowHot - root composition (atelier, 1080x1920 @ 30 fps, duration = props.timeline.total_frames).
// Pattern copied from projects/what-if-earth-stopped-spinning/Composition.tsx (video 12, delivered, QA passed).
//
// Scenes are mounted by ABSOLUTE frame windows (no <Sequence>): inside a scene, useCurrentFrame() is the absolute frame,
// so every trigger is keyed to a word / key frame / the root schedules via useT(). A scene receives { from, to } = its
// boundary and the next scene's, and is mounted from `from - pre` to `to + post` (each scene file exports its own `mount`;
// hand-off contracts in BUILD.md §7). Higher z draws on top.
//
// Layers (THE ROOT OWNS THE BLACK-BODY WORLD): <Forge> (Forge Black + static iron grain) -> <GlowField> (the computed
// black-body light of props.glow, clamped under the tab / slab) -> <WindowView> (the AI plates K1 / S2 / K2 / S4 + the
// false-colour view + the dim) -> <Ladder> (floor, spine, rungs, marks, cursor, '?', chips) -> scenes (picture: U1-U4
// hero labels and drawings, above the window and the rail) -> <Grain> (2.5 %, seed T.driftFrame(T.loopFrame(f))) -> the
// OVERLAY PLANE, bottom to top: the window's AI tags -> scene Overlays -> placard rail -> honesty tab -> captions -> the
// settle CTA. props.layers === "picture" renders the picture layer only. The soundtrack (narration + the ducked bed
// landing on its final C attack + SFX, -14 LUFS) is one premixed file (build_soundtrack.py).

import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, staticFile, useCurrentFrame } from "remotion";
import { Captions } from "./overlay/Captions";
import { HonestyTab } from "./overlay/HonestyTab";
import { PlacardRail, SettleCta } from "./overlay/PlacardRail";
import { SCENES } from "./scenes";
import { Forge, GlowField } from "./shared/GlowField";
import { Grain } from "./shared/Grain";
import { Ladder } from "./shared/Ladder";
import { WindowTags, WindowView } from "./shared/Window";
import { C } from "./theme";
import { TimingProvider } from "./time";
import type { HotProps, SceneId } from "./types";

export const HowHot: React.FC<HotProps> = (props) => {
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
      <AbsoluteFill style={{ backgroundColor: C.forge }}>
        <Forge />
        <GlowField />
        <WindowView />
        <Ladder />
        {live.map((s) => {
          const Scene = SCENES[s.id].Component;
          return (
            <AbsoluteFill key={s.id}>
              <Scene from={s.from} to={s.to} />
            </AbsoluteFill>
          );
        })}
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

export const calculateMetadata: CalculateMetadataFunction<HotProps> = async ({ props }) => ({
  durationInFrames: props.timeline.total_frames,
  fps: props.timeline.fps,
  width: props.timeline.width,
  height: props.timeline.height,
});
