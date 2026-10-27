#!/usr/bin/env python3
"""Contact sheet 2 (foundation layout) -> renders/foundation_sheet.jpg. Run from the repo root AFTER:
    node projects/how-hot-can-it-get/stills.cjs --frames $(python3 projects/how-hot-can-it-get/contact_sheet2.py --frames) --scale 0.5 --out renders/review/foundation/sheet
    node projects/how-hot-can-it-get/stills.cjs --frames $(python3 projects/how-hot-can-it-get/contact_sheet2.py --pic) --scale 0.5 --layers picture --out renders/review/foundation/sheet_pic
Rows 1-2: one stub frame per scene (all layers: the black-body world + window + root tags + overlay + stub labels; sc03 /
sc05 carry the FOUNDATION DEMO hero labels). Row 3: the glow engine on the picture layer (dark forge, the false-colour
window, first glow ~975 K, orange, yellow-white, converged blue-white, the compressed rail, the Planck view + fray, the
settle). Right: an sc06 frame at full height with the safe zones drawn (BUILD.md §2). Pattern of video 12's contact_sheet2.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

P = Path("projects/how-hot-can-it-get")
R = P / "renders/review/foundation"
props = json.loads((P / "artifacts/props.json").read_text())
scenes = props["timeline"]["scenes"]
FR = [s["from"] + int(s["durationInFrames"] * (0.62 if s["id"] != "sc13" else 0.9)) for s in scenes]
K = props["audio"]
glow_k = props["glow"]["k"]


def first_at(kelvin: float) -> int:
    return next(f for f in range(K["sweepStart"], K["sunCoreSeat"] + 1) if glow_k[f] >= kelvin)


PIC = [40, K["lutOn"] + 12, first_at(975), first_at(1650), first_at(3400), first_at(40000), K["lhcSeat"] + 10, K["fray"] + 20, props["timeline"]["total_frames"] - 1]
PIC_LABEL = ["dark forge (sc01)", "false colour (K1)", "first glow ~975 K", "orange ~1,650 K", "yellow-white ~3,400 K", "converged >= 40,000 K",
             "compressed (LHC)", "Planck view + fray", "settle (last frame)"]
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
    total = props["timeline"]["total_frames"]
    ncol = max(7, len(PIC))
    W = ncol * (TW + 8) + 8 + 560 + 16
    out = Image.new("RGB", (W, 60 + 3 * (TH + 34) + 40), (22, 20, 18))
    d = ImageDraw.Draw(out)
    d.text((8, 8), f"How Hot Can It Get? - contact sheet 2: foundation layout (stub scenes, black-body engine, ladder, window, overlay). {total} f / {total / 30:.2f} s.",
           fill=(240, 236, 228), font=big)
    d.text((8, 34), "Rows 1-2: one frame per scene (all layers; dashed amber card = temporary stub; sc03 / sc05 = FOUNDATION DEMO labels). Row 3: picture layer only, the glow engine's states.",
           fill=(180, 172, 164), font=font)
    for i, f in enumerate(FR):
        x = 8 + (i % 7) * (TW + 8)
        y = 60 + (i // 7) * (TH + 34)
        out.paste(Image.open(R / f"sheet/f{f:04d}.png").convert("RGB").resize((TW, TH), Image.LANCZOS), (x, y))
        d.text((x, y + TH + 4), f"{scene_of(f)} f{f}", fill=(220, 215, 205), font=font)
    for i, f in enumerate(PIC):
        x = 8 + i * (TW + 8)
        y = 60 + 2 * (TH + 34)
        out.paste(Image.open(R / f"sheet_pic/f{f:04d}.png").convert("RGB").resize((TW, TH), Image.LANCZOS), (x, y))
        k = glow_k[f]
        d.text((x, y + TH + 4), f"f{f} {PIC_LABEL[i]}", fill=(255, 170, 90), font=font)
        d.text((x, y + TH + 18), f"glow {k:,.0f} K, i {props['glow']['i'][f]:.2f}" if k < 1e7 else f"glow i {props['glow']['i'][f]:.2f}", fill=(170, 160, 150), font=font)
    f6 = FR[5]
    big_im = Image.open(R / f"sheet/f{f6:04d}.png").convert("RGB").resize((540, 960), Image.LANCZOS)
    z = ImageDraw.Draw(big_im, "RGBA")
    s = 0.5

    def rect(x0, y0, x1, y1, col, label, fill=None):
        z.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=col, width=2, fill=fill)
        z.text((x0 * s + 4, y0 * s + 2), label, fill=col, font=font)
    rect(0, 0, 1080, 192, (255, 80, 80), "top UI: ground only", (255, 80, 80, 40))
    rect(0, 1574, 1080, 1920, (255, 80, 80), "bottom UI y>=1574: no text", (255, 80, 80, 40))
    rect(929, 192, 1080, 1574, (255, 80, 80), "x>=929", (255, 80, 80, 40))
    rect(0, 320, 1080, 1100, (120, 220, 120), "stage y 320-1100")
    rect(220, 360, 920, 900, (240, 236, 228), "WINDOW 220-920 / 360-900")
    rect(150, 350, 214, 1060, (255, 160, 60), "rail")
    rect(248, 210, 520, 254, (255, 160, 60), "chip")
    rect(140, 1124, 912, 1204, (230, 230, 120), "placard rail")
    rect(140, 1236, 628, 1290, (230, 230, 120), "tab")
    rect(140, 1296, 940, 1488, (230, 230, 120), "caption slab")
    xr = 8 + ncol * (TW + 8) + 8
    out.paste(big_im, (xr, 60))
    d.text((xr, 60 + 964), f"f{f6} ({scene_of(f6)}) with the safe zones", fill=(220, 215, 205), font=font)
    out.save(P / "renders/foundation_sheet.jpg", quality=88)
    print("wrote", P / "renders/foundation_sheet.jpg", out.size)


if __name__ == "__main__":
    main()
