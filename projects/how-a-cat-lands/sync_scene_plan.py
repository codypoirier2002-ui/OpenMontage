#!/usr/bin/env python3
"""Sync artifacts/scene_plan.json with the foundation's measurements (idempotent; run from the repo root, after
align_narration.py and prepare_media.py):

    python3 projects/how-a-cat-lands/sync_scene_plan.py

Copied from projects/how-a-mosquito-drinks/sync_scene_plan.py (video 14). It:
  * sets every scene's start / end from the measured timeline (anchor onset - 2 f; artifacts/timeline.json); metadata.total_*
    = the film; the planned values stay in metadata.planned_total_*;
  * A1 (Marey): the archival download SUCCEEDED (assets_report A1) - it is an ENGRAVING after Marey's 1894 photographs, so
    its on-screen tag is 'engraving after É.-J. Marey, 1894' (added to verified_on_screen_strings; the unused variants
    'É.-J. Marey, 1894' and 'drawn after É.-J. Marey, 1894' are REMOVED); metadata.archival[A1] records the file, the cells
    used and the hands crop (media_report.json);
  * 'UP' (sc04's drawn arrow label) is added to verified_on_screen_strings (no claim; a direction label);
  * metadata.safe_areas['window'] = the ONE window box as built (x 160-620, y 360-1000: left of the checklist card; the
    plan's x 160-920 box would have covered the card), + 'dials' / 'ledger' as built (theme.ts L);
  * metadata.stills carry their crop boxes; metadata.foundation_changes lists the divergences;
  * validated against schemas/artifacts/scene_plan.schema.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

P = Path("projects/how-a-cat-lands")
A1_TAG = "engraving after É.-J. Marey, 1894"
DROP = ["É.-J. Marey, 1894", "drawn after É.-J. Marey, 1894"]
ADD = [A1_TAG, "UP"]


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
        sc["framing"] = sc["framing"].replace("window x 160-920 y 360-900", "window x 160-620 y 360-1000 (left of the checklist card)")
    md["total_duration_seconds"] = tl["total_seconds"]
    md["total_frames"] = tl["total_frames"]
    md["timing_basis"] = (f"MEASURED (foundation): every scene boundary after sc01 = its anchor word's hand-measured onset - 2 frames "
                          f"(align_narration.py, the clean WAVs, 107/107 words swept); the film = 0.5 s lead + {tl['narration_seconds']} s narration "
                          f"(widened gaps 1.2/1.2/1.2/1.45 s) to the release of 'vet.' ({tl['vet_end_seconds']} s) + 1.5 s settle. Planned values kept in planned_total_*.")
    v = [s for s in md["verified_on_screen_strings"] if s not in DROP]
    for s in ADD:
        if s not in v:
            v.append(s)
    md["verified_on_screen_strings"] = v
    md["verified_strings_note"] = ("foundation: A1 is an ENGRAVING after Marey's photographs (Commons File:Falling_cat_1894.jpg), so it is tagged "
                                   f"'{A1_TAG}'; the plan's two variants were removed (unused). 'UP' added for sc04's drawn arrow (a direction, no claim).")
    for sc in plan["scenes"]:
        if sc["id"] == "sc03":
            sc["description"] = sc["description"].replace(
                "archival Marey frames if the download succeeds (credited 'É.-J. Marey, 1894'), else a drawn copy of the sequence (tag 'drawn after É.-J. Marey, 1894')",
                f"the archival engraving after Marey's photographs (download succeeded): 8 cells of its top strip (the hands cropped out) in a vertical film strip, tag '{A1_TAG}'")
            sc["overlay_notes"] = sc["overlay_notes"].replace("credit 'É.-J. Marey, 1894' or 'drawn after É.-J. Marey, 1894'", f"tag '{A1_TAG}'")
            sc["required_assets"] = [{"type": "image_still", "description": "A1 marey_1894.jpg: top-strip cells 3-10 (hands cropped, media_report.json), film strip", "source": "source"}]
    for a in md.get("archival", []):
        if a["id"] == "A1":
            a["status"] = "downloaded (assets stage); used as a film strip of 8 top-strip cells (3-10), the experimenter's hands cropped out (cells 1-2 dropped)"
            a["file"] = media["A1"]["file"]
            a["tag"] = A1_TAG
            a["cells"] = [c["cell"] for c in media["A1"]["cells"]]
    for st in md.get("stills", []):
        r = media["plates"].get(st["still_id"])
        if r:
            st["crop_px"] = r["crop_px"]
            st["crop_pct"] = r["crop_pct"]
            st["window"] = r["window"]
    md["safe_areas"]["window"] = {"x": [160, 620], "y": [360, 1000],
                                  "note": "ONE box for S1, A1 and S2 (portrait 460 x 640); left of the checklist card (never over it)"}
    md["safe_areas"]["cat_field"] = {"x": [120, 620], "y": [360, 1000]}
    md["safe_areas"]["dials"] = {"x": [640, 920], "y": [620, 860]}
    md["safe_areas"]["ledger"] = {"x": [140, 920], "y": [620, 1000]}
    md["safe_areas"]["drawn_tag"] = {"x": [140, 420], "y": [1066, 1104]}
    md["foundation_changes"] = [
        f"Film {tl['total_frames']} f ({tl['total_seconds']} s), not {md['planned_total_frames']}: the read is short (38.6 s raw); section gaps widened to 1.2/1.2/1.2/1.45 s (lead 0.5 s, settle 1.5 s); all 12 windows re-timed (anchor - 2 f).",
        "ONE window box x 160-620, y 360-1000 (portrait) for S1, A1 and S2, left of the checklist card (the plan's x 160-920 box covered the card).",
        f"A1 downloaded: an engraving after Marey, tagged '{A1_TAG}'; top-strip cells 3-10 as a vertical film strip; the hands cropped (cells 1-2 dropped).",
        "Caption pages re-flowed (s2, s3, s5) so each claim starts its own page (lesson 3) and no page is a 2-word orphan ('the vet.').",
        "Caption tones: 'front' amber (both s3 words), 'back' cyan ONLY in s3 ('the back half'); s4 'back arched' is the spine: plain.",
        "The ELAPSED clock reads seconds with hundredths ('0.00 s' -> '0.64 s', illustrative), not m:ss (a fall lasts under a second).",
        "Dials and 'total spin: 0' leave before the 'But not always.' page (lesson 42); the FRONT dial returns alone for the short-drop demo (sc10).",
        "Music: V -> I + the tonic re-struck at src 52.81 (the chord, 0.15 s after 'vet'); NO IV-V-I (none claimed).",
    ]
    schema = json.loads(Path("schemas/artifacts/scene_plan.schema.json").read_text())
    jsonschema.validate(plan, schema)
    (P / "artifacts/scene_plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    print("scene_plan.json synced + schema-valid:", [(s["id"], s["start_seconds"], s["end_seconds"]) for s in plan["scenes"]])


if __name__ == "__main__":
    main()
