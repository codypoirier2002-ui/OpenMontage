#!/usr/bin/env python3
"""Sync artifacts/scene_plan.json with the foundation's measurements (idempotent; run from the repo root, after
align_narration.py and prepare_media.py):

    python3 projects/how-long-can-anything-last/sync_scene_plan.py

Video 19 ("How Long Can Anything Last?", the Lifespan Column). The plan was drafted before the build; this script makes its
metadata the build's and keeps it in step:
  * every scene's start / end from the measured timeline (anchor onset - 2 f; artifacts/timeline.json) and a description of what
    the scene shows; metadata.total_* = the film; the planned values stay in metadata.planned_total_*;
  * metadata.captions.pages = the caption pages AS BUILT (<= 2 lines, <= 6 words, every claim starts its own page, no 2-word
    orphans); build_props.py reads them and asserts they cover the narration;
  * metadata.placards (5, the source rail), palette, signature device, verified_on_screen_strings, forbidden_on_screen,
    honesty_grammar, stills (S1-S3 as staged by prepare_media.py), safe_areas as built (theme.ts L);
  * metadata.foundation_changes lists the divergences; validated against schemas/artifacts/scene_plan.schema.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

P = Path("projects/how-long-can-anything-last")

PAGES = [
    ("s1", "An adult mayfly"), ("s1", "lives about a day."), ("s1", "You live about seventy-three years."),
    ("s1", "A tortoise named Jonathan"), ("s1", "is nearly two hundred."),
    ("s2", "A Greenland shark can live"), ("s2", "about four hundred years."),
    ("s2", "The oldest known tree,"), ("s2", "a bristlecone pine,"), ("s2", "is nearly five thousand."),
    ("s3", "The Sun will shine"), ("s3", "for about ten billion years."),
    ("s3", "A small red dwarf star,"), ("s3", "for four trillion."),
    ("s4", "A proton, though,"), ("s4", "has never been seen to decay."), ("s4", "It would take more than"), ("s4", "a billion trillion trillion years."),
    ("s5", "That's thirty-three zeros,"), ("s5", "and still nobody"), ("s5", "has caught one going."),
    ("s5", "Maybe something really does last forever."),
]
PLACARDS = [
    {"scenes": "sc01-sc02", "text": "mayfly adults ~30 min-2 days (NC State) · people 73.3 yr (WHO)", "fine_print": "global life expectancy at birth, 2023"},
    {"scenes": "sc03-sc05", "text": "Jonathan ~193 yr (Guinness) · shark 392 ± 120 yr (Nielsen 2016)", "fine_print": "oldest known bristlecone ~4,850 yr (Guinness)"},
    {"scenes": "sc06-sc07", "text": "Sun ~10 billion yr (NASA) · red dwarf ~4 trillion yr (Space.com)", "fine_print": "stellar-model predictions, not measured lifetimes"},
    {"scenes": "sc08-sc11", "text": "no proton decay seen: lifetime > 10³³ yr (Super-Kamiokande)", "fine_print": "a lower limit, not a measured lifetime"},
    {"scenes": "sc12", "text": "whether protons decay at all is unknown (APS Physics)", "fine_print": "some theories predict decay near 10³⁴-10³⁶ yr"},
]
SUPD = "⁰¹²³⁴⁵⁶⁷⁸⁹"
DECADES = [f"10{''.join('⁻' if c == '-' else SUPD[int(c)] for c in str(n))} yr" for n in range(-3, 34, 3)]
RUNG_LINES = ["MAYFLY · ~1 day", "YOU · ~73 yr", "TORTOISE · ~190 yr", "SHARK · ~400 yr", "PINE · ~4,800 yr", "SUN · ~10 billion yr", "RED DWARF · ~4 trillion yr",
              "PROTON", "> 10³³ yr", "lower limit"]
READOUT = "1" + "0" * 33 + " yr"
VERIFIED = ["years · log scale", *DECADES, "ZEROS", *[str(n) for n in range(0, 34)], *RUNG_LINES,
            "forever?", "Sun", "red dwarf", "~10 billion yr", "~4 trillion yr", "no decay seen", "water detector", READOUT,
            "AI impression", "drawn · not to scale", "What's the oldest thing you've ever seen?"]
FORBIDDEN = ["proven forever (no proton decay is a lower limit, not a lifetime)", "protons last forever", "protons are stable", "the red dwarf has died",
             "red dwarfs live trillions of years (observed)", "actual size"]


SCENE_TEXT = {
    "sc01": "Render: atelier component sc01. 'Lifespan Column': the rail draws bottom -> top; the marker sits on MAYFLY ~1 day, ZEROS 0 seats on 'day'.",
    "sc02": "Render: atelier component sc02. The marker climbs to YOU ~73 yr (ZEROS 1).",
    "sc03": "Render: atelier component sc03. The window opens on the AI tortoise plate; TORTOISE ~190 yr seats (ZEROS 2).",
    "sc04": "Render: atelier component sc04. The window crossfades to the AI Greenland shark plate; SHARK ~400 yr seats (ZEROS stays 2).",
    "sc05": "Render: atelier component sc05. The window crossfades to the AI bristlecone pine plate; PINE ~4,800 yr seats (ZEROS 3).",
    "sc06": "Render: atelier component sc06. The window shows a DRAWN Sun; the marker climbs to SUN ~10 billion yr, ZEROS 4 -> 10.",
    "sc07": "Render: atelier component sc07. A much smaller DRAWN red dwarf joins the Sun; RED DWARF ~4 trillion yr seats (ZEROS 12).",
    "sc08": "Render: atelier component sc08. The window shows a DRAWN detector tank, nothing flashing, 'no decay seen'.",
    "sc09": "Render: atelier component sc09. The marker climbs to the PROTON's lower limit (> 10^33 yr, dashed open rung + up arrow) as ZEROS runs 12 -> 33; the rail BREAKS above it.",
    "sc10": "Render: atelier component sc10. The readout types 1 followed by 33 zeros under the tank window.",
    "sc11": "Render: atelier component sc11. The readout holds, then fades; the tank stays quiet.",
    "sc12": "Render: atelier component sc12. A dashed 'forever?' line rises through the break under the MAYBE tab; the finished line, the settle, the CTA.",
}


def main() -> None:
    plan = json.loads((P / "artifacts/scene_plan.json").read_text())
    tl = json.loads((P / "artifacts/timeline.json").read_text())
    media = json.loads((P / "artifacts/media_report.json").read_text())
    md = plan["metadata"]
    md.setdefault("planned_total_duration_seconds", md.get("total_duration_seconds"))
    md.setdefault("planned_total_frames", md.get("total_frames"))
    tls = {s["id"]: s for s in tl["scenes"]}
    for sc in plan["scenes"]:
        s = tls[sc["id"]]
        sc["start_seconds"] = round(s["from"] / 30, 3)
        sc["end_seconds"] = round((s["from"] + s["durationInFrames"]) / 30, 3)
    md["total_duration_seconds"] = tl["total_seconds"]
    md["total_frames"] = tl["total_frames"]
    md["timing_basis"] = (f"MEASURED (foundation): every scene boundary after sc01 = its anchor word's measured onset - 2 frames "
                          f"(align_narration.py, the clean WAVs); the film = {tl['lead_seconds']} s lead + {tl['narration_seconds']} s narration to the "
                          f"release of 'one.' ({tl['way_end_seconds']} s) + {tl['settle_seconds']} s settle. Planned values kept in planned_total_*.")
    words = {}
    for w in tl["words"]:
        words.setdefault(w["section"], []).append(w["text"])
    for sid, toks in words.items():
        assert " ".join(t for s_, t in PAGES if s_ == sid) == " ".join(toks), ("caption pages do not cover the narration", sid)
    md.setdefault("captions", {})
    md["captions"]["pages"] = [{"section": s_, "page": t} for s_, t in PAGES]
    md["captions"]["note"] = "re-flowed by the foundation (lesson 3): every claim starts its own page; <= 2 lines / <= 6 words; no 2-word orphan"
    md["placards"] = PLACARDS
    md["verified_on_screen_strings"] = VERIFIED
    md["forbidden_on_screen"] = FORBIDDEN
    md["honesty_grammar"] = ("MEASURED solid tab (people's life expectancy; the proton's LOWER LIMIT, sublabel 'lower limit'; the arithmetic of the zeros); "
                             "PROBABLY outline + hatch (mayfly, tortoise, shark, pine, the Sun, the red dwarf: estimates and stellar models); MAYBE dashed ghost "
                             "(the closing 'forever', from 'Maybe' to the end of s5); IDLE at the CTA. AI plates S1-S3 tagged 'AI impression'; the Sun inset and "
                             "the detector tank are 'drawn · not to scale'. The rail is labelled 'years · log scale'.")
    md["palette"] = {"Night Ink (sky)": "#0B0E16 -> #05060A", "Steel (rail, ticks)": "#AEB8C2", "Marker (ONLY the marker)": "#BFF6FF",
                     "Chip / card": "#121722", "Bone (text)": "#F4EFE6", "Sun / red dwarf tints": "#FFE3A3 / #D9654A (only the two drawn discs in the Sun inset)",
                     "red": "none: the red wall of video 16 is dropped"}
    md["signature_device"] = ("One log-scale lifespan rail in years (10^-4 to 10^33) with a single white-cyan marker that CLIMBS rung by rung (MAYFLY ~1 day to PROTON > 10^33 yr) while a ZEROS "
                              "counter ticks 0 -> 33; the PROTON is an open, dashed rung with an up arrow (a lower limit), the rail BREAKS above it and a dashed 'forever?' line rises to the top.")
    md["hero_beats"] = ["sc09 the marker climbs from the red dwarf to the proton's lower limit while ZEROS runs 12 -> 33 and the rail breaks above it",
                        "sc12 the dashed 'forever?' line rises through the break under the MAYBE tab"]
    md["series_style"] = "Lifespan Column: video 16-18's ladder engine, ascending in years (video 18's layout)"
    md["taste_profile"] = {"design_read": "Youth science short: one long climb from a day to thirty-three zeros of years, ending on a dashed line that nobody can measure.",
                           "visual_variance": 4, "motion_intensity": 4, "information_density": 4,
                           "palette_discipline": "Night ink, steel rail, ONE white-cyan marker; no red; the two stars tinted only inside their drawn inset.",
                           "layout_variation": "Log rail + marker, zeros counter, AI plates then drawn insets, the typed 1 + 33 zeros readout.",
                           "reference_strategy": "Numbers from the brief only; AI stills as short tagged inserts.",
                           "anti_patterns": ["'protons last forever' as fact", "a measured lifetime for the proton", "a red dwarf drawn to scale", "any flash in the detector"],
                           "quality_gates": ["Every rung's number matches the brief", "Log scale labelled as such", "The proton rung is a LOWER LIMIT (dashed, open, 'lower limit')", "Closing claim is MAYBE"]}
    md["risks"] = [{"risk": "Log scale misread as linear", "fallback": "'years · log scale' label + a power of ten every 3 decades"},
                   {"risk": "A lower limit read as a lifetime", "fallback": "dashed open rung, up arrow, 'lower limit' in the chip, the tab sublabel and the placard"},
                   {"risk": "Detector drawing implies decays were seen", "fallback": "nothing flashes; 'no decay seen' seats in the tank"}]
    md["ending"] = {"rule": "finished line", "closing_line": "Maybe something really does last forever.", "settle_seconds": 1.5, "loop_cut": "optional only"}
    md["audio"] = {**md.get("audio", {}), "duck_db": 12, "alignment": "last tonic pinned by assets/music/music_qa.json; chord ~0.15 s after 'forever.'; duck deeper + a voice-only lift on the soft closing sentence"}
    for sc in plan["scenes"]:
        sc["description"] = SCENE_TEXT[sc["id"]]
    md["stills"] = [{"still_id": k, "name": Path(v.get("source", v["file"])).stem, "output_path": v.get("source"), "used_in": [v["scene"]],
                     "placeholder": v["placeholder"], "window": v["window"], "crop_px": v.get("crop_px"), "crop_pct": v.get("crop_pct"),
                     "honesty": "'AI impression' tag while visible."} for k, v in media["plates"].items()]
    md["safe_areas"] = {
        "top_ui_y": 192, "bottom_ui_y": 1574, "right_rail": 929,
        "rail": {"x": [100, 330], "y": [206, 1020], "note": "spine x 250, L = log10(years): y = 1020 - (L + 4) * 520 / 37; powers every 3 right-aligned at x 224; the PROTON at y 500, the break y 432-458, the dashed 'forever?' line to y 240, its label y 206-250"},
        "rung_labels": {"x": [280, 572], "note": "chips de-overlapped bottom-up with leaders; never under the open window (build_props asserts)"},
        "axis_label": {"x": [100, 400], "y": [1050, 1078]},
        "window": {"x": [580, 920], "y": [440, 893], "note": "S1 tortoise, S2 shark, S3 pine, then the DRAWN Sun + red dwarf, then the DRAWN detector tank"},
        "counter": {"x": [640, 920], "y": [220, 340], "note": "the ZEROS chip, right-aligned at x 920"},
        "readout": {"x": [580, 920], "y": [930, 1060], "scenes": "sc10-sc11", "note": "1 + 33 zeros card under the window"},
        "placard_rail": {"x": [140, 912], "y": [1124, 1204]}, "honesty_tab": {"x": [140, 628], "y": [1236, 1290]},
        "caption_slab": {"x": [140, 940], "y": [1296, 1488]},
    }
    md["foundation_changes"] = [
        "Built on video 18's ascending engine (Weight Column) re-dressed in years: bottom 10^-4 yr (about an hour), top = the PROTON's lower limit 10^33 yr at y 500.",
        "The PROTON is an OPEN rung (dashed tick + up arrow, three-line chip with 'lower limit'); the rail breaks above it and a dashed 'forever?' line rises to y 240.",
        "ZEROS = the power of ten of the active rung's years; MAYFLY shows 0 (under a year); SHARK keeps 2; the run 12 -> 33 accelerates across the PROTON climb and lands ON 'years'.",
        "Window states: AI tortoise / shark / pine, a DRAWN Sun + red dwarf, a DRAWN detector tank (open to sc11); the typed readout sits under the window (y 930-1060), fading before the MAYBE glide.",
        "Honesty: the tab sublabel 'lower limit' on the PROTON and ZEROS keys; the tortoise's age is an estimate (PROBABLY). No red anywhere except the dwarf disc.",
        "The closing sentence is soft: a voice-only lift (+5.5 dB, from 'Maybe') and a -12 dB closing duck; script.json claim_tags are not used (build_props.py CLAIMS).",
        "Superscripts are in none of the faces: the powers are DRAWN as raised text >= 24 px (shared/Type.tsx <Sci>).",
    ]
    schema = json.loads(Path("schemas/artifacts/scene_plan.schema.json").read_text())
    jsonschema.validate(plan, schema)
    (P / "artifacts/scene_plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    print("scene_plan.json synced + schema-valid:", [(s["id"], s["start_seconds"], s["end_seconds"]) for s in plan["scenes"]])


if __name__ == "__main__":
    main()
