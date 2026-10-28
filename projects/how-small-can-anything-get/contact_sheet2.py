#!/usr/bin/env python3
"""Contact sheet 2 (foundation layout) -> renders/foundation_sheet.jpg. Run from the repo root AFTER:
    node projects/how-small-can-anything-get/stills.cjs --frames $(python3 projects/how-small-can-anything-get/contact_sheet2.py --frames) --scale 0.5 --out renders/review/foundation/sheet
    node projects/how-small-can-anything-get/stills.cjs --frames $(python3 projects/how-small-can-anything-get/contact_sheet2.py --pic) --scale 0.5 --layers picture --out renders/review/foundation/sheet_pic
Rows 1-2: one stub frame per scene (all layers: the ladder + window + counter + root tags + overlay + stub labels + the
FOUNDATION DEMOS). Row 3: the engine's states on the picture layer (frame 0, the rail drawn, the CHEETAH seat with the
placeholder window, the FALCON chip, the SOUND ring, the YOU jump mid-air, EARTH seated + orbit, PARKER two-line chip, the
beam mid-rail, LIGHT lit, the energy bar, the nines, the settle). Right: the sc05 hero frame with the safe zones drawn, and
the media crops / placeholders (renders/review/crops.jpg). Pattern of video 15's contact_sheet2.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

P = Path("projects/how-small-can-anything-get")
R = P / "renders/review/foundation"
props = json.loads((P / "artifacts/props.json").read_text())
scenes = props["timeline"]["scenes"]
FR = [s["from"] + int(s["durationInFrames"] * (0.62 if s["id"] != "sc12" else 0.92)) for s in scenes]
K = props["audio"]
T_ = props["timeline"]["total_frames"]
PIC = [0, K["railDraw"] + 12, K["cheetahSeat"] + 6, K["falconSeat"] + 6, K["soundSeat"] + 8, (K["jumpStart"] + K["earthSeat"]) // 2, K["orbitIn"] + 20,
       K["parkerSeat"] + 6, K["beamStart"] + 7, K["lightSeat"] + 12, K["barTicks"][4], K["digitTicks"][-1] + 2, T_ - 1]
PIC_LABEL = ["f0: dim rail, marker at WALK", "rail drawn + WALK chip", "CHEETAH seated + window", "FALCON chip + cited", "SOUND ring (X2)", "YOU jump mid-air",
             "EARTH seated + orbit inset", "PARKER two-line chip", "beam mid-rail", "LIGHT lit, c red, 9", "ENERGY bar + curve", "nines landed", "settle (last frame)"]
TW, TH = 216, 384
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
except OSError:
    font = big = ImageFont.load_default()


def scene_of(f: int) -> str:
    return next(s["id"] for s in scenes if s["from"] <= f < s["from"] + s["durationInFrames"])


def main() -> None:
    if "--frames" in sys.argv:
        print(",".join(map(str, FR)))
        return
    if "--pic" in sys.argv:
        print(",".join(map(str, PIC)))
        return
    ncol = max(7, len(PIC))
    crops = Image.open(P / "renders/review/crops.jpg").convert("RGB")
    ck = 540 / crops.size[0]
    crops = crops.resize((540, int(crops.size[1] * ck)), Image.LANCZOS)
    W = ncol * (TW + 8) + 8 + 560 + 16
    H = max(60 + 3 * (TH + 34) + 40, 60 + 964 + 30 + crops.size[1] + 30)
    out = Image.new("RGB", (W, H), (28, 36, 42))
    d = ImageDraw.Draw(out)
    d.text((8, 8), f"How Fast Can Anything Go? - contact sheet 2: foundation layout (stub scenes, the speed ladder, the window (placeholders), counter, overlay). {T_} f / {T_ / 30:.2f} s.",
           fill=(240, 236, 228), font=big)
    d.text((8, 34), "Rows 1-2: one frame per scene (all layers; dashed card = temporary stub label; FOUNDATION DEMOS in sc01, sc04, sc05 (hero), sc06-sc12). Row 3: picture layer only, the engine's states.",
           fill=(180, 190, 186), font=font)
    for i, f in enumerate(FR):
        x = 8 + (i % 6) * (TW + 8)
        y = 60 + (i // 6) * (TH + 34)
        out.paste(Image.open(R / f"sheet/f{f:04d}.png").convert("RGB").resize((TW, TH), Image.LANCZOS), (x, y))
        d.text((x, y + TH + 4), f"{scene_of(f)} f{f}", fill=(220, 225, 215), font=font)
    for i, f in enumerate(PIC):
        x = 8 + i * (TW + 8)
        y = 60 + 2 * (TH + 34)
        out.paste(Image.open(R / f"sheet_pic/f{f:04d}.png").convert("RGB").resize((TW, TH), Image.LANCZOS), (x, y))
        d.text((x, y + TH + 4), f"f{f}", fill=(160, 220, 230), font=font)
        d.text((x, y + TH + 18), PIC_LABEL[i][:28], fill=(160, 220, 230), font=font)
    f5 = FR[4]
    big_im = Image.open(R / f"sheet/f{f5:04d}.png").convert("RGB").resize((540, 960), Image.LANCZOS)
    z = ImageDraw.Draw(big_im, "RGBA")
    s = 0.5

    def rect(x0, y0, x1, y1, col, label, fill=None):
        z.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=col, width=2, fill=fill)
        z.text((x0 * s + 4, y0 * s + 2), label, fill=col, font=font)
    rect(0, 0, 1080, 192, (255, 80, 80), "top UI: no content", (255, 80, 80, 40))
    rect(0, 1574, 1080, 1920, (255, 80, 80), "bottom UI y>=1574: no text", (255, 80, 80, 40))
    rect(929, 192, 1080, 1574, (255, 80, 80), "x>=929", (255, 80, 80, 40))
    rect(180, 380, 320, 1080, (120, 220, 120), "RAIL")
    rect(280, 360, 572, 1080, (120, 220, 120), "rung chips")
    rect(580, 440, 920, 893, (240, 236, 228), "WINDOW / orbit / readout")
    rect(640, 220, 920, 340, (232, 163, 61), "COUNTER")
    rect(140, 1124, 912, 1204, (230, 230, 120), "placard rail")
    rect(140, 1236, 628, 1290, (230, 230, 120), "tab")
    rect(140, 1296, 940, 1488, (230, 230, 120), "caption slab")
    xr = 8 + ncol * (TW + 8) + 8
    out.paste(big_im, (xr, 60))
    d.text((xr, 60 + 964), f"f{f5} ({scene_of(f5)}, hero) with the safe zones", fill=(220, 225, 215), font=font)
    out.paste(crops, (xr, 60 + 964 + 26))
    d.text((xr, 60 + 964 + 30 + crops.size[1]), "S1 / S2 / S3: PLACEHOLDER cards until the stills land (prepare_media.py)", fill=(220, 225, 215), font=font)
    (P / "renders").mkdir(exist_ok=True)
    out.save(P / "renders/foundation_sheet.jpg", quality=86)
    print("wrote", P / "renders/foundation_sheet.jpg", out.size)


if __name__ == "__main__":
    main()
