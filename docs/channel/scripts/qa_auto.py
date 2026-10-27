#!/usr/bin/env python3
"""qa_auto.py - the channel's mechanical QA pass. Run it on every master BEFORE any QA agent.

    python3 docs/channel/scripts/qa_auto.py projects/<id> [--master renders/<x>_master.mp4] [--no-pixels]

Reads the atelier build's standard files (artifacts/timeline.json, props.json, script.json, scene_plan.json,
soundtrack_report.json) and measures the master. Each check names the CHANNEL_FORMULA lesson it enforces.
Writes artifacts/qa_auto.json and exits 1 if any check FAILs (WARN does not fail).

What it cannot judge (leave to the QA agents): anatomy, whether a visual contradicts a fact, readability,
a label sitting under the wrong number (L33), the colour at the spine of a drawn line (L58), drawn detail.
Video 16 added: SFX under the first word (L57), claim graphics gone before the tab glide (L42/L52), fine print >= 24 px
including axis numbers and labels in the tsx (L54), the still hold after the release (L25).
Only ffmpeg/ffprobe, numpy and scipy are used.
"""
import argparse, glob, json, re, subprocess, sys
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter
from scipy.signal import butter, sosfilt

SR = 48000
RESULTS = []


def check(name, lesson, ok, value, expect, level="FAIL", note=""):
    status = "PASS" if ok else level
    RESULTS.append({"check": name, "lesson": lesson, "status": status, "value": value, "expect": expect, "note": note})


def jload(p):
    return json.load(open(p))


def norm(w):
    return re.sub(r"[^a-z0-9%~.']", "", w.lower().replace("\u2019", "'")).strip(".")


# ---------- media helpers ----------
def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def decode_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def db(x):
    return float(20 * np.log10(max(float(x), 1e-9)))


def rms(a):
    return float(np.sqrt(np.mean(np.square(a)))) if len(a) else 0.0


def band(mono, lo=300, hi=4000):
    return sosfilt(butter(4, [lo, hi], btype="band", fs=SR, output="sos"), mono)


def peak100_db(mono, t0, t1):
    """Loudest 100 ms (10 ms hop) inside [t0, t1]: a word's stressed core, not its decaying tail."""
    seg = mono[int(t0 * SR):int(t1 * SR)]
    wl = int(0.1 * SR)
    if len(seg) <= wl:
        return db(rms(seg))
    return max(db(rms(seg[i:i + wl])) for i in range(0, len(seg) - wl + 1, int(0.01 * SR)))


def win_rms_db(mono, t0, t1):
    return db(rms(mono[int(t0 * SR):int(t1 * SR)]))


# ---------- checks ----------
def spec_checks(master, tl):
    p = probe(master)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    a = next((s for s in p["streams"] if s["codec_type"] == "audio"), None)
    fps = eval(v["r_frame_rate"])
    frames = int(v.get("nb_frames") or round(float(p["format"]["duration"]) * fps))
    check("resolution", "format", (v["width"], v["height"]) == (1080, 1920), f'{v["width"]}x{v["height"]}', "1080x1920")
    check("fps", "format", abs(fps - tl["fps"]) < 0.01, fps, tl["fps"])
    check("frame count", "format", frames == tl["total_frames"], frames, tl["total_frames"])
    check("video codec", "L7", v["codec_name"] == "h264" and v.get("profile") == "High", f'{v["codec_name"]} {v.get("profile")}', "h264 High")
    check("colour", "L7", v.get("color_primaries") == "bt709" and v.get("color_range") == "tv",
          f'{v.get("color_primaries")}/{v.get("color_range")}', "bt709/tv")
    check("audio", "format", a is not None and a["codec_name"] == "aac" and a["sample_rate"] == "48000" and a["channels"] == 2,
          a and f'{a["codec_name"]} {a["sample_rate"]} {a["channels"]}ch', "aac 48000 2ch")
    err = subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(master), "-f", "null", "-"],
                         capture_output=True, text=True).stderr.strip()
    check("strict decode", "format", not err, err[:200] or "clean", "clean")
    mb = int(p["format"]["size"]) / 1e6
    check("file size", "format", mb < 60, round(mb, 1), "< 60 MB", "WARN")


def loudness_checks(master):
    out = subprocess.run(["ffmpeg", "-nostats", "-i", str(master), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summ = out[out.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
    check("integrated loudness", "master", abs(i + 14) <= 0.5, i, "-14 +-0.5 LUFS")
    check("true peak", "master", tp <= -1.0, tp, "<= -1.0 dBTP")


def caption_checks(props, tl, script):
    fps = tl["fps"]
    words = tl["words"]
    cap = [w for pg in props["captionPages"] for w in pg["words"]]
    # verbatim: caption words == script words, in order
    sw = [norm(w) for s in script["sections"] for w in s["text"].split()]
    cw = [norm(w["text"]) for w in cap]
    check("captions verbatim", "L17", sw == cw, f"{len(cw)} caption words / {len(sw)} script words",
          "identical word list", note="" if sw == cw else f"first diff at {next((i for i,(x,y) in enumerate(zip(sw,cw)) if x!=y), min(len(sw),len(cw)))}")
    # onset: each caption word's f0 vs the aligned onset (timeline words, film seconds)
    offs = []
    for c, w in zip(cap, words):
        offs.append(c["f0"] - round(w["start"] * fps))
    worst = max(offs, key=abs) if offs else 0
    check("caption onsets", "L2/L13", all(abs(o) <= 3 for o in offs), f"{len(offs)} words, worst {worst:+d} f", "within +-3 f of aligned onset")
    bad = [i for i, pg in enumerate(props["captionPages"]) if len(pg["words"]) > 6 or max(w.get("line", 0) for w in pg["words"]) > 1]
    check("caption pages", "format", not bad, f"{len(props['captionPages'])} pages, {len(bad)} over", "<= 6 words, <= 2 lines", note=str(bad[:8]))
    starts = {pg["startFrame"] for pg in props["captionPages"]}
    off = [m["frame"] for m in props.get("meter", []) if m["state"] != "IDLE" and m["frame"] not in starts and m["frame"] != 0]
    check("tab on caption page starts", "L3", not off, f"{len(off)} off-page tab changes", "every tab change on a page start", "WARN", note=str(off[:8]))


def forbidden_check(props, plan):
    bad = [s for s in plan.get("metadata", {}).get("forbidden_on_screen", [])]
    blob = json.dumps(props, ensure_ascii=False).lower()
    hits = [s for s in bad if s.lower() in blob]
    check("forbidden strings", "L16/L20", not hits, hits or "none", "none of scene_plan forbidden_on_screen in props")


def last_word(tl):
    k = next(k for k in tl if k.endswith("_end_frame") and not k.startswith("voice"))
    stem = k[: -len("_end_frame")]
    lw = [w for w in tl["words"] if w["section"] == tl["sections"][-1]["id"]]
    return stem, tl[k], tl[stem + "_end_seconds"], lw


def ending_checks(props, tl, audio, sr=None):
    fps = tl["fps"]
    stem, rel_f, rel_s, lw = last_word(tl)
    chord_f = props["settle"]["chordFrame"]
    total = tl["total_frames"]
    check("settle length", "L25", abs((total - rel_f) - 1.5 * fps) <= 2, f"{(total - rel_f) / fps:.2f} s after '{stem}'", "1.5 s +-2 f")
    check("chord after last word", "L26", 0.08 <= (chord_f - rel_f) / fps <= 0.25, f"{(chord_f - rel_f) / fps:.3f} s", "0.08-0.25 s after release")
    mono = audio.mean(1)
    n = len(mono)
    tail = [db(rms(mono[max(0, n - int((k + 1) * 0.05 * SR)): n - int(k * 0.05 * SR)])) for k in range(12)][::-1]
    last20 = db(rms(mono[-int(0.02 * SR):]))
    check("end fade (no cut chord)", "L43", tail[-1] <= -30 and last20 <= -33, f"last 50 ms {tail[-1]:.1f} dB, last 20 ms {last20:.1f} dB",
          "last 50 ms <= -30, last 20 ms <= -33 dBFS")
    rising = sum(1 for a, b in zip(tail[-6:], tail[-5:]) if b > a + 3)
    check("end decays smoothly", "L43", rising == 0, [round(x, 1) for x in tail[-6:]], "no 50 ms step up > 3 dB in the last 0.3 s", "WARN")
    # closing word level: broadband vs its sentence, and 300-4000 Hz over the bed in the sentence's gaps
    w = lw[-1]
    sent = lw[max(i for i, x in enumerate(lw[:-1]) if x["text"].rstrip().endswith((".", "?", "!", ":"))) + 1:] if any(
        x["text"].rstrip().endswith((".", "?", "!", ":")) for x in lw[:-1]) else lw
    voiced = [peak100_db(mono, x["start"], x["end"]) for x in sent]
    gap_db = float(np.median(voiced)) - voiced[-1]
    check("last word broadband", "L30", gap_db <= 5, f"'{w['text']}' {voiced[-1]:.1f} vs sentence median {np.median(voiced):.1f} dB",
          "loudest 100 ms <= 5 dB under its sentence's median (FAIL)")
    if gap_db <= 5:
        check("last word broadband (soft)", "L30", gap_db <= 3, f"{gap_db:+.1f} dB under", "<= 3 dB under", "WARN",
              note="3-5 dB under can be a natural falling cadence; listen on a phone speaker")
    b = band(mono)
    # bed estimate from the closing sentence's own word gaps only: the release-to-chord window is not used,
    # because the duck is already lifting there (it gave false WARNs on every finished-line ending)
    gaps = [(a["end"] + 0.01, c["start"] - 0.01) for a, c in zip(sent, sent[1:]) if c["start"] - a["end"] > 0.05]
    gaps = [g for g in gaps if g[1] - g[0] > 0.03]
    bed = np.median([win_rms_db(b, g0, g1) for g0, g1 in gaps]) if len(gaps) >= 2 else None
    word_band = win_rms_db(b, w["start"], w["end"])
    # preferred: the stem measurement build_soundtrack.py writes (ending.<word>_min_margin_db or closing_min_margin_db)
    end = (sr or {}).get("ending", {})
    stem = next((end[k] for k in end if k.endswith("_min_margin_db") and isinstance(end[k], (int, float))), None)
    if stem is not None:
        check("last word over bed", "L18", stem >= 12, f"+{stem:.1f} dB (stems, soundtrack_report)", ">= +12 dB in 300-4000 Hz")
    elif bed is None:
        check("last word over bed", "L18", False, "not measurable (< 2 word gaps)", ">= +12 dB in 300-4000 Hz", "WARN",
              note="measure it on the stems (clean narration vs the ducked bed)")
    else:
        check("last word over bed", "L18", word_band - bed >= 12, f"+{word_band - bed:.1f} dB (gap estimate)", ">= +12 dB in 300-4000 Hz",
              "WARN", note="estimated from the sentence's word gaps; WARN means measure it on the stems")


def floor_check(audio, tl):
    mono = audio.mean(1)
    hop, wl = int(0.01 * SR), int(0.1 * SR)
    start = int(tl.get("lead_seconds", 0.5) * SR)
    end = len(mono) - int(0.6 * SR)  # the final fade is checked by the ending checks
    sq = np.square(mono.astype(np.float64))
    cs = np.concatenate([[0], np.cumsum(sq)])
    idx = np.arange(start, end - wl, hop)
    vals = 10 * np.log10(np.maximum((cs[idx + wl] - cs[idx]) / wl, 1e-12))
    lo = float(vals.min())
    check("audio floor", "L6/L29", lo >= -42, f"{lo:.1f} dBFS at {idx[vals.argmin()] / SR:.2f} s", ">= -42 dBFS (100 ms windows)")


def sfx_checks(props, sr, tl):
    fps = tl["fps"]
    rows = sr.get("sfx", [])
    off = []
    for r in rows:
        if "placed_at_s" in r and "frame" in r:
            land = r["placed_at_s"] + r.get("landing_offset_in_sample_s", 0.0)
            d = (land - r["frame"] / fps) * fps
            if abs(d) > 1.0:
                off.append(f'{r.get("name", r.get("id"))} {d:+.1f} f')
    check("sfx land on their frames", "L4/L41", not off, f"{len(rows)} cues, {len(off)} off", "landing within 1 f of its key frame", note="; ".join(off[:8]))
    fr, au = sr.get("frames", {}), props.get("audio", {})
    diff = [k for k in fr if k in au and fr[k] != au[k]]
    check("props key frames == soundtrack", "L4", not diff, f"{len(diff)} mismatched", "props.audio == soundtrack_report.frames", note=str(diff[:8]))


def first_word_sfx_check(sr, tl):
    """L57: an SFX cue landing on the first word of the film must not sit over it in the phone band (voice-over-SFX, not
    only SFX-over-bed). Uses the cue windows build_soundtrack.py measured (final_phone_band_dbfs.sfx / .voice)."""
    rows = sr.get("sfx", [])
    words = tl.get("words", [])
    if not rows or not words or "start" not in words[0]:
        return
    w0 = words[0]
    hot = []
    for r in rows:
        land = r.get("placed_at_s", 0.0) + r.get("landing_offset_in_sample_s", 0.0)
        fb = r.get("final_phone_band_dbfs") or {}
        if w0["start"] - 0.1 <= land <= w0["end"] + 0.3 and isinstance(fb.get("sfx"), (int, float)) and isinstance(fb.get("voice"), (int, float)):
            if fb["sfx"] - fb["voice"] > 3.0:
                hot.append(f'{r.get("name", r.get("id"))} +{fb["sfx"] - fb["voice"]:.1f} dB over \'{w0["text"]}\'')
    check("sfx under the first word", "L57", not hot, hot[0] if hot else f"no cue over '{w0['text']}' by > 3 dB",
          "no SFX > +3 dB over the first word in 300-4000 Hz", "WARN", note="lead the cue before the word and duck the lead-in" if hot else "")


def claim_graphic_exit_check(props, tl):
    """L42/L47/L52: a claim's graphics (placards, the plate window) leave >= 6 f before the honesty tab's next glide, never
    straddle it. Reads props.placards[enter, exit], props.window.open[] and props.meter[glideStart, frame]."""
    glides = [(m["glideStart"], m["frame"], m.get("claim", "")) for m in props.get("meter", []) if m.get("glideStart") is not None and m["frame"] > 0]
    if not glides:
        return
    late = []
    for i, pl in enumerate(props.get("placards", [])):
        for g0, g1, claim in glides:
            if pl["enter"] < g0 - 6 < pl["exit"] <= g1 + 60:
                late.append(f"placard {i + 1} exits f{pl['exit']} vs glide f{g0} ({claim})")
    op = (props.get("window") or {}).get("open")
    if isinstance(op, list) and op:
        a = np.array(op, dtype=float) > 0.05
        edges = np.where(a[:-1] & ~a[1:])[0]  # last open frame before each close
        for f in edges.tolist():
            for g0, g1, claim in glides:
                if g0 - 6 < f <= g1 + 60:
                    late.append(f"window still open at f{f} vs glide f{g0} ({claim})")
    check("claim graphics gone before the glide", "L42/L52", not late, f"{len(late)} late" if late else "all >= 6 f before", ">= 6 f before the tab glide", "WARN",
          note="; ".join(late[:6]))


def fine_print_check(props, project):
    """L33/L54: no on-screen text under 24 px, INCLUDING axis numbers and counter labels. Scans numeric *size/*Px leaves in
    props and fontSize literals in the build's tsx (shared/, overlay/, scenes/)."""
    small = []

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool) and re.search(r"(size|px)$", k, re.I) and 0 < v < 24:
                    small.append(f"props.{path}{k}={v}")
                else:
                    walk(v, f"{path}{k}.")
        elif isinstance(o, list) and o and isinstance(o[0], dict):
            for i, v in enumerate(o[:50]):
                walk(v, f"{path}{i}.")

    walk(props, "")
    files = glob.glob(str(project / "*.ts")) + glob.glob(str(project / "shared/*.tsx")) + glob.glob(str(project / "overlay/*.tsx")) + glob.glob(str(project / "scenes/*.tsx"))
    for f in sorted(x for x in files if not Path(x).name.startswith("_")):  # _stub.tsx etc. are not rendered
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            for m in re.finditer(r"fontSize:\s*(\d+(?:\.\d+)?)\b|\b(\w*Px):\s*(\d+)\b", line):
                v = float(m.group(1) or m.group(3))
                if 0 < v < 24:
                    small.append(f"{Path(f).relative_to(project)}:{n} {m.group(0).strip()}")
    check("fine print >= 24 px", "L33/L54", not small, f"{len(small)} under 24 px", "every text size >= 24 px (props *size/*Px and tsx fontSize)", "WARN",
          note="; ".join(small[:8]))


def still_hold_check(v, tl, props):
    """L25: the picture is constant from the release (+ the tab's own 8 f settle and a 3 f CTA swap = 12 f) to the end."""
    stem, rel_f, _, _ = last_word(tl)
    f0 = min(len(v) - 2, rel_f + 12)
    d = np.abs(np.diff(v[f0:], axis=0)).mean((1, 2))
    worst = float(d.max()) if len(d) else 0.0
    first_const = next((f0 + i for i in range(len(d)) if float(d[i:].max()) < 0.05), len(v))
    check("still hold after the release", "L25", worst < 0.3, f"max frame diff {worst:.2f} from f{f0}; bit-constant from f{first_const}",
          f"no change from '{stem}' release f{rel_f} + 12 f to the end", "WARN", note="a CTA fade or a tab still gliding eats the settle")


def pixel_checks(master, tl):
    w, h = 270, 480
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(master), "-vf", f"scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    v = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    pixel_checks.frames = v
    mean = v.mean((1, 2))
    black = np.where(mean < 6)[0]
    check("no black frames", "picture", len(black) == 0, f"{len(black)} frames", "mean luma >= 6", note=str(black[:10].tolist()))
    d = np.abs(np.diff(v, axis=0)).mean((1, 2))  # d[i] = |f[i+1]-f[i]|
    flashes = []
    for i in range(1, len(v) - 1):
        a, b, c = d[i - 1], d[i], np.abs(v[i + 1] - v[i - 1]).mean()
        if a > 12 and b > 12 and c < 0.35 * min(a, b):
            flashes.append(i)
    check("no one-frame flashes", "picture", not flashes, f"{len(flashes)} frames", "no frame unlike both neighbours", note=str(flashes[:10]))
    # UI zones: anything that differs from the zone's usual (median) look = something drawn there
    y0, x0 = int(1574 / 1920 * h), int(929 / 1080 * w)
    for name, z in (("bottom UI zone y>=1574", v[:, y0:, :]), ("right rail x>=929", v[:, int(0.2 * h):int(0.78 * h), x0:])):
        hp = z - uniform_filter(z, size=(1, 5, 5))  # fine detail only: text and thin lines, not glows or gradients
        dev = np.abs(hp - np.median(hp, axis=0)).max(axis=2)  # per row: the strongest new detail vs the usual background
        score = np.sort(dev, axis=1)[:, -4:].mean(1)  # the 4 worst rows: one line of small text is enough
        base = np.median(score)
        hot = np.where(score > max(2.5 * base, base + 12))[0]
        runs = []
        for f in hot.tolist():
            if runs and f == runs[-1][1] + 1:
                runs[-1][1] = f
            else:
                runs.append([f, f])
        check(name, "safe zones", len(hot) == 0, f"{len(hot)} frames with new detail", "no text there", "WARN",
              note=("frames " + ", ".join(f"{a}-{b}" for a, b in runs[:8]) + " - look: text there is a fail" if runs else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--master")
    ap.add_argument("--no-pixels", action="store_true")
    a = ap.parse_args()
    P = Path(a.project)
    A = P / "artifacts"
    master = Path(a.master) if a.master else None
    if master and not master.is_absolute() and not master.exists():
        master = P / master
    if not master:
        m = sorted(glob.glob(str(P / "renders/*master*.mp4")))
        if not m:
            sys.exit("no renders/*master*.mp4; pass --master")
        master = Path(m[0])
    tl, props, script, plan = (jload(A / f) for f in ("timeline.json", "props.json", "script.json", "scene_plan.json"))
    sr = jload(A / "soundtrack_report.json") if (A / "soundtrack_report.json").exists() else {}

    spec_checks(master, tl)
    loudness_checks(master)
    caption_checks(props, tl, script)
    forbidden_check(props, plan)
    audio = decode_audio(master)
    ending_checks(props, tl, audio, sr)
    floor_check(audio, tl)
    sfx_checks(props, sr, tl)
    first_word_sfx_check(sr, tl)
    claim_graphic_exit_check(props, tl)
    fine_print_check(props, P)
    if not a.no_pixels:
        pixel_checks(master, tl)
        still_hold_check(pixel_checks.frames, tl, props)

    fails = [r for r in RESULTS if r["status"] == "FAIL"]
    warns = [r for r in RESULTS if r["status"] == "WARN"]
    for r in RESULTS:
        print(f'{r["status"]:4}  {r["check"]:<32} {str(r["value"])[:60]:<60}  [{r["lesson"]}]  {r["note"][:90]}')
    out = {"master": str(master), "verdict": "FAIL" if fails else "PASS", "fails": len(fails), "warns": len(warns), "checks": RESULTS}
    json.dump(out, open(A / "qa_auto.json", "w"), indent=1)
    print(f'\n{out["verdict"]}: {len(fails)} fail, {len(warns)} warn -> {A / "qa_auto.json"}')
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
