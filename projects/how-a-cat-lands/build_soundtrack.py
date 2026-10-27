#!/usr/bin/env python3
"""Build the soundtrack premix: narration (+ the lesson-30 lifts) + the ducked, level-evened music bed (its LAST TONIC attack
landing ~0.15 s after 'vet.') + the SFX -> public/audio/soundtrack.wav (frame-aligned: exactly total_frames x 1600 samples @
48 kHz) and artifacts/soundtrack_report.json (video 14's shape: sfx[] rows with frame / placed_at_s /
landing_offset_in_sample_s, frames{}, ending{}, min_window; docs/channel/scripts/qa_auto.py reads them).

Run from the repo root:  python3 projects/how-a-cat-lands/build_soundtrack.py

Copied from projects/how-a-mosquito-drinks/build_soundtrack.py (video 14, QA passed; itself videos 12-13): the finished-line
chord placement, `with_harmonics` / `body` phone layers, the no-dead-air floor, SFX PEAKS on the visible landing frame. Every
film time comes from artifacts/timeline.json; the only seconds written here are positions INSIDE the source files.

THIS FILE OWNS THE KEY FRAMES (`K`, -> soundtrack_report.json 'frames' -> props.audio -> T.sfx.*): every root schedule in
build_props.py (the rig, the cat curves, the checklist ticks, the clock, the window plates, the dials) and every SFX landing
derive from them, so a visual and its sound can never drift apart. A beat that needs a new key frame is a §7 request.

Music bed (eleven_music_v2_5, 58.03 s; assets_report M1 + assets/music/music_qa.json, measured, lesson 26): G major, 96 BPM,
8th grid t = 0.288 + k * 0.3125 s. The ending is V (47.8-50.0) -> I (50.29 / 50.40) and the tonic RE-STRUCK at 52.81 s (the LAST
attack), left to ring. THERE IS NO IV-V-I (no IV at all; nothing here claims one). THE FINISHED-LINE CHORD IS THAT LAST TONIC
ATTACK: it lands CHORD_AFTER_S (0.15 s) after the release of 'vet.' (timeline vet_end_seconds). The head trim is SNAPPED TO THE
8th GRID (the k whose trim needs the smaller speed change), refined to the measured attack there; the rest is a resample of a
few cents (asserted <= MAX_CENTS). The V->I arrival (src 50.40) then lands ~2.4 s before the chord, i.e. at the very end of
the pause before 'It': the closing duck is therefore ramped in DURING that pause (from 'It' - CLOSING_LEAD_S), so the
bed's loudest event of the ending is already ducked (bed table 'bed_into_closing_50ms_rms_dbfs').
The ring-out is quiet (-24 dB re. the body at 53.0 s): RING_LIFT_DB on the bed from the chord + 0.15 s (0.2 s ramp) to the end.
LEVEL EVENING on 2 s windows (+-LEVEL_EVEN_MAX_DB, smoothed EVEN_SMOOTH_S, frozen 0.5 s before the chord).
Ducked DUCK_DB (-12) under narration (120 ms attack, 400 ms release, 250 ms hold); CLOSING_DUCK_DB (-13) more from the first
word of the closing sentence 'It' (lesson 44); END_DUCK_DB more under 'vet' + a +END_LIFT_DB 300-4000 Hz lift on the word;
all released linearly from the release of 'vet.' to 20 ms before the chord.
THE LIFTS (lesson 30, constant gains on the voice lane, raised-cosine 40 ms in / 30 ms out, never a limiter):
  'all four.' (s4, the soft '[softly]' landing; 'four' sat ~20 dB under 'Legs')     ALL_FOUR_GAIN_DB
  'reached the vet.' (s5; 'vet' sat ~10 dB under 'only')                            VET_GAIN_DB (raised from 5 dB in 1 dB steps
  until qa_auto's lesson-30 metric - the loudest 100 ms of 'vet' vs the MEDIAN of its sentence's words - is <= VET_MAX_UNDER_DB)
FLOOR: where the 100 ms mix level would fall under FLOOR_PRE_DBFS the duck is eased back (never above the undipped bed), so no
100 ms window of the premix is under -42 dBFS (lesson 5); never under the closing sentence (lesson 18 wins there).
END (lesson 43): cos^2 fade over the last FINAL_FADE_S to FINAL_FADE_FLOOR_DB, then a 10 ms ramp: last 50 ms <= -30 dBFS and
last 20 ms <= -33 dBFS (asserted, qa_auto's thresholds), no click.
SFX (assets/sfx/*.wav + sfx_qa.json; every transient ON its visible frame, lessons 4 / 14 / 22 / 41: PEAKS are aligned, not
sample 0; the key frame is the frame the element is FULLY down / open / landed). Phone band (lesson 5):
  X1 clamp_whoosh  as is (43 % in band); its click (0.145 s) ON the clamp's open frame (sc01, 'Drop').
  X2 window_slide  as is (80 % in band); a texture: STARTS on the window's first visible frame (S1 sc02, S2 sc09).
  X3 stamp_thunk   ONE hit cut STAMP_CUT (2.44-2.62 s, peak 2.512) + an LF body; ON each stamp's seat ('IMPOSSIBLE?' sc03,
                   'NOT ALWAYS' sc10).
  X4 check_tick    98 % > 4 kHz: ONE tick cut TICK_CUT (1.38-1.50 s, peak 1.402) + a 1-3 kHz body + with_harmonics; ON every
                   checklist tick (01-06).
  X5 spring_creak  97 % > 4 kHz: cut CREAK_CUT (0.03-0.32 s) pitched -4 st + a 1-3 kHz body + harmonics; its FIRST click ON
                   the twist's first moving frame (bend sc05, front turn sc06, swap sc08).
  X6 paw_thump     81 % in 60-300 Hz: + a 1-3 kHz CONTACT layer (band noise on its own envelope) + LF-saturation harmonics;
                   its peak (0.255 s) ON the paws' contact frame (sc09, 'all').
  X7 ledger_slide  as is (52 % in band), 0-1.5 s; its peak (0.448 s) ON the ledger card's seat (sc11, 'study').
  NOTHING from 50 ms before 'It' (the closing sentence) to the end (asserted on the SFX lane).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

P = Path("projects/how-a-cat-lands")
NDIR = P / "assets/audio/narration/clean"
SR = 48000
FPS = 30
CHORD_SRC_NEAR_S = 52.81           # music_qa last_tonic_attack_s (re-measured below)
VI_SRC_NEAR_S = 50.40              # music_qa resolution_attack_s (V -> I arrival; reported only)
GRID0_S = 0.288
GRID_S = 0.3125
CHORD_AFTER_S = 0.15
MAX_CENTS = 8.0
BED_LUFS = -19.0
LEVEL_EVEN_MAX_DB = 5.0
LEVEL_WIN_S = 2.0
EVEN_SMOOTH_S = 1.5
DUCK_DB = -12.0
CLOSING_DUCK_DB = -13.0
CLOSING_LEAD_S = 0.55
END_DUCK_DB = -6.0
END_DUCK_IN_S = 0.10
END_LIFT_DB = 4.0
END_LIFT_EDGE_S = 0.02
RING_LIFT_DB = 5.0
S4_GAIN_DB = 2.2           # s4 was true-peak-capped at -23.7 LUFS (others -21.5): ONE constant gain over the section (ramps in its silences)
ALL_FOUR_GAIN_DB = 4.0     # + on top of S4_GAIN_DB (total +6.2 on "all four.")
ALL_FOUR_DUCK_DB = -6.0
VET_GAIN_START_DB = 5.0
VET_GAIN_MAX_DB = 9.0
VET_MAX_UNDER_DB = 2.5
GAIN_RAMP_IN_S = 0.04
GAIN_RAMP_OUT_S = 0.03
TARGET_LUFS = -14.0
TP_CEIL_DBFS = -1.0
LIMIT_DBFS = -1.25
HARMONICS_DB = -4.0
HARMONICS_DECAY_S = 0.12
FLOOR_PRE_DBFS = -39.5
FLOOR_CH_PRE_DBFS = -40.2
SFX_SIDECHAIN_DB = -4.0
SFX_TEXTURE_DIP_DB = -2.0
FINAL_FADE_S = 0.60
FINAL_FADE_FLOOR_DB = -36.0
MIN_LAST_MARGIN_DB = 12.0
MIN_HIT_OVER_BED_DB = 4.0
CLAMP_PEAK_S = 0.145
STAMP_CUT = (2.440, 2.620)
TICK_CUT = (1.380, 1.500)
CREAK_CUT = (0.030, 0.320)
CREAK_FIRST_S = 0.020              # the first click inside the cut (file 0.05 s)
THUMP_PEAK_S = 0.255
LEDGER_PEAK_S = 0.448
LEDGER_LEN_S = 1.5
# motion constants shared with build_props.py (it imports this module)
SEAT_F = 8            # a stamp / the ledger card drop (gravity ease-in, still moving on seat - 1; T.seat)
WINDOW_OPEN_F = 6     # the window opens (out-quad, first visible frame ON its key frame)
WINDOW_CLOSE_F = 8    # ... and closes (ease-in-out)
XFADE_F = 12          # S1 -> A1 plate crossfade (the tag swaps by a HARD cut at the midpoint, lesson 38)
STRIP_STEP_F = 14     # the Marey strip advances one cell every 14 f (eased over STRIP_MOVE_F)
STRIP_MOVE_F = 8
TICK_F = 6            # a checklist tick draws (its stroke completes ON the tick frame)
TWIST_F = 12          # the bend forms over 14 f ending ON its seat; legs fold over TWIST_F
N_STRIP = 8


def key_frames(tl: dict) -> dict:
    """THE KEY FRAMES (props.audio -> T.sfx.*). Every visual landing + its sound is keyed here, from the measured words."""
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

    def on(section: str, text: str, nth: int = 1) -> int:
        hits = [w for w in tl["words"] if w["section"] == section and norm(w["text"]) == norm(text)]
        return int(round(hits[nth - 1]["start"] * FPS))

    def end(section: str, text: str, nth: int = 1) -> int:
        hits = [w for w in tl["words"] if w["section"] == section and norm(w["text"]) == norm(text)]
        return int(round(hits[nth - 1]["end"] * FPS))
    sc = {s["id"]: s for s in tl["scenes"]}
    rel_f = tl["vet_end_frame"]
    chord_f = int(round((tl["vet_end_seconds"] + CHORD_AFTER_S) * FPS))
    strip0 = on("s1", "1894") + 8
    K = {
        # sc01 CatDrop: the rig + the cat hanging under the clamp from frame 0; the clamp OPENS on 'Drop' (X1 click); the cat
        # falls (gravity) and flips feet-down (a preview) by 'midair'; then it holds as a ghost outline
        "clampOpen": on("s1", "drop"),
        "previewFlipEnd": on("s1", "midair"),
        # sc02 NothingToPush: the window opens ON the scene start (S1 plate, X2 slide); the readouts tick to their values
        "windowOpen1": sc["sc02"]["from"],
        "readouts": [on("s1", "nothing"), on("s1", "push")],
        # sc03 Marey1894: S1 -> A1 crossfade from the scene start (tag swap at the midpoint); the strip steps one cell per
        # STRIP_STEP_F; 'IMPOSSIBLE?' stamp SEATED on 'impossible' (X3); the window closes into sc04
        "plateSwap": sc["sc03"]["from"],
        "stripSteps": [strip0 + i * STRIP_STEP_F for i in range(N_STRIP - 1)],
        "stampImpossible": on("s1", "impossible"),
        "windowClose1": sc["sc04"]["from"] - WINDOW_CLOSE_F,
        # sc04 FindUp: the cat reset at the top (upside down) from the scene start; the clock starts on 'First'; the inner
        # ear glows from 'inner'; the UP arrow seats + '01 FIND UP' ticks on 'up' (X4)
        "catReset": sc["sc04"]["from"],
        "clockStart": on("s2", "first"),
        "innerEar": on("s2", "inner"),
        "tick01": on("s2", "up"),
        # sc05 Bend: the waist bends from 'bends', the V fully formed ON 'middle' (X5 creak on the first moving frame = 'bends');
        # the two axes + the dials appear on 'each'; 'total spin: 0' seats on 'turn'; '02 BEND' ticks on 'own' (X4)
        "bendStart": on("s2", "bends"),
        "bendSeat": on("s2", "middle"),
        "dialsIn": on("s2", "each"),
        "totalSeat": on("s2", "turn"),
        "tick02": on("s2", "own"),
        # sc06 TuckFront (HERO): the front legs fold from 'tucks', fully in ON 'legs'; the front half turns FAST and the back
        # half a little the other way from 'front' (2nd; X5 on the first moving frame) to turnEnd; '03 TUCK FRONT' on 'fast' (X4)
        "tuckStart": on("s3", "tucks"),
        "tuckSeat": on("s3", "legs"),
        "turnStart": on("s3", "front", 2),
        "tick03": on("s3", "fast"),
        "turnEnd": end("s3", "fast") + 4,
        # sc07 Skater: the skater pulls her arms in on 'pulling' (no SFX); the cat holds its pose
        "armsIn": on("s3", "pulling"),
        # sc08 Swap: the legs swap (back in, front out) from 'swaps' (X5 on the first moving frame); the back half follows from
        # 'back' to swapEnd (the front moves back a little); '04 SWAP' on 'follows' (X4)
        "swapStart": on("s3", "swaps"),
        "backTurnStart": on("s3", "back"),
        "tick04": on("s3", "follows"),
        "swapEnd": end("s3", "follows") + 4,
        # sc09 Land: the floor line from the scene start; legs spread ON 'out' + '05 SPREAD' (X4); back arched on 'arched'; the
        # paws CONTACT the floor ON 'all' (X6 thump); '06 LAND' ticks + the clock STOPS on 'four' + 6 (X4); the S2 window
        # opens in the landing beat after 'four.' (X2) and closes into sc10
        "floorIn": sc["sc09"]["from"],
        "tick05": on("s4", "out"),
        "arch": on("s4", "arched"),
        "land": on("s4", "all"),
        "tick06": on("s4", "four") + 6,
        "windowOpen2": end("s4", "four") + 2,
        "windowClose2": sc["sc10"]["from"] - WINDOW_CLOSE_F,
        # sc10 NotAlways: dials + 'total spin' are GONE before the 'But' page (lesson 42); 'NOT ALWAYS' stamp SEATED on
        # 'always' (X3); the short-drop ghost from 'Short', its FRONT turn starts on 'drops', it fades out before the floor
        # by 'turn' (never shown hitting anything)
        "dialsOut": on("s5", "but") - 4,
        "stampNotAlways": on("s5", "always"),
        "shortStart": on("s5", "short"),
        "shortTurn": on("s5", "drops"),
        "shortGone": on("s5", "turn"),
        # sc11 TheStudy: the ledger card slides in and SEATS on 'study' (X7 peak); the bar fills from 'ninety' to 'survived'
        "ledgerSeat": on("s5", "study"),
        "barFrom": on("s5", "ninety"),
        "barTo": on("s5", "survived"),
        # sc12 NotCounted: the ghost column draws from 'only'; 'not counted' on 'counted'; the bracket 'of cats brought in' on
        # 'cats'; NO SFX from 'It' - 50 ms; release vetEndFrame; chord chordFrame; CTA 4 f after the release
        "closingStart": on("s5", "it"),
        "ghostColumn": on("s5", "only"),
        "notCounted": on("s5", "counted"),
        "bracket": on("s5", "cats"),
        "vetFrame": on("s5", "vet"),
        "vetEndFrame": rel_f,
        "chordFrame": chord_f,
        "ctaFrame": rel_f + 4,
    }
    # ordering / spacing asserts (the visuals are built on these)
    assert K["clampOpen"] < K["previewFlipEnd"] < K["windowOpen1"] < K["readouts"][0] < K["readouts"][1] < K["plateSwap"], K
    assert K["plateSwap"] + XFADE_F < K["stripSteps"][0] and K["stripSteps"][-1] + STRIP_MOVE_F < K["windowClose1"], K
    assert K["stripSteps"][0] < K["stampImpossible"] < K["windowClose1"], K
    assert K["windowClose1"] + WINDOW_CLOSE_F <= K["catReset"] <= K["clockStart"] < K["innerEar"] < K["tick01"] < K["bendStart"], K
    assert K["bendStart"] + 8 <= K["bendSeat"] < K["dialsIn"] < K["totalSeat"] < K["tick02"] < K["tuckStart"], K
    assert K["tuckStart"] + 8 <= K["tuckSeat"] < K["turnStart"] < K["tick03"] < K["turnEnd"] < K["armsIn"] < K["swapStart"], K
    assert K["swapStart"] + 8 <= K["backTurnStart"] < K["tick04"] < K["swapEnd"] < K["floorIn"] <= K["tick05"] < K["arch"] < K["land"] < K["tick06"], K
    assert K["tick06"] < K["windowOpen2"] and K["windowOpen2"] + WINDOW_OPEN_F + 20 < K["windowClose2"], K
    assert K["windowClose2"] + WINDOW_CLOSE_F <= sc["sc10"]["from"] and K["dialsOut"] > K["windowClose2"] - 30, K
    assert K["stampNotAlways"] < K["shortStart"] < K["shortTurn"] < K["shortGone"] < K["ledgerSeat"] < K["barFrom"] < K["barTo"], K
    assert K["barTo"] < K["closingStart"] < K["ghostColumn"] < K["notCounted"] < K["bracket"] < K["vetFrame"] < rel_f < chord_f, K
    assert K["ctaFrame"] < tl["total_frames"] - 30, K
    return K


def decode(path: Path, channels: int, af: str | None = None) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-ac", str(channels)]
    cmd += ["-af", af] if af else ["-ar", str(SR)]
    raw = subprocess.run(cmd + ["-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, channels).copy()


def write_wav(path: Path, x: np.ndarray) -> None:
    y = np.clip(np.round(x * 32767), -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())


def lufs(path: Path) -> tuple[float, float]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])


def place(dst: np.ndarray, src: np.ndarray, at_s: float, fade_out_s: float = 0.0) -> None:
    a = int(round(at_s * SR))
    src = src[max(0, -a):]
    a = max(0, a)
    seg = src[: max(0, min(len(src), len(dst) - a))].copy()
    if fade_out_s > 0 and len(seg):
        n = min(len(seg), int(fade_out_s * SR)); seg[-n:] *= np.linspace(1, 0, n)[:, None]
    dst[a:a + len(seg)] += seg


def split_band(x: np.ndarray, lo_hz: float, hi_hz: float) -> np.ndarray:
    """Zero-phase band-pass via FFT with raised-cosine skirts (one octave below lo, a quarter-octave above hi)."""
    f = np.fft.rfftfreq(len(x), 1 / SR)
    lo_edge = np.clip(np.log2(np.maximum(f, 1e-9) / (lo_hz / 2)), 0, 1)
    hi_edge = np.clip(np.log2(hi_hz * 2 ** 0.25 / np.maximum(f, 1e-9)) / 0.25, 0, 1)
    h = (0.5 - 0.5 * np.cos(np.pi * lo_edge)) * (0.5 - 0.5 * np.cos(np.pi * hi_edge))
    return np.fft.irfft(np.fft.rfft(x, axis=0) * (h[:, None] if x.ndim == 2 else h), len(x), axis=0).astype(np.float32)


def onset_of(x: np.ndarray) -> int:
    return int(np.argmax(np.abs(x).max(axis=1) > 0.1 * np.abs(x).max()))


def band_share(x: np.ndarray, lo: float, hi: float) -> float:
    m = x.mean(axis=1) if x.ndim == 2 else x
    p = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1 / SR)
    return float(p[(f >= lo) & (f < hi)].sum() / (p.sum() + 1e-12))


def with_harmonics(x: np.ndarray, db: float = HARMONICS_DB, decay_s: float = HARMONICS_DECAY_S) -> tuple[np.ndarray, str]:
    """Phone layer (lesson 5; video 12/13's function, unchanged). LF mode (the hit has a body, >= 5 % in 25-250 Hz): saturate
    the hit's own low end and keep 300-2500 Hz of the result, decaying. HF mode (mostly > 4 kHz, no body): full-wave RECTIFY
    the hit's own 3.5-12 kHz band and keep 300-3500 Hz of that. Scaled to `db` re. the hit's peak (RMS over its first 150 ms)."""
    on = onset_of(x)
    if band_share(x, 25, 250) >= 0.05:
        low = split_band(x, 25, 250)
        sat = np.tanh(10.0 * low / (np.abs(low).max() + 1e-9))
        env = np.zeros(len(x), dtype=np.float32)
        env[on:] = np.exp(-np.arange(len(x) - on) / SR / decay_s)
        harm = split_band(sat, 300, 2500) * env[:, None]
        mode = "LF saturation 25-250 Hz -> 300-2500 Hz"
    else:
        hf = split_band(x, 3500, 12000)
        rect = np.abs(hf)
        rect = rect - rect.mean(axis=0)
        harm = split_band(rect, 300, 3500)
        mode = "HF rectification 3.5-12 kHz -> 300-3500 Hz"
    harm *= np.abs(x).max() * 10 ** (db / 20) / (np.sqrt(np.mean(harm[on:on + int(0.15 * SR)] ** 2)) + 1e-9)
    return (x + harm).astype(np.float32), mode


def body(x: np.ndarray, lo: float, hi: float, amount: float, seed: int, smooth_s: float = 0.005) -> np.ndarray:
    """a band-limited noise body that follows x's own envelope (phone-band presence for HF / LF-only sounds)"""
    nb = split_band(np.random.default_rng(seed).standard_normal(len(x)).astype(np.float32), lo, hi)
    k = max(1, int(smooth_s * SR))
    ev = np.sqrt(np.convolve(np.abs(x).mean(1) ** 2, np.ones(k) / k, mode="same")).astype(np.float32)
    return (x + amount * (nb * ev / (ev.max() + 1e-9))[:, None] * np.abs(x).max() / (np.abs(nb).max() + 1e-9)).astype(np.float32)


def limit(x: np.ndarray, thr_db: float, look_s: float = 0.005, rel_s: float = 0.08) -> np.ndarray:
    """Look-ahead peak limiter on the 4x-oversampled peak envelope (both channels linked)."""
    up = np.fft.irfft(np.fft.rfft(x, axis=0), 4 * len(x), axis=0) * 4
    pk = np.abs(up).max(axis=1).reshape(-1, 4).max(axis=1)
    thr = 10 ** (thr_db / 20)
    need = np.minimum(1.0, thr / np.maximum(pk, 1e-12))
    la = int(look_s * SR)
    padded = np.concatenate([need, np.ones(la)])
    g = np.lib.stride_tricks.sliding_window_view(padded, la + 1).min(axis=1)[: len(need)]
    a = np.exp(-1 / (rel_s * SR))
    out = np.empty_like(g); cur = 1.0
    for i, v in enumerate(g):
        cur = v if v < cur else a * cur + (1 - a) * v
        out[i] = cur
    k = int(0.002 * SR); w = np.hanning(2 * k + 1); w /= w.sum()
    sm = np.convolve(np.concatenate([np.full(k, out[0]), out, np.full(k, out[-1])]), w, mode="valid")
    return (x * np.minimum(sm, out)[:, None]).astype(np.float32)


def measured_onset(x: np.ndarray, near_s: float, win_s: float = 0.08, sr: int = SR) -> float:
    """Attack of the note nearest `near_s` (mono): the steepest 1 ms-RMS rise within +-win_s."""
    a, b = int((near_s - win_s) * sr), int((near_s + win_s) * sr)
    seg = x[a:b]
    hop = sr // 1000
    e = np.array([np.sqrt(np.mean(seg[i:i + 5 * hop] ** 2)) + 1e-9 for i in range(0, len(seg) - 5 * hop, hop)])
    d = np.diff(20 * np.log10(e))
    return (a + (int(np.argmax(d)) + 1) * hop) / sr


def pitch(x: np.ndarray, semitones: float) -> np.ndarray:
    """resample-pitch (shorter + higher for +, longer + lower for -)"""
    r = 2 ** (semitones / 12)
    n = int(len(x) / r)
    src = np.arange(n) * r
    return np.stack([np.interp(src, np.arange(len(x)), x[:, c]) for c in range(x.shape[1])], 1).astype(np.float32)




def main() -> None:
    tl = json.loads((P / "artifacts/timeline.json").read_text())
    total_frames = tl["total_frames"]
    total_s = total_frames / FPS
    n = total_frames * (SR // FPS)
    t = np.arange(n) / SR
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

    def word(section: str, text: str, nth: int = 1) -> dict:
        hits = [w for w in tl["words"] if w["section"] == section and norm(w["text"]) == norm(text)]
        return hits[nth - 1]

    rel_s = tl["vet_end_seconds"]
    rel_f = tl["vet_end_frame"]
    chord_film_s = rel_s + CHORD_AFTER_S
    K = key_frames(tl)
    hop = SR // 100

    # ---- music bed: head trimmed ON the 8th grid (refined to the measured attack), a few cents, last tonic at release + 0.15
    bed44 = decode(P / "assets/music/bed_raw.mp3", 1)[:, 0]
    chord_src = measured_onset(bed44, CHORD_SRC_NEAR_S, 0.05)
    vi_src = measured_onset(bed44, VI_SRC_NEAR_S, 0.12)
    assert abs(chord_src - CHORD_SRC_NEAR_S) <= 0.04, chord_src
    want_trim = chord_src - chord_film_s
    cands = []
    for kgrid in (int(np.floor((want_trim - GRID0_S) / GRID_S)), int(np.ceil((want_trim - GRID0_S) / GRID_S))):
        g_ = GRID0_S + kgrid * GRID_S
        tr_ = measured_onset(bed44, g_, 0.03)
        sp_ = (chord_src - tr_) / chord_film_s
        cands.append((abs(1200 * np.log2(sp_)), kgrid, g_, tr_))
    _, kgrid, grid_trim, trim_src = min(cands)
    speed = (chord_src - trim_src) / chord_film_s
    out_rate = int(round(SR / speed))
    speed = SR / out_rate
    cents = 1200 * np.log2(speed)
    assert abs(cents) <= MAX_CENTS, ("speed change beyond a few cents", cents, trim_src, grid_trim)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(P / "assets/music/bed_raw.mp3"), "-ac", "2", "-af",
                          f"aresample={out_rate}:resampler=soxr:precision=28", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    src = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
    a0 = int(round(trim_src * out_rate)) - int(0.002 * out_rate)
    bed = src[a0:].copy()
    assert len(bed) >= n, ("the bed is shorter than the film", len(bed) / SR, total_s)
    fi = int(0.008 * SR)
    bed[:fi] *= np.linspace(0, 1, fi)[:, None]
    music = bed[:n].copy()
    chord_film_actual = (int(round(chord_src * out_rate)) - a0) / SR
    vi_film_s = (int(round(vi_src * out_rate)) - a0) / SR
    ce = int(chord_film_actual * SR)
    pw = (music.astype(np.float64) ** 2).mean(1)
    lvl = 10 * np.log10(np.convolve(pw, np.ones(int(LEVEL_WIN_S * SR)) / (LEVEL_WIN_S * SR), mode="same")[::hop] + 1e-12)
    ci = ce // hop
    ref = float(np.median(lvl[100: ci - 50]))
    g_even = np.clip(ref - lvl, -LEVEL_EVEN_MAX_DB, LEVEL_EVEN_MAX_DB)
    g_even[:100] = g_even[100]
    g_even[ci - 50:] = g_even[ci - 50]
    ks = int(EVEN_SMOOTH_S * 100) | 1
    kh = np.hanning(ks); kh /= kh.sum()
    g_even = np.convolve(np.concatenate([np.full(ks // 2, g_even[0]), g_even, np.full(ks // 2, g_even[-1])]), kh, mode="valid")
    g_even[ci - 50:] = g_even[ci - 50]
    even_db = np.interp(np.arange(n) / hop, np.arange(len(g_even)), g_even)
    pre_even = [round(float(10 * np.log10(pw[i * SR:(i + 2) * SR].mean() + 1e-12)), 1) for i in range(0, int(chord_film_actual) - 1, 2)]
    # the ring-out lift (the tonic rings -24 dB re. the body 0.2 s after its attack): + RING_LIFT_DB from chord + 0.15 s
    ring = np.clip((t - (chord_film_actual + 0.15)) / 0.2, 0, 1)
    ring = 0.5 - 0.5 * np.cos(np.pi * ring)
    music *= (10 ** ((even_db + RING_LIFT_DB * ring) / 20)).astype(np.float32)[:, None]
    tmp = P / "assets/music/bed_edit_tmp.wav"
    write_wav(tmp, music[:ce])
    gain_db = BED_LUFS - lufs(tmp)[0]
    tmp.unlink(missing_ok=True)
    music *= np.float32(10 ** (gain_db / 20))
    film_rms2 = [round(float(20 * np.log10(np.sqrt(np.mean(music[i * SR:(i + 2) * SR] ** 2)) + 1e-9)), 1) for i in range(0, int(total_s) - 1, 2)]
    even_ok = [v for i, v in zip(range(0, int(total_s) - 1, 2), film_rms2) if i + 2 <= chord_film_actual - 0.5]
    assert max(even_ok) - min(even_ok) <= 3.0, ("bed not level after evening (2 s windows)", film_rms2)

    # ---- narration + the lesson-30 lifts --------------------------------------------------------------------------
    narration = np.zeros(n, dtype=np.float32)
    for s in tl["sections"]:
        x = decode(NDIR / f"{s['id']}.wav", 1)[:, 0]
        a = int(round(s["start"] * SR))
        narration[a:a + len(x)] += x[: max(0, n - a)]
    narration_unlifted = narration.copy()

    def gain_env(a_s: float, b_s: float) -> np.ndarray:
        e = np.clip((t - (a_s - GAIN_RAMP_IN_S)) / GAIN_RAMP_IN_S, 0, 1) * np.clip((b_s - t) / GAIN_RAMP_OUT_S, 0, 1)
        return (0.5 - 0.5 * np.cos(np.pi * e)).astype(np.float32)

    def peak100(x: np.ndarray, a_s: float, b_s: float) -> float:
        seg = x[int(a_s * SR):int(b_s * SR)].astype(np.float64)
        w = int(0.1 * SR)
        if len(seg) <= w:
            return float(10 * np.log10(np.mean(seg ** 2) + 1e-12))
        cs = np.concatenate([[0], np.cumsum(seg ** 2)])
        return float(10 * np.log10(((cs[w:] - cs[:-w]) / w).max() + 1e-12))
    s4sec = next(x for x in tl["sections"] if x["id"] == "s4")
    s4w = [x for x in tl["words"] if x["section"] == "s4"]
    s4env = np.clip((t - (s4w[0]["start"] - 0.25)) / 0.2, 0, 1) * np.clip(((s4w[-1]["end"] + 0.25) - t) / 0.2, 0, 1)
    assert s4w[0]["start"] - 0.25 > s4sec["start"] - 1.2, "the s4 gain ramp must sit in the gap before s4"
    narration = (narration * (1 + (10 ** (S4_GAIN_DB / 20) - 1) * s4env)).astype(np.float32)
    w_all, w_four = word("s4", "all"), word("s4", "four")
    af_a, af_b = w_all["start"], w_four["end"]
    narration = (narration * (1 + (10 ** (ALL_FOUR_GAIN_DB / 20) - 1) * gain_env(af_a, af_b))).astype(np.float32)
    s5_words = [w for w in tl["words"] if w["section"] == "s5"]
    i_it = max(i for i, x in enumerate(s5_words[:-1]) if x["text"].rstrip().endswith((".", "?", "!", ":"))) + 1
    sent = s5_words[i_it:]
    assert sent[0]["text"] == "It" and sent[-1]["text"] == "vet.", sent
    w_reached = word("s5", "reached")
    vw = word("s5", "vet")
    lifted_base = narration.copy()
    vet_gain = VET_GAIN_START_DB
    while True:
        cand = (lifted_base * (1 + (10 ** (vet_gain / 20) - 1) * gain_env(w_reached["start"], rel_s))).astype(np.float32)
        pk = [peak100(cand, x["start"], x["end"]) for x in sent]
        under = float(np.median(pk)) - pk[-1]
        if under <= VET_MAX_UNDER_DB or vet_gain >= VET_GAIN_MAX_DB:
            break
        vet_gain += 1.0
    narration = cand
    pk_before = [peak100(narration_unlifted, x["start"], x["end"]) for x in sent]
    vet_metric = {"metric": "qa_auto lesson 30: loudest 100 ms of 'vet.' vs the median of its sentence's words (voice lane)",
                  "gain_db": vet_gain, "span_film_s": [round(w_reached["start"] - GAIN_RAMP_IN_S, 3), round(rel_s, 3)],
                  "words": [x["text"] for x in sent], "peak100_before_dbfs": [round(v, 1) for v in pk_before],
                  "peak100_after_dbfs": [round(v, 1) for v in pk], "vet_under_median_before_db": round(float(np.median(pk_before)) - pk_before[-1], 1),
                  "vet_under_median_after_db": round(under, 1)}
    assert under <= 3.0, ("lesson 30: 'vet' still > 3 dB under its sentence median", vet_metric)
    # the band lift on 'vet' (lesson 18)
    g_on = vw["start"]
    a, b, e = int((g_on - 0.01) * SR), int((rel_s + 0.01) * SR), int(END_LIFT_EDGE_S * SR)
    pad = int(0.2 * SR)
    seg = narration[a - pad:b + pad].astype(np.float32)
    band = split_band(seg, 300, 4000)
    env = np.zeros(len(seg), np.float32)
    env[pad:pad + (b - a)] = 1.0
    ramp = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, e))).astype(np.float32)
    env[pad:pad + e] = ramp
    env[pad + (b - a) - e:pad + (b - a)] = ramp[::-1]
    narration[a - pad:b + pad] = seg + (10 ** (END_LIFT_DB / 20) - 1) * band * env

    # ---- ducking ----------------------------------------------------------------------------------------------------
    rms = np.sqrt(np.convolve(narration_unlifted ** 2, np.ones(hop) / hop, mode="same")[::hop] + 1e-12)
    voiced = 20 * np.log10(rms) > -45
    held = voiced.copy()
    last = -10 ** 9
    for i, v in enumerate(voiced):
        if v:
            last = i
        held[i] = i - last <= 25

    def duck_curve(depth: float) -> np.ndarray:
        target = np.where(held, depth, 0.0)
        g = np.zeros_like(target)
        cur = 0.0
        a_att, a_rel = 1 - np.exp(-1 / 12), 1 - np.exp(-1 / 40)
        for i, tg in enumerate(target):
            cur += (tg - cur) * (a_att if tg < cur else a_rel)
            g[i] = cur
        return np.interp(np.arange(n) / hop, np.arange(len(g)), g)

    duck_db = duck_curve(DUCK_DB)
    r0, r1 = rel_s, chord_film_actual - 0.02
    relr = np.clip((t - r0) / (r1 - r0), 0, 1)
    duck_db = np.where(t >= r0, np.minimum(0.0, duck_db[int(r0 * SR)] * (1 - relr)), duck_db)
    it_on = word("s5", "it")["start"]
    cl_env = np.clip((t - (it_on - CLOSING_LEAD_S)) / (CLOSING_LEAD_S - 0.15), 0, 1)
    cl_env = np.where(t >= r0, 1 - relr, 0.5 - 0.5 * np.cos(np.pi * cl_env))
    duck_db = duck_db + CLOSING_DUCK_DB * cl_env
    end_env = np.clip((t - (g_on - END_DUCK_IN_S)) / END_DUCK_IN_S, 0, 1)
    end_env = np.where(t >= r0, 1 - relr, 0.5 - 0.5 * np.cos(np.pi * end_env))
    duck_db = duck_db + END_DUCK_DB * end_env
    af_env = np.clip((t - (af_a - 0.1)) / 0.1, 0, 1) * np.clip((af_b + 0.1 - t) / 0.1, 0, 1)
    duck_db = duck_db + ALL_FOUR_DUCK_DB * (0.5 - 0.5 * np.cos(np.pi * af_env))
    att_db = duck_db.copy()
    music_undipped = music.copy()

    # ---- SFX ----------------------------------------------------------------------------------------------------
    sd = P / "assets/sfx"

    def fades(x, fin=0.001, fout=0.02):
        a_, b_ = int(fin * SR), int(fout * SR)
        x = x.copy()
        if a_:
            x[:a_] *= np.linspace(0, 1, a_)[:, None]
        x[-b_:] *= np.linspace(1, 0, b_)[:, None]
        return x

    pk_ = lambda x: float(np.argmax(np.abs(x).max(1)) / SR)
    clamp = decode(sd / "clamp_whoosh.wav", 2)
    assert abs(pk_(clamp) - CLAMP_PEAK_S) < 0.006, pk_(clamp)
    clamp = body(clamp, 1000, 3000, 0.8, 29, 0.003)          # a 1-3 kHz edge on the click (phone band)
    window = fades(decode(sd / "window_slide.wav", 2), 0.01, 0.12)
    stamp_full = decode(sd / "stamp_thunk.wav", 2)
    stamp = fades(stamp_full[int(STAMP_CUT[0] * SR):int(STAMP_CUT[1] * SR)], 0.003, 0.06)
    stamp, stamp_mode = with_harmonics(stamp, db=-6.0, decay_s=0.06)
    assert abs(pk_(stamp) + STAMP_CUT[0] - 2.512) < 0.01, pk_(stamp)
    tick_full = decode(sd / "check_tick.wav", 2)
    tick_cut = fades(tick_full[int(TICK_CUT[0] * SR):int(TICK_CUT[1] * SR)], 0.001, 0.04)
    tick_b = body(tick_cut, 1000, 3000, 1.2, 31, 0.003)
    tick, tick_mode = with_harmonics(tick_b, db=-2.0, decay_s=0.03)
    assert abs(pk_(tick_cut) + TICK_CUT[0] - 1.402) < 0.008, pk_(tick_cut)
    creak_full = decode(sd / "spring_creak.wav", 2)
    creak_cut = fades(creak_full[int(CREAK_CUT[0] * SR):int(CREAK_CUT[1] * SR)], 0.002, 0.05)
    accent = np.ones(len(creak_cut), np.float32)
    accent[int(0.012 * SR):int(0.040 * SR)] = 2.2              # the FIRST click (the key frame's) up ~7 dB to the level of the loudest
    creak_p = pitch(creak_cut * accent[:, None], -4.0)
    creak_b = body(creak_p, 1000, 3000, 1.0, 37, 0.004)
    creak, creak_mode = with_harmonics(creak_b, db=-3.0, decay_s=0.05)
    creak_first = CREAK_FIRST_S * 2 ** (4 / 12)     # pitched down 4 st: the cut is longer by 2^(4/12)
    thump_raw = decode(sd / "paw_thump.wav", 2)
    assert abs(pk_(thump_raw) - THUMP_PEAK_S) < 0.012, pk_(thump_raw)
    thump_b = body(thump_raw, 1000, 3000, 1.6, 43, 0.004)
    thump, thump_mode = with_harmonics(thump_b, db=-2.0, decay_s=0.08)
    ledger = fades(decode(sd / "ledger_slide.wav", 2)[: int(LEDGER_LEN_S * SR)], 0.02, 0.2)
    assert abs(pk_(ledger) - LEDGER_PEAK_S) < 0.01, pk_(ledger)

    PLACE = [
        ("X1", "clamp_release", clamp, -5.0, K["clampOpen"], "the clamp's jaws open (sc01, 'Drop'); its whoosh follows the fall", "peak", CLAMP_PEAK_S),
        ("X2", "window_open_S1", window, -16.0, K["windowOpen1"], "the window's first visible frame (S1, sc02)", "start", 0.0),
        ("X3", "stamp_impossible", stamp, -9.0, K["stampImpossible"], "'IMPOSSIBLE?' stamp SEATED (sc03)", "peak", pk_(stamp)),
        ("X4", "tick01", tick, -9.0, K["tick01"], "'01 FIND UP' tick", "peak", pk_(tick)),
        ("X5", "creak_bend", creak, -6.0, K["bendStart"], "the waist starts to bend (sc05; first click on the first moving frame)", "peak", creak_first),
        ("X4", "tick02", tick, -9.0, K["tick02"], "'02 BEND' tick", "peak", pk_(tick)),
        ("X5", "creak_turn", creak, -6.0, K["turnStart"], "the front half starts its fast turn (sc06)", "peak", creak_first),
        ("X4", "tick03", tick, -9.0, K["tick03"], "'03 TUCK FRONT' tick", "peak", pk_(tick)),
        ("X5", "creak_swap", creak, -6.0, K["swapStart"], "the legs start to swap (sc08)", "peak", creak_first),
        ("X4", "tick04", tick, -9.0, K["tick04"], "'04 SWAP' tick", "peak", pk_(tick)),
        ("X4", "tick05", tick, -9.0, K["tick05"], "'05 SPREAD' tick (legs out)", "peak", pk_(tick)),
        ("X6", "paw_thump", thump, -11.0, K["land"], "the paws CONTACT the floor line (sc09, 'all')", "peak", pk_(thump)),
        ("X4", "tick06", tick, -9.0, K["tick06"], "'06 LAND' tick + the clock stops", "peak", pk_(tick)),
        ("X2", "window_open_S2", window, -16.0, K["windowOpen2"], "the window's first visible frame (S2, sc09 landing beat)", "start", 0.0),
        ("X3", "stamp_not_always", stamp, -8.0, K["stampNotAlways"], "'NOT ALWAYS' stamp SEATED (sc10)", "peak", pk_(stamp)),
        ("X7", "ledger_seat", ledger, -11.0, K["ledgerSeat"], "the ledger card SEATED (sc11, 'study')", "peak", LEDGER_PEAK_S),
    ]
    PLACE.sort(key=lambda p: p[4])
    sfx = np.zeros((n, 2), dtype=np.float32)
    cues = []
    for xid, name, x, gdb, frame, rule, land, off in PLACE:
        x = x.copy()
        x *= np.float32(10 ** (gdb / 20) / (np.abs(x).max() + 1e-12))
        if land == "start":
            off = 0.0
        at = frame / FPS - off
        lane = np.zeros((n, 2), np.float32)
        place(lane, x, at, fade_out_s=0.01)
        sfx += lane
        cues.append({"id": xid, "name": name, "frame": frame, "seconds": round(frame / FPS, 3), "peak_dbfs": round(gdb, 1),
                     "landing": land, "landing_offset_in_sample_s": round(float(off), 4), "placed_at_s": round(float(at), 4),
                     "rule": rule, "_len": len(x)})
    closing_s = it_on
    assert np.abs(sfx[int((closing_s - 0.05) * SR):]).max() < 1e-6, "an SFX reaches under the closing sentence"
    sc_db = np.zeros(n)
    for c in cues:
        p0, p1_ = c["placed_at_s"], c["placed_at_s"] + c["_len"] / SR
        if c["landing"] == "start":
            env = np.clip((t - p0) / 0.3, 0, 1) * np.clip((p1_ - t) / 0.3, 0, 1)
            sc_db = np.minimum(sc_db, SFX_TEXTURE_DIP_DB * env)
            continue
        s0 = c["seconds"] - 0.09
        dur = 0.12 if c["id"] in ("X4", "X5") else 0.25
        env = np.clip((t - s0) / 0.02, 0, 1) * np.clip(1 - (t - (s0 + dur)) / 0.1, 0, 1)
        sc_db = np.minimum(sc_db, SFX_SIDECHAIN_DB * np.where(t < s0, 0, env))
    att_db = att_db + sc_db

    # ---- final fade, then no dead air -------------------------------------------------------------------------------
    fade = np.ones(n, np.float32)
    nf = int(FINAL_FADE_S * SR)
    nr = int(0.010 * SR)
    ffl = 10 ** (FINAL_FADE_FLOOR_DB / 20)
    fade[-nf:-nr] = ffl + (1 - ffl) * np.cos(np.linspace(0, np.pi / 2, nf - nr)) ** 2
    fade[-nr:] = ffl * np.linspace(1, 0, nr)
    voice2 = np.repeat(narration[:, None], 2, axis=1)
    w_ = 10
    lift_db = np.zeros(n // hop + 1)
    music = music_undipped * (10 ** (att_db / 20)).astype(np.float32)[:, None]
    for _ in range(3):
        mix_ = music + sfx + voice2
        m64 = mix_.astype(np.float64)
        lv = lambda pw_: 10 * np.log10(np.convolve(pw_[: (n // hop) * hop].reshape(-1, hop).mean(axis=1), np.ones(w_) / w_, mode="same") + 1e-12)
        lvl_ = lv(np.minimum((m64 ** 2).mean(axis=1), m64.mean(axis=1) ** 2))
        lvl_ch = lv(np.minimum(m64[:, 0] ** 2, m64[:, 1] ** 2))
        need = np.maximum.reduce([np.zeros_like(lvl_), FLOOR_PRE_DBFS - lvl_, FLOOR_CH_PRE_DBFS - lvl_ch])
        need[(n - nf) // hop - 5:] = 0
        need[int((it_on - 0.15) * 100): int(chord_film_actual * 100) + 1] = 0
        need = np.maximum.reduce([np.roll(need, k) for k in range(-12, 13)])
        kern = np.hanning(31)
        kern /= kern.sum()
        need = np.convolve(need, kern, mode="same")
        lift_db[: len(need)] = np.minimum(lift_db[: len(need)] + need, -np.interp(np.arange(len(need)) * hop, np.arange(n), att_db))
        # no floor lift may reach into the closing sentence (it fought the closing duck over the V -> I attack): faded out
        # over the 0.15 s before 'It' - 0.05 s, zero to the chord
        tt_ = np.arange(len(lift_db)) * 0.01
        lift_db *= np.where(tt_ >= chord_film_actual, 1.0, np.clip(((it_on - 0.05) - tt_) / 0.15, 0, 1))
        lift = np.interp(np.arange(n) / hop, np.arange(len(lift_db)), lift_db)
        music = music_undipped * (10 ** ((att_db + lift) / 20)).astype(np.float32)[:, None]
    floor_lift_max_db = float(lift_db.max())
    music = music * fade[:, None]
    mix = music + sfx + voice2
    mix_pre = mix.copy()

    # ---- loudness ---------------------------------------------------------------------------------------------------
    out = P / "public/audio/soundtrack.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    gain_total = 0.0
    for _ in range(6):
        write_wav(out, mix)
        integ, tpk = lufs(out)
        if abs(integ - TARGET_LUFS) <= 0.1 and tpk <= TP_CEIL_DBFS:
            break
        gdb = TARGET_LUFS - integ
        gain_total += gdb
        mix = limit(mix * np.float32(10 ** (gdb / 20)), LIMIT_DBFS)
    write_wav(out, mix)
    integ, tpk = lufs(out)
    assert len(mix) == n and tpk <= TP_CEIL_DBFS, (len(mix), n, tpk)
    ta, tb = int(g_on * SR), int(rel_s * SR)
    ref_ = np.abs(mix_pre[ta:tb] * np.float32(10 ** (gain_total / 20))).max(axis=1) + 1e-9
    red = 20 * np.log10(np.maximum(np.abs(mix[ta:tb]).max(axis=1), 1e-9) / ref_)
    lim_vet_db = round(float(np.min(red[ref_ > 1e-3])), 2)

    # ---- checks on the FINAL premix -------------------------------------------------------------------------------
    rms_db = lambda x: float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9))
    g_lin = np.float32(10 ** (gain_total / 20))
    bed_final = music * g_lin
    bed_table = {f"{tt:.2f}": round(rms_db(bed_final[int(tt * SR) - int(0.025 * SR): int(tt * SR) + int(0.025 * SR)]), 1)
                 for tt in (vi_film_s - 0.3, vi_film_s, vi_film_s + 0.1, it_on, it_on + 0.3, g_on, rel_s, rel_s + 0.10, chord_film_actual, chord_film_actual + 0.1)}
    sfx_final = sfx * g_lin
    ph_sfx, ph_bed, ph_voice = split_band(sfx_final, 300, 4000), split_band(bed_final, 300, 4000), split_band(narration * g_lin, 300, 4000)
    weak = []
    for c in cues:
        a = max(0, int(c["frame"] / FPS * SR) - int(0.075 * SR)) if c["landing"] == "peak" else int((c["placed_at_s"] + 0.25) * SR)
        b = a + int(0.15 * SR)
        d = {"sfx": round(rms_db(ph_sfx[a:b]), 1), "bed": round(rms_db(ph_bed[a:b]), 1), "voice": round(rms_db(ph_voice[a:b]), 1)}
        d["sfx_over_bed_db"] = round(d["sfx"] - d["bed"], 1)
        if c["landing"] == "peak":
            h = int((c["placed_at_s"] + c["landing_offset_in_sample_s"]) * SR) - int(0.015 * SR)
            d["hit_30ms_sfx_over_bed_db"] = round(rms_db(ph_sfx[h:h + int(0.03 * SR)]) - rms_db(ph_bed[h:h + int(0.03 * SR)]), 1)
        q0 = max(0, int(c["placed_at_s"] * SR)); q1 = min(n, q0 + c["_len"])
        w50 = int(0.05 * SR)
        diffs = [rms_db(ph_sfx[i:i + w50]) - rms_db(ph_bed[i:i + w50]) for i in range(q0, max(q0 + 1, q1 - w50), w50) if rms_db(ph_sfx[i:i + w50]) > -70]
        d["win50_max_over_bed_db"] = round(max(diffs), 1) if diffs else None
        c["final_phone_band_dbfs"] = d
        p0 = max(0, int(c["placed_at_s"] * SR))
        p1 = min(n, p0 + c.pop("_len"))
        c["sample_peak_dbfs"] = round(float(20 * np.log10(np.abs(sfx_final[p0:p1]).max() + 1e-12)), 1)
        if c["landing"] == "peak" and d["hit_30ms_sfx_over_bed_db"] < MIN_HIT_OVER_BED_DB:
            weak.append((c["name"], d["hit_30ms_sfx_over_bed_db"]))
    if weak:
        print("WEAK HITS (lesson 5):", weak)
    assert not weak or "--report" in sys.argv, ("lesson 5: hits not over the bed in the phone band", weak)
    # 'all four' vs the X6 thump in 300-4000 Hz (the lifted words must clear the thump on phones)
    fa, fb = int(af_a * SR), int(af_b * SR)
    sec_lufs = {}
    for x in tl["sections"]:
        a_, b_ = int(x["start"] * SR), int((x["start"] + x["durationInFrames"] / FPS) * SR)
        seg_ = narration[a_:b_].astype(np.float64)
        m_ = len(seg_) // 4800
        fr_ = seg_[: m_ * 4800].reshape(m_, 4800)
        e_ = 10 * np.log10((fr_ ** 2).mean(1) + 1e-12)
        sec_lufs[x["id"]] = round(float(10 * np.log10((fr_[e_ > e_.max() - 25] ** 2).mean() + 1e-12)), 1)
    print("voice-lane voiced RMS by section (pre-master dBFS)", sec_lufs)
    all_four = {"gain_db": ALL_FOUR_GAIN_DB, "s4_section_gain_db": S4_GAIN_DB, "voice_rms_by_section_dbfs": sec_lufs, "span_film_s": [round(af_a - GAIN_RAMP_IN_S, 3), round(af_b, 3)],
                "voice_band_dbfs": round(rms_db(ph_voice[fa:fb]), 1), "x6_band_dbfs": round(rms_db(ph_sfx[fa:fb]), 1),
                "bed_band_dbfs": round(rms_db(ph_bed[fa:fb]), 1)}
    all_four["voice_over_x6_db"] = round(all_four["voice_band_dbfs"] - all_four["x6_band_dbfs"], 1)
    all_four["voice_over_bed_db"] = round(all_four["voice_band_dbfs"] - all_four["bed_band_dbfs"], 1)
    vb_ = 20 * np.log10(np.sqrt(np.convolve(ph_voice.astype(np.float64) ** 2, np.ones(4800) / 4800, mode="same")[::480]) + 1e-9)
    bb_ = 20 * np.log10(np.sqrt(np.convolve(ph_bed.mean(axis=1).astype(np.float64) ** 2, np.ones(4800) / 4800, mode="same")[::480]) + 1e-9)
    vmask_ = (vb_ > vb_.max() - 30) & (np.arange(len(vb_)) * 0.01 < it_on)
    all_four["film_voice_over_bed_band_median_db"] = round(float(np.median((vb_ - bb_)[vmask_])), 1)
    fa100, fb100 = int(af_a * 100), int(af_b * 100)
    m_ = vmask_[fa100:fb100]
    all_four["voice_over_bed_band_median_db"] = round(float(np.median((vb_ - bb_)[fa100:fb100][m_])), 1) if m_.any() else None
    print("all four", all_four)
    assert all_four["voice_over_x6_db"] >= 3 and all_four["voice_over_bed_band_median_db"] >= all_four["film_voice_over_bed_band_median_db"] - 0.5, all_four
    w100 = int(0.1 * SR)
    hop100 = int(0.01 * SR)
    starts = np.arange(0, n - w100 + 1, hop100)
    body_ = starts + w100 <= n - nf
    m2 = (mix.astype(np.float64) ** 2).mean(axis=1)
    cs = np.concatenate([[0.0], np.cumsum(m2)])
    wdb = 10 * np.log10((cs[starts + w100] - cs[starts]) / w100 + 1e-12)
    mono2 = (mix.astype(np.float64).mean(axis=1)) ** 2
    csm = np.concatenate([[0.0], np.cumsum(mono2)])
    wdbm = 10 * np.log10((csm[starts + w100] - csm[starts]) / w100 + 1e-12)
    lead = int(tl["lead_seconds"] * SR)
    body_l = body_ & (starts >= lead)
    imin = int(np.argmin(np.where(body_l, wdb, 99)))
    imin_m = int(np.argmin(np.where(body_l, wdbm, 99)))
    mono = mix.astype(np.float64).mean(axis=1)
    last50 = rms_db(mono[-int(0.05 * SR):])
    last20 = rms_db(mono[-int(0.02 * SR):])
    tail = [round(rms_db(mono[n - int((k + 1) * 0.05 * SR): n - int(k * 0.05 * SR)]), 1) for k in range(12)][::-1]
    min_window = {"min_100ms_rms_dbfs": round(float(wdb[imin]), 1), "at_frame": round(starts[imin] / SR * FPS, 1),
                  "mono_fold_min_100ms_rms_dbfs": round(float(wdbm[imin_m]), 1), "mono_at_frame": round(starts[imin_m] / SR * FPS, 1),
                  "windows_below_minus42": int((wdb[body_l] < -42).sum()), "mono_windows_below_minus42": int((wdbm[body_l] < -42).sum()),
                  "lead_in_min_100ms_rms_dbfs": round(float(wdb[starts < lead].min()), 1),
                  "final_fade": {"seconds": FINAL_FADE_S, "floor_gain_db": FINAL_FADE_FLOOR_DB, "last_50ms_dbfs": round(last50, 1),
                                 "last_20ms_dbfs": round(last20, 1), "last_0p6s_by_50ms_dbfs": tail},
                  "note": "10 ms hop from the end of the 0.5 s lead-in to the start of the final fade (qa_auto's window); the fade is checked by its last 50 / 20 ms"}
    assert min_window["windows_below_minus42"] == 0 and min_window["mono_windows_below_minus42"] == 0, min_window
    assert last50 <= -30 and last20 <= -33, ("lesson 43: the end is not faded enough", tail)
    assert sum(1 for x_, y_ in zip(tail[-6:], tail[-5:]) if y_ > x_ + 3) == 0, ("the end steps up", tail)
    chord_meas = measured_onset(bed_final.mean(axis=1), chord_film_actual, 0.06)
    s5_0 = next(s["start"] for s in tl["sections"] if s["id"] == "s5")
    parts = {}
    for x in sent:
        a, b = int(x["start"] * SR), int(min(x["end"], x["start"] + 0.35) * SR)
        parts[x["text"]] = {"window_s5_s": [round(x["start"] - s5_0, 3), round(x["end"] - s5_0, 3)], "voice": round(rms_db(ph_voice[a:b]), 1), "bed": round(rms_db(ph_bed[a:b]), 1)}
        parts[x["text"]]["voice_over_bed_db"] = round(parts[x["text"]]["voice"] - parts[x["text"]]["bed"], 1)
    for k_, (a_s, b_s) in {"vet: v + e (onset + vowel)": (vw["start"], vw["start"] + 0.18), "vet: t release": (rel_s - 0.12, rel_s)}.items():
        a, b = int(a_s * SR), int(b_s * SR)
        parts[k_] = {"window_s5_s": [round(a_s - s5_0, 3), round(b_s - s5_0, 3)], "voice": round(rms_db(ph_voice[a:b]), 1), "bed": round(rms_db(ph_bed[a:b]), 1)}
        parts[k_]["voice_over_bed_db"] = round(parts[k_]["voice"] - parts[k_]["bed"], 1)
    margin = min(v["voice_over_bed_db"] for k_, v in parts.items() if k_ != "vet: t release")   # the release burst is reported, not a syllable
    assert margin >= MIN_LAST_MARGIN_DB, ("lesson 18: the closing sentence under +12 dB over the bed in 300-4000 Hz", parts)
    vm = np.repeat(voiced, hop)[:n]
    vm = np.pad(vm, (0, max(0, n - len(vm)))).astype(bool) & (t < closing_s)
    duck_report = {"target_db": DUCK_DB, "median_bed_attenuation_while_voiced_db": round(float(np.median((att_db + lift)[vm])), 1),
                   "p10_p90_db": [round(float(np.percentile((att_db + lift)[vm], 10)), 1), round(float(np.percentile((att_db + lift)[vm], 90)), 1)]}
    ending = {
        "release_s": rel_s, "release_frame": rel_f,
        "release_definition": "timeline.json vet_end_seconds: the last voiced 10 ms (-40 dB re. the narration max) of s5 (the t release of 'vet')",
        "chord": "the bed's LAST TONIC attack (G: open G-D, I re-struck after the V -> I at src 50.29-50.40). NO IV-V-I exists in this bed (music_qa); none is claimed",
        "chord_src_s": round(chord_src, 4), "chord_film_s": round(chord_film_actual, 4), "chord_measured_on_premix_bed_s": round(chord_meas, 4),
        "chord_after_release_s": round(chord_film_actual - rel_s, 3), "chord_measured_after_release_s": round(chord_meas - rel_s, 3),
        "chord_frame": K["chordFrame"],
        "v_to_i": {"src_s": round(vi_src, 4), "film_s": round(vi_film_s, 3), "it_onset_s": round(it_on, 3),
                   "note": "the V -> I arrival lands at the end of the pause before 'It': the closing duck ramps in from 'It' - 0.55 s, full from 'It' - 0.15 s"},
        "bed_into_closing_50ms_rms_dbfs": bed_table,
        "duck_release_s": [round(r0, 3), round(r1, 3)],
        "closing_duck": {"db": CLOSING_DUCK_DB, "ramp_from_s": round(it_on - CLOSING_LEAD_S, 3), "full_from_s": round(it_on - 0.15, 3)},
        "end_duck": {"db": END_DUCK_DB, "from_s": round(g_on - END_DUCK_IN_S, 3)},
        "end_lift": {"db": END_LIFT_DB, "band_hz": [300, 4000], "film_s": [round(g_on - 0.01, 3), round(rel_s + 0.01, 3)]},
        "ring_lift": {"db": RING_LIFT_DB, "from_s": round(chord_film_actual + 0.15, 3)},
        "vet_lift": vet_metric, "all_four_lift": all_four,
        "closing_words_300_4000": parts, "closing_min_margin_db": margin, "limiter_max_reduction_on_vet_db": lim_vet_db,
        "mix_rms_by_100ms_after_chord_dbfs": [round(rms_db(mix[ce + i * w100: ce + (i + 1) * w100]), 1) for i in range((n - ce) // w100)],
        "settle_after_chord_s": round(total_s - chord_film_actual, 3),
        "nothing_under_closing_line": "asserted: the SFX lane is silent from 'It' - 0.05 s to the end",
    }
    report = {
        "total_seconds": round(total_s, 4), "total_frames": total_frames, "samples": n, "sample_rate": SR, "channels": 2,
        "narration_source": "assets/audio/narration/clean/sN.wav (THE CLEAN WAVs, process_narration.py)",
        "frames": K,
        "motion": {"SEAT_F": SEAT_F, "WINDOW_OPEN_F": WINDOW_OPEN_F, "WINDOW_CLOSE_F": WINDOW_CLOSE_F, "XFADE_F": XFADE_F, "STRIP_STEP_F": STRIP_STEP_F,
                   "STRIP_MOVE_F": STRIP_MOVE_F, "TICK_F": TICK_F, "TWIST_F": TWIST_F},
        "music": {"source": "assets/music/bed_raw.mp3", "key": "G major, 96 BPM (music_qa); V -> I then the tonic re-struck at src 52.81 (the chord); NO IV-V-I",
                  "grid": {"t0_s": GRID0_S, "step_s": GRID_S, "k": kgrid, "grid_trim_s": round(grid_trim, 4)},
                  "trim_src_s": round(trim_src, 4), "wanted_trim_s": round(want_trim, 4), "chord_src_s": round(chord_src, 4),
                  "resample": {"decode_rate": out_rate, "speed": round(speed, 6), "cents": round(float(cents), 2)},
                  "level_evening": {"window_s": LEVEL_WIN_S, "max_db": LEVEL_EVEN_MAX_DB, "smooth_s": EVEN_SMOOTH_S, "ref_db": round(ref, 1),
                                    "gain_range_db": [round(float(even_db.min()), 2), round(float(even_db.max()), 2)], "bed_film_2s_dbfs_before_evening": pre_even},
                  "bed_film_2s_rms_dbfs_pre_mix_gain": film_rms2, "bed_gain_db": round(gain_db, 2), "bed_lufs_target": BED_LUFS,
                  "ducking": {"under_speech_db": DUCK_DB, "attack_ms": 120, "release_ms": 400, "hold_ms": 250, "measured": duck_report}},
        "ending": ending,
        "sfx_processing": {"X1": "as is (click 0.145 s on the clamp's open frame)", "X2": "as is (80 % in band); texture, start-aligned",
                           "X3": f"ONE hit cut {STAMP_CUT} s + with_harmonics: {stamp_mode}", "X4": f"ONE tick cut {TICK_CUT} s + 1-3 kHz body + with_harmonics: {tick_mode}",
                           "X5": f"cut {CREAK_CUT} s, -4 st, + 1-3 kHz body + with_harmonics: {creak_mode}; first click on the key frame",
                           "X6": f"+ 1-3 kHz contact layer (body) + with_harmonics: {thump_mode}", "X7": f"as is, 0-{LEDGER_LEN_S} s, peak {LEDGER_PEAK_S} s on the seat"},
        "sfx": cues,
        "master_gain_db": round(gain_total, 2),
        "limiter": {"threshold_dbfs": LIMIT_DBFS, "lookahead_ms": 5, "release_ms": 80, "oversampling": 4},
        "floor_lift_max_db": round(floor_lift_max_db, 1),
        "soundtrack_lufs": integ, "soundtrack_true_peak_dbfs": tpk,
        "min_window": min_window,
        "note": "Premix at the delivery loudness (-14 LUFS integrated, TP <= -1 dBFS). All anchors from artifacts/timeline.json.",
    }
    (P / "artifacts/soundtrack_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(f"integrated {integ} LUFS, true peak {tpk} dBFS, master gain {gain_total:+.2f} dB; bed trim {trim_src:.3f} cents {cents:.2f}")
    print("chord film", round(chord_film_actual, 3), "after release", round(chord_film_actual - rel_s, 3), "V->I film", round(vi_film_s, 3), "It", round(it_on, 3))
    print("bed table", bed_table)
    print("vet", vet_metric["gain_db"], "dB, under median", vet_metric["vet_under_median_before_db"], "->", vet_metric["vet_under_median_after_db"])
    print("all four", all_four)
    for k_, v in parts.items():
        print(f"  {k_:<26} voice {v['voice']:6.1f} bed {v['bed']:6.1f}  +{v['voice_over_bed_db']:.1f} dB")
    for c in cues:
        fb = c["final_phone_band_dbfs"]
        print(f'{c["id"]:<4}{c["name"]:<18} f{c["frame"]:5d}  sfx-bed {fb["sfx_over_bed_db"]:+5.1f}  30ms {fb.get("hit_30ms_sfx_over_bed_db", float("nan")):+5.1f}  50ms max {fb["win50_max_over_bed_db"]}')
    print("duck", duck_report, "floor lift max", round(floor_lift_max_db, 1), "min window", min_window)


if __name__ == "__main__":
    main()
