"""Build the master timeline (sections, scene windows, word timings) from THE CLEAN WAVs.

Usage (from repo root):
    HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1 python3 projects/how-a-cat-lands/align_narration.py            # write
    HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1 python3 projects/how-a-cat-lands/align_narration.py --check    # print only
    ... align_narration.py --raw    # print whisper's raw (pre-override) onsets, section-relative (for sweep_onsets.py)

Copied from projects/how-a-mosquito-drinks/align_narration.py (video 14, QA passed; itself videos 12-13).

THE CLEAN WAVs = assets/audio/narration/clean/sN.wav (process_narration.py: lead / tail trimmed, s4's end click cut, ONE
constant gain per section (no loudnorm), + the WIDENED section gaps 1.2 / 1.2 / 1.2 / 1.45 s inside the files (the read is
short); s5 has NO gap - the 1.5 s settle is added here; NO baked-in pause existed, nothing cut). These are the ONLY clean WAVs
for alignment, OVERRIDES, the premix and QA A (lesson 17). The raw assets/audio/narration/sN.wav are NOT used from here on.

Layout (FINISHED-LINE ending, no loop splice): LEAD_S of lead-in (frame 0 = the test lab: rig, header, the cat hanging, the
checklist card, tab idle, no captions), then s1..s5 back to back at their clean durations (the gaps are inside the files),
then a fixed SETTLE_S after the aligned end of "vet." (the last voiced 10 ms of s5, -40 dB re. the narration max): the bed's
last TONIC (G) lands ~0.15 s later, the ledger + the completed checklist hold, the CTA sits on the caption slab.
total_frames = ceil((vet_end + SETTLE_S) * 30). timeline.json carries vet_end_seconds / vet_end_frame (qa_auto.py reads the
first '<word>_end_frame' key: no other '*_end_frame' key may precede it).

Words: faster-whisper small.en (word timestamps, prompted with the script text) aligned to the SCRIPT text by sequence
matching (script tokens verbatim: '1894,' is ONE caption token for the spoken 'eighteen ninety-four'). Envelope correction:
1. onset snap (voiced-run onsets, -40 dB, <= 250 ms, one word per run); 2. OVERRIDES / CONFIRMED: the full 107-word sweep
(every word read by hand on the spectrogram strips); 3./4. word ends trimmed at internal silences / extended to the end of a
phrase-final voiced run.
Scene windows: sc01 starts at frame 0; EVERY other scene starts at its anchor word's onset - 2 frames. The anchors are
DERIVED (derive_anchors) from scene_plan.metadata.narration_by_scene: the first token of each scene's fragment, with its
occurrence index in the section text (asserted: the fragments tile the sections in order). sc12 ('It only counted cats that
reached the vet.') is a NARRATED scene: it runs from 'It' - 2 f to total_frames, and the settle (release of 'vet.' -> end) is
INSIDE it (props.settle.from = the release, not a scene start).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np

P = Path("projects/how-a-cat-lands")
NDIR = P / "assets/audio/narration/clean"     # THE CLEAN WAVs (process_narration.py)
FPS = 30
LEAD_S = 0.50
SETTLE_S = 1.50
N_WORDS = 107
LAST_WORD = "vet."


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
# ---- the FULL 107-word onset sweep (foundation) on THE CLEAN WAVs: spectrogram strips (sweep_onsets.py --png, 1 px = 1 ms,
# band envelopes) read for EVERY word + 10 ms / 5 ms band tables (80-300 / 300-900 / 900-2k / 2-4k / 4-9 kHz) on every
# doubtful boundary. Convention (lesson 2): a stop's onset is its BURST; a fricative / nasal / h at its own noise / murmur /
# breath; a vowel after a stop at the end of the stop; merged segments across a word boundary at their midpoint (soft).
# Whisper small.en was off by up to 7 f (s1 'impossible.' sat on the p burst of 'possible', -7.0 f; s5 'It' sat in the
# silence before it, +5.0 f; s5 'that' / 'percent' / 'on' (s4) / 'can' (s2) / 'fast,' (s3) 4-5 f): every value below is
# hand-measured; OVERRIDES = whisper's snapped onset off by > 0.5 f, the comment gives (measured - whisper) and the cue.
# Soft (+-1-2 f): s1 'it' 'in' 'midair' 'with', s2 'is' 'the' 'half', s3 'the' (x2) 'her' 'follows.', s4 -, s5 'that' (x1)
# 'study' 'reached'. 'But' (s5) is at its BURST after a 55 ms voice bar (video 14 'By' convention). QA A must re-measure every
# onset independently (lesson 13).
OVERRIDES: dict[tuple[str, str, int], tuple[float | None, float | None]] = {
    ("s1", "a", 1):           (0.300, None),   # whisper 0.260 (+1.2 f): 'Drop' p closure 0.255-0.295, release into the schwa 0.300
    ("s1", "cat", 1):         (0.392, None),   # whisper 0.420 (-0.8 f): schwa to 0.37, k closure, k BURST 0.392
    ("s1", "upside", 1):      (0.630, None),   # whisper 0.600 (+0.9 f): 'cat' t closure 0.605-0.625, release into the vowel 0.630
    ("s1", "down,", 1):       (1.045, None),   # whisper 0.920 (+3.7 f): 'side' d + 'down' d merged: closure 0.93-1.04, d BURST 1.045 (whisper sat in 'side')
    ("s1", "flips", 1):       (1.805, None),   # whisper 1.840 (-1.1 f): 'it' t closure 1.78-1.80, f noise 1.805
    ("s1", "over", 1):        (2.205, None),   # whisper 2.100 (+3.1 f): 'flips' s 2.10-2.20, vowel onset 2.205 (whisper sat on the s)
    ("s1", "in", 1):          (2.405, None),   # whisper 2.440 (-1.1 f): 'over' v dip 2.33-2.37, er, i 2.405 (soft)
    ("s1", "midair", 1):      (2.585, None),   # whisper 2.620 (-1.1 f): 'in' n + 'midair' m merged nasal 2.48-2.70: midpoint 2.585 (soft)
    ("s1", "with", 1):        (3.090, None),   # whisper 3.000 (+2.7 f): 'air' r -> w: F2/MID fall from 3.09 (soft)
    ("s1", "push", 1):        (3.868, None),   # whisper 3.840 (+0.8 f): 'to' oo to 3.80, p closure, p BURST 3.868
    ("s1", "on.", 1):         (4.108, None),   # whisper 4.040 (+2.0 f): 'push' sh 3.99-4.10, vowel 4.108 (whisper sat in the sh)
    ("s1", "In", 1):          (4.968, None),   # whisper 4.990 (-0.7 f): after the pause: voicing 4.968
    ("s1", "that", 1):        (6.455, None),   # whisper 6.480 (-0.8 f): after the pause: dh voicing 6.455
    ("s1", "impossible.", 1): (6.825, None),   # whisper 7.060 (-7.0 f): 'looked' k BURST 6.79 + t release 6.81, i vowel 6.825 (whisper 7.06 sat on the p burst of 'possible')
    ("s2", "inner", 1):       (1.045, None),   # whisper 0.980 (+1.9 f): 'its' s to 0.97, glottal closure 0.98-1.04, vowel 1.045
    ("s2", "ear", 1):         (1.345, None),   # whisper 1.240 (+3.1 f): 'inner' r to 1.30, glottal dip 1.30-1.34, vowel 1.345
    ("s2", "finds", 1):       (1.640, None),   # whisper 1.560 (+2.4 f): 'ear' to 1.63, f noise 1.640 (whisper sat in 'ear')
    ("s2", "which", 1):       (2.048, None),   # whisper 1.960 (+2.6 f): 'finds' z 2.00-2.04, w voicing 2.048
    ("s2", "way", 1):         (2.355, None),   # whisper 2.260 (+2.9 f): 'which' ch 2.24-2.33, w voicing 2.355
    ("s2", "it", 1):          (3.820, None),   # whisper 3.760 (+1.8 f): 'Then' n 3.72-3.81, i (2-4 kHz up) 3.820
    ("s2", "bends", 1):       (4.100, None),   # whisper 4.000 (+3.0 f): 'it' t + b voice bar 3.94-4.09, b BURST 4.100 (whisper sat in the voice bar)
    ("s2", "in", 1):          (4.415, None),   # whisper 4.300 (+3.5 f): 'bends' dz 4.36-4.40, vowel 4.415
    ("s2", "middle,", 1):     (4.578, None),   # whisper 4.640 (-1.9 f): 'the' vowel to 4.57, m murmur (MID drop) 4.578
    ("s2", "each", 1):        (5.455, None),   # whisper 5.380 (+2.3 f): 'so' to 5.38, silence, vowel 5.455
    ("s2", "half", 1):        (5.668, None),   # whisper 5.640 (+0.8 f): 'each' ch 5.62-5.66, h breath 5.668 (soft)
    ("s2", "can", 1):         (6.100, None),   # whisper 5.960 (+4.2 f): 'half' f 5.97-6.06, k closure, k BURST 6.100 (whisper sat on the f)
    ("s2", "turn", 1):        (6.275, None),   # whisper 6.220 (+1.7 f): 'can' n to 6.24, t BURST 6.275
    ("s2", "on", 1):          (6.520, None),   # whisper 6.460 (+1.8 f): 'turn' n 6.48-6.51, vowel 6.520
    ("s2", "own.", 1):        (6.797, None),   # whisper 6.780 (+0.5 f): 'its' ts 6.69-6.79, vowel 6.797
    ("s3", "front", 1):       (0.575, None),   # whisper 0.620 (-1.4 f): 'its' s to 0.56, f noise 0.575
    ("s3", "legs,", 1):       (0.925, None),   # whisper 0.880 (+1.4 f): 'front' t closure 0.88-0.92, l voicing 0.925
    ("s3", "front", 2):       (1.735, None),   # whisper 1.800 (-1.9 f): 'the' vowel to 1.72, f noise 1.735
    ("s3", "fast,", 1):       (2.778, None),   # whisper 2.640 (+4.1 f): 'spins' z 2.68-2.775, f noise (4-9 kHz drop) 2.778 (whisper sat in 'spins')
    ("s3", "like", 1):        (3.730, None),   # whisper 3.750 (-0.6 f): after the pause: l voicing 3.730
    ("s3", "skater", 1):      (3.945, None),   # whisper 4.020 (-2.2 f): 'a' to 3.94, s noise 3.945
    ("s3", "in", 1):          (4.872, None),   # whisper 4.780 (+2.8 f): 'pulling' ng 4.82-4.86, i (2-4 kHz up) 4.872
    ("s3", "swaps,", 1):      (6.335, None),   # whisper 6.380 (-1.3 f): 'it' t closure 6.31-6.33, s noise 6.335
    ("s3", "back", 1):        (7.380, None),   # whisper 7.360 (+0.6 f): 'the' to 7.36, b closure, b BURST 7.380
    ("s3", "follows.", 1):    (7.887, None),   # whisper 7.840 (+1.4 f): 'half' f + 'follows' f merged 7.82-7.95: midpoint 7.887 (soft)
    ("s4", "out,", 1):        (0.357, None),   # whisper 0.280 (+2.3 f): 'Legs' g + z 0.26-0.35, vowel 0.357 (whisper sat on the z)
    ("s4", "lands", 1):       (2.740, None),   # whisper 2.720 (+0.6 f): 'it' t closure 2.70-2.735, l voicing 2.740
    ("s4", "on", 1):          (3.130, None),   # whisper 2.980 (+4.5 f): 'lands' dz 3.06-3.11, creaky vowel 3.130 (whisper 2.98 sat in 'lands')
    ("s4", "all", 1):         (3.348, None),   # whisper 3.280 (+2.0 f): 'on' n 3.23-3.27, glottal stop 3.31-3.345, vowel 3.348
    ("s5", "But", 1):         (0.148, None),   # whisper 0.070 (+2.3 f): b voice bar 0.065-0.12, closure, b BURST 0.148
    ("s5", "always.", 1):     (0.555, None),   # whisper 0.520 (+1.1 f): 'not' t (glottal) 0.52-0.55, vowel 0.555
    ("s5", "drops", 1):       (2.028, None),   # whisper 1.920 (+3.2 f): 'Short' t 1.95-1.98, d voice bar, d BURST 2.028
    ("s5", "leave", 1):       (2.448, None),   # whisper 2.360 (+2.6 f): 'drops' s to 2.42, l voicing 2.448
    ("s5", "no", 1):          (2.628, None),   # whisper 2.580 (+1.4 f): 'leave' v 2.57-2.62, n murmur 2.628
    ("s5", "time", 1):        (2.908, None),   # whisper 2.860 (+1.4 f): 'no' to 2.88, t closure, t BURST 2.908
    ("s5", "to", 1):          (3.198, None),   # whisper 3.100 (+2.9 f): 'time' m to 3.17, t closure, t BURST 3.198
    ("s5", "study", 1):       (5.025, None),   # whisper 4.940 (+2.5 f): 'famous' s + 'study' s merged 4.95-5.10: midpoint 5.025 (soft)
    ("s5", "where", 1):       (5.358, None),   # whisper 5.280 (+2.3 f): 'study' y 5.26-5.35, w (2-4 kHz fall) 5.358
    ("s5", "percent", 1):     (6.010, None),   # whisper 5.860 (+4.5 f): 'ninety' t BURST 5.875 + y, p closure 5.96-6.00, p BURST 6.010 (whisper 5.86 sat on the t of 'ninety')
    ("s5", "survived", 1):    (6.355, None),   # whisper 6.260 (+2.9 f): 'percent' t to 6.34, s noise 6.355
    ("s5", "high", 1):        (6.798, None),   # whisper 6.760 (+1.1 f): 'survived' d release 6.79, h breath 6.798
    ("s5", "It", 1):          (8.088, None),   # whisper 7.920 (+5.0 f): after the pause: voicing 8.088 (whisper 7.92 sat in the silence)
    ("s5", "only", 1):        (8.195, None),   # whisper 8.090 (+3.2 f): 'It' t closure 8.18, release 8.19, vowel 8.195
    ("s5", "counted", 1):     (8.455, None),   # whisper 8.420 (+1.1 f): 'only' y to 8.42, k closure, k BURST 8.455
    ("s5", "cats", 1):        (8.862, None),   # whisper 8.740 (+3.7 f): 'counted' d closure 8.76-8.85, k BURST 8.862 (whisper sat in 'counted')
    ("s5", "that", 2):        (9.368, None),   # whisper 9.200 (+5.0 f): 'cats' t + s 9.19-9.33, dh voicing 9.368 (whisper sat on the s)
    ("s5", "reached", 1):     (9.488, None),   # whisper 9.460 (+0.8 f): 'that' t (unreleased) 9.44-9.48, r voicing 9.488 (soft)
    ("s5", "the", 1):         (9.790, None),   # whisper 9.660 (+3.9 f): 'reached' ch 9.65-9.75, closure, dh release 9.790
    ("s5", "vet.", 1):        (9.862, None),   # whisper 9.900 (-1.1 f): 'the' vowel to 9.86, v (LF only) 9.862
}
# the words whose snapped onset the sweep CONFIRMED (within 0.5 f; measured onset recorded, so the final check covers all 107)
CONFIRMED: dict[tuple[str, str, int], float] = {
    ("s1", "Drop", 1):        0.030,           # whisper 0.030 (+0.0 f): d burst out of the lead
    ("s1", "and", 1):         1.600,           # whisper 1.600 (+0.0 f): after the comma: creaky voicing onset 1.600
    ("s1", "it", 1):          1.722,           # whisper 1.720 (+0.1 f): 'and' n -> i: MID rise 1.722 (soft)
    ("s1", "nothing", 1):     3.245,           # whisper 3.240 (+0.1 f): 'with' th 3.20-3.24, n murmur 3.245
    ("s1", "to", 1):          3.565,           # whisper 3.560 (+0.1 f): 'nothing' ng to 3.55, t BURST 3.565
    ("s1", "1894,", 1):       5.095,           # whisper 5.100 (-0.1 f): 'In' n -> 'ei' of eighteen: onset transient 5.095
    ("s1", "looked", 1):      6.630,           # whisper 6.620 (+0.3 f): 'that' t closure 6.61-6.63, l voicing 6.630
    ("s2", "First,", 1):      0.030,           # whisper 0.040 (-0.3 f): f noise out of the lead
    ("s2", "its", 1):         0.797,           # whisper 0.800 (-0.1 f): after the pause: vowel 0.797
    ("s2", "is", 1):          2.490,           # whisper 2.500 (-0.3 f): 'way' -> 'is': F1 minimum 2.49 (soft)
    ("s2", "up.", 1):         2.660,           # whisper 2.660 (+0.0 f): 'is' z 2.58-2.65, glottal attack 2.660
    ("s2", "Then", 1):        3.467,           # whisper 3.470 (-0.1 f): after the pause: dh voicing 3.467
    ("s2", "the", 1):         4.525,           # whisper 4.520 (+0.2 f): 'in' n 4.46-4.52 -> dh/vowel 4.525 (soft)
    ("s2", "so", 1):          5.210,           # whisper 5.220 (-0.3 f): after the comma: s noise 5.210
    ("s2", "its", 2):         6.628,           # whisper 6.640 (-0.4 f): 'on' n 6.60-6.62, i (2-4 kHz up) 6.628
    ("s3", "It", 1):          0.030,           # whisper 0.040 (-0.3 f): voicing out of the lead
    ("s3", "tucks", 1):       0.175,           # whisper 0.160 (+0.4 f): 'It' t closure 0.10-0.17, t BURST 0.175
    ("s3", "its", 1):         0.465,           # whisper 0.460 (+0.2 f): 'tucks' s to 0.46, vowel 0.465
    ("s3", "and", 1):         1.565,           # whisper 1.570 (-0.2 f): after the comma: voicing 1.565
    ("s3", "the", 1):         1.675,           # whisper 1.680 (-0.1 f): 'and' n -> dh 1.675 (soft)
    ("s3", "half", 1):        2.015,           # whisper 2.000 (+0.5 f): 'front' t closure 1.99-2.01, h breath 2.015
    ("s3", "spins", 1):       2.305,           # whisper 2.320 (-0.4 f): 'half' f + 'spins' s: s noise jump 2.305
    ("s3", "a", 1):           3.860,           # whisper 3.860 (+0.0 f): 'like' k closure 3.83-3.85, vowel 3.860
    ("s3", "pulling", 1):     4.578,           # whisper 4.580 (-0.1 f): 'skater' to 4.51, p closure, p BURST 4.578
    ("s3", "her", 1):         4.990,           # whisper 4.980 (+0.3 f): 'in' n 4.93-4.96, h breath 4.990 (soft)
    ("s3", "arms.", 1):       5.150,           # whisper 5.140 (+0.3 f): 'her' r to 5.12, glottal dip, vowel 5.150
    ("s3", "Then", 1):        6.078,           # whisper 6.090 (-0.4 f): after the pause: dh voicing 6.078
    ("s3", "it", 1):          6.248,           # whisper 6.240 (+0.2 f): 'Then' n 6.22-6.24, vowel 6.248
    ("s3", "and", 2):         7.155,           # whisper 7.150 (+0.1 f): after the comma: voicing 7.155
    ("s3", "the", 2):         7.272,           # whisper 7.260 (+0.4 f): 'and' n 7.20-7.27 -> dh/vowel 7.272 (soft)
    ("s3", "half", 2):        7.590,           # whisper 7.580 (+0.3 f): 'back' k BURST 7.585, h breath 7.590
    ("s4", "Legs", 1):        0.025,           # whisper 0.030 (-0.1 f): l voicing out of the lead
    ("s4", "back", 1):        1.187,           # whisper 1.190 (-0.1 f): after the comma: b BURST 1.187
    ("s4", "arched,", 1):     1.415,           # whisper 1.420 (-0.1 f): 'back' k BURST 1.41, creaky vowel 1.415
    ("s4", "it", 1):          2.565,           # whisper 2.580 (-0.5 f): after the comma: voicing 2.565
    ("s4", "four.", 1):       3.522,           # whisper 3.520 (+0.1 f): 'all' l to 3.52, f noise 3.522
    ("s5", "not", 1):         0.265,           # whisper 0.260 (+0.2 f): 'But' t (glottal) 0.25-0.26, n murmur 0.265
    ("s5", "Short", 1):       1.665,           # whisper 1.680 (-0.4 f): after the pause: sh noise 1.665
    ("s5", "turn.", 1):       3.292,           # whisper 3.280 (+0.4 f): 'to' to 3.26, t closure, t BURST 3.292
    ("s5", "And", 1):         4.330,           # whisper 4.340 (-0.3 f): after the pause: voicing 4.330
    ("s5", "that", 1):        4.445,           # whisper 4.440 (+0.1 f): 'And' n -> dh/vowel 4.445 (soft)
    ("s5", "famous", 1):      4.575,           # whisper 4.580 (-0.1 f): 'that' t closure 4.55-4.57, f noise 4.575
    ("s5", "ninety", 1):      5.525,           # whisper 5.520 (+0.2 f): 'where' r -> n (2-4 kHz drop) 5.525
    ("s5", "falls?", 1):      7.028,           # whisper 7.020 (+0.2 f): 'high' to 7.02, f noise 7.028
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
    segs, _ = model.transcribe(str(f), word_timestamps=True, vad_filter=False, language="en", initial_prompt=text)
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
    # the end of "vet.": the last voiced 10 ms of the narration (-40 dB re. its max); s5.wav's own tail does not count
    vo = np.nonzero(full_db > -40)[0]
    voice_end = LEAD_S + (vo[-1] + 1) * 0.01
    last = words[-1]
    assert last["text"] == LAST_WORD, last
    last["end"] = round(max(last["end"], voice_end), 3)
    vet_end = last["end"]
    total_frames = int(np.ceil((vet_end + SETTLE_S) * FPS))
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
          "voice_end_seconds": round(voice_end, 3), "vet_end_seconds": vet_end, "vet_end_frame": round(vet_end * FPS),
          "sections": sections, "scenes": scenes, "words": words,
          "notes": ("Timings measured from THE CLEAN WAVs (assets/audio/narration/clean/sN.wav: ElevenLabs Bella eleven_v4, take 1 of "
                    "every section; NO baked-in pause (nothing cut); lead/tail trimmed; s4 end click cut; ONE constant gain per section to -21.5 LUFS (s4 TP-capped; no loudnorm); widened gaps 1.2/1.2/1.2/1.45 s inside the files; no time-stretch). "
                    f"Lead-in {LEAD_S} s before s1; sections back to back at their measured durations. "
                    "Words: faster-whisper small.en aligned to the script text (script punctuation, "
                    "punctuation); onsets snapped to the RMS envelope (-40 dB, <= 250 ms); every onset swept (OVERRIDES / "
                    "CONFIRMED, section-relative). Scene splits = anchor-word onset - 2 frames (ALL scenes after sc01). "
                    f"FINISHED-LINE ending: the film runs {SETTLE_S} s past the aligned end of 'vet.' (inside sc12; no loop splice). "
                    "Captions show script text.")}
    for w in words:
        print(f'{w["section"]} {w["text"]:<14} {w["start"]:7.3f} {w["end"]:7.3f}  f{round(w["start"] * FPS):5d}')
    print("heard:", json.dumps(heard, indent=1))
    print("narration", narr, "total", tl["total_seconds"], "frames", total_frames, "voice end", round(voice_end, 3),
          "vet end", vet_end, "exact-match", match)
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
