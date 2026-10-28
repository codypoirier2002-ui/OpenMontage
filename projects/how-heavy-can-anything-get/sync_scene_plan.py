#!/usr/bin/env python3
"""Sync artifacts/scene_plan.json with the foundation's measurements (idempotent; run from the repo root, after
align_narration.py and prepare_media.py):

    python3 projects/how-heavy-can-anything-get/sync_scene_plan.py

Video 18 ("How Heavy Can Anything Get?", the Weight Column). The plan was copied from video 17; this script makes its
metadata video 18's and keeps it in step with the build:
  * every scene's start / end from the measured timeline (anchor onset - 2 f; artifacts/timeline.json); metadata.total_*
    = the film; the planned values stay in metadata.planned_total_*;
  * metadata.captions.pages = the caption pages AS BUILT (re-flowed from the narration: <= 2 lines, <= 6 words, every claim
    starts its own page, no 2-word orphans); build_props.py reads them and asserts they cover the narration;
  * metadata.placards (5, the source rail), verified_on_screen_strings, forbidden_on_screen, honesty_grammar, stills
    (S1-S3 as staged by prepare_media.py, crop boxes from media_report.json), safe_areas as built (theme.ts L);
  * metadata.foundation_changes lists the divergences; validated against schemas/artifacts/scene_plan.schema.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

P = Path("projects/how-heavy-can-anything-get")

PAGES = [
    ("s1", "You weigh about seventy kilograms."), ("s1", "A blue whale can reach"), ("s1", "a hundred and fifty thousand."),
    ("s1", "The Eiffel Tower, about ten million."),
    ("s2", "Every human alive, put together:"), ("s2", "around four hundred billion."), ("s2", "The whole Earth: six trillion trillion."),
    ("s3", "The Sun outweighs"), ("s3", "three hundred and thirty thousand Earths."), ("s3", "And a neutron star squeezes"),
    ("s3", "even more into a ball"), ("s3", "the size of a city."),
    ("s4", "The black hole at the centre"), ("s4", "of our galaxy weighs"), ("s4", "four million Suns,"), ("s4", "packed smaller than Mercury's orbit."),
    ("s5", "All the ordinary matter"), ("s5", "we can see comes to"), ("s5", "about fifty-three zeros of kilograms."),
    ("s5", "And dark matter outweighs it"), ("s5", "five to one."),
]
PLACARDS = [
    {"scenes": "sc01-sc03", "text": "Eiffel Tower 10,100 t (toureiffel.paris) · blue whale up to ~150-190 t (NOAA)", "fine_print": "adult ~70 kg, typical"},
    {"scenes": "sc04-sc05", "text": "all humans ~287-390 million t (2012, 2018 studies)", "fine_print": "Earth 5.97 × 10²⁴ kg (NASA)"},
    {"scenes": "sc06-sc07", "text": "Sun = 333,000 Earths (NASA)", "fine_print": "neutron star ~1.4 Suns in ~20 km"},
    {"scenes": "sc08-sc09", "text": "Sgr A* ~4 million Suns (EHT, NASA)", "fine_print": "horizon ~24 million km; Mercury's orbit ~116 million km"},
    {"scenes": "sc10-sc12", "text": "ordinary matter ~1.5 × 10⁵³ kg (critical-density estimate)", "fine_print": "dark matter ~5.4 : 1 (Planck 2018, inferred)"},
]
SUPD = "⁰¹²³⁴⁵⁶⁷⁸⁹"
DECADES = [f"10{''.join(SUPD[int(c)] for c in str(n))} kg" for n in range(0, 37, 3)]
RUNG_LINES = ["YOU · ~70 kg", "BLUE WHALE · up to ~150,000 kg", "EIFFEL TOWER · ~10 million kg", "ALL HUMANS · ~400 billion kg",
              "EARTH · 6 × 10²⁴ kg", "SUN · 2 × 10³⁰ kg", "NEUTRON STAR · ~1.4 Suns, ~20 km wide", "SGR A* · 4 million Suns"]
VERIFIED = ["kilograms · log scale", *DECADES, "ZEROS", *[str(n) for n in range(0, 54)], *RUNG_LINES,
            "OBSERVABLE UNIVERSE · ~10⁵³ kg (ordinary matter)", "ordinary matter", "DARK MATTER", "~5 : 1 · inferred", "drawn",
            "Mercury's orbit", "AI impression", "drawn · not to scale", "What's the heaviest thing you've ever lifted?"]
FORBIDDEN = ["heaviest possible (nothing says the ladder stops)", "weighs exactly", "dark matter has been seen (it is inferred from gravity)",
             "the universe weighs (only the observable universe's ordinary matter is estimated)", "actual size"]


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
    md["honesty_grammar"] = ("MEASURED solid tab (you, the Eiffel Tower, Earth, the Sun, the neutron star, Sgr A*); PROBABLY outline + hatch (the "
                             "blue whale's top weight, all humans' total, the observable universe's ordinary matter and dark matter's ~5 : 1, from "
                             "'All the ordinary matter' to the end of s5); IDLE at the CTA. AI plates S1-S3 tagged 'AI impression'; the black hole "
                             "is 'drawn · not to scale'; the matter bars are 'drawn' (linear). The rail is labelled 'kilograms · log scale'.")
    md["stills"] = [{"still_id": k, "name": Path(v.get("source", v["file"])).stem, "output_path": v.get("source"), "used_in": [v["scene"]],
                     "placeholder": v["placeholder"], "window": v["window"], "crop_px": v.get("crop_px"), "crop_pct": v.get("crop_pct"),
                     "honesty": "'AI impression' tag while visible."} for k, v in media["plates"].items()]
    md["safe_areas"] = {
        "top_ui_y": 192, "bottom_ui_y": 1574, "right_rail": 929,
        "rail": {"x": [100, 330], "y": [345, 1000], "note": "spine x 250, L = log10(kg): y = 1000 - L * 620 / 37; powers every 3 right-aligned at x 224; the break y 345-370"},
        "rung_labels": {"x": [280, 572], "note": "chips de-overlapped bottom-up with leaders; never under the open window (build_props asserts)"},
        "axis_label": {"x": [100, 400], "y": [1026, 1054]},
        "universe": {"x": [100, 620], "y": [214, 284], "scenes": "sc10-sc12", "note": "the dashed line at y 280 + its label above, left of the counter"},
        "window": {"x": [580, 920], "y": [440, 893], "note": "S1 whale, S2 Eiffel Tower, S3 neutron star, then the DRAWN black hole + Mercury's orbit"},
        "counter": {"x": [640, 920], "y": [220, 340], "note": "the ZEROS chip, right-aligned at x 920"},
        "bars": {"x": [584, 912], "y": [400, 1100], "scenes": "sc10-sc12", "note": "linear ordinary (amber) / dark (violet) matter bars, base y 1060"},
        "placard_rail": {"x": [140, 912], "y": [1124, 1204]}, "honesty_tab": {"x": [140, 628], "y": [1236, 1290]},
        "caption_slab": {"x": [140, 940], "y": [1296, 1488]},
    }
    md["foundation_changes"] = [
        "Copied from video 17 (Scale Well); the visual layer is the Weight Column: the log ladder pointing UP in kilograms (bottom 1 kg, top 10³⁷ kg).",
        "Caption pages re-flowed from the narration (lesson 3): each claim starts its own page; <= 6 words per page.",
        "Rung numbers are set in mono 26 px (names 28 px) so BLUE WHALE fits beside the open window as two lines; NEUTRON STAR's number is split in two rows.",
        "Chips de-overlap bottom-up: NEUTRON STAR stacks above SUN, SGR A* above it; the OBSERVABLE UNIVERSE line sits at y 280 (not ~320) so it stays clear of the SGR A* chip.",
        "Superscripts are in none of the faces: the powers are DRAWN as raised text >= 24 px (shared/Type.tsx <Sci>).",
        "script.json claim_tags are not used: build_props.py keys the meter from its own CLAIMS (the brief's grades).",
    ]
    schema = json.loads(Path("schemas/artifacts/scene_plan.schema.json").read_text())
    jsonschema.validate(plan, schema)
    (P / "artifacts/scene_plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    print("scene_plan.json synced + schema-valid:", [(s["id"], s["start_seconds"], s["end_seconds"]) for s in plan["scenes"]])


if __name__ == "__main__":
    main()
