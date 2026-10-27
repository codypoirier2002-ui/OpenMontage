#!/usr/bin/env python3
"""Build artifacts/props.json + props.generated.ts from the measured timeline (run from the repo root).

    python3 projects/how-a-cat-lands/build_props.py          # write
    python3 projects/how-a-cat-lands/build_props.py --check  # print pages + schedules only

Copied from projects/how-a-mosquito-drinks/build_props.py (video 14, QA passed; itself videos 12-13) and re-dressed.
Inputs: artifacts/timeline.json (aligned words, sections, scene windows), artifacts/script.json (caption text, claim tags),
artifacts/scene_plan.json (caption pages, placards, verified / forbidden strings), artifacts/soundtrack_report.json (key /
SFX frames + the motion constants: build_soundtrack.py owns K), artifacts/media_report.json (the window plates). Everything
out is in ABSOLUTE frames @ 30 fps.

Caption pages: scene_plan.metadata.captions.pages, RE-FLOWED (lesson 3: every claim starts its own page; no 2-word orphan):
s2 'First, its inner ear finds which' / 'way is up.' -> 'First, its inner ear' / 'finds which way is up.'; 'so each half can
turn on' / 'its own.' -> 'so each half' / 'can turn on its own.'; s3 'like a skater pulling in her' / 'arms. Then it swaps,' ->
'like a skater' / 'pulling in her arms.' / 'Then it swaps,' (SKATER -> TUCK inside a page); s5 'Short drops leave no time to'
/ 'turn. And that famous study where' (SHORT -> HIGHRISE inside a page) -> 'Short drops leave' / 'no time to turn.' / 'And that
famous study where'; 'It only counted cats that reached' / 'the vet.' -> 'It only counted cats' / 'that reached the vet.'
(the tokens are the plan's, asserted). <= 2 lines / <= 6 words; the line break is chosen with Bricolage Grotesque 800 @ 58 px
advance widths against a 700 px budget. Exit = 4 f after the page's last word ends (held >= 36 f when the next page allows),
clipped to the next page's start, or BUTTED to it (lesson 6). The CTA 'Seen a cat do this?' takes the slab 4 f after 'vet.'.
Tones: 'front' (amber, lightened) on both s3 'front's; 'back' (cyan, lightened) ONLY on s3's 'the back half' (s4 'back arched'
is the spine: plain).

Honesty meter (lesson 3: keyed to the START OF THE CAPTION PAGE that carries the claim; consecutive pages of one claim merge;
a NEW claim of the same state pulses): s1 MAREY MEASURED; s2 UP / BEND MEASURED; s3 TUCK / SKATER / TUCK (swap) MEASURED;
s4 SPREAD MEASURED; s5 'But not always.' SHORT PROBABLY, 'And that famous study where' (+ 'ninety percent survived high
falls?') HIGHRISE MEASURED, 'It only counted cats' (+ 'that reached the vet.') BIAS PROBABLY; IDLE at the CTA (the settle).

THE TEST LAB is ONE set of per-frame root curves (types.ts): props.rig (clamp, floor, drawn tag), props.checklist (ticks + the
illustrative clock), props.window (ONE box; S1 -> A1 crossfade with a hard tag swap; the Marey strip's steps; S2), props.cat
(the two-half cat: position, the per-half ROLL angles, legs tucked / out, bend, arch, flex, vis, ghost) and props.dials. The
cat's angle curves CONSERVE SPIN by construction: on every frame I_front * dFront + I_back * dBack = 0 with I = 1 - 0.9 * tuck
(legs out 1.0, tucked 0.1), the driven half eased (sine), the other half derived. Asserted: while the cat turns (sc06, sc08,
and the sc01 preview / sc10 demo) FRONT and BACK deltas have opposite signs and the TUCKED half always turns MORE; the
conserved total is 0 on every frame (so the readout 'total spin: 0' is constant and true); no angle moves more than
MAX_STEP_DEG per frame (no rigid jumps while visible); the short-drop ghost never reaches the floor line; every channel is
constant through the settle (lesson 25); the dials + 'total spin: 0' are gone before the 'But not always.' page (lesson 42).
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

P = Path("projects/how-a-cat-lands")
FPS = 30
LINE_BUDGET_PX = 700
LINE_HARD_PX = 744
CAPTION_PX = 58
EXIT_TAIL = 4
MIN_PAGE = 36
WITHIN_SENTENCE_BUTT_F = 21
BUTT_GAP = 13
GLIDE_LEAD = 6
PLACARD_MIN_F = 36
PLACARD_PAGE_GUARD_F = 4
PLACARD_ENTER_WORD = {"sc10-sc12": "And"}   # the study placard enters on the study's own page (not under SHORT, lesson 42)
PLACARD_TEXT_W = 772 - 2 * 28
PLACARD_SIZES = [26, 25, 24, 23, 22]
FINE_SIZES = [25, 24]
CTA_TEXT = "Seen a cat do this?"
CTA_PX = 52
PAGES = [
    ("s1", "Drop a cat upside down,"), ("s1", "and it flips over in midair"), ("s1", "with nothing to push on."),
    ("s1", "In 1894, that looked impossible."),
    ("s2", "First, its inner ear"), ("s2", "finds which way is up."), ("s2", "Then it bends in the middle,"), ("s2", "so each half"),
    ("s2", "can turn on its own."),
    ("s3", "It tucks its front legs,"), ("s3", "and the front half spins fast,"), ("s3", "like a skater"), ("s3", "pulling in her arms."),
    ("s3", "Then it swaps,"), ("s3", "and the back half follows."),
    ("s4", "Legs out, back arched,"), ("s4", "it lands on all four."),
    ("s5", "But not always."), ("s5", "Short drops leave"), ("s5", "no time to turn."), ("s5", "And that famous study where"),
    ("s5", "ninety percent survived high falls?"), ("s5", "It only counted cats"), ("s5", "that reached the vet."),
]
CLAIMS = {   # page -> (claim id, section, claim_tags key fragment, state)
    "Drop a cat upside down,": ("MAREY", "s1", "(MAREY)", "MEASURED"), "and it flips over in midair": ("MAREY", "s1", "(MAREY)", "MEASURED"),
    "with nothing to push on.": ("MAREY", "s1", "(MAREY)", "MEASURED"), "In 1894, that looked impossible.": ("MAREY", "s1", "(MAREY)", "MEASURED"),
    "First, its inner ear": ("UP", "s2", "(UP)", "MEASURED"), "finds which way is up.": ("UP", "s2", "(UP)", "MEASURED"),
    "Then it bends in the middle,": ("BEND", "s2", "(BEND)", "MEASURED"), "so each half": ("BEND", "s2", "(BEND)", "MEASURED"),
    "can turn on its own.": ("BEND", "s2", "(BEND)", "MEASURED"),
    "It tucks its front legs,": ("TUCK", "s3", "(TUCK)", "MEASURED"), "and the front half spins fast,": ("TUCK", "s3", "(TUCK)", "MEASURED"),
    "like a skater": ("SKATER", "s3", "(SKATER)", "MEASURED"), "pulling in her arms.": ("SKATER", "s3", "(SKATER)", "MEASURED"),
    "Then it swaps,": ("TUCK", "s3", "(TUCK)", "MEASURED"), "and the back half follows.": ("TUCK", "s3", "(TUCK)", "MEASURED"),
    "Legs out, back arched,": ("SPREAD", "s4", "(SPREAD)", "MEASURED"), "it lands on all four.": ("SPREAD", "s4", "(SPREAD)", "MEASURED"),
    "But not always.": ("SHORT", "s5", "(SHORT)", "PROBABLY"), "Short drops leave": ("SHORT", "s5", "(SHORT)", "PROBABLY"),
    "no time to turn.": ("SHORT", "s5", "(SHORT)", "PROBABLY"),
    "And that famous study where": ("HIGHRISE", "s5", "(HIGHRISE)", "MEASURED"),
    "ninety percent survived high falls?": ("HIGHRISE", "s5", "(HIGHRISE)", "MEASURED"),
    "It only counted cats": ("BIAS", "s5", "(BIAS", "PROBABLY"), "that reached the vet.": ("BIAS", "s5", "(BIAS", "PROBABLY"),
}
WEAK_END = {"a", "an", "the", "to", "of", "and", "is", "in", "it", "at", "as", "its", "by", "for", "if", "so", "her", "with", "on", "no"}
BOUND = {("upside", "down"), ("front", "legs"), ("front", "half"), ("back", "half"), ("inner", "ear"), ("all", "four"),
         ("ninety", "percent"), ("high", "falls"), ("the", "vet"), ("famous", "study"), ("spins", "fast"), ("which", "way")}
PLACARD_SCENES = {"sc01-sc03": ("sc01", "sc03"), "sc04-sc05": ("sc04", "sc05"), "sc06-sc08": ("sc06", "sc08"), "sc09": ("sc09", "sc09"),
                  "sc10-sc12": ("sc10", "sc12")}
# THE TEST LAB (mirrored in theme.ts L; asserted against it)
CARD = {"x0": 640, "x1": 920, "y0": 220, "y1": 600}
FIELD = {"x0": 120, "x1": 620, "y0": 360, "y1": 1000}
DIALS = {"x0": 640, "x1": 920, "y0": 620, "y1": 860}
LEDGER = {"x0": 140, "x1": 920, "y0": 630, "y1": 1010}
FLOOR_Y = 960
HEADER = "PROCEDURE: LANDING"
ROWS = [("01", "01 FIND UP", "tick01"), ("02", "02 BEND", "tick02"), ("03", "03 TUCK FRONT", "tick03"), ("04", "04 SWAP", "tick04"),
        ("05", "05 SPREAD", "tick05"), ("06", "06 LAND", "tick06")]
# the ELAPSED clock (illustrative, seconds): (key, value) - linear between keys, 0.00 until 'First', stopped on '06 LAND'.
# The end value is NOT one of the research brief's numbers (SHORT's ~0.2-0.5 s is PROBABLY and never on screen).
CLOCK_KEYS = [("clockStart", 0.0), ("tick02", 0.12), ("turnStart", 0.20), ("tick04", 0.38), ("land", 0.62), ("tick06", 0.64)]
LABELS = {"drawn": "drawn · not to scale", "ai": "AI impression", "marey": "engraving after É.-J. Marey, 1894", "illustrative": "illustrative",
          "elapsed": "ELAPSED", "header": HEADER, "front": "FRONT", "back": "BACK", "total": "total spin: 0", "up": "UP"}
# THE CAT (frame px; shared/Cat.tsx draws the same geometry: CAT in Cat.tsx)
CAT_X, CAT_SCALE = 380, 1.0
HANG_Y = 500                 # under the clamp (paws up to the jaws)
BODY_HALF_H, LEG_OUT = 34, 84
Y_LAND = FLOOR_Y - (BODY_HALF_H + LEG_OUT) * CAT_SCALE   # paws ON the floor line when upright with legs out
I_OUT, I_TUCK = 1.0, 0.1
TURN = 200.0                 # front turn (sc06) = 180 / (1 - r), r = I_TUCK / I_OUT: both halves end at 180 after the swap
SHORT_TURN = 70.0
MAX_STEP_DEG = 15.0         # deg / frame (the fast sc01 preview peaks ~13); + MAX_ACCEL_DEG: eased, never a jump
MAX_ACCEL_DEG = 3.0
EPS = 0.05

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
    """A per-frame channel built from keyframes: hold the value, then ease to the next over [a, b)."""

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




def cat_curves(T: int, fr: dict, mo: dict) -> tuple[dict, list[tuple[str, int, int, str]]]:
    """The two-half cat. Returns the per-frame channels and the TURN segments (name, a, b, driver) for the asserts."""
    TW = mo["TWIST_F"]
    co, cr = fr["clampOpen"], fr["catReset"]
    # legs: 0 out, 1 tucked
    ftuck = (Track(T, 0.0).to(co, co + 6, 1.0).to(48, 56, 0.0).to(cr, cr, 0.0, "step")
             .to(fr["tuckStart"], fr["tuckSeat"], 1.0).to(fr["swapStart"], fr["swapStart"] + TW, 0.0)
             .to(fr["shortStart"] + 3, fr["shortTurn"], 1.0).build())
    btuck = (Track(T, 0.0).to(48, 56, 1.0).to(86, 92, 0.0).to(cr, cr, 0.0, "step")
             .to(fr["swapStart"], fr["swapStart"] + TW, 1.0).to(fr["tick05"] - 8, fr["tick05"], 0.0).build())
    assert co + 6 <= 22 and fr["previewFlipEnd"] >= 92, ("the sc01 preview schedule assumes 'Drop' ~16 and 'midair' >= 92", co)
    # the TURN segments: (name, a, b, driver half, driver delta)
    segs = [("preview front", 22, 46, "front", TURN), ("preview back", 56, 84, "back", TURN),
            ("sc06 front (hero)", fr["turnStart"], fr["turnEnd"], "front", TURN),
            ("sc08 back follows", fr["backTurnStart"], fr["swapEnd"], "back", TURN),
            ("sc10 short drop (partial)", fr["shortTurn"], fr["shortGone"], "front", SHORT_TURN)]
    resets = {cr: (0.0, 0.0), fr["shortStart"] - 5: (0.0, 0.0)}
    ease = lambda x: 0.5 - 0.5 * math.cos(math.pi * x)
    front, back = np.zeros(T), np.zeros(T)
    f_, b_ = 0.0, 0.0
    I = lambda tuck: I_OUT - (I_OUT - I_TUCK) * tuck
    for f in range(T):
        if f in resets:
            f_, b_ = resets[f]
        if f > 0:
            for _, a, b, drv, dlt in segs:
                if a < f <= b:
                    d = dlt * (ease((f - a) / (b - a)) - ease((f - 1 - a) / (b - a)))
                    if drv == "front":
                        f_ += d
                        b_ += -d * I(ftuck[f]) / I(btuck[f])
                    else:
                        b_ += d
                        f_ += -d * I(btuck[f]) / I(ftuck[f])
        front[f], back[f] = f_, b_
    # position / shape
    y = (Track(T, HANG_Y).to(co, fr["previewFlipEnd"], 760.0, "in").to(cr, cr, 520.0, "step")
         .to(fr["bendStart"], fr["scenes_sc06"], 560.0, "linear").to(fr["scenes_sc06"], fr["scenes_sc07"], 620.0, "linear")
         .to(fr["scenes_sc07"], 900, 700.0, "linear").to(900, fr["land"], Y_LAND, "in")
         .to(fr["shortStart"] - 5, fr["shortStart"] - 5, 650.0, "step").to(fr["shortStart"], fr["shortGone"], 790.0, "in").build())
    x = np.full(T, float(CAT_X))
    bend = (Track(T, 0.0).to(fr["bendStart"], fr["bendSeat"], 35.0).to(fr["floorIn"], fr["tick05"], 0.0).build())
    arch = Track(T, 0.0).to(fr["arch"] - 8, fr["arch"], 1.0).to(fr["shortStart"] - 5, fr["shortStart"] - 5, 0.0, "step").build()
    flex = Track(T, 0.0).to(fr["land"], fr["land"] + 4, 1.0, "out").to(fr["land"] + 4, fr["land"] + 20, 0.25).to(fr["shortStart"] - 5, fr["shortStart"] - 5, 0.0, "step").build()
    vis = (Track(T, 1.0).to(270, 280, 0.0).to(cr, cr + 10, 1.0).to(975, 985, 0.0)
           .to(fr["shortStart"], fr["shortStart"] + 8, 1.0).to(fr["shortGone"] - 12, fr["shortGone"], 0.0).build())
    ghost = Track(T, 0.0).to(96, 106, 1.0).to(cr - 1, cr - 1, 0.0, "step").to(fr["shortStart"] - 5, fr["shortStart"] - 5, 1.0, "step").build()
    return ({"x": x, "y": y, "front": front, "back": back, "frontTuck": ftuck, "backTuck": btuck, "bend": bend, "arch": arch,
             "flex": flex, "vis": vis, "ghost": ghost}, [(s[0], s[1], s[2], s[3]) for s in segs])


def main() -> None:
    check = "--check" in sys.argv
    snd = load_module("build_soundtrack")
    tl = json.loads((P / "artifacts/timeline.json").read_text())
    script = json.loads((P / "artifacts/script.json").read_text())
    plan = json.loads((P / "artifacts/scene_plan.json").read_text())
    sound = json.loads((P / "artifacts/soundtrack_report.json").read_text())
    media = json.loads((P / "artifacts/media_report.json").read_text())
    width = advance("BricolageGrotesque-normal-800-latin.woff2", CAPTION_PX)
    total = tl["total_frames"]
    assert sound["total_frames"] == total, "soundtrack is stale: run build_soundtrack.py after align_narration.py"
    sc = {s["id"]: s for s in tl["scenes"]}
    order = [s["id"] for s in tl["scenes"]]
    fr = sound["frames"]
    assert fr == snd.key_frames(tl), "soundtrack_report frames != build_soundtrack.key_frames(timeline): rerun build_soundtrack.py"
    mo = sound["motion"]
    assert mo["SEAT_F"] == snd.SEAT_F and mo["TICK_F"] == snd.TICK_F and mo["WINDOW_OPEN_F"] == snd.WINDOW_OPEN_F and mo["TWIST_F"] == snd.TWIST_F
    T = total
    rel = fr["vetEndFrame"]

    words = [{**w, "f0": round(w["start"] * FPS), "f1": max(round(w["end"] * FPS), round(w["start"] * FPS) + 2)} for w in tl["words"]]
    for sec in script["sections"]:
        assert [w["text"] for w in words if w["section"] == sec["id"]] == sec["text"].split(), sec["id"]
    for w in words:
        n_ = norm(w["text"])
        w["tone"] = "front" if (n_ == "front" and w["section"] == "s3") else "back" if (n_ == "back" and w["section"] == "s3") else "plain"
    assert sum(w["tone"] == "front" for w in words) == 2 and sum(w["tone"] == "back" for w in words) == 1

    # --- caption pages ------------------------------------------------------------------------------------------
    planp = plan["metadata"]["captions"]["pages"]
    for sid in ("s1", "s2", "s3", "s4", "s5"):
        assert " ".join(p["page"] for p in planp if p["section"] == sid) == " ".join(t for s_, t in PAGES if s_ == sid), sid
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
    cursor = {s["id"]: 0 for s in script["sections"]}
    for sid, text in PAGES:
        toks = [w for w in words if w["section"] == sid]
        n = len(text.split())
        run = toks[cursor[sid]: cursor[sid] + n]
        assert " ".join(w["text"] for w in run) == text, (text, [w["text"] for w in run])
        cursor[sid] += n
        assert n <= 6, text
        pages.append({"section": sid, "lines": best_lines(run), "text": text})
    for s in script["sections"]:
        assert cursor[s["id"]] == len(s["text"].split()), ("pages do not cover the section", s["id"])
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
            "section": pg["section"], "startFrame": start, "exitFrame": exit_,
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
    assert cta_adv(CTA_TEXT) <= LINE_BUDGET_PX, cta_adv(CTA_TEXT)

    # --- honesty meter ---------------------------------------------------------------------------------------------
    tags_ = script["metadata"]["claim_tags"]
    for text, (cid, sec, frag, st) in CLAIMS.items():
        hits = [v for k, v in tags_[sec].items() if frag in k]
        assert len(hits) == 1 and hits[0] == st, ("claim state != script.json claim_tags", text, cid, frag, st, hits)
    assert set(CLAIMS) == {t for _, t in PAGES}
    meter = [{"frame": 0, "glideStart": 0, "state": "IDLE", "sublabel": "", "section": "", "anchor": "frame 0", "claim": "none (cold open)", "repeat": False}]
    prev_claim = None
    for (sid, text), pg in zip(PAGES, out_pages):
        cid, _, _, state = CLAIMS[text]
        if cid == prev_claim:
            continue
        prev = meter[-1]
        f = pg["startFrame"]
        meter.append({"frame": f, "glideStart": max(0, f - GLIDE_LEAD), "state": state, "sublabel": "", "section": sid,
                      "anchor": f"page '{text}'", "claim": cid, "repeat": state == prev["state"] and state != "IDLE"})
        prev_claim = cid
    meter.append({"frame": fr["ctaFrame"], "glideStart": fr["ctaFrame"] - GLIDE_LEAD, "state": "IDLE", "sublabel": "", "section": "",
                  "anchor": "the CTA (settle)", "claim": "none (settle)", "repeat": False})
    for a, b in zip(meter, meter[1:]):
        assert b["glideStart"] >= a["frame"] - GLIDE_LEAD and b["frame"] > a["frame"], (a, b)
    keyed = [k["frame"] for k in meter[1:]]
    assert len(keyed) == len(set(keyed)), ("two claims keyed on one caption page (lesson 3)", keyed)
    but_page = next(pg["startFrame"] for pg in out_pages if pg["words"][0]["text"] == "But")
    and_page = next(pg["startFrame"] for pg in out_pages if pg["words"][0]["text"] == "And")
    it_page = next(pg["startFrame"] for pg in out_pages if pg["words"][0]["text"] == "It" and pg["section"] == "s5")

    # --- THE CAT + THE DIALS -------------------------------------------------------------------------------------------
    frx = {**fr, **{f"scenes_{k}": v["from"] for k, v in sc.items()}}
    cat, segs = cat_curves(T, frx, mo)
    I = lambda tuck: I_OUT - (I_OUT - I_TUCK) * tuck
    dF, dB = np.diff(cat["front"]), np.diff(cat["back"])
    spin = I(cat["frontTuck"][1:]) * dF + I(cat["backTuck"][1:]) * dB
    hidden = (cat["vis"][:-1] == 0) & (cat["vis"][1:] == 0)
    resets = [f for f in range(T - 1) if abs(spin[f]) > 1e-9]
    assert all(hidden[f] for f in resets), ("a pose reset while the cat is visible", resets)
    spin = np.where(hidden, 0.0, spin)
    assert np.abs(spin).max() < 1e-9, ("total spin is not conserved", float(np.abs(spin).max()))
    turn_report = []
    for name, a, b, drv in segs:
        moving = [f for f in range(a, b) if abs(dF[f]) > EPS or abs(dB[f]) > EPS]
        assert moving, name
        for f in moving:
            assert dF[f] * dB[f] < 0, ("FRONT and BACK must turn opposite ways", name, f, dF[f], dB[f])
            tucked_front = cat["frontTuck"][f + 1] > cat["backTuck"][f + 1]
            assert tucked_front == (drv == "front"), ("the driven half must be the tucked one", name, f)
            big, small = (abs(dF[f]), abs(dB[f])) if tucked_front else (abs(dB[f]), abs(dF[f]))
            assert big > small, ("the TUCKED half must turn MORE", name, f)
        turn_report.append({"segment": name, "frames": [a, b], "tucked": drv,
                            "front_delta_deg": round(float(cat["front"][b] - cat["front"][a]), 2), "back_delta_deg": round(float(cat["back"][b] - cat["back"][a]), 2)})
    for k in ("sc06 front (hero)", "sc08 back follows"):
        r = next(x for x in turn_report if x["segment"] == k)
        assert sc[k[:4]]["from"] <= r["frames"][0] and r["frames"][1] <= sc[k[:4]]["from"] + sc[k[:4]]["durationInFrames"], ("turn outside its scene", r)
    assert abs(cat["front"][fr["swapEnd"]] - 180) < 1e-6 and abs(cat["back"][fr["swapEnd"]] - 180) < 1e-6, "both halves must end feet-down"
    vis_ = cat["vis"]
    for k_ in ("front", "back", "bend", "frontTuck", "backTuck"):
        st = np.abs(np.diff(cat[k_]))
        lim = MAX_STEP_DEG if k_ in ("front", "back", "bend") else 0.3
        bad = [f for f in range(T - 1) if st[f] > lim and (vis_[f] > 0 or vis_[f + 1] > 0)]
        assert not bad, ("a rigid jump while visible", k_, bad[:5])
        if k_ in ("front", "back", "bend"):
            acc = np.abs(np.diff(cat[k_], 2))
            bad = [f for f in range(T - 2) if acc[f] > MAX_ACCEL_DEG and all(vis_[f + i] > 0 for i in range(3))]
            assert not bad, ("a velocity jump (not eased) while visible", k_, bad[:5])
    stv = np.abs(np.diff(cat["y"]))
    assert not [f for f in range(T - 1) if stv[f] > 40 and (vis_[f] > 0 or vis_[f + 1] > 0)], "the cat jumps in y while visible"
    # the landing: the paws touch the floor line ON 'all' (X6), still above it on 'all' - 1
    paw = lambda f: cat["y"][f] + (BODY_HALF_H + LEG_OUT) * CAT_SCALE
    assert abs(paw(fr["land"]) - FLOOR_Y) < 0.5 and FLOOR_Y - paw(fr["land"] - 1) >= 3, (paw(fr["land"]), paw(fr["land"] - 1))
    # the short drop: never shown reaching the floor (upside down: its lowest point is the back of the body)
    for f in range(fr["shortStart"], fr["shortGone"] + 1):
        if vis_[f] > 0:
            assert cat["y"][f] + BODY_HALF_H * CAT_SCALE < FLOOR_Y - 60, ("the short-drop cat reaches the floor", f)
    for f in range(T):
        if vis_[f] > 0:
            assert FIELD["x0"] <= cat["x"][f] - 230 and cat["x"][f] + 230 <= FIELD["x1"] + 10 and FIELD["y0"] - 40 <= cat["y"][f] <= FIELD["y1"], (f, cat["x"][f], cat["y"][f])
    dials = {
        "front": Track(T, 0.0).to(fr["dialsIn"] - 8, fr["dialsIn"], 1.0).to(fr["dialsOut"] - 17, fr["dialsOut"] - 3, 0.0)
                 .to(fr["shortStart"] + 8, fr["shortStart"] + 16, 1.0).to(fr["shortGone"] - 14, fr["shortGone"] - 2, 0.0).build(),
        "back": Track(T, 0.0).to(fr["dialsIn"] - 8, fr["dialsIn"], 1.0).to(fr["dialsOut"] - 17, fr["dialsOut"] - 3, 0.0).build(),
        "total": Track(T, 0.0).to(fr["totalSeat"] - 8, fr["totalSeat"], 1.0).to(fr["dialsOut"] - 17, fr["dialsOut"] - 3, 0.0).build(),
    }
    # lesson 42: 'total spin: 0' + the BACK dial gone before the 'But not always.' (PROBABLY) page; FRONT returns for the demo
    assert dials["total"][but_page - 1] == 0 and dials["back"][but_page - 1] == 0 and dials["front"][but_page - 1] == 0
    glide = but_page - 6  # the tab starts gliding to PROBABLY 6 f before the page (QA m2)
    assert all(dials[k][glide] == 0 for k in ("front", "back", "total")), glide
    assert dials["front"][fr["shortGone"]] == 0 and dials["front"][and_page] == 0
    # the dials read the cat's own curves: while a dial is visible its half is visible too (same angle, one curve)
    assert all(vis_[f] > 0 or (dials["front"][f] == 0 and dials["back"][f] == 0) for f in range(T) if not (fr["windowOpen2"] <= f < fr["dialsOut"]))

    # --- THE RIG + THE CHECKLIST + THE CLOCK ---------------------------------------------------------------------------
    clampv = Track(T, 0.0).to(fr["clampOpen"] - 4, fr["clampOpen"], 1.0, "in").build()
    assert clampv[fr["clampOpen"]] == 1 and clampv[fr["clampOpen"] - 1] < 0.8
    floor = Track(T, 0.0).to(fr["floorIn"], fr["floorIn"] + 8, 1.0).to(fr["shortGone"] + 8, fr["shortGone"] + 20, 0.0).build()
    assert floor[fr["land"]] == 1 and floor[fr["ledgerSeat"] - snd.SEAT_F] == 0
    drawn = Track(T, 1.0).to(fr["ledgerSeat"] - 14, fr["ledgerSeat"] - 8, 0.0).build()
    rig = {"clamp": [round(float(v), 4) for v in clampv], "floor": [round(float(v), 4) for v in floor], "floorY": FLOOR_Y, "header": HEADER,
           "drawnTag": [round(float(v), 4) for v in drawn]}
    rows = [{"id": rid, "text": text, "tick": fr[key]} for rid, text, key in ROWS]
    ticks = [r["tick"] for r in rows]
    assert ticks == sorted(ticks) and ticks[-1] < rel, ticks
    kf = [(fr[k], v) for k, v in CLOCK_KEYS]
    assert [f for f, _ in kf] == sorted(f for f, _ in kf), kf
    clock = np.interp(np.arange(T), [f for f, _ in kf], [v for _, v in kf])
    assert np.all(np.diff(clock) >= 0) and clock[fr["tick06"]] == CLOCK_KEYS[-1][1]
    checklist = {"seat": 0, "header": HEADER, "rows": rows, "tickF": mo["TICK_F"], "clock": [round(float(v), 4) for v in clock],
                 "clockStop": fr["tick06"], "clockLabel": LABELS["elapsed"], "clockNote": LABELS["illustrative"]}

    # --- THE WINDOW ------------------------------------------------------------------------------------------------------
    WO, WC, XF = mo["WINDOW_OPEN_F"], mo["WINDOW_CLOSE_F"], mo["XFADE_F"]
    o1, c1, o2, c2 = fr["windowOpen1"], fr["windowClose1"], fr["windowOpen2"], fr["windowClose2"]
    wopen = Track(T, 0.0).to(o1 - 1, o1 - 1 + WO, 1.0, "outquad").to(c1, c1 + WC, 0.0).to(o2 - 1, o2 - 1 + WO, 1.0, "outquad").to(c2, c2 + WC, 0.0).build()
    assert wopen[o1 - 1] == 0 and wopen[o1] > 0.25 and wopen[c1 + WC] == 0 and wopen[o2 - 1] == 0 and wopen[o2] > 0.25 and wopen[c2 + WC] == 0
    ps = fr["plateSwap"]
    aS1 = Track(T, 1.0).to(ps, ps + XF, 0.0, "linear").build()
    aA1 = Track(T, 0.0).to(ps, ps + XF, 1.0, "linear").to(c1 + WC, c1 + WC, 0.0, "step").build()
    aS2 = Track(T, 0.0).to(c1 + WC + 1, c1 + WC + 1, 1.0, "step").build()
    step = Track(T, 0.0)
    for i, s_ in enumerate(fr["stripSteps"]):
        step.to(s_ - mo["STRIP_MOVE_F"], s_, float(i + 1))
    step = step.build()
    cells = [c["file"] for c in media["A1"]["cells"]]
    assert len(cells) == len(fr["stripSteps"]) + 1
    # lesson 38: exactly one tag on every frame the window is visible; the swap is a hard cut at the crossfade midpoint
    tags_seen = []
    for f in range(T):
        if wopen[f] > 0:
            al = {"S1": aS1[f], "A1": aA1[f], "S2": aS2[f]}
            best = max(al, key=lambda k: (al[k], -["S1", "A1", "S2"].index(k)))
            assert al[best] > 0, f
            tags_seen.append((f, best))
    swap_f = next(f for f, b in tags_seen if b == "A1")
    assert abs(swap_f - (ps + XF / 2)) <= 1, ("the tag must swap at the crossfade midpoint", swap_f)
    assert all(b == "S2" for f, b in tags_seen if f >= o2 - 1), "S2's tag only in sc09"
    mp = media["plates"]
    box = media["window"]
    assert box == {"x0": 160, "x1": 620, "y0": 360, "y1": 1000}
    assert box["x1"] <= CARD["x0"] - 10, "the window must never cover the checklist card"
    plates = [
        {"id": "S1", "scene": "sc02", "alpha": [round(float(v), 4) for v in aS1], "push": mp["S1"]["push"], "pushFrom": o1, "pushTo": c1 + WC,
         "tag": LABELS["ai"], "base": mp["S1"]["file"]},
        {"id": "A1", "scene": "sc03", "alpha": [round(float(v), 4) for v in aA1], "push": [1.0, 1.0], "pushFrom": ps, "pushTo": c1 + WC,
         "tag": LABELS["marey"], "base": None, "cells": cells, "step": [round(float(v), 4) for v in step]},
        {"id": "S2", "scene": "sc09", "alpha": [round(float(v), 4) for v in aS2], "push": mp["S2"]["push"], "pushFrom": o2, "pushTo": c2 + WC,
         "tag": LABELS["ai"], "base": mp["S2"]["file"]},
    ]
    window = {"box": box, "radius": 22, "frame": 6, "open": [round(float(v), 4) for v in wopen], "plates": plates}

    # theme.ts must equal these numbers
    theme = (P / "theme.ts").read_text()
    for name, d_ in (("card", CARD), ("win", box), ("field", FIELD), ("dials", DIALS), ("ledger", LEDGER)):
        m = re.search(name + r":\s*\{\s*x0:\s*(\d+),\s*x1:\s*(\d+),\s*y0:\s*(\d+),\s*y1:\s*(\d+)", theme)
        assert m and [int(v) for v in m.groups()] == [d_[k] for k in ("x0", "x1", "y0", "y1")], f"theme.ts L.{name} stale"
    assert re.search(r"floorY:\s*%d" % FLOOR_Y, theme), "theme.ts L.field.floorY stale"
    cat_src = (P / "shared/Cat.tsx").read_text()
    for k_, v_ in (("halfH", BODY_HALF_H), ("legOut", LEG_OUT)):
        assert re.search(r"%s:\s*%d\b" % (k_, v_), cat_src), f"shared/Cat.tsx CAT.{k_} != build_props {v_}"

    # --- placards (root rail) ----------------------------------------------------------------------------------------
    bc = {px: advance("IBMPlexSansCondensed-normal-600-latin.woff2", px) for px in set(PLACARD_SIZES + FINE_SIZES)}
    starts = sorted(p["startFrame"] for p in out_pages)
    placards = []
    for pl in plan["metadata"]["placards"]:
        first, last = PLACARD_SCENES[pl["scenes"]]
        enter = sc[first]["from"] + 2
        if pl["scenes"] in PLACARD_ENTER_WORD:
            enter = next(pg["startFrame"] for pg in out_pages if pg["words"][0]["text"] == PLACARD_ENTER_WORD[pl["scenes"]])
        for ps_ in starts:
            if ps_ <= enter < ps_ + PLACARD_PAGE_GUARD_F:
                enter = ps_ + PLACARD_PAGE_GUARD_F
        exit_ = sc[order[order.index(last) + 1]]["from"] if last != order[-1] else rel
        assert exit_ - enter >= PLACARD_MIN_F, ("placard held < 1.2 s", pl, enter, exit_)
        line, fine = pl["text"], pl.get("fine_print")
        size = next((px for px in PLACARD_SIZES if bc[px](line) <= PLACARD_TEXT_W), None)
        assert size, ("placard line too long", line)
        fsize = next((px for px in FINE_SIZES if bc[px](fine) <= PLACARD_TEXT_W), None) if fine else None
        assert fine is None or fsize, ("fine print too long at >= 24 px (lesson 31)", fine)
        assert size * 1.15 + (fsize * 1.15 + 2 if fine else 0) <= 80 - 6, ("placard rows overflow the 80 px rail", line)
        placards.append({"enter": enter, "exit": exit_, "line": line, "lines": [line], "size": size, "w": round(bc[size](line), 1),
                         "fine": fine, "fineSize": fsize, "fineW": round(bc[fsize](fine), 1) if fine else None, "anchor": pl["scenes"]})
        assert 140 + 28 + placards[-1]["w"] <= 912 and (not fine or 140 + 28 + placards[-1]["fineW"] <= 912), ("placard reaches x >= 912", placards[-1])
    for a, b in zip(placards, placards[1:]):
        assert a["exit"] <= b["enter"], (a, b)
    assert placards[-1]["enter"] >= and_page, "the study placard must not sit under the SHORT claim (lesson 42)"

    # --- strings: verified / forbidden (lessons 20, 32) ----------------------------------------------------------------
    verified = set(plan["metadata"]["verified_on_screen_strings"])
    forbidden = [f.split(" (")[0].lower() for f in plan["metadata"]["forbidden_on_screen"]]
    root_strings = [HEADER] + [r[1] for r in ROWS] + list(LABELS.values()) + [CTA_TEXT]
    for s_ in root_strings:
        assert s_ in verified, ("root string not in verified_on_screen_strings (lesson 20)", s_)
    lit = set()
    for f in sorted((P / "scenes").glob("u*/*.ts*")):
        src = f.read_text()
        lit |= set(re.findall(r'text(?:=|:\s*)\{?"([^"]+)"', src))
        lit |= set(re.findall(r'(?:TEXT|LINE|LABEL|NUM)\w*\s*=\s*"([^"]+)"', src))
    bad = sorted(t_ for t_ in lit if not any(t_ in v for v in verified))
    assert not bad, ("on-screen literals not in verified_on_screen_strings (lesson 20)", bad)
    placard_text = " ".join(p["line"] + " " + (p["fine"] or "") for p in placards)
    allscreen = " ".join(sorted(verified | lit | set(root_strings))).lower() + " " + placard_text.lower()
    assert not [f for f in forbidden if f in allscreen], ("forbidden_on_screen string on screen", [f for f in forbidden if f in allscreen])
    print("verified on-screen literals in scenes:", len(lit))

    # --- the settle is STILL (lesson 25) ---------------------------------------------------------------------------------
    chans = {f"cat.{k}": v for k, v in cat.items()}
    chans.update({f"dials.{k}": v for k, v in dials.items()})
    chans.update({"rig.clamp": clampv, "rig.floor": floor, "rig.drawnTag": drawn, "clock": clock, "window.open": wopen,
                  "S1.alpha": aS1, "A1.alpha": aA1, "S2.alpha": aS2, "A1.step": step})
    for name, arr in chans.items():
        assert np.all(np.abs(arr[rel:] - arr[rel]) < 1e-9), ("the settle must be still", name)
    assert wopen[rel] == 0 and cat["vis"][rel] == 0 and all(r["tick"] + 1 <= rel for r in rows) and placards[-1]["exit"] <= rel
    assert fr["ghostColumn"] >= it_page and fr["bracket"] < rel

    r4 = lambda a: [round(float(v), 4) for v in a]
    props = {
        "timeline": {
            "fps": FPS, "width": 1080, "height": 1920, "total_frames": total, "lead_frames": round(tl["lead_seconds"] * FPS),
            "sections": [{"id": s["id"], "from": s["from"], "durationInFrames": s["durationInFrames"]} for s in tl["sections"]],
            "scenes": [{"id": s["id"], "section": s["section"], "from": s["from"], "durationInFrames": s["durationInFrames"]} for s in tl["scenes"]],
            "words": [{"section": w["section"], "text": w["text"], "f0": w["f0"], "f1": w["f1"]} for w in words],
        },
        "captionPages": out_pages,
        "meter": meter,
        "cat": {**{k: r4(v) for k, v in cat.items()}, "scale": CAT_SCALE},
        "dials": {k: r4(v) for k, v in dials.items()},
        "rig": rig,
        "checklist": checklist,
        "window": window,
        "placards": placards,
        "labels": LABELS,
        "cta": {"text": CTA_TEXT, "lines": [CTA_TEXT], "frame": fr["ctaFrame"]},
        "settle": {"from": rel, "freezeFrom": rel, "chordFrame": fr["chordFrame"]},
        "freezes": [],
        "audio": {"soundtrack": "audio/soundtrack.wav", **fr},
        "motion": mo,
        "layers": "all",
        "exportVariant": "main",
    }

    for pg in out_pages:
        lines = {}
        for w in pg["words"]:
            lines.setdefault(w["line"], []).append(w["text"] + {"front": "^", "back": "~", "plain": ""}[w["tone"]])
        print(f'{pg["startFrame"]:5d}-{pg["exitFrame"]:5d} {pg["section"]} | ' + " / ".join(" ".join(v) for v in lines.values()))
    for k in meter:
        print(f'meter {k["glideStart"]:5d}->{k["frame"]:5d} {k["state"]:<9}{" (pulse)" if k["repeat"] else "        "} {k["anchor"]}')
    print("placards:", [(p["enter"], p["exit"], p["size"], p["fineSize"], p["line"][:30]) for p in placards])
    print("turns:", turn_report)
    print("checklist:", [(r["id"], r["tick"]) for r in rows], "clock stop", checklist["clockStop"], "tag swap", swap_f)
    if check:
        return
    (P / "artifacts/props.json").write_text(json.dumps(props, ensure_ascii=False, separators=(",", ":")))
    (P / "artifacts/cat_turns.json").write_text(json.dumps({"turns": turn_report, "spin_conservation_max_abs": float(np.abs(spin).max()),
                                                            "I_out": I_OUT, "I_tucked": I_TUCK}, indent=1))
    ts = ("// GENERATED by build_props.py from artifacts/props.json - do not edit by hand.\n"
          "import type { CatProps } from \"./types\";\n\n"
          f"export const DEFAULT_PROPS: CatProps = {json.dumps(props, ensure_ascii=False, separators=(',', ':'))};\n")
    (P / "props.generated.ts").write_text(ts)
    print("wrote artifacts/props.json and props.generated.ts")


if __name__ == "__main__":
    main()
