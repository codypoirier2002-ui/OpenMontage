#!/usr/bin/env python3
"""Caption-onset sweep helper (lesson 2): candidate onsets for ALL 109 words on the clean WAVs, independent of Whisper.

    python3 projects/how-hot-can-it-get/sweep_onsets.py raw.json            # table + artifacts/onset_sweep.json
    python3 projects/how-hot-can-it-get/sweep_onsets.py raw.json s3 about   # zoom: 1 ms profile around one word

raw.json = the output of align_narration.py --raw (Whisper's snapped section-relative onsets: the initial guess only).
Features (5.3 ms STFT window, 1 ms hop): full-band RMS dB and three band envelopes LF 80-900 / MID 900-4k / HF 4-9 kHz,
plus positive log-spectral flux. Candidate onset per word:
  * after a pause (the 40 ms before the guess holds a run < -45 dB re. the section max): the first 1 ms frame of the voiced
    run that is 12 dB above the local floor (a stop's burst, a fricative's noise, an h's breath, a vowel's voicing);
  * otherwise: the frame of maximum positive spectral flux within +-70 ms of the guess (not earlier than the previous
    word's onset + 50 ms): a stop's BURST, a fricative's noise rise, the vowel after a stop, a nasal/l/w transition.
Words where |candidate - whisper| > 1.5 f are hand-checked with the zoom view (band envelopes), and the decided onset goes
into align_narration.py OVERRIDES (with a comment); the rest go into CONFIRMED. Convention: a stop's onset is its burst;
a fricative, nasal or /h/ starts at its own noise / murmur; a vowel after a stop at the end of the stop.
"""
from __future__ import annotations

import json
import sys
import wave
from pathlib import Path

import numpy as np

P = Path("projects/how-hot-can-it-get")
NDIR = P / "assets/audio/narration/clean"     # THE CLEAN WAVs (process_narration.py)
FPS = 30


def load(f: Path):
    w = wave.open(str(f))
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x, sr


def features(x: np.ndarray, sr: int):
    n, hop = 256, sr // 1000
    win = np.hanning(n).astype(np.float32)
    idx = np.arange(0, len(x) - n, hop)
    fr = np.stack([x[i:i + n] * win for i in idx])
    S = np.abs(np.fft.rfft(fr, axis=1)) ** 2 + 1e-12
    f = np.fft.rfftfreq(n, 1 / sr)
    band = lambda lo, hi: 10 * np.log10(S[:, (f >= lo) & (f < hi)].sum(1) + 1e-12)
    tot = 10 * np.log10(S.sum(1))
    ref = tot.max()
    L = np.log(S)
    flux = np.concatenate([[0], np.maximum(0, np.diff(L, axis=0)).sum(1)])
    flux = np.convolve(flux, np.ones(3) / 3, mode="same")
    t = (idx + n / 2) / sr
    return t, tot - ref, band(80, 900) - ref, band(900, 4000) - ref, band(4000, 9000) - ref, flux


def candidate(t, tot, flux, guess, prev_on):
    i0 = int(np.searchsorted(t, guess))
    pre = tot[max(0, i0 - 40): i0]
    lo = max(prev_on + 0.05, guess - 0.07)
    if len(pre) and (pre < -45).sum() >= 15:
        # after a pause: first frame 12 dB above the local floor, within [guess - 70 ms, guess + 120 ms]
        a, b = np.searchsorted(t, max(lo, guess - 0.07)), np.searchsorted(t, guess + 0.12)
        floor = np.percentile(tot[max(0, a - 60): a + 1], 20)
        hit = np.nonzero(tot[a:b] > floor + 12)[0]
        return float(t[a + hit[0]]) if len(hit) else guess, "after-pause"
    a, b = np.searchsorted(t, lo), np.searchsorted(t, guess + 0.07)
    if b <= a:
        return guess, "none"
    return float(t[a + int(np.argmax(flux[a:b]))]), "flux"


def main() -> None:
    raw = json.loads(Path(sys.argv[1]).read_text())["snapped_section_rel"]
    out = {}
    for sid, words in raw.items():
        x, sr = load(NDIR / f"{sid}.wav")
        t, tot, lf, mid, hf, flux = features(x, sr)
        if len(sys.argv) > 3 and sys.argv[2] == sid:
            seen = 0
            for k, (w, g, _) in enumerate(words):
                if w.lower().strip(".,:?!") == sys.argv[3].lower():
                    seen += 1
                    if len(sys.argv) > 4 and seen != int(sys.argv[4]):
                        continue
                    a, b = np.searchsorted(t, g - 0.16), np.searchsorted(t, g + 0.16)
                    print(f"{sid} {w} guess {g}")
                    for i in range(a, b, 5):
                        bar = "#" * int(max(0, (flux[i]) / 8))
                        print(f"{t[i]:7.3f} tot {tot[i]:6.1f} LF {lf[i]:6.1f} MID {mid[i]:6.1f} HF {hf[i]:6.1f} {bar}")
            return
        rows, prev = [], -1.0
        for k, (w, g, snapped) in enumerate(words):
            c, how = candidate(t, tot, flux, g, prev)
            rows.append({"k": k, "word": w, "whisper": g, "cand": round(c, 3), "how": how, "diff_f": round((g - c) * FPS, 2)})
            prev = c
        out[sid] = rows
        for r in rows:
            flag = "  <-- check" if abs(r["diff_f"]) > 1.5 else ""
            print(f'{sid} {r["word"]:<14} whisper {r["whisper"]:6.3f} cand {r["cand"]:6.3f} ({r["how"]:<11}) diff {r["diff_f"]:+6.2f} f{flag}')
    if len(sys.argv) <= 2:
        (P / "artifacts/onset_sweep.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
