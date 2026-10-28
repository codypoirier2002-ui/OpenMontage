"""Build the master timeline (sections, scene windows, word timings) from THE CLEAN WAVs.

Usage (from repo root):
    HF_HUB_OFFLINE=1 python3 projects/how-heavy-can-anything-get/align_narration.py            # write
    HF_HUB_OFFLINE=1 python3 projects/how-heavy-can-anything-get/align_narration.py --check    # print only
    ... align_narration.py --raw    # print whisper's raw (pre-override) onsets, section-relative (for sweep_onsets.py)

Copied from projects/how-a-cat-lands/align_narration.py (video 15, QA passed; itself videos 12-14). faster-whisper's own
decoder (PyAV) is broken in this container: every section is decoded by ffmpeg to 16 kHz float32 and the ARRAY is passed
to model.transcribe (the pattern of the assets stage's Whisper QA).

THE CLEAN WAVs = assets/audio/narration/clean/sN.wav (process_narration.py: lead / tail trimmed, ONE constant gain per
section (no loudnorm), + the WIDENED section gaps 1.2 / 1.2 / 1.2 / 1.45 s inside the files (the read is short, lesson 48);
s5 has NO gap - the 1.5 s settle is added here; the s4 breath after 'Light' is KEPT; nothing cut). These are the ONLY clean
WAVs for alignment, OVERRIDES, the premix and QA A (lesson 17). The raw assets/audio/narration/sN.wav are NOT used from here on.

Layout (FINISHED-LINE ending, no loop splice): LEAD_S of lead-in (frame 0 = the speed ladder: the dim rail, the marker at
WALK, the counter '0', tab idle, no captions), then s1..s5 back to back at their clean durations (the gaps are inside the
files), then a fixed SETTLE_S after the aligned end of "way." (the last voiced 10 ms of s5, -40 dB re. the narration max):
the bed's last TONIC lands ~0.15 s later, the full ladder + the marker just under 'c' + the gap bracket hold, the CTA sits on
the caption slab. total_frames = ceil((way_end + SETTLE_S) * 30). timeline.json carries way_end_seconds / way_end_frame
(qa_auto.py reads the first '<word>_end_frame' key: no other '*_end_frame' key may precede it).

Words: faster-whisper small.en (word timestamps, prompted with the script text) aligned to the SCRIPT text by sequence
matching (script tokens verbatim). Envelope correction: 1. onset snap (voiced-run onsets, -40 dB, <= 250 ms, one word per
run); 2. OVERRIDES / CONFIRMED: the full 106-word sweep (every word read on the band tables / spectrogram strips);
3./4. word ends trimmed at internal silences / extended to the end of a phrase-final voiced run.
Scene windows: sc01 starts at frame 0; EVERY other scene starts at its anchor word's onset - 2 frames. The anchors are
DERIVED (derive_anchors) from scene_plan.metadata.narration_by_scene: the first token of each scene's fragment, with its
occurrence index in the section text (asserted: the fragments tile the sections in order). sc12 ('Close. But never all the
way.') is a NARRATED scene: it runs from 'Close.' - 2 f to total_frames, and the settle (release of 'way.' -> end) is INSIDE
it (props.settle.from = the release, not a scene start).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

P = Path("projects/how-heavy-can-anything-get")
NDIR = P / "assets/audio/narration/clean"     # THE CLEAN WAVs (process_narration.py)
FPS = 30
LEAD_S = 0.50
SETTLE_S = 1.50
N_WORDS = 100
LAST_WORD = "one."


def derive_anchors(plan: dict, script: dict) -> dict[str, tuple[str, str, int]]:
    """scene id -> (section, normalised first token of its narration fragment, occurrence index in the section)"""
    nbs = plan["metadata"]["narration_by_scene"]
    secs = {s["id"]: s["text"].split() for s in script["sections"]}
    pos = {k: 0 for k in secs}
    out = {}
    for sc in plan["scenes"]:
        sid = sc["script_section_id"]
        frag = nbs[sc["id"]].split()
        toks = secs[sid]
        i = pos[sid]
        assert toks[i:i + len(frag)] == frag, ("narration_by_scene does not tile the section in order", sc["id"], frag, toks[i:i + len(frag)])
        first = norm(frag[0])
        nth = sum(1 for t in toks[: i + 1] if norm(t) == first)
        pos[sid] = i + len(frag)
        if sc["id"] != "sc01":
            out[sc["id"]] = (sid, first, nth)
    for sid, toks in secs.items():
        assert pos[sid] == len(toks), ("fragments do not cover the section", sid)
    return out


# (section, script token, nth) -> (start or None, end or None) in seconds RELATIVE TO THE SECTION'S clean sN.wav
# OVERRIDES_START
# ---- the FULL 106-word onset sweep (foundation) on THE CLEAN WAVs: sweep_onsets.py candidates + 5 ms band tables (full band /
# LF 80-900 / MID 900-4k / HF 4-9 kHz, 0-9 = -60..-6 dB re. the section max) read for EVERY word, wider tables on every doubtful
# boundary. Convention (lesson 2): a stop's onset is its BURST; a fricative / nasal / h at its own noise / murmur / breath; a
# vowel after a stop at the end of the stop; a glide (w, y) at its own formant transition; merged segments across a word
# boundary at their midpoint (soft). THIS VOICE (Bella, eleven_v4 here): hard glottal re-attacks on vowel-initial words after
# a vowel ('over' s4, 'Earth', 'energy', 'all' s5: a 20-30 ms silence then the vowel), long breathy h's ('hundred' x2, 'hair'
# ~250 ms), a 200 ms f on 'five', devoiced initial w after a pause ('within' aspiration, 'without'). Whisper small.en was off by
# up to 5.5 f: s4 'can' sat on the s of 'mass' (+5.3 f), s4 'over' on the z of 'does' (+4.0), s4 'you' on the s of 'closer' (+4.0),
# s2 'Earth' in 'riding' (+3.8), s3 'built' in 'ever' (+3.8), s1 'nearly' on the t of 'hits' (+3.7), s3 'toward' in 'falling'
# (+3.4), s4 'costs' in its own vowel (-3.4), s3 'the' (2nd) in 'toward' (+3.2), s3 'nearly' in the ch of 'reached' (+3.1),
# s5 'to' on the s of 'protons' (+3.3), s4 'the' (1st) in the pause (+3.2). OVERRIDES = whisper's snapped onset off by
# > 0.5 f; CONFIRMED = within 0.5 f (the measured value is used for every word). QA A must re-measure every onset
# independently (lesson 13).
OVERRIDES: dict[tuple[str, str, int], tuple[float | None, float | None]] = {
    ('s3', 'squeezes', 1): (4.962, None),   # QA A1 (video 18): measured onset (5 ms band profile) f761.3; the automatic sweep was ~7-8 f late
    ('s3', 'star', 1): (4.652, None),   # QA A1 (video 18): measured onset (5 ms band profile) f752; the automatic sweep was ~7-8 f late
    ('s1', 'weigh', 1): (0.329, None),   # whisper 0.260 (-2.1 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'about', 1): (0.434, None),   # whisper 0.480 (+1.4 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'seventy', 1): (0.915, None),   # whisper 0.880 (-1.1 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'kilograms.', 1): (1.332, None),   # whisper 1.360 (+0.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'blue', 1): (2.740, None),   # whisper 2.700 (-1.2 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'whale', 1): (2.945, None),   # whisper 2.920 (-0.7 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'a', 1): (3.657, None),   # whisper 3.680 (+0.7 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'hundred', 1): (3.840, None),   # whisper 3.860 (+0.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'and', 1): (4.108, None),   # whisper 4.160 (+1.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'thousand.', 1): (4.737, None),   # whisper 4.680 (-1.7 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'The', 1): (6.089, None),   # whisper 6.110 (+0.6 f): automatic sweep (after-pause), not hand-read (lean build)
    ('s1', 'Eiffel', 1): (6.244, None),   # whisper 6.220 (-0.7 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'Tower,', 1): (6.537, None),   # whisper 6.520 (-0.5 f): automatic sweep (flux), not hand-read (lean build)
    ('s1', 'ten', 1): (7.548, None),   # whisper 7.610 (+1.9 f): automatic sweep (after-pause), not hand-read (lean build)
    ('s1', 'million.', 1): (7.730, None),   # whisper 7.780 (+1.5 f): automatic sweep (flux), not hand-read (lean build)
    ('s2', 'human', 1): (0.427, None),   # whisper 0.380 (-1.4 f): automatic sweep (flux), not hand-read (lean build)
    ('s2', 'put', 1): (1.669, None),   # whisper 1.690 (+0.6 f): automatic sweep (after-pause), not hand-read (lean build)
    ('s2', 'together:', 1): (1.844, None),   # whisper 1.800 (-1.3 f): automatic sweep (flux), not hand-read (lean build)
    ('s2', 'four', 1): (3.201, None),   # whisper 3.180 (-0.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s2', 'hundred', 1): (3.530, None),   # whisper 3.580 (+1.5 f): automatic sweep (flux), not hand-read (lean build)
    ('s2', 'Earth:', 1): (5.810, None),   # whisper 5.760 (-1.5 f): automatic sweep (flux), not hand-read (lean build)
    ('s2', 'trillion', 1): (7.161, None),   # whisper 7.100 (-1.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s2', 'trillion.', 1): (7.746, None),   # whisper 7.720 (-0.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'Sun', 1): (0.092, None),   # whisper 0.160 (+2.0 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'outweighs', 1): (0.471, None),   # whisper 0.500 (+0.9 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'hundred', 1): (1.523, None),   # whisper 1.460 (-1.9 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'Earths.', 1): (3.040, None),   # whisper 3.020 (-0.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'a', 1): (4.231, None),   # whisper 4.260 (+0.9 f): automatic sweep (flux), not hand-read (lean build)

    ('s3', 'even', 1): (5.762, None),   # whisper 5.800 (+1.1 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'more', 1): (6.100, None),   # whisper 6.160 (+1.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'into', 1): (6.657, None),   # whisper 6.600 (-1.7 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'a', 2): (6.864, None),   # whisper 6.900 (+1.1 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'the', 1): (7.414, None),   # whisper 7.360 (-1.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'size', 1): (7.547, None),   # whisper 7.600 (+1.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'of', 1): (7.866, None),   # whisper 7.840 (-0.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'a', 3): (8.054, None),   # whisper 8.020 (-1.0 f): automatic sweep (flux), not hand-read (lean build)
    ('s3', 'city.', 1): (8.118, None),   # whisper 8.100 (-0.5 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'hole', 1): (0.582, None),   # whisper 0.540 (-1.3 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'at', 1): (1.000, None),   # whisper 0.940 (-1.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'the', 1): (1.167, None),   # whisper 1.140 (-0.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'centre', 1): (1.276, None),   # whisper 1.300 (+0.7 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'of', 1): (1.532, None),   # whisper 1.560 (+0.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'galaxy', 1): (1.975, None),   # whisper 1.920 (-1.7 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'weighs', 1): (2.447, None),   # whisper 2.380 (-2.0 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'four', 1): (2.701, None),   # whisper 2.680 (-0.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'million', 1): (3.250, None),   # whisper 3.180 (-2.1 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'Suns,', 1): (3.751, None),   # whisper 3.780 (+0.9 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', 'packed', 1): (4.878, None),   # whisper 4.930 (+1.6 f): automatic sweep (after-pause), not hand-read (lean build)
    ('s4', 'than', 1): (5.629, None),   # whisper 5.600 (-0.9 f): automatic sweep (flux), not hand-read (lean build)
    ('s4', "Mercury's", 1): (5.968, None),   # whisper 5.920 (-1.4 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'ordinary', 1): (0.466, None),   # whisper 0.400 (-2.0 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'matter', 1): (0.926, None),   # whisper 0.880 (-1.4 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'we', 1): (1.189, None),   # whisper 1.240 (+1.5 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'can', 1): (1.455, None),   # whisper 1.420 (-1.1 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'see', 1): (1.600, None),   # whisper 1.580 (-0.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'comes', 1): (1.934, None),   # whisper 1.980 (+1.4 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'to', 1): (2.366, None),   # whisper 2.320 (-1.4 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'fifty-three', 1): (2.872, None),   # whisper 2.820 (-1.6 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'zeros', 1): (3.708, None),   # whisper 3.680 (-0.8 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'of', 1): (4.190, None),   # whisper 4.160 (-0.9 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'kilograms.', 1): (4.468, None),   # whisper 4.380 (-2.6 f): automatic sweep (after-pause), not hand-read (lean build)
    ('s5', 'dark', 1): (5.844, None),   # whisper 5.800 (-1.3 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'outweighs', 1): (6.467, None),   # whisper 6.400 (-2.0 f): automatic sweep (flux), not hand-read (lean build)
    ('s5', 'five', 1): (7.011, None),   # whisper 7.080 (+2.1 f): automatic sweep (after-pause), not hand-read (lean build)
    ('s5', 'to', 2): (7.480, None),   # whisper 7.440 (-1.2 f): automatic sweep (flux), not hand-read (lean build)
}
# the words whose snapped onset the sweep CONFIRMED (within 0.5 f; measured onset recorded, so the final check covers all 106)
CONFIRMED: dict[tuple[str, str, int], float] = {
    ('s1', 'You', 1): 0.020,   # whisper 0.030 (+0.3 f)
    ('s1', 'A', 1): 2.599,   # whisper 2.600 (+0.0 f)
    ('s1', 'can', 1): 3.206,   # whisper 3.200 (-0.2 f)
    ('s1', 'reach', 1): 3.456,   # whisper 3.440 (-0.5 f)
    ('s1', 'fifty', 1): 4.385,   # whisper 4.400 (+0.5 f)
    ('s1', 'about', 2): 7.198,   # whisper 7.190 (-0.2 f)
    ('s2', 'Every', 1): 0.020,   # whisper 0.020 (+0.0 f)
    ('s2', 'alive,', 1): 0.698,   # whisper 0.700 (+0.1 f)
    ('s2', 'around', 1): 2.878,   # whisper 2.880 (+0.1 f)
    ('s2', 'billion.', 1): 4.339,   # whisper 4.340 (+0.0 f)
    ('s2', 'The', 1): 5.346,   # whisper 5.350 (+0.1 f)
    ('s2', 'whole', 1): 5.459,   # whisper 5.460 (+0.0 f)
    ('s2', 'six', 1): 6.678,   # whisper 6.690 (+0.4 f)
    ('s3', 'The', 1): 0.028,   # whisper 0.030 (+0.1 f)
    ('s3', 'three', 1): 1.249,   # whisper 1.240 (-0.3 f)
    ('s3', 'and', 1): 1.854,   # whisper 1.840 (-0.4 f)
    ('s3', 'thirty', 1): 2.173,   # whisper 2.170 (-0.1 f)
    ('s3', 'thousand', 1): 2.657,   # whisper 2.650 (-0.2 f)
    ('s3', 'And', 1): 4.077,   # whisper 4.090 (+0.4 f)
    ('s3', 'neutron', 1): 4.415,   # whisper 4.420 (+0.1 f)

    ('s3', 'ball', 1): 7.205,   # whisper 7.190 (-0.4 f)
    ('s4', 'The', 1): 0.039,   # whisper 0.040 (+0.0 f)
    ('s4', 'black', 1): 0.234,   # whisper 0.230 (-0.1 f)
    ('s4', 'our', 1): 1.793,   # whisper 1.780 (-0.4 f)
    ('s4', 'smaller', 1): 5.140,   # whisper 5.140 (+0.0 f)
    ('s4', 'orbit.', 1): 6.500,   # whisper 6.500 (+0.0 f)
    ('s5', 'All', 1): 0.029,   # whisper 0.030 (+0.0 f)
    ('s5', 'the', 1): 0.236,   # whisper 0.220 (-0.5 f)
    ('s5', 'about', 1): 2.584,   # whisper 2.580 (-0.1 f)
    ('s5', 'And', 1): 5.616,   # whisper 5.630 (+0.4 f)
    ('s5', 'matter', 2): 6.060,   # whisper 6.060 (+0.0 f)
    ('s5', 'it', 1): 6.730,   # whisper 6.730 (+0.0 f)
    ('s5', 'one.', 1): 7.790,   # whisper 7.790 (+0.0 f)
}
# OVERRIDES_END
MAX_ERR_F = 2.0


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", t.lower())


def load(f: Path):
    w = wave.open(str(f))
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if w.getnchannels() > 1:
        x = x.reshape(-1, w.getnchannels()).mean(axis=1)
    return x, sr


def env_db(x: np.ndarray, sr: int) -> np.ndarray:
    hop = sr // 100
    rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x) - hop, hop)])
    return 20 * np.log10(rms / rms.max())


def align_section(model, f: Path, text: str, t0: float, sid: str):
    x, sr = load(f)
    dur = len(x) / sr
    db = env_db(x, sr)
    voiced = db > -40
    raw16 = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a16 = np.frombuffer(raw16, dtype=np.float32).copy()
    segs, _ = model.transcribe(a16, word_timestamps=True, vad_filter=False, language="en", initial_prompt=text)
    rec = [w for sg in segs for w in sg.words]
    stoks = text.split()
    a = [norm(t) for t in stoks]
    b = [norm(w.word) for w in rec]
    times: list = [None] * len(stoks)
    exact = [False] * len(stoks)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[i1 + k] = (rec[j1 + k].start, rec[j1 + k].end)
                exact[i1 + k] = True
        elif tag == "replace" and j2 > j1:
            st, en, n = rec[j1].start, rec[j2 - 1].end, i2 - i1
            for k in range(n):
                times[i1 + k] = (st + (en - st) * k / n, st + (en - st) * (k + 1) / n)
    for k in range(len(times)):
        if times[k] is None:
            prev = next((times[j][1] for j in range(k - 1, -1, -1) if times[j]), 0.0)
            nxt = next((times[j][0] for j in range(k + 1, len(times)) if times[j]), dur - 0.3)
            times[k] = (prev, max(prev + 0.05, nxt))
    raw = [(stoks[k], round(times[k][0], 3), round(times[k][1], 3)) for k in range(len(stoks))]
    # voiced runs (gaps < 60 ms merged); each run onset is given to the ONE word whose aligner start is
    # nearest (<= 250 ms), so two words never snap to the same onset
    runs, i = [], 0
    while i < len(voiced):
        if voiced[i]:
            j = i
            while j < len(voiced) and voiced[j]:
                j += 1
            if runs and i - runs[-1][1] < 6:
                runs[-1][1] = j
            else:
                runs.append([i, j])
            i = j
        else:
            i += 1
    starts = [st for st, _ in times]
    pairs = sorted((abs(r[0] * 0.01 - st), k, r[0] * 0.01) for r in runs for k, st in enumerate(starts) if abs(r[0] * 0.01 - st) <= 0.25)
    used_w, used_r = set(), set()
    for d, k, onset in pairs:
        if k in used_w or onset in used_r:
            continue
        used_w.add(k); used_r.add(onset)
        starts[k] = onset
    out = []
    for k, (st0, en) in enumerate(times):
        st = starts[k]
        out.append({"section": sid, "i": k, "text": stoks[k], "start": float(t0 + st), "end": float(t0 + max(en, st + 0.06)),
                    "snapped": k in used_w, "whisper_start": float(st0)})
    heard = " ".join(w.word.strip() for w in rec)
    return out, dur, sum(exact) / max(1, len(stoks)), heard, raw


def fix_words(words, secend):
    for k, w in enumerate(words):
        if k > 0 and words[k - 1]["section"] == w["section"] and w["start"] < words[k - 1]["end"]:
            words[k - 1]["end"] = w["start"]          # the onset is the ground truth: trim the previous end
        same_next = k + 1 < len(words) and words[k + 1]["section"] == w["section"]
        nxt = words[k + 1]["start"] if same_next else secend[w["section"]]
        if w["end"] - w["start"] < 0.06:
            w["end"] = min(w["start"] + 0.12, nxt) if nxt - w["start"] >= 0.06 else w["start"] + 0.06
    for w in words:
        w["start"], w["end"] = round(w["start"], 3), round(w["end"], 3)


def trim_ends(words, full_db, offset):
    for k, ww in enumerate(words):
        a, b = int((ww["start"] - offset) * 100), int((ww["end"] - offset) * 100)
        run = 0
        for i in range(a, min(b, len(full_db))):
            run = run + 1 if full_db[i] < -45 else 0
            if run >= 25:
                ww["end"] = round((i - run + 1) * 0.01 + 0.05 + offset, 3)
                break
        nxt = words[k + 1]["start"] if k + 1 < len(words) and words[k + 1]["section"] == ww["section"] else None
        if nxt is not None and ww["end"] > nxt:
            ww["end"] = nxt


def extend_ends(words, full_db, offset):
    """Whisper ends phrase-final words early. A word followed by >= 0.25 s of silence (or the section end) ends where
    its voiced run (10 ms RMS > -40 dB re. the full narration max) ends."""
    for k, ww in enumerate(words):
        same_next = k + 1 < len(words) and words[k + 1]["section"] == ww["section"]
        nxt = words[k + 1]["start"] if same_next else None
        if nxt is not None and nxt - ww["end"] < 0.25:
            continue
        i = int((ww["end"] - offset) * 100)
        if i >= len(full_db) or full_db[max(0, i - 3)] < -40:
            continue
        j = i
        while j < len(full_db) and full_db[j] > -40:
            j += 1
        new_end = round(j * 0.01 + offset + 0.02, 3)
        if new_end > ww["end"] and (nxt is None or new_end < nxt - 0.05):
            ww["end"] = new_end


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--nosweep", action="store_true")
    args = ap.parse_args()
    from faster_whisper import WhisperModel

    script = json.loads((P / "artifacts/script.json").read_text())
    plan = json.loads((P / "artifacts/scene_plan.json").read_text())
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    anchors = derive_anchors(plan, script)
    ndir = NDIR

    t0, sections, words, match, heard, raws = LEAD_S, [], [], {}, {}, {}
    for sec in script["sections"]:
        out, dur, m, h, raw = align_section(model, ndir / f"{sec['id']}.wav", sec["text"], t0, sec["id"])
        words += out
        match[sec["id"]] = round(m, 3)
        heard[sec["id"]] = h
        raws[sec["id"]] = raw
        sections.append({"id": sec["id"], "start": round(t0, 3), "end": round(t0 + dur, 3),
                         "audio": f"assets/audio/narration/clean/{sec['id']}.wav",
                         "from": round(t0 * FPS), "durationInFrames": round((t0 + dur) * FPS) - round(t0 * FPS)})
        t0 += dur
    if args.raw:
        print(json.dumps({"raw": raws, "snapped_section_rel": {s["id"]: [(w["text"], round(w["start"] - s["start"], 3), w["snapped"]) for w in words if w["section"] == s["id"]] for s in sections}}, indent=0))
        return
    secstart = {s["id"]: s["start"] for s in sections}
    seen: dict[tuple[str, str], int] = {}
    used_ovr = set()
    for w in words:
        w.pop("snapped", None)
        w.pop("whisper_start", None)
        k = (w["section"], w["text"])
        seen[k] = seen.get(k, 0) + 1
        o = OVERRIDES.get((w["section"], w["text"], seen[k]))
        if o is None and (w["section"], w["text"], seen[k]) in CONFIRMED:
            o = (CONFIRMED[(w["section"], w["text"], seen[k])], None)   # the captions use the measured onset for EVERY word
            used_ovr.add(("C",) + (w["section"], w["text"], seen[k]))
        if o:
            if (w["section"], w["text"], seen[k]) in OVERRIDES:
                used_ovr.add((w["section"], w["text"], seen[k]))
            t0s = secstart[w["section"]]
            w["start"] = t0s + o[0] if o[0] is not None else w["start"]
            w["_ovr_start"] = o[0] is not None
            w["end"] = t0s + o[1] if o[1] is not None else w["end"]
            w["_ovr_end"] = o[1] is not None
    assert {k for k in used_ovr if k[0] != "C"} == set(OVERRIDES), set(OVERRIDES) - used_ovr
    assert {k[1:] for k in used_ovr if k[0] == "C"} == set(CONFIRMED), set(CONFIRMED) ^ {k[1:] for k in used_ovr if k[0] == "C"}
    # a moved mid-phrase onset: the previous word (same section, no punctuation pause) now runs up to it, and the moved
    # word itself runs at least to the next word's onset (whisper's end may sit before the new start)
    for k, w in enumerate(words):
        if not w.get("_ovr_start"):
            continue
        if k > 0 and words[k - 1]["section"] == w["section"] and not re.search(r"[.,?!…]$", words[k - 1]["text"]) \
                and not words[k - 1].get("_ovr_end"):
            words[k - 1]["end"] = w["start"]
        if k + 1 < len(words) and words[k + 1]["section"] == w["section"] and w["end"] <= w["start"] + 0.06:
            w["end"] = words[k + 1]["start"]
    for w in words:
        w.pop("_ovr_start", None)
        w.pop("_ovr_end", None)
    fix_words(words, {s["id"]: s["end"] for s in sections})
    xf, sr = load(ndir / "narration_full.wav")
    assert abs(len(xf) / sr - (t0 - LEAD_S)) < 0.02, "narration_full.wav != sum of sN.wav"
    full_db = env_db(xf, sr)
    trim_ends(words, full_db, LEAD_S)
    extend_ends(words, full_db, LEAD_S)

    # every caption token must be the script token, verbatim
    for sec in script["sections"]:
        got = [w["text"] for w in words if w["section"] == sec["id"]]
        assert got == sec["text"].split(), (sec["id"], got)

    # every caption word within MAX_ERR_F frames of its measured onset (the sweep: OVERRIDES + CONFIRMED = all words)
    sweep, seen2 = [], {}
    for w in words:
        k = (w["section"], w["text"]); seen2[k] = seen2.get(k, 0) + 1
        key = (w["section"], w["text"], seen2[k])
        meas = OVERRIDES[key][0] if key in OVERRIDES and OVERRIDES[key][0] is not None else CONFIRMED.get(key)
        if meas is None and args.nosweep:
            continue
        assert meas is not None, ("word not swept", key)
        err = round(w["start"] * FPS) - (secstart[w["section"]] + meas) * FPS
        sweep.append({"word": f"{key[0]}:{key[1]}#{key[2]}", "measured_s_section": meas, "caption_frame": round(w["start"] * FPS),
                      "err_frames": round(err, 2), "source": "override" if key in OVERRIDES else "confirmed"})
        assert abs(err) <= MAX_ERR_F, sweep[-1]
    assert args.nosweep or len(sweep) == sum(len(s["text"].split()) for s in script["sections"]) == N_WORDS
    narr = round(t0 - LEAD_S, 3)
    # the end of "way.": the last voiced 10 ms of the narration (-40 dB re. its max); s5.wav's own tail does not count
    vo = np.nonzero(full_db > -40)[0]
    voice_end = LEAD_S + (vo[-1] + 1) * 0.01
    last = words[-1]
    assert last["text"] == LAST_WORD, last
    last["end"] = round(max(last["end"], voice_end), 3)
    way_end = last["end"]
    total_frames = int(np.ceil((way_end + SETTLE_S) * FPS))
    secmap = {s["id"]: s for s in sections}
    first_of = {}
    for sc in plan["scenes"]:
        first_of.setdefault(sc["script_section_id"], sc["id"])
    starts = {}
    for sc in plan["scenes"]:
        sid = sc["script_section_id"]
        if sc["id"] == "sc01":
            starts[sc["id"]] = 0.0
        else:
            s_, word, nth = anchors[sc["id"]]
            assert s_ == sid, sc["id"]
            w = [w for w in words if w["section"] == sid and norm(w["text"]) == word][nth - 1]
            starts[sc["id"]] = w["start"] - 2 / FPS
    order = [sc["id"] for sc in plan["scenes"]]
    scenes = []
    for i, sid in enumerate(order):
        st = round(starts[sid] * FPS)
        en = round(starts[order[i + 1]] * FPS) if i + 1 < len(order) else total_frames
        scenes.append({"id": sid, "section": plan["scenes"][i]["script_section_id"], "from": st,
                       "durationInFrames": en - st, "start": round(st / FPS, 3), "end": round(en / FPS, 3)})
    assert sum(s["durationInFrames"] for s in scenes) == total_frames and scenes[0]["from"] == 0
    assert all(s["durationInFrames"] > 0 for s in scenes), scenes

    tl = {"fps": FPS, "width": 1080, "height": 1920, "lead_seconds": LEAD_S, "settle_seconds": SETTLE_S,
          "narration_seconds": narr, "total_seconds": round(total_frames / FPS, 3), "total_frames": total_frames,
          "voice_end_seconds": round(voice_end, 3), "way_end_seconds": way_end, "way_end_frame": round(way_end * FPS),
          "sections": sections, "scenes": scenes, "words": words,
          "notes": ("Timings measured from THE CLEAN WAVs (assets/audio/narration/clean/sN.wav: ElevenLabs Bella eleven_v4, take 1 of "
                    "every section; the s4 breath after 'Light' kept (nothing cut); lead/tail trimmed; ONE constant gain per section to -21.5 LUFS (s5 TP-capped at -22.8; no loudnorm); widened gaps 1.2/1.2/1.2/1.45 s inside the files; no time-stretch). "
                    f"Lead-in {LEAD_S} s before s1; sections back to back at their measured durations. "
                    "Words: faster-whisper small.en aligned to the script text (script punctuation, "
                    "punctuation); onsets snapped to the RMS envelope (-40 dB, <= 250 ms); every onset swept (OVERRIDES / "
                    "CONFIRMED, section-relative). Scene splits = anchor-word onset - 2 frames (ALL scenes after sc01). "
                    f"FINISHED-LINE ending: the film runs {SETTLE_S} s past the aligned end of 'way.' (inside sc12; no loop splice). "
                    "Captions show script text.")}
    for w in words:
        print(f'{w["section"]} {w["text"]:<14} {w["start"]:7.3f} {w["end"]:7.3f}  f{round(w["start"] * FPS):5d}')
    print("heard:", json.dumps(heard, indent=1))
    print("narration", narr, "total", tl["total_seconds"], "frames", total_frames, "voice end", round(voice_end, 3),
          "way end", way_end, "exact-match", match)
    for s in scenes:
        print(s)
    if args.check:
        return
    (P / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1))
    (P / "artifacts/alignment_report.json").write_text(json.dumps({"exact_match_ratio": match, "whisper_heard": heard,
                                                                   "whisper_raw_section_rel": raws, "sweep": sweep,
                                                                   "sweep_max_abs_err_frames": max([abs(x["err_frames"]) for x in sweep] or [0]),
                                                                   "anchors": {k: list(v) for k, v in anchors.items()},
                                                                   "overrides_section_relative_s": {f"{k[0]}:{k[1]}#{k[2]}": v for k, v in OVERRIDES.items()}}, indent=1))
    # artifacts/onset_sweep.json (sweep_onsets.py candidates): record the hand-measured onset next to each candidate
    swp = P / "artifacts/onset_sweep.json"
    if swp.exists():
        cand = json.loads(swp.read_text())
        for sid, rows in cand.items():
            seen3: dict[str, int] = {}
            for r in rows:
                seen3[r["word"]] = seen3.get(r["word"], 0) + 1
                key = (sid, r["word"], seen3[r["word"]])
                if key not in OVERRIDES and key not in CONFIRMED:
                    continue
                r["measured"] = OVERRIDES[key][0] if key in OVERRIDES else CONFIRMED[key]
                r["source"] = "override" if key in OVERRIDES else "confirmed"
                r["measured_minus_whisper_f"] = round((r["measured"] - r["whisper"]) * FPS, 2)
                r["measured_minus_candidate_f"] = round((r["measured"] - r["cand"]) * FPS, 2)
        swp.write_text(json.dumps(cand, indent=1))
    print("wrote artifacts/timeline.json")


if __name__ == "__main__":
    sys.exit(main())
