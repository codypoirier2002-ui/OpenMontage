#!/usr/bin/env python3
"""Sync artifacts/scene_plan.json with the foundation's measurements (idempotent; run from the repo root, after
align_narration.py and prepare_media.py):

    python3 projects/how-small-can-anything-get/sync_scene_plan.py

Video 17 ("How Small Can Anything Get?", the Scale Well). The plan was copied from video 16; this script makes its metadata
video 17's and keeps it in step with the build:
  * every scene's start / end from the measured timeline (anchor onset - 2 f; artifacts/timeline.json); metadata.total_*
    = the film; the planned values stay in metadata.planned_total_*;
  * metadata.captions.pages = the caption pages AS BUILT (re-flowed from the narration: <= 2 lines, <= 6 words, every claim
    starts its own page, no 2-word orphans); build_props.py reads them and asserts they cover the narration;
  * metadata.placards (4, the source rail), verified_on_screen_strings, forbidden_on_screen, honesty_grammar, stills
    (S1-S3 as staged by prepare_media.py, crop boxes from media_report.json), safe_areas as built (theme.ts L);
  * metadata.foundation_changes lists the divergences; validated against schemas/artifacts/scene_plan.schema.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

P = Path("projects/how-small-can-anything-get")

PAGES = [
    ("s1", "A grain of sand"), ("s1", "is about half a millimetre."), ("s1", "A human hair"), ("s1", "is a tenth of that."),
    ("s1", "And that's about where"), ("s1", "your eyes give up."),
    ("s2", "A red blood cell"), ("s2", "is ten times smaller again."), ("s2", "Most viruses are smaller still,"),
    ("s2", "too small for any ordinary"), ("s2", "microscope to see."),
    ("s3", "An atom is a thousand"), ("s3", "times smaller than a virus."), ("s3", "And the proton at its centre"),
    ("s3", "is sixty thousand times smaller"), ("s3", "than the atom."),
    ("s4", "Electrons are so small"), ("s4", "that no experiment has found"), ("s4", "any size at all."),
    ("s4", "Below that, physicists point"), ("s4", "to the Planck length,"), ("s4", "twenty more zeros down."),
    ("s5", "Thirty-four zeros after the decimal point."), ("s5", "Maybe that's the floor."), ("s5", "Or maybe there isn't one."),
]
PLACARDS = [
    {"scenes": "sc01-sc03", "text": "sand ~0.06-2 mm (Wentworth) · hair 17-180 µm", "fine_print": "naked-eye limit ~0.04-0.1 mm, varies"},
    {"scenes": "sc04-sc05", "text": "red blood cell ~8 µm · influenza ~100 nm (NCBI)", "fine_print": "light-microscope limit ~200 nm (Abbe)"},
    {"scenes": "sc06-sc07", "text": "proton radius 0.8414 fm (CODATA 2018)", "fine_print": "atom ~0.1-0.3 nm across"},
    {"scenes": "sc08-sc12", "text": "electron: no size found, < 10⁻¹⁸ m", "fine_print": "Planck length 1.6 × 10⁻³⁵ m: not proven to be a minimum"},
]
DECADES = [f"10⁻{''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(c)] for c in str(n))} m" for n in range(3, 19)]
VERIFIED = ["metres · log scale", *DECADES, "ZEROS", *[str(n) for n in range(0, 35)],
            "SAND · ~0.5 mm", "HAIR · ~70 µm", "RED BLOOD CELL · ~8 µm", "VIRUS · ~100 nm", "ATOM · ~0.1 nm", "PROTON · ~1.7 fm across",
            "YOUR EYE · ~0.1 mm", "LIGHT MICROSCOPE · ~200 nm", "ELECTRON", "no size found · < 10⁻¹⁸ m", "PLANCK LENGTH · 1.6 × 10⁻³⁵ m",
            "a floor? unproven", "0." + "0" * 34 + "16 m", "to scale, this dot would be ~0.006 px", "AI impression", "drawn · not to scale",
            "What's the smallest thing you've ever seen?"]
FORBIDDEN = ["smallest possible (the Planck length is not proven to be a minimum)", "proven floor", "electrons are points",
             "the smallest thing in the universe", "actual size"]


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
    md["captions"]["pages"] = [{"section": s_, "page": t} for s_, t in PAGES]
    md["captions"]["note"] = "re-flowed by the foundation (lesson 3): every claim starts its own page; <= 2 lines / <= 6 words; no 2-word orphan"
    md["placards"] = PLACARDS
    md["verified_on_screen_strings"] = VERIFIED
    md["forbidden_on_screen"] = FORBIDDEN
    md["honesty_grammar"] = ("MEASURED solid tab (sand, hair, cell, virus, atom, proton, electron's upper bound); PROBABLY outline + hatch (the "
                             "naked-eye limit); MAYBE dashed ghost (the Planck length as a floor, from 'Below that,' to the end of s5); IDLE at the CTA. "
                             "AI plates S1-S3 tagged 'AI impression'; the atom is 'drawn · not to scale'. The rail is labelled 'metres · log scale'.")
    md["stills"] = [{"still_id": k, "name": Path(v.get("source", v["file"])).stem, "output_path": v.get("source"), "used_in": [v["scene"]],
                     "placeholder": v["placeholder"], "window": v["window"], "crop_px": v.get("crop_px"), "crop_pct": v.get("crop_pct"),
                     "honesty": "'AI impression' tag while visible."} for k, v in media["plates"].items()]
    md["safe_areas"] = {
        "top_ui_y": 192, "bottom_ui_y": 1574, "right_rail": 929,
        "rail": {"x": [100, 330], "y": [380, 1110], "note": "spine x 250, L = -log10(m): y = 380 + (L - 3) * 620 / 15; decade powers right-aligned at x 224; the break y 1012-1040; the Planck line y 1080"},
        "rung_labels": {"x": [280, 572], "note": "chips de-overlapped top-down with leaders; never under the open window (build_props asserts)"},
        "reference_labels": {"x": [40, 224], "note": "'YOUR EYE' / 'LIGHT MICROSCOPE' left of the rail (the decade powers under them are hidden)"},
        "window": {"x": [580, 920], "y": [440, 893], "note": "S1 sand, S2 blood cells, S3 virus, then the DRAWN atom"},
        "counter": {"x": [640, 920], "y": [220, 340], "note": "the ZEROS chip, right-aligned at x 920"},
        "electron": {"x": [270, 700], "y": [960, 1040], "scenes": "sc08-sc12"},
        "readout": {"x": [580, 920], "y": [470, 600], "scenes": "sc10-sc12"},
        "placard_rail": {"x": [140, 912], "y": [1124, 1204]}, "honesty_tab": {"x": [140, 628], "y": [1236, 1290]},
        "caption_slab": {"x": [140, 940], "y": [1296, 1488]},
    }
    md["foundation_changes"] = [
        "Copied from video 16 (Speed Ladder); the visual layer is the Scale Well: the log ladder flipped DOWNWARD in metres (top 1 mm, bottom 10⁻¹⁸ m).",
        "Caption pages re-flowed from the narration (lesson 3): each claim starts its own page; 'And that's about where' / 'your eyes give up.' is two pages (8 words > 6), the PROBABLY key sits on the first.",
        "The reference lines' labels (YOUR EYE, LIGHT MICROSCOPE) sit LEFT of the rail (they are 6 / 12 px from the HAIR / VIRUS rungs; on the right they would shove seated chips).",
        "Superscripts (⁻ ⁴-⁹ ⁰) are in none of the faces: the powers are DRAWN as raised text >= 24 px (shared/Type.tsx <Sci>).",
        "PROTON is a two-line chip (name over '~1.7 fm across') so it fits beside the open window.",
        "script.json claim_tags are still video 16's: build_props.py keys the meter from its own CLAIMS (the brief's grades) instead of asserting against them.",
    ]
    schema = json.loads(Path("schemas/artifacts/scene_plan.schema.json").read_text())
    jsonschema.validate(plan, schema)
    (P / "artifacts/scene_plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    print("scene_plan.json synced + schema-valid:", [(s["id"], s["start_seconds"], s["end_seconds"]) for s in plan["scenes"]])


if __name__ == "__main__":
    main()
