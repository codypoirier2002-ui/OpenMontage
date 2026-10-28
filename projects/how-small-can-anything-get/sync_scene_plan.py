#!/usr/bin/env python3
"""Sync artifacts/scene_plan.json with the foundation's measurements (idempotent; run from the repo root, after
align_narration.py and prepare_media.py):

    python3 projects/how-small-can-anything-get/sync_scene_plan.py

Copied from projects/how-a-cat-lands/sync_scene_plan.py (video 15). It:
  * sets every scene's start / end from the measured timeline (anchor onset - 2 f; artifacts/timeline.json); metadata.total_*
    = the film; the planned values stay in metadata.planned_total_*;
  * metadata.safe_areas['window'] = the ONE window box as built (x 580-920, y 440-893: right of the rung label chips, which
    the plan's x 470-920 box would have covered), + 'counter' / 'readout' / 'orbit' / 'energy' as built (theme.ts L);
  * metadata.stills carry 'placeholder' / crop boxes from media_report.json; metadata.placards[2] = the lesson-32 rewording;
  * metadata.foundation_changes lists the divergences; validated against schemas/artifacts/scene_plan.schema.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

P = Path("projects/how-small-can-anything-get")
PLACARD3 = {"text": "Parker Solar Probe: ~692,000 km/h (Dec 2024)", "fine_print": "NASA's figure as reported by Space.com · speed from falling toward the Sun"}


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
        sc["framing"] = sc["framing"].replace("window x 470-920 y 420-900", "window x 580-920 y 440-893 (right of the rung label chips)")
    md["total_duration_seconds"] = tl["total_seconds"]
    md["total_frames"] = tl["total_frames"]
    md["timing_basis"] = (f"MEASURED (foundation): every scene boundary after sc01 = its anchor word's hand-measured onset - 2 frames "
                          f"(align_narration.py, the clean WAVs, 106/106 words swept); the film = 0.5 s lead + {tl['narration_seconds']} s narration "
                          f"(widened gaps 1.2/1.2/1.2/1.45 s, lesson 48) to the release of 'way.' ({tl['way_end_seconds']} s) + 1.5 s settle. Planned values kept in planned_total_*.")
    for pl in md["placards"]:
        if pl["scenes"] == "sc06-sc07":
            pl.update(PLACARD3)
            pl["lesson_32"] = "reworded by the foundation: the brief holds NASA's figure only through Space.com / SlashGear / Live Science reports"
    for st in md.get("stills", []):
        r = media["plates"].get(st["still_id"])
        if r:
            st["placeholder"] = r["placeholder"]
            st["window"] = r["window"]
            if not r["placeholder"]:
                st["crop_px"] = r["crop_px"]
                st["crop_pct"] = r["crop_pct"]
            else:
                st["status"] = "NOT GENERATED: a labelled placeholder card is staged in public/stills/; re-run prepare_media.py --force + build_props.py when it lands"
    md["safe_areas"]["window"] = {"x": [580, 920], "y": [440, 893], "note": "ONE portrait box (340 x 453) for S1, S2 and S3, right of the rung label chips (never over one: build_props asserts)"}
    md["safe_areas"]["counter"] = {"x": [640, 920], "y": [220, 340], "note": "the ZEROS chip, right-aligned at x 920"}
    md["safe_areas"]["rail"] = {"x": [180, 320], "y": [380, 1080], "note": "spine x 250; decade numbers right-aligned at x 224 (the longest reaches x ~86); rung chips from x 280"}
    md["safe_areas"]["rung_labels"] = {"x": [280, 572], "note": "label chips (one line, or two lines for EARTH / PARKER) end before the window at x 580"}
    md["safe_areas"]["orbit_inset"] = {"x": [600, 920], "y": [460, 800], "scenes": "sc05 (window closed)"}
    md["safe_areas"]["energy"] = {"bar_x": [600, 650], "curve": {"x": [690, 920], "y": [440, 640]}, "scenes": "sc10"}
    md["safe_areas"]["readout"] = {"x": [600, 920], "y": [460, 600], "scenes": "sc11-sc12"}
    md["safe_areas"]["you_tag"] = {"x": [120, 224], "note": "LEFT of the rail at its rung (WALK, then EARTH); the decade number within 26 px of it is hidden"}
    md["safe_areas"]["mass_label"] = {"x": [280, 545], "y": [483, 517], "scenes": "sc09-sc10 (fixed chip + a dotted leader to the marker)"}
    md["foundation_changes"] = [
        f"Film {tl['total_frames']} f ({tl['total_seconds']} s), not {md['planned_total_frames']}: the read is 42.56 s raw; section gaps widened to 1.2/1.2/1.2/1.45 s (lead 0.5 s, settle 1.5 s); all 12 windows re-timed (anchor - 2 f).",
        "ONE window box x 580-920, y 440-893 (portrait 3:4) for S1, S2, S3, right of the rung label chips (the plan's x 470-920 box covered 'EARTH (orbit) · ~107,000' and 'PARKER (fastest built) · ~692,000').",
        "Rung labels are CHIPS (name in Saira Condensed 700 + number in IBM Plex Mono 500, slashed zeros); EARTH and PARKER are two-line chips (name over number) so they fit beside the open window; the strings are the verified ones.",
        "Stills S1-S3 are PLACEHOLDER cards (labelled 'PENDING STILL') until they are generated; the window, its tag and the chain run unchanged.",
        "Music bed M1 pending: the premix is voice + SFX; build_soundtrack.py picks up assets/music/bed_raw.mp3 automatically (last tonic from the audio, lesson 26).",
        "Placard 3 reworded (lesson 32): 'Parker Solar Probe: ~692,000 km/h (Dec 2024)' + 'NASA's figure as reported by Space.com · speed from falling toward the Sun'.",
        "Caption pages re-flowed (s1, s2, s4, s5) so each claim starts its own page (lesson 3) and no page is a 2-word orphan; the CTA is set on two lines (994 px at 52 px on one).",
        "The YOU tag is ROOT-owned (it persists sc05 -> sc12 across both units); the orbit inset, the light beam, the mass label, the energy bar and the LHC readout are unit-mounted engines driven by root curves.",
        "ZEROS counter = floor(log10) of the rung's number (the digits after the first: 1,235 -> 3, as the plan's 'counter 3'); it steps on X3 ticks ending ON each seat.",
        "The gap under 'c' is DRAWN (14 px, marker centre to line; asserted >= 14 on every frame): 0.999999991 c would be invisible on any log scale; 'the gap' bracket + the log-scale label say so.",
        "The 'anything with mass' label sits at a fixed chip (x 280, y 500) with a dotted leader to the moving marker (riding the marker would collide with the PARKER / LIGHT chips).",
        "The s4 breath after 'Light' (0.28 s) is kept (the [awed] beat); no narration was cut.",
    ]
    schema = json.loads(Path("schemas/artifacts/scene_plan.schema.json").read_text())
    jsonschema.validate(plan, schema)
    (P / "artifacts/scene_plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    print("scene_plan.json synced + schema-valid:", [(s["id"], s["start_seconds"], s["end_seconds"]) for s in plan["scenes"]])


if __name__ == "__main__":
    main()
