#!/usr/bin/env python3
"""Stage the render material in public/ and MEASURE it (idempotent; run from the repo root).

    python3 projects/how-hot-can-it-get/prepare_media.py [--force]

Pattern copied from projects/what-if-earth-stopped-spinning/prepare_media.py (video 12, delivered, QA passed).

Every AI plate is seen ONLY through the root WINDOW (shared/Window.tsx, scheduled in build_props.py props.window):
  WINDOW x 220-920, y 360-900 (700 x 540; scene_plan.metadata.safe_areas.window; scenes.md's 'x 160-920' is superseded)
  K1 (sc03) -> S2 (sc04) | closed sc05 | K2 (sc06) -> S4 (sc07-sc09, dimmed for U3's drawings in sc08-sc09) | closed
Staged at the resolution they are shown (smaller files decode faster):
  clips/K1_30.mp4  the assets' 30 fps copy (already FRAME-BLENDED from 24 fps, no duplicated frames: assets_report K1)
                   f0-f150, scaled to 756 x 1344. Played FORWARD ONLY (lesson 27: Kling added a forward glide; the near
                   ground flows down ~1.9 px/f, a ping-pong would run it backwards). The fit puts the horizon at 45 % of the
                   window (the planned framing; S1's horizon is 30.8 % - the '14 % shift'), which also crops the near
                   ground (source y > ~53 % is below the window): the window shows the locked sky / mountains / horizon
                   shimmer band + the slow mid ground.
  clips/K2_30.mp4  f0-f150 (all clean; slow push-in ~6-7 % / 5 s), 778 x 1382. Played FORWARD, then the LAST FRAME HOLDS
                   (sc06 is longer than the clip; no ping-pong: the push-in would reverse); the root adds a slow code push
                   1.00 -> 1.03 over the whole open span so the hold never reads as a freeze.
  stills/S2.jpg    Venus, 756 x 1344 (q 92), as generated (the rocks are sky-lit, NOT glowing: no glow / grade added);
                   the root pushes it 1.00 -> 1.04 over sc04.
  stills/S4.jpg    the collider, 756 x 1344 (q 92); push 1.00 -> 1.05 over sc07-sc09. Resembles a real detector: the tag
                   is the generic 'AI illustration' only; no experiment is named on screen.
  frames/K1_first.jpg, frames/K2_first.jpg, frames/K2_last.jpg  (shown before `start` / after the last staged frame)
  Asserted: nothing staged reaches outside the clean range (K1, K2 <= 30 fps f150).
MEASURED FROM PIXELS (lesson 9) -> artifacts/media_report.json 'fits' (theme.ts FITS must equal them; build_props.py
asserts). A fit draws the staged source (w x h px) at `scale` frame px per source px with `anchor` (source px) at `at`
(frame px); left/top are the source's top-left in frame px.
  K1  horizon (salt edge / mountain base): the strongest smoothed vertical-luma-gradient row in 3 column bands, 25-40 %
      of the staged f0 (assets: 30.8 %) -> at 45 % down the window.
  S2  Venus haze horizon (assets 37.1 %), 30-45 % -> at 42 % down the window (more rock foreground).
  K2  the violet plasma loop's centroid (pixels with B > G + 30 and R > G + 20: violet-pink), on staged f0 (assets
      46.6 % / 44.4 %) -> at the window centre.
  S4  the detector's red module ring: the bounding box of R > 1.5 G and R > 110 pixels (assets x 2-92 %, y 23-70 %); its
      centre (assets ring centre ~50 % / 40 %) -> at the window centre.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as nd

P = Path("projects/how-hot-can-it-get")
PUB = P / "public"
FORCE = "--force" in sys.argv
WIN = {"x0": 220, "x1": 920, "y0": 360, "y1": 900}
CLIPS = {
    "K1": {"src": "clip_k1_heat_shimmer.mp4", "first": 0, "last": 150, "w": 756, "h": 1344, "clean_last": 150},
    "K2": {"src": "clip_k2_plasma_ring.mp4", "first": 0, "last": 150, "w": 778, "h": 1382, "clean_last": 150},
}
STILLS = {"S2": {"src": "plate_venus_surface.png", "w": 756, "h": 1344}, "S4": {"src": "plate_collider_detector.png", "w": 756, "h": 1344}}


def run(*a: str) -> None:
    subprocess.run(list(a), check=True)


def probe_frames(path: Path) -> int:
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return int(r.stdout.strip())


def frame_img(src: Path, n: int, dst: Path) -> None:
    run("ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"select=eq(n\\,{n})", "-frames:v", "1", "-q:v", "2", str(dst))


def fit(w: int, h: int, scale: float, anchor: tuple[float, float], at: tuple[float, float]) -> dict:
    return {"w": w, "h": h, "scale": scale, "anchor": [round(anchor[0], 1), round(anchor[1], 1)], "at": [round(at[0], 1), round(at[1], 1)],
            "left": round(at[0] - scale * anchor[0], 1), "top": round(at[1] - scale * anchor[1], 1)}


def horizon_row(img: np.ndarray, lo: float, hi: float) -> tuple[float, list[float]]:
    """the strongest smoothed vertical luma gradient row inside [lo, hi] (fractions of the height), in 3 column bands"""
    L = nd.gaussian_filter(img.mean(2), 3)
    H, W = L.shape
    g = np.abs(np.diff(L, axis=0))
    rows = []
    for b in range(3):
        band = g[:, b * W // 3 + W // 12:(b + 1) * W // 3 - W // 12].mean(1)
        band = nd.gaussian_filter1d(band, 4)
        a, z = int(lo * H), int(hi * H)
        rows.append(float(a + np.argmax(band[a:z])))
    return float(np.median(rows)), rows


def violet_centroid(img: np.ndarray) -> tuple[float, float, list[float]]:
    R, G, B = img[..., 0], img[..., 1], img[..., 2]
    m = (B > G + 30) & (R > G + 20) & (R + B > 220)
    m = nd.binary_opening(m, iterations=2)
    ys, xs = np.nonzero(m)
    return float(xs.mean()), float(ys.mean()), [round(100 * xs.min() / img.shape[1], 1), round(100 * xs.max() / img.shape[1], 1),
                                                  round(100 * ys.min() / img.shape[0], 1), round(100 * ys.max() / img.shape[0], 1)]


def red_ring_box(img: np.ndarray) -> tuple[float, float, list[float]]:
    R, G = img[..., 0], img[..., 1]
    m = (R > 1.5 * G) & (R > 110)
    m = nd.binary_opening(m, iterations=2)
    ys, xs = np.nonzero(m)
    x0, x1 = np.percentile(xs, [1, 99])
    y0, y1 = np.percentile(ys, [1, 99])
    H, W = m.shape
    return float((x0 + x1) / 2), float((y0 + y1) / 2), [round(100 * x0 / W, 1), round(100 * x1 / W, 1), round(100 * y0 / H, 1), round(100 * y1 / H, 1)]


def covers(f: dict, box: dict, push: float = 1.0, margin: float = 2.0) -> bool:
    """the fitted source (at the given push about the box centre) covers the box (+ margin)"""
    cx, cy = (box["x0"] + box["x1"]) / 2, (box["y0"] + box["y1"]) / 2
    l = cx + (f["left"] - cx) * push
    t = cy + (f["top"] - cy) * push
    r = cx + (f["left"] + f["w"] * f["scale"] - cx) * push
    b = cy + (f["top"] + f["h"] * f["scale"] - cy) * push
    return l <= box["x0"] - margin and t <= box["y0"] - margin and r >= box["x1"] + margin and b >= box["y1"] + margin


def main() -> None:
    for sub in ("stills", "clips", "frames"):
        (PUB / sub).mkdir(parents=True, exist_ok=True)
    nframes = {}
    for cid, c in CLIPS.items():
        assert c["last"] <= c["clean_last"], cid
        out = PUB / "clips" / f"{cid}_30.mp4"
        if FORCE or not out.exists():
            run("ffmpeg", "-v", "error", "-y", "-i", str(P / "assets/video" / c["src"]), "-vf",
                f"select=between(n\\,{c['first']}\\,{c['last']}),setpts=N/30/TB,scale={c['w']}:{c['h']}:flags=lanczos,format=yuv420p",
                "-r", "30", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-g", "15", "-movflags", "+faststart", str(out))
            print("wrote", out)
        nframes[cid] = probe_frames(out)
        assert nframes[cid] == c["last"] - c["first"] + 1, (cid, nframes[cid])
        first = PUB / "frames" / f"{cid}_first.jpg"
        if FORCE or not first.exists():
            frame_img(out, 0, first)
    last = PUB / "frames" / "K2_last.jpg"
    if FORCE or not last.exists():
        frame_img(PUB / "clips/K2_30.mp4", nframes["K2"] - 1, last)
    for sid, s in STILLS.items():
        dst = PUB / "stills" / f"{sid}.jpg"
        if FORCE or not dst.exists():
            Image.open(P / "assets/images" / s["src"]).convert("RGB").resize((s["w"], s["h"]), Image.LANCZOS).save(dst, quality=92)

    # ---- measurements (on the STAGED pixels) -----------------------------------------------------------------------
    k1 = np.asarray(Image.open(PUB / "frames/K1_first.jpg").convert("RGB")).astype(float)
    k1_h, k1_rows = horizon_row(k1, 0.25, 0.40)
    s2 = np.asarray(Image.open(PUB / "stills/S2.jpg").convert("RGB")).astype(float)
    s2_h, s2_rows = horizon_row(s2, 0.30, 0.45)
    k2 = np.asarray(Image.open(PUB / "frames/K2_first.jpg").convert("RGB")).astype(float)
    k2_x, k2_y, k2_ext = violet_centroid(k2)
    s4 = np.asarray(Image.open(PUB / "stills/S4.jpg").convert("RGB")).astype(float)
    s4_x, s4_y, s4_ext = red_ring_box(s4)
    meas = {
        "K1_horizon_pct": round(100 * k1_h / CLIPS["K1"]["h"], 2), "K1_horizon_bands_px": k1_rows,
        "S2_horizon_pct": round(100 * s2_h / STILLS["S2"]["h"], 2), "S2_horizon_bands_px": s2_rows,
        "K2_ring_centroid_pct": [round(100 * k2_x / CLIPS["K2"]["w"], 2), round(100 * k2_y / CLIPS["K2"]["h"], 2)], "K2_ring_extent_pct_x0x1y0y1": k2_ext,
        "S4_ring_centre_pct": [round(100 * s4_x / STILLS["S4"]["w"], 2), round(100 * s4_y / STILLS["S4"]["h"], 2)], "S4_red_extent_pct_x0x1y0y1": s4_ext,
    }
    # the assets agent measured S1 30.8 %, S2 37.1 %, S3 ring (46.6 %, 44.4 %), S4 ring centre ~(50 %, 40 %): ours must agree
    assert abs(meas["K1_horizon_pct"] - 30.8) < 3.0, meas
    assert abs(meas["S2_horizon_pct"] - 37.1) < 3.0, meas
    assert abs(meas["K2_ring_centroid_pct"][0] - 46.6) < 6 and abs(meas["K2_ring_centroid_pct"][1] - 44.4) < 6, meas
    assert abs(meas["S4_ring_centre_pct"][0] - 50) < 8 and abs(meas["S4_ring_centre_pct"][1] - 46) < 10, meas

    ww, wh = WIN["x1"] - WIN["x0"], WIN["y1"] - WIN["y0"]
    cx, cy = (WIN["x0"] + WIN["x1"]) / 2, (WIN["y0"] + WIN["y1"]) / 2
    fits = {
        "K1": fit(CLIPS["K1"]["w"], CLIPS["K1"]["h"], 1.0, (CLIPS["K1"]["w"] / 2, k1_h), (cx, WIN["y0"] + 0.45 * wh)),
        "S2": fit(STILLS["S2"]["w"], STILLS["S2"]["h"], 1.0, (STILLS["S2"]["w"] / 2, s2_h), (cx, WIN["y0"] + 0.42 * wh)),
        "K2": fit(CLIPS["K2"]["w"], CLIPS["K2"]["h"], 1.0, (k2_x, k2_y), (cx, cy)),
        "S4": fit(STILLS["S4"]["w"], STILLS["S4"]["h"], 1.0, (s4_x, s4_y), (cx, cy)),
    }
    for k in fits:
        assert covers(fits[k], WIN), (k, fits[k], WIN)
    checks = {k: {"window_shows_source_y_pct": [round(100 * (WIN["y0"] - fits[k]["top"]) / fits[k]["scale"] / fits[k]["h"], 1),
                                                 round(100 * (WIN["y1"] - fits[k]["top"]) / fits[k]["scale"] / fits[k]["h"], 1)],
                  "window_shows_source_x_pct": [round(100 * (WIN["x0"] - fits[k]["left"]) / fits[k]["scale"] / fits[k]["w"], 1),
                                                 round(100 * (WIN["x1"] - fits[k]["left"]) / fits[k]["scale"] / fits[k]["w"], 1)]} for k in fits}
    # K1: the near ground (source y >= 70 %, ~1.9 px/f) must stay out of the window
    assert checks["K1"]["window_shows_source_y_pct"][1] < 60, checks["K1"]

    report = {
        "images": {"S2": "stills/S2.jpg", "S4": "stills/S4.jpg"},
        "clips": {cid: {"file": f"clips/{cid}_30.mp4", "frames": nframes[cid], "fps": 30, "w": c["w"], "h": c["h"],
                        "srcRange30": [c["first"], c["last"]],
                        "source": f"assets/video/{c['src']} (30 fps, frame-blended by the assets stage), clean f{c['first']}-f{c['last']} only"} for cid, c in CLIPS.items()},
        "frames": {"K1_first": "frames/K1_first.jpg", "K2_first": "frames/K2_first.jpg", "K2_last": "frames/K2_last.jpg"},
        "window": WIN,
        "measured": meas,
        "fits": fits,
        "framing_checks": checks,
        "notes": {"K1": "forward only (Kling forward glide: near ground ~1.9 px/f, cropped out by the fit); 151 frames cover the K1 span",
                  "K2": "forward, then the last frame holds (+ a root code push 1.00 -> 1.03 over the open span); no ping-pong",
                  "S2": "still, push 1.00 -> 1.04; no glow / grade added (464 degC rock does not glow)",
                  "S4": "still, push 1.00 -> 1.05; resembles a real detector: generic 'AI illustration' tag, no experiment named"},
    }
    (P / "artifacts/media_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: report[k] for k in ("clips", "measured", "fits", "framing_checks")}, indent=1))
    print("wrote artifacts/media_report.json")


if __name__ == "__main__":
    main()
