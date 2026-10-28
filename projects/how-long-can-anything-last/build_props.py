#!/usr/bin/env python3
"""Build artifacts/props.json + props.generated.ts from the measured timeline (run from the repo root).

    python3 projects/how-long-can-anything-last/build_props.py          # write
    python3 projects/how-long-can-anything-last/build_props.py --check  # print pages + schedules only

Video 17 "How Small Can Anything Get?" / the SCALE WELL. Copied from projects/how-fast-can-anything-go/build_props.py (video
16, QA passed) and flipped: the log ladder runs DOWNWARD in metres (L = -log10(m)). Inputs: artifacts/timeline.json (aligned
words, sections, scene windows), artifacts/scene_plan.json (caption pages, placards, verified / forbidden strings: written by
sync_scene_plan.py), artifacts/soundtrack_report.json (key frames + motion constants: build_soundtrack.py owns K, asserted
== build_soundtrack.key_frames(timeline)), artifacts/media_report.json (the window plates). Everything out is ABSOLUTE frames.

Caption pages: scene_plan.metadata.captions.pages (<= 2 lines / <= 6 words, every claim starts its own page, no 2-word
orphan; asserted to cover the narration word for word); the line break is chosen with Bricolage Grotesque 800 @ 58 px
advance widths against a 700 px budget. Exit = 4 f after the page's last word ends (held >= 36 f when the next page allows),
clipped / butted to the next page (lesson 6). The CTA takes the slab ON ctaFrame.

Honesty meter (lesson 3: keyed to the START of the caption page carrying the claim; consecutive pages of one claim merge; a
new claim of the same grade pulses): SAND, HAIR MEASURED; EYE PROBABLY; CELL, VIRUS, ATOM, PROTON, ELECTRON (upper bound)
MEASURED; PLANCK MAYBE from 'Below that,' through all of s5; IDLE at the CTA. (script.json's claim_tags are still video 16's:
the grades here are the brief's.)

THE LADDER: props.ladder.markerL descends rung by rung on eased moves whose FIRST MOVING FRAME is descend* and which END ON
*Seat (asserted); rung chips seat on their seats with their numbers (Ladder.tsx, T.seat); props.counter (ZEROS = zeros after
the decimal point of the active rung's metres, asserted on every seat; 7/8/9 on atomTicks, 10..14 on protonTicks, then an
accelerating spin 15..34 landing 34 ON spinEnd); props.window (S1 sand -> S2 cells -> S3 virus, the drawn ATOM); props.devices
(the reference lines, the electron bracket, the break, the Planck line, the readout, the atom note). Asserted: chips never sit
under the open window and never overlap each other or the electron labels; claim graphics (window states, the atom note) are
gone >= 6 f before the next tab glide; placards exit >= 6 f before the next glide; every channel is constant from the release
(lesson 25); a literal scan of scenes/u*/ against verified_on_screen_strings / forbidden_on_screen (lesson 20).
"""
from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont

P = Path("projects/how-long-can-anything-last")
FPS = 30
LINE_BUDGET_PX = 700
LINE_HARD_PX = 744
CAPTION_PX = 58
EXIT_TAIL = 4
MIN_PAGE = 36
WITHIN_SENTENCE_BUTT_F = 21
BUTT_GAP = 13
GLIDE_LEAD = 6
CLAIM_EXIT_F = 6              # claim graphics / placards gone >= 6 f before the next tab glide (lessons 42 / 52)
PLACARD_MIN_F = 36
PLACARD_PAGE_GUARD_F = 4
PLACARD_TEXT_W = 772 - 2 * 28
PLACARD_SIZES = [26, 25, 24]
FINE_SIZES = [25, 24]
CTA_TEXT = "What's the smallest thing you've ever seen?"
CTA_LINES = ["What's the smallest thing", "you've ever seen?"]
CTA_PX = 52
CLAIMS = {   # first words of a page -> (claim id, state); a page belongs to the claim of the last key at or before it
    ("s1", "A grain of sand"): ("SAND", "MEASURED"),
    ("s1", "A human hair"): ("HAIR", "MEASURED"),
    ("s1", "And that's about where"): ("EYE", "PROBABLY"),
    ("s2", "A red blood cell"): ("CELL", "MEASURED"),
    ("s2", "Most viruses are smaller still,"): ("VIRUS", "MEASURED"),
    ("s3", "An atom is a thousand"): ("ATOM", "MEASURED"),
    ("s3", "And the proton at its centre"): ("PROTON", "MEASURED"),
    ("s4", "Electrons are so small"): ("ELECTRON", "MEASURED"),
    ("s4", "Below that, physicists point"): ("PLANCK", "MAYBE"),
}
WEAK_END = {"a", "an", "the", "to", "of", "and", "is", "in", "it", "at", "as", "its", "by", "for", "if", "so", "with", "on", "no", "any", "that"}
BOUND = {("grain", "of"), ("of", "sand"), ("half", "a"), ("a", "millimetre"), ("human", "hair"), ("a", "tenth"), ("red", "blood"), ("blood", "cell"),
         ("ten", "times"), ("any", "ordinary"), ("ordinary", "microscope"), ("a", "thousand"), ("a", "virus"), ("sixty", "thousand"), ("its", "centre"),
         ("no", "experiment"), ("the", "planck"), ("planck", "length"), ("more", "zeros"), ("the", "decimal"), ("decimal", "point"), ("the", "floor"),
         ("isnt", "one"), ("thirtyfour", "zeros")}
PLACARD_SCENES = {"sc01-sc03": ("sc01", "sc03"), "sc04-sc05": ("sc04", "sc05"), "sc06-sc07": ("sc06", "sc07"), "sc08-sc12": ("sc08", "sc12")}
# THE LADDER (mirrored in theme.ts L; asserted against it)
RAIL = {"x": 250, "y0": 380, "y1": 1000, "L0": 3, "L1": 18}
PPD = (RAIL["y1"] - RAIL["y0"]) / (RAIL["L1"] - RAIL["L0"])
WIN = {"x0": 580, "x1": 920, "y0": 440, "y1": 893}
COUNTER = {"x0": 640, "x1": 920, "y0": 220, "y1": 340}
READOUT = {"x0": 580, "x1": 920, "y0": 470, "y1": 600}
READOUT_PX = 26
ELECTRON = {"x": 300, "nameY": 972, "subY": 1010}
PLANCK_Y = 1080
LABEL_X = 280
CHIP_MAX_RIGHT = WIN["x0"] - 8
MARKER_R = 6
LABEL_PX = 28
ROW_H, CHIP_PAD, CHIP_GAP = 36, 12, 6
# (id, name, number string, metres, L as placed by the brief, seat key, descend key)
RUNGS = [
    ("sand", "SAND", "~0.5 mm", 5e-4, 3.30, "sandSeat", None),
    ("hair", "HAIR", "~70 µm", 7e-5, 4.15, "hairSeat", "descendHair"),
    ("cell", "RED BLOOD CELL", "~8 µm", 8e-6, 5.10, "cellSeat", "descendCell"),
    ("virus", "VIRUS", "~100 nm", 1e-7, 7.00, "virusSeat", "descendVirus"),
    ("atom", "ATOM", "~0.1 nm", 1e-10, 10.0, "atomSeat", "descendAtom"),
    ("proton", "PROTON", "~1.7 fm across", 1.7e-15, 14.77, "protonSeat", "descendProton"),
]
PLANCK_M = 1.6e-35
SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
DECADES = [f"10{('-' + str(n)).translate(SUP)} m" for n in range(RAIL["L0"], RAIL["L1"] + 1)]
REFS = [("eye", 4.0, ["YOUR EYE", "~0.1 mm"], "YOUR EYE · ~0.1 mm", "eyeLine"),
        ("micro", 6.70, ["LIGHT MICROSCOPE", "~200 nm"], "LIGHT MICROSCOPE · ~200 nm", "lightLine")]
LABELS = {"axis": "metres · log scale", "zeros": "ZEROS", "ai": "AI impression", "drawn": "drawn · not to scale"}
ELECTRON_NAME, ELECTRON_SUB = "ELECTRON", "no size found · < 10⁻¹⁸ m"
PLANCK_LABEL, FLOOR_LABEL = "PLANCK LENGTH · 1.6 × 10⁻³⁵ m", "a floor? unproven"
READOUT_TEXT = "0." + "0" * 34 + "16 m"
READOUT_LINES = ["0." + "0" * 18, "0" * 16 + "16 m"]
ATOM_NOTE = "to scale, this dot would be ~0.006 px"
ATOM_NOTE_LINES = ["to scale, this dot", "would be ~0.006 px"]
SPIN_OFFSETS = [0, 2, 4, 6, 8, 10, 12, 14] + list(range(15, 27))   # the spin's 20 steps (15..34) after spinStart: every 2 f, then every frame (accelerating)

norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, P / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def advance(font: str, px: float):
    f = TTFont(str(P / "public/fonts" / font))
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    space = hmtx[cmap[32]][0]
    return lambda s: sum(hmtx[cmap[ord(c)]][0] if ord(c) in cmap else space for c in s) / upm * px


class Track:
    """A per-frame channel built from keyframes: hold the value, then ease to the next over [a, b) (value v ON b)."""

    def __init__(self, total: int, v0: float):
        self.total, self.keys = total, [(0, 0, v0, "hold")]

    def to(self, a: int, b: int, v: float, ease: str = "sine") -> "Track":
        assert a >= self.keys[-1][1] and b >= a, ("keys must not overlap", self.keys[-1], (a, b))
        self.keys.append((a, b, v, ease))
        return self

    def build(self) -> np.ndarray:
        ease = {"sine": lambda x: 0.5 - 0.5 * math.cos(math.pi * x), "linear": lambda x: x, "in": lambda x: x * x,
                "out": lambda x: 1 - (1 - x) ** 3, "outquad": lambda x: 1 - (1 - x) ** 2, "step": lambda x: 1.0}
        out = np.empty(self.total)
        for f in range(self.total):
            cur = self.keys[0][2]
            for a, b, v, e in self.keys[1:]:
                if f >= b:
                    cur = v
                elif f >= a:
                    cur = cur + (v - cur) * ease[e]((f - a) / max(1, b - a))
                    break
                else:
                    break
            out[f] = cur
        return out


def rail_y(Lv: float) -> float:
    return RAIL["y0"] + (Lv - RAIL["L0"]) * PPD


def zeros_after_point(metres: float) -> int:
    return math.ceil(-math.log10(metres) - 1e-9) - 1


def main() -> None:
    check = "--check" in sys.argv
    snd = load_module("build_soundtrack")
    tl = json.loads((P / "artifacts/timeline.json").read_text())
    plan = json.loads((P / "artifacts/scene_plan.json").read_text())
    sound = json.loads((P / "artifacts/soundtrack_report.json").read_text())
    media = json.loads((P / "artifacts/media_report.json").read_text())
    width = advance("BricolageGrotesque-normal-800-latin.woff2", CAPTION_PX)
    total = tl["total_frames"]
    assert sound["total_frames"] == total, "soundtrack is stale"
    sc = {s["id"]: s for s in tl["scenes"]}
    order = [s["id"] for s in tl["scenes"]]
    fr = sound["frames"]
    assert fr == snd.key_frames(tl), "soundtrack_report frames != build_soundtrack.key_frames(timeline)"
    mo = sound["motion"]
    for k in ("SEAT_F", "WINDOW_OPEN_F", "WINDOW_CLOSE_F", "XFADE_F", "CLIMB_F", "TICK_STEP_F"):
        assert mo[k] == getattr(snd, k), ("motion constant differs from build_soundtrack.py", k)
    T = total
    rel = fr["wayEndFrame"]
    SEAT_F, WO, WC, XF = mo["SEAT_F"], mo["WINDOW_OPEN_F"], mo["WINDOW_CLOSE_F"], mo["XFADE_F"]

    words = [{**w, "f0": round(w["start"] * FPS), "f1": max(round(w["end"] * FPS), round(w["start"] * FPS) + 2)} for w in tl["words"]]
    for w in words:
        w["tone"] = "plain"

    # --- caption pages ------------------------------------------------------------------------------------------------
    PAGES = [(p["section"], p["page"]) for p in plan["metadata"]["captions"]["pages"]]
    for sid in ("s1", "s2", "s3", "s4", "s5"):
        assert " ".join(t for s_, t in PAGES if s_ == sid) == " ".join(w["text"] for w in words if w["section"] == sid), ("pages != narration", sid)
    text_w = lambda ws: width(" ".join(w["text"] for w in ws))

    def penalty(ws, k) -> int:
        a = norm(ws[k - 1]["text"])
        b = norm(ws[k]["text"]) if k < len(ws) else ""
        if (a, b) in BOUND:
            return 400
        return 200 if (a in WEAK_END and not re.search(r"[.,:;?!]$", ws[k - 1]["text"])) else 0

    def best_lines(ws, budget=LINE_BUDGET_PX):
        if text_w(ws) <= budget and len(ws) <= 4:
            return [ws]
        best = None
        for k in range(1, len(ws)):
            a, b = ws[:k], ws[k:]
            if text_w(a) > budget or text_w(b) > budget:
                continue
            cost = max(text_w(a), text_w(b)) + penalty(ws, k)
            if best is None or cost < best[0]:
                best = (cost, [a, b])
        if best is None and budget < LINE_HARD_PX:
            return best_lines(ws, LINE_HARD_PX)
        if best is None or text_w(ws) <= budget and best[0] >= 200:
            return [ws] if text_w(ws) <= budget else best[1]
        return best[1]

    pages = []
    cursor = {s: 0 for s in ("s1", "s2", "s3", "s4", "s5")}
    for sid, text in PAGES:
        toks = [w for w in words if w["section"] == sid]
        n = len(text.split())
        run = toks[cursor[sid]: cursor[sid] + n]
        assert " ".join(w["text"] for w in run) == text, (text, [w["text"] for w in run])
        cursor[sid] += n
        assert 3 <= n <= 6, ("page must hold 3-6 words (no 2-word orphan)", text)
        pages.append({"section": sid, "lines": best_lines(run), "text": text})
    clipped = {}
    for pg in pages:
        flat = [w for l in pg["lines"] for w in l]
        for a, b in zip(flat, flat[1:]):
            if a["f0"] < b["f0"] < a["f1"]:
                clipped[(a["text"], a["f0"])] = b["f0"]
    out_pages = []
    for i, pg in enumerate(pages):
        flat = [w for l in pg["lines"] for w in l]
        start = flat[0]["f0"]
        nxt = pages[i + 1]["lines"][0][0]["f0"] if i + 1 < len(pages) else fr["ctaFrame"]
        exit_ = min(max(flat[-1]["f1"] + EXIT_TAIL, start + MIN_PAGE), nxt)
        if nxt - exit_ <= BUTT_GAP:
            exit_ = nxt
        if re.search(r"[,:;]$", flat[-1]["text"]) and nxt - exit_ <= WITHIN_SENTENCE_BUTT_F:
            exit_ = nxt
        out_pages.append({
            "section": pg["section"], "startFrame": start, "exitFrame": exit_, "text": pg["text"],
            "words": [{"text": w["text"], "f0": w["f0"], "f1": clipped.get((w["text"], w["f0"]), w["f1"]), "line": li, "tone": w["tone"]}
                      for li, l in enumerate(pg["lines"]) for w in l],
        })
    for pg in out_pages:
        for li in (0, 1):
            ln = [w["text"] for w in pg["words"] if w["line"] == li]
            assert len(ln) == 0 or width(" ".join(ln)) <= LINE_HARD_PX, ln
        assert max(w["line"] for w in pg["words"]) <= 1 and len(pg["words"]) <= 6
    assert out_pages[-1]["exitFrame"] == fr["ctaFrame"], ("the CTA must take the slab as the last page leaves", out_pages[-1]["exitFrame"], fr["ctaFrame"])
    cta_adv = advance("BricolageGrotesque-normal-800-latin.woff2", CTA_PX)
    assert " ".join(CTA_LINES) == CTA_TEXT and all(cta_adv(l) <= LINE_BUDGET_PX for l in CTA_LINES), [cta_adv(l) for l in CTA_LINES]

    # --- honesty meter (lesson 3) ----------------------------------------------------------------------------------------
    assert all(any(s_ == k[0] and t == k[1] for s_, t in PAGES) for k in CLAIMS), "a CLAIMS key is not a caption page"
    meter = [{"frame": 0, "glideStart": 0, "state": "IDLE", "sublabel": "", "section": "", "anchor": "frame 0", "claim": "none (cold open)", "repeat": False}]
    for (sid, text), pg in zip(PAGES, out_pages):
        if (sid, text) not in CLAIMS:
            continue
        cid, state = CLAIMS[(sid, text)]
        prev = meter[-1]
        f = pg["startFrame"]
        meter.append({"frame": f, "glideStart": max(0, f - GLIDE_LEAD), "state": state, "sublabel": "", "section": sid,
                      "anchor": f"page '{text}'", "claim": cid, "repeat": state == prev["state"] and state != "IDLE"})
    meter.append({"frame": fr["ctaFrame"], "glideStart": fr["ctaFrame"] - GLIDE_LEAD, "state": "IDLE", "sublabel": "", "section": "",
                  "anchor": "the CTA (settle)", "claim": "none (settle)", "repeat": False})
    for a, b in zip(meter, meter[1:]):
        assert b["glideStart"] >= a["frame"] - GLIDE_LEAD and b["frame"] > a["frame"], (a, b)
    keyed = [k["frame"] for k in meter[1:]]
    assert len(keyed) == len(set(keyed)), ("two claims keyed on one caption page (lesson 3)", keyed)
    mkey = {k["claim"]: k for k in meter}
    assert mkey["EYE"]["state"] == "PROBABLY" and mkey["PLANCK"]["state"] == "MAYBE" and meter[-2]["claim"] == "PLANCK"
    glides = [k["glideStart"] for k in meter[1:]]
    next_glide = lambda f: min(g for g in glides if g > f)

    # --- THE LADDER: rungs + the marker -----------------------------------------------------------------------------------
    saira = advance("SairaCondensed-normal-700-latin.woff2", LABEL_PX)
    mono = advance("IBMPlexMono-normal-500-latin.woff2", LABEL_PX)
    one_w = lambda name, num: saira(name) + saira(" · ") + mono(num) + 2 * CHIP_PAD
    rungs = []
    for rid, name, num, metres, Lv, seatk, desck in RUNGS:
        assert abs(Lv + math.log10(metres)) < 0.06, ("the rung's L is not -log10(metres)", rid)
        lines = [f"{name} · {num}"] if LABEL_X + one_w(name, num) <= CHIP_MAX_RIGHT else [name, num]
        rungs.append({"id": rid, "name": name, "num": num, "lines": lines, "metres": metres, "L": Lv, "seat": fr[seatk], "_desc": desck})
    Lof = {r["id"]: r["L"] for r in rungs}
    mk = Track(T, Lof["sand"])
    for r in rungs[1:]:
        mk.to(fr[r["_desc"]] - 1, r["seat"], r["L"], "sine")
    markerL = mk.build()
    for r in rungs[1:]:
        d, s_ = fr[r["_desc"]], r["seat"]
        assert markerL[d - 1] == markerL[d - 2] and markerL[d] > markerL[d - 1], ("the descent's first moving frame must be its key frame", r["id"])
        assert markerL[s_] == r["L"] and markerL[s_ - 1] < r["L"], ("the descent must land ON the seat", r["id"])
    assert np.all(np.diff(markerL) >= 0), "the marker only descends"
    assert markerL[fr["electronIn"]:].max() == markerL[fr["electronIn"]:].min() == Lof["proton"], "the marker does not move from sc08 (nothing to stand on)"
    # QA A1 (lesson 33): from 'Electrons' the narration leaves the proton; the marker stays (there is no size to land on)
    # but dims to a ghost so the eye follows the electron bracket and the Planck line
    vis = Track(T, 1.0).to(fr["electronIn"], fr["electronIn"] + 12, 0.3, "sine").build()
    assert vis[fr["electronIn"]] == 1.0 and abs(vis[-1] - 0.3) < 1e-6
    rail_draw = Track(T, 0.0).to(fr["railDraw"] - 1, fr["railDraw"] + 15, 1.0, "outquad").build()
    assert rail_draw[fr["railDraw"] - 1] == 0 and rail_draw[fr["railDraw"]] > 0
    veil = Track(T, 0.0).to(fr["eyeLine"] - 1, fr["eyeLine"] + 11, 0.2, "linear").build()

    # chip boxes as Ladder.tsx lays them (top-down de-overlap); widths from the faces' advances
    def chip_w(r) -> float:
        if len(r["lines"]) == 1:
            return one_w(r["name"], r["num"])
        return max(saira(r["name"]), mono(r["num"])) + 2 * CHIP_PAD
    boxes, prev_bottom = {}, -1e9
    for r in sorted(rungs, key=lambda r: rail_y(r["L"])):
        h = len(r["lines"]) * ROW_H + 8
        cy = max(rail_y(r["L"]), prev_bottom + CHIP_GAP + h / 2)
        boxes[r["id"]] = (LABEL_X, LABEL_X + chip_w(r), cy - h / 2, cy + h / 2)
        prev_bottom = cy + h / 2
    for r in rungs:
        x0, x1, y0, y1 = boxes[r["id"]]
        assert x1 <= CHIP_MAX_RIGHT, ("a rung chip would reach under the window", r["id"], round(x1))
        assert y0 >= 342, ("a chip reaches the counter band", r["id"])
    ebox = (ELECTRON["x"], ELECTRON["x"] + 420, ELECTRON["nameY"] - 18, ELECTRON["subY"] + 18)
    assert boxes["proton"][3] + 6 <= ebox[2], ("the PROTON chip overlaps the electron labels", boxes["proton"], ebox)
    ladder_notes = "y(L) = 380 + (L - 3) * 620 / 15, L = -log10(m) (no camera); chips de-overlapped top-down (Ladder.tsx, mirrored here)"

    # --- THE COUNTER (ZEROS after the decimal point) ---------------------------------------------------------------------
    value = np.zeros(T, dtype=int)
    steps = [(fr["sandSeat"], 3), (fr["hairSeat"], 4), (fr["cellSeat"], 5), (fr["virusSeat"], 6)]
    steps += [(f_, 7 + i) for i, f_ in enumerate(fr["atomTicks"])] + [(f_, 10 + i) for i, f_ in enumerate(fr["protonTicks"])]
    for f_, v_ in steps:
        value[f_:] = v_
    st = fr["spinTicks"]
    assert st[0] == fr["spinStart"] and st[-1] == fr["spinEnd"] and SPIN_OFFSETS[-1] == fr["spinEnd"] - fr["spinStart"] and len(SPIN_OFFSETS) == 20
    for i, off in enumerate(SPIN_OFFSETS):
        value[fr["spinStart"] + off:] = 15 + i
    spin = [int(v) for v in value[st[0] - 1: st[-1] + 1]]
    assert spin[0] == 14 and spin[1] == 15 and spin[-1] == 34 and spin[-2] == 33 and sorted(set(spin)) == list(range(14, 35)), ("spin 14 -> 34, 20 steps", spin)
    gaps = np.diff(SPIN_OFFSETS)
    assert np.all(np.diff(gaps) <= 0) and gaps[0] > gaps[-1], ("the spin must accelerate", gaps)
    for f_ in st + fr["atomTicks"] + fr["protonTicks"]:
        assert value[f_] > value[f_ - 1], ("the counter must step ON every tick", f_)
    for r in rungs:
        assert value[r["seat"]] == zeros_after_point(r["metres"]) and value[r["seat"] - 1] < value[r["seat"]], ("counter != zeros of the rung ON its seat", r["id"])
    assert value[-1] == zeros_after_point(PLANCK_M) == 34
    calpha = Track(T, 0.0).to(fr["sandSeat"], fr["sandSeat"], 1.0, "step").build()
    assert calpha[fr["sandSeat"] - 1] == 0 and calpha[fr["sandSeat"]] == 1
    ticks = [f_ for f_ in range(1, T) if value[f_] != value[f_ - 1]]
    counter = {"value": [int(v) for v in value], "alpha": [float(a) for a in calpha], "ticks": ticks, "label": LABELS["zeros"]}

    # --- THE WINDOW ------------------------------------------------------------------------------------------------------
    o1, c1, o2, c2 = fr["windowOpen1"], fr["windowClose1"], fr["windowOpen2"], fr["windowClose2"]
    wopen = Track(T, 0.0).to(o1 - 1, o1 - 1 + WO, 1.0, "outquad").to(c1 - 1, c1 - 1 + WC, 0.0).to(o2 - 1, o2 - 1 + WO, 1.0, "outquad").to(c2 - 1, c2 - 1 + WC, 0.0).build()
    for o in (o1, o2):
        assert wopen[o - 1] == 0 and wopen[o] > 0.25, ("the window's first visible frame must be its key frame", o)
    for c in (c1, c2):
        assert wopen[c - 1] == 1 and wopen[c] < 1 and wopen[c - 1 + WC] == 0, ("the window closes from its key frame", c)
    p1, p2 = fr["plateSwap1"], fr["plateSwap2"]
    shut1 = c1 - 1 + WC
    aS1 = Track(T, 1.0).to(p1 - 1, p1 - 1 + XF, 0.0, "linear").build()
    aS2 = Track(T, 0.0).to(p1 - 1, p1 - 1 + XF, 1.0, "linear").to(p2 - 1, p2 - 1 + XF, 0.0, "linear").build()
    aS3 = Track(T, 0.0).to(p2 - 1, p2 - 1 + XF, 1.0, "linear").to(shut1, shut1, 0.0, "step").build()
    aA = Track(T, 0.0).to(o2 - 1, o2 - 1, 1.0, "step").build()
    for p_, a_, b_ in ((p1, aS1, aS2), (p2, aS2, aS3)):
        assert a_[p_ - 1] == 1 and a_[p_] < 1 and b_[p_] > 0, ("the crossfade starts ON its key frame", p_)
        sw = next(f for f in range(p_, p_ + XF + 1) if b_[f] > a_[f])
        assert abs(sw - (p_ - 1 + XF / 2)) <= 1, ("the tag swaps at the crossfade midpoint", sw)
    mp = media["plates"]
    assert media["window"] == WIN
    plates = [
        {"id": "S1", "scene": "sc01", "alpha": [round(float(v), 4) for v in aS1], "push": mp["S1"]["push"], "pushFrom": o1, "pushTo": p1 + XF,
         "tag": LABELS["ai"], "base": mp["S1"]["file"], "placeholder": mp["S1"]["placeholder"]},
        {"id": "S2", "scene": "sc04", "alpha": [round(float(v), 4) for v in aS2], "push": mp["S2"]["push"], "pushFrom": p1, "pushTo": p2 + XF,
         "tag": LABELS["ai"], "base": mp["S2"]["file"], "placeholder": mp["S2"]["placeholder"]},
        {"id": "S3", "scene": "sc05", "alpha": [round(float(v), 4) for v in aS3], "push": mp["S3"]["push"], "pushFrom": p2, "pushTo": shut1,
         "tag": LABELS["ai"], "base": mp["S3"]["file"], "placeholder": mp["S3"]["placeholder"]},
        {"id": "ATOM", "scene": "sc06", "alpha": [round(float(v), 4) for v in aA], "push": [1.0, 1.04], "pushFrom": o2, "pushTo": c2 - 1 + WC,
         "tag": LABELS["drawn"], "base": None, "placeholder": False},
    ]
    window = {"box": WIN, "radius": 22, "frame": 6, "open": [round(float(v), 4) for v in wopen], "plates": plates}
    # claim graphics in the window are gone >= 6 f before the next claim's glide (lessons 42 / 52)
    assert wopen[next_glide(c1) - CLAIM_EXIT_F] == 0, ("window 1 still open at the ATOM glide - 6", next_glide(c1))
    assert wopen[next_glide(c2) - CLAIM_EXIT_F] == 0, ("window 2 still open at the ELECTRON glide - 6", next_glide(c2))

    # --- THE DEVICES -----------------------------------------------------------------------------------------------------
    refs = []
    for rid, Lv, lines, _full, key in REFS:
        a = fr[key]
        draw = Track(T, 0.0).to(a - 6, a, 1.0, "outquad").build()
        assert draw[a] == 1 and draw[a - 1] < 1 and draw[a - 6] == 0, rid
        refs.append({"id": rid, "L": Lv, "lines": lines, "draw": [round(float(v), 4) for v in draw], "at": a})
    eA = Track(T, 0.0).to(fr["electronIn"] - 1, fr["electronIn"] + 7, 1.0, "linear").build()
    assert eA[fr["electronIn"] - 1] == 0 and eA[fr["electronIn"]] > 0
    brk = Track(T, 0.0).to(fr["breakDraw"] - 1, fr["breakDraw"] + 11, 1.0, "outquad").build()
    assert brk[fr["breakDraw"] - 1] == 0 and brk[fr["breakDraw"]] > 0
    pA = Track(T, 0.0).to(fr["planckIn"] - 6, fr["planckIn"], 1.0, "linear").build()
    assert pA[fr["planckIn"]] == 1 and pA[fr["planckIn"] - 1] < 1
    pG = Track(T, 0.0).to(fr["floorGlow"] - 6, fr["floorGlow"], 1.0, "outquad").build()
    assert pG[fr["floorGlow"]] == 1 and pG[fr["floorGlow"] - 1] < 1
    rs, re_ = fr["readoutStart"], fr["readoutEnd"]
    n = len(READOUT_TEXT)
    count = np.zeros(T, dtype=int)
    for f_ in range(rs, T):
        count[f_] = min(n, 1 + (n - 1) * (f_ - rs) // (re_ - rs))
    assert count[rs - 1] == 0 and count[rs] == 1 and count[re_] == n and count[re_ - 1] < n and np.all(np.diff(count) >= 0)
    assert "".join(READOUT_LINES) == READOUT_TEXT and READOUT_TEXT.count("0") == 1 + 34 and READOUT_TEXT.startswith("0." + "0" * 34 + "16")
    rA = Track(T, 0.0).to(rs - 2, rs, 1.0, "linear").build()   # QA A4: the card appears with its first glyph, not 8 f empty
    rmono = advance("IBMPlexMono-normal-500-latin.woff2", READOUT_PX)
    assert READOUT["x0"] + 12 + max(rmono(l) for l in READOUT_LINES) <= 912, ("the readout reaches x >= 912", [rmono(l) for l in READOUT_LINES])
    nA = Track(T, 0.0).to(fr["nucleusPulse"] - SEAT_F, fr["nucleusPulse"], 1.0, "linear").to(c2 - 1, c2 - 1 + WC, 0.0).build()
    assert nA[fr["nucleusPulse"]] == 1 and nA[fr["nucleusPulse"] - SEAT_F] == 0 and nA[next_glide(c2) - CLAIM_EXIT_F] == 0
    nmono = advance("IBMPlexMono-normal-400-latin.woff2", 24)
    assert all(WIN["x0"] + 20 + nmono(l) <= WIN["x1"] - 20 for l in ATOM_NOTE_LINES) and " ".join(ATOM_NOTE_LINES) == ATOM_NOTE
    # the readout card never covers the marker, the Planck line or the ATOM / PROTON chips
    for rid in ("atom", "proton", "virus", "cell", "hair", "sand"):
        x0, x1, y0, y1 = boxes[rid]
        assert x1 <= READOUT["x0"] or y1 <= READOUT["y0"] or y0 >= READOUT["y1"], ("the readout covers a chip", rid)
    assert READOUT["x0"] > RAIL["x"] + 30 and READOUT["y1"] < PLANCK_Y - 40
    devices = {
        "refs": refs,
        "electron": {"alpha": [round(float(v), 4) for v in eA], "name": ELECTRON_NAME, "sub": ELECTRON_SUB, "subSeat": fr["noSize"]},
        "brk": [round(float(v), 4) for v in brk],
        "planck": {"y": PLANCK_Y, "alpha": [round(float(v), 4) for v in pA], "glow": [round(float(v), 4) for v in pG], "label": PLANCK_LABEL,
                   "floor": FLOOR_LABEL, "floorSeat": fr["floorGlow"]},
        "readout": {"count": [int(v) for v in count], "alpha": [round(float(v), 4) for v in rA], "text": READOUT_TEXT, "lines": READOUT_LINES},
        "atomNote": {"lines": ATOM_NOTE_LINES, "seat": fr["nucleusPulse"], "alpha": [round(float(v), 4) for v in nA], "pulse": fr["nucleusPulse"]},
    }

    # theme.ts must equal these numbers
    theme = (P / "theme.ts").read_text()
    assert re.search(r"rail:\s*\{\s*x:\s*250,\s*y0:\s*380,\s*y1:\s*1000,\s*L0:\s*3,\s*L1:\s*18,\s*ppd:\s*620 / 15", theme), "theme.ts L.rail stale"
    assert re.search(r"planckY:\s*%d" % PLANCK_Y, theme) and re.search(r"labelX:\s*%d" % LABEL_X, theme), "theme.ts L.rail stale"
    for name, d_ in (("win", WIN), ("counter", COUNTER), ("readout", READOUT)):
        m = re.search(name + r":\s*\{\s*x0:\s*(\d+),\s*x1:\s*(\d+),\s*y0:\s*(\d+),\s*y1:\s*(\d+)", theme)
        assert m and [int(v) for v in m.groups()] == [d_[k] for k in ("x0", "x1", "y0", "y1")], f"theme.ts L.{name} stale"
    m = re.search(r"electron:\s*\{\s*x:\s*(\d+),\s*nameY:\s*(\d+),\s*subY:\s*(\d+)", theme)
    assert m and [int(v) for v in m.groups()] == [ELECTRON["x"], ELECTRON["nameY"], ELECTRON["subY"]], "theme.ts L.electron stale"

    # --- placards (root rail) ----------------------------------------------------------------------------------------------
    bc = {px: advance("SairaCondensed-normal-600-latin.woff2", px) for px in set(PLACARD_SIZES + FINE_SIZES)}
    starts = sorted(p["startFrame"] for p in out_pages)
    placards = []
    for pl in plan["metadata"]["placards"]:
        key, line, fine = pl["scenes"], pl["text"], pl.get("fine_print")
        first, last = PLACARD_SCENES[key]
        enter = sc[first]["from"] + 2
        for ps_ in starts:
            if ps_ <= enter < ps_ + PLACARD_PAGE_GUARD_F:
                enter = ps_ + PLACARD_PAGE_GUARD_F
        if last != order[-1]:
            nfrom = sc[order[order.index(last) + 1]]["from"]
            exit_ = min(nfrom - 8, next_glide(nfrom - 8) - CLAIM_EXIT_F)
        else:
            exit_ = min(rel - 14, next_glide(rel - 20) - CLAIM_EXIT_F)
        assert exit_ <= next_glide(exit_ - 1) - CLAIM_EXIT_F, ("placard exits < 6 f before the next glide", line)
        assert exit_ - enter >= PLACARD_MIN_F, ("placard held < 1.2 s", line, enter, exit_)
        size = next((px for px in PLACARD_SIZES if bc[px](line) <= PLACARD_TEXT_W), None)
        assert size, ("placard line too long", line)
        fsize = next((px for px in FINE_SIZES if bc[px](fine) <= PLACARD_TEXT_W), None) if fine else None
        assert fine is None or fsize, ("fine print too long at >= 24 px (lesson 31)", fine)
        assert size * 1.15 + (fsize * 1.15 + 2 if fine else 0) <= 80 - 6, ("placard rows overflow the 80 px rail", line)
        placards.append({"enter": enter, "exit": exit_, "line": line, "lines": [line], "size": size, "w": round(bc[size](line), 1),
                         "fine": fine, "fineSize": fsize, "fineW": round(bc[fsize](fine), 1) if fine else None, "anchor": key})
        assert 140 + 28 + placards[-1]["w"] <= 912 and (not fine or 140 + 28 + placards[-1]["fineW"] <= 912), ("placard reaches x >= 912", placards[-1])
    assert [p["anchor"] for p in placards] == list(PLACARD_SCENES)
    for a, b in zip(placards, placards[1:]):
        assert a["exit"] <= b["enter"], (a, b)
    brief = json.dumps(json.loads((P / "artifacts/research_brief.json").read_text())).lower()
    for src in ("wentworth", "ncbi", "abbe", "codata", "planck"):
        assert src in brief, ("placard source not in the research brief (lesson 32)", src)

    # --- strings: verified / forbidden (lessons 20, 32) ---------------------------------------------------------------------
    verified = set(plan["metadata"]["verified_on_screen_strings"])
    forbidden = [f.split(" (")[0].lower() for f in plan["metadata"]["forbidden_on_screen"]]
    root_strings = list(LABELS.values()) + [CTA_TEXT, ELECTRON_NAME, ELECTRON_SUB, PLANCK_LABEL, FLOOR_LABEL, READOUT_TEXT, ATOM_NOTE] \
        + ATOM_NOTE_LINES + [ln for r in rungs for ln in r["lines"]] + [ln for r in REFS for ln in r[2]] + [r[3] for r in REFS] + DECADES \
        + [str(v) for v in sorted(set(value.tolist()))]
    for s_ in root_strings:
        assert any(s_ in v for v in verified), ("root string not in verified_on_screen_strings (lesson 20)", s_)
    lit = set()
    for f in sorted((P / "scenes").glob("u*/*.ts*")):
        src = f.read_text()
        lit |= set(re.findall(r'text(?:=|:\s*)\{?"([^"]+)"', src))
        lit |= set(re.findall(r'(?:TEXT|LINE|LABEL|NUM)\w*\s*=\s*"([^"]+)"', src))
        for old in ("km/h", "cheetah", "falcon", "LHC", "YouTag", "Orbit", "Beam", "Energy", "Nines", "MassLabel"):
            assert old not in src, ("a video-16 device / string is left in a scene", f.name, old)
    bad = sorted(t_ for t_ in lit if not any(t_ in v for v in verified))
    assert not bad, ("on-screen literals not in verified_on_screen_strings (lesson 20)", bad)
    placard_text = " ".join(p["line"] + " " + (p["fine"] or "") for p in placards)
    allscreen = " ".join(sorted(verified | lit | set(root_strings))).lower() + " " + placard_text.lower()
    assert not [f for f in forbidden if f in allscreen], ("forbidden_on_screen string on screen", [f for f in forbidden if f in allscreen])
    print("verified on-screen literals in scenes:", len(lit))

    # --- the settle is STILL (lesson 25) ------------------------------------------------------------------------------------
    chans = {"ladder.markerL": markerL, "ladder.vis": vis, "ladder.railDraw": rail_draw, "ladder.veil": veil, "counter": value.astype(float),
             "counter.alpha": calpha, "window.open": wopen, "S1": aS1, "S2": aS2, "S3": aS3, "ATOM": aA, "electron": eA, "brk": brk,
             "planck.alpha": pA, "planck.glow": pG, "readout.count": count.astype(float), "readout.alpha": rA, "atomNote": nA}
    for r in refs:
        chans["ref." + r["id"]] = np.array(r["draw"])
    for name, arr in chans.items():
        assert np.all(np.abs(arr[rel:] - arr[rel]) < 1e-9), ("the settle must be still", name)
    assert wopen[rel] == 0 and placards[-1]["exit"] <= rel and fr["ctaFrame"] == rel

    r4 = lambda a: [round(float(v), 4) for v in a]
    for r in rungs:
        r.pop("_desc")
    props = {
        "timeline": {
            "fps": FPS, "width": 1080, "height": 1920, "total_frames": total, "lead_frames": round(tl["lead_seconds"] * FPS),
            "sections": [{"id": s["id"], "from": s["from"], "durationInFrames": s["durationInFrames"]} for s in tl["sections"]],
            "scenes": [{"id": s["id"], "section": s["section"], "from": s["from"], "durationInFrames": s["durationInFrames"]} for s in tl["scenes"]],
            "words": [{"section": w["section"], "text": w["text"], "f0": w["f0"], "f1": w["f1"]} for w in words],
        },
        "captionPages": [{k: v for k, v in p.items() if k != "text"} for p in out_pages],
        "meter": meter,
        "ladder": {"markerL": [round(float(v), 5) for v in markerL], "markerVis": r4(vis), "railDraw": r4(rail_draw), "veil": r4(veil),
                   "rungs": rungs, "markerR": MARKER_R, "notes": ladder_notes},
        "devices": devices,
        "counter": counter,
        "window": window,
        "placards": placards,
        "labels": LABELS,
        "cta": {"text": CTA_TEXT, "lines": CTA_LINES, "frame": fr["ctaFrame"]},
        "settle": {"from": rel, "freezeFrom": rel, "chordFrame": fr["chordFrame"]},
        "freezes": [],
        "audio": {"soundtrack": "audio/soundtrack.wav", **fr},
        "motion": mo,
        "layers": "all",
        "exportVariant": "main",
    }
    assert {k: v for k, v in props["audio"].items() if k != "soundtrack"} == fr, "props.audio != soundtrack frames"

    for pg in out_pages:
        lines = {}
        for w in pg["words"]:
            lines.setdefault(w["line"], []).append(w["text"])
        print(f'{pg["startFrame"]:5d}-{pg["exitFrame"]:5d} {pg["section"]} | ' + " / ".join(" ".join(v) for v in lines.values()))
    for k in meter:
        print(f'meter {k["glideStart"]:5d}->{k["frame"]:5d} {k["state"]:<9}{" (pulse)" if k["repeat"] else "        "} {k["anchor"]}')
    print("placards:", [(p["enter"], p["exit"], p["size"], p["fineSize"], p["line"][:30]) for p in placards])
    print("chips:", {k: [round(v) for v in b] for k, b in boxes.items()})
    print("counter steps:", [(f_, int(value[f_])) for f_ in ticks])
    if check:
        return
    (P / "artifacts/props.json").write_text(json.dumps(props, ensure_ascii=False, separators=(",", ":")))
    ts = ("// GENERATED by build_props.py from artifacts/props.json - do not edit by hand.\n"
          "import type { ScaleProps } from \"./types\";\n\n"
          f"export const DEFAULT_PROPS: ScaleProps = {json.dumps(props, ensure_ascii=False, separators=(',', ':'))};\n")
    (P / "props.generated.ts").write_text(ts)
    print("wrote artifacts/props.json and props.generated.ts")


if __name__ == "__main__":
    main()
