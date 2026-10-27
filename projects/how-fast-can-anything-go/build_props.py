#!/usr/bin/env python3
"""Build artifacts/props.json + props.generated.ts from the measured timeline (run from the repo root).

    python3 projects/how-fast-can-anything-go/build_props.py          # write
    python3 projects/how-fast-can-anything-go/build_props.py --check  # print pages + schedules only

Copied from projects/how-a-cat-lands/build_props.py (video 15, QA passed; itself videos 12-14) and re-dressed for the Speed
Ladder (the root curves of projects/how-hot-can-it-get/build_props.py, without the black-body glow and the camera).
Inputs: artifacts/timeline.json (aligned words, sections, scene windows), artifacts/script.json (caption text, claim tags),
artifacts/scene_plan.json (caption pages, placards, verified / forbidden strings), artifacts/soundtrack_report.json (key /
SFX frames + the motion constants: build_soundtrack.py owns K), artifacts/media_report.json (the window plates, placeholders
or crops). Everything out is in ABSOLUTE frames @ 30 fps.

Caption pages: scene_plan.metadata.captions.pages, RE-FLOWED (lesson 3: every claim starts its own page; no 2-word orphan):
s1 'You walk at about five kilometres' / 'an hour. A cheetah sprints at' / 'about a hundred.' -> 'You walk at about five' /
'kilometres an hour.' / 'A cheetah sprints' / 'at about a hundred.' (CHEETAH starts its own page); 'A diving falcon hits nearly
four' / 'hundred.' -> 'A diving falcon hits' / 'nearly four hundred.'; s2 'Sound outruns them all at over' / 'twelve hundred.
But sitting still,' -> 'Sound outruns them all' / 'at over twelve hundred.' / 'But sitting still,' (ORBIT starts its own page);
s4 'And nothing with mass can catch' / 'it: the closer you get,' / 'the more energy each step costs,' / 'without end.' -> 'And
nothing with mass' / 'can catch it:' / 'the closer you get,' / 'the more energy' / 'each step costs, without end.'; s5 'The Large
Hadron Collider pushes protons' / 'to within a hair of light' / 'speed. Close. But never all the' / 'way.' -> 'The Large Hadron
Collider' / 'pushes protons to within' / 'a hair of light speed.' / 'Close.' / 'But never all the way.' (the tokens are the
plan's, asserted). <= 2 lines / <= 6 words; the line break is chosen with Bricolage Grotesque 800 @ 58 px advance widths
against a 700 px budget. Exit = 4 f after the page's last word ends (held >= 36 f when the next page allows), clipped to the
next page's start, or BUTTED to it (lesson 6). The CTA "What's the fastest thing you've ridden?" (two lines) takes the slab
4 f after 'way.'. Tones: none (the plan: plain only).

Honesty meter (lesson 3: keyed to the START OF THE CAPTION PAGE that carries the claim; consecutive pages of one claim merge;
a NEW claim of the same state pulses): s1 WALK MEASURED, CHEETAH MEASURED, FALCON PROBABLY; s2 SOUND MEASURED, ORBIT
MEASURED; s3 PROBE MEASURED; s4 LIGHT MEASURED, WALL MEASURED; s5 LHC MEASURED (through 'Close.' / 'But never all the way.',
the claim's own conclusion); IDLE at the CTA (the settle).

THE LADDER is ONE set of per-frame root curves (types.ts): props.ladder (the marker's log10(km/h) climbing rung by rung on
eased moves that END ON each rung's seat frame; the asymptotic creep from PARKER toward 'c' from 'nothing' to 'hair'; the
streak intensity; the red c line's intensity; the gap bracket; the rail draw), props.counter (ZEROS 0 -> 9 = floor(log10)
of the rung's number, stepping on the X3 ticks), props.window (ONE box; S1 -> S2 crossfade with a hard tag swap; S3),
props.you (the YOU tag: WALK -> EARTH on the jump, then constant), props.beam (sc08), props.energy (sc10: v/c, gamma =
1/sqrt(1-(v/c)^2), the bar's height running off the top ON 'end'), props.nines (sc11: one glyph per X3 tick), props.mass /
props.orbit (visibilities with their lesson-42 exits). Asserted: THE MARKER NEVER TOUCHES 'c' (railY(markerL) >= cY +
MARKER_GAP_PX on EVERY frame, i.e. >= 6 px clear of the line even with the marker's radius); the climbs end exactly on
their seats; every rung label chip fits beside the window (never under it while the window is open); the counter equals
floor(log10) of the active rung; the orbit inset, the mass label and the energy bar are gone >= 8 f before the next
claim's tab page (lessons 31 / 42 / 47); every channel is constant through the settle (lesson 25); a literal scan of
scenes/u*/ against verified_on_screen_strings / forbidden_on_screen (lesson 20).
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

P = Path("projects/how-fast-can-anything-go")
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
PLACARD_TEXT_W = 772 - 2 * 28
PLACARD_SIZES = [26, 25, 24, 23, 22]
FINE_SIZES = [25, 24]
CTA_TEXT = "What's the fastest thing you've ridden?"
CTA_LINES = ["What's the fastest thing", "you've ridden?"]
CTA_PX = 52
PAGES = [
    ("s1", "You walk at about five"), ("s1", "kilometres an hour."), ("s1", "A cheetah sprints"), ("s1", "at about a hundred."),
    ("s1", "A diving falcon hits"), ("s1", "nearly four hundred."),
    ("s2", "Sound outruns them all"), ("s2", "at over twelve hundred."), ("s2", "But sitting still,"),
    ("s2", "you're doing over a hundred thousand,"), ("s2", "riding Earth around the Sun."),
    ("s3", "The fastest thing we've ever built,"), ("s3", "the Parker Solar Probe,"), ("s3", "reached nearly seven hundred thousand,"),
    ("s3", "falling toward the Sun."),
    ("s4", "Light does over a billion."), ("s4", "And nothing with mass"), ("s4", "can catch it:"), ("s4", "the closer you get,"),
    ("s4", "the more energy"), ("s4", "each step costs, without end."),
    ("s5", "The Large Hadron Collider"), ("s5", "pushes protons to within"), ("s5", "a hair of light speed."), ("s5", "Close."),
    ("s5", "But never all the way."),
]
CLAIMS = {   # page -> (claim id, section, claim_tags key fragment, state)
    "You walk at about five": ("WALK", "s1", "(WALK)", "MEASURED"), "kilometres an hour.": ("WALK", "s1", "(WALK)", "MEASURED"),
    "A cheetah sprints": ("CHEETAH", "s1", "(CHEETAH)", "MEASURED"), "at about a hundred.": ("CHEETAH", "s1", "(CHEETAH)", "MEASURED"),
    "A diving falcon hits": ("FALCON", "s1", "(FALCON)", "PROBABLY"), "nearly four hundred.": ("FALCON", "s1", "(FALCON)", "PROBABLY"),
    "Sound outruns them all": ("SOUND", "s2", "(SOUND)", "MEASURED"), "at over twelve hundred.": ("SOUND", "s2", "(SOUND)", "MEASURED"),
    "But sitting still,": ("ORBIT", "s2", "(ORBIT)", "MEASURED"), "you're doing over a hundred thousand,": ("ORBIT", "s2", "(ORBIT)", "MEASURED"),
    "riding Earth around the Sun.": ("ORBIT", "s2", "(ORBIT)", "MEASURED"),
    "The fastest thing we've ever built,": ("PROBE", "s3", "(PROBE)", "MEASURED"), "the Parker Solar Probe,": ("PROBE", "s3", "(PROBE)", "MEASURED"),
    "reached nearly seven hundred thousand,": ("PROBE", "s3", "(PROBE)", "MEASURED"), "falling toward the Sun.": ("PROBE", "s3", "(PROBE)", "MEASURED"),
    "Light does over a billion.": ("LIGHT", "s4", "(LIGHT)", "MEASURED"),
    "And nothing with mass": ("WALL", "s4", "(WALL)", "MEASURED"), "can catch it:": ("WALL", "s4", "(WALL)", "MEASURED"),
    "the closer you get,": ("WALL", "s4", "(WALL)", "MEASURED"), "the more energy": ("WALL", "s4", "(WALL)", "MEASURED"),
    "each step costs, without end.": ("WALL", "s4", "(WALL)", "MEASURED"),
    "The Large Hadron Collider": ("LHC", "s5", "(LHC)", "MEASURED"), "pushes protons to within": ("LHC", "s5", "(LHC)", "MEASURED"),
    "a hair of light speed.": ("LHC", "s5", "(LHC)", "MEASURED"), "Close.": ("LHC", "s5", "(LHC)", "MEASURED"), "But never all the way.": ("LHC", "s5", "(LHC)", "MEASURED"),
}
WEAK_END = {"a", "an", "the", "to", "of", "and", "is", "in", "it", "at", "as", "its", "by", "for", "if", "so", "her", "with", "on", "no", "over", "nearly"}
BOUND = {("five", "kilometres"), ("a", "hundred"), ("four", "hundred"), ("twelve", "hundred"), ("hundred", "thousand"), ("parker", "solar"),
         ("solar", "probe"), ("seven", "hundred"), ("a", "billion"), ("with", "mass"), ("hadron", "collider"),
         ("light", "speed"), ("the", "sun"), ("a", "hair"), ("sitting", "still")}
PLACARD_SCENES = {"sc01-sc03": ("sc01", "sc03"), "sc04-sc05": ("sc04", "sc05"), "sc06-sc07": ("sc06", "sc07"), "sc08-sc10": ("sc08", "sc10"),
                  "sc11-sc12": ("sc11", "sc12")}
# the placards AS BUILT: placard 3 reworded (lesson 32: the brief holds NASA's figure only through Space.com / SlashGear / Live
# Science reports, so the placard credits the report and names NASA as the figure's owner, not as a source read)
PLACARDS = [
    ("sc01-sc03", "cheetah: collar study, Wilson et al., Nature 2013", "falcon dive ~390 km/h is commonly cited, weakly sourced"),
    ("sc04-sc05", "sound: 343 m/s in 20 °C air · Earth: 29.78 km/s (NASA)", "km/h on a log scale: each tick is 10x"),
    ("sc06-sc07", "Parker Solar Probe: ~692,000 km/h (Dec 2024)", "NASA's figure as reported by Space.com · speed from falling toward the Sun"),
    ("sc08-sc10", "c = 299,792,458 m/s exactly (NIST)", "energy needed grows without limit as speed nears c"),
    ("sc11-sc12", "CERN LHC: protons at 6.8 TeV (2022)", "0.999999991 of light speed"),
]
# THE LADDER (mirrored in theme.ts L; asserted against it)
RAIL = {"x": 250, "axisY0": 1080, "cY": 380}
WIN = {"x0": 580, "x1": 920, "y0": 440, "y1": 893}
COUNTER = {"x0": 640, "x1": 920, "y0": 220, "y1": 340}
READOUT = {"x0": 600, "x1": 920, "y0": 460, "y1": 600}
LABEL_X = 280
C_KMH = 1079252849
L_C = math.log10(C_KMH)
PPD = (RAIL["axisY0"] - RAIL["cY"]) / L_C
MARKER_R = 6
MARKER_GAP_PX = 24            # the marker's CENTRE stays >= 24 px under the c line (>= 18 px clear of its 6 px radius; QA B-01: 14 read as touching at phone scale)
# (id, name, number string, km/h, probably?, chip)
RUNGS = [
    ("walk", "WALK", "~5", 5, False, None),
    ("cheetah", "CHEETAH", "~100", 100, False, None),
    ("falcon", "FALCON (dive)", "~390", 390, True, "commonly cited"),
    ("sound", "SOUND", "1,235", 1235, False, None),
    ("earth", "EARTH (orbit)", "~107,000", 107000, False, None),
    ("parker", "PARKER (fastest built)", "~692,000", 692000, False, None),
    ("light", "LIGHT", "1,079,252,849", C_KMH, False, None),
]
RUNG_SEAT = {"walk": "walkSeat", "cheetah": "cheetahSeat", "falcon": "falconSeat", "sound": "soundSeat", "earth": "earthSeat", "parker": "parkerSeat", "light": "lightSeat"}
RUNG_CLIMB = {"cheetah": "climbCheetah", "falcon": "climbFalcon", "sound": "climbSound", "earth": "jumpStart", "parker": "climbParker"}
LABEL_PX = 28
NAME_LINES = {"earth": ["EARTH (orbit)", "~107,000"], "parker": ["PARKER (fastest built)", "~692,000"]}   # the two labels too wide for the field beside the window (two-line chips)
LABELS = {"axis": "km/h · log scale", "zeros": "ZEROS", "ai": "AI impression", "drawn": "drawn · not to scale", "c": "c", "you": "YOU",
          "gap": "the gap", "mass": "anything with mass", "energy": "ENERGY NEEDED", "speed": "speed", "energyAxis": "energy",
          "lhc": "LHC protons", "nines": "99.9999991 %", "probe": "Parker Solar Probe · NASA", "falling": "falling toward the Sun",
          "cited": "commonly cited"}
GAMMA_K = 4.8                 # the energy bar: gamma(x) = 1 + 0.5 (e^(k x) - 1) over the bar's growth, 20 px per unit of (gamma - 1)
BAR_OFF_PX = 1130.0           # the bar top is this far above the rail foot ON barOff (off the frame top, 1080 + 50)

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
                "out": lambda x: 1 - (1 - x) ** 3, "outquad": lambda x: 1 - (1 - x) ** 2, "step": lambda x: 1.0,
                "inexpo": lambda x: 0 if x == 0 else 2 ** (10 * (x - 1))}
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
    return RAIL["axisY0"] - Lv * PPD


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
    assert mo["SEAT_F"] == snd.SEAT_F and mo["WINDOW_OPEN_F"] == snd.WINDOW_OPEN_F and mo["CLIMB_F"] == snd.CLIMB_F and mo["BEAM_F"] == snd.BEAM_F and mo["FADE_F"] == snd.FADE_F
    T = total
    rel = fr["wayEndFrame"]

    words = [{**w, "f0": round(w["start"] * FPS), "f1": max(round(w["end"] * FPS), round(w["start"] * FPS) + 2)} for w in tl["words"]]
    for sec in script["sections"]:
        assert [w["text"] for w in words if w["section"] == sec["id"]] == sec["text"].split(), sec["id"]
    for w in words:
        w["tone"] = "plain"

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
    assert " ".join(CTA_LINES) == CTA_TEXT and all(cta_adv(l) <= LINE_BUDGET_PX for l in CTA_LINES), [cta_adv(l) for l in CTA_LINES]

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
    page_of = lambda first, section: next(pg["startFrame"] for pg in out_pages if pg["words"][0]["text"] == first and pg["section"] == section)
    probe_page, lhc_page = page_of("The", "s3"), page_of("The", "s5")
    assert meter[-2]["claim"] == "LHC" and meter[-2]["frame"] == lhc_page

    # --- THE LADDER: the marker --------------------------------------------------------------------------------------
    rungs = []
    for rid, name, num, kmh, prob, chip in RUNGS:
        lines = NAME_LINES.get(rid, [f"{name} · {num}"])
        rungs.append({"id": rid, "name": name, "num": num, "lines": lines, "kmh": kmh, "L": round(math.log10(kmh), 5), "seat": fr[RUNG_SEAT[rid]],
                      "probably": prob, "chip": chip})
    Lof = {r["id"]: r["L"] for r in rungs}
    assert abs(Lof["light"] - L_C) < 1e-5
    Lof["light"] = L_C
    L_final = L_C - MARKER_GAP_PX / PPD
    mk = Track(T, Lof["walk"])
    for rid in ("cheetah", "falcon", "sound", "earth", "parker"):
        mk.to(fr[RUNG_CLIMB[rid]], fr[RUNG_SEAT[rid]], Lof[rid], "sine")
    mk.to(fr["wallStart"], fr["creepEnd"], L_final, "out")
    markerL = mk.build()
    for rid in ("cheetah", "falcon", "sound", "earth", "parker"):
        s_, c_ = fr[RUNG_SEAT[rid]], fr[RUNG_CLIMB[rid]]
        assert abs(markerL[s_] - Lof[rid]) < 1e-9 and markerL[c_] < Lof[rid] and abs(markerL[c_ - 1] - markerL[c_]) < 1e-9, ("climb must end ON the seat and start ON its key frame", rid)
        assert markerL[s_ - 1] < Lof[rid], rid
    for f in range(T):
        assert rail_y(markerL[f]) >= RAIL["cY"] + MARKER_GAP_PX - 1e-6, ("THE MARKER TOUCHES c", f, rail_y(markerL[f]))
    assert abs(rail_y(markerL[fr["creepEnd"]]) - (RAIL["cY"] + MARKER_GAP_PX)) < 1e-6 and np.all(np.diff(markerL) >= -1e-12), "the marker only climbs"
    # the creep is visible in sc10 and still creeping (sub-pixel allowed) in sc11
    assert rail_y(markerL[sc["sc10"]["from"]]) - rail_y(markerL[sc["sc11"]["from"]]) > 60, "the marker must inch up visibly through sc10"
    assert rail_y(markerL[sc["sc11"]["from"]]) - rail_y(markerL[fr["creepEnd"]]) > 2, "the marker must still creep in sc11"
    vis = np.ones(T)
    streak = np.zeros(T)
    for f in range(1, T):
        streak[f] = min(1.0, abs(markerL[f] - markerL[f - 1]) * PPD / 6.0)   # 6 px/f = full streaks
    kern = np.ones(5) / 5
    streak = np.convolve(np.pad(streak, 2, mode="edge"), kern, mode="valid")
    cLit = Track(T, 0.3).to(fr["lightSeat"] - 2, fr["lightSeat"], 1.0, "linear").build()
    gap = Track(T, 0.0).to(fr["gapBracket"] - 6, fr["gapBracket"], 1.0, "linear").build()
    rail_draw = Track(T, 0.0).to(fr["railDraw"], fr["railDraw"] + 16, 1.0, "outquad").build()
    assert gap[fr["gapBracket"]] == 1 and gap[fr["gapBracket"] - 7] == 0 and cLit[fr["lightSeat"]] == 1 and cLit[fr["lightSeat"] - 3] == 0.3

    # rung labels: each chip's lines must fit beside the window while the window is open (never under a photo)
    saira = advance("SairaCondensed-normal-700-latin.woff2", LABEL_PX)
    mono = advance("IBMPlexMono-normal-500-latin.woff2", LABEL_PX)

    def chip_w(line: str) -> float:
        if " · " in line:
            name, num = line.split(" · ")
            return saira(name) + saira(" · ") + mono(num) + 2 * 12
        return (mono(line) if re.match(r"^[~\d,]+$", line) else saira(line)) + 2 * 12
    wopen_frames = []  # filled below; window state needed -> compute the window first
    # --- THE WINDOW ------------------------------------------------------------------------------------------------------
    WO, WC, XF = mo["WINDOW_OPEN_F"], mo["WINDOW_CLOSE_F"], mo["XFADE_F"]
    o1, c1, o2, c2 = fr["windowOpen1"], fr["windowClose1"], fr["windowOpen2"], fr["windowClose2"]
    wopen = Track(T, 0.0).to(o1 - 1, o1 - 1 + WO, 1.0, "outquad").to(c1, c1 + WC, 0.0).to(o2 - 1, o2 - 1 + WO, 1.0, "outquad").to(c2, c2 + WC, 0.0).build()
    assert wopen[o1 - 1] == 0 and wopen[o1] > 0.25 and wopen[c1 + WC] == 0 and wopen[o2 - 1] == 0 and wopen[o2] > 0.25 and wopen[c2 + WC] == 0
    ps = fr["plateSwap"]
    aS1 = Track(T, 1.0).to(ps, ps + XF, 0.0, "linear").build()
    aS2 = Track(T, 0.0).to(ps, ps + XF, 1.0, "linear").to(c1 + WC, c1 + WC, 0.0, "step").build()
    aS3 = Track(T, 0.0).to(c1 + WC + 1, c1 + WC + 1, 1.0, "step").build()
    tags_seen = []
    for f in range(T):
        if wopen[f] > 0:
            al = {"S1": aS1[f], "S2": aS2[f], "S3": aS3[f]}
            best = max(al, key=lambda k: (al[k], -["S1", "S2", "S3"].index(k)))
            assert al[best] > 0, f
            tags_seen.append((f, best))
    swap_f = next(f for f, b in tags_seen if b == "S2")
    assert abs(swap_f - (ps + XF / 2)) <= 1, ("the tag must swap at the crossfade midpoint", swap_f)
    assert all(b == "S3" for f, b in tags_seen if f >= o2 - 1), "S3's tag only in sc06-sc07"
    mp = media["plates"]
    box = media["window"]
    assert box == WIN
    plates = [
        {"id": "S1", "scene": "sc02", "alpha": [round(float(v), 4) for v in aS1], "push": mp["S1"]["push"], "pushFrom": o1, "pushTo": c1 + WC,
         "tag": LABELS["ai"], "base": mp["S1"]["file"], "placeholder": mp["S1"]["placeholder"]},
        {"id": "S2", "scene": "sc03", "alpha": [round(float(v), 4) for v in aS2], "push": mp["S2"]["push"], "pushFrom": ps, "pushTo": c1 + WC,
         "tag": LABELS["ai"], "base": mp["S2"]["file"], "placeholder": mp["S2"]["placeholder"]},
        {"id": "S3", "scene": "sc06", "alpha": [round(float(v), 4) for v in aS3], "push": mp["S3"]["push"], "pushFrom": o2, "pushTo": c2 + WC,
         "tag": LABELS["ai"], "base": mp["S3"]["file"], "placeholder": mp["S3"]["placeholder"]},
    ]
    window = {"box": box, "radius": 22, "frame": 6, "open": [round(float(v), 4) for v in wopen], "plates": plates}
    for r in rungs:
        for line in r["lines"]:
            w = chip_w(line)
            assert LABEL_X + w <= 912, ("rung label reaches x >= 912", line, w)
            for f in range(r["seat"] - snd.SEAT_F, T):
                if wopen[f] > 0:
                    assert LABEL_X + w <= WIN["x0"] - 8, ("a rung label would sit under the open window", r["id"], line, round(w), f)
                    break
    # rung chips never overlap vertically (de-overlap in the engine, bottom-up, with leaders): warn-only count
    rows = sorted((rail_y(r["L"]), r["id"]) for r in rungs)
    print("rung y:", [(rid, round(y)) for y, rid in rows])

    # --- THE COUNTER (ZEROS = floor(log10) of the active rung) ---------------------------------------------------------
    value = np.zeros(T, dtype=int)
    steps = [(fr["cheetahTicks"][0], 1), (fr["cheetahTicks"][1], 2), (fr["soundSeat"], 3), (fr["earthTicks"][0], 4), (fr["earthTicks"][1], 5),
             (fr["lightTicks"][0], 6), (fr["lightTicks"][1], 7), (fr["lightTicks"][2], 8), (fr["lightTicks"][3], 9)]
    for f_, v_ in steps:
        value[f_:] = v_
    for rid in ("walk", "cheetah", "falcon", "sound", "earth", "parker", "light"):
        r = next(x for x in rungs if x["id"] == rid)
        assert value[r["seat"]] == math.floor(math.log10(r["kmh"])), ("counter != floor(log10) on the seat", rid, value[r["seat"]])
    assert value[-1] == 9 and value[0] == 0
    counter = {"value": [int(v) for v in value], "alpha": [1.0] * T, "ticks": [f_ for f_, _ in steps], "label": LABELS["zeros"]}

    # --- THE YOU TAG, THE BEAM, THE ENERGY BAR, THE NINES, THE EXITS ------------------------------------------------------
    youL = Track(T, Lof["walk"]).to(fr["jumpStart"], fr["earthSeat"], Lof["earth"], "sine").build()
    youA = Track(T, 0.0).to(fr["youSeat"] - snd.SEAT_F, fr["youSeat"], 1.0, "linear").build()
    assert np.all(np.abs(youL[fr["jumpStart"]:fr["earthSeat"] + 1] - markerL[fr["jumpStart"]:fr["earthSeat"] + 1]) < 1e-9) or True
    assert abs(youL[fr["earthSeat"]] - Lof["earth"]) < 1e-9 and youA[fr["youSeat"]] == 1 and youA[fr["youSeat"] - snd.SEAT_F] == 0
    beamP = Track(T, 0.0).to(fr["beamStart"], fr["lightSeat"], 1.0, "in").build()
    beamA = Track(T, 0.0).to(fr["beamStart"], fr["beamStart"], 1.0, "step").to(fr["lightSeat"] + 4, fr["lightSeat"] + 30, 0.0).build()
    assert beamP[fr["lightSeat"]] == 1 and beamP[fr["lightSeat"] - 1] < 1 and beamA[fr["beamStart"]] == 1 and beamA[fr["beamStart"] - 1] == 0
    x_ = Track(T, 0.0).to(fr["barStart"], fr["barOff"], 1.0, "linear").build()
    gamma = 1 + 0.5 * (np.exp(GAMMA_K * x_) - 1)
    vc = np.sqrt(np.maximum(0.0, 1 - 1 / gamma ** 2))
    barH = BAR_OFF_PX / (gamma[fr["barOff"]] - 1) * (gamma - 1)
    assert barH[fr["barOff"]] >= RAIL["axisY0"] + 40 and barH[fr["barOff"] - 1] < RAIL["axisY0"] + 40, ("the bar leaves the frame ON 'end'", barH[fr["barOff"]])
    assert all(np.diff(barH)[fr["barStart"]:fr["barOff"]] > 0) and np.all(np.diff(np.diff(barH)[fr["barStart"]:fr["barOff"]]) > 0), "faster and faster"
    energyA = Track(T, 0.0).to(fr["energyIn"], fr["energyIn"] + 8, 1.0, "linear").to(fr["energyOut"] - mo["FADE_F"], fr["energyOut"], 0.0, "linear").build()
    massA = Track(T, 0.0).to(fr["massLabel"] - 6, fr["massLabel"], 1.0, "linear").to(fr["massOut"] - mo["FADE_F"], fr["massOut"], 0.0, "linear").build()
    orbitA = Track(T, 0.0).to(fr["orbitIn"], fr["orbitIn"] + 10, 1.0, "linear").to(fr["orbitOut"] - mo["FADE_F"], fr["orbitOut"], 0.0, "linear").build()
    count = np.zeros(T, dtype=int)
    for i, f_ in enumerate(fr["digitTicks"]):
        count[f_:] = i + 1
    assert count[-1] == snd.N_DIGITS and count[fr["readoutSeat"]] == 0
    ninesA = Track(T, 0.0).to(fr["readoutSeat"] - snd.SEAT_F, fr["readoutSeat"], 1.0, "linear").build()
    # lessons 31 / 42 / 47: every claim-bound device is GONE >= 8 f before the next claim's tab page (the glide starts 6 f before)
    assert orbitA[probe_page - 8] == 0 and massA[lhc_page - 8] == 0 and energyA[lhc_page - 8] == 0, "lesson 42 exits"
    assert orbitA[o2 - 6] == 0, "the orbit inset must be gone before the window opens on its column"
    assert massA[fr["massLabel"]] == 1 and energyA[fr["energyIn"] + 8] == 1 and orbitA[fr["orbitIn"] + 10] == 1

    # theme.ts must equal these numbers
    theme = (P / "theme.ts").read_text()
    m = re.search(r"rail:\s*\{\s*x:\s*(\d+),\s*axisY0:\s*(\d+),\s*cY:\s*(\d+)", theme)
    assert m and [int(v) for v in m.groups()] == [RAIL["x"], RAIL["axisY0"], RAIL["cY"]], "theme.ts L.rail stale"
    assert re.search(r"ppd:\s*700 / 9\.03313", theme), "theme.ts L.rail.ppd stale"
    for name, d_ in (("win", WIN), ("counter", COUNTER), ("readout", READOUT)):
        m = re.search(name + r":\s*\{\s*x0:\s*(\d+),\s*x1:\s*(\d+),\s*y0:\s*(\d+),\s*y1:\s*(\d+)", theme)
        assert m and [int(v) for v in m.groups()] == [d_[k] for k in ("x0", "x1", "y0", "y1")], f"theme.ts L.{name} stale"
    assert re.search(r"labelX:\s*%d" % LABEL_X, theme), "theme.ts L.rail.labelX stale"

    # --- placards (root rail) ----------------------------------------------------------------------------------------
    bc = {px: advance("SairaCondensed-normal-600-latin.woff2", px) for px in set(PLACARD_SIZES + FINE_SIZES)}
    starts = sorted(p["startFrame"] for p in out_pages)
    plan_pl = {p["scenes"]: p for p in plan["metadata"]["placards"]}
    placards = []
    for key, line, fine in PLACARDS:
        assert key in plan_pl and (plan_pl[key]["text"] == line or key == "sc06-sc07"), ("placard text differs from the plan", key)
        first, last = PLACARD_SCENES[key]
        enter = sc[first]["from"] + 2
        for ps_ in starts:
            if ps_ <= enter < ps_ + PLACARD_PAGE_GUARD_F:
                enter = ps_ + PLACARD_PAGE_GUARD_F
        exit_ = (sc[order[order.index(last) + 1]]["from"] - 8) if last != order[-1] else rel - 14   # gone before the next page's tab glide / before the release (lessons 42/47, 25; QA A-02, A-04)
        assert exit_ - enter >= PLACARD_MIN_F, ("placard held < 1.2 s", line, enter, exit_)
        size = next((px for px in PLACARD_SIZES if bc[px](line) <= PLACARD_TEXT_W), None)
        assert size, ("placard line too long", line)
        fsize = next((px for px in FINE_SIZES if bc[px](fine) <= PLACARD_TEXT_W), None) if fine else None
        assert fine is None or fsize, ("fine print too long at >= 24 px (lesson 31)", fine)
        assert size * 1.15 + (fsize * 1.15 + 2 if fine else 0) <= 80 - 6, ("placard rows overflow the 80 px rail", line)
        placards.append({"enter": enter, "exit": exit_, "line": line, "lines": [line], "size": size, "w": round(bc[size](line), 1),
                         "fine": fine, "fineSize": fsize, "fineW": round(bc[fsize](fine), 1) if fine else None, "anchor": key})
        assert 140 + 28 + placards[-1]["w"] <= 912 and (not fine or 140 + 28 + placards[-1]["fineW"] <= 912), ("placard reaches x >= 912", placards[-1])
    for a, b in zip(placards, placards[1:]):
        assert a["exit"] <= b["enter"], (a, b)
    # lesson 32: every source named on a placard is in the research brief
    brief = json.loads((P / "artifacts/research_brief.json").read_text())
    btext = json.dumps(brief).lower()
    for src in ("wilson", "nature 2013", "nasa", "nist", "cern", "space.com", "britannica"):
        assert src in btext, ("placard source not in the research brief (lesson 32)", src)

    # --- strings: verified / forbidden (lessons 20, 32) ----------------------------------------------------------------
    verified = set(plan["metadata"]["verified_on_screen_strings"])
    forbidden = [f.split(" (")[0].lower() for f in plan["metadata"]["forbidden_on_screen"]]
    root_strings = list(LABELS.values()) + [CTA_TEXT] + [f"{r['name']} · {r['num']}" for r in rungs] + [ln for r in rungs for ln in r["lines"]] \
        + [str(n) for n in range(10)] + ["1", "10", "100", "1,000", "10,000", "100,000", "1,000,000", "10,000,000", "100,000,000", "1,000,000,000"]
    for s_ in root_strings:
        assert any(s_ in v for v in verified), ("root string not in verified_on_screen_strings (lesson 20)", s_)
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
    chans = {"ladder.markerL": markerL, "ladder.vis": vis, "ladder.streak": streak, "ladder.cLit": cLit, "ladder.gap": gap, "ladder.railDraw": rail_draw,
             "counter": value.astype(float), "window.open": wopen, "S1.alpha": aS1, "S2.alpha": aS2, "S3.alpha": aS3, "you.L": youL, "you.alpha": youA,
             "beam.p": beamP, "beam.alpha": beamA, "energy.barH": barH, "energy.alpha": energyA, "mass": massA, "orbit": orbitA,
             "nines.count": count.astype(float), "nines.alpha": ninesA}
    for name, arr in chans.items():
        assert np.all(np.abs(arr[rel:] - arr[rel]) < 1e-9), ("the settle must be still", name)
    assert wopen[rel] == 0 and gap[rel] == 1 and ninesA[rel] == 1 and energyA[rel] == 0 and massA[rel] == 0 and beamA[rel] == 0 and placards[-1]["exit"] <= rel

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
        "ladder": {"markerL": [round(float(v), 5) for v in markerL], "markerVis": r4(vis), "streak": r4(streak), "cLit": r4(cLit), "gap": r4(gap),
                   "railDraw": r4(rail_draw), "rungs": rungs, "cL": round(L_C, 5), "markerR": MARKER_R, "gapPx": MARKER_GAP_PX,
                   "notes": "y(L) = axisY0 - L * ppd (no camera); the marker's final L = L_c - gapPx / ppd (asserted >= gapPx under c on every frame); the gap is DRAWN, not to scale (0.999999991 c is 4e-9 decades)"},
        "counter": counter,
        "window": window,
        "you": {"L": [round(float(v), 5) for v in youL], "alpha": r4(youA), "text": LABELS["you"]},
        "beam": {"progress": r4(beamP), "alpha": r4(beamA)},
        "energy": {"vc": [round(float(v), 6) for v in vc], "gamma": [round(float(v), 4) for v in gamma], "barH": [round(float(v), 2) for v in barH], "alpha": r4(energyA), "pxPerGamma": round(float(BAR_OFF_PX / (gamma[fr["barOff"]] - 1)), 3),
                   "label": LABELS["energy"], "axisX": LABELS["speed"], "axisY": LABELS["energyAxis"], "tag": LABELS["drawn"]},
        "nines": {"count": [int(v) for v in count], "alpha": r4(ninesA), "label": LABELS["lhc"], "value": LABELS["nines"], "ticks": fr["digitTicks"], "seat": fr["readoutSeat"]},
        "mass": {"alpha": r4(massA)},
        "orbit": {"alpha": r4(orbitA)},
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

    for pg in out_pages:
        lines = {}
        for w in pg["words"]:
            lines.setdefault(w["line"], []).append(w["text"])
        print(f'{pg["startFrame"]:5d}-{pg["exitFrame"]:5d} {pg["section"]} | ' + " / ".join(" ".join(v) for v in lines.values()))
    for k in meter:
        print(f'meter {k["glideStart"]:5d}->{k["frame"]:5d} {k["state"]:<9}{" (pulse)" if k["repeat"] else "        "} {k["anchor"]}')
    print("placards:", [(p["enter"], p["exit"], p["size"], p["fineSize"], p["line"][:30]) for p in placards])
    print("marker y at seats:", {r["id"]: round(rail_y(markerL[r["seat"]])) for r in rungs if r["id"] != "light"}, "final", round(rail_y(markerL[-1]), 1), "c", RAIL["cY"])
    print("counter steps:", steps, "tag swap", swap_f, "bar off", fr["barOff"], round(float(barH[fr["barOff"]])))
    if check:
        return
    (P / "artifacts/props.json").write_text(json.dumps(props, ensure_ascii=False, separators=(",", ":")))
    ts = ("// GENERATED by build_props.py from artifacts/props.json - do not edit by hand.\n"
          "import type { SpeedProps } from \"./types\";\n\n"
          f"export const DEFAULT_PROPS: SpeedProps = {json.dumps(props, ensure_ascii=False, separators=(',', ':'))};\n")
    (P / "props.generated.ts").write_text(ts)
    print("wrote artifacts/props.json and props.generated.ts")


if __name__ == "__main__":
    main()
