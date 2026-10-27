#!/usr/bin/env python3
"""Caption-onset sweep helper (lesson 2): candidate onsets for ALL 106 words on the clean WAVs, independent of Whisper.

    python3 projects/how-a-cat-lands/sweep_onsets.py raw.json            # table + artifacts/onset_sweep.json
    python3 projects/how-a-cat-lands/sweep_onsets.py raw.json s3 about   # zoom: 1 ms profile around one word

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

P = Path("projects/how-a-cat-lands")
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


def strip(sid: str, words, t, tot, lf, mid, hf, flux, rows) -> None:
    """--strip: a compact 5 ms text strip per word (g-100 ms .. g+70 ms) of the four levels (0-9 = -60..-6 dB re. the
    section max, 6 dB per step) + a flux mark, the guess '|' and the candidate '^' (the hand check reads these)"""
    q = lambda v: str(int(np.clip((v + 60) / 6, 0, 9)))
    for (w, g, _), r in zip(words, rows):
        a, b = np.searchsorted(t, g - 0.10), np.searchsorted(t, g + 0.07)
        idx = list(range(a, b, 5))
        mk = "".join("|" if abs(t[i] - g) < 0.0025 else "^" if abs(t[i] - r["cand"]) < 0.0025 else " " for i in idx)
        fm = "".join("*" if flux[i] > 60 else "+" if flux[i] > 30 else "." for i in idx)
        print(f"{sid} {w:<13} g {g:6.3f} c {r['cand']:6.3f} ({r['how'][:5]}) {r['diff_f']:+5.1f}f  t0 {t[a]:.3f}")
        for name, arr in (("tot", tot), ("LF ", lf), ("MID", mid), ("HF ", hf)):
            print(f"   {name} " + "".join(q(arr[i]) for i in idx))
        print(f"   flx {fm}\n   mrk {mk}")


def pngs(sid: str, words, outdir: Path, chunk_s: float = 1.25) -> None:
    """--png: spectrogram strips (1 px = 1 ms, 0-9 kHz, 4 ms Hann / 1 ms hop) + the band envelopes (tot white, LF orange,
    MID green, HF cyan; 0 to -60 dB) with 10 ms ticks (50 ms labelled); whisper's snapped onset red, the decided onset
    (OVERRIDES / CONFIRMED in align_narration.py, if any) yellow. One PNG per chunk_s seconds of the clean section."""
    from PIL import Image, ImageDraw
    x, sr = load(NDIR / f"{sid}.wav")
    n, hop = 192, sr // 1000
    win = np.hanning(n).astype(np.float32)
    idx = np.arange(0, len(x) - n, hop)
    S = np.abs(np.fft.rfft(np.stack([x[i:i + n] * win for i in idx]), axis=1)) ** 2 + 1e-12
    f = np.fft.rfftfreq(n, 1 / sr)
    keep = f <= 9000
    D = 10 * np.log10(S[:, keep])
    D = np.clip((D - (D.max() - 80)) / 80, 0, 1)
    t, tot, lf, mid, hf, flux = features(x, sr)
    dec = {}
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("al", P / "align_narration.py")
        al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
        seen: dict = {}
        for w, g, _ in words:
            seen[w] = seen.get(w, 0) + 1
            key = (sid, w, seen[w])
            v = al.OVERRIDES.get(key, (None,))[0] if key in al.OVERRIDES else al.CONFIRMED.get(key)
            if v is not None:
                dec[(w, seen[w])] = v
    except Exception as e:  # noqa: BLE001
        print("no decisions loaded:", e)
    outdir.mkdir(parents=True, exist_ok=True)
    dur = len(x) / sr
    k = 0
    while k * chunk_s < dur:
        a = int(k * chunk_s * 1000); b = min(len(idx), int((k + 1) * chunk_s * 1000))
        W, Hs, He = b - a, 260, 150
        im = Image.new("RGB", (W, Hs + He + 16), (0, 0, 0))
        spec_img = (255 * D[a:b].T[::-1]).astype(np.uint8)
        im.paste(Image.fromarray(spec_img).resize((W, Hs)), (0, 0))
        d = ImageDraw.Draw(im)
        for name, arr, col in (("tot", tot, (255, 255, 255)), ("LF", lf, (255, 160, 40)), ("MID", mid, (60, 230, 60)), ("HF", hf, (60, 200, 255))):
            seg = arr[a:b]
            pts = [(i, Hs + 8 + He * (-np.clip(v, -60, 0) / 60)) for i, v in enumerate(seg)]
            d.line(pts, fill=col, width=1)
        for ms in range(a - a % 10, b, 10):
            X = ms - a
            if X < 0:
                continue
            big = ms % 50 == 0
            d.line([(X, Hs), (X, Hs + (8 if big else 4))], fill=(200, 200, 200))
            if big:
                d.line([(X, 0), (X, 6)], fill=(200, 200, 200))
                d.text((X + 1, Hs + He + 4), f"{ms / 1000:.2f}", fill=(200, 200, 200))
        seen2: dict = {}
        for w, g, _ in words:
            seen2[w] = seen2.get(w, 0) + 1
            X = int(g * 1000) - a
            if 0 <= X < W:
                d.line([(X, 0), (X, Hs + He)], fill=(255, 40, 40))
                d.text((X + 2, 10), w, fill=(255, 80, 80))
            v = dec.get((w, seen2[w]))
            if v is not None and 0 <= int(v * 1000) - a < W:
                Xv = int(v * 1000) - a
                d.line([(Xv, 0), (Xv, Hs + He)], fill=(255, 230, 0))
                d.text((Xv + 2, 24), w, fill=(255, 230, 0))
        im.save(outdir / f"{sid}_{k:02d}.png")
        k += 1


def main() -> None:
    raw = json.loads(Path(sys.argv[1]).read_text())["snapped_section_rel"]
    if len(sys.argv) > 2 and sys.argv[2] == "--png":
        for sid, words in raw.items():
            if len(sys.argv) > 3 and sid != sys.argv[3]:
                continue
            pngs(sid, words, Path(sys.argv[4] if len(sys.argv) > 4 else "/tmp/onset_png"))
        return
    if len(sys.argv) > 2 and sys.argv[2] == "--strip":
        for sid, words in raw.items():
            if len(sys.argv) > 3 and sid != sys.argv[3]:
                continue
            x, sr = load(NDIR / f"{sid}.wav")
            t, tot, lf, mid, hf, flux = features(x, sr)
            rows, prev = [], -1.0
            for k, (w, g, _) in enumerate(words):
                c, how = candidate(t, tot, flux, g, prev)
                rows.append({"cand": round(c, 3), "how": how, "diff_f": round((g - c) * FPS, 2)})
                prev = c
            strip(sid, words, t, tot, lf, mid, hf, flux, rows)
        return
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
