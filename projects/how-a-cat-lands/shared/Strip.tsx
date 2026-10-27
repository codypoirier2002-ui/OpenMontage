// THE MAREY FILM STRIP (engine; NEW for video 15; ROOT-drawn inside the window by shared/Window.tsx for plate A1): the cells
// of the 1894 engraving's top strip (prepare_media.py: cells 3-10, the experimenter's hands cropped out) stacked in a
// vertical film strip with sprocket holes drawn in code; `step` = the cell at the window top (float: eased moves between
// integers, props.window plate A1 step[f]). The cells are archival (tagged 'engraving after É.-J. Marey, 1894' by the root);
// nothing drawn over them. Pure (no hooks).

import React from "react";
import { Img, staticFile } from "remotion";
import { C, rgba } from "../theme";

export const STRIP = { margin: 46, gap: 22, top: 26 } as const;

export const MareyStrip: React.FC<{ cells: string[]; step: number; w: number; h: number }> = ({ cells, step, w, h }) => {
  const cw = w - 2 * STRIP.margin;
  const ch = Math.round(cw * (406 / 325));
  const pitch = ch + STRIP.gap;
  const y0 = STRIP.top - step * pitch;
  const holes = Math.ceil((cells.length * pitch + h) / 34) + 2;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: w, height: h, backgroundColor: "#141618", overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 0, top: y0 - 40, width: w, height: cells.length * pitch + 80 }}>
        {Array.from({ length: holes }, (_, i) => (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: 14, top: i * 34 + 8, width: 18, height: 14, borderRadius: 3, backgroundColor: rgba(C.steelLit, 0.16) }} />
            <div style={{ position: "absolute", right: 14, top: i * 34 + 8, width: 18, height: 14, borderRadius: 3, backgroundColor: rgba(C.steelLit, 0.16) }} />
          </React.Fragment>
        ))}
        {cells.map((c, i) => (
          <div key={c} style={{ position: "absolute", left: STRIP.margin, top: 40 + i * pitch, width: cw, height: ch, overflow: "hidden", borderRadius: 4,
            boxShadow: `0 0 0 2px ${rgba(C.steelEdge, 0.35)}` }}>
            <Img src={staticFile(c)} style={{ width: cw, height: ch }} />
          </div>
        ))}
      </div>
    </div>
  );
};
