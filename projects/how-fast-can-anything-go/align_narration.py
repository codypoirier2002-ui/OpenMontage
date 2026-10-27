"""Build the master timeline (sections, scene windows, word timings) from THE CLEAN WAVs.

Usage (from repo root):
    HF_HUB_OFFLINE=1 python3 projects/how-fast-can-anything-go/align_narration.py            # write
    HF_HUB_OFFLINE=1 python3 projects/how-fast-can-anything-go/align_narration.py --check    # print only
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

P = Path("projects/how-fast-can-anything-go")
NDIR = P / "assets/audio/narration/clean"     # THE CLEAN WAVs (process_narration.py)
FPS = 30
LEAD_S = 0.50
SETTLE_S = 1.50
N_WORDS = 106
LAST_WORD = "way."


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
    ("s1", "at", 1):          (0.464, None),   # whisper 0.420 (+1.3 f): 'walk' k closure 0.43-0.45, k BURST 0.456 (belongs to 'walk'), vowel 0.464
    ("s1", "about", 1):       (0.571, None),   # whisper 0.600 (-0.9 f): 'at' t (a weak closure 0.551-0.566), release into the schwa 0.571; the b closure 0.62-0.66 is INSIDE 'about'
    ("s1", "five", 1):        (0.908, None),   # whisper 0.840 (+2.0 f): 'about' t closure + silence 0.89-0.905, f noise 0.908 (a LONG f: voicing only from 1.115; 'five' is the stressed word)
    ("s1", "kilometres", 1):  (1.403, None),   # whisper 1.320 (+2.5 f): 'five' v devoices 1.315-1.36, closure 1.365-1.395, k BURST 1.403 (whisper 1.32 sat on the tail of 'five')
    ("s1", "hour.", 1):       (1.998, None),   # whisper 2.040 (-1.3 f): 'an' n murmur 1.956-1.993 (HF 0), vowel onset 1.998
    ("s1", "sprints", 1):     (3.464, None),   # whisper 3.420 (+1.3 f): 'cheetah' ah to 3.46, s noise 3.464 (HF 5-6, MID 2)
    ("s1", "hundred.", 1):    (4.228, None),   # whisper 4.280 (-1.6 f): 'a' schwa to 4.22, h breath 4.228 (LF falls, HF 3-4; vowel 4.386)
    ("s1", "diving", 1):      (5.346, None),   # whisper 5.320 (+0.8 f): 'A' ay, d closure 5.331-5.341, d BURST 5.346
    ("s1", "falcon", 1):      (5.716, None),   # whisper 5.680 (+1.1 f): 'diving' ng murmur 5.676-5.711 (HF 0), f noise 5.716
    ("s1", "hits", 1):        (6.024, None),   # whisper 6.120 (-2.9 f): 'falcon' k burst 6.011 + reduced 'on', h breath 6.021-6.05 (HF 2-5, LF low), vowel 6.056
    ("s1", "nearly", 1):      (6.484, None),   # whisper 6.360 (+3.7 f): 'hits' t closure 6.366-6.376 + s 6.381-6.476 (LF 0), n murmur 6.484 (whisper 6.36 sat on the t)
    ("s1", "four", 1):        (6.806, None),   # whisper 6.740 (+2.0 f): 'nearly' y to 6.80, f noise 6.806 (HF 4, LF falling; vowel ~6.96)
    ("s1", "hundred.", 2):    (7.258, None),   # whisper 7.180 (+2.3 f): 'four' r to 7.25, h breath 7.258 (LF dip 7.261-7.321, HF 4-5), vowel 7.33
    ("s2", "them", 1):        (0.958, None),   # whisper 0.940 (+0.5 f): 'outruns' z 0.926-0.956 (HF 5-6), dh 0.958 (HF falls to 4)
    ("s2", "at", 1):          (1.590, None),   # whisper 1.520 (+2.1 f): 'all' dark l 1.546-1.586 (MID 5), vowel 1.591 (MID up)
    ("s2", "over", 1):        (1.719, None),   # whisper 1.700 (+0.6 f): 'at' t closure 1.686, burst 1.696 (belongs to 'at'), vowel 1.719
    ("s2", "twelve", 1):      (2.006, None),   # whisper 1.960 (+1.4 f): 'over' r, t closure 1.936-1.996 (HF 0), t BURST 2.006
    ("s2", "still,", 1):      (3.936, None),   # whisper 4.040 (-3.1 f): 'sitting' ng to 3.93, s noise 3.936 (LF 2-3, HF 5-6), t + vowel 3.986 (whisper 4.04 sat in the vowel)
    ("s2", "over", 2):        (5.364, None),   # whisper 5.320 (+1.3 f): 'doing' ng murmur 5.316-5.34, glottal re-attack 5.361-5.366 (tot dip then up)
    ("s2", "a", 1):           (5.543, None),   # whisper 5.600 (-1.7 f): 'over' r (MID 4) -> 'a': MID rises 4->5->7 at 5.535-5.55 (the stressed 'a' runs to 5.72)
    ("s2", "hundred", 1):     (5.724, None),   # whisper 5.760 (-1.1 f): 'a' to 5.72, h breath 5.724 (LF 2-4, HF 4-5, a long breathy h; vowel 5.891)
    ("s2", "Earth", 1):       (7.686, None),   # whisper 7.560 (+3.8 f): 'riding' ing 7.49-7.65, glottal closure 7.651-7.681 (tot 4-1), vowel 7.686 (whisper 7.56 sat in 'ing')
    ("s2", "around", 1):      (7.948, None),   # whisper 7.860 (+2.6 f): 'Earth' th 7.866-7.91 (HF 4-6), gap 7.92-7.94, weak schwa 7.946 (MID 2->4)
    ("s2", "the", 1):         (8.266, None),   # whisper 8.200 (+2.0 f): 'around' n murmur 8.196-8.26 (HF 0, MID 3), dh/vowel 8.266 (MID 4-5)
    ("s2", "Sun.", 1):        (8.314, None),   # whisper 8.380 (-2.0 f): 'the' vowel to 8.31, s noise 8.316 (HF 5-6, LF falls)
    ("s3", "fastest", 1):     (0.053, None),   # whisper 0.140 (-2.6 f): 'The' = dh + a swallowed schwa (0.03-0.05); f noise 0.053 (HF 4), the ae vowel 0.065 ('th'fastest', read fast)
    ("s3", "thing", 1):       (0.606, None),   # whisper 0.660 (-1.6 f): 'fastest' s 0.54-0.57, t closure 0.581-0.596, burst 0.601 fused into the th noise 0.606 (LF 1-3, HF 5-7), vowel 0.631
    ("s3", "built,", 1):      (1.688, None),   # whisper 1.560 (+3.8 f): 'ever' er to 1.64, b closure 1.641-1.681, b BURST 1.688 (whisper 1.56 sat in 'ever')
    ("s3", "Parker", 1):      (2.428, None),   # whisper 2.400 (+0.8 f): 'the' decays to 2.42, p closure, p BURST 2.428
    ("s3", "Solar", 1):       (2.791, None),   # whisper 2.720 (+2.1 f): 'Parker' k burst 2.661, aspiration, 'er' 2.706-2.79, s noise 2.791 (HF 5-6, LF falls; whisper 2.72 sat in 'er')
    ("s3", "nearly", 1):      (4.264, None),   # whisper 4.160 (+3.1 f): 'reached' ch 4.10-4.26 (LF 0, HF 5-7), n murmur 4.264 (LF up, HF 0; whisper 4.16 sat in the ch)
    ("s3", "seven", 1):       (4.616, None),   # whisper 4.580 (+1.1 f): 'nearly' ly to 4.61, s noise 4.616 (HF 5-6, LF falls; a long s, vowel 4.846)
    ("s3", "toward", 1):      (7.193, None),   # whisper 7.080 (+3.4 f): 'falling' ng to 7.17, t closure 7.176-7.19, t BURST 7.193 (HF 3->7; whisper 7.08 sat in 'ing')
    ("s3", "the", 2):         (7.466, None),   # whisper 7.360 (+3.2 f): 'toward' ard vowel 7.296-7.42, d closure 7.42-7.46, release/dh 7.466 (whisper 7.36 sat in the vowel)
    ("s3", "Sun.", 1):        (7.541, None),   # whisper 7.620 (-2.4 f): 'the' vowel 7.47-7.54, s noise 7.541 (HF 5-6, LF 5->0)
    ("s4", "over", 1):        (0.834, None),   # whisper 0.700 (+4.0 f): 'does' z 0.69-0.75, a voiced blip 0.756-0.78, glottal silence 0.80-0.83, vowel re-attack 0.834 (whisper 0.70 sat in the z)
    ("s4", "a", 1):           (1.121, None),   # whisper 1.100 (+0.6 f): 'over' er (MID 4-5), MID dip 1.111-1.116, 'a' 1.121 (MID 5-6), b closure 1.141
    ("s4", "nothing", 1):     (2.796, None),   # whisper 2.820 (-0.7 f): 'And' nd + 'nothing' n merged nasal 2.776-2.806: midpoint / HF->0 point 2.796 (soft)
    ("s4", "mass", 1):        (3.484, None),   # whisper 3.460 (+0.7 f): 'with' dh 3.40-3.47, dip 3.471-3.481, m murmur 3.484 (LF 5->7, HF 0, MID 0-1)
    ("s4", "can", 1):         (3.978, None),   # whisper 3.800 (+5.3 f): 'mass' s 3.801-3.955 (HF 5-6, LF 0), k release/aspiration 3.96-3.98, vowel 3.986 (whisper 3.80 sat on the s)
    ("s4", "catch", 1):       (4.111, None),   # whisper 4.060 (+1.5 f): 'can' n 4.045-4.09 (MID 0-1), k closure 4.091-4.106 (tot -48..-54), k BURST 4.111 (HF 3, MID 5), long aspiration, vowel 4.221
    ("s4", "it:", 1):         (4.413, None),   # whisper 4.320 (+2.8 f): 'catch' sh 4.316-4.39 (HF 5-6), vowel 4.413 (LF 4->6)
    ("s4", "the", 1):         (5.108, None),   # whisper 5.000 (+3.2 f): after the pause: dh voicing 5.108 (whisper 5.00 sat in the silence)
    ("s4", "closer", 1):      (5.205, None),   # whisper 5.110 (+2.8 f): 'the' decays 5.15-5.19, k closure 5.19-5.20, k BURST 5.205 (HF 5, MID 6), l, vowel 5.275
    ("s4", "you", 1):         (5.532, None),   # whisper 5.400 (+4.0 f): 'closer' s 5.44-5.49, er 5.495-5.525 (MID 5-6), y glide 5.530 (MID falls 6->4->2 into the uu; whisper 5.40 sat on the s)
    ("s4", "get,", 1):        (5.724, None),   # whisper 5.680 (+1.3 f): 'you' uu, g closure 5.711-5.721, g BURST 5.724-5.726 (HF 5, MID 6)
    ("s4", "more", 1):        (6.426, None),   # whisper 6.360 (+2.0 f): 'the' schwa 6.30-6.42 (MID 7->5), m murmur 6.426 (HF 0-1, MID dip)
    ("s4", "energy", 1):      (6.668, None),   # whisper 6.580 (+2.6 f): 'more' or decays 6.61-6.63, glottal closure 6.635-6.660 (silence), vowel re-attack 6.668 (whisper 6.58 sat in 'more')
    ("s4", "costs,", 1):      (7.586, None),   # whisper 7.700 (-3.4 f): 'step' p unreleased into the k closure 7.5-7.58, k BURST 7.586 (HF 6), vowel 7.601 (whisper 7.70 sat in the vowel)
    ("s4", "end.", 1):        (8.893, None),   # whisper 8.920 (-0.8 f): 'without' ou to 8.886 (tot dip), flap/glottal, 'e' from 8.891 (tot up, MID 4-5), n murmur 8.941
    ("s5", "Hadron", 1):      (0.536, None),   # whisper 0.480 (+1.7 f): 'Large' dzh closure 0.46-0.48, release 0.481 + zh noise (HF 6-7) to 0.53, h breath 0.536 (HF 5->4, MID 5-6), vowel 0.610
    ("s5", "Collider", 1):    (1.011, None),   # whisper 0.960 (+1.5 f): 'Hadron' n murmur 0.936-0.996 (HF 0), k closure 0.996-1.006, k BURST 1.011 (HF 4), weak 'ol', vowel 1.096
    ("s5", "to", 1):          (2.669, None),   # whisper 2.560 (+3.3 f): 'protons' s 2.566-2.655 (HF 4-5), closure 2.655-2.665, t BURST 2.669 (HF 4; whisper 2.56 sat on the s)
    ("s5", "within", 1):      (2.713, None),   # whisper 2.760 (-1.4 f): 'to' aspiration 2.675-2.70 (HF 7), w: LF 4->6->7 at 2.713-2.725, HF falls (whisper 2.76 sat in the vowel)
    ("s5", "a", 1):           (3.036, None),   # whisper 3.000 (+1.1 f): 'within' n murmur 2.986-3.031 (MID 2, HF 0-2), vowel 3.036 (MID 3->4)
    ("s5", "hair", 1):        (3.148, None),   # whisper 3.200 (-1.6 f): 'a' to 3.14, h breath 3.148 (tot 7->5->4, LF 6->1: a LONG breathy h to 3.40; 'air' 3.406-3.59)
    ("s5", "of", 1):          (3.690, None),   # whisper 3.600 (+2.7 f): 'hair' r murmur 3.60-3.68 (HF 0), creaky 'o' 3.681-3.746 then modal 3.751-3.85, f 3.856-3.906 (LF 0, HF 3): onset at the r->o transition 3.690 (soft, +-2 f)
    ("s5", "light", 1):       (3.911, None),   # whisper 3.880 (+0.9 f): 'of' f 3.856-3.906 (LF 0-1), l 3.911 (LF 3-4 rising, MID 0-2), diphthong 3.931-4.09, t closure 4.09-4.16
    ("s5", "never", 1):       (6.478, None),   # whisper 6.440 (+1.1 f): 'But' t closure 6.441-6.471 (silence), nasal release: n murmur 6.478 (LF 2->3->6, HF 0)
    ("s5", "all", 1):         (6.812, None),   # whisper 6.780 (+1.0 f): 'never' v 6.75-6.80 (tot -36..-42, LF 1-2), glottal re-attack 6.811-6.816 (tot 4->7, MID 2->5)
    ("s5", "the", 1):         (7.131, None),   # whisper 7.100 (+0.9 f): 'all' l to 7.10, dh constriction 7.106-7.126 (tot -48..-42, MID 0), frication 7.131, vowel 7.156
    ("s5", "way.", 1):        (7.196, None),   # whisper 7.240 (-1.3 f): 'the' vowel 7.156-7.19 (MID 3-4), w: MID falls to <= 2 at 7.196 (HF 0), the 'ay' diphthong 7.271
}
# the words whose snapped onset the sweep CONFIRMED (within 0.5 f; measured onset recorded, so the final check covers all 106)
CONFIRMED: dict[tuple[str, str, int], float] = {
    ("s1", "You", 1):         0.033,           # whisper 0.030 (+0.1 f): voicing out of the lead (j glide)
    ("s1", "walk", 1):        0.214,           # whisper 0.220 (-0.2 f): 'You' uu -> w: MID (F2) falls below -48 dB at 0.211 (the glide's own transition)
    ("s1", "an", 1):          1.740,           # whisper 1.740 (+0.0 f): 'kilometres' z 1.69-1.72, MID dip 1.725-1.735, vowel 1.740
    ("s1", "A", 1):           2.858,           # whisper 2.850 (+0.2 f): after the pause: voicing 2.856
    ("s1", "cheetah", 1):     2.990,           # whisper 3.000 (-0.3 f): 'A' decays to 2.98, ch affricate burst 2.991 (HF jump)
    ("s1", "at", 2):          3.888,           # whisper 3.880 (+0.2 f): 'sprints' ts 3.81-3.88 (LF 0), vowel 3.888
    ("s1", "about", 2):       3.958,           # whisper 3.960 (-0.1 f): 'at' t (weak, 3.936-3.956), schwa 3.958
    ("s1", "a", 1):           4.156,           # whisper 4.160 (-0.1 f): 'about' t closure 4.146-4.151, release 4.156
    ("s1", "A", 2):           5.214,           # whisper 5.210 (+0.1 f): after the pause: voicing 5.214
    ("s2", "Sound", 1):       0.033,           # whisper 0.030 (+0.1 f): s noise out of the lead
    ("s2", "outruns", 1):     0.449,           # whisper 0.440 (+0.3 f): 'Sound' n murmur 0.42-0.446 (HF 0), d release + vowel 0.451
    ("s2", "all", 1):         1.279,           # whisper 1.270 (+0.3 f): after the pause: glottal onset 1.279
    ("s2", "hundred.", 1):    2.184,           # whisper 2.180 (+0.1 f): 'twelve' v, a 65 ms gap 2.111-2.176, voicing 2.184 (the h is absent)
    ("s2", "But", 1):         3.601,           # whisper 3.590 (+0.3 f): after the pause: b voice bar 3.586-3.596, b BURST 3.601
    ("s2", "sitting", 1):     3.726,           # whisper 3.720 (+0.2 f): 'But' t burst fused into the s: s noise 3.726 (LF 0 to 3.88, vowel 3.881)
    ("s2", "you're", 1):      4.964,           # whisper 4.960 (+0.1 f): after the pause: voicing 4.964
    ("s2", "doing", 1):       5.124,           # whisper 5.120 (+0.1 f): 'you're' r, d closure 5.10-5.12 (MID 0), d BURST 5.124
    ("s2", "thousand,", 1):   6.372,           # whisper 6.370 (+0.1 f): after the pause: th noise 6.372
    ("s2", "riding", 1):      7.224,           # whisper 7.220 (+0.1 f): after the pause: r voicing 7.224
    ("s3", "The", 1):         0.033,           # whisper 0.020 (+0.4 f): dh voicing out of the lead
    ("s3", "we've", 1):       0.980,           # whisper 0.980 (+0.0 f): 'thing' ng murmur 0.961-0.98 (HF 0), w glide 0.980 (soft)
    ("s3", "ever", 1):        1.340,           # whisper 1.330 (+0.3 f): after the pause: soft onset 1.336-1.346 (tot -42 dB), full voicing 1.351
    ("s3", "the", 1):         2.300,           # whisper 2.300 (+0.0 f): after the pause: voicing 2.301
    ("s3", "Probe,", 1):      3.078,           # whisper 3.080 (-0.1 f): 'Solar' lar, p burst 3.078-3.081 (HF 2)
    ("s3", "reached", 1):     3.924,           # whisper 3.920 (+0.1 f): after the pause: r voicing 3.924
    ("s3", "hundred", 1):     4.941,           # whisper 4.940 (+0.0 f): 'seven' en to 4.94, h breath 4.941 (LF dip to 0 4.961-4.966, HF 3), vowel 4.976
    ("s3", "thousand,", 1):   5.739,           # whisper 5.740 (-0.0 f): after the pause: th noise 5.739
    ("s3", "falling", 1):     6.696,           # whisper 6.710 (-0.4 f): after the pause: a very soft f noise 6.69-6.81 (tot -48..-42 dB, HF 1), vowel 6.814
    ("s4", "Light", 1):       0.036,           # whisper 0.040 (-0.1 f): l voicing out of the lead
    ("s4", "does", 1):        0.551,           # whisper 0.550 (+0.0 f): after the breath: d BURST 0.551 (HF 6)
    ("s4", "billion.", 1):    1.528,           # whisper 1.520 (+0.2 f): after the b closure: b BURST 1.528 (HF 4)
    ("s4", "And", 1):         2.683,           # whisper 2.680 (+0.1 f): after the pause: soft glottal lead 2.671-2.681, vowel 2.686
    ("s4", "with", 1):        3.168,           # whisper 3.160 (+0.2 f): 'nothing' th 3.08-3.16 (LF 0), w voicing 3.168 (LF 2->5->8)
    ("s4", "the", 2):         6.276,           # whisper 6.270 (+0.2 f): after the pause: dh voicing 6.276
    ("s4", "each", 1):        7.046,           # whisper 7.040 (+0.2 f): 'energy' y + 'each' ea merged vowel 6.991-7.101: midpoint 7.046 (soft)
    ("s4", "step", 1):        7.216,           # whisper 7.210 (+0.2 f): 'each' ch+s quiet 7.106-7.126, t closure 7.13-7.21, t BURST 7.216 (weak), vowel 7.226
    ("s4", "without", 1):     8.309,           # whisper 8.310 (-0.0 f): after the pause: a voiceless w [wh] 8.309-8.33 (HF 2-5, LF 0), voicing later
    ("s5", "The", 1):         0.033,           # whisper 0.030 (+0.1 f): dh voicing out of the lead
    ("s5", "Large", 1):       0.148,           # whisper 0.160 (-0.4 f): 'The' schwa (MID 7-8) to 0.14, l 0.146 (MID falls 6->4, HF 1)
    ("s5", "pushes", 1):      1.618,           # whisper 1.610 (+0.2 f): 'Collider' er decays 1.54-1.57, p closure 1.576-1.611 (silence), p BURST 1.618 (tot 3->5, MID 5), voicing 1.686
    ("s5", "protons", 1):     2.014,           # whisper 2.010 (+0.1 f): 'pushes' z to 1.95, p closure 1.966-2.01, p BURST 2.014 (tot 5, LF 5, MID 4), devoiced r, vowel 2.091
    ("s5", "speed.", 1):      4.166,           # whisper 4.160 (+0.2 f): after the t closure of 'light': s noise 4.166 (HF 4-5, LF 0)
    ("s5", "Close.", 1):      5.189,           # whisper 5.190 (-0.0 f): after the pause: k BURST 5.189-5.196 (tot 4-6, HF 1-3), a soft 'lose' (tot -48..-36)
    ("s5", "But", 1):         6.319,           # whisper 6.320 (-0.0 f): after the pause: b BURST 6.321 (voice bar '1' at 6.316), dip 6.331-6.336, vowel 6.341
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
