#!/usr/bin/env python3
"""Contact sheet 2 (foundation layout) -> renders/foundation_sheet.jpg. Run from the repo root AFTER:
    node projects/how-a-cat-lands/stills.cjs --frames $(python3 projects/how-a-cat-lands/contact_sheet2.py --frames) --scale 0.5 --out renders/review/foundation/sheet
    node projects/how-a-cat-lands/stills.cjs --frames $(python3 projects/how-a-cat-lands/contact_sheet2.py --pic) --scale 0.5 --layers picture --out renders/review/foundation/sheet_pic
Rows 1-2: one stub frame per scene (all layers: the test lab + window + root tags + overlay + stub labels + the FOUNDATION
DEMOS). Row 3: the engine's states on the picture layer (the hanging cat, the preview flip, S1, the Marey strip, the bend,
the hero turn mid / end, the swap done, the paws' contact frame, S2, the short-drop ghost, the ledger, the settle). Right: an
sc06 frame with the safe zones drawn, and the media crops (renders/review/crops.jpg). Pattern of video 14's contact_sheet2.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

P = Path("projects/how-a-cat-lands")
R = P / "renders/review/foundation"
props = json.loads((P / "artifacts/props.json").read_text())
scenes = props["timeline"]["scenes"]
FR = [s["from"] + int(s["durationInFrames"] * (0.62 if s["id"] != "sc12" else 0.92)) for s in scenes]
K = props["audio"]
T_ = props["timeline"]["total_frames"]
PIC = [0, K["clampOpen"] + 22, K["windowOpen1"] + 20, K["stripSteps"][2] + 2, K["bendSeat"], (K["turnStart"] + K["turnEnd"]) // 2, K["turnEnd"],
       K["swapEnd"], K["land"], K["windowOpen2"] + 10, K["shortTurn"] + 16, K["bracket"] + 10, T_ - 1]
PIC_LABEL = ["f0: hanging, clamp shut", "preview flip (front)", "S1 window", "Marey strip", "bend seated + axes", "HERO mid-turn",
             "HERO end (front ~200, back -20)", "swap done: both feet down", "paws ON the floor (X6)", "S2 window", "short drop ghost",
             "ledger + ghost column", "settle (last frame)"]
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
    d.text((8, 8), f"How Does a Cat Always Land on Its Feet? - contact sheet 2: foundation layout (stub scenes, the test lab, the window plates, overlay). {T_} f / {T_ / 30:.2f} s.",
           fill=(240, 236, 228), font=big)
    d.text((8, 34), "Rows 1-2: one frame per scene (all layers; dashed card = temporary stub label; FOUNDATION DEMOS in sc03, sc04, sc06 (hero), sc07, sc10-sc12). Row 3: picture layer only, the engine's states.",
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
    f6 = FR[5]
    big_im = Image.open(R / f"sheet/f{f6:04d}.png").convert("RGB").resize((540, 960), Image.LANCZOS)
    z = ImageDraw.Draw(big_im, "RGBA")
    s = 0.5

    def rect(x0, y0, x1, y1, col, label, fill=None):
        z.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=col, width=2, fill=fill)
        z.text((x0 * s + 4, y0 * s + 2), label, fill=col, font=font)
    rect(0, 0, 1080, 192, (255, 80, 80), "top UI: no content", (255, 80, 80, 40))
    rect(0, 1574, 1080, 1920, (255, 80, 80), "bottom UI y>=1574: no text", (255, 80, 80, 40))
    rect(929, 192, 1080, 1574, (255, 80, 80), "x>=929", (255, 80, 80, 40))
    rect(120, 360, 620, 1000, (120, 220, 120), "CAT FIELD / WINDOW 160-620")
    rect(640, 220, 920, 600, (240, 236, 228), "CARD")
    rect(640, 620, 920, 860, (232, 163, 61), "DIALS")
    rect(140, 630, 920, 1010, (108, 198, 217), "LEDGER (sc11-12)")
    rect(140, 1124, 912, 1204, (230, 230, 120), "placard rail")
    rect(140, 1236, 628, 1290, (230, 230, 120), "tab")
    rect(140, 1296, 940, 1488, (230, 230, 120), "caption slab")
    xr = 8 + ncol * (TW + 8) + 8
    out.paste(big_im, (xr, 60))
    d.text((xr, 60 + 964), f"f{f6} ({scene_of(f6)}, hero) with the safe zones", fill=(220, 225, 215), font=font)
    out.paste(crops, (xr, 60 + 964 + 26))
    d.text((xr, 60 + 964 + 30 + crops.size[1]), "S1 / S2 crops (green) + the Marey cells (green) with their hand cuts (red)", fill=(220, 225, 215), font=font)
    (P / "renders").mkdir(exist_ok=True)
    out.save(P / "renders/foundation_sheet.jpg", quality=86)
    print("wrote", P / "renders/foundation_sheet.jpg", out.size)


if __name__ == "__main__":
    main()
