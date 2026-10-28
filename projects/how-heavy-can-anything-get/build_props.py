#!/usr/bin/env python3
"""Build artifacts/props.json + props.generated.ts from the measured timeline (run from the repo root).

    python3 projects/how-heavy-can-anything-get/build_props.py          # write
    python3 projects/how-heavy-can-anything-get/build_props.py --check  # print pages + schedules only

Video 18 "How Heavy Can Anything Get?" / the WEIGHT COLUMN. Copied from projects/how-small-can-anything-get/build_props.py
(video 17, QA passed) and flipped back up: the log ladder climbs in kilograms (L = log10(kg)). Inputs: artifacts/timeline.json
(aligned words, sections, scene windows), artifacts/scene_plan.json (caption pages, placards, verified / forbidden strings:
written by sync_scene_plan.py), artifacts/soundtrack_report.json (key frames + motion constants: build_soundtrack.py owns K,
asserted == build_soundtrack.key_frames(timeline)), artifacts/media_report.json (the window plates). Everything out is ABSOLUTE.

Caption pages: scene_plan.metadata.captions.pages (<= 2 lines / <= 6 words, every claim starts its own page, no 2-word
orphan; asserted to cover the narration word for word); the line break is chosen with Bricolage Grotesque 800 @ 58 px
advance widths against a 700 px budget. Exit = 4 f after the page's last word ends (held >= 36 f when the next page allows),
clipped / butted to the next page (lesson 6). The CTA takes the slab ON ctaFrame.

Honesty meter (lesson 3: keyed to the START of the caption page carrying the claim; consecutive pages of one claim merge; a
new claim of the same grade pulses): YOU MEASURED; WHALE PROBABLY; EIFFEL MEASURED; ALL HUMANS PROBABLY; EARTH, SUN, NEUTRON
STAR, SGR A* MEASURED; UNIVERSE and DARK MATTER PROBABLY from 'All the ordinary matter' to the end; IDLE at the CTA.

THE LADDER: props.ladder.markerL climbs rung by rung on eased moves whose FIRST MOVING FRAME is climb* and which END ON *Seat
(asserted); the marker stays put for NEUTRON STAR and dims to a ghost from universeIn (lesson 60); rung chips seat on their
seats with their numbers (Ladder.tsx, T.seat); props.counter (ZEROS = the power of ten of the active rung's kilograms, asserted
on every seat; steps ON every *Ticks frame; 11 -> 24 accelerating across earthTicks, 36 -> 53 across spinTicks); props.window
(S1 whale -> S2 Eiffel Tower, S3 neutron star, the drawn black hole + Mercury's orbit); props.devices (the orbit, the break, the
universe line, the linear ordinary / dark matter bars). Asserted: chips never sit under the open window and never overlap each
other; claim graphics (window states, the orbit note) are gone >= 6 f before the next tab glide; placards exit >= 6 f before
the next glide; every channel is constant from the release (lesson 25); a literal scan of scenes/u*/ against
verified_on_screen_strings / forbidden_on_screen (lesson 20).
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

P = Path("projects/how-heavy-can-anything-get")
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
CTA_TEXT = "What's the heaviest thing you've ever lifted?"
CTA_LINES = ["What's the heaviest thing", "you've ever lifted?"]
CTA_PX = 52
CLAIMS = {   # first words of a page -> (claim id, state); a page belongs to the claim of the last key at or before it
    ("s1", "You weigh about seventy kilograms."): ("YOU", "MEASURED"),
    ("s1", "A blue whale can reach"): ("WHALE", "PROBABLY"),
    ("s1", "The Eiffel Tower, about ten million."): ("EIFFEL", "MEASURED"),
    ("s2", "Every human alive, put together:"): ("ALL HUMANS", "PROBABLY"),
    ("s2", "The whole Earth: six trillion trillion."): ("EARTH", "MEASURED"),
    ("s3", "The Sun outweighs"): ("SUN", "MEASURED"),
    ("s3", "And a neutron star squeezes"): ("NEUTRON STAR", "MEASURED"),
    ("s4", "The black hole at the centre"): ("SGR A*", "MEASURED"),
    ("s5", "All the ordinary matter"): ("UNIVERSE", "PROBABLY"),
    ("s5", "And dark matter outweighs it"): ("DARK MATTER", "PROBABLY"),
}
WEAK_END = {"a", "an", "the", "to", "of", "and", "is", "in", "it", "at", "as", "its", "by", "for", "if", "so", "with", "on", "no", "any", "that", "can", "we"}
BOUND = {("blue", "whale"), ("a", "hundred"), ("hundred", "and"), ("and", "fifty"), ("fifty", "thousand"), ("eiffel", "tower"), ("ten", "million"),
         ("human", "alive"), ("put", "together"), ("four", "hundred"), ("hundred", "billion"), ("whole", "earth"), ("six", "trillion"),
         ("trillion", "trillion"), ("the", "sun"), ("three", "hundred"), ("and", "thirty"), ("thirty", "thousand"), ("thousand", "earths"),
         ("neutron", "star"), ("a", "ball"), ("a", "city"), ("black", "hole"), ("the", "centre"), ("our", "galaxy"), ("four", "million"),
         ("million", "suns"), ("mercurys", "orbit"), ("ordinary", "matter"), ("fiftythree", "zeros"), ("dark", "matter"), ("of", "kilograms")}
PLACARD_SCENES = {"sc01-sc03": ("sc01", "sc03"), "sc04-sc05": ("sc04", "sc05"), "sc06-sc07": ("sc06", "sc07"), "sc08-sc09": ("sc08", "sc09"),
                  "sc10-sc12": ("sc10", "sc12")}
# THE LADDER (mirrored in theme.ts L; asserted against it)
RAIL = {"x": 250, "y0": 380, "y1": 1000, "L0": 0, "L1": 37}
PPD = (RAIL["y1"] - RAIL["y0"]) / (RAIL["L1"] - RAIL["L0"])
WIN = {"x0": 580, "x1": 920, "y0": 440, "y1": 893}
COUNTER = {"x0": 640, "x1": 920, "y0": 220, "y1": 340}
UNIVERSE = {"x0": 120, "x1": 620, "y": 280, "labelX": 100, "labelY": 214}
BARS = {"x0": 584, "x1": 912, "base": 1060, "ordX0": 604, "ordX1": 704, "darkX0": 800, "darkX1": 900, "ordH": 110}
BREAK = (345, 370)
LABEL_X = 280
CHIP_MAX_RIGHT = WIN["x0"] - 8
MARKER_R = 7
NAME_PX, NUM_PX = 28, 26
ROW_H, CHIP_PAD, CHIP_GAP = 30, 12, 6
# (id, name, number string, kg, L as placed by the brief, seat key, climb key)
RUNGS = [
    ("you", "YOU", "~70 kg", 70, 1.85, "youSeat", None),
    ("whale", "BLUE WHALE", "up to ~150,000 kg", 1.5e5, 5.18, "whaleSeat", "climbWhale"),
    ("eiffel", "EIFFEL TOWER", "~10 million kg", 1.0e7, 7.00, "eiffelSeat", "climbEiffel"),
    ("humans", "ALL HUMANS", "~400 billion kg", 4e11, 11.6, "humansSeat", "climbHumans"),
    ("earth", "EARTH", "6 × 10²⁴ kg", 6e24, 24.78, "earthSeat", "climbEarth"),
    ("sun", "SUN", "2 × 10³⁰ kg", 2e30, 30.30, "sunSeat", "climbSun"),
    ("neutron", "NEUTRON STAR", "~1.4 Suns, ~20 km wide", 2.8e30, 30.44, "neutronSeat", None),
    ("sgra", "SGR A*", "4 million Suns", 8e36, 36.9, "sgraSeat", "climbSgra"),
]
UNIVERSE_KG = 1.5e53
SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
DECADES = [f"10{str(n).translate(SUP)} kg" for n in range(RAIL["L0"], RAIL["L1"] + 1, 3)]
LABELS = {"axis": "kilograms · log scale", "zeros": "ZEROS", "ai": "AI impression", "drawn": "drawn · not to scale"}
UNIVERSE_LINES = ["OBSERVABLE UNIVERSE · ~10⁵³ kg", "(ordinary matter)"]
UNIVERSE_FULL = "OBSERVABLE UNIVERSE · ~10⁵³ kg (ordinary matter)"
ORBIT_LABEL = "Mercury's orbit"
HORIZON_KM, ORBIT_KM = 24e6, 116e6          # Sgr A*'s horizon diameter vs Mercury's orbit diameter (the brief)
BAR_LABELS = {"ord": "ordinary matter", "dark": "DARK MATTER", "ratio": "~5 : 1 · inferred", "tag": "drawn"}
DARK_RATIO = 5.4
# the counter's step offsets (frames after the first tick) for the two accelerating runs; every *Ticks frame is a step
EARTH_OFFSETS = [0, 7, 14, 19, 23, 26, 28, 30, 32, 33, 34, 35, 36]            # 12 .. 24 (gaps 7,7,5,4,3,2,2,2,1,1,1,1)
SPIN_OFFSETS = [0, 4, 7, 10, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]  # 37 .. 53 (gaps 4,3,3,2,2,1 ...)

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
    return RAIL["y1"] - (Lv - RAIL["L0"]) * PPD


def power_of_ten(kg: float) -> int:
    return math.floor(math.log10(kg) + 1e-9)


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
    assert mkey["WHALE"]["state"] == "PROBABLY" and mkey["ALL HUMANS"]["state"] == "PROBABLY" and mkey["UNIVERSE"]["state"] == "PROBABLY"
    assert mkey["DARK MATTER"]["state"] == "PROBABLY" and meter[-2]["claim"] == "DARK MATTER" and mkey["DARK MATTER"]["repeat"]
    glides = [k["glideStart"] for k in meter[1:]]
    next_glide = lambda f: min(g for g in glides if g > f)

    # --- THE LADDER: rungs + the marker -----------------------------------------------------------------------------------
    saira = advance("SairaCondensed-normal-700-latin.woff2", NAME_PX)
    mono = advance("IBMPlexMono-normal-500-latin.woff2", NUM_PX)
    fits = lambda w: LABEL_X + w + 2 * CHIP_PAD <= CHIP_MAX_RIGHT
    rungs = []
    for rid, name, num, kg, Lv, seatk, climbk in RUNGS:
        assert abs(Lv - math.log10(kg)) < 0.06, ("the rung's L is not log10(kg)", rid)
        if fits(saira(name) + saira(" · ") + mono(num)):
            lines = [f"{name} · {num}"]
        elif fits(mono(num)):
            lines = [name, num]
        else:
            k = num.index(", ") + 1
            lines = [name, num[:k], num[k + 1:]]
            assert all(fits(mono(l)) for l in lines[1:]), ("a rung number does not fit beside the window even split", rid)
        rungs.append({"id": rid, "name": name, "num": num, "lines": lines, "kg": kg, "L": Lv, "seat": fr[seatk], "_climb": climbk})
    Lof = {r["id"]: r["L"] for r in rungs}
    mk = Track(T, Lof["you"])
    for r in rungs[1:]:
        if r["_climb"]:
            mk.to(fr[r["_climb"]] - 1, r["seat"], r["L"], "sine")
    markerL = mk.build()
    for r in rungs[1:]:
        s_ = r["seat"]
        if r["_climb"]:
            c = fr[r["_climb"]]
            assert markerL[c - 1] == markerL[c - 2] and markerL[c] > markerL[c - 1], ("the climb's first moving frame must be its key frame", r["id"])
            assert markerL[s_] == r["L"] and markerL[s_ - 1] < r["L"], ("the climb must land ON the seat", r["id"])
            assert fr[r["_climb"]] + mo["CLIMB_F"] == s_, ("climb length != CLIMB_F", r["id"])
    assert np.all(np.diff(markerL) >= 0), "the marker only climbs"
    assert np.all(markerL[fr["sunSeat"]:fr["climbSgra"]] == Lof["sun"]), "the marker does not move for the neutron star"
    assert markerL[fr["sgraSeat"]:].max() == markerL[fr["sgraSeat"]:].min() == Lof["sgra"], "the marker does not move from SGR A* (the universe is off the rail)"
    # lesson 60: from universeIn the story leaves the rungs; the marker stays but dims to a ghost
    U = fr["universeIn"]
    vis = Track(T, 1.0).to(U, U + 12, 0.3, "sine").build()
    assert vis[U] == 1.0 and vis[U + 1] < 1 and abs(vis[-1] - 0.3) < 1e-6
    rail_draw = Track(T, 0.0).to(fr["railDraw"] - 1, fr["railDraw"] + 15, 1.0, "outquad").build()
    assert rail_draw[fr["railDraw"] - 1] == 0 and rail_draw[fr["railDraw"]] > 0

    # chip boxes as Ladder.tsx lays them (bottom-up de-overlap); widths from the faces' advances
    def chip_w(r) -> float:
        ws = []
        for l in r["lines"]:
            if l.startswith(r["name"] + " · "):
                ws.append(saira(r["name"]) + saira(" · ") + mono(l[len(r["name"]) + 3:]))
            else:
                ws.append(saira(l) if l == r["name"] else mono(l))
        return max(ws) + 2 * CHIP_PAD
    boxes, prev_top = {}, 1e9
    for r in sorted(rungs, key=lambda r: -rail_y(r["L"])):
        h = len(r["lines"]) * ROW_H + 8
        cy = min(rail_y(r["L"]), prev_top - CHIP_GAP - h / 2)
        boxes[r["id"]] = (LABEL_X, LABEL_X + chip_w(r), cy - h / 2, cy + h / 2)
        prev_top = cy - h / 2
    for r in rungs:
        x0, x1, y0, y1 = boxes[r["id"]]
        assert x1 <= CHIP_MAX_RIGHT, ("a rung chip would reach under the window", r["id"], round(x1))
        assert y0 >= UNIVERSE["y"] + 8, ("a chip reaches the universe line", r["id"], round(y0))
        assert y1 <= 1000 + 30, ("a chip falls below the rail", r["id"])
    ids = [r["id"] for r in rungs]
    for i, a_ in enumerate(ids):
        for b_ in ids[i + 1:]:
            A, B = boxes[a_], boxes[b_]
            assert A[3] + CHIP_GAP - 0.01 <= B[2] or B[3] + CHIP_GAP - 0.01 <= A[2], ("chips overlap", a_, b_)
    # chips seat in climbing order, so a new chip never shoves a seated one (bottom-up de-overlap keeps the lower chips put)
    assert [r["seat"] for r in sorted(rungs, key=lambda r: -rail_y(r["L"]))] == sorted(r["seat"] for r in rungs)
    # the marker (r 7, glow 3x) never covers a label: chips start at x 280, powers end at x 224
    assert RAIL["x"] + 3 * MARKER_R < LABEL_X and RAIL["x"] - 3 * MARKER_R > 224
    ladder_notes = "y(L) = 1000 - L * 620 / 37, L = log10(kg) (no camera); chips de-overlapped bottom-up (Ladder.tsx, mirrored here)"

    # --- THE COUNTER (ZEROS = the power of ten) ---------------------------------------------------------------------------
    value = np.zeros(T, dtype=int)
    steps = [(fr["youSeat"], 1)]
    steps += [(f_, 2 + i) for i, f_ in enumerate(fr["whaleTicks"])] + [(f_, 6 + i) for i, f_ in enumerate(fr["eiffelTicks"])]
    steps += [(f_, 8 + i) for i, f_ in enumerate(fr["humansTicks"])]
    et = fr["earthTicks"]
    assert set(et) <= {et[0] + o for o in EARTH_OFFSETS} and et[-1] == et[0] + EARTH_OFFSETS[-1] and len(EARTH_OFFSETS) == 24 - 11
    steps += [(et[0] + o, 12 + i) for i, o in enumerate(EARTH_OFFSETS)]
    steps += [(f_, 25 + i) for i, f_ in enumerate(fr["sunTicks"])] + [(f_, 31 + i) for i, f_ in enumerate(fr["sgraTicks"])]
    st = fr["spinTicks"]
    assert st[0] == fr["spinStart"] and st[-1] == fr["spinEnd"] and set(st) <= {st[0] + o for o in SPIN_OFFSETS}
    assert SPIN_OFFSETS[-1] == fr["spinEnd"] - fr["spinStart"] and len(SPIN_OFFSETS) == 53 - 36
    steps += [(st[0] + o, 37 + i) for i, o in enumerate(SPIN_OFFSETS)]
    for f_, v_ in steps:
        value[f_:] = v_
    for offs in (EARTH_OFFSETS, SPIN_OFFSETS):
        gaps = np.diff(offs)
        assert np.all(np.diff(gaps) <= 0) and gaps[0] > gaps[-1], ("the run must accelerate", gaps)
    for f_ in fr["youTicks"] + fr["whaleTicks"] + fr["eiffelTicks"] + fr["humansTicks"] + et + fr["sunTicks"] + fr["sgraTicks"] + st:
        assert value[f_] > value[f_ - 1], ("the counter must step ON every tick", f_)
    for r in rungs:
        assert value[r["seat"]] == power_of_ten(r["kg"]), ("counter != the rung's power of ten ON its seat", r["id"])
        if r["id"] != "neutron":
            assert value[r["seat"] - 1] < value[r["seat"]], ("counter must step ON the seat", r["id"])
    assert value[fr["neutronSeat"]] == value[fr["sunSeat"]] == 30
    assert value[fr["spinEnd"]] == value[-1] == power_of_ten(UNIVERSE_KG) == 53 and value[fr["spinEnd"] - 1] == 52
    assert value[et[-1]] == 24 and value[et[0] - 1] == 11 and value[st[0] - 1] == 36
    calpha = Track(T, 0.0).to(fr["youSeat"], fr["youSeat"], 1.0, "step").build()
    assert calpha[fr["youSeat"] - 1] == 0 and calpha[fr["youSeat"]] == 1
    ticks = [f_ for f_ in range(1, T) if value[f_] != value[f_ - 1]]
    counter = {"value": [int(v) for v in value], "alpha": [float(a) for a in calpha], "ticks": ticks, "label": LABELS["zeros"]}

    # --- THE WINDOW ------------------------------------------------------------------------------------------------------
    o1, c1, o2, c2, o3, c3 = fr["windowOpen1"], fr["windowClose1"], fr["windowOpen2"], fr["windowClose2"], fr["windowOpen3"], fr["windowClose3"]
    wt = Track(T, 0.0)
    for o, c in ((o1, c1), (o2, c2), (o3, c3)):
        wt.to(o - 1, o - 1 + WO, 1.0, "outquad").to(c - 1, c - 1 + WC, 0.0)
    wopen = wt.build()
    for o in (o1, o2, o3):
        assert wopen[o - 1] == 0 and wopen[o] > 0.25, ("the window's first visible frame must be its key frame", o)
    for c in (c1, c2, c3):
        assert wopen[c - 1] == 1 and wopen[c] < 1 and wopen[c - 1 + WC] == 0, ("the window closes from its key frame", c)
    p1 = fr["plateSwap"]
    shut1, shut2 = c1 - 1 + WC, c2 - 1 + WC
    aS1 = Track(T, 1.0).to(p1 - 1, p1 - 1 + XF, 0.0, "linear").build()
    aS2 = Track(T, 0.0).to(p1 - 1, p1 - 1 + XF, 1.0, "linear").to(shut1, shut1, 0.0, "step").build()
    aS3 = Track(T, 0.0).to(o2 - 1, o2 - 1, 1.0, "step").to(shut2, shut2, 0.0, "step").build()
    aB = Track(T, 0.0).to(o3 - 1, o3 - 1, 1.0, "step").build()
    assert aS1[p1 - 1] == 1 and aS1[p1] < 1 and aS2[p1] > 0, ("the crossfade starts ON its key frame", p1)
    sw = next(f for f in range(p1, p1 + XF + 1) if aS2[f] > aS1[f])
    assert abs(sw - (p1 - 1 + XF / 2)) <= 1, ("the tag swaps at the crossfade midpoint", sw)
    mp = media["plates"]
    assert media["window"] == WIN
    plates = [
        {"id": "S1", "scene": "sc02", "alpha": [round(float(v), 4) for v in aS1], "push": mp["S1"]["push"], "pushFrom": o1, "pushTo": p1 + XF,
         "tag": LABELS["ai"], "base": mp["S1"]["file"], "placeholder": mp["S1"]["placeholder"]},
        {"id": "S2", "scene": "sc03", "alpha": [round(float(v), 4) for v in aS2], "push": mp["S2"]["push"], "pushFrom": p1, "pushTo": shut1,
         "tag": LABELS["ai"], "base": mp["S2"]["file"], "placeholder": mp["S2"]["placeholder"]},
        {"id": "S3", "scene": "sc07", "alpha": [round(float(v), 4) for v in aS3], "push": mp["S3"]["push"], "pushFrom": o2, "pushTo": shut2,
         "tag": LABELS["ai"], "base": mp["S3"]["file"], "placeholder": mp["S3"]["placeholder"]},
        {"id": "BH", "scene": "sc08", "alpha": [round(float(v), 4) for v in aB], "push": [1.0, 1.03], "pushFrom": o3, "pushTo": c3 - 1 + WC,
         "tag": LABELS["drawn"], "base": None, "placeholder": False},
    ]
    window = {"box": WIN, "radius": 22, "frame": 6, "open": [round(float(v), 4) for v in wopen], "plates": plates}
    # claim graphics in the window are gone >= 6 f before the next claim's glide (lessons 42 / 52)
    for c in (c1, c2, c3):
        assert wopen[next_glide(c) - CLAIM_EXIT_F] == 0, ("the window still open at the next glide - 6", c, next_glide(c))

    # --- THE DEVICES -----------------------------------------------------------------------------------------------------
    od = fr["orbitDraw"]
    oD = Track(T, 0.0).to(od - 1, od + 11, 1.0, "outquad").build()
    assert oD[od - 1] == 0 and oD[od] > 0 and oD[od + 11] == 1
    orbit_seat = od + 12
    horizon = HORIZON_KM / ORBIT_KM
    assert 0.18 <= horizon <= 0.22, "the horizon is about 1/5 of Mercury's orbit across"
    assert orbit_seat < c3 and wopen[next_glide(c3) - CLAIM_EXIT_F] == 0
    brk = Track(T, 0.0).to(fr["breakDraw"] - 1, fr["breakDraw"] + 11, 1.0, "outquad").build()
    assert brk[fr["breakDraw"] - 1] == 0 and brk[fr["breakDraw"]] > 0
    uA = Track(T, 0.0).to(U - 1, U + 5, 1.0, "linear").build()
    assert uA[U - 1] == 0 and uA[U] > 0
    ordA = Track(T, 0.0).to(U - 1, U + 5, 1.0, "linear").build()
    dr, ds = fr["darkRise"], fr["darkSeat"]
    rise = Track(T, 0.0).to(dr - 1, ds, 1.0, "out").build()
    assert rise[dr - 1] == 0 and rise[dr] > 0 and rise[ds] == 1 and rise[ds - 1] < 1, "the dark bar lands ON darkSeat"
    assert abs(DARK_RATIO - 5.4) < 1e-9
    dark_top = BARS["base"] - BARS["ordH"] * DARK_RATIO
    assert dark_top - 40 >= COUNTER["y1"] + 20 and BARS["x1"] <= 912 and BARS["darkX1"] <= 912, ("the dark bar + its label leave the column", dark_top)
    assert wopen[U - 1] == 0, "the bars live in the closed window's column"
    lab24 = advance("IBMPlexMono-normal-500-latin.woff2", 24)
    lab30 = advance("IBMPlexMono-normal-500-latin.woff2", 30)
    dsp30 = advance("SairaCondensed-normal-700-latin.woff2", 30)
    assert BARS["ordX0"] - 16 + lab24(BAR_LABELS["ord"]) <= 912
    assert BARS["ordX0"] - 16 + max(lab30(BAR_LABELS["ratio"].split(" · ")[0]), lab24(BAR_LABELS["ratio"].split(" · ")[1])) <= BARS["darkX0"] - 10, "the ratio label sits clear of the dark bar"
    assert BARS["x1"] - dsp30(BAR_LABELS["dark"]) >= BARS["ordX1"], "'DARK MATTER' sits clear of the ordinary bar column"
    ud = advance("SairaCondensed-normal-700-latin.woff2", 28)
    um = advance("IBMPlexMono-normal-500-latin.woff2", 26)
    nm, val = UNIVERSE_LINES[0].split(" · ")
    assert UNIVERSE["labelX"] + ud(nm + " · ") + um(val) <= COUNTER["x0"] - 16, "the universe label runs into the counter"
    assert UNIVERSE["labelY"] >= 192 and UNIVERSE["labelY"] + 60 <= UNIVERSE["y"] - 4
    assert BREAK[1] < RAIL["y0"] and BREAK[0] > UNIVERSE["y"]
    devices = {
        "orbit": {"draw": [round(float(v), 4) for v in oD], "label": ORBIT_LABEL, "labelSeat": orbit_seat, "horizon": round(horizon, 4)},
        "brk": [round(float(v), 4) for v in brk],
        "universe": {"alpha": [round(float(v), 4) for v in uA], "lines": UNIVERSE_LINES},
        "bars": {"ordAlpha": [round(float(v), 4) for v in ordA], "rise": [round(float(v), 5) for v in rise], "ratio": DARK_RATIO, "ordLabel": BAR_LABELS["ord"],
                 "darkLabel": BAR_LABELS["dark"], "ratioLabel": BAR_LABELS["ratio"], "tag": BAR_LABELS["tag"], "seat": ds},
    }

    # theme.ts must equal these numbers
    theme = (P / "theme.ts").read_text()
    assert re.search(r"rail:\s*\{\s*x:\s*250,\s*y0:\s*380,\s*y1:\s*1000,\s*L0:\s*0,\s*L1:\s*37,\s*ppd:\s*620 / 37", theme), "theme.ts L.rail stale"
    assert re.search(r"labelX:\s*%d" % LABEL_X, theme) and re.search(r"breakY0:\s*%d,\s*breakY1:\s*%d" % BREAK, theme), "theme.ts L.rail stale"
    for name, d_ in (("win", WIN), ("counter", COUNTER)):
        m = re.search(name + r":\s*\{\s*x0:\s*(\d+),\s*x1:\s*(\d+),\s*y0:\s*(\d+),\s*y1:\s*(\d+)", theme)
        assert m and [int(v) for v in m.groups()] == [d_[k] for k in ("x0", "x1", "y0", "y1")], f"theme.ts L.{name} stale"
    m = re.search(r"universe:\s*\{\s*x0:\s*(\d+),\s*x1:\s*(\d+),\s*y:\s*(\d+),\s*labelX:\s*(\d+),\s*labelY:\s*(\d+)", theme)
    assert m and [int(v) for v in m.groups()] == list(UNIVERSE.values()), "theme.ts L.universe stale"
    m = re.search(r"bars:\s*\{([^}]*)\}", theme)
    assert m and dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).split(",") if kv.strip())) == BARS, "theme.ts L.bars stale"

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
    for src in ("toureiffel", "noaa", "nasa", "eht", "planck"):
        assert src in brief, ("placard source not in the research brief (lesson 32)", src)

    # --- strings: verified / forbidden (lessons 20, 32) ---------------------------------------------------------------------
    verified = set(plan["metadata"]["verified_on_screen_strings"])
    forbidden = [f.split(" (")[0].lower() for f in plan["metadata"]["forbidden_on_screen"]]
    root_strings = list(LABELS.values()) + [CTA_TEXT, UNIVERSE_FULL, ORBIT_LABEL] + list(BAR_LABELS.values()) \
        + [r["name"] + " · " + r["num"] for r in rungs] + DECADES + [str(v) for v in sorted(set(value.tolist()))]
    for s_ in root_strings:
        assert any(s_ in v for v in verified), ("root string not in verified_on_screen_strings (lesson 20)", s_)
    for r in rungs:
        assert all(l in r["name"] + " · " + r["num"] or l in r["num"] for l in r["lines"]), r["lines"]
    assert " ".join(UNIVERSE_LINES) == UNIVERSE_FULL
    lit = set()
    for f in sorted((P / "scenes").glob("u*/*.ts*")):
        src = f.read_text()
        lit |= set(re.findall(r'text(?:=|:\s*)\{?"([^"]+)"', src))
        lit |= set(re.findall(r'(?:TEXT|LINE|LABEL|NUM)\w*\s*=\s*"([^"]+)"', src))
        for old in ("metres", "Planck", "Atom", "atom", "Electron", "Readout", "readout", "micro", "Sand", "sand", "veil", "Proton", "nucleus"):
            assert old not in src, ("a video-17 device / string is left in a scene", f.name, old)
    bad = sorted(t_ for t_ in lit if not any(t_ in v for v in verified))
    assert not bad, ("on-screen literals not in verified_on_screen_strings (lesson 20)", bad)
    placard_text = " ".join(p["line"] + " " + (p["fine"] or "") for p in placards)
    allscreen = " ".join(sorted(verified | lit | set(root_strings))).lower() + " " + placard_text.lower()
    assert not [f for f in forbidden if f in allscreen], ("forbidden_on_screen string on screen", [f for f in forbidden if f in allscreen])
    print("verified on-screen literals in scenes:", len(lit))

    # --- the settle is STILL (lesson 25) ------------------------------------------------------------------------------------
    chans = {"ladder.markerL": markerL, "ladder.vis": vis, "ladder.railDraw": rail_draw, "counter": value.astype(float),
             "counter.alpha": calpha, "window.open": wopen, "S1": aS1, "S2": aS2, "S3": aS3, "BH": aB, "orbit": oD, "brk": brk,
             "universe": uA, "bars.ord": ordA, "bars.rise": rise}
    for name, arr in chans.items():
        assert np.all(np.abs(arr[rel:] - arr[rel]) < 1e-9), ("the settle must be still", name)
    assert wopen[rel] == 0 and placards[-1]["exit"] <= rel and fr["ctaFrame"] == rel

    r4 = lambda a: [round(float(v), 4) for v in a]
    for r in rungs:
        r.pop("_climb")
    props = {
        "timeline": {
            "fps": FPS, "width": 1080, "height": 1920, "total_frames": total, "lead_frames": round(tl["lead_seconds"] * FPS),
            "sections": [{"id": s["id"], "from": s["from"], "durationInFrames": s["durationInFrames"]} for s in tl["sections"]],
            "scenes": [{"id": s["id"], "section": s["section"], "from": s["from"], "durationInFrames": s["durationInFrames"]} for s in tl["scenes"]],
            "words": [{"section": w["section"], "text": w["text"], "f0": w["f0"], "f1": w["f1"]} for w in words],
        },
        "captionPages": [{k: v for k, v in p.items() if k != "text"} for p in out_pages],
        "meter": meter,
        "ladder": {"markerL": [round(float(v), 5) for v in markerL], "markerVis": r4(vis), "railDraw": r4(rail_draw),
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
