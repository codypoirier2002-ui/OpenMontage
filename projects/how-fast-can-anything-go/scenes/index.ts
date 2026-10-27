// Scene registry: id -> { Component, mount, Overlay? }. Each scene file (in its unit's folder scenes/uN/) owns its own
// `mount` and may export an `Overlay` (labels, tags on the overlay plane). Builders edit ONLY their own scenes/uN/
// (BUILD.md §7); this file and the root are foundation-owned.
import type React from "react";
import type { Mount, SceneId, SceneProps } from "../types";
import * as sc01 from "./u1/Walk";
import * as sc02 from "./u1/Cheetah";
import * as sc03 from "./u1/Falcon";
import * as sc04 from "./u1/Sound";
import * as sc05 from "./u1/YouAreFast";
import * as sc06 from "./u1/Parker";
import * as sc07 from "./u2/Falling";
import * as sc08 from "./u2/Light";
import * as sc09 from "./u2/Wall";
import * as sc10 from "./u2/Energy";
import * as sc11 from "./u2/LHC";
import * as sc12 from "./u2/NeverAllTheWay";

type SceneModule = { mount: Mount; Overlay?: React.FC<SceneProps> };
const ov = (m: object): React.FC<SceneProps> | undefined => (m as SceneModule).Overlay;

export const SCENES: Record<SceneId, { Component: React.FC<SceneProps>; mount: Mount; Overlay?: React.FC<SceneProps> }> = {
  sc01: { Component: sc01.Walk, mount: sc01.mount, Overlay: ov(sc01) },
  sc02: { Component: sc02.Cheetah, mount: sc02.mount, Overlay: ov(sc02) },
  sc03: { Component: sc03.Falcon, mount: sc03.mount, Overlay: ov(sc03) },
  sc04: { Component: sc04.Sound, mount: sc04.mount, Overlay: ov(sc04) },
  sc05: { Component: sc05.YouAreFast, mount: sc05.mount, Overlay: ov(sc05) },
  sc06: { Component: sc06.Parker, mount: sc06.mount, Overlay: ov(sc06) },
  sc07: { Component: sc07.Falling, mount: sc07.mount, Overlay: ov(sc07) },
  sc08: { Component: sc08.Light, mount: sc08.mount, Overlay: ov(sc08) },
  sc09: { Component: sc09.Wall, mount: sc09.mount, Overlay: ov(sc09) },
  sc10: { Component: sc10.Energy, mount: sc10.mount, Overlay: ov(sc10) },
  sc11: { Component: sc11.LHC, mount: sc11.mount, Overlay: ov(sc11) },
  sc12: { Component: sc12.NeverAllTheWay, mount: sc12.mount, Overlay: ov(sc12) },
};
