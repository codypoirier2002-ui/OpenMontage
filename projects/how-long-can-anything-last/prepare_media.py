#!/usr/bin/env python3
"""Stage the window plates in public/stills/ and MEASURE them (idempotent; run from the repo root).

    python3 projects/how-long-can-anything-last/prepare_media.py [--force]

Pattern of video 17 / 18. No AI clips. ONE window box for every plate
(theme.ts L.win: x 580-920, y 440-893, 340 x 453, portrait 3:4, RIGHT of the rung labels so a seated label never sits under a
photo; the plan's x 470-920 box would have covered 'EARTH (orbit) · ~107,000' and 'PARKER (fastest built)'), so each crop has
the window's aspect (0.7506).

The three AI stills exist (assets/images/plate_tortoise.png, plate_shark.png, plate_pine.png; 1152 x 2048). Crop boxes
are MEASURED on them (lesson 9: from pixels, the window's aspect) with the subject inside (lesson 39: feature points asserted
inside the crop with a 20 px margin). The window's other states (the Sun vs a red dwarf, the detector tank) are DRAWN in code (shared/Window.tsx), not plates. A missing source still falls back to a labelled placeholder card ("placeholder": true).
-> artifacts/media_report.json + renders/review/crops.jpg (the crops on their plates, or the placeholders).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

P = Path("projects/how-long-can-anything-last")
PUB = P / "public" / "stills"
FORCE = "--force" in sys.argv
WIN = {"x0": 580, "x1": 920, "y0": 440, "y1": 893}
WW, WH = WIN["x1"] - WIN["x0"], WIN["y1"] - WIN["y0"]

# crop boxes MEASURED on the 1152 x 2048 plates (video 19, read at 1/2 scale then checked in renders/review/crops.jpg): full plate
# width, the window's aspect (1152 x 1535). `middle` = the SUBJECT's centre points, asserted inside the middle 60 % of the crop on
# both axes; `contains` = further feature points asserted inside the crop with a 20 px margin (the head / tail / tips at the edge).
PLATES = {
    "S1": {"src": "plate_tortoise.png", "crop": (0, 193, 1152, 1728), "scene": "sc03", "push": [1.0, 1.03],
           "middle": {"shell_centre": (461, 737), "front_leg": (625, 1230)},
           "contains": {"head": (1085, 901), "rear_foot": (300, 1300)}, "label": "S1 plate_tortoise",
           "qa": "one giant tortoise on grass, no text"},
    "S2": {"src": "plate_shark.png", "crop": (0, 88, 1152, 1623), "scene": "sc04", "push": [1.0, 1.03],
           "middle": {"body_centre": (573, 850), "eye": (886, 960)},
           "contains": {"snout": (1090, 990), "tail": (82, 660)}, "label": "S2 plate_shark",
           "qa": "one Greenland shark, no text"},
    "S3": {"src": "plate_pine.png", "crop": (0, 130, 1152, 1665), "scene": "sc05", "push": [1.0, 1.03],
           "middle": {"trunk_mid": (512, 1024), "canopy": (778, 614)},
           "contains": {"top_tip": (328, 174), "trunk_base": (700, 1500)}, "label": "S3 plate_pine",
           "qa": "one bristlecone pine on a ridge, no text"},
}


def default_crop(w: int, h: int) -> tuple[int, int, int, int]:
    """the widest box of the window's aspect inside the plate, centred on the middle of the frame"""
    cw = w
    ch = round(cw * WH / WW)
    if ch > h:
        ch = h
        cw = round(ch * WW / WH)
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    return x0, y0, x0 + cw, y0 + ch


def placeholder(mid: str, cfg: dict) -> Image.Image:
    im = Image.new("RGB", (WW, WH), (14, 19, 32))
    d = ImageDraw.Draw(im)
    try:
        big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    except OSError:
        big = small = ImageFont.load_default()
    for y in range(0, WH, 24):
        d.line([(0, y), (WW, y)], fill=(22, 29, 46), width=1)
    d.rectangle([12, 12, WW - 13, WH - 13], outline=(80, 92, 108), width=2)
    d.text((WW / 2, WH / 2 - 40), "PENDING STILL", fill=(190, 200, 210), font=big, anchor="mm")
    d.text((WW / 2, WH / 2 + 4), cfg["label"], fill=(150, 160, 172), font=small, anchor="mm")
    d.text((WW / 2, WH / 2 + 34), "placeholder: not the AI impression", fill=(120, 130, 142), font=small, anchor="mm")
    return im


def crop_plate(mid: str, cfg: dict) -> dict:
    src = P / "assets/images" / cfg["src"]
    out = PUB / f"{mid}.png"
    if not src.exists():
        if FORCE or not out.exists():
            placeholder(mid, cfg).save(out)
        return {"file": f"stills/{mid}.png", "placeholder": True, "missing_source": f"assets/images/{cfg['src']}", "window": WIN,
                "scene": cfg["scene"], "push": cfg["push"], "pending_qa": cfg["qa"],
                "note": "a labelled dark card in the window's size; replace by re-running prepare_media.py --force once the still exists"}
    im = Image.open(src).convert("RGB")
    x0, y0, x1, y1 = cfg["crop"] or default_crop(im.width, im.height)
    assert abs((x1 - x0) / (y1 - y0) - WW / WH) < 0.004, (mid, (x1 - x0) / (y1 - y0), WW / WH)
    for name, (x, y) in cfg["contains"].items():
        assert x0 + 20 <= x <= x1 - 20 and y0 + 20 <= y <= y1 - 20, ("feature outside the crop", mid, name)
    for name, (x, y) in cfg["middle"].items():
        cw, ch = x1 - x0, y1 - y0
        assert x0 + 0.2 * cw <= x <= x1 - 0.2 * cw and y0 + 0.2 * ch <= y <= y1 - 0.2 * ch, ("subject outside the middle 60 % of the crop", mid, name)
    if FORCE or not out.exists():
        im.crop((x0, y0, x1, y1)).resize((WW, WH), Image.LANCZOS).save(out)
    return {"file": f"stills/{mid}.png", "placeholder": False, "source": f"assets/images/{cfg['src']}", "source_px": [im.width, im.height],
            "crop_px": [x0, y0, x1, y1], "crop_pct": {"x": [round(100 * x0 / im.width, 1), round(100 * x1 / im.width, 1)],
            "y": [round(100 * y0 / im.height, 1), round(100 * y1 / im.height, 1)]}, "scale": round(WW / (x1 - x0), 4), "window": WIN,
            "scene": cfg["scene"], "push": cfg["push"], "contains_asserted": cfg["contains"], "middle_60pct_asserted": cfg["middle"],
            "crop_basis": "measured (PLATES crop)" if cfg["crop"] else "DEFAULT middle band (measure it: lesson 9)"}


def review(rep: dict) -> None:
    tiles = []
    for mid in ("S1", "S2", "S3"):
        r = rep["plates"][mid]
        if r["placeholder"]:
            tiles.append(Image.open(PUB / f"{mid}.png").convert("RGB").resize((240, 320)))
            continue
        im = Image.open(P / "assets/images" / PLATES[mid]["src"]).convert("RGB")
        d = ImageDraw.Draw(im)
        x0, y0, x1, y1 = r["crop_px"]
        d.rectangle([x0, y0, x1, y1], outline=(60, 230, 60), width=8)
        for _, (x, y) in {**PLATES[mid]["contains"], **PLATES[mid]["middle"]}.items():
            d.ellipse([x - 14, y - 14, x + 14, y + 14], outline=(255, 220, 0), width=5)
        tiles.append(im.resize((240, 427)))
    sheet = Image.new("RGB", (3 * 248 + 8, max(t.size[1] for t in tiles) + 16), (20, 26, 30))
    for i, t in enumerate(tiles):
        sheet.paste(t, (8 + i * 248, 8))
    (P / "renders/review").mkdir(parents=True, exist_ok=True)
    sheet.save(P / "renders/review/crops.jpg", quality=88)


def main() -> None:
    PUB.mkdir(parents=True, exist_ok=True)
    rep = {"window": WIN, "plates": {mid: crop_plate(mid, cfg) for mid, cfg in PLATES.items()}}
    rep["placeholders"] = [m for m, r in rep["plates"].items() if r["placeholder"]]
    rep["process"] = __doc__.split("\n\n", 1)[1]
    (P / "artifacts/media_report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    review(rep)
    print("plates:", {k: ("PLACEHOLDER" if v["placeholder"] else v["crop_px"]) for k, v in rep["plates"].items()})


if __name__ == "__main__":
    main()
