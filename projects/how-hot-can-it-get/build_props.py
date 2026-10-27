#!/usr/bin/env python3
"""Build artifacts/props.json + props.generated.ts from the measured timeline (run from the repo root).

    python3 projects/how-hot-can-it-get/build_props.py          # write
    python3 projects/how-hot-can-it-get/build_props.py --check  # print pages + schedules only

Pattern copied from projects/what-if-earth-stopped-spinning/build_props.py (video 12, delivered, QA passed).
Inputs: artifacts/timeline.json (aligned words, sections, scene windows), artifacts/script.json (caption text, claim tags),
artifacts/scene_plan.json (caption pages, placards, verified / forbidden strings), artifacts/soundtrack_report.json (key /
SFX frames + the motion constants: build_soundtrack.py owns K), artifacts/media_report.json (window fits). Everything out
is in ABSOLUTE frames @ 30 fps.

Caption pages: scene_plan.metadata.captions.pages, RE-FLOWED so every claim starts its own page (lesson 3): s1 'absolute
zero. So how hot can' / 'it get? Is there a ceiling?' -> 'absolute zero.' / 'So how hot can it get?' / 'Is there a
ceiling?'; s2 'fifty-seven degrees. Venus sits about four' / 'hundred sixty-five, hot enough to melt' / 'lead.' ->
'fifty-seven degrees.' / 'Venus sits about four hundred sixty-five,' / 'hot enough to melt lead.'; s3 'The Sun's core
reaches about fifteen' / 'million. Yet a fusion reactor in' / 'Korea held a hundred million degrees' -> 'The Sun's core
reaches about' / 'fifteen million.' / 'Yet a fusion reactor in Korea' / 'held a hundred million degrees'; s5 'just an edge
to what we' / 'know.' -> 'just an edge' / 'to what we know.' (the plan's text otherwise verbatim; asserted). Each page =
the next run of script tokens; <= 2 lines / <= 6 words; the line break is chosen with Bricolage Grotesque 800 @ 58 px
advance widths against a 700 px budget (text column x 168-912), never after a function word or inside a bound pair. Exit
= 4 frames after the page's last word ends (held >= 36 frames when the next page allows), clipped to the next page's
start, or BUTTED to it when the gap would be < BUTT_GAP (lesson 6: the slab stays up) or the page ends inside a sentence
(',' ':' ';'); the slab is empty on frame 0 and in longer pauses, and the CTA "Floor or ceiling - which is stranger?"
takes the slab 4 f after 'know.' ends (no blink). Tones (art direction 'word states'): 'heat' on spoken NUMBER words (the
current black-body colour, lifted for contrast), 'ice' on 'floor:', else Bone.

Honesty meter (lesson 3: each state keyed to the START OF THE CAPTION PAGE that carries the claim; a state shows only while
its claim is on screen): CLAIMS below map pages -> script.json metadata.claim_tags; consecutive pages of one claim merge; a
NEW claim of the same state pulses. IDLE on the s1 question and the settle.

THE BLACK-BODY WORLD is ONE set of per-frame root schedules (props.glow / props.rail / props.zeros / props.window; types.ts)
+ the rungs and marks; shared/GlowField.tsx, shared/Ladder.tsx and shared/Window.tsx draw them on every frame, time.ts
reads them. Asserted: no glow before the sweep and never below the Draper point (sc01-sc04 stay dark); the colour sweep
crosses the three rail marks in order; every seated rung sits inside the rail; the settle (release of 'know.' -> the
end) is STILL: every channel constant (lesson 25: end-running elements end at T + 8).
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

P = Path("projects/how-hot-can-it-get")
FPS = 30
LINE_BUDGET_PX = 700
LINE_HARD_PX = 744
CAPTION_PX = 58
EXIT_TAIL = 4
MIN_PAGE = 36
WITHIN_SENTENCE_BUTT_F = 21
BUTT_GAP = 13   # A-m6: the slab stays up across gaps <= 12 f
GLIDE_LEAD = 6
PLACARD_MIN_F = 36
PLACARD_PAGE_GUARD_F = 4
PLACARD_TEXT_W = 772 - 2 * 28   # rail x 140-912, 28 px padding
PLACARD_SIZES = [26, 25, 24, 23, 22]
FINE_SIZES = [25, 24]           # lesson 31: fine print >= 24 px
CTA_TEXT = "Floor or ceiling - which is stranger?"
CTA_PX = 46
# the plan's pages, with the lesson-3 re-flows (s1, s2, s3, s5)
PAGES = [
    ("s1", "Cold has a floor:"), ("s1", "absolute zero."), ("s1", "So how hot can it get?"), ("s1", "Is there a ceiling?"),
    ("s2", "Death Valley's air once hit nearly"), ("s2", "fifty-seven degrees."), ("s2", "Venus sits about four hundred sixty-five,"),
    ("s2", "hot enough to melt lead."),
    ("s3", "The Sun's core reaches about"), ("s3", "fifteen million."), ("s3", "Yet a fusion reactor in Korea"),
    ("s3", "held a hundred million degrees"), ("s3", "for forty-eight seconds."),
    ("s4", "The hottest we've ever made:"), ("s4", "lead atoms smashed at CERN,"), ("s4", "over five trillion degrees."),
    ("s4", "So hot that protons melt into"), ("s4", "a soup of quarks."),
    ("s5", "Beyond that waits the Planck temperature,"), ("s5", "roughly a one with thirty-two zeros,"), ("s5", "where our physics breaks."),
    ("s5", "So heat may have no ceiling,"), ("s5", "just an edge"), ("s5", "to what we know."),
]
# page -> (claim id, state); claim ids are script.json metadata.claim_tags keys' research ids
CLAIMS = {
    "Cold has a floor:": ("FLOOR", "MEASURED"), "absolute zero.": ("FLOOR", "MEASURED"),
    "So how hot can it get?": ("question", "IDLE"), "Is there a ceiling?": ("question", "IDLE"),
    "Death Valley's air once hit nearly": ("DV", "MEASURED"), "fifty-seven degrees.": ("DV", "MEASURED"),
    "Venus sits about four hundred sixty-five,": ("VENUS", "MEASURED"), "hot enough to melt lead.": ("VENUS", "MEASURED"),
    "The Sun's core reaches about": ("SUN", "MEASURED"), "fifteen million.": ("SUN", "MEASURED"),
    "Yet a fusion reactor in Korea": ("KSTAR", "MEASURED"), "held a hundred million degrees": ("KSTAR", "MEASURED"),
    "for forty-eight seconds.": ("KSTAR", "MEASURED"),
    "The hottest we've ever made:": ("LHC", "PROBABLY"), "lead atoms smashed at CERN,": ("LHC", "PROBABLY"),
    "over five trillion degrees.": ("LHC", "PROBABLY"),
    "So hot that protons melt into": ("QGP", "MEASURED"), "a soup of quarks.": ("QGP", "MEASURED"),
    "Beyond that waits the Planck temperature,": ("PLANCK", "MEASURED"), "roughly a one with thirty-two zeros,": ("PLANCK", "MEASURED"),
    "where our physics breaks.": ("PLANCK", "MEASURED"),
    "So heat may have no ceiling,": ("NOCEIL", "PROBABLY"), "just an edge": ("NOCEIL", "PROBABLY"), "to what we know.": ("NOCEIL", "PROBABLY"),
}
NUMBER_WORDS = {"fiftyseven", "four", "hundred", "sixtyfive", "fifteen", "million", "fortyeight", "five", "trillion", "one", "thirtytwo"}
TONE_WORDS = {("s1", "floor"): "ice"}
WEAK_END = {"a", "an", "the", "to", "of", "and", "is", "in", "it", "at", "as", "its", "by", "for", "if", "so", "would", "will",
            "only", "very", "our", "that", "we", "no", "may", "with"}
BOUND = {("death", "valleys"), ("fiftyseven", "degrees"), ("four", "hundred"), ("hundred", "sixtyfive"), ("fifteen", "million"),
         ("hundred", "million"), ("million", "degrees"), ("fortyeight", "seconds"), ("trillion", "degrees"),
         ("thirtytwo", "zeros"), ("planck", "temperature"), ("melt", "lead"), ("lead", "atoms"), ("fusion", "reactor"),
         ("suns", "core"), ("absolute", "zero"), ("no", "ceiling"), ("an", "edge"), ("our", "physics")}
PLACARD_SCENES = {"sc01-sc02": ("sc01", "sc02"), "sc03-sc04": ("sc03", "sc04"), "sc05-sc06": ("sc06", "sc06"),
                  "sc07-sc09": ("sc07", "sc09"), "sc10-sc13": ("sc10", "sc13")}
# the black-body world (mirrored in theme.ts L.rail / shared/blackbody.ts; asserted)
C_TO_K = 273.15
DRAPER_K = 798.15
AXIS_Y0, TOP_Y, FLOOR_Y = 990, 350, 1060
LO = 2.42                 # log10 K at the axis bottom (Death Valley 329.85 K = 2.518 sits just above it)
TOP_LOW = 3.18            # sc03-sc04: Venus (2.8675) and the Draper point (2.902) read ~30 px apart
TOP_MARGIN = 0.30         # the sweep zooms out keeping the cursor TOP_MARGIN decades under the top
TOP_KSTAR = 8.40
TOP_LHC = 13.10
TOP_PLANCK = 32.55
CAM_TILT_PX = 40.0
SWEEP_DRAPER_F = 7     # sweepStart + 7 = the number passes 525 degC (~f490)
SWEEP_TAIL_F = 7       # the converged blue-white is reached 7 f before the seat (~f545), then the fast roll
I_MAX, I_SETTLE = 0.80, 0.42
I_FULL_LG = 3.55          # the glow reaches I_MAX by ~3,550 K
SLAB_CLAMP = 0.40         # glow under the honesty tab / caption slab clamped to ~40 %
RUNGS = [   # id, kelvin, num, label (verified strings), seat key, intro scene (its end = compactFrom)
    ("dv", 56.7 + C_TO_K, "56.7 °C", "Death Valley · 1913 · air", "dvSeat", "sc03"),
    ("venus", 464 + C_TO_K, "~464 °C", "Venus surface", "venusSeat", "sc04"),
    ("suncore", 15e6 + C_TO_K, "~15,000,000 °C", "Sun's core", "sunCoreSeat", "sc05"),
    ("kstar", 1e8 + C_TO_K, "100,000,000 °C", "KSTAR · Korea · 48 s · 2024", "kstarSeat", "sc06"),
    ("lhc", 5e12, "> 5,000,000,000,000 K", "LHC · CERN · 2012 · record estimate", "lhcSeat", "sc08"),
    ("planck", 1.417e32, "1.4 × 10^32 K", "Planck temperature", "planckMark", None),
]
MARKS = [("draper", DRAPER_K, "first visible glow ~525 °C"), ("sunsurface", 5500 + C_TO_K, "Sun's surface ~5,500 °C"),
         ("converge", 40000.0, "colour barely changes past ~40,000 K")]
LABELS = {"floor": "the floor", "floorValue": "0 K = -273.15 °C", "logScale": "log scale", "chip": "black-body colour",
          "planck": "Planck temperature", "fray": "where known physics stops working", "zerosUnit": "zeros"}
LUT_TAG = "false colour"

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
    send = lambda sid: sc[sid]["from"] + sc[sid]["durationInFrames"]
    fr = sound["frames"]
    mo = sound["motion"]
    assert mo["SEAT_F"] == snd.SEAT_F and mo["COMPRESS_F"] == snd.COMPRESS_F
    T = total
    rel = fr["knowEndFrame"]

    words = [{**w, "f0": round(w["start"] * FPS), "f1": max(round(w["end"] * FPS), round(w["start"] * FPS) + 2)} for w in tl["words"]]
    for sec in script["sections"]:
        assert [w["text"] for w in words if w["section"] == sec["id"]] == sec["text"].split(), sec["id"]
    for w in words:
        n_ = norm(w["text"])
        w["tone"] = TONE_WORDS.get((w["section"], n_), "heat" if n_ in NUMBER_WORDS else "plain")

    # --- caption pages ------------------------------------------------------------------------------------------
    planp = plan["metadata"]["captions"]["pages"]
    for sid in ("s1", "s2", "s3", "s4", "s5"):
        assert " ".join(p["page"] for p in planp if p["section"] == sid) == " ".join(t for s_, t in PAGES if s_ == sid), sid
    text_w = lambda ws: width(" ".join(w["text"] for w in ws))

    def penalty(ws, k) -> int:
        """a break inside a bound pair costs 400; after a weak function word 200 (so 'held a / hundred million degrees'
        beats 'held a hundred / million degrees')"""
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
        if nxt - exit_ < BUTT_GAP:
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
    assert out_pages[-1]["exitFrame"] == fr["ctaFrame"], ("the CTA must take the slab as the last page leaves", out_pages[-1]["exitFrame"], fr["ctaFrame"])
    cta_lines = [CTA_TEXT[: CTA_TEXT.index(" - ") + 2], CTA_TEXT[CTA_TEXT.index(" - ") + 3:]]
    cta_adv = advance("BricolageGrotesque-normal-800-latin.woff2", CTA_PX)
    assert " ".join(cta_lines) == CTA_TEXT and all(cta_adv(l) <= LINE_BUDGET_PX for l in cta_lines), cta_lines

    # --- honesty meter ---------------------------------------------------------------------------------------------
    tags_ = script["metadata"]["claim_tags"]
    for cid, st in set(CLAIMS.values()):
        if cid == "question":
            hits = [v for sec in tags_.values() for k, v in sec.items() if "(question)" in k]
            assert hits == ["idle"], hits
            continue
        hits = [v for sec in tags_.values() for k, v in sec.items() if f"({cid})" in k]
        assert hits and all(h == st for h in hits), ("claim state != script.json claim_tags", cid, st, hits)
    meter = [{"frame": 0, "glideStart": 0, "state": "IDLE", "sublabel": "", "section": "", "anchor": "frame 0", "claim": "none (cold open)", "repeat": False}]
    prev_claim = None
    for (sid, text), pg in zip(PAGES, out_pages):
        cid, state = CLAIMS[text]
        if cid == prev_claim:
            continue
        prev = meter[-1]
        f = pg["startFrame"]
        meter.append({"frame": f, "glideStart": max(0, f - GLIDE_LEAD), "state": state, "sublabel": "", "section": sid,
                      "anchor": f"page '{text}'", "claim": cid, "repeat": state == prev["state"] and state != "IDLE"})
        prev_claim = cid
    meter.append({"frame": fr["ctaFrame"], "glideStart": fr["ctaFrame"] - GLIDE_LEAD, "state": "IDLE", "sublabel": "", "section": "settle",
                  "anchor": "the settle CTA", "claim": "none (the settle)", "repeat": False})
    for a, b in zip(meter, meter[1:]):
        assert b["glideStart"] >= a["glideStart"], (a, b)
    keyed = [k["frame"] for k in meter[1:]]
    assert len(keyed) == len(set(keyed)), ("two claims keyed on one caption page (lesson 3)", keyed)

    # --- THE GLOW: temperature + intensity per frame --------------------------------------------------------------------
    lgV, lgSC = math.log10(464 + C_TO_K), math.log10(15e6 + C_TO_K)
    lgD = math.log10(DRAPER_K)
    S, E_ = fr["sweepStart"], fr["sunCoreSeat"]
    rk = {r[0]: r for r in RUNGS}
    lg = np.full(T, lgV)
    # piecewise (coordinator request): Venus -> the Draper point by SWEEP_DRAPER_F, then a SLOW log-linear dwell through
    # the visible colours (798 K -> 40,000 K) until SWEEP_CONVERGE_F, then a fast ease-in roll to 15 million degC ON the seat
    lgC = math.log10(40000.0)
    fD, fC = S + SWEEP_DRAPER_F, E_ - SWEEP_TAIL_F
    for f in range(T):
        if S <= f < fD:
            lg[f] = lgV + (lgD - lgV) * (f - S) / (fD - S)
        elif fD <= f < fC:
            lg[f] = lgD + (lgC - lgD) * (f - fD) / (fC - fD)
        elif fC <= f < E_:
            lg[f] = lgC + (lgSC - lgC) * ((f - fC) / (E_ - fC)) ** 2
        elif f >= E_:
            lg[f] = lgSC
    # after the sweep the glow temperature follows the rungs (the colour no longer changes: asserted below)
    for key, rid in (("kstarSeat", "kstar"), ("lhcSeat", "lhc"), ("planckMark", "planck")):
        a = fr[key] - snd.SEAT_F
        target = math.log10(rk[rid][1])
        for f in range(a, T):
            lg[f] = lg[a - 1] + (target - lg[a - 1]) * min(1.0, (f - a + 1) / snd.SEAT_F)
    gk = 10 ** lg
    gi = np.clip((lg - lgD) / (I_FULL_LG - lgD), 0, 1) ** 1.3 * I_MAX
    gi[: S] = 0.0
    cs, SG = fr["closingStart"], mo["SETTLE_GLOW_F"]
    for f in range(cs, T):
        u = min(1.0, (f - cs) / SG)
        gi[f] = I_MAX + (I_SETTLE - I_MAX) * (0.5 - 0.5 * math.cos(math.pi * u))
    assert all(gi[f] == 0 for f in range(T) if gk[f] < DRAPER_K), "no glow below the Draper point"
    assert all(gi[f] == 0 for f in range(S)), "sc01-sc04 stay dark"
    assert gi[E_] == I_MAX and cs + SG <= rel

    # --- THE LADDER RAIL ---------------------------------------------------------------------------------------------
    top = Track(T, TOP_LOW).build()
    for f in range(S, E_ + 1):
        top[f] = max(TOP_LOW, lg[f] + TOP_MARGIN)
    top[E_ + 1:] = lgSC + TOP_MARGIN
    tr = Track(T, lgSC + TOP_MARGIN).to(fr["windowOpen2"], fr["windowOpen2"] + mo["ZOOM_F"], TOP_KSTAR) \
        .to(fr["compress"], fr["compress"] + mo["COMPRESS_F"], TOP_LHC).to(fr["drift"], fr["drift"] + mo["DRIFT_F"], TOP_PLANCK).build()
    top[E_ + 1:] = tr[E_ + 1:]
    ppd = (AXIS_Y0 - TOP_Y) / (top - LO)
    camY = Track(T, 0.0).to(fr["camTilt"], fr["camTilt"] + mo["CAM_TILT_F"], CAM_TILT_PX).to(fr["windowOpen"], fr["windowOpen"] + mo["CAM_RETURN_F"], 0.0).build()
    floor = Track(T, 0.0).to(fr["floorDraw"], fr["floorDraw"] + mo["FLOOR_DRAW_F"], 1.0, "out").build()
    spine = Track(T, 0.0).to(fr["spineStart"], fr["spineStart"] + mo["SPINE_DRAW_F"], 1.0, "out").build()
    fray = Track(T, 0.0).to(fr["fray"], fr["fray"] + mo["FRAY_F"], 1.0, "sine").build()
    q = Track(T, 0.0).to(fr["qStart"] - 1, fr["qStart"] - 1 + mo["Q_DRAW_F"], 1.0, "sine").build()
    qa = Track(T, 1.0).to(fr["planckMark"], fr["planckMark"] + mo["Q_DIM_F"], 0.5).to(fr["qFade"], fr["qFade"] + mo["Q_FADE_F"], 0.0).build()
    cur = Track(T, 0.0).to(S, S + 6, 1.0).to(E_, E_ + snd.SEAT_F, 0.0).build()
    chip = Track(T, 0.0).to(S, S + 8, 1.0).build()
    WO = mo["WINDOW_OPEN_F"]
    # QA B10 / C-m3: the open eases over 6 f with its first visible frame ON the hiss / hum (no 72 % pop: WindowFrame is linear in
    # open), the close is ease-in-out over 8 f (no end snap)
    WOE = 6
    wopen = Track(T, 0.0).to(fr["windowOpen"] - 1, fr["windowOpen"] - 1 + WOE, 1.0, "outquad").to(fr["windowClose1"], fr["windowClose1"] + WO, 0.0, "sine") \
        .to(fr["windowOpen2"] - 1, fr["windowOpen2"] - 1 + WOE, 1.0, "outquad").to(fr["windowClose2"], fr["windowClose2"] + WO, 0.0, "sine").build()
    for k_ in ("windowOpen", "windowOpen2"):
        assert wopen[fr[k_] - 1] == 0 and 0.25 < wopen[fr[k_]] < 0.4, ("the window's first visible frame is its sound frame", k_)
    wdim = Track(T, 0.0).to(fr["compress"], fr["compress"] + mo["DIM_F"], 0.55).to(fr["soupStart"], fr["soupStart"] + mo["DIM_F"], 0.8).build()
    wlut = Track(T, 0.0).to(fr["lutOn"], fr["lutOn"] + mo["LUT_F"], 1.0).to(fr["venusXfade"], fr["venusXfade"] + mo["MEDIA_XFADE_F"], 0.0).build()
    # QA B5: rail labels are hidden while a plate is up and only return once the closing plate is mostly gone (no ghosting)
    compact_vis = np.clip(1.0 - wopen / 0.35, 0.0, 1.0)
    railY = lambda L_, f: AXIS_Y0 + camY[f] - (L_ - LO) * ppd[f]

    rungs = []
    for rid, kel, num, label, seat_key, intro in RUNGS:
        seat = fr[seat_key]
        cf = send(intro) if intro else T + 8
        rungs.append({"id": rid, "kelvin": kel, "L": round(math.log10(kel), 5), "num": num, "label": label, "seat": seat,
                      "compactFrom": cf, "glows": kel >= DRAPER_K})
        for f in range(seat, T):
            y = railY(math.log10(kel), f)
            assert TOP_Y - 12 <= y <= AXIS_Y0 + 2 + camY[f], ("a seated rung leaves the rail", rid, f, round(y, 1))
    assert not rungs[0]["glows"] and not rungs[1]["glows"] and all(r["glows"] for r in rungs[2:]), "DV / Venus do not glow"
    marks = []
    for mid, kel, text in MARKS:
        Lm = math.log10(kel)
        at = fr["draperMark"] if mid == "draper" else int(next(f for f in range(S, E_ + 1) if lg[f] >= Lm))
        marks.append({"id": mid, "kelvin": kel, "L": round(Lm, 5), "text": text, "at": at})
    assert marks[0]["at"] < S < marks[1]["at"] < marks[2]["at"] <= E_, marks
    zero_val = np.full(T, 12, dtype=int)
    for tk in fr["zeroTicks"]:
        zero_val[tk:] += 1
    assert zero_val[-1] == 32 and zero_val[fr["zeroTicks"][-1]] == 32 and zero_val[fr["zeroTicks"][0] - 1] == 12
    # QA B6 / A-m3: the chip never crosses the LHC compact number: it fades out under the LHC rung, jumps (unseen) to the Planck
    # rung, and fades back in ON the Planck seat (fully visible 8 f later, well before the first zero tick)
    zalpha = Track(T, 0.0).to(fr["lhcSeat"] - snd.SEAT_F, fr["lhcSeat"], 1.0, "in").to(fr["planckMark"] - 22, fr["planckMark"] - 14, 0.0) \
        .to(fr["planckMark"], fr["planckMark"] + 8, 1.0).build()
    zL = Track(T, math.log10(5e12)).to(fr["planckMark"] - 12, fr["planckMark"] - 11, math.log10(1.417e32), "step").build()
    assert zalpha[fr["planckMark"] - 12] == 0 and fr["planckMark"] + 8 < fr["zeroTicks"][0]
    zeros = {"value": [int(v) for v in zero_val], "alpha": [round(float(v), 4) for v in zalpha], "L": [round(float(v), 5) for v in zL],
             "seat": fr["lhcSeat"], "ticks": fr["zeroTicks"]}

    # --- THE WINDOW ------------------------------------------------------------------------------------------------------
    mc, fits, win = media["clips"], media["fits"], media["window"]
    XF = mo["MEDIA_XFADE_F"]
    wmedia = [
        {"id": "K1", "kind": "clip", "src": mc["K1"]["file"], "first": media["frames"]["K1_first"], "last": media["frames"]["K1_first"],
         "frames": mc["K1"]["frames"], "mode": "forward", "start": fr["windowOpen"], "from": fr["windowOpen"], "to": fr["venusXfade"], "xf": XF,
         "push": [1.0, 1.02], "fit": fits["K1"], "tag": "AI impression", "srcRange30": mc["K1"]["srcRange30"]},
        {"id": "S2", "kind": "still", "src": media["images"]["S2"], "first": media["images"]["S2"], "last": media["images"]["S2"], "frames": 1,
         "mode": "still", "start": fr["venusXfade"], "from": fr["venusXfade"], "to": fr["windowClose1"] + WO, "xf": XF,
         "push": [1.0, 1.04], "fit": fits["S2"], "tag": "AI impression · not a photo", "srcRange30": [0, 0]},
        {"id": "K2", "kind": "clip", "src": mc["K2"]["file"], "first": media["frames"]["K2_first"], "last": media["frames"]["K2_last"],
         "frames": mc["K2"]["frames"], "mode": "forward", "start": fr["windowOpen2"], "from": fr["windowOpen2"], "to": fr["colliderXfade"], "xf": XF,
         "push": [1.0, 1.03], "fit": fits["K2"], "tag": "AI illustration", "srcRange30": mc["K2"]["srcRange30"]},
        {"id": "S4", "kind": "still", "src": media["images"]["S4"], "first": media["images"]["S4"], "last": media["images"]["S4"], "frames": 1,
         "mode": "still", "start": fr["colliderXfade"], "from": fr["colliderXfade"], "to": fr["windowClose2"] + WO, "xf": XF,
         "push": [1.0, 1.05], "fit": fits["S4"], "tag": "AI illustration", "srcRange30": [0, 0]},
    ]
    k1 = wmedia[0]
    assert k1["to"] + XF - k1["start"] <= mc["K1"]["frames"] - 1, "K1 must stay inside its clean range (forward only, no hold)"
    for a, b in zip(wmedia, wmedia[1:]):
        assert a["to"] <= b["from"], (a["id"], b["id"])
    window = {"box": win, "radius": 28, "open": [round(float(v), 4) for v in wopen], "dim": [round(float(v), 4) for v in wdim],
              "lut": [round(float(v), 4) for v in wlut], "media": wmedia, "lutTag": LUT_TAG}

    # theme.ts must equal the measurements (FITS, the window box, the rail constants)
    theme = (P / "theme.ts").read_text()
    for key in ("K1", "S2", "K2", "S4"):
        f = fits[key]
        m = re.search(key + r":\s*\{\s*w:\s*(\d+),\s*h:\s*(\d+),\s*scale:\s*([\d.]+),\s*left:\s*(-?[\d.]+),\s*top:\s*(-?[\d.]+)", theme)
        assert m, f"theme.ts FITS.{key} missing"
        got = [float(v) for v in m.groups()]
        assert got == [f["w"], f["h"], f["scale"], f["left"], f["top"]], (f"theme.ts FITS.{key} is stale", got, f)
    m = re.search(r"window:\s*\{\s*x0:\s*(\d+),\s*x1:\s*(\d+),\s*y0:\s*(\d+),\s*y1:\s*(\d+)", theme)
    assert m and [int(v) for v in m.groups()] == [win[k] for k in ("x0", "x1", "y0", "y1")], "theme.ts L.window stale"
    m = re.search(r"rail:\s*\{\s*x:\s*(\d+),\s*axisY0:\s*(\d+),\s*topY:\s*(\d+),\s*floorY:\s*(\d+)", theme)
    assert m and [int(v) for v in m.groups()] == [180, AXIS_Y0, TOP_Y, FLOOR_Y], "theme.ts L.rail stale"

    # --- placards (root rail) ----------------------------------------------------------------------------------------
    bc = {px: advance("SairaCondensed-normal-700-latin.woff2", px) for px in set(PLACARD_SIZES + FINE_SIZES)}
    starts = sorted(p["startFrame"] for p in out_pages)
    placards = []
    for pl in plan["metadata"]["placards"]:
        first, last = PLACARD_SCENES[pl["scenes"]]
        enter = sc[first]["from"] + 2
        for ps in starts:
            if ps <= enter < ps + PLACARD_PAGE_GUARD_F:
                enter = ps + PLACARD_PAGE_GUARD_F
        exit_ = sc[order[order.index(last) + 1]]["from"] if last != order[-1] else rel   # the last one is gone by the settle
        assert exit_ - enter >= PLACARD_MIN_F, ("placard held < 1.2 s", pl, enter, exit_)
        line, fine = pl["text"], pl.get("fine_print")
        size = next((px for px in PLACARD_SIZES if bc[px](line) <= PLACARD_TEXT_W), None)
        assert size, ("placard line too long", line)
        fsize = next((px for px in FINE_SIZES if bc[px](fine) <= PLACARD_TEXT_W), None) if fine else None
        assert fine is None or fsize, ("fine print too long at >= 24 px (lesson 31)", fine)
        rows_h = size * 1.15 + (fsize * 1.15 + 2 if fine else 0)
        assert rows_h <= 80 - 6, ("placard rows overflow the 80 px rail", line, rows_h)
        placards.append({"enter": enter, "exit": exit_, "line": line, "lines": [line], "size": size, "w": round(bc[size](line), 1),
                         "fine": fine, "fineSize": fsize, "fineW": round(bc[fsize](fine), 1) if fine else None, "anchor": pl["scenes"]})
        assert 140 + 28 + placards[-1]["w"] <= 912 and (not fine or 140 + 28 + placards[-1]["fineW"] <= 912), ("placard reaches x >= 912", placards[-1])
    for a, b in zip(placards, placards[1:]):
        assert a["exit"] <= b["enter"], (a, b)

    # --- strings: verified / forbidden (lessons 20, 32) ----------------------------------------------------------------
    verified = set(plan["metadata"]["verified_on_screen_strings"])
    forbidden = [f.split(" (")[0].lower() for f in plan["metadata"]["forbidden_on_screen"]]
    root_strings = list(LABELS.values()) + [LUT_TAG] + [m_["tag"] for m_ in wmedia] + [r["num"] for r in rungs] + [r["label"] for r in rungs] \
        + [m_["text"] for m_ in marks] + [f"{n} zeros" for n in range(12, 33)]
    for s_ in root_strings:
        if s_ == "zeros":
            continue
        assert s_ in verified, ("root string not in verified_on_screen_strings (lesson 20)", s_)
    lit = set()
    for f in sorted((P / "scenes").glob("u*/*.ts*")):
        src = f.read_text()
        lit |= set(re.findall(r'text(?:=|:\s*)\{?"([^"]+)"', src))
        lit |= set(re.findall(r'(?:TEXT|LINE|LABEL|NUM)\w*\s*=\s*"([^"]+)"', src))
    bad = sorted(t_ for t_ in lit if not any(t_ in v for v in verified))
    assert not bad, ("on-screen literals not in verified_on_screen_strings (lesson 20)", bad)
    placard_text = " ".join(p["line"] + " " + (p["fine"] or "") for p in placards)
    allscreen = " ".join(sorted(verified | lit | {CTA_TEXT} | set(root_strings))).lower() + " " + placard_text.lower()
    assert not [f for f in forbidden if f in allscreen], ("forbidden_on_screen string on screen", [f for f in forbidden if f in allscreen])
    assert "nasa" not in allscreen, "lesson 32: no 'NASA' on screen"
    assert "^" not in " ".join(LABELS.values()), "'^' is never set: the exponent is drawn"
    print("verified on-screen literals in scenes:", len(lit))

    # --- the settle is STILL (lesson 25) ---------------------------------------------------------------------------------
    chans = {"glow.k": gk, "glow.i": gi, "rail.lo": np.full(T, LO), "rail.ppd": ppd, "rail.camY": camY, "rail.floor": floor, "rail.spine": spine,
             "rail.fray": fray, "rail.q": q, "rail.qAlpha": qa, "rail.cursor": cur, "rail.chip": chip, "rail.compactVis": compact_vis,
             "window.open": wopen, "window.dim": wdim, "window.lut": wlut, "zeros.alpha": zalpha, "zeros.L": zL, "zeros.value": zero_val.astype(float)}
    for name, arr in chans.items():
        assert np.all(np.abs(arr[rel:] - arr[rel]) < 1e-9), ("the settle must be still", name)
    assert wopen[rel] == 0 and qa[rel] == 0 and fray[rel] == 1 and chip[rel] == 1
    assert placards[-1]["exit"] <= rel

    rd = lambda a, k=4: [round(float(v), k) for v in a]
    props = {
        "timeline": {
            "fps": FPS, "width": 1080, "height": 1920, "total_frames": total, "lead_frames": round(tl["lead_seconds"] * FPS),
            "sections": [{"id": s["id"], "from": s["from"], "durationInFrames": s["durationInFrames"]} for s in tl["sections"]],
            "scenes": [{"id": s["id"], "section": s["section"], "from": s["from"], "durationInFrames": s["durationInFrames"]} for s in tl["scenes"]],
            "words": [{"section": w["section"], "text": w["text"], "f0": w["f0"], "f1": w["f1"]} for w in words],
        },
        "captionPages": out_pages,
        "meter": meter,
        "glow": {"k": rd(gk, 1), "i": rd(gi), "iMax": I_MAX, "iSettle": I_SETTLE, "slabClamp": SLAB_CLAMP,
                 "notes": "per-frame: k = the glow temperature (K; colour = shared/blackbody.ts bbRgb(k)), i = intensity 0..1 (0 below the Draper point)"},
        "rail": {"lo": rd(np.full(T, LO), 5), "ppd": rd(ppd, 3), "camY": rd(camY, 2), "floor": rd(floor), "spine": rd(spine), "fray": rd(fray),
                 "q": rd(q), "qAlpha": rd(qa), "cursor": rd(cur), "chip": rd(chip), "compactVis": rd(compact_vis),
                 "axisY0": AXIS_Y0, "topY": TOP_Y, "floorY": FLOOR_Y, "x": 180, "qX": 180, "qY": 252, "qK": 1800,
                 "notes": "y(L, f) = axisY0 + camY[f] - (L - lo[f]) * ppd[f]; L = log10 kelvin; the floor is a fixed callback at floorY + camY (0 K is not on a log axis)"},
        "rungs": rungs,
        "marks": marks,
        "zeros": zeros,
        "window": window,
        "placards": placards,
        "labels": LABELS,
        "cta": {"text": CTA_TEXT, "lines": cta_lines, "frame": fr["ctaFrame"]},
        "settle": {"from": rel, "freezeFrom": rel, "chordFrame": fr["chordFrame"]},
        "freezes": [],
        "audio": {"soundtrack": "audio/soundtrack.wav", **fr},
        "layers": "all",
        "exportVariant": "main",
    }

    for pg in out_pages:
        lines = {}
        for w in pg["words"]:
            lines.setdefault(w["line"], []).append(w["text"] + {"heat": "*", "ice": "~", "plain": ""}[w["tone"]])
        print(f'{pg["startFrame"]:5d}-{pg["exitFrame"]:5d} {pg["section"]} | ' + " / ".join(" ".join(v) for v in lines.values()))
    for k in meter:
        print(f'meter {k["glideStart"]:5d}->{k["frame"]:5d} {k["state"]:<9}{" (pulse)" if k["repeat"] else "        "} {k["anchor"]}')
    print("placards:", [(p["enter"], p["exit"], p["size"], p["fineSize"], p["line"][:30]) for p in placards])
    print("rungs:", [(r["id"], r["seat"], r["compactFrom"], round(railY(r["L"], min(T - 1, max(r["seat"], 0))), 1), round(railY(r["L"], T - 1), 1)) for r in rungs])
    print("marks:", [(m_["id"], m_["at"], round(railY(m_["L"], m_["at"]), 1)) for m_ in marks])
    print("ppd at key frames:", {k: round(float(ppd[fr[k]]), 1) for k in ("dvSeat", "sweepStart", "sunCoreSeat", "kstarSeat", "lhcSeat", "planckMark")}, "end", round(float(ppd[-1]), 2))
    print("glow:", {f: (round(float(gk[f])), round(float(gi[f]), 3)) for f in (S, S + 20, S + 40, S + 60, E_, rel)})
    print("clipped highlights:", clipped)
    if check:
        return
    (P / "artifacts/props.json").write_text(json.dumps(props, ensure_ascii=False, separators=(",", ":")))
    ts = ("// GENERATED by build_props.py from artifacts/props.json - do not edit by hand.\n"
          "import type { HotProps } from \"./types\";\n\n"
          f"export const DEFAULT_PROPS: HotProps = {json.dumps(props, ensure_ascii=False, separators=(',', ':'))};\n")
    (P / "props.generated.ts").write_text(ts)
    print("wrote artifacts/props.json and props.generated.ts")


if __name__ == "__main__":
    main()
