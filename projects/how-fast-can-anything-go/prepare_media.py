#!/usr/bin/env python3
"""Stage the window plates in public/stills/ and MEASURE them (idempotent; run from the repo root).

    python3 projects/how-fast-can-anything-go/prepare_media.py [--force]

Pattern of projects/how-a-cat-lands/prepare_media.py (video 15, QA passed). No AI clips. ONE window box for every plate
(theme.ts L.win: x 580-920, y 440-893, 340 x 453, portrait 3:4, RIGHT of the rung labels so a seated label never sits under a
photo; the plan's x 470-920 box would have covered 'EARTH (orbit) · ~107,000' and 'PARKER (fastest built)'), so each crop has
the window's aspect (0.7506).

THE STILLS ARE NOT GENERATED YET (assets_report: S1-S3 'NOT GENERATED', the full ElevenLabs connector was denied). Until
they land this script writes a clearly labelled PLACEHOLDER plate per still (a dark card with the plate's name and 'PENDING
STILL' in the window's size) into public/stills/<id>.png and records "placeholder": true in artifacts/media_report.json, so the
whole chain (build_props.py, the composition, the stubs, the contact sheet) runs unchanged.

WHEN THE REAL STILLS LAND (assets/images/plate_cheetah.png, plate_falcon_dive.png, plate_parker_probe.png; 9:16 2K):
  1. count legs / wings / tails on each at 4x (lesson 39) and write the measured feature points into PLATES[*]['contains']
     (every point is asserted inside the crop with a 20 px margin) and the crop box (lesson 9: measure from pixels, keep the
     window's aspect; the plan asks for the middle 60 % to be the most interesting);
  2. python3 projects/how-fast-can-anything-go/prepare_media.py --force   (re-stages the crops, drops the placeholders)
  3. python3 projects/how-fast-can-anything-go/build_props.py             (the plates' 'placeholder' flags go false)
  then re-render the affected stills (sc02, sc03, sc06, sc07). Nothing else changes.
-> artifacts/media_report.json + renders/review/crops.jpg (the crops on their plates, or the placeholders).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

P = Path("projects/how-fast-can-anything-go")
PUB = P / "public" / "stills"
FORCE = "--force" in sys.argv
WIN = {"x0": 580, "x1": 920, "y0": 440, "y1": 893}
WW, WH = WIN["x1"] - WIN["x0"], WIN["y1"] - WIN["y0"]

# crop boxes MEASURED on the 1152 x 2048 plates (2026-10-27; legs/wings/tails counted at 2x: S1 4 legs 1 tail 2 ears, S2 1 head 2 wings 1 tail feet tucked, S3 one craft, shield to the Sun, no text)
# (previously: DEFAULTS for a 1152 x 2048 (9:16 2K) plate: the middle 60 % band, the window's aspect; replace with
# measured boxes + feature points when the stills land (lesson 9 / 39)
PLATES = {
    "S1": {"src": "plate_cheetah.png", "crop": (0, 300, 1152, 1835), "scene": "sc02", "push": [1.0, 1.03], "contains": {"head": (1000, 760), "ear": (960, 730), "tail_tip": (45, 850), "hind_paw": (150, 1100), "front_paw": (1110, 1150)}, "label": "S1 plate_cheetah",
           "qa": "4 legs, 1 tail, 2 ears at 4x (lesson 39) before any crop"},
    "S2": {"src": "plate_falcon_dive.png", "crop": (0, 130, 1152, 1665), "scene": "sc03", "push": [1.0, 1.03], "contains": {"tail_top": (200, 175), "beak": (917, 1536), "eye": (850, 1430), "foot": (277, 810), "wing_edge": (700, 1050)}, "label": "S2 plate_falcon_dive",
           "qa": "1 head, 2 wings tucked, 1 tail; peregrine markings"},
    "S3": {"src": "plate_parker_probe.png", "crop": (0, 100, 1152, 1635), "scene": "sc06", "push": [1.0, 1.04], "contains": {"shield": (600, 1000), "left_panel": (240, 1200), "right_panel": (700, 1350), "bus": (480, 1150), "sun_limb": (600, 700)}, "label": "S3 plate_parker_probe",
           "qa": "one spacecraft, heat shield toward the Sun, no text / logos"},
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
