#!/usr/bin/env python3
"""Stage the window plates in public/stills/ and MEASURE them (idempotent; run from the repo root).

    python3 projects/how-heavy-can-anything-get/prepare_media.py [--force]

Pattern of projects/how-a-cat-lands/prepare_media.py (video 15, QA passed). No AI clips. ONE window box for every plate
(theme.ts L.win: x 580-920, y 440-893, 340 x 453, portrait 3:4, RIGHT of the rung labels so a seated label never sits under a
photo; the plan's x 470-920 box would have covered 'EARTH (orbit) · ~107,000' and 'PARKER (fastest built)'), so each crop has
the window's aspect (0.7506).

The three AI stills exist (assets/images/plate_sand.png, plate_blood_cells.png, plate_virus.png; 1152 x 2048). Crop boxes
are MEASURED on them (lesson 9: from pixels, the window's aspect) with the subject inside (lesson 39: feature points asserted
inside the crop with a 20 px margin). The window's fourth state (sc06-sc07, the atom) is DRAWN in code (shared/Window.tsx), not
a plate. A missing source still falls back to a labelled placeholder card ("placeholder": true).
-> artifacts/media_report.json + renders/review/crops.jpg (the crops on their plates, or the placeholders).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

P = Path("projects/how-heavy-can-anything-get")
PUB = P / "public" / "stills"
FORCE = "--force" in sys.argv
WIN = {"x0": 580, "x1": 920, "y0": 440, "y1": 893}
WW, WH = WIN["x1"] - WIN["x0"], WIN["y1"] - WIN["y0"]

# crop boxes MEASURED on the 1152 x 2048 plates (video 17, 2026-10-28, read at 1/4 scale then checked in renders/review/crops.jpg):
# S1 the clear quartz grain sits centre-left (~560, 860); S2 the frontal biconcave cell (~536, 1000); S3 the whole virion
# (centre ~572, 940, radius ~520 px, spikes included). Full plate width, the window's aspect (1152 x 1535).
PLATES = {
    "S1": {"src": "plate_sand.png", "crop": (0, 100, 1152, 1635), "scene": "sc01", "push": [1.0, 1.03],
           "contains": {"quartz_grain": (560, 860), "amber_grain_top": (190, 300), "grain_bottom": (500, 1460)}, "label": "S1 plate_sand",
           "qa": "loose grains, no scale bar / text"},
    "S2": {"src": "plate_blood_cells.png", "crop": (0, 250, 1152, 1785), "scene": "sc04", "push": [1.0, 1.03],
           "contains": {"front_cell": (536, 1000), "cell_top": (440, 300), "cell_low": (480, 1420)}, "label": "S2 plate_blood_cells",
           "qa": "biconcave discs, no text"},
    "S3": {"src": "plate_virus.png", "crop": (0, 173, 1152, 1708), "scene": "sc05", "push": [1.0, 1.03],
           "contains": {"virion_centre": (572, 940), "spike_top": (572, 440), "spike_bottom": (572, 1440), "spike_left": (60, 940), "spike_right": (1090, 940)},
           "label": "S3 plate_virus", "qa": "one whole virion in the crop, spikes included, no text"},
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
    if FORCE or not out.exists():
        im.crop((x0, y0, x1, y1)).resize((WW, WH), Image.LANCZOS).save(out)
    return {"file": f"stills/{mid}.png", "placeholder": False, "source": f"assets/images/{cfg['src']}", "source_px": [im.width, im.height],
            "crop_px": [x0, y0, x1, y1], "crop_pct": {"x": [round(100 * x0 / im.width, 1), round(100 * x1 / im.width, 1)],
            "y": [round(100 * y0 / im.height, 1), round(100 * y1 / im.height, 1)]}, "scale": round(WW / (x1 - x0), 4), "window": WIN,
            "scene": cfg["scene"], "push": cfg["push"], "contains_asserted": cfg["contains"],
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
        for _, (x, y) in PLATES[mid]["contains"].items():
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
