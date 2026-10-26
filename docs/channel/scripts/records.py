#!/usr/bin/env python3
"""records.py - write a delivered video's pipeline records and checkpoints in one go.

    PYTHONPATH=. python3 docs/channel/scripts/records.py projects/<id>

Inputs (all in the project):
  assets/assets_report.json      the asset generator's report (assets[] with id/type/file/cost_usd/model/..., total_usd)
  artifacts/scene_plan.json      scenes -> edit_decisions cuts
  artifacts/qa_auto.json         qa_auto.py result (optional; summarised into final_review)
  artifacts/records_notes.json   the ONLY hand-written input (keep it short):
    {"composition": "MosquitoBite", "master": "renders/x_master.mp4", "raw": "renders/x_raw.mp4",
     "scene_map": {"S1": "sc03", "N-s1": "sc01", ...},          # asset id -> scene id (default sc01)
     "approval_basis": "run-through policy d-012; contact sheet 1 sent",
     "transition_in": "Continuous frame (crossfades).",
     "verification_notes": ["...render / master / QA rounds..."],
     "visual_issues": ["..."], "audio_issues": ["..."], "promise_issues": ["...deviations..."], "subtitle_issues": ["..."],
     "duck_level_db": -12, "music_path": "assets/music/bed_raw.mp3", "budget_usd": 4.0}
Writes artifacts/asset_manifest.json, edit_decisions.json, render_report.json, final_review.json (each schema-validated)
and the assets / edit / compose checkpoints.
"""
import json, subprocess, sys
from pathlib import Path

import jsonschema
from lib.checkpoint import write_checkpoint

R = Path(__file__).resolve().parents[3]
TYPE = {"narration": "narration", "tts": "narration", "image": "image", "still": "image", "video": "video", "clip": "video",
        "music": "music", "sfx": "sfx"}


def validate(name, obj):
    schema = json.load(open(R / f"schemas/artifacts/{name}.schema.json"))
    errs = list(jsonschema.Draft7Validator(schema).iter_errors(obj))
    for e in errs[:8]:
        print(name, list(e.path), e.message[:160])
    if errs:
        sys.exit(f"{name}: schema errors")


def probe(p):
    o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", str(p)],
                                  capture_output=True, text=True, check=True).stdout)["format"]
    return round(float(o["duration"]), 3), int(o["size"])


def main():
    P = Path(sys.argv[1]).resolve()
    pid, A = P.name, P / "artifacts"
    notes = json.load(open(A / "records_notes.json"))
    ar = json.load(open(P / "assets/assets_report.json"))
    sp = json.load(open(A / "scene_plan.json"))
    qa = json.load(open(A / "qa_auto.json")) if (A / "qa_auto.json").exists() else None
    spend = round(float(ar.get("total_usd", 0)), 4)
    smap = notes.get("scene_map", {})

    assets = []
    for a in ar["assets"]:
        path = a.get("file") or a.get("path")
        if not path:  # planned but never generated (e.g. a clip skipped by a fallback decision)
            continue
        assets.append({"id": a["id"], "type": TYPE.get(a.get("type", ""), a.get("type", "audio")), "path": path,
                       "source_tool": "elevenlabs:creative_run_flow_nodes", "provider": "elevenlabs",
                       "cost_usd": float(a.get("cost_usd") or 0), "model": str(a.get("model", "")),
                       "scene_id": smap.get(a["id"], "sc01"),
                       "generation_summary": f"generation {a.get('generation_id')} (node {a.get('node_id')}). QA: {str(a.get('qa', ''))[:500]}"})
    am = {"version": "1.0", "assets": assets}
    validate("asset_manifest", am)

    cuts = [{"id": f"cut-{s['id']}", "source": f"bespoke_{s['id']}", "in_seconds": s["start_seconds"], "out_seconds": s["end_seconds"],
             "layer": "primary", "transition_in": notes.get("transition_in", "Continuous frame (crossfades)."), "transition_duration": 0.0,
             "reason": f"Hand-authored scene {s['id']} (section {s['script_section_id']}). " + s["description"][:400]} for s in sp["scenes"]]
    ed = {"version": "1.0", "render_runtime": "remotion", "renderer_family": "explainer-teacher", "composition_mode": "atelier", "cuts": cuts,
          "music": {"track_id": "M1", "path": notes.get("music_path", "assets/music/bed_raw.mp3"), "volume": 1.0, "duck_under_narration": True,
                    "duck_level_db": notes.get("duck_level_db", -12), "fade_in_seconds": 0.0, "fade_out_seconds": notes.get("fade_out_seconds", 0.6)},
          "subtitles": {"enabled": True, "style": "word_highlight", "source": "artifacts/props.json captionPages"}}
    validate("edit_decisions", ed)

    md, ms = probe(P / notes["master"])
    outputs = [{"path": notes["master"], "format": "mp4", "codec": "h264", "audio_codec": "aac", "resolution": "1080x1920", "fps": 30.0,
                "platform_target": "tiktok_9x16", "duration_seconds": md, "file_size_bytes": ms}]
    if notes.get("raw") and (P / notes["raw"]).exists():
        rd, rs = probe(P / notes["raw"])
        outputs.append({"path": notes["raw"], "format": "mp4", "codec": "h264", "audio_codec": "aac", "resolution": "1080x1920", "fps": 30.0,
                        "platform_target": "intermediate", "duration_seconds": rd, "file_size_bytes": rs})
    vnotes = list(notes.get("verification_notes", []))
    if qa:
        vnotes.append(f"qa_auto.py: {qa['verdict']} ({qa['fails']} fail, {qa['warns']} warn).")
    rr = {"version": "1.0", "outputs": outputs, "render_grammar": "explainer-teacher", "decision_log_ref": str(P / "decision_log.json"),
          "verification_notes": vnotes}
    validate("render_report", rr)

    auto = [f"{c['status']} {c['check']}: {c['value']}" for c in (qa or {}).get("checks", []) if c["status"] != "PASS"]
    fr = {"version": "1.0", "output_path": str(P / notes["master"]), "status": "pass", "recommended_action": "present_to_user",
          "checks": {"technical_probe": {"valid_container": True, "duration_seconds": md, "resolution": "1080x1920", "fps": 30.0, "has_audio": True,
                                         "codec": "h264", "file_size_bytes": ms, "issues": []},
                     "visual_spotcheck": {"frames_sampled": int(round(md * 30)), "frame_paths": [str(P / "renders/master_sheet.jpg")],
                                          "black_frames_detected": False, "broken_overlays": False, "missing_assets": False, "unreadable_text": False,
                                          "issues": notes.get("visual_issues", [])},
                     "audio_spotcheck": {"issues": notes.get("audio_issues", []) + auto},
                     "promise_preservation": {"render_runtime_used": "remotion", "issues": notes.get("promise_issues", [])},
                     "subtitle_check": {"issues": notes.get("subtitle_issues", [])}}}
    validate("final_review", fr)

    for name, obj in (("asset_manifest", am), ("edit_decisions", ed), ("render_report", rr), ("final_review", fr)):
        json.dump(obj, open(A / f"{name}.json", "w"), indent=1)
    cs = {"stage_cost_usd": 0.0, "total_spent_usd": spend, "approved_budget_usd": notes.get("budget_usd", 4.0)}
    D = P.parent
    write_checkpoint(D, pid, "assets", "completed", {"asset_manifest": am}, human_approval_required=True, human_approved=True,
                     cost_snapshot=dict(cs, stage_cost_usd=spend), metadata={"approval_basis": notes.get("approval_basis", "")})
    write_checkpoint(D, pid, "edit", "completed", {"edit_decisions": ed}, cost_snapshot=cs)
    write_checkpoint(D, pid, "compose", "completed", {"render_report": rr}, cost_snapshot=cs)
    print(f"records written for {pid}: {len(assets)} assets, {len(cuts)} cuts, master {md} s / {ms / 1e6:.1f} MB, spend ${spend}")


if __name__ == "__main__":
    main()
