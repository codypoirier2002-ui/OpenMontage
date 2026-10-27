#!/usr/bin/env python3
"""Stage the window plates in public/stills/ and MEASURE them (idempotent; run from the repo root).

    python3 projects/how-a-cat-lands/prepare_media.py [--force]

Pattern of projects/how-a-mosquito-drinks/prepare_media.py (video 14, QA passed). No AI clips. ONE window box for every plate
(theme.ts L.win: x 160-620, y 360-1000, 460 x 640, portrait, LEFT of the checklist card - the plan's x 160-920 box would cover
the card), so each crop has the window's aspect (0.719). Frame windows come from MEASURED pixels (lesson 9; the points below
were read on assets_sheet.jpg at 2x and on the plates):

  S1  plate_cat_midair.png   (sc02)  head-down, belly to camera (assets: 4 legs, 1 tail, 2 ears; fine for "upside down").
      crop px [80, 1122) x [180, 1630) (1042 x 1450): every paw (H1 (310,420), H2 (950,700), F1 (184,932), F2 (814,1268)),
      the tail tip (1080,260) and both ears ((274,1450), (534,1530)) INSIDE (asserted with a margin). Lanczos to 460 x 640.
  S2  plate_cat_landing.png  (sc09)  all four paws on the floor. crop px [8, 1144) x [70, 1650) (1136 x 1580): tail tip
      (268,120), ears ((648,800), (904,800)), the paws (H1 (268,1560), F2 (818,1600)) INSIDE; the occluded far hind paw
      (645-715, 1515-1580) is inside but never zoomed (push <= 1.03).
  A1  marey_1894.jpg (engraving after E.-J. Marey's 1894 chronophotographs, two strips; public domain). The TOP strip (the
      drop and the turn) is used; its experimenter's HANDS / sleeves reach down to the cats in every cell. Per cell (source px,
      measured on a 2x enlargement): the hand's lowest point and the cut below which the cell is kept. Cells 1-2 are DROPPED
      (the paws are held IN the hands: no cut separates them); cells 3-10 are kept, each cut >= its hand bottom + 4 px
      (asserted) with an 8 px dark feather (the engraving's own dark ground colour) so no hand or sleeve pixel survives and the
      held-up paws of cells 3-5 fade at the cut. Each cell -> a 125 x 156 px source tile centred on its cat, Lanczos x2.6 ->
      325 x 406 (light unsharp) -> public/stills/A1_fNN.png; shared/Strip.tsx stacks them in a vertical FILM STRIP (sprocket
      margins drawn in code) that steps up one frame at a time (props.window plate A1 'step'). Tag (root): 'engraving after
      É.-J. Marey, 1894' (verified_on_screen_strings via sync_scene_plan.py).
-> artifacts/media_report.json + renders/review/crops.jpg (the crops on their plates + the Marey cells with their cut lines).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

P = Path("projects/how-a-cat-lands")
PUB = P / "public" / "stills"
FORCE = "--force" in sys.argv
WIN = {"x0": 160, "x1": 620, "y0": 360, "y1": 1000}
WW, WH = WIN["x1"] - WIN["x0"], WIN["y1"] - WIN["y0"]
UNSHARP = ImageFilter.UnsharpMask(radius=1.0, percent=50, threshold=2)

PLATES = {
    "S1": {"src": "plate_cat_midair.png", "crop": (80, 180, 1122, 1630), "scene": "sc02", "push": [1.0, 1.03],
           "contains": {"paw H1": (310, 420), "paw H2": (950, 700), "paw F1": (184, 932), "paw F2": (814, 1268),
                        "tail tip": (1080, 260), "ear L": (274, 1450), "ear R": (534, 1530)}},
    "S2": {"src": "plate_cat_landing.png", "crop": (8, 70, 1144, 1650), "scene": "sc09", "push": [1.0, 1.03],
           "contains": {"tail tip": (268, 120), "ear L": (648, 800), "ear R": (904, 800), "paw H1": (268, 1560),
                        "paw F2": (818, 1600), "far hind paw (occluded shaft)": (680, 1548)}},
}
# A1 top-strip cells (source px of the 1251 x 737 engraving): (cell, x centre of the cat, hand bottom y, cut y)
MAREY_CELLS = [(3, 298, 166, 172), (4, 411, 160, 166), (5, 541, 157, 162), (6, 672, 147, 156), (7, 797, 141, 154),
               (8, 922, 132, 154), (9, 1053, 110, 154), (10, 1185, 100, 154)]
MAREY_DROPPED = {1: "paws held in the hand (hand bottom ~163, paw top ~154): no clean cut", 2: "same (hand ~163, paws ~150)"}
TILE_W, TILE_Y0, TILE_Y1 = 125, 150, 306
CELL_SCALE = 2.6
FEATHER = 8


def crop_plate(mid: str, cfg: dict) -> dict:
    im = Image.open(P / "assets/images" / cfg["src"]).convert("RGB")
    x0, y0, x1, y1 = cfg["crop"]
    assert abs((x1 - x0) / (y1 - y0) - WW / WH) < 0.004, (mid, (x1 - x0) / (y1 - y0), WW / WH)
    for name, (x, y) in cfg["contains"].items():
        assert x0 + 20 <= x <= x1 - 20 and y0 + 20 <= y <= y1 - 20, ("feature outside the crop", mid, name)
    out = PUB / f"{mid}.png"
    if FORCE or not out.exists():
        im.crop((x0, y0, x1, y1)).resize((WW, WH), Image.LANCZOS).save(out)
    return {"file": f"stills/{mid}.png", "crop_px": [x0, y0, x1, y1], "crop_pct": {"x": [round(100 * x0 / im.width, 1), round(100 * x1 / im.width, 1)],
            "y": [round(100 * y0 / im.height, 1), round(100 * y1 / im.height, 1)]}, "scale": round(WW / (x1 - x0), 4), "window": WIN,
            "scene": cfg["scene"], "push": cfg["push"], "contains_asserted": cfg["contains"]}


def marey() -> dict:
    src = Image.open(P / "assets/images/marey_1894.jpg").convert("L")
    a = np.asarray(src).astype(np.float32)
    ground = float(np.median(a[320:370, :]))      # the engraving's dark ground between the strips
    cells = []
    for n, cx, hand, cut in MAREY_CELLS:
        assert cut >= hand + 4, ("cut above the hand", n)
        x0 = int(cx - TILE_W / 2)
        tile = a[TILE_Y0:TILE_Y1, x0:x0 + TILE_W].copy()
        yy = np.arange(TILE_Y0, TILE_Y1)[:, None]
        w = np.clip((yy - cut) / FEATHER, 0, 1)    # 0 above the cut, ramps to 1 over FEATHER px below it
        tile = ground + (tile - ground) * w
        # assert: nothing bright survives above the cut (hands / sleeves are bright engraving whites)
        assert float(tile[: cut - TILE_Y0].max()) <= ground + 1, (n, "bright pixels above the cut")
        img = Image.fromarray(np.clip(tile, 0, 255).astype(np.uint8)).convert("RGB")
        img = img.resize((round(TILE_W * CELL_SCALE), round((TILE_Y1 - TILE_Y0) * CELL_SCALE)), Image.LANCZOS).filter(UNSHARP)
        f = PUB / f"A1_f{n:02d}.png"
        if FORCE or not f.exists():
            img.save(f)
        cells.append({"cell": n, "file": f"stills/A1_f{n:02d}.png", "src_box": [x0, TILE_Y0, x0 + TILE_W, TILE_Y1], "hand_bottom_y": hand,
                      "cut_y": cut, "feather_px": FEATHER})
    return {"file": "assets/images/marey_1894.jpg", "strip": "top (the drop and the turn)", "cells": cells, "dropped": MAREY_DROPPED,
            "tile_px": [round(TILE_W * CELL_SCALE), round((TILE_Y1 - TILE_Y0) * CELL_SCALE)], "ground_luma": round(ground, 1),
            "tag": "engraving after É.-J. Marey, 1894",
            "provenance": "Wikimedia Commons File:Falling_cat_1894.jpg (public domain; an engraved print after Marey's chronophotographs, Nature 51 (1894) / Comptes rendus 119)"}


def review(rep: dict) -> None:
    tiles = []
    for mid in ("S1", "S2"):
        im = Image.open(P / "assets/images" / PLATES[mid]["src"]).convert("RGB")
        d = ImageDraw.Draw(im)
        x0, y0, x1, y1 = PLATES[mid]["crop"]
        d.rectangle([x0, y0, x1, y1], outline=(60, 230, 60), width=8)
        for _, (x, y) in PLATES[mid]["contains"].items():
            d.ellipse([x - 14, y - 14, x + 14, y + 14], outline=(255, 220, 0), width=5)
        tiles.append(im.resize((288, 512)))
    src = Image.open(P / "assets/images/marey_1894.jpg").convert("RGB")
    d = ImageDraw.Draw(src)
    for c in rep["A1"]["cells"]:
        bx = c["src_box"]
        d.rectangle(bx, outline=(60, 230, 60), width=2)
        d.line([bx[0], c["cut_y"], bx[2], c["cut_y"]], fill=(255, 60, 60), width=2)
    top = src.crop((0, 60, 1251, 320)).resize((600, 125))
    cells = [Image.open(P / "public" / c["file"]).resize((75, 94)) for c in rep["A1"]["cells"]]
    sheet = Image.new("RGB", (600 + 16, 512 + 125 + 94 + 32), (20, 26, 30))
    sheet.paste(tiles[0], (0, 0)); sheet.paste(tiles[1], (300, 0))
    sheet.paste(top, (0, 520))
    for i, c in enumerate(cells):
        sheet.paste(c, (i * 77, 520 + 130))
    (P / "renders/review").mkdir(parents=True, exist_ok=True)
    sheet.save(P / "renders/review/crops.jpg", quality=88)


def main() -> None:
    PUB.mkdir(parents=True, exist_ok=True)
    rep = {"window": WIN, "plates": {mid: crop_plate(mid, cfg) for mid, cfg in PLATES.items()}, "A1": marey()}
    rep["plates"]["A1"] = {"file": None, "window": WIN, "scene": "sc03", "cells": len(rep["A1"]["cells"]), "push": [1.0, 1.0]}
    rep["process"] = __doc__.split("\n\n", 1)[1]
    (P / "artifacts/media_report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    review(rep)
    print("plates:", {k: v.get("crop_px") for k, v in rep["plates"].items()}, "marey cells:", [c["cell"] for c in rep["A1"]["cells"]])


if __name__ == "__main__":
    main()
