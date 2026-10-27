// sc10 · NotAlways (U2, BUILD.md §7): 'NOT ALWAYS' seated ON stampNotAlways (X3, overlay); short-drop ghost (curves) + 'short drop: no time to turn' (PROBABLY).
// The whole unit's action is ONE continuous stage (Stage.tsx), mounted by whichever U2 scene owns the frame, so the unit-internal
// seams match by construction. Hooks: none here (Stage.tsx has them at the top).

import React from "react";
import type { Mount, SceneProps } from "../../types";
import { U2Overlay, U2Picture } from "./Stage";

export const mount: Mount = { pre: 0, post: 0, z: 1 };

export const NotAlways: React.FC<SceneProps> = () => <U2Picture />;

export const Overlay: React.FC<SceneProps> = () => <U2Overlay />;
