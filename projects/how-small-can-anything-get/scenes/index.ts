// Scene registry: id -> { Component, mount, Overlay? }. Each scene file owns its own `mount` and may export an `Overlay`.
import type React from "react";
import type { Mount, SceneId, SceneProps } from "../types";
import * as sc01 from "./u1/Sand";
import * as sc02 from "./u1/Hair";
import * as sc03 from "./u1/Eye";
import * as sc04 from "./u1/Cell";
import * as sc05 from "./u1/Virus";
import * as sc06 from "./u1/Atom";
import * as sc07 from "./u2/Proton";
import * as sc08 from "./u2/Electron";
import * as sc09 from "./u2/Planck";
import * as sc10 from "./u2/Readout";
import * as sc11 from "./u2/Floor";
import * as sc12 from "./u2/NoFloor";

type SceneModule = { mount: Mount; Overlay?: React.FC<SceneProps> };
const ov = (m: object): React.FC<SceneProps> | undefined => (m as SceneModule).Overlay;

export const SCENES: Record<SceneId, { Component: React.FC<SceneProps>; mount: Mount; Overlay?: React.FC<SceneProps> }> = {
  sc01: { Component: sc01.Sand, mount: sc01.mount, Overlay: ov(sc01) },
  sc02: { Component: sc02.Hair, mount: sc02.mount, Overlay: ov(sc02) },
  sc03: { Component: sc03.Eye, mount: sc03.mount, Overlay: ov(sc03) },
  sc04: { Component: sc04.Cell, mount: sc04.mount, Overlay: ov(sc04) },
  sc05: { Component: sc05.Virus, mount: sc05.mount, Overlay: ov(sc05) },
  sc06: { Component: sc06.Atom, mount: sc06.mount, Overlay: ov(sc06) },
  sc07: { Component: sc07.Proton, mount: sc07.mount, Overlay: ov(sc07) },
  sc08: { Component: sc08.Electron, mount: sc08.mount, Overlay: ov(sc08) },
  sc09: { Component: sc09.Planck, mount: sc09.mount, Overlay: ov(sc09) },
  sc10: { Component: sc10.Readout, mount: sc10.mount, Overlay: ov(sc10) },
  sc11: { Component: sc11.Floor, mount: sc11.mount, Overlay: ov(sc11) },
  sc12: { Component: sc12.NoFloor, mount: sc12.mount, Overlay: ov(sc12) },
};
