#!/usr/bin/env python3
"""Make THE CLEAN WAVs (lesson 17): assets/audio/narration/clean/s1..s5.wav + narration_full.wav + process_report.json.

    python3 projects/how-hot-can-it-get/process_narration.py        # from the repo root

Pattern copied from projects/what-if-earth-stopped-spinning/process_narration.py (video 12, delivered, QA passed).
The assets stage delivered UNTRIMMED, UN-NORMALISED takes (assets/audio/narration/sN.wav, 48 kHz mono, decoded from the
selected MP3s). This script makes the only WAVs used from here on for alignment, OVERRIDES, the premix and QA A:

  1. s3 ONLY - THE BAKED-IN PAUSE CUT (lesson 29; assets_report N-s3 edit_fix): take 1 has 0.22 s of near-silence between
     'held' and 'a hundred million degrees' (raw 5.48-5.70 s), mid-clause. Measured here (10 ms bands): the l/d voicing
     of 'held' decays by 5.49 (sub -60 dBFS 5.50-5.52), a weak 500-8000 Hz breath / d-release hump at ~-50 dBFS
     5.52-5.64 (no LF; ~47 dB under the speech peaks: inaudible), digital near-silence 5.64-5.69 (-73..-78 dBFS), the
     schwa of 'a' at 5.700. The cut removes S3_CUT = [5.505, 5.672] s (raw s3 seconds) in one piece, both splice sides
     < -60 dBFS, 10 ms raised-cosine crossfade: the pause left between the decay of 'held' and 'a' is ~0.05 s (asserted
     0.03-0.08 s below -45 dBFS). Nothing else is cut anywhere (no beat pause trimmed).
  2. Lead / tail: keep LEAD_PRE_S before the first 5 ms block above -50 dB re. the section peak, and TAIL_POST_S after
     the last one (the decays are kept; the tails reach < -60 dBFS).
  3. Loudness: ffmpeg loudnorm two-pass, I = -16 LUFS, TP = -1.5 dBTP, LRA 11, linear=true (ffmpeg falls back to
     dynamic when the linear gain would break the true-peak ceiling; norm_type is recorded per section, as video 12).
  4. + the script's pause_after (script.json delivery_cues.pause_after_seconds: 0.35 / 0.4 / 0.45 / 0.45 / 0) as digital
     silence at the end of each file, so align_narration.py lays the sections back to back unchanged (video 12 layout).
The last word 'know' is NOT lifted here (the clean WAVs stay the untouched alignment / QA reference): build_soundtrack.py
applies its constant broadband gain on the voice lane (as video 12's 'time'). Its span on the CLEAN s5 is measured here
(nasal onset: 2-6 kHz drops while 80-400 Hz stays up; end = the last 10 ms above -45 dB re. the section peak) ->
process_report.json s5.know_span_clean_s.
"""
from __future__ import annotations

import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

P = Path("projects/how-hot-can-it-get")
RAW = P / "assets/audio/narration"
OUT = RAW / "clean"
SR = 48000
S3_CUT = (5.505, 5.672)
XFADE_S = 0.010
LEAD_PRE_S = 0.03
TAIL_POST_S = 0.10
THR_DB = -50.0
KNOW_RAW_NEAR = (10.30, 10.80)   # assets_report N-s5 cadence: 'know' raw 10.38-10.76 s (re-measured on the clean s5)


def load(f: Path) -> np.ndarray:
    w = wave.open(str(f))
    assert w.getframerate() == SR and w.getnchannels() == 1, f
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768


def save(f: Path, x: np.ndarray) -> None:
    y = np.clip(np.round(x * 32767), -32768, 32767).astype(np.int16)
    with wave.open(str(f), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())


def env_db(x: np.ndarray, hop: int = 240) -> np.ndarray:
    n = len(x) // hop
    r = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-14)
    return 20 * np.log10(r / r.max())


def cut(x: np.ndarray, a_s: float, b_s: float) -> np.ndarray:
    a, b, k = int(a_s * SR), int(b_s * SR), int(XFADE_S * SR)
    fo = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, k))
    mid = x[a - k:a] * fo + x[b:b + k] * fo[::-1]
    return np.concatenate([x[:a - k], mid, x[b + k:]])


def level_dbfs(x: np.ndarray, t_s: float, w_s: float = 0.005) -> float:
    a = int(t_s * SR)
    seg = x[a:a + int(w_s * SR)]
    return float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12))


def gap_below(x: np.ndarray, lo_s: float, hi_s: float, db: float) -> float:
    """the longest run (s) of 1 ms blocks under `db` dBFS inside [lo, hi]"""
    a, b = int(lo_s * SR), int(hi_s * SR)
    hop = 48
    seg = x[a:b]
    n = len(seg) // hop
    lv = 20 * np.log10(np.sqrt((seg[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-12)
    best = run = 0
    for v in lv < db:
        run = run + 1 if v else 0
        best = max(best, run)
    return float(best * hop / SR)


def know_span(y: np.ndarray, near: tuple[float, float]) -> dict:
    """'know' on the clean s5: the /n/ onset = the first 5 ms frame after the preceding 'we' where 2-6 kHz falls >= 15 dB
    under its level 30 ms earlier while 80-400 Hz stays within 8 dB; the end = the last 10 ms above -45 dB re. the peak."""
    n, hop = 256, 240
    a, b = int(near[0] * SR), int(near[1] * SR)
    idx = np.arange(a, b - n, hop)
    win = np.hanning(n)
    S = np.abs(np.fft.rfft(np.stack([y[i:i + n] * win for i in idx]), axis=1)) ** 2 + 1e-14
    f = np.fft.rfftfreq(n, 1 / SR)
    hf = 10 * np.log10(S[:, (f >= 2000) & (f < 6000)].sum(1))
    lf = 10 * np.log10(S[:, (f >= 80) & (f < 400)].sum(1))
    t = (idx + n / 2) / SR
    onset = None
    for i in range(6, len(t)):
        if hf[i - 6] - hf[i] >= 15 and abs(lf[i] - lf[i - 6]) <= 8 and lf[i] > lf.max() - 25:
            onset = float(t[i - 3])
            break
    e = env_db(y, 480)
    voiced = np.nonzero(e > -45)[0]
    end = float((voiced[-1] + 1) * 480 / SR)
    return {"onset_s": round(onset, 3) if onset else None, "end_s": round(end, 3)}


def loudnorm(src: Path, dst: Path) -> dict:
    flt = "loudnorm=I=-16:TP=-1.5:LRA=11"
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", flt + ":print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(re.findall(r"\{[^{}]*\}", err, re.S)[-1])
    flt2 = (f"{flt}:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:print_format=json")
    err = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(src), "-af", flt2, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(dst)],
                         capture_output=True, text=True).stderr
    m2 = json.loads(re.findall(r"\{[^{}]*\}", err, re.S)[-1])
    return {"in_I": m["input_i"], "in_TP": m["input_tp"], "out_I": m2["output_i"], "out_TP": m2["output_tp"], "norm_type": m2["normalization_type"]}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    script = json.loads((P / "artifacts/script.json").read_text())
    report, full, t = {}, [], 0.0
    for sec in script["sections"]:
        sid = sec["id"]
        x = load(RAW / f"{sid}.wav")
        rec: dict = {"raw_file": f"assets/audio/narration/{sid}.wav", "raw_duration": round(len(x) / SR, 3)}
        lead_shift = 0.0
        if sid == "s3":
            sides = [level_dbfs(x, S3_CUT[0] - 0.005), level_dbfs(x, S3_CUT[1])]
            assert max(sides) < -60, ("splice sides must be < -60 dBFS", sides)
            before = gap_below(x, 5.40, 5.75, -45.0)
            x = cut(x, *S3_CUT)
            after = gap_below(x, 5.40, 5.75 - (S3_CUT[1] - S3_CUT[0]), -45.0)
            rec["pause_cut"] = {"removed_raw_s": list(S3_CUT), "removed_s": round(S3_CUT[1] - S3_CUT[0], 3), "crossfade_s": XFADE_S,
                                "splice_side_levels_dbfs": [round(v, 1) for v in sides],
                                "sub_minus45_dbfs_pause_before_s": round(before, 3), "sub_minus45_dbfs_pause_after_s": round(after, 3),
                                "note": "lesson 29: the baked-in pause between 'held' and 'a hundred' cut in one piece (incl. a ~-50 dBFS breath hump); 'held a hundred million degrees' is one clause again"}
            assert 0.03 <= after <= 0.08, after
        db = env_db(x)
        v = np.nonzero(db > THR_DB)[0]
        a = max(0, int(v[0] * 240 - LEAD_PRE_S * SR))
        b = min(len(x), int((v[-1] + 1) * 240 + TAIL_POST_S * SR))
        rec["lead_trimmed_s"] = round(a / SR, 3)
        rec["tail_trimmed_s"] = round((len(x) - b) / SR, 3)
        lead_shift = a / SR
        x = x[a:b]
        k = int(0.003 * SR)
        x[:k] *= np.linspace(0, 1, k)
        x[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
        tmp = OUT / f"_{sid}_trim.wav"
        save(tmp, x)
        ln = loudnorm(tmp, OUT / f"_{sid}_ln.wav")
        tmp.unlink()
        y = load(OUT / f"_{sid}_ln.wav")
        (OUT / f"_{sid}_ln.wav").unlink()
        pause = float(sec["delivery_cues"]["pause_after_seconds"])
        if sid == "s5":
            near = (KNOW_RAW_NEAR[0] - lead_shift, min(len(y) / SR, KNOW_RAW_NEAR[1] - lead_shift))
            ks = know_span(y, near)
            assert ks["onset_s"] is not None and 0.25 < ks["end_s"] - ks["onset_s"] < 0.55, ks
            rec["know_span_clean_s"] = ks
            rec["know_span_raw_equiv_s"] = [round(ks["onset_s"] + lead_shift, 3), round(ks["end_s"] + lead_shift, 3)]
        y = np.concatenate([y, np.zeros(int(round(pause * SR)))])
        save(OUT / f"{sid}.wav", y)
        rec.update(ln)
        rec.update({"pause_after": pause, "duration": round(len(y) / SR, 4), "start_in_full": round(t, 4),
                    "speech_s": round((len(y) - pause * SR) / SR, 3), "file": f"assets/audio/narration/clean/{sid}.wav"})
        t += len(y) / SR
        full.append(y)
        report[sid] = rec
        print(sid, rec)
    save(OUT / "narration_full.wav", np.concatenate(full))
    report["total_seconds"] = round(t, 4)
    report["process"] = __doc__.split("\n\n", 1)[1]
    (OUT / "process_report.json").write_text(json.dumps(report, indent=1))
    print("total", round(t, 3), "s -> wrote", OUT)


if __name__ == "__main__":
    main()
