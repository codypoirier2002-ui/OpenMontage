"""Build the master timeline (sections, scene windows, word timings) from THE CLEAN WAVs.

Usage (from repo root):
    HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1 python3 projects/how-hot-can-it-get/align_narration.py            # write
    HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1 python3 projects/how-hot-can-it-get/align_narration.py --check    # print only
    ... align_narration.py --raw    # print whisper's raw (pre-override) onsets, section-relative (for sweep_onsets.py)

Pattern copied from projects/what-if-earth-stopped-spinning/align_narration.py (video 12, delivered, QA passed).

THE CLEAN WAVs = assets/audio/narration/clean/sN.wav (process_narration.py: s3's baked-in 0.167 s pause between 'held'
and 'a hundred' cut (lesson 29), lead / tail trimmed, loudnorm -16 LUFS, + the script's pause_after s1-s4 0.35/0.4/0.45/0.45 s inside
the files; s5 has NO pause - the 1.5 s settle is added here). These are the ONLY clean WAVs for alignment, OVERRIDES,
the premix and QA A (lesson 17). The raw assets/audio/narration/sN.wav are NOT used from here on.

Layout (FINISHED-LINE ending, no loop splice): LEAD_S of lead-in (frame 0 = the dark forge frame, the X1 ember crackle,
tab idle, no captions), then s1..s5 back to back at their clean durations (the boundary pauses are inside the files),
then a fixed SETTLE_S after the aligned end of "know." (the last voiced 10 ms of s5, -40 dB re. the narration max): the
bed's own C tonic (its last strong attack) lands ~0.15 s later, the ladder holds in its low blue-white glow, the CTA
sits on the caption slab. total_frames = ceil((know_end + SETTLE_S) * 30).

Words: faster-whisper small.en (word timestamps, prompted with the script text) aligned to the SCRIPT text by sequence
matching (script canonical: 'fifty-seven', 'four hundred sixty-five', 'fifteen million', 'forty-eight',
'thirty-two' - whisper writes '57' / '465' / '15 million' / '48' / '32'). Envelope correction: 1. onset snap (voiced-run
onsets, -40 dB, <= 250 ms, one word per run); 2. OVERRIDES / CONFIRMED: the full 109-word sweep (sweep_onsets.py candidates on 5 ms RMS + band envelopes, every disagreement hand-checked); 3./4. word
ends trimmed at internal silences / extended to the end of a phrase-final voiced run.
Scene windows: sc01 starts at frame 0; EVERY other scene starts at its anchor word's onset - 2 frames (the anchor = the
first word of the scene's narration fragment, scene_plan.metadata.narration_by_scene). sc13 ('just an edge to what we
know.') is a NARRATED scene: it runs from 'just' - 2 f to total_frames, and the settle (release of 'know.' -> end) is
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

P = Path("projects/how-hot-can-it-get")
NDIR = P / "assets/audio/narration/clean"     # THE CLEAN WAVs (process_narration.py)
FPS = 30
LEAD_S = 0.50
SETTLE_S = 1.50
N_WORDS = 109
LAST_WORD = "know."
# scene id -> (section, anchor word (normalised), occurrence in that section); scene starts at onset - 2 frames
ANCHORS = {"sc02": ("s1", "so", 1), "sc03": ("s2", "death", 1), "sc04": ("s2", "venus", 1), "sc05": ("s3", "the", 1),
           "sc06": ("s3", "yet", 1), "sc07": ("s4", "the", 1), "sc08": ("s4", "over", 1), "sc09": ("s4", "so", 1),
           "sc10": ("s5", "beyond", 1), "sc11": ("s5", "roughly", 1), "sc12": ("s5", "so", 1), "sc13": ("s5", "just", 1)}
# (section, script token, nth) -> (start or None, end or None) in seconds RELATIVE TO THE SECTION'S clean sN.wav
# OVERRIDES_START
# ---- the FULL 109-word onset sweep (foundation) on THE CLEAN WAVs: sweep_onsets.py candidates + 1 ms-hop band profiles
# (80-500 / 500-2.5k / 2.5-8k Hz, 5.3 ms window), 7-band 10.7 ms profiles (0-400 ... 6-10 kHz) and spectrograms (5 ms
# hop) read for EVERY word; whisper medium.en word starts used as a third opinion on the glides / merged segments.
# Convention (lesson 2): a stop's onset is its BURST; a fricative / nasal / h at its own noise / murmur / breath; a vowel
# after a stop at the end of the stop; merged segments across a word boundary at their midpoint (soft). Bella realises
# th/dh as a dental stop after a closure (onset = the release). Whisper small.en was off by 2-10 f on many words here
# (it repeatedly sat on the previous word's last segment: s1 'absolute' 'how', s3 'in' 'hundred', s4 'we've' 'lead' 'at',
# s5 'that' 'waits' 'the' 'edge' 'to'): every value below is hand-measured; OVERRIDES = whisper's snapped onset off by
# > 0.5 f; the comment gives (measured - whisper) and the cue. Soft (+-1-2 f): s1 'zero.' 'a'#2, s2 'Valley's' 'once'
# 'sits' 'melt', s3 'reaches' 'million.' 'held' 'degrees', s4 'hot' 'into', s5 'with' 'our'.
OVERRIDES: dict[tuple[str, str, int], tuple[float | None, float | None]] = {
    ("s1", "has", 1):              (0.358, None),   # whisper 0.280 (+2.3 f): 'Cold' d closure 0.33-0.35, d release into h breath 0.355-0.45
    ("s1", "a", 1):                (0.582, None),   # whisper 0.540 (+1.3 f): 'has' z 0.53-0.58, schwa voicing 0.582
    ("s1", "floor:", 1):           (0.637, None),   # whisper 0.700 (-1.9 f): schwa to 0.63, f (weak, LF drop) 0.637
    ("s1", "absolute", 1):         (1.565, None),   # whisper 1.020 (+16.3 f): after the 0.41 s beat: vowel 1.565 (whisper sat in 'floor')
    ("s1", "zero.", 1):            (2.135, None),   # whisper 2.020 (+3.4 f): 'absolute' t closure 2.09-2.12, z voice bar 2.13 + noise 2.145 (soft)
    ("s1", "how", 1):              (3.655, None),   # whisper 3.440 (+6.4 f): 'So' o 3.31-3.64 (long), h breath 3.655 (whisper 3.44 sat in 'o')
    ("s1", "hot", 1):              (3.895, None),   # whisper 3.820 (+2.3 f): 'how' ow to 3.88, h noise 3.895
    ("s1", "can", 1):              (4.160, None),   # whisper 4.100 (+1.8 f): 'hot' t release 4.12, k closure 4.135-4.155, k BURST 4.160
    ("s1", "get?", 1):             (4.425, None),   # whisper 4.400 (+0.7 f): 'it' t closure 4.39-4.41, g BURST 4.425
    ("s1", "there", 1):            (5.278, None),   # whisper 5.240 (+1.1 f): 'Is' z 5.19-5.24, dental closure 5.25-5.27, dh release 5.278
    ("s1", "ceiling?", 1):         (5.455, None),   # whisper 5.560 (-3.1 f): s noise 5.455
    ("s2", "Death", 1):            (0.087, None),   # whisper 0.030 (+1.7 f): d voice bar 0.035-0.07, d BURST 0.087
    ("s2", "Valley's", 1):         (0.285, None),   # whisper 0.260 (+0.7 f): 'Death' th 0.23-0.29 -> v (weaker, voiced) merged: 0.285 (soft)
    ("s2", "air", 1):              (0.785, None),   # whisper 0.740 (+1.4 f): 'Valley's' z to 0.70, glottal stop 0.75-0.78, vowel 0.785
    ("s2", "once", 1):             (1.105, None),   # whisper 0.980 (+3.8 f): 'air' r to 1.10, w (MID drop, HF -74) 1.105 (soft)
    ("s2", "hit", 1):              (1.375, None),   # whisper 1.300 (+2.2 f): 'once' s 1.33-1.37 -> h breath (MID rise) 1.375
    ("s2", "fifty-seven", 1):      (1.900, None),   # whisper 1.860 (+1.2 f): 'nearly' ee to 1.89, f noise (LF drop) 1.900
    ("s2", "degrees.", 1):         (2.925, None),   # whisper 2.840 (+2.5 f): 'seven' n to 2.91, d closure 2.915-2.92, d BURST 2.925
    ("s2", "sits", 1):             (4.500, None),   # whisper 4.400 (+3.0 f): 'Venus' s + 'sits' s merged 4.43-4.57: midpoint 4.500 (soft)
    ("s2", "about", 1):            (4.745, None),   # whisper 4.660 (+2.5 f): 'sits' t burst 4.69 + s 4.70-4.74, vowel 4.745
    ("s2", "sixty-five,", 1):      (5.678, None),   # whisper 5.620 (+1.7 f): 'hundred' d to 5.67, s noise 5.678
    ("s2", "enough", 1):           (7.220, None),   # whisper 7.200 (+0.6 f): 'hot' t flapped 7.21-7.22, vowel 7.220
    ("s2", "to", 1):               (7.540, None),   # whisper 7.420 (+3.6 f): 'enough' f 7.445-7.495, t closure 7.50-7.535, t BURST 7.540 (whisper 7.42 sat on the f)
    ("s2", "melt", 1):             (7.608, None),   # whisper 7.640 (-1.0 f): 'to' t aspiration 7.55-7.58, schwa 7.59-7.60, m (MID dip) 7.608 (soft)
    ("s2", "lead.", 1):            (8.005, None),   # whisper 7.940 (+2.0 f): 'melt' t closure 7.91-8.00, l 8.005
    ("s3", "Sun's", 1):            (0.128, None),   # whisper 0.180 (-1.6 f): 'The' schwa to 0.12, s noise 0.128
    ("s3", "core", 1):             (0.598, None),   # whisper 0.580 (+0.5 f): 'Sun's' z 0.45-0.53, k closure 0.54-0.59, k BURST 0.598
    ("s3", "reaches", 1):          (0.950, None),   # whisper 0.880 (+2.1 f): 'core' r + 'reaches' r merged 0.85-1.05 (ee rises from 1.05): midpoint 0.950 (soft)
    ("s3", "about", 1):            (1.355, None),   # whisper 1.280 (+2.2 f): 'reaches' z 1.29-1.35, vowel 1.355
    ("s3", "fifteen", 1):          (1.615, None),   # whisper 1.580 (+1.0 f): 'about' t closure 1.57-1.60, f noise 1.615
    ("s3", "million.", 1):         (2.355, None),   # whisper 2.200 (+4.6 f): 'fifteen' n + 'million' m merged 2.25-2.43: m (MID drop) 2.355 (soft)
    ("s3", "a", 1):                (3.648, None),   # whisper 3.580 (+2.0 f): 'Yet' t closure 3.60-3.64, vowel 3.648
    ("s3", "fusion", 1):           (3.705, None),   # whisper 3.800 (-2.8 f): 'a' to 3.69, f noise 3.705 (broadband 3.5-10k from 3.70; whisper 3.80 sat in the f)
    ("s3", "reactor", 1):          (4.330, None),   # whisper 4.180 (+4.5 f): 'fusion' n 4.22-4.32, r 4.330 (ee from 4.36)
    ("s3", "in", 1):               (4.775, None),   # whisper 4.660 (+3.5 f): 'reactor' t burst 4.66 + or 4.69-4.75, dip 4.76-4.77, i (F2 rise) 4.775 (whisper 4.66 sat on 'tor')
    ("s3", "Korea", 1):            (4.925, None),   # whisper 4.900 (+0.7 f): 'in' n 4.80-4.90, k closure 4.91-4.92, k BURST 4.925 + aspiration to 5.00
    ("s3", "held", 1):             (5.285, None),   # whisper 5.340 (-1.6 f): 'Korea' ea to 5.27, voiced h (4-8 band jump) 5.285 (soft)
    ("s3", "a", 2):                (5.520, None),   # whisper 5.660 (-4.2 f): the lesson-29 splice 5.495; vowel 5.520
    ("s3", "hundred", 1):          (5.690, None),   # whisper 5.860 (-5.1 f): 'a' to 5.63, glottal release 5.69 into a long breathy h 5.70-6.01 (whisper 5.86 sat in the h)
    ("s3", "for", 1):              (7.385, None),   # whisper 7.260 (+3.8 f): 'degrees' z to 7.38, f (LF drop) 7.385
    ("s3", "seconds.", 1):         (8.378, None),   # whisper 8.360 (+0.5 f): after the beat: s noise 8.378
    ("s4", "hottest", 1):          (0.180, None),   # whisper 0.200 (-0.6 f): 'The' schwa to 0.17, h breath (LF drop) 0.180
    ("s4", "we've", 1):            (0.850, None),   # whisper 0.640 (+6.3 f): 'hottest' s 0.66-0.74 + t release 0.77, closure 0.79-0.84, w voicing 0.850 (whisper 0.64 sat on the s)
    ("s4", "made:", 1):            (1.437, None),   # whisper 1.460 (-0.7 f): 'ever' er to 1.43, m (MID drop) 1.437
    ("s4", "lead", 1):             (2.505, None),   # whisper 2.760 (-7.6 f): after the colon beat: l voicing 2.505 (whisper 2.76 put 'lead' at 'ead')
    ("s4", "smashed", 1):          (3.350, None),   # whisper 3.300 (+1.5 f): 'atoms' z to 3.34, s noise 3.350
    ("s4", "at", 1):               (4.268, None),   # whisper 4.040 (+6.8 f): 'smashed' sh 4.05-4.20, t closure 4.21-4.24, t burst 4.25, vowel 4.268 (whisper 4.04 sat on the sh)
    ("s4", "CERN,", 1):            (4.405, None),   # whisper 4.440 (-1.1 f): 'at' t closure 4.34-4.39, release into s 4.405
    ("s4", "five", 1):             (5.680, None),   # whisper 5.660 (+0.6 f): 'over' er to 5.67, f noise (LF drop) 5.680
    ("s4", "hot", 1):              (8.440, None),   # whisper 8.540 (-3.0 f): 'So' s 8.13-8.37 + o 8.38-8.42, breathy h (0-400 Hz dip) 8.440 (soft; whisper 8.54 sat on the vowel)
    ("s4", "melt", 1):             (9.770, None),   # whisper 9.740 (+0.9 f): 'protons' z 9.73-9.76, m 9.770
    ("s4", "into", 1):             (10.180, None),   # whisper 10.100 (+2.4 f): 'melt' t closure 10.12-10.16, release into i 10.180 (soft)
    ("s4", "a", 1):                (10.440, None),   # whisper 10.400 (+1.2 f): 'into' t asp 10.33-10.37 + oo 10.38-10.43, schwa (MID rise) 10.440
    ("s4", "soup", 1):             (10.505, None),   # whisper 10.560 (-1.6 f): 'a' to 10.50, s noise 10.505
    ("s4", "of", 1):               (10.928, None),   # whisper 10.860 (+2.0 f): 'soup' p closure 10.86-10.91, p release 10.92, vowel 10.928
    ("s5", "that", 1):             (0.418, None),   # whisper 0.280 (+4.1 f): 'Beyond' n 0.30-0.40, d/dh closure 0.40-0.415, dental release 0.418 (whisper 0.28 sat in 'yond')
    ("s5", "waits", 1):            (0.865, None),   # whisper 0.700 (+5.0 f): 'that' t release 0.74 + aspiration to 0.82, gap, w voicing 0.865
    ("s5", "the", 1):              (1.188, None),   # whisper 1.020 (+5.0 f): 'waits' s 1.04-1.11, dental closure 1.12-1.18, dh release 1.188
    ("s5", "a", 1):                (3.020, None),   # whisper 2.900 (+3.6 f): 'roughly' ly to 3.00, dip 3.01, schwa 3.020 (whisper 2.90 sat in 'ly')
    ("s5", "our", 1):              (5.320, None),   # whisper 5.300 (+0.6 f): 'where' -> 'our' vowel merged: formant change 5.320 (soft)
    ("s5", "breaks.", 1):          (5.845, None),   # whisper 5.800 (+1.3 f): 'physics' s to 5.83, b BURST 5.845
    ("s5", "heat", 1):             (7.235, None),   # whisper 7.180 (+1.7 f): 'So' o to 7.23, h aspiration (F2 rise) 7.235
    ("s5", "may", 1):              (7.568, None),   # whisper 7.520 (+1.4 f): 'heat' t closure 7.52-7.56, m 7.568
    ("s5", "an", 1):               (9.258, None),   # whisper 9.200 (+1.7 f): 'just' s 9.20-9.24 + t closure, vowel 9.258
    ("s5", "edge", 1):             (9.468, None),   # whisper 9.400 (+2.0 f): 'an' n to 9.41, glottal stop 9.41-9.46, vowel 9.468 (whisper 9.40 sat on the n)
    ("s5", "to", 1):               (9.868, None),   # whisper 9.720 (+4.4 f): 'edge' dzh release 9.72 + frication 9.74-9.82, t closure 9.84-9.86, t BURST 9.868 (whisper 9.72 sat on the dzh)
    ("s5", "we", 1):               (10.140, None),   # whisper 10.100 (+1.2 f): 'what' t closure 10.08-10.12, t release 10.13, w 10.140
}
# the words whose snapped onset the sweep CONFIRMED (within 0.5 f; measured onset recorded, so the final check covers all 109)
CONFIRMED: dict[tuple[str, str, int], float] = {
    ("s1", "Cold", 1):             0.030,           # whisper 0.030 (+0.0 f): after the lead: k burst
    ("s1", "So", 1):               3.143,           # whisper 3.150 (-0.2 f): after the beat: s noise 3.143
    ("s1", "it", 1):               4.280,           # whisper 4.280 (+0.0 f): 'can' n 4.25-4.27, i (2.5-8k rise) 4.280
    ("s1", "Is", 1):               5.133,           # whisper 5.130 (+0.1 f): after the beat: vowel 5.133
    ("s1", "a", 2):                5.380,           # whisper 5.380 (+0.0 f): 'there' r -> schwa merged (MID rise): 5.380 (soft)
    ("s2", "nearly", 1):           1.572,           # whisper 1.560 (+0.4 f): 'hit' t closure 1.52-1.57, n murmur 1.572
    ("s2", "Venus", 1):            4.025,           # whisper 4.030 (-0.1 f): after the beat: v voicing 4.025
    ("s2", "four", 1):             4.975,           # whisper 4.960 (+0.4 f): 'about' t release 4.97, f noise 4.975
    ("s2", "hundred", 1):          5.335,           # whisper 5.320 (+0.4 f): 'four' vowel to 5.33, h breath 5.335
    ("s2", "hot", 1):              6.968,           # whisper 6.970 (-0.1 f): after the beat: h breath 6.968
    ("s3", "The", 1):              0.035,           # whisper 0.030 (+0.2 f): dh voicing out of the head 0.035
    ("s3", "Yet", 1):              3.445,           # whisper 3.440 (+0.1 f): after the beat: y voicing 3.445
    ("s3", "million", 1):          6.310,           # whisper 6.300 (+0.3 f): 'hundred' d to 6.30, m (HF drop) 6.310
    ("s3", "degrees", 1):          6.845,           # whisper 6.840 (+0.1 f): 'million' n to 6.84, d (unreleased; HF drop) 6.845 (soft)
    ("s3", "forty-eight", 1):      7.615,           # whisper 7.620 (-0.1 f): 'for' r to 7.61, f noise 7.615
    ("s4", "The", 1):              0.030,           # whisper 0.030 (+0.0 f): dh voicing out of the head 0.030
    ("s4", "ever", 1):             1.200,           # whisper 1.200 (+0.0 f): after the beat: vowel 1.200
    ("s4", "atoms", 1):            2.870,           # whisper 2.860 (+0.3 f): 'lead' d 2.84-2.86, vowel 2.870
    ("s4", "over", 1):             5.445,           # whisper 5.450 (-0.1 f): after the beat: vowel 5.445
    ("s4", "trillion", 1):         6.405,           # whisper 6.400 (+0.1 f): after the beat: t closure 6.31-6.40, t BURST 6.405
    ("s4", "degrees.", 1):         6.965,           # whisper 6.960 (+0.1 f): 'trillion' n 6.93-6.96, d release 6.965
    ("s4", "So", 1):               8.125,           # whisper 8.130 (-0.2 f): after the beat: s noise 8.125
    ("s4", "that", 1):             8.978,           # whisper 8.970 (+0.2 f): 'hot' t closure 8.89-8.97, dh release 8.978
    ("s4", "protons", 1):          9.168,           # whisper 9.160 (+0.2 f): 'that' t closure 9.06-9.15, p BURST 9.168
    ("s4", "quarks.", 1):          11.125,           # whisper 11.130 (-0.2 f): 'of' v to 11.04, k closure 11.05-11.12, k BURST 11.125
    ("s5", "Beyond", 1):           0.035,           # whisper 0.030 (+0.2 f): b BURST out of the head 0.035
    ("s5", "Planck", 1):           1.300,           # whisper 1.300 (+0.0 f): 'the' schwa to 1.22, p closure 1.22-1.29, p BURST 1.300
    ("s5", "temperature,", 1):     1.665,           # whisper 1.660 (+0.2 f): 'Planck' k + t one closure 1.63-1.66, t BURST 1.665
    ("s5", "roughly", 1):          2.638,           # whisper 2.640 (-0.1 f): after the beat: r voicing 2.638
    ("s5", "one", 1):              3.125,           # whisper 3.120 (+0.1 f): 'a' to 3.12, w (F2 dip) 3.125
    ("s5", "with", 1):             3.380,           # whisper 3.380 (+0.0 f): 'one' n to 3.37, w 3.380 (soft)
    ("s5", "thirty-two", 1):       3.675,           # whisper 3.680 (-0.2 f): 'with' th + 'thirty' th: voiceless th noise 3.675
    ("s5", "zeros,", 1):           4.300,           # whisper 4.300 (+0.0 f): 'two' oo to 4.29, z noise 4.300
    ("s5", "where", 1):            5.200,           # whisper 5.200 (+0.0 f): after the beat: w voicing 5.200
    ("s5", "physics", 1):          5.475,           # whisper 5.480 (-0.2 f): 'our' r to 5.47, f noise 5.475
    ("s5", "So", 1):               6.925,           # whisper 6.930 (-0.1 f): after the beat: s noise 6.925
    ("s5", "have", 1):             7.720,           # whisper 7.720 (+0.0 f): 'may' ay to 7.71, breathy h 7.720
    ("s5", "no", 1):               7.972,           # whisper 7.960 (+0.4 f): 'have' v 7.94-7.97, n 7.972
    ("s5", "ceiling,", 1):         8.140,           # whisper 8.140 (+0.0 f): 'no' o to 8.13, s noise 8.140
    ("s5", "just", 1):             9.045,           # whisper 9.050 (-0.2 f): after the beat: dzh BURST 9.045
    ("s5", "what", 1):             9.945,           # whisper 9.960 (-0.5 f): 'to' oo to 9.94, w (HF -58 -> -69) 9.945
    ("s5", "know.", 1):            10.245,           # whisper 10.240 (+0.1 f): 'we' ee to 10.24, n (2-6 kHz drop, LF steady) 10.245
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
    args = ap.parse_args()
    from faster_whisper import WhisperModel

    script = json.loads((P / "artifacts/script.json").read_text())
    plan = json.loads((P / "artifacts/scene_plan.json").read_text())
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
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
        assert meas is not None, ("word not swept", key)
        err = round(w["start"] * FPS) - (secstart[w["section"]] + meas) * FPS
        sweep.append({"word": f"{key[0]}:{key[1]}#{key[2]}", "measured_s_section": meas, "caption_frame": round(w["start"] * FPS),
                      "err_frames": round(err, 2), "source": "override" if key in OVERRIDES else "confirmed"})
        assert abs(err) <= MAX_ERR_F, sweep[-1]
    assert len(sweep) == sum(len(s["text"].split()) for s in script["sections"]) == N_WORDS
    narr = round(t0 - LEAD_S, 3)
    # the end of "know.": the last voiced 10 ms of the narration (-40 dB re. its max); s5.wav's own tail does not count
    vo = np.nonzero(full_db > -40)[0]
    voice_end = LEAD_S + (vo[-1] + 1) * 0.01
    last = words[-1]
    assert last["text"] == LAST_WORD, last
    last["end"] = round(max(last["end"], voice_end), 3)
    know_end = last["end"]
    total_frames = int(np.ceil((know_end + SETTLE_S) * FPS))
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
            s_, word, nth = ANCHORS[sc["id"]]
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
          "voice_end_seconds": round(voice_end, 3), "know_end_seconds": know_end, "know_end_frame": round(know_end * FPS),
          "sections": sections, "scenes": scenes, "words": words,
          "notes": ("Timings measured from THE CLEAN WAVs (assets/audio/narration/clean/sN.wav: ElevenLabs Bella eleven_v4, take 1 of "
                    "every section; s3 baked-in pause cut 0.167 s (lesson 29); lead/tail trimmed; loudnorm -16; script pauses inside the files; no time-stretch). "
                    f"Lead-in {LEAD_S} s before s1; sections back to back at their measured durations. "
                    "Words: faster-whisper small.en aligned to the script text (script canonical: number words, script "
                    "punctuation); onsets snapped to the RMS envelope (-40 dB, <= 250 ms); every onset swept (OVERRIDES / "
                    "CONFIRMED, section-relative). Scene splits = anchor-word onset - 2 frames (ALL scenes after sc01). "
                    f"FINISHED-LINE ending: the film runs {SETTLE_S} s past the aligned end of 'know.' (inside sc13; no loop splice). "
                    "Captions show script text.")}
    for w in words:
        print(f'{w["section"]} {w["text"]:<14} {w["start"]:7.3f} {w["end"]:7.3f}  f{round(w["start"] * FPS):5d}')
    print("heard:", json.dumps(heard, indent=1))
    print("narration", narr, "total", tl["total_seconds"], "frames", total_frames, "voice end", round(voice_end, 3),
          "know end", know_end, "exact-match", match)
    for s in scenes:
        print(s)
    if args.check:
        return
    (P / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1))
    (P / "artifacts/alignment_report.json").write_text(json.dumps({"exact_match_ratio": match, "whisper_heard": heard,
                                                                   "whisper_raw_section_rel": raws, "sweep": sweep,
                                                                   "sweep_max_abs_err_frames": max(abs(x["err_frames"]) for x in sweep),
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
                r["measured"] = OVERRIDES[key][0] if key in OVERRIDES else CONFIRMED[key]
                r["source"] = "override" if key in OVERRIDES else "confirmed"
                r["measured_minus_whisper_f"] = round((r["measured"] - r["whisper"]) * FPS, 2)
                r["measured_minus_candidate_f"] = round((r["measured"] - r["cand"]) * FPS, 2)
        swp.write_text(json.dumps(cand, indent=1))
    print("wrote artifacts/timeline.json")


if __name__ == "__main__":
    sys.exit(main())
