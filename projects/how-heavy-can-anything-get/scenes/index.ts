// Scene registry: id -> { Component, mount, Overlay? }. Each scene file owns its own `mount` and may export an `Overlay`.
import type React from "react";
import type { Mount, SceneId, SceneProps } from "../types";
import * as sc01 from "./u1/You";
import * as sc02 from "./u1/Whale";
import * as sc03 from "./u1/Eiffel";
import * as sc04 from "./u1/Humans";
import * as sc05 from "./u1/Earth";
import * as sc06 from "./u1/Sun";
import * as sc07 from "./u2/Neutron";
import * as sc08 from "./u2/SgrA";
import * as sc09 from "./u2/Mercury";
import * as sc10 from "./u2/Universe";
import * as sc11 from "./u2/DarkMatter";
import * as sc12 from "./u2/Settle";

type SceneModule = { mount: Mount; Overlay?: React.FC<SceneProps> };
const ov = (m: object): React.FC<SceneProps> | undefined => (m as SceneModule).Overlay;

export const SCENES: Record<SceneId, { Component: React.FC<SceneProps>; mount: Mount; Overlay?: React.FC<SceneProps> }> = {
  sc01: { Component: sc01.You, mount: sc01.mount, Overlay: ov(sc01) },
  sc02: { Component: sc02.Whale, mount: sc02.mount, Overlay: ov(sc02) },
  sc03: { Component: sc03.Eiffel, mount: sc03.mount, Overlay: ov(sc03) },
  sc04: { Component: sc04.Humans, mount: sc04.mount, Overlay: ov(sc04) },
  sc05: { Component: sc05.Earth, mount: sc05.mount, Overlay: ov(sc05) },
  sc06: { Component: sc06.Sun, mount: sc06.mount, Overlay: ov(sc06) },
  sc07: { Component: sc07.Neutron, mount: sc07.mount, Overlay: ov(sc07) },
  sc08: { Component: sc08.SgrA, mount: sc08.mount, Overlay: ov(sc08) },
  sc09: { Component: sc09.Mercury, mount: sc09.mount, Overlay: ov(sc09) },
  sc10: { Component: sc10.Universe, mount: sc10.mount, Overlay: ov(sc10) },
  sc11: { Component: sc11.DarkMatter, mount: sc11.mount, Overlay: ov(sc11) },
  sc12: { Component: sc12.Settle, mount: sc12.mount, Overlay: ov(sc12) },
};
