#!/usr/bin/env python3
"""Build the soundtrack premix: narration + the ducked, level-evened music bed (landing on its own final C attack, which
rings out) + the SFX -> public/audio/soundtrack.wav (frame-aligned: exactly total_frames x 1600 samples @ 48 kHz), and
artifacts/soundtrack_report.json (with the phone-band checks).

Run from the repo root:  python3 projects/how-hot-can-it-get/build_soundtrack.py

Pattern copied from projects/what-if-earth-stopped-spinning/build_soundtrack.py (video 12, delivered, QA passed): the
finished-line chord placement, `with_harmonics` phone layers, the broadband lift + extra duck + band lift on the last
word, the no-dead-air floor, SFX PEAKS on the visible landing frame. Every film time comes from artifacts/timeline.json
(aligned words, frames @ 30 fps); the only seconds written here are positions INSIDE the source files.

THIS FILE OWNS THE KEY FRAMES (`K`, -> soundtrack_report.json 'frames' -> props.audio -> T.sfx.*): every root schedule in
build_props.py (the glow sweep, the ladder rail's camera / scale, the rungs and marks, the '?', the windows, the zeros
counter, the fray) and every SFX landing are derived from them, so a visual and its sound can never drift apart.
Builders read them through useT(); a beat that needs a new key frame is a §7 request.

Narration: THE CLEAN WAVs assets/audio/narration/clean/sN.wav (process_narration.py) at each section's EXACT start.

Music bed (eleven_music_v2_5, 58.0 s; assets_report M1 + music_qa.json): C major (asked D, lesson 26), 75 BPM, 16th-note
onset grid t = 0.189 + k * 0.200 s. There is NO IV-V-I: over a G pedal the C/G/A/D figure stops; its last strong attack
(bass to C) is at src ~51.18 s (re-measured below as the steepest 1 ms rise), then ~5 s of natural decay. That attack is
THE FINAL CHORD: it lands CHORD_AFTER_S (0.15 s) after the release of "know." (timeline.know_end_seconds). The head trim
is SNAPPED TO THE GRID and refined to the measured attack there; the remainder is a resample of a few cents (asserted <=
MAX_CENTS). No splice, no synthetic tail (last FINAL_FADE_S faded).
LEVEL EVENING: the bed climbs ~11 dB in steps at src 19.0 / 32.0 / 44.5 s with a dip 39.5-44.5 s and a quiet head: a
gain curve (the inverse of its 1 s level, +-LEVEL_EVEN_MAX_DB, smoothed EVEN_SMOOTH_S - short, so the 0.5 s steps leave
no long bumps) holds it flat before the chord (report: bed_film_1s_rms).
Ducked DUCK_DB (-12) under narration (120 ms attack, 400 ms release, 250 ms hold); RELEASED BEFORE THE CHORD (linear from
the release of "know." to 20 ms before the chord).
THE LAST WORD (lessons 18, 30): 'know.' sat 6.2 dB under its sentence (assets_report N-s5 last_word_level). A constant
BROADBAND gain KNOW_GAIN_DB on the voice over 'know.' only (raised-cosine ramp in over 40 ms before its onset, out over
30 ms ending at the release: a lift, not a limiter, so the falling cadence keeps its shape) -> broadband within ~3 dB of
its sentence (measured + asserted); then an EXTRA END_DUCK_DB under it and a +END_LIFT_DB 300-4000 Hz band lift on the
word; measured on the final premix (KNOW_PARTS, s5 seconds) and asserted >= +12 dB over the bed.
FLOOR: where the 100 ms mix level would fall under FLOOR_PRE_DBFS the bed's duck is eased back (never above the undipped
bed), so no 100 ms window of the premix is under -42 dBFS (the final fade excepted).
SFX (scene_plan.metadata.audio.sfx + overlay_notes; assets/sfx/*.wav + sfx_qa.json; every transient ON its visible
frame, lessons 4 / 14 / 22: PEAKS are aligned, not sample 0). X1-X6 are almost entirely outside 300-4000 Hz (sfx_qa
band_pct) -> each gets a phone layer (with_harmonics, video 12's function) and/or a band-limited body (lesson 5):
  X1 ember_crackle  frame 0: the low crackle bed fades up under the forge frame (sc01); + LF harmonics + 1-3 kHz crackle body.
  X7 counter_tick   the asset is a RATCHET of 8 clicks 62 ms apart: ONE click cut (TICK_CUT, transient 0.158 s), + a
                    1-3 kHz body + HF harmonics; its PEAK on: the floor label seat, the DV / Venus / Sun-core / KSTAR
                    rung seats, the LHC digit-group seats (light; the last LOUDER) and the 20 zeros-counter steps (light,
                    accelerating then settling; none on 'breaks').
  X3 filament_ignite 97 % in 60-300 Hz: + LF harmonics + 600-2500 Hz body; soft, its PEAK on the '?' ignition (sc02) and
                    on the Planck mark (sc10, softer).
  X2 heat_hiss      99 % above 4 kHz: + HF harmonics (rectified) + 1-3 kHz body; a looped texture under the K1 / S2
                    window (sc03-sc04, low, ducked under speech) and a soft rising texture under the quark soup (sc09).
  X4 glow_swell     79 % below 300 Hz, crest 1.109 s: + LF harmonics + a rising 800-3000 Hz shimmer body; its CREST on the
                    Sun's-core seat (the sweep builds under it).
  X5 reactor_hum    78 % below 60 Hz: HP 40 Hz + LF harmonics (2nd-4th); a looped texture under the K2 window (sc06).
  X6 impact_thump   79 % below 60 Hz, attack 7 ms: + LF harmonics + a 1-4 kHz shimmer tail; its PEAK on the beam flash.
  X8 settle_tone    spare: NOT used (nothing under the closing sentence; the chord is the bed's own).
  NOTHING from 50 ms before 'So' (the closing sentence, s5) to the end (asserted on the SFX lane).
Phone audibility (lesson 5): SFX vs BED in 300 Hz-4 kHz over a 150 ms window around the landing, master gain applied;
the bed dips SFX_SIDECHAIN_DB under every transient hit.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

P = Path("projects/how-hot-can-it-get")
NDIR = P / "assets/audio/narration/clean"
SR = 48000
FPS = 30
CHORD_SRC_NEAR_S = 51.18            # assets_report M1 / music_qa: the last strong attack (bass to C); re-measured below
GRID0_S = 0.189
GRID_S = 0.200
CHORD_AFTER_S = 0.15
MAX_CENTS = 8.0
BED_LUFS = -19.0
LEVEL_EVEN_MAX_DB = 7.0
EVEN_SMOOTH_S = 0.6
DUCK_DB = -12.0
TEXTURE_DUCK_DB = -8.0
END_DUCK_DB = -12.0
END_DUCK_IN_S = 0.10
END_LIFT_DB = 4.0
KNOW_GAIN_DB = 5.5          # lesson 30: 'know.' sat 6.2 dB under its sentence (assets_report N-s5): a constant broadband lift
KNOW_GAIN_RAMP_IN_S = 0.04
KNOW_GAIN_RAMP_OUT_S = 0.03
KNOW_MAX_UNDER_SENTENCE_DB = 3.0
END_LIFT_EDGE_S = 0.02
KNOW_PARTS = {"n+o (nasal + vowel)": (10.245, 10.45), "o (vowel)": (10.30, 10.55)}   # s5 seconds (the clean WAV); 'know.' = 10.245 -> 10.64
KNOW_LIFT_SEC = ("s5", 10.235, 10.66)
TARGET_LUFS = -14.0
TP_CEIL_DBFS = -1.0
LIMIT_DBFS = -1.25
HARMONICS_DB = -4.0
HARMONICS_DECAY_S = 0.12
FLOOR_PRE_DBFS = -39.5
FLOOR_CH_PRE_DBFS = -40.2
SFX_SIDECHAIN_DB = -4.0
SFX_TEXTURE_DIP_DB = -2.0
FINAL_FADE_S = 0.40       # QA A-m5: the chord DECAYS out (cos^2 to FINAL_FADE_FLOOR_DB, then a 10 ms ramp to 0: every 100 ms >= -42)
FINAL_FADE_FLOOR_DB = -8.0   # the mono fold of the last 100 ms stays >= -42 on the master too
MIN_KNOW_MARGIN_DB = 12.0
TICK_CUT = (0.128, 0.192)   # X7: one click of the 8-click ratchet (transient 0.158 s)
TICK_PEAK_S = 0.158
SWELL_PEAK_S = 1.109        # X4 crest (sfx_qa peak_time_in_trimmed_s; trimmed 0.125 s head in the asset)
THUMP_PEAK_S = 0.007
FILAMENT_PEAK_S = 0.062
# motion constants shared with build_props.py (it imports this module)
SEAT_F = 8            # a rung / label drop (gravity ease-in, still moving on seat - 1; T.seat)
FLOOR_DRAW_F = 12     # sc01: the floor hairline draws left -> right
CAM_TILT_F = 60       # sc02: the view tilts up (the floor slides down CAM_TILT_PX)
CAM_RETURN_F = 20     # sc03: the floor returns
Q_DRAW_F = 18         # sc02: the filament '?' draws
SPINE_DRAW_F = 20     # sc02: the dashed spine draws floor -> '?'
WINDOW_OPEN_F = 8     # a window opens / closes (scale + fade)
MEDIA_XFADE_F = 8     # a window's media crossfades to the next plate
LUT_F = 8             # sc03: the false-colour view fades in
ZOOM_F = 24           # a rail re-scale (sc03 -> sweep, sc05 -> sc06)
COMPRESS_F = 10       # sc08: the rail compresses (log scale re-spaces; done before the first digit group seats)
DRIFT_F = 40          # sc10: the camera drifts up to the Planck view
DIM_F = 10            # a window dims (sc08 / sc09)
Q_DIM_F = 15          # sc10: the '?' dims to half
Q_FADE_F = 20         # sc12: the '?' fades out
FRAY_F = 14           # sc11: the rail above the Planck mark frays + fades to a broken dash
SETTLE_GLOW_F = 45    # sc12-sc13: the glow eases to its low settle intensity (constant from the release)
LHC_GROUP_F = [0, 8, 15, 22, 29]   # sc08: '> 5' / ',000' x4 seat on 'five' + these (the ' K' + label LOUDER on 'degrees')
ZERO_STEPS = [5, 4, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3]   # sc11: intervals of the 12 -> 32 count (accel, settle)


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


def highpass(x: np.ndarray, hz: float) -> np.ndarray:
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = np.clip(np.log2(np.maximum(f, 1e-9) / (hz / 2)), 0, 1)
    h = 0.5 - 0.5 * np.cos(np.pi * h)
    return np.fft.irfft(np.fft.rfft(x, axis=0) * h[:, None], len(x), axis=0).astype(np.float32)


def onset_of(x: np.ndarray) -> int:
    return int(np.argmax(np.abs(x).max(axis=1) > 0.1 * np.abs(x).max()))


def band_share(x: np.ndarray, lo: float, hi: float) -> float:
    m = x.mean(axis=1) if x.ndim == 2 else x
    p = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1 / SR)
    return float(p[(f >= lo) & (f < hi)].sum() / (p.sum() + 1e-12))


def with_harmonics(x: np.ndarray, db: float = HARMONICS_DB, decay_s: float = HARMONICS_DECAY_S) -> tuple[np.ndarray, str]:
    """Phone layer (lesson 5; video 12's function, unchanged). LF mode (the hit has a body, >= 5 % in 25-250 Hz): saturate
    the hit's own low end and keep 300-2500 Hz of the result, decaying. HF mode (mostly > 4 kHz, no body): full-wave
    RECTIFY the hit's own 3.5-12 kHz band and keep 300-3500 Hz of that. Scaled to `db` re. the hit's peak (RMS over its
    first 150 ms)."""
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


def true_peak_db(x: np.ndarray) -> float:
    up = np.fft.irfft(np.fft.rfft(x, axis=0), 4 * len(x), axis=0) * 4
    return float(20 * np.log10(np.abs(up).max() + 1e-12))


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
    """resample-pitch (shorter + higher): the louder ticks"""
    r = 2 ** (semitones / 12)
    n = int(len(x) / r)
    src = np.arange(n) * r
    return np.stack([np.interp(src, np.arange(len(x)), x[:, c]) for c in range(x.shape[1])], 1).astype(np.float32)


def loop_plateau(x: np.ndarray, a_s: float, b_s: float, dur_s: float, xf_s: float = 0.25) -> np.ndarray:
    """a steady bed: the [a, b] plateau of x repeated with raised-cosine crossfades to dur_s"""
    seg = x[int(a_s * SR):int(b_s * SR)]
    k = int(xf_s * SR)
    fi = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, k)))[:, None].astype(np.float32)
    out = seg.copy()
    while len(out) < dur_s * SR:
        out = np.concatenate([out[:-k], out[-k:] * (1 - fi) + seg[:k] * fi, seg[k:]])
    return out[: int(dur_s * SR)]


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

    fr = lambda s: int(round(s * FPS))
    on = lambda s_, w_, k=1: fr(word(s_, w_, k)["start"])
    sc = {s["id"]: s for s in tl["scenes"]}
    rel_s = tl["know_end_seconds"]
    rel_f = tl["know_end_frame"]
    chord_film_s = rel_s + CHORD_AFTER_S

    # ---- KEY FRAMES (props.audio -> T.sfx.*; the root schedules and every SFX are keyed to these) ------------------
    zero0 = on("s5", "roughly")
    zticks = [zero0]
    for d in ZERO_STEPS:
        zticks.append(zticks[-1] + d)
    zticks.append(on("s5", "zeros"))       # the 20th step (32) lands ON 'zeros'
    K = {
        # sc01 FloorLine: the ember bed fades up from frame 0; the ice floor hairline draws on 'floor'; its label
        # '0 K = -273.15 °C' SEATED on 'absolute' (X7 tick)
        "ember": 0,
        "floorDraw": on("s1", "floor"),
        "floorLabelSeat": on("s1", "absolute"),
        # sc02 CeilingQuestion: the view tilts up from the scene start (the floor slides down, CAM_TILT_F); the filament
        # '?' ignites + draws on 'ceiling' (X3 soft PEAK there); the dashed spine draws floor -> '?' from 'ceiling' + 3
        "camTilt": sc["sc02"]["from"],
        "qStart": on("s1", "ceiling"),
        "spineStart": on("s1", "ceiling") + 3,
        # sc03 DeathValley: the window opens onto K1 at the scene start (forward only; 'AI impression'), the floor returns;
        # the DV rung SEATED on 'fifty-seven' (X7); the false-colour view on 'degrees'; X2 hiss texture under the window
        "windowOpen": sc["sc03"]["from"],
        "dvSeat": on("s2", "fifty-seven"),
        "lutOn": on("s2", "degrees"),
        # sc04 Venus: the window crossfades to S2 at the scene start (the false colour clears with it); the Venus rung
        # SEATED on 'four' (X7); the 'first visible glow ~525 °C' mark on 'hot'; U1's lead ingot slumps on 'melt'
        "venusXfade": sc["sc04"]["from"],
        "venusSeat": on("s2", "four"),
        "draperMark": on("s2", "hot"),
        "leadMelt": on("s2", "melt"),
        # sc05 GlowSweep (HERO 1): the window closes at the scene start; the glow sweeps 737 K -> 15 million degC from
        # 'The' to 'million' (the Sun's-core rung SEATED there: X4 swell CREST + X7); the marks appear as it passes them
        "windowClose1": sc["sc05"]["from"],
        "sweepStart": on("s3", "the"),
        "sunCoreSeat": on("s3", "million"),
        # sc06 Reactor: the window reopens onto K2 at the scene start (forward, then held; X5 hum texture); the KSTAR rung
        # SEATED on 'hundred' (X7); U2's 48-second timer arc on 'forty-eight'
        "windowOpen2": sc["sc06"]["from"],
        "kstarSeat": on("s3", "hundred"),
        "timerArc": on("s3", "forty-eight"),
        # sc07 Collider: the window crossfades to S4 at the scene start; U3's beam lines converge and FLASH on 'smashed'
        # (X6 thump PEAK there)
        "colliderXfade": sc["sc07"]["from"],
        "beamFlash": on("s4", "smashed"),
        # sc08 FiveTrillion: the rail compresses from the scene start; the window dims; the LHC number's digit groups SEAT
        # from 'five' (X7 light) and its ' K' + label on 'degrees' (X7 LOUDER) = lhcSeat; the zeros chip '12 zeros' seats there
        "compress": sc["sc08"]["from"],
        "lhcGroupSeats": [on("s4", "five") + d for d in LHC_GROUP_F],
        "lhcSeat": on("s4", "degrees"),
        # sc09 QuarkSoup: the window dims further for U3's drawn proton -> quark soup (X2 soft texture rising); protons
        # melt on 'melt'
        "soupStart": sc["sc09"]["from"],
        "protonMelt": on("s4", "melt"),
        # sc10 PlanckTemperature: the window closes at the scene start; the camera drifts up to the Planck view
        # (DRIFT_F); the Planck mark appears on 'Planck' (X3 soft PEAK), the '?' dims to half
        "windowClose2": sc["sc10"]["from"],
        "drift": sc["sc10"]["from"],
        "planckMark": on("s5", "planck"),
        # sc11 ThirtyTwoZeros (HERO 2): the chip counts 12 -> 32 on these 20 frames (X7 light ticks, accelerating then
        # settling; 32 ON 'zeros'); U4 writes '1.4 × 10^32 K' from 'zeros'; the rail above the mark FRAYS on 'breaks' (no SFX)
        "zeroTicks": zticks,
        "sciWrite": on("s5", "zeros"),
        "fray": on("s5", "breaks"),
        # sc12 NoCeiling (NO SFX from 'So'): the '?' fades out on 'ceiling'; the glow eases to its settle intensity from 'So'
        "closingStart": on("s5", "so"),
        "qFade": on("s5", "ceiling"),
        # sc13 EdgeOfKnowing: 'know.' -> the bed's final C attack 0.15 s after its release; the CTA 4 f after the release
        "knowFrame": on("s5", "know"),
        "knowEndFrame": rel_f,
        "chordFrame": fr(chord_film_s),
        "ctaFrame": rel_f + 4,
    }
    assert len(K["zeroTicks"]) == 20 and all(b - a >= 2 for a, b in zip(zticks, zticks[1:])), zticks
    assert K["zeroTicks"][-1] - K["zeroTicks"][-2] >= 2 and K["zeroTicks"][-1] < K["fray"], zticks
    assert K["dvSeat"] > K["windowOpen"] + WINDOW_OPEN_F and K["venusSeat"] > K["venusXfade"] + MEDIA_XFADE_F, K
    assert K["sweepStart"] >= K["windowClose1"] and K["sunCoreSeat"] - K["sweepStart"] >= 45, K
    assert K["kstarSeat"] > K["windowOpen2"] + WINDOW_OPEN_F and K["beamFlash"] > K["colliderXfade"] + MEDIA_XFADE_F, K
    assert K["lhcGroupSeats"][-1] < K["lhcSeat"] and K["compress"] + COMPRESS_F <= K["lhcGroupSeats"][0], K
    assert K["drift"] + DRIFT_F <= K["planckMark"] + 4 and K["qFade"] < rel_f and K["chordFrame"] > rel_f, K

    # ---- music bed: head trimmed ON the 16th grid (refined to the measured attack), a few cents, the chord at release + 0.15
    bed44 = decode(P / "assets/music/bed_raw.mp3", 1)[:, 0]
    chord_src = measured_onset(bed44, CHORD_SRC_NEAR_S, 0.05)
    assert abs(chord_src - CHORD_SRC_NEAR_S) <= 0.04, chord_src
    want_trim = chord_src - chord_film_s
    kgrid = int(round((want_trim - GRID0_S) / GRID_S))
    grid_trim = GRID0_S + kgrid * GRID_S
    trim_src = measured_onset(bed44, grid_trim, 0.03)
    speed = (chord_src - trim_src) / chord_film_s
    out_rate = int(round(SR / speed))
    speed = SR / out_rate
    cents = 1200 * np.log2(speed)
    assert abs(cents) <= MAX_CENTS, ("speed change beyond a few cents", cents, trim_src, grid_trim)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(P / "assets/music/bed_raw.mp3"), "-ac", "2", "-af",
                          f"aresample={out_rate}:resampler=soxr:precision=28", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    src = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()   # src samples at out_rate == film samples at SR
    a0 = int(round(trim_src * out_rate)) - int(0.002 * out_rate)
    bed = src[a0:].copy()
    fi = int(0.008 * SR)
    bed[:fi] *= np.linspace(0, 1, fi)[:, None]
    music = np.zeros((n, 2), dtype=np.float32)
    music[: min(n, len(bed))] = bed[:n]
    chord_film_actual = (int(round(chord_src * out_rate)) - a0) / SR
    ce = int(chord_film_actual * SR)
    # LEVEL EVENING (the quiet head + the steps at src 19.0 / 32.0 / 44.5 s + the 39.5-44.5 s dip): inverse of the bed's
    # 1 s level, +-LEVEL_EVEN_MAX_DB, smoothed EVEN_SMOOTH_S, frozen 0.5 s before the chord
    hop = SR // 100
    pw = (music.astype(np.float64) ** 2).mean(1)
    lvl = 10 * np.log10(np.convolve(pw, np.ones(SR) / SR, mode="same")[::hop] + 1e-12)
    ci = ce // hop
    ref = float(np.median(lvl[: ci - 50]))
    g_even = np.clip(ref - lvl, -LEVEL_EVEN_MAX_DB, LEVEL_EVEN_MAX_DB)
    g_even[ci - 50:] = g_even[ci - 50]
    ks = int(EVEN_SMOOTH_S * 100) | 1
    kh = np.hanning(ks); kh /= kh.sum()
    g_even = np.convolve(np.concatenate([np.full(ks // 2, g_even[0]), g_even, np.full(ks // 2, g_even[-1])]), kh, mode="valid")
    g_even[ci - 50:] = g_even[ci - 50]
    even_db = np.interp(np.arange(n) / hop, np.arange(len(g_even)), g_even)
    pre_even = [round(float(10 * np.log10(pw[i * SR:(i + 1) * SR].mean() + 1e-12)), 1) for i in range(int(chord_film_actual))]
    music *= (10 ** (even_db / 20)).astype(np.float32)[:, None]
    tmp = P / "assets/music/bed_edit_tmp.wav"
    write_wav(tmp, music[:ce])
    gain_db = BED_LUFS - lufs(tmp)[0]
    tmp.unlink(missing_ok=True)
    music *= np.float32(10 ** (gain_db / 20))
    film_rms = [round(float(20 * np.log10(np.sqrt(np.mean(music[i * SR:(i + 1) * SR] ** 2)) + 1e-9)), 1) for i in range(int(total_s))]
    even_ok = film_rms[1:int(chord_film_actual) - 1]
    assert max(even_ok) - min(even_ok) <= 6.0, ("bed not level after evening", film_rms)

    # ---- narration + 'know' lift + ducking -----------------------------------------------------------------------
    narration = np.zeros(n, dtype=np.float32)
    for s in tl["sections"]:
        x = decode(NDIR / f"{s['id']}.wav", 1)[:, 0]
        a = int(round(s["start"] * SR))
        narration[a:a + len(x)] += x[: max(0, n - a)]
    narration_unlifted = narration.copy()   # the duck's voiced mask is computed on the UNLIFTED voice
    kw = word("s5", "know")
    k_on, k_rel = kw["start"], rel_s
    sent_on = word("s5", "so")["start"]
    rmsdb = lambda x: float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12))

    def voiced_rms(x: np.ndarray, a_s: float, b_s: float) -> float:
        """RMS over the 10 ms frames above -45 dBFS (the sentence's speech frames; pauses excluded)"""
        seg = x[int(a_s * SR):int(b_s * SR)]
        m = len(seg) // 480
        fr10 = seg[: m * 480].reshape(m, 480)
        e = np.sqrt((fr10 ** 2).mean(1))
        keep = 20 * np.log10(e + 1e-12) > -45
        return float(20 * np.log10(np.sqrt((fr10[keep] ** 2).mean()) + 1e-12))
    sent_rms_before = voiced_rms(narration, sent_on, k_on)
    know_rms_before = voiced_rms(narration, k_on, k_rel)
    genv = np.clip((t - (k_on - KNOW_GAIN_RAMP_IN_S)) / KNOW_GAIN_RAMP_IN_S, 0, 1) * np.clip((k_rel - t) / KNOW_GAIN_RAMP_OUT_S, 0, 1)
    genv = 0.5 - 0.5 * np.cos(np.pi * genv)
    narration = (narration * (1 + (10 ** (KNOW_GAIN_DB / 20) - 1) * genv)).astype(np.float32)
    know_rms_after = voiced_rms(narration, k_on, k_rel)
    assert know_rms_after >= sent_rms_before - KNOW_MAX_UNDER_SENTENCE_DB, ("lesson 30: 'know' still > 3 dB under its sentence", know_rms_after, sent_rms_before)
    sec, la, lb = KNOW_LIFT_SEC
    s5_0 = next(s["start"] for s in tl["sections"] if s["id"] == sec)
    a, b, e = int((s5_0 + la) * SR), int((s5_0 + lb) * SR), int(END_LIFT_EDGE_S * SR)
    pad = int(0.2 * SR)
    seg = narration[a - pad:b + pad].astype(np.float32)
    band = split_band(seg, 300, 4000)
    env = np.zeros(len(seg), np.float32)
    env[pad:pad + (b - a)] = 1.0
    ramp = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, e))).astype(np.float32)
    env[pad:pad + e] = ramp
    env[pad + (b - a) - e:pad + (b - a)] = ramp[::-1]
    narration[a - pad:b + pad] = seg + (10 ** (END_LIFT_DB / 20) - 1) * band * env
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
    e0 = k_on
    end_env = np.clip((t - (e0 - END_DUCK_IN_S)) / END_DUCK_IN_S, 0, 1)
    end_env = 0.5 - 0.5 * np.cos(np.pi * end_env)
    end_env = np.where(t >= r0, 1 - relr, end_env)
    duck_db = duck_db + END_DUCK_DB * end_env
    att_db = duck_db.copy()
    music_undipped = music.copy()
    texture_duck = duck_curve(TEXTURE_DUCK_DB)

    # ---- SFX ----------------------------------------------------------------------------------------------------
    sd = P / "assets/sfx"

    def fades(x, fin=0.001, fout=0.02):
        a_, b_ = int(fin * SR), int(fout * SR)
        x = x.copy()
        if a_:
            x[:a_] *= np.linspace(0, 1, a_)[:, None]
        x[-b_:] *= np.linspace(1, 0, b_)[:, None]
        return x

    # X7: ONE click of the ratchet + a 1-3 kHz body + HF harmonics (peak 0.158 s -> TICK_PEAK in the cut sample)
    tick_full = decode(sd / "counter_tick.wav", 2)
    full_pk = float(np.argmax(np.abs(tick_full).max(1)) / SR)
    assert abs(full_pk - TICK_PEAK_S) < 0.01, full_pk
    tick_cut = fades(tick_full[int(TICK_CUT[0] * SR):int(TICK_CUT[1] * SR)], 0.002, 0.012)
    tick_b = body(tick_cut, 1000, 3000, 0.55, 31, 0.002)
    tick, tick_mode = with_harmonics(tick_b, db=-1.0, decay_s=0.02)
    tick_peak = float(np.argmax(np.abs(tick).max(1)) / SR)
    assert abs(tick_peak - (TICK_PEAK_S - TICK_CUT[0])) < 0.006, tick_peak
    tick_loud = pitch(tick, -2.0)
    # X1 ember crackle: LF harmonics + a 1-3 kHz crackle body; fades up from frame 0
    ember_raw = decode(sd / "ember_crackle.wav", 2)
    ember, ember_mode = with_harmonics(ember_raw, db=-6.0, decay_s=4.0)
    ember = body(ember, 1000, 3000, 0.6, 11, 0.003)
    ember = fades(ember, 0.6, 0.5)
    # X3 filament: LF harmonics + a 600-2500 Hz body
    fil_raw = decode(sd / "filament_ignite.wav", 2)
    fil, fil_mode = with_harmonics(fil_raw, db=0.0, decay_s=0.25)
    fil = fades(body(fil, 600, 2500, 0.5, 13, 0.004), 0.001, 0.05)
    fil_peak = float(np.argmax(np.abs(fil_raw).max(1)) / SR)
    assert abs(fil_peak - FILAMENT_PEAK_S) < 0.02, fil_peak
    # X2 hiss: HF harmonics + 1-3 kHz body (looped textures)
    hiss_raw = decode(sd / "heat_hiss.wav", 2)
    hiss, hiss_mode = with_harmonics(hiss_raw, db=-3.0, decay_s=3.0)
    hiss = body(hiss, 1000, 3000, 0.5, 17, 0.02)
    # X4 swell: LF harmonics + a rising 800-3000 Hz shimmer body; CREST at 1.109 s (the energy maximum)
    swell_raw = decode(sd / "glow_swell.wav", 2)
    e10 = np.sqrt(np.convolve((swell_raw.astype(np.float64) ** 2).mean(1), np.ones(480) / 480, mode="same"))
    swell_peak = float(np.argmax(e10) / SR)
    assert abs(swell_peak - SWELL_PEAK_S) < 0.08, swell_peak
    swell, swell_mode = with_harmonics(swell_raw, db=-2.0, decay_s=1.5)
    swell = fades(body(swell, 800, 3000, 0.7, 19, 0.03), 0.01, 0.2)
    # X5 hum: HP 40 Hz + LF harmonics (2nd-4th)
    hum_raw = highpass(decode(sd / "reactor_hum.wav", 2), 40.0)
    hum, hum_mode = with_harmonics(hum_raw, db=-6.0, decay_s=4.0)
    hum = body(hum, 300, 3000, 1.5, 29, 0.02)   # QA A-m4: a 300-3000 Hz body so the hum registers on a phone
    # X6 thump: LF harmonics + a 1-4 kHz shimmer tail (decaying 0.35 s)
    thump_raw = decode(sd / "impact_thump.wav", 2)
    thump, thump_mode = with_harmonics(thump_raw, db=-1.0, decay_s=0.15)
    nb = split_band(np.random.default_rng(23).standard_normal(len(thump)).astype(np.float32), 1000, 4000)
    tt = np.arange(len(thump)) / SR
    shimmer = nb * np.exp(-tt / 0.35) * np.clip(tt / 0.004, 0, 1)
    thump = (thump + 0.35 * np.abs(thump).max() * (shimmer / (np.abs(shimmer).max() + 1e-9))[:, None]).astype(np.float32)
    thump_peak = float(np.argmax(np.abs(thump_raw).max(1)) / SR)
    assert abs(thump_peak - THUMP_PEAK_S) < 0.01, thump_peak

    # textures: X2 under the K1 / S2 window, X5 under the K2 window, X2 soft rising under the quark soup
    def texture(x: np.ndarray, a_s: float, b_s: float, f0: int, f1: int, fin: float, fout: float, rise: bool = False) -> np.ndarray:
        dur = (f1 - f0) / FPS
        y = loop_plateau(x, a_s, b_s, dur)
        tt_ = np.arange(len(y)) / SR
        env_ = np.clip(tt_ / fin, 0, 1) * np.clip((dur - tt_) / fout, 0, 1)
        if rise:
            env_ = env_ * (10 ** ((-8 + 8 * np.clip(tt_ / dur, 0, 1)) / 20))
        return (y * env_[:, None]).astype(np.float32)
    hiss_win = texture(hiss, 0.1, 2.6, K["windowOpen"], K["windowClose1"] + 6, 0.5, 0.6)
    hum_win = texture(hum, 0.3, 3.6, K["windowOpen2"], K["colliderXfade"] + 6, 0.5, 0.6)
    hiss_soup = texture(hiss, 0.1, 2.6, K["soupStart"], K["windowClose2"] + 6, 0.8, 0.6, rise=True)

    # (id, name, sample, peak dBFS (pre-master), frame, rule, landing: onset | peak | start, landing offset s)
    pk = lambda x: float(np.argmax(np.abs(x).max(1)) / SR)
    PLACE = [
        ("X1", "ember_bed", ember, -17.0, K["ember"], "frame 0: the crackle bed fades up under the forge frame", "start", 0.0),
        ("X7", "tick_floor", tick, -12.0, K["floorLabelSeat"], "'0 K = -273.15 °C' label SEATED", "peak", tick_peak),
        ("X3", "filament_q", fil, -16.0, K["qStart"], "the filament '?' ignites (soft)", "peak", fil_peak),
        ("X2", "hiss_window", hiss_win, -21.0, K["windowOpen"], "under the K1 / S2 window (texture, low, ducked)", "start", 0.0),
        ("X7", "tick_dv", tick, -12.0, K["dvSeat"], "DV rung SEATED", "peak", tick_peak),
        ("X7", "tick_venus", tick, -12.0, K["venusSeat"], "Venus rung SEATED", "peak", tick_peak),
        ("X4", "swell_sweep", swell, -12.0, K["sunCoreSeat"], "the glow sweep: CREST on the Sun's-core seat", "peak", swell_peak),
        ("X7", "tick_suncore", tick_loud, -13.0, K["sunCoreSeat"], "Sun's-core rung SEATED", "peak", pk(tick_loud)),
        ("X5", "hum_window", hum_win, -14.0, K["windowOpen2"], "under the K2 window (texture, ducked)", "start", 0.0),
        ("X7", "tick_kstar", tick, -12.0, K["kstarSeat"], "KSTAR rung SEATED", "peak", tick_peak),
        ("X6", "thump_beams", thump, -10.0, K["beamFlash"], "the beams meet + FLASH: PEAK on the frame", "peak", thump_peak),
    ]
    for i, f in enumerate(K["lhcGroupSeats"]):
        PLACE.append(("X7", f"tick_lhc{i + 1}", tick, -16.0, f, f"LHC digit group {i + 1} SEATED (light)", "peak", tick_peak))
    PLACE += [
        ("X7", "tick_lhc", tick_loud, -12.0, K["lhcSeat"], "LHC ' K' + label SEATED (louder)", "peak", pk(tick_loud)),
        ("X2", "hiss_soup", hiss_soup, -14.0, K["soupStart"], "under the quark soup (soft, rising)", "start", 0.0),
        ("X3", "filament_planck", fil, -19.0, K["planckMark"], "the Planck mark appears (softer)", "peak", fil_peak),
    ]
    for i, f in enumerate(K["zeroTicks"]):
        PLACE.append(("X7", f"tick_zero{i + 13}", tick, -17.0 if i < 19 else -13.0, f, f"zeros chip -> {i + 13}", "peak", tick_peak))
    PLACE.sort(key=lambda p: p[4])
    sfx = np.zeros((n, 2), dtype=np.float32)
    cues = []
    for xid, name, x, gdb, frame, rule, land, off in PLACE:
        x = x.copy()
        x *= np.float32(10 ** (gdb / 20) / (np.abs(x).max() + 1e-12))
        if land == "onset":
            off = onset_of(x) / SR
        elif land == "start":
            off = 0.0
        at = frame / FPS - off
        lane = np.zeros((n, 2), np.float32)
        place(lane, x, at, fade_out_s=0.01)
        if name in ("hiss_window", "hum_window", "hiss_soup"):
            lane *= (10 ** (texture_duck / 20)).astype(np.float32)[:, None]
        sfx += lane
        cues.append({"id": xid, "name": name, "frame": frame, "seconds": round(frame / FPS, 3), "peak_dbfs": round(gdb, 1),
                     "landing": land, "landing_offset_in_sample_s": round(float(off), 4), "placed_at_s": round(float(at), 4),
                     "rule": rule, "_len": len(x)})
    closing_s = word("s5", "so")["start"]
    assert np.abs(sfx[int((closing_s - 0.05) * SR):]).max() < 1e-6, "an SFX reaches under the closing sentence"
    assert not any(abs(c["frame"] - K["fray"]) < 3 for c in cues), "no SFX on 'breaks'"

    sc_db = np.zeros(n)
    for c in cues:
        p0, p1_ = c["placed_at_s"], c["placed_at_s"] + c["_len"] / SR
        if c["landing"] == "start":   # textures + the ember bed: a soft local bed dip over their span
            env = np.clip((t - p0) / 0.3, 0, 1) * np.clip((p1_ - t) / 0.3, 0, 1)
            sc_db = np.minimum(sc_db, SFX_TEXTURE_DIP_DB * env)
            continue
        if c["id"] == "X4":   # the swell: a -3 dB dip over its body
            env = np.clip((t - p0) / 0.3, 0, 1) * np.clip((p1_ - t) / 0.3, 0, 1)
            sc_db = np.minimum(sc_db, -3.0 * env)
            continue
        s0 = c["seconds"] - 0.03 - (0.06 if c["landing"] == "peak" else 0.0)
        dur = 0.12 if c["id"] == "X7" else 0.25
        env = np.clip((t - s0) / 0.02, 0, 1) * np.clip(1 - (t - (s0 + dur)) / 0.1, 0, 1)
        sc_db = np.minimum(sc_db, SFX_SIDECHAIN_DB * np.where(t < s0, 0, env))
    att_db = att_db + sc_db

    # ---- final fade, then no dead air: ease the duck back where the mix < floor ---------------------------------------
    fade = np.ones(n, np.float32)
    nf = int(FINAL_FADE_S * SR)
    nr = int(0.010 * SR)
    ffl = 10 ** (FINAL_FADE_FLOOR_DB / 20)
    fade[-nf:-nr] = ffl + (1 - ffl) * np.cos(np.linspace(0, np.pi / 2, nf - nr)) ** 2
    fade[-nr:] = ffl * np.linspace(1, 0, nr)
    voice2 = np.repeat(narration[:, None], 2, axis=1)
    hop_ = SR // 100
    w_ = 10
    lift_db = np.zeros(n // hop_ + 1)
    music = music_undipped * (10 ** (att_db / 20)).astype(np.float32)[:, None]
    lift = np.zeros(n)
    for _ in range(3):
        mix_ = music + sfx + voice2
        m64 = mix_.astype(np.float64)
        lv = lambda pw_: 10 * np.log10(np.convolve(pw_[: (n // hop_) * hop_].reshape(-1, hop_).mean(axis=1), np.ones(w_) / w_, mode="same") + 1e-12)
        lvl_ = lv(np.minimum((m64 ** 2).mean(axis=1), m64.mean(axis=1) ** 2))
        lvl_ch = lv(np.minimum(m64[:, 0] ** 2, m64[:, 1] ** 2))
        need = np.maximum.reduce([np.zeros_like(lvl_), FLOOR_PRE_DBFS - lvl_, FLOOR_CH_PRE_DBFS - lvl_ch])
        need[(n - nf) // hop_ - 5:] = 0
        need[int((e0 - END_DUCK_IN_S) * 100): int(chord_film_actual * 100) + 1] = 0   # no floor lift under 'know.' (lesson 18 wins; -42 still asserted)
        need = np.maximum.reduce([np.roll(need, k) for k in range(-12, 13)])
        kern = np.hanning(31)
        kern /= kern.sum()
        need = np.convolve(need, kern, mode="same")
        lift_db[: len(need)] = np.minimum(lift_db[: len(need)] + need, -np.interp(np.arange(len(need)) * hop_, np.arange(n), att_db))
        lift = np.interp(np.arange(n) / hop_, np.arange(len(lift_db)), lift_db)
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

    # the limiter's action on 'know.' (final vs the un-limited mix at the same master gain): must be ~0 (a lift, not a limiter)
    ta, tb = int(k_on * SR), int(k_rel * SR)
    ref_ = np.abs(mix_pre[ta:tb] * np.float32(10 ** (gain_total / 20))).max(axis=1) + 1e-9
    red = 20 * np.log10(np.maximum(np.abs(mix[ta:tb]).max(axis=1), 1e-9) / ref_)
    lim_know_db = round(float(np.min(red[ref_ > 1e-3])), 2)

    # ---- checks on the FINAL premix -------------------------------------------------------------------------------
    rms_db = lambda x: float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9))
    g_lin = np.float32(10 ** (gain_total / 20))
    bed_final = music * g_lin
    sfx_final = sfx * g_lin
    if os.environ.get("DUMP_SFX"):   # analysis aid (QA A-m4 check): the final SFX lane + bed, premix gain, float32 mono
        sfx_final.mean(axis=1).astype(np.float32).tofile(os.environ["DUMP_SFX"] + "_sfx.f32")
        bed_final.mean(axis=1).astype(np.float32).tofile(os.environ["DUMP_SFX"] + "_bed.f32")
    ph_sfx, ph_bed, ph_voice = split_band(sfx_final, 300, 4000), split_band(bed_final, 300, 4000), split_band(narration * g_lin, 300, 4000)
    for c in cues:
        if c["landing"] == "peak":
            a = int(c["frame"] / FPS * SR) - int(0.075 * SR)
        elif c["landing"] == "start":   # textures: 1.0 s in (the ember: 1.5 s in, its loudest pop)
            a = int((c["placed_at_s"] + (1.5 if c["id"] == "X1" else 1.0)) * SR)
        else:
            a = int(c["frame"] / FPS * SR) - int(0.03 * SR)
        a = max(0, a)
        b = a + int(0.15 * SR)
        d = {"sfx": round(rms_db(ph_sfx[a:b]), 1), "bed": round(rms_db(ph_bed[a:b]), 1), "voice": round(rms_db(ph_voice[a:b]), 1)}
        d["sfx_over_bed_db"] = round(d["sfx"] - d["bed"], 1)
        if c["landing"] in ("onset", "peak"):
            h = int(c["frame"] / FPS * SR) - int(0.015 * SR)
            d["hit_30ms_sfx_over_bed_db"] = round(rms_db(ph_sfx[h:h + int(0.03 * SR)]) - rms_db(ph_bed[h:h + int(0.03 * SR)]), 1)
        q0 = max(0, int(c["placed_at_s"] * SR)); q1 = min(n, q0 + c["_len"])
        w50 = int(0.05 * SR)
        diffs = [rms_db(ph_sfx[i:i + w50]) - rms_db(ph_bed[i:i + w50]) for i in range(q0, max(q0 + 1, q1 - w50), w50)
                 if rms_db(ph_sfx[i:i + w50]) > -70]
        d["win50_max_over_bed_db"] = round(max(diffs), 1) if diffs else None
        d["win50_share_ge_3db"] = round(sum(x >= 3 for x in diffs) / len(diffs), 2) if diffs else None
        c["final_phone_band_dbfs"] = d
        p0 = max(0, int(c["placed_at_s"] * SR))
        p1 = min(n, p0 + c.pop("_len"))
        c["sample_peak_dbfs"] = round(float(20 * np.log10(np.abs(sfx_final[p0:p1]).max() + 1e-12)), 1)
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
    imin = int(np.argmin(np.where(body_, wdb, 99)))
    imin_m = int(np.argmin(np.where(body_, wdbm, 99)))
    min_window = {"min_100ms_rms_dbfs": round(float(wdb[imin]), 1), "at_frame": round(starts[imin] / SR * FPS, 1),
                  "mono_fold_min_100ms_rms_dbfs": round(float(wdbm[imin_m]), 1), "mono_at_frame": round(starts[imin_m] / SR * FPS, 1),
                  "windows_below_minus42": int((wdb[body_] < -42).sum()), "mono_windows_below_minus42": int((wdbm[body_] < -42).sum()),
                  "final_fade": {"seconds": FINAL_FADE_S, "min_100ms_rms_dbfs": round(float(wdb.min()), 1)},
                  "note": "10 ms hop over the whole film; the last FINAL_FADE_S excluded"}
    assert min_window["windows_below_minus42"] == 0 and min_window["mono_windows_below_minus42"] == 0, min_window
    assert wdb.min() >= -42, ("the final fade window dips under -42 dBFS", float(wdb.min()))
    assert wdbm.min() >= -41, ("the final fade window (mono fold) dips under -41 dBFS: keep 1 dB for the AAC master", float(wdbm.min()))
    chord_meas = measured_onset(bed_final.mean(axis=1), chord_film_actual, 0.06)
    parts = {}
    for k_, (a_s, b_s) in KNOW_PARTS.items():
        a, b = int((s5_0 + a_s) * SR), int((s5_0 + b_s) * SR)
        parts[k_] = {"window_film_s": [round(s5_0 + a_s, 3), round(s5_0 + b_s, 3)], "voice": round(rms_db(ph_voice[a:b]), 1), "bed": round(rms_db(ph_bed[a:b]), 1)}
        parts[k_]["voice_over_bed_db"] = round(parts[k_]["voice"] - parts[k_]["bed"], 1)
    a, b = int((rel_s - 0.20) * SR), int((rel_s - 0.02) * SR)
    parts["breathy tail (last 180 ms voiced)"] = {"window_film_s": [round(rel_s - 0.20, 3), round(rel_s - 0.02, 3)], "voice": round(rms_db(ph_voice[a:b]), 1), "bed": round(rms_db(ph_bed[a:b]), 1)}
    parts["breathy tail (last 180 ms voiced)"]["voice_over_bed_db"] = round(parts["breathy tail (last 180 ms voiced)"]["voice"] - parts["breathy tail (last 180 ms voiced)"]["bed"], 1)
    margin = min(parts[k_]["voice_over_bed_db"] for k_ in KNOW_PARTS)
    assert margin >= MIN_KNOW_MARGIN_DB, ("lesson 18: 'know' under +12 dB over the bed in 300-4000 Hz", parts)
    vmask = np.repeat(voiced, hop)[:n]
    vmask = np.pad(vmask, (0, max(0, n - len(vmask))))
    vm = vmask.astype(bool) & (t < closing_s)
    duck_report = {"target_db": DUCK_DB, "median_bed_attenuation_while_voiced_db": round(float(np.median((att_db + lift)[vm])), 1),
                   "p10_p90_db": [round(float(np.percentile((att_db + lift)[vm], 10)), 1), round(float(np.percentile((att_db + lift)[vm], 90)), 1)]}
    vb = 20 * np.log10(np.sqrt(np.convolve(ph_voice.astype(np.float64) ** 2, np.ones(4800) / 4800, mode="same")[::480]) + 1e-9)
    bb = 20 * np.log10(np.sqrt(np.convolve(ph_bed.mean(axis=1).astype(np.float64) ** 2, np.ones(4800) / 4800, mode="same")[::480]) + 1e-9)
    vmm = vm[::480][: len(vb)]
    duck_report["voice_over_bed_phone_band_median_db"] = round(float(np.median((vb - bb)[vmm & (vb > -40)])), 1)
    vlane = np.abs(narration * g_lin)
    k5 = int(0.005 * SR)
    venv = 20 * np.log10(np.sqrt(np.convolve(vlane ** 2, np.ones(k5) / k5, mode="same")) + 1e-9)
    i60 = int(rel_s * SR) - int(0.3 * SR) + int(np.argmax(venv[int(rel_s * SR) - int(0.3 * SR):] < -60))
    sent_final = voiced_rms(narration * g_lin, sent_on, k_on)
    know_final = voiced_rms(narration * g_lin, k_on, k_rel)
    ending = {
        "release_s": rel_s, "release_frame": rel_f,
        "release_definition": "timeline.json know_end_seconds: the last voiced 10 ms (-40 dB re. the narration max) of s5",
        "voice_tail_below_minus60_dbfs_s": round(i60 / SR, 3),
        "chord": "the bed's own final strong attack (bass to C, C-G-D ringing with E from ~3 s: a C tonic colour over the G pedal); NO IV-V-I exists in this bed (assets_report M1)",
        "chord_src_s": round(chord_src, 4), "chord_film_s": round(chord_film_actual, 4), "chord_measured_on_premix_bed_s": round(chord_meas, 4),
        "chord_after_release_s": round(chord_film_actual - rel_s, 3), "chord_measured_after_release_s": round(chord_meas - rel_s, 3),
        "chord_frame": K["chordFrame"], "duck_release_s": [round(r0, 3), round(r1, 3)],
        "end_duck": {"db": END_DUCK_DB, "from_s": round(e0 - END_DUCK_IN_S, 3), "full_from_s": round(e0, 3), "released_with_main_duck": True},
        "end_lift": {"db": END_LIFT_DB, "band_hz": [300, 4000], "s5_s": list(KNOW_LIFT_SEC[1:])},
        "know_parts_300_4000": parts, "know_min_margin_db": margin,
        "know_broadband_gain": {"db": KNOW_GAIN_DB, "ramp_in_s": KNOW_GAIN_RAMP_IN_S, "ramp_out_s": KNOW_GAIN_RAMP_OUT_S,
                                "window_film_s": [round(k_on - KNOW_GAIN_RAMP_IN_S, 3), round(k_rel, 3)],
                                "voiced_rms_dbfs_before": {"sentence_So_to_we": round(sent_rms_before, 1), "know": round(know_rms_before, 1),
                                                           "know_minus_sentence": round(know_rms_before - sent_rms_before, 1)},
                                "voiced_rms_dbfs_after": {"know": round(know_rms_after, 1), "know_minus_sentence": round(know_rms_after - sent_rms_before, 1)},
                                "final_premix_voiced_rms_dbfs": {"sentence": round(sent_final, 1), "know": round(know_final, 1),
                                                                 "know_minus_sentence": round(know_final - sent_final, 1)},
                                "limiter_max_reduction_on_know_db": lim_know_db},
        "bed_rms_200ms_before_chord_dbfs": round(rms_db(bed_final[ce - int(0.2 * SR): ce]), 1),
        "bed_rms_first_300ms_of_chord_dbfs": round(rms_db(bed_final[ce: ce + int(0.3 * SR)]), 1),
        "mix_rms_by_100ms_after_chord_dbfs": [round(rms_db(mix[ce + i * w100: ce + (i + 1) * w100]), 1) for i in range((n - ce) // w100)],
        "settle_after_chord_s": round(total_s - chord_film_actual, 3),
        "nothing_under_closing_line": "asserted: the SFX lane is silent from 'So' - 0.05 s to the end",
    }
    report = {
        "total_seconds": round(total_s, 4), "total_frames": total_frames, "samples": n, "sample_rate": SR, "channels": 2,
        "narration_source": "assets/audio/narration/clean/sN.wav (THE CLEAN WAVs, process_narration.py)",
        "frames": K,
        "motion": {"SEAT_F": SEAT_F, "FLOOR_DRAW_F": FLOOR_DRAW_F, "CAM_TILT_F": CAM_TILT_F, "CAM_RETURN_F": CAM_RETURN_F, "Q_DRAW_F": Q_DRAW_F,
                   "SPINE_DRAW_F": SPINE_DRAW_F, "WINDOW_OPEN_F": WINDOW_OPEN_F, "MEDIA_XFADE_F": MEDIA_XFADE_F, "LUT_F": LUT_F,
                   "ZOOM_F": ZOOM_F, "COMPRESS_F": COMPRESS_F, "DRIFT_F": DRIFT_F, "DIM_F": DIM_F, "Q_DIM_F": Q_DIM_F, "Q_FADE_F": Q_FADE_F,
                   "FRAY_F": FRAY_F, "SETTLE_GLOW_F": SETTLE_GLOW_F},
        "music": {"source": "assets/music/bed_raw.mp3", "key": "C major (asked D: lesson 26); NO IV-V-I: the figure stops over a G pedal, its last strong attack = the final chord",
                  "grid": {"t0_s": GRID0_S, "step_s": GRID_S, "k": kgrid, "grid_trim_s": round(grid_trim, 4)},
                  "trim_src_s": round(trim_src, 4), "wanted_trim_s": round(want_trim, 4),
                  "chord_src_s": round(chord_src, 4), "resample": {"decode_rate": out_rate, "speed": round(speed, 6), "cents": round(float(cents), 2)},
                  "level_evening": {"max_db": LEVEL_EVEN_MAX_DB, "smooth_s": EVEN_SMOOTH_S, "ref_db": round(ref, 1),
                                    "gain_range_db": [round(float(even_db.min()), 2), round(float(even_db.max()), 2)],
                                    "bed_film_1s_dbfs_before_evening": pre_even},
                  "bed_film_1s_rms_dbfs_pre_mix_gain": film_rms, "bed_gain_db": round(gain_db, 2), "bed_lufs_target": BED_LUFS,
                  "ducking": {"under_speech_db": DUCK_DB, "attack_ms": 120, "release_ms": 400, "hold_ms": 250,
                              "release_before_chord": "linear from the release of 'know.' to the chord - 20 ms", "measured": duck_report},
                  "ring_out": "the bed's own natural ~5 s decay after the attack (no synthetic tail); final fade " + str(FINAL_FADE_S) + " s"},
        "ending": ending,
        "sfx_processing": {"X1": f"with_harmonics: {ember_mode} + a 1-3 kHz crackle body; 0.6 s fade-in from frame 0",
                           "X2": f"with_harmonics: {hiss_mode} + a 1-3 kHz body; 0.1-2.6 s plateau looped; ducked {TEXTURE_DUCK_DB} dB under speech",
                           "X3": f"with_harmonics: {fil_mode} + a 600-2500 Hz body; PEAK {fil_peak:.3f} s aligned",
                           "X4": f"with_harmonics: {swell_mode} + an 800-3000 Hz shimmer body; CREST {swell_peak:.3f} s aligned",
                           "X5": f"HP 40 Hz; with_harmonics: {hum_mode} + a 300-3000 Hz body; 0.3-3.6 s plateau looped; ducked {TEXTURE_DUCK_DB} dB under speech",
                           "X6": f"with_harmonics: {thump_mode} + a 1-4 kHz shimmer tail (0.35 s); PEAK {thump_peak:.3f} s aligned",
                           "X7": f"ONE click cut {TICK_CUT} s from the 8-click ratchet (transient {TICK_PEAK_S} s) + a 1-3 kHz body + with_harmonics: {tick_mode}; louder variant -2 st",
                           "X8": "spare: not used"},
        "sfx": cues,
        "master_gain_db": round(gain_total, 2),
        "limiter": {"threshold_dbfs": LIMIT_DBFS, "lookahead_ms": 5, "release_ms": 80, "oversampling": 4},
        "floor_lift_max_db": round(floor_lift_max_db, 1),
        "soundtrack_lufs": integ, "soundtrack_true_peak_dbfs": tpk,
        "min_window": min_window,
        "note": "Premix at the delivery loudness (-14 LUFS integrated, TP <= -1 dBFS). All anchors from artifacts/timeline.json.",
    }
    (P / "artifacts/soundtrack_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(f"integrated {integ} LUFS, true peak {tpk} dBFS, master gain {gain_total:+.2f} dB")
    print("music", {k: v for k, v in report["music"].items() if k not in ("bed_film_1s_rms_dbfs_pre_mix_gain", "level_evening")})
    print("bed film 1 s rms", film_rms)
    print("ending", {k: v for k, v in ending.items() if k not in ("know_parts_300_4000", "mix_rms_by_100ms_after_chord_dbfs", "know_broadband_gain")})
    print("know gain", ending["know_broadband_gain"])
    for k_, v in parts.items():
        print(f"  {k_:<34} voice {v['voice']:6.1f} bed {v['bed']:6.1f}  +{v['voice_over_bed_db']:.1f} dB")
    for c in cues:
        fb = c["final_phone_band_dbfs"]
        print(f'{c["id"]:<4}{c["name"]:<16} f{c["frame"]:5d}  sfx {fb["sfx"]:6.1f} bed {fb["bed"]:6.1f} (sfx-bed {fb["sfx_over_bed_db"]:+5.1f}, 30ms {fb.get("hit_30ms_sfx_over_bed_db", float("nan")):+5.1f}, 50ms max {fb["win50_max_over_bed_db"]} share>=3 {fb["win50_share_ge_3db"]})  pk {c["sample_peak_dbfs"]:6.1f}')
    print("duck", duck_report, "floor lift max", round(floor_lift_max_db, 1), "min window", min_window)
    print("K", K)


if __name__ == "__main__":
    main()
