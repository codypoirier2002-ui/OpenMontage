#!/usr/bin/env python3
"""Make THE CLEAN WAVs (lesson 17): assets/audio/narration/clean/s1..s5.wav + narration_full.wav + process_report.json.

    python3 projects/how-a-cat-lands/process_narration.py        # from the repo root

Copied from projects/how-a-mosquito-drinks/process_narration.py (video 14, QA passed). NO loudnorm: each section gets ONE
CONSTANT linear gain (video 13 QA: loudnorm fell back to dynamic normalisation).

The assets stage delivered UNTRIMMED, UN-NORMALISED takes (assets/audio/narration/sN.wav, 48 kHz mono, take 1 of every
section; Whisper QA passed). This script makes the only WAVs used from here on for alignment, OVERRIDES, the premix and QA A:

  1. Lead / tail: keep LEAD_PRE_S before the first 5 ms block above -50 dB re. the section peak, and TAIL_POST_S after the
     last one (3 ms fade-in, 20 ms fade-out on digital near-silence).
     s4 ENDS ON A CLICK (assets_report N-s4: the last 15 ms jump from about -80 to -33 dB re. full scale at 4.225-4.24 s, a
     truncation): the take is CUT at S4_CUT_S (4.20 s, after 'four.' has decayed to about -80 dB) with a 20 ms fade-out, and
     the cut's last 20 ms are asserted < -60 dB re. the section peak (no click survives).
  2. Loudness: ONE constant gain per section so every section measures TARGET_LUFS integrated (ffmpeg ebur128 on the
     trimmed section), capped so the true peak stays <= TP_MAX (recorded, never compressed). The premix sets the delivery
     loudness with one master gain.
  3. + the section GAP as digital silence at the end of each file (s1-s4), so align_narration.py lays the sections back to
     back unchanged. THE READ IS SHORT (38.64 s raw vs 48.11 s planned): the script's pause_after (0.35 / 0.4 / 0.4 / 0.45 s)
     would put the film at ~42 s (format 45-55 s), so the gaps are WIDENED (GAPS: 1.2 / 1.2 / 1.2 s after s1-s3, 1.45 s after
     s4 = the landing beat, where the S2 photo window holds); with the 0.5 s lead-in and the 1.5 s settle after 'vet' the film
     is >= 45.2 s (asserted below on the estimate; align_narration.py measures it).
Lesson 29 (baked-in pauses): every internal silence >= 0.2 s of every section is listed in process_report.json with the
preceding script punctuation check; all sit at punctuation (asserted: their count per section <= the section's internal
punctuation marks), so NOTHING is cut.
The lesson-30 lifts ('all four' about +4 dB, 'reached the vet' about +5 dB) are NOT applied here (the clean WAVs stay the
untouched alignment / QA reference): build_soundtrack.py applies them as constant gains on the voice lane of the premix.
"""
from __future__ import annotations

import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

P = Path("projects/how-a-cat-lands")
RAW = P / "assets/audio/narration"
OUT = RAW / "clean"
SR = 48000
LEAD_PRE_S = 0.03
TAIL_POST_S = 0.10
THR_DB = -50.0
TARGET_LUFS = -21.5
TP_MAX = -1.5
S4_CUT_S = 4.20
GAPS = {"s1": 1.20, "s2": 1.20, "s3": 1.20, "s4": 1.45, "s5": 0.0}
LEAD_S, SETTLE_S, MIN_FILM_S = 0.50, 1.50, 45.2


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


def ebur(f: Path) -> tuple[float, float]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])


def silences(x: np.ndarray, min_s: float = 0.2, thr: float = -45.0) -> list[list[float]]:
    db = env_db(x, 480)
    out, i = [], 0
    while i < len(db):
        if db[i] < thr:
            j = i
            while j < len(db) and db[j] < thr:
                j += 1
            if (j - i) * 0.01 >= min_s and i > 0 and j < len(db):
                out.append([round(i * 0.01, 2), round((j - i) * 0.01, 2)])
            i = j
        else:
            i += 1
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    script = json.loads((P / "artifacts/script.json").read_text())
    report, full, t = {}, [], 0.0
    for sec in script["sections"]:
        sid = sec["id"]
        x = load(RAW / f"{sid}.wav")
        rec: dict = {"raw_file": f"assets/audio/narration/{sid}.wav", "raw_duration": round(len(x) / SR, 3)}
        if sid == "s4":
            x = x[: int(S4_CUT_S * SR)].copy()
            k = int(0.02 * SR)
            x[-k:] *= np.linspace(1, 0, k)
            rec["click_cut"] = {"cut_at_s": S4_CUT_S, "fade_out_s": 0.02,
                                "why": "the raw take ends on a click (-80 -> -33 dB re. full scale in the last 15 ms, 4.225-4.24 s)"}
        db = env_db(x)
        v = np.nonzero(db > THR_DB)[0]
        a = max(0, int(v[0] * 240 - LEAD_PRE_S * SR))
        b = min(len(x), int((v[-1] + 1) * 240 + TAIL_POST_S * SR))
        rec["lead_trimmed_s"] = round(a / SR, 3)
        rec["tail_trimmed_s"] = round((len(x) - b) / SR, 3)
        x = x[a:b].copy()
        k = int(0.003 * SR)
        x[:k] *= np.linspace(0, 1, k)
        x[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
        if sid == "s4":
            last = x[-int(0.02 * SR):]
            lvl = 20 * np.log10(np.sqrt((last ** 2).mean()) + 1e-12) - 20 * np.log10(np.abs(x).max())
            assert lvl < -60, ("s4 end click survived", lvl)
            rec["click_cut"]["last_20ms_db_re_peak"] = round(float(lvl), 1)
        tmp = OUT / f"_{sid}_trim.wav"
        save(tmp, x)
        in_i, in_tp = ebur(tmp)
        gain = TARGET_LUFS - in_i
        capped = False
        if in_tp + gain > TP_MAX:
            gain = TP_MAX - in_tp
            capped = True
        y = x * 10 ** (gain / 20)
        save(tmp, y)
        out_i, out_tp = ebur(tmp)
        tmp.unlink()
        assert out_tp <= TP_MAX + 0.05, (sid, out_tp)
        sil = silences(y)
        punct = len(re.findall(r"[,.;:?!]", sec["text"].rstrip(".?!")))
        assert len(sil) <= punct, ("lesson 29: more internal pauses than punctuation marks", sid, sil, punct)
        rec["internal_silences_ge_0.2s_[start,dur]"] = sil
        rec["lesson29"] = f"{len(sil)} internal pauses >= 0.2 s for {punct} internal punctuation marks: all at punctuation (nothing cut)"
        gap = GAPS[sid]
        y = np.concatenate([y, np.zeros(int(round(gap * SR)))])
        save(OUT / f"{sid}.wav", y)
        rec.update({"in_I_lufs": in_i, "in_TP_dbfs": in_tp, "gain_db": round(gain, 2), "gain_tp_capped": capped,
                    "out_I_lufs": out_i, "out_TP_dbfs": out_tp, "normalisation": "ONE constant linear gain (no loudnorm, no dynamics)",
                    "gap_after": gap, "script_pause_after": float(sec["delivery_cues"]["pause_after_seconds"]),
                    "duration": round(len(y) / SR, 4), "start_in_full": round(t, 4),
                    "speech_s": round((len(y) - gap * SR) / SR, 3), "file": f"assets/audio/narration/clean/{sid}.wav"})
        t += len(y) / SR
        full.append(y)
        report[sid] = rec
        print(sid, {k: v for k, v in rec.items() if k not in ("raw_file", "file")})
    save(OUT / "narration_full.wav", np.concatenate(full))
    # film estimate: lead + everything up to the end of the voiced s5 (-45 dB re. peak) + settle
    s5 = full[-1]
    e = env_db(s5, 480)
    s5_voice_end = (np.nonzero(e > -45)[0][-1] + 1) * 0.01
    est = LEAD_S + (t - len(s5) / SR) + s5_voice_end + SETTLE_S
    assert est >= MIN_FILM_S, ("film under 45 s: widen GAPS", est)
    report["total_seconds"] = round(t, 4)
    report["film_estimate_s"] = round(est, 3)
    report["gaps"] = GAPS
    report["target_lufs"] = TARGET_LUFS
    report["process"] = __doc__.split("\n\n", 1)[1]
    (OUT / "process_report.json").write_text(json.dumps(report, indent=1))
    print("total", round(t, 3), "s; film estimate", round(est, 3), "s -> wrote", OUT)


if __name__ == "__main__":
    main()
