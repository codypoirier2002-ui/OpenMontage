// THE LIGHT IS THE METER (ROOT ONLY: Composition.tsx mounts these once).
//   <Forge/>      the ground: Forge Black #0B0907 + a faint STATIC warm iron grain (3 % luma; seeded feTurbulence, never
//                 animated, so it never shimmers or costs bitrate)
//   <GlowField/>  the whole frame's ambient light = the COMPUTED black-body colour of props.glow.k[f] (shared/blackbody.ts)
//                 at intensity props.glow.i[f]: a broad radial light from above (the unknown 'ceiling') + a faint wash.
//                 i is EXACTLY 0 below the Draper point (sc01-sc04 stay dark: Death Valley and Venus do not glow); the
//                 sc05 sweep runs red -> orange -> yellow-white -> blue-white and then holds (the colour barely changes);
//                 from 'So' (s5) it eases to the low settle intensity, constant through the settle.
//                 Under the honesty tab / caption slab the glow is CLAMPED to ~40 % (a mask gradient y 1150 -> 1236) so
//                 the captions keep their contrast. Banding (lesson 7): a static fine luma dither in the glow's own colour
//                 (plain opacity) + the root Grain; the master also gets the encode-side dither. NO blend modes and no
//                 fading parent (lesson 24): plain colour + opacity only.
// Hooks at the top (lesson 1; useId unconditional).

import React, { useId } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { AMBIENT, C, L } from "../theme";
import { useT } from "../time";
import { lighten } from "./blackbody";
import { cssId } from "./noise";

export const Forge: React.FC = () => {
  const id = cssId(useId(), "iron");
  return (
    <AbsoluteFill style={{ backgroundColor: C.forge }}>
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0 }}>
        <filter id={id} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.05" numOctaves={3} seed={13} result="n" />
          {/* warm iron grain: luminance -> alpha, colour = Iron lifted */}
          <feColorMatrix type="matrix" values="0 0 0 0 0.42  0 0 0 0 0.33  0 0 0 0 0.27  1.2 0 0 0 -0.45" />
        </filter>
        <rect width={L.W} height={L.H} filter={`url(#${id})`} opacity={AMBIENT.iron * 1.6} />
      </svg>
      {/* a faint vignette: the forge is darkest at the edges */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 85% 65% at 50% 42%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.35) 100%)" }} />
    </AbsoluteFill>
  );
};

/** the slab clamp: full glow down to y 1150, ~40 % from the tab's top (1236) down */
const clampMask = (k: number) =>
  `linear-gradient(to bottom, rgba(0,0,0,1) 0px, rgba(0,0,0,1) 1150px, rgba(0,0,0,${k}) ${L.tab.y}px, rgba(0,0,0,${k}) ${L.H}px)`;

export const GlowField: React.FC = () => {
  const frame = useCurrentFrame();
  const T = useT();
  const id = cssId(useId(), "dither");
  const g = T.glow(frame);
  if (g.i <= 0) return null;
  const mask = clampMask(T.glowInfo.slabClamp);
  const c = (a: number) => g.css(Math.max(0, Math.min(1, a * g.i)));
  const lit = lighten(g.rgb, 0.45);
  const core = (a: number) => `rgba(${lit[0]},${lit[1]},${lit[2]},${Math.max(0, Math.min(1, a * g.i))})`;
  return (
    <AbsoluteFill style={{ WebkitMaskImage: mask, maskImage: mask, pointerEvents: "none" }}>
      {/* the light from above (the unknown 'ceiling'): a bright core in the colour lifted toward white (so blue-white
          reads as LIGHT, not as a blue night), falling off into a broad halo; the lower frame stays forge-dark */}
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 95% 46% at 50% 6%, ${core(0.9)} 0%, ${core(0.55)} 22%, ${c(0.28)} 52%, ${c(0.08)} 80%, ${c(0)} 100%)` }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 150% 95% at 50% 18%, ${c(0.24)} 0%, ${c(0.12)} 45%, ${c(0.03)} 80%, ${c(0)} 100%)` }} />
      {/* a faint floor bounce */}
      <AbsoluteFill style={{ background: `linear-gradient(to top, ${c(0.06)} 0%, ${c(0)} 30%)` }} />
      {/* static fine dither in the glow's colour (breaks up 8-bit steps in the big smooth gradient) */}
      <svg width={L.W} height={L.H} style={{ position: "absolute", inset: 0, opacity: AMBIENT.dither * 4 * g.i }}>
        <filter id={id} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={1} seed={7} />
          <feColorMatrix type="matrix" values={`0 0 0 0 ${g.rgb[0] / 255}  0 0 0 0 ${g.rgb[1] / 255}  0 0 0 0 ${g.rgb[2] / 255}  1 0 0 0 -0.35`} />
        </filter>
        <rect width={L.W} height={L.H} filter={`url(#${id})`} />
      </svg>
    </AbsoluteFill>
  );
};
