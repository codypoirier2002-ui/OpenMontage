// Scene registry: id -> { Component, mount, Overlay? }. Each scene file (in its unit's folder scenes/uN/) owns its own
// `mount` and may export an `Overlay` (labels, tags on the overlay plane). Builders edit ONLY their own scenes/uN/
// (BUILD.md §7); this file and the root are foundation-owned.
import type React from "react";
import type { Mount, SceneId, SceneProps } from "../types";
import * as sc01 from "./u1/FloorLine";
import * as sc02 from "./u1/CeilingQuestion";
import * as sc03 from "./u1/DeathValley";
import * as sc04 from "./u1/Venus";
import * as sc05 from "./u2/GlowSweep";
import * as sc06 from "./u2/Reactor";
import * as sc07 from "./u3/Collider";
import * as sc08 from "./u3/FiveTrillion";
import * as sc09 from "./u3/QuarkSoup";
import * as sc10 from "./u4/PlanckTemperature";
import * as sc11 from "./u4/ThirtyTwoZeros";
import * as sc12 from "./u4/NoCeiling";
import * as sc13 from "./u4/EdgeOfKnowing";

type SceneModule = { mount: Mount; Overlay?: React.FC<SceneProps> };
const ov = (m: object): React.FC<SceneProps> | undefined => (m as SceneModule).Overlay;

export const SCENES: Record<SceneId, { Component: React.FC<SceneProps>; mount: Mount; Overlay?: React.FC<SceneProps> }> = {
  sc01: { Component: sc01.FloorLine, mount: sc01.mount, Overlay: ov(sc01) },
  sc02: { Component: sc02.CeilingQuestion, mount: sc02.mount, Overlay: ov(sc02) },
  sc03: { Component: sc03.DeathValley, mount: sc03.mount, Overlay: ov(sc03) },
  sc04: { Component: sc04.Venus, mount: sc04.mount, Overlay: ov(sc04) },
  sc05: { Component: sc05.GlowSweep, mount: sc05.mount, Overlay: ov(sc05) },
  sc06: { Component: sc06.Reactor, mount: sc06.mount, Overlay: ov(sc06) },
  sc07: { Component: sc07.Collider, mount: sc07.mount, Overlay: ov(sc07) },
  sc08: { Component: sc08.FiveTrillion, mount: sc08.mount, Overlay: ov(sc08) },
  sc09: { Component: sc09.QuarkSoup, mount: sc09.mount, Overlay: ov(sc09) },
  sc10: { Component: sc10.PlanckTemperature, mount: sc10.mount, Overlay: ov(sc10) },
  sc11: { Component: sc11.ThirtyTwoZeros, mount: sc11.mount, Overlay: ov(sc11) },
  sc12: { Component: sc12.NoCeiling, mount: sc12.mount, Overlay: ov(sc12) },
  sc13: { Component: sc13.EdgeOfKnowing, mount: sc13.mount, Overlay: ov(sc13) },
};
