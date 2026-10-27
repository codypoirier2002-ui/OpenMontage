#!/usr/bin/env python3
"""Build the soundtrack premix: narration (+ the lesson-30 lift on 'way') + the ducked, level-evened music bed (its LAST
TONIC attack landing ~0.15 s after 'way.') + the SFX -> public/audio/soundtrack.wav (frame-aligned: exactly total_frames x
1600 samples @ 48 kHz) and artifacts/soundtrack_report.json (video 15's shape: sfx[] rows with frame / placed_at_s /
landing_offset_in_sample_s, frames{}, ending{}, min_window; docs/channel/scripts/qa_auto.py reads them).

Run from the repo root:  python3 projects/how-fast-can-anything-go/build_soundtrack.py

Copied from projects/how-a-cat-lands/build_soundtrack.py (video 15, QA passed; itself videos 12-14). Every film time comes
from artifacts/timeline.json; the only seconds written here are positions INSIDE the source files.

THIS FILE OWNS THE KEY FRAMES (`K`, -> soundtrack_report.json 'frames' -> props.audio -> T.sfx.*): every root curve in
build_props.py (the marker's climbs, the rung seats, the counter ticks, the window plates, the YOU jump, the beam, the energy
bar, the LHC digits, the gap bracket) and every SFX landing derive from them, so a visual and its sound can never drift
apart. A beat that needs a new key frame is a §7 request.

THE MUSIC BED IS NOT GENERATED YET (assets_report M1 'NOT GENERATED'). This script runs WITHOUT it: voice + SFX only, the
bed section skipped with a clear warning, `ending.closing_min_margin_db` left null (qa_auto then falls back to its gap
estimate and WARNs; the number is written from the stems the moment the bed exists). It picks up
assets/music/bed_raw.mp3 AUTOMATICALLY when the file exists:
  * lesson 26: the final cadence is found FROM THE AUDIO: the last strong attack of the file whose tail only decays
    (`last_tonic_attack`), overridable by assets/music/music_qa.json {"last_tonic_attack_s": ...} when the music QA measured it;
  * the head trim = chord_src - (release of 'way.' + CHORD_AFTER_S), snapped to the nearest detected attack within +-0.4 s
    (a beat, so the bed starts on a hit, not mid-note) when that costs <= MAX_CENTS of resampling; otherwise trimmed exactly,
    with no speed change;
  * LEVEL EVENING on 2 s windows (+-LEVEL_EVEN_MAX_DB, smoothed EVEN_SMOOTH_S, frozen 0.5 s before the chord), the bed at
    BED_LUFS (-19) before the duck; DUCK_DB (-12) under narration (120 ms attack, 400 ms release, 250 ms hold);
    CLOSING_DUCK_DB (-13) more from the first word of the closing sentence 'But' (lesson 44), ramped in from 'But' -
    CLOSING_LEAD_S; END_DUCK_DB more under 'way' + a +END_LIFT_DB 300-4000 Hz lift on the word; all released linearly from
    the release of 'way.' to 20 ms before the chord; RING_LIFT_DB on the ring-out from the chord + 0.15 s;
  * FLOOR: where the 100 ms mix level would fall under FLOOR_PRE_DBFS the duck is eased back (never above the undipped bed),
    so no 100 ms window of the premix is under -42 dBFS (lesson 5); never under the closing sentence (lesson 18 wins there).
    WITHOUT A BED this check is DEFERRED (the voice-only premix has silent gaps by construction; reported, not asserted).
THE LIFTS (lesson 30, constant gains on the voice lane, raised-cosine 40 ms in / 30 ms out, never a limiter):
  s5 as a section: S5_GAIN_DB (its clean WAV was true-peak-capped at -22.8 LUFS, the others sit at -21.5: + 1.3 dB);
  'way.' WAY_GAIN_START_DB, raised in 1 dB steps until qa_auto's lesson-30 metric (the loudest 100 ms of 'way' vs the MEDIAN
  of its sentence 'But never all the way.') is <= WAY_MAX_UNDER_DB.
END (lesson 43): cos^2 fade over the last FINAL_FADE_S to FINAL_FADE_FLOOR_DB, then a 10 ms ramp: last 50 ms <= -30 dBFS and
last 20 ms <= -33 dBFS (asserted, qa_auto's thresholds), no click.
SFX (assets/sfx/X*.mp3, 44.1 kHz stereo, decoded to 48 kHz; every transient ON its visible frame, lessons 4 / 14 / 22 / 41).
Phone band (lesson 5; measured in the file analysis):
  X1 whoosh   98 % in 300-4000 Hz, a slow swell: its 10 %-of-peak ONSET (0.167 s) lands on the FIRST MOVING FRAME of a climb
              (the rail draw sc01; the marker's climbs sc02 / sc03 / sc04 / sc07; the YOU jump sc05 at +6 dB).
  X2 boom     96 % < 250 Hz: + with_harmonics (LF saturation) + a 1-3 kHz body; its PEAK (0.221 s) ON the SOUND rung's seat.
  X3 tick     a 10-tick rattle, 99 % > 4 kHz: ONE tick cut TICK_CUT + a 1-3 kHz body + with_harmonics (HF rectification);
              its peak ON every counter step (sc02 x2, sc05 x2, sc08 x4), the energy bar's accelerating ticks (sc10 x6) and
              every LHC digit (sc11 x10).
  X4 hum      a flat 0 dBFS drone, 96 % < 250 Hz: SHAPED (0.4 s in, 0.6 s out, HUM_LEN_S) + harmonics; soft, start-aligned
              on the window's first visible frame (S3, sc06).
  X5 shimmer  99 % > 4 kHz, decaying from its first ms: + harmonics; START-aligned on the beam's first frame (sc08).
  X6 tink     a soft sustained glass tone whose attack IS sample 0 (-31 dBFS peak, 50 % in band): normalised, START-aligned
              on the gap bracket's frame (sc11, 'hair': the marker's final stop; 1.4 s before the closing sentence).
  NOTHING from 50 ms before 'But' (the closing sentence) to the end (asserted on the SFX lane).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

P = Path("projects/how-fast-can-anything-go")
NDIR = P / "assets/audio/narration/clean"
BED = (P / "assets/music/bed_raw.wav") if (P / "assets/music/bed_raw.wav").exists() else (P / "assets/music/bed_raw.mp3")  # lossless WAV preferred when present
MUSIC_QA = P / "assets/music/music_qa.json"
SR = 48000
FPS = 30
CHORD_AFTER_S = 0.15
MAX_CENTS = 8.0
TRIM_SNAP_S = 0.40
BED_LUFS = -19.0
LEVEL_EVEN_MAX_DB = 5.0
LEVEL_WIN_S = 2.0
EVEN_SMOOTH_S = 1.5
DUCK_DB = -12.0
CLOSING_DUCK_DB = -13.0
CLOSING_LEAD_S = 0.55
END_DUCK_DB = -3.0
END_DUCK_IN_S = 0.10
END_LIFT_DB = 3.0
END_LIFT_EDGE_S = 0.02
RING_LIFT_DB = 5.0
S5_GAIN_DB = 1.3           # s5 was true-peak-capped at -22.8 LUFS (others -21.5): ONE constant gain over the section (ramps in the gap before it)
WAY_GAIN_START_DB = 3.0
WAY_GAIN_MAX_DB = 9.0
WAY_MAX_UNDER_DB = 2.5
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
WHOOSH_ONSET_S = 0.167            # 10 % of the peak (file analysis); the peak is at 0.334 s
BOOM_PEAK_S = 0.221
TICK_CUT = (0.258, 0.306)         # one tick of the 10-tick rattle (its rise at 0.262, peak ~0.274)
HUM_LEN_S = 1.6
HUM_IN_S, HUM_OUT_S = 0.40, 0.60
SHIMMER_LEN_S = 1.0
TINK_LEN_S = 1.0
# motion constants shared with build_props.py (it imports this module)
SEAT_F = 8            # a rung label / chip / the readout card drop (gravity ease-in, still moving on seat - 1; T.seat)
WINDOW_OPEN_F = 6     # the window opens (out-quad, first visible frame ON its key frame)
WINDOW_CLOSE_F = 8    # ... and closes (ease-in-out)
XFADE_F = 12          # S1 -> S2 plate crossfade (the tag swaps by a HARD cut at the midpoint, lesson 38)
CLIMB_F = 36          # the longest a rung-to-rung climb takes (it ends ON the seat; a shorter word gap shortens it)
BEAM_F = 12           # the light beam races the whole rail in BEAM_F frames, reaching 'c' ON lightSeat
TICK_STEP_F = 6       # counter steps before a seat (…, seat - 12, seat - 6, seat)
FADE_F = 12           # the lesson-42 exits (mass label, energy bar, orbit inset) fade over FADE_F, ending >= 8 f before the next tab page
DIGIT_STEP_F = 4      # the LHC readout lands one glyph every DIGIT_STEP_F
N_DIGITS = 10         # '99.9999991 %' = 9, 9, ., 9, 9, 9, 9, 9, 9, 1 -> the '.' rides with the 2nd 9, ' %' with the final 1: 10 landings


def key_frames(tl: dict) -> dict:
    """THE KEY FRAMES (props.audio -> T.sfx.*). Every visual landing + its sound is keyed here, from the measured words."""
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

    def on(section: str, text: str, nth: int = 1) -> int:
        hits = [w for w in tl["words"] if w["section"] == section and norm(w["text"]) == norm(text)]
        return int(round(hits[nth - 1]["start"] * FPS))

    sc = {s["id"]: s for s in tl["scenes"]}
    rel_f = tl["way_end_frame"]
    chord_f = int(round((tl["way_end_seconds"] + CHORD_AFTER_S) * FPS))
    page = lambda section, text: on(section, text)        # the caption page carrying a claim starts on its first word
    lhc_page = page("s5", "the")                             # 'The Large Hadron Collider' (the LHC claim's tab, lesson 42)
    probe_page = page("s3", "the")                           # 'The fastest thing we've ever built,' (the PROBE claim's tab)
    cheetah_seat, falcon_seat, sound_seat = on("s1", "hundred", 1), on("s1", "hundred", 2), on("s2", "hundred", 1)
    earth_seat, parker_seat, light_seat = on("s2", "thousand"), on("s3", "thousand"), on("s4", "billion")
    bar_start, bar_off = on("s4", "energy"), on("s4", "end")
    K = {
        # sc01 Walk: the dim rail + the marker at WALK from frame 0; the rail DRAWS bright from 'You' (X1 whoosh onset on its
        # first moving frame); the WALK label seats on 'walk'
        "railDraw": on("s1", "you"),
        "walkSeat": on("s1", "walk"),
        # sc02 Cheetah: the window opens ON the scene start (S1, placeholder until the still lands); the marker climbs from
        # 'cheetah' (X1 onset on the first moving frame) and ARRIVES on 'hundred' (the CHEETAH label seats); the counter steps
        # 0 -> 1 -> 2 (X3 ticks) ending ON the seat
        "windowOpen1": sc["sc02"]["from"],
        "climbCheetah": max(on("s1", "cheetah"), cheetah_seat - CLIMB_F),
        "cheetahSeat": cheetah_seat,
        "cheetahTicks": [cheetah_seat - TICK_STEP_F, cheetah_seat],
        # sc03 Falcon: S1 -> S2 crossfade from the scene start (hard tag swap at the midpoint); climb from 'falcon', seat on
        # 'hundred' (2nd) with the hatched 'commonly cited' chip (PROBABLY); the window closes into sc04
        "plateSwap": sc["sc03"]["from"],
        "climbFalcon": max(on("s1", "falcon"), falcon_seat - CLIMB_F),
        "falconSeat": falcon_seat,
        "windowClose1": sc["sc04"]["from"] - WINDOW_CLOSE_F - 10,   # gone >= 6 f before the SOUND page's tab glide (lessons 42/47; QA A-02)
        # sc04 Sound: climb from 'Sound' (X1), seat ON 'hundred' (X2 soft thump; U1's pressure ring expands from there);
        # counter 2 -> 3 on the seat (no X3 under the thump)
        "climbSound": max(on("s2", "sound"), sound_seat - CLIMB_F),
        "soundSeat": sound_seat,
        # sc05 YouAreFast (HERO): the YOU tag seats at WALK on 'still' (gravity drop, no SFX); it JUMPS with the marker from
        # 'doing' (X1 big whoosh on the first moving frame) and both ARRIVE at EARTH on 'thousand' (label seats; counter
        # 3 -> 4 -> 5, X3 x2); U1's orbit inset draws from 'riding' and is GONE before the PROBE page (lesson 42)
        "youSeat": on("s2", "still"),
        "jumpStart": on("s2", "doing"),
        "earthSeat": earth_seat,
        "earthTicks": [earth_seat - TICK_STEP_F, earth_seat],
        "orbitIn": on("s2", "riding"),
        "orbitOut": probe_page - 8,
        # sc06 Parker: the window opens ON the scene start (S3; X4 hum start-aligned, soft); U1's label 'Parker Solar Probe ·
        # NASA' on 'Parker'
        "windowOpen2": sc["sc06"]["from"],
        "probeLabel": on("s3", "parker"),
        # sc07 Falling: climb from 'reached' (X1), seat ON 'thousand' (PARKER label); U2's arrow 'falling toward the Sun' on
        # 'falling'; the window closes into sc08
        "climbParker": max(on("s3", "reached"), parker_seat - CLIMB_F),
        "parkerSeat": parker_seat,
        "fallArrow": on("s3", "falling"),
        "windowClose2": sc["sc08"]["from"] - WINDOW_CLOSE_F - 10,   # same for the LIGHT page (QA A-03)
        # sc08 Light: the beam races the rail over BEAM_F frames and reaches 'c' ON 'billion' (LIGHT label seats, the c line
        # lights red; X5 shimmer start-aligned on the beam's first frame); counter 5 -> 9 (X3 x4) ending ON the seat
        "beamStart": light_seat - BEAM_F,
        "lightSeat": light_seat,
        "lightTicks": [light_seat - 3 * TICK_STEP_F, light_seat - 2 * TICK_STEP_F, light_seat - TICK_STEP_F, light_seat],
        # sc09 Wall: the marker leaves PARKER on 'nothing' and climbs toward 'c', slowing (no SFX); U2's 'anything with mass'
        # label shares the first moving frame and is GONE before the LHC page (lesson 42)
        "wallStart": on("s4", "nothing"),
        "massLabel": on("s4", "nothing"),
        "massOut": lhc_page - 8,
        # sc10 Energy: 'ENERGY NEEDED' + the drawn curve in on the scene's first word; the bar grows from 'energy', faster and
        # faster (X3 accelerating ticks), OFF the top ON 'end'; everything gone before the LHC page (lesson 42)
        "energyIn": on("s4", "the", 1),
        "barStart": bar_start,
        "barTicks": [bar_start + int(round((bar_off - bar_start) * q)) for q in (0.0, 0.38, 0.64, 0.82, 0.93, 1.0)],
        "barOff": bar_off,
        "energyOut": lhc_page - 8,
        # sc11 LHC (HERO 2): the readout card seats on 'Collider' (no SFX); '99.9999991 %' lands one glyph per DIGIT_STEP_F
        # from 'pushes' (X3 per glyph); the marker's creep ENDS + the gap bracket 'the gap' ON 'hair' (X6 tink)
        "readoutSeat": on("s5", "collider"),
        "digitTicks": [on("s5", "pushes") + i * DIGIT_STEP_F for i in range(N_DIGITS)],
        "creepEnd": on("s5", "hair"),
        "gapBracket": on("s5", "hair"),
        # sc12 NeverAllTheWay: NO SFX from 'But' - 50 ms; release wayEndFrame; chord chordFrame; CTA 4 f after the release
        "closingStart": on("s5", "but"),
        "wayFrame": on("s5", "way"),
        "wayEndFrame": rel_f,
        "chordFrame": chord_f,
        "ctaFrame": rel_f,   # the CTA swaps ON the release so the settle is still from the release (lesson 25; QA A-04)
    }
    # ordering / spacing asserts (the visuals are built on these)
    assert 0 < K["railDraw"] < K["walkSeat"] < K["windowOpen1"] < K["climbCheetah"] < K["cheetahSeat"] < K["plateSwap"], K
    assert K["cheetahTicks"][0] > K["climbCheetah"] and K["cheetahTicks"][-1] == K["cheetahSeat"]
    assert K["plateSwap"] + XFADE_F < K["climbFalcon"] < K["falconSeat"] < K["windowClose1"], K
    assert K["windowClose1"] + WINDOW_CLOSE_F <= K["climbSound"] < K["soundSeat"] < K["youSeat"] < K["jumpStart"] < K["earthSeat"] < K["orbitIn"], K
    assert K["orbitIn"] + 20 < K["orbitOut"] - FADE_F and K["orbitOut"] <= K["windowOpen2"] - 6, K
    assert K["windowOpen2"] < K["probeLabel"] < K["climbParker"] < K["parkerSeat"] < K["fallArrow"] < K["windowClose2"], K
    assert K["windowClose2"] + WINDOW_CLOSE_F <= sc["sc08"]["from"] <= K["beamStart"] < K["lightSeat"] < K["wallStart"], K
    assert K["lightTicks"][0] >= K["beamStart"] - 6 and K["lightTicks"][-1] == K["lightSeat"]
    assert K["wallStart"] < K["energyIn"] < K["barStart"] < K["barOff"] < K["energyOut"] and K["massOut"] == K["energyOut"], K
    assert K["barTicks"][0] == K["barStart"] and K["barTicks"][-1] == K["barOff"] and all(b > a for a, b in zip(K["barTicks"], K["barTicks"][1:]))
    assert K["energyOut"] < K["readoutSeat"] < K["digitTicks"][0] and K["digitTicks"][-1] < K["creepEnd"] == K["gapBracket"] < K["closingStart"], K
    assert K["gapBracket"] + 45 <= K["closingStart"], "the X6 tink (1 s) must end before the closing sentence"
    assert K["closingStart"] < K["wayFrame"] < rel_f <= K["ctaFrame"] < chord_f < tl["total_frames"] - 30, K   # the CTA may swap ON the release (lesson 25)
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
    """Phone layer (lesson 5; video 12-15's function, unchanged). LF mode (the hit has a body, >= 5 % in 25-250 Hz): saturate
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
    a, b = max(0, int((near_s - win_s) * sr)), min(len(x), int((near_s + win_s) * sr))
    seg = x[a:b]
    hop = sr // 1000
    e = np.array([np.sqrt(np.mean(seg[i:i + 5 * hop] ** 2)) + 1e-9 for i in range(0, len(seg) - 5 * hop, hop)])
    d = np.diff(20 * np.log10(e))
    return (a + (int(np.argmax(d)) + 1) * hop) / sr


def attacks(x: np.ndarray, min_rise_db: float = 6.0, sr: int = SR) -> list[tuple[float, float]]:
    """(time, rise dB) of every attack in a mono signal: a 10 ms-RMS rise >= min_rise_db over 30 ms, local maxima only."""
    hop = sr // 100
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9 for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(e)
    rise = db[3:] - db[:-3]
    out = []
    for i in range(1, len(rise) - 1):
        if rise[i] >= min_rise_db and rise[i] >= rise[i - 1] and rise[i] >= rise[i + 1]:
            out.append((round((i + 3) * hop / sr, 3), round(float(rise[i]), 1)))
    return out


def last_tonic_attack(x: np.ndarray, sr: int = SR) -> float:
    """lesson 26: the final cadence FROM THE AUDIO. The last attack in the file after which the 1 s-RMS level only decays
    (a ring-out): the last strong attack (>= 8 dB rise) of the final 10 s, refined to its 1 ms-RMS steepest rise."""
    hop = sr // 100
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9 for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(e)
    tail0 = max(0, len(db) - 1000)
    cands = [t for t, r in attacks(x[tail0 * hop:], 8.0, sr)]
    assert cands, "no attack found in the bed's last 10 s"
    for t in reversed(cands):
        i = int((tail0 * hop) / sr * 100 + t * 100)
        after = db[i + 10:]
        if len(after) > 50 and np.all(np.diff(np.convolve(after, np.ones(50) / 50, mode="valid")) < 0.2):
            return measured_onset(x, tail0 * hop / sr + t, 0.05, sr)
    return measured_onset(x, tail0 * hop / sr + cands[-1], 0.05, sr)


def pitch(x: np.ndarray, semitones: float) -> np.ndarray:
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

    rel_s = tl["way_end_seconds"]
    rel_f = tl["way_end_frame"]
    chord_film_s = rel_s + CHORD_AFTER_S
    K = key_frames(tl)
    hop = SR // 100
    has_bed = BED.exists()
    rms_db = lambda x: float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9))

    # ---- music bed (only when it exists): the last tonic FROM THE AUDIO, trimmed so it lands at release + 0.15 ------------
    music_report: dict = {"source": None, "status": "NO BED: assets/music/bed_raw.mp3 is missing (M1 not generated). Voice + SFX only; rerun this script when it lands."}
    music_undipped = np.zeros((n, 2), np.float32)
    chord_film_actual = chord_film_s
    even_db = np.zeros(n)
    gain_db = 0.0
    if has_bed:
        bed44 = decode(BED, 1)[:, 0]
        qa = json.loads(MUSIC_QA.read_text()) if MUSIC_QA.exists() else {}
        chord_src = measured_onset(bed44, qa["last_tonic_attack_s"], 0.05) if "last_tonic_attack_s" in qa else last_tonic_attack(bed44)
        want_trim = chord_src - chord_film_s
        assert want_trim >= 0, ("the bed is too short to reach the chord: its last tonic sits before the film's release", chord_src, chord_film_s)
        near = [a for a, _ in attacks(bed44, 6.0) if abs(a - want_trim) <= TRIM_SNAP_S]
        best = None
        for a in near:
            sp = (chord_src - a) / chord_film_s
            c = 1200 * np.log2(sp)
            if abs(c) <= MAX_CENTS and (best is None or abs(c) < abs(best[1])):
                best = (a, c)
        if best:
            trim_src, cents = best[0], best[1]
            trim_how = f"snapped to the bed's attack at src {trim_src:.3f} s ({len(near)} attacks within +-{TRIM_SNAP_S} s)"
        else:
            trim_src, cents = want_trim, 0.0
            trim_how = "exact trim (no attack within the cents budget); 30 ms fade-in"
        speed = (chord_src - trim_src) / chord_film_s
        out_rate = int(round(SR / speed))
        speed = SR / out_rate
        cents = 1200 * np.log2(speed)
        assert abs(cents) <= MAX_CENTS, ("speed change beyond a few cents", cents)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(BED), "-ac", "2", "-af",
                              f"aresample={out_rate}:resampler=soxr:precision=28", "-f", "f32le", "-"], capture_output=True, check=True).stdout
        src = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
        a0 = int(round(trim_src * out_rate)) - int(0.002 * out_rate)
        bed = src[max(0, a0):].copy()
        if len(bed) < n:
            # the bed's ring-out ends a little before the film does: pad with silence only when the shortfall is < 1 s and the
            # bed's last 50 ms are already quiet (<= -40 dBFS), so the pad continues a decay that is effectively over
            short_s = (n - len(bed)) / SR
            tail_db = 20 * np.log10(np.sqrt(np.mean(bed[-int(0.05 * SR):] ** 2)) + 1e-12)
            assert short_s < 1.0 and tail_db <= -40.0, ("the bed is shorter than the film", len(bed) / SR, total_s, tail_db)
            print(f"NOTE: bed ends {short_s:.3f} s before the film; its last 50 ms are {tail_db:.1f} dBFS; padded with silence")
            bed = np.concatenate([bed, np.zeros((n - len(bed), 2), np.float32)])
        fi = int((0.008 if best else 0.03) * SR)
        bed[:fi] *= np.linspace(0, 1, fi)[:, None]
        music = bed[:n].copy()
        chord_film_actual = (int(round(chord_src * out_rate)) - a0) / SR
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
        music_undipped = music.copy()
        music_report = {"source": str(BED.relative_to(P)), "status": "bed present",
                        "cadence": "the LAST TONIC attack found from the audio (last_tonic_attack; music_qa.json override if present), lesson 26",
                        "chord_src_s": round(chord_src, 4), "wanted_trim_s": round(want_trim, 4), "trim_src_s": round(trim_src, 4), "trim_how": trim_how,
                        "resample": {"decode_rate": out_rate, "speed": round(speed, 6), "cents": round(float(cents), 2)},
                        "level_evening": {"window_s": LEVEL_WIN_S, "max_db": LEVEL_EVEN_MAX_DB, "smooth_s": EVEN_SMOOTH_S, "ref_db": round(ref, 1),
                                          "gain_range_db": [round(float(even_db.min()), 2), round(float(even_db.max()), 2)], "bed_film_2s_dbfs_before_evening": pre_even},
                        "bed_film_2s_rms_dbfs_pre_mix_gain": film_rms2, "bed_gain_db": round(gain_db, 2), "bed_lufs_target": BED_LUFS,
                        "ducking": {"under_speech_db": DUCK_DB, "attack_ms": 120, "release_ms": 400, "hold_ms": 250}}
    else:
        print("WARNING: no music bed (assets/music/bed_raw.mp3 missing): building the premix with voice + SFX only; the bed section is skipped.")

    # ---- narration + the lesson-30 lift --------------------------------------------------------------------------
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
    s5sec = next(x for x in tl["sections"] if x["id"] == "s5")
    s5w = [x for x in tl["words"] if x["section"] == "s5"]
    s5env = np.clip((t - (s5w[0]["start"] - 0.25)) / 0.2, 0, 1)
    assert s5w[0]["start"] - 0.25 > s5sec["start"] - 1.45, "the s5 gain ramp must sit in the gap before s5"
    narration = (narration * (1 + (10 ** (S5_GAIN_DB / 20) - 1) * s5env)).astype(np.float32)
    i_but = max(i for i, x in enumerate(s5w[:-1]) if x["text"].rstrip().endswith((".", "?", "!", ":"))) + 1
    sent = s5w[i_but:]
    assert sent[0]["text"] == "But" and sent[-1]["text"] == "way.", sent
    ww = word("s5", "way")
    lifted_base = narration.copy()
    way_gain = WAY_GAIN_START_DB
    while True:
        cand = (lifted_base * (1 + (10 ** (way_gain / 20) - 1) * gain_env(ww["start"], rel_s))).astype(np.float32)
        pk = [peak100(cand, x["start"], x["end"]) for x in sent]
        under = float(np.median(pk)) - pk[-1]
        if under <= WAY_MAX_UNDER_DB or way_gain >= WAY_GAIN_MAX_DB:
            break
        way_gain += 1.0
    narration = cand
    pk_before = [peak100(narration_unlifted, x["start"], x["end"]) for x in sent]
    way_metric = {"metric": "qa_auto lesson 30: loudest 100 ms of 'way.' vs the median of its sentence's words (voice lane)",
                  "gain_db": way_gain, "span_film_s": [round(ww["start"] - GAIN_RAMP_IN_S, 3), round(rel_s, 3)],
                  "words": [x["text"] for x in sent], "peak100_before_dbfs": [round(v, 1) for v in pk_before],
                  "peak100_after_dbfs": [round(v, 1) for v in pk], "way_under_median_before_db": round(float(np.median(pk_before)) - pk_before[-1], 1),
                  "way_under_median_after_db": round(under, 1)}
    assert under <= 3.0, ("lesson 30: 'way' still > 3 dB under its sentence median", way_metric)
    g_on = ww["start"]
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
    but_on = word("s5", "but")["start"]
    cl_env = np.clip((t - (but_on - CLOSING_LEAD_S)) / (CLOSING_LEAD_S - 0.15), 0, 1)
    cl_env = np.where(t >= r0, 1 - relr, 0.5 - 0.5 * np.cos(np.pi * cl_env))
    duck_db = duck_db + CLOSING_DUCK_DB * cl_env
    end_env = np.clip((t - (g_on - END_DUCK_IN_S)) / END_DUCK_IN_S, 0, 1)
    end_env = np.where(t >= r0, 1 - relr, 0.5 - 0.5 * np.cos(np.pi * end_env))
    duck_db = duck_db + END_DUCK_DB * end_env
    att_db = duck_db.copy()

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
    whoosh = fades(decode(sd / "X1_whoosh.mp3", 2), 0.002, 0.05)
    w_on = onset_of(whoosh) / SR
    assert abs(w_on - WHOOSH_ONSET_S) < 0.01, ("X1 onset moved", w_on)
    boom_raw = decode(sd / "X2_boom.mp3", 2)
    assert abs(pk_(boom_raw) - BOOM_PEAK_S) < 0.01, pk_(boom_raw)
    boom_b = body(boom_raw, 1000, 3000, 1.4, 31, 0.004)
    boom, boom_mode = with_harmonics(boom_b, db=-2.0, decay_s=0.10)
    tick_full = decode(sd / "X3_tick.mp3", 2)
    tick_cut = fades(tick_full[int(TICK_CUT[0] * SR):int(TICK_CUT[1] * SR)], 0.001, 0.02)
    tick_b = body(tick_cut, 1000, 3000, 1.2, 37, 0.003)
    tick, tick_mode = with_harmonics(tick_b, db=-2.0, decay_s=0.03)
    tick_peak = pk_(tick)
    assert 0.006 < tick_peak < 0.03, ("the tick's peak is not near the cut's start", tick_peak)
    hum_raw = decode(sd / "X4_hum.mp3", 2)[: int(HUM_LEN_S * SR)]
    henv = np.minimum(np.clip(np.arange(len(hum_raw)) / (HUM_IN_S * SR), 0, 1), np.clip((len(hum_raw) - np.arange(len(hum_raw))) / (HUM_OUT_S * SR), 0, 1))
    henv = (0.5 - 0.5 * np.cos(np.pi * henv)).astype(np.float32)
    hum, hum_mode = with_harmonics((hum_raw * henv[:, None]).astype(np.float32), db=-8.0, decay_s=HUM_LEN_S)
    shimmer_raw = fades(decode(sd / "X5_shimmer.mp3", 2)[: int(SHIMMER_LEN_S * SR)], 0.001, 0.05)
    shimmer, shimmer_mode = with_harmonics(shimmer_raw, db=-6.0, decay_s=0.5)
    whoosh_h, whoosh_h_mode = with_harmonics(whoosh, db=-4.0, decay_s=0.6)   # the opening whoosh: in-band harmonics instead of +3 dB broadband, so it does not sit over 'You' (QA A-06)
    tink = fades(decode(sd / "X6_tink.mp3", 2)[: int(TINK_LEN_S * SR)], 0.002, 0.08)
    assert onset_of(tink) < 0.005 * SR, "X6's attack is its first samples (start-aligned)"

    PLACE = [
        ("X1", "rail_draw", whoosh, 2.8, K["railDraw"], "the rail starts drawing bright (sc01, 'You')", "peak", w_on),
        ("X1", "climb_cheetah", whoosh, -6.0, K["climbCheetah"], "the marker's first moving frame toward CHEETAH (sc02)", "peak", w_on),
        ("X3", "tick_cheetah_1", tick, -13.5, K["cheetahTicks"][0], "counter 0 -> 1", "peak", tick_peak),
        ("X3", "tick_cheetah_2", tick, -13.5, K["cheetahTicks"][1], "counter 1 -> 2 ON the CHEETAH seat", "peak", tick_peak),
        ("X1", "climb_falcon", whoosh, -6.0, K["climbFalcon"], "the marker's first moving frame toward FALCON (sc03)", "peak", w_on),
        ("X1", "climb_sound", whoosh, -3.0, K["climbSound"], "the marker's first moving frame toward SOUND (sc04)", "peak", w_on),
        ("X2", "sound_thump", boom, -12.0, K["soundSeat"], "the SOUND rung SEATED: the pressure ring starts (sc04, 'hundred')", "peak", pk_(boom)),
        ("X1", "jump_you", whoosh, -5.0, K["jumpStart"], "the YOU tag + the marker's first moving frame of the jump (sc05, 'doing'; the big whoosh)", "peak", w_on),
        ("X3", "tick_earth_1", tick, -13.5, K["earthTicks"][0], "counter 3 -> 4", "peak", tick_peak),
        ("X3", "tick_earth_2", tick, -13.5, K["earthTicks"][1], "counter 4 -> 5 ON the EARTH seat", "peak", tick_peak),
        ("X4", "hum_probe", hum, -22.0, K["windowOpen2"], "the window's first visible frame (S3, sc06); a soft swell under the plate", "start", 0.0),
        ("X1", "climb_parker", whoosh, -3.0, K["climbParker"], "the marker's first moving frame toward PARKER (sc07)", "peak", w_on),
        ("X5", "beam_shimmer", shimmer, -14.0, K["beamStart"], "the light beam's first frame (sc08); it reaches 'c' on lightSeat", "start", 0.0),
        ("X3", "tick_light_1", tick, -13.5, K["lightTicks"][0], "counter 5 -> 6", "peak", tick_peak),
        ("X3", "tick_light_2", tick, -13.5, K["lightTicks"][1], "counter 6 -> 7", "peak", tick_peak),
        ("X3", "tick_light_3", tick, -13.5, K["lightTicks"][2], "counter 7 -> 8", "peak", tick_peak),
        ("X3", "tick_light_4", tick, -13.5, K["lightTicks"][3], "counter 8 -> 9 ON the LIGHT seat", "peak", tick_peak),
    ] + [("X3", f"tick_bar_{i + 1}", tick, -16.0, f, f"the ENERGY NEEDED bar's accelerating tick {i + 1}/6 (sc10)", "peak", tick_peak) for i, f in enumerate(K["barTicks"])] \
      + [("X3", f"tick_digit_{i + 1}", tick, -14.5, f, f"LHC readout glyph {i + 1}/{N_DIGITS} lands (sc11)", "peak", tick_peak) for i, f in enumerate(K["digitTicks"])] \
      + [("X6", "gap_tink", tink, -16.0, K["gapBracket"], "the marker's final stop + the gap bracket (sc11, 'hair'); before the closing sentence", "start", 0.0)]
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
    closing_s = but_on
    assert np.abs(sfx[int((closing_s - 0.05) * SR):]).max() < 1e-6, "an SFX reaches under the closing sentence"
    sc_db = np.zeros(n)
    for c in cues:
        p0, p1_ = c["placed_at_s"], c["placed_at_s"] + c["_len"] / SR
        if c["landing"] == "start":
            env = np.clip((t - p0) / 0.3, 0, 1) * np.clip((p1_ - t) / 0.3, 0, 1)
            sc_db = np.minimum(sc_db, SFX_TEXTURE_DIP_DB * env)
            continue
        s0 = c["seconds"] - 0.09
        dur = 0.12 if c["id"] == "X3" else 0.3
        env = np.clip((t - s0) / 0.02, 0, 1) * np.clip(1 - (t - (s0 + dur)) / 0.1, 0, 1)
        sc_db = np.minimum(sc_db, SFX_SIDECHAIN_DB * np.where(t < s0, 0, env))
    att_db = att_db + sc_db

    # ---- final fade, then no dead air (the floor lift needs the bed) ---------------------------------------------------
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
    if has_bed:
        for _ in range(3):
            mix_ = music + sfx + voice2
            m64 = mix_.astype(np.float64)
            lv = lambda pw_: 10 * np.log10(np.convolve(pw_[: (n // hop) * hop].reshape(-1, hop).mean(axis=1), np.ones(w_) / w_, mode="same") + 1e-12)
            lvl_ = lv(np.minimum((m64 ** 2).mean(axis=1), m64.mean(axis=1) ** 2))
            lvl_ch = lv(np.minimum(m64[:, 0] ** 2, m64[:, 1] ** 2))
            need = np.maximum.reduce([np.zeros_like(lvl_), FLOOR_PRE_DBFS - lvl_, FLOOR_CH_PRE_DBFS - lvl_ch])
            need[(n - nf) // hop - 5:] = 0
            need[int((but_on - 0.15) * 100): int(chord_film_actual * 100) + 1] = 0
            need = np.maximum.reduce([np.roll(need, k) for k in range(-12, 13)])
            kern = np.hanning(31)
            kern /= kern.sum()
            need = np.convolve(need, kern, mode="same")
            lift_db[: len(need)] = np.minimum(lift_db[: len(need)] + need, -np.interp(np.arange(len(need)) * hop, np.arange(n), att_db))
            tt_ = np.arange(len(lift_db)) * 0.01
            lift_db *= np.where(tt_ >= chord_film_actual, 1.0, np.clip(((but_on - 0.05) - tt_) / 0.15, 0, 1))
            lift = np.interp(np.arange(n) / hop, np.arange(len(lift_db)), lift_db)
            music = music_undipped * (10 ** ((att_db + lift) / 20)).astype(np.float32)[:, None]
    lift = np.interp(np.arange(n) / hop, np.arange(len(lift_db)), lift_db)
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
    lim_way_db = round(float(np.min(red[ref_ > 1e-3])), 2)

    # ---- checks on the FINAL premix -------------------------------------------------------------------------------
    g_lin = np.float32(10 ** (gain_total / 20))
    bed_final = music * g_lin
    sfx_final = sfx * g_lin
    ph_sfx, ph_bed, ph_voice = split_band(sfx_final, 300, 4000), split_band(bed_final, 300, 4000), split_band(narration * g_lin, 300, 4000)
    weak = []
    for c in cues:
        a = max(0, int(c["frame"] / FPS * SR) - int(0.075 * SR)) if c["landing"] == "peak" else int(c["placed_at_s"] * SR)
        b = a + int(0.15 * SR)
        d = {"sfx": round(rms_db(ph_sfx[a:b]), 1), "bed": round(rms_db(ph_bed[a:b]), 1), "voice": round(rms_db(ph_voice[a:b]), 1)}
        d["sfx_over_bed_db"] = round(d["sfx"] - d["bed"], 1) if has_bed else None
        if c["landing"] == "peak":
            h = int((c["placed_at_s"] + c["landing_offset_in_sample_s"]) * SR) - int(0.015 * SR)
            d["hit_30ms_sfx_dbfs"] = round(rms_db(ph_sfx[h:h + int(0.03 * SR)]), 1)
            d["hit_30ms_sfx_over_bed_db"] = round(d["hit_30ms_sfx_dbfs"] - rms_db(ph_bed[h:h + int(0.03 * SR)]), 1) if has_bed else None
        p0 = max(0, int(c["placed_at_s"] * SR))
        p1 = min(n, p0 + c.pop("_len"))
        c["final_phone_band_dbfs"] = d
        c["sample_peak_dbfs"] = round(float(20 * np.log10(np.abs(sfx_final[p0:p1]).max() + 1e-12)), 1)
        if has_bed and c["landing"] == "peak" and d["hit_30ms_sfx_over_bed_db"] < MIN_HIT_OVER_BED_DB:
            weak.append((c["name"], d["hit_30ms_sfx_over_bed_db"]))
    if weak:
        print("WEAK HITS (lesson 5):", weak)
    assert not weak or "--report" in sys.argv, ("lesson 5: hits not over the bed in the phone band", weak)
    sec_lufs = {}
    for x in tl["sections"]:
        a_, b_ = int(x["start"] * SR), int((x["start"] + x["durationInFrames"] / FPS) * SR)
        seg_ = narration[a_:b_].astype(np.float64)
        m_ = len(seg_) // 4800
        fr_ = seg_[: m_ * 4800].reshape(m_, 4800)
        e_ = 10 * np.log10((fr_ ** 2).mean(1) + 1e-12)
        sec_lufs[x["id"]] = round(float(10 * np.log10((fr_[e_ > e_.max() - 25] ** 2).mean() + 1e-12)), 1)
    print("voice-lane voiced RMS by section (pre-master dBFS)", sec_lufs)
    assert max(sec_lufs.values()) - min(sec_lufs.values()) <= 2.0, ("sections uneven on the voice lane", sec_lufs)
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
                  "note": "10 ms hop from the end of the 0.5 s lead-in to the start of the final fade (qa_auto's window); the fade is checked by its last 50 / 20 ms"
                          + ("" if has_bed else " - NO BED: the dead-air floor (lesson 5) is DEFERRED until bed_raw.mp3 lands; the voice-only premix has silent gaps by construction")}
    if has_bed:
        assert min_window["windows_below_minus42"] == 0 and min_window["mono_windows_below_minus42"] == 0, min_window
    if has_bed:
        assert last50 <= -30 and last20 <= -33, ("lesson 43: the end is not faded enough", tail)
    assert sum(1 for x_, y_ in zip(tail[-6:], tail[-5:]) if y_ > x_ + 3) == 0, ("the end steps up", tail)
    s5_0 = next(s["start"] for s in tl["sections"] if s["id"] == "s5")
    parts = {}
    for x in sent:
        a, b = int(x["start"] * SR), int(min(x["end"], x["start"] + 0.35) * SR)
        parts[x["text"]] = {"window_s5_s": [round(x["start"] - s5_0, 3), round(x["end"] - s5_0, 3)], "voice": round(rms_db(ph_voice[a:b]), 1),
                            "bed": round(rms_db(ph_bed[a:b]), 1) if has_bed else None}
        parts[x["text"]]["voice_over_bed_db"] = round(parts[x["text"]]["voice"] - parts[x["text"]]["bed"], 1) if has_bed else None
    for k_, (a_s, b_s) in {"way: w + ay (onset + vowel)": (ww["start"], ww["start"] + 0.18), "way: tail": (rel_s - 0.12, rel_s)}.items():
        a, b = int(a_s * SR), int(b_s * SR)
        parts[k_] = {"window_s5_s": [round(a_s - s5_0, 3), round(b_s - s5_0, 3)], "voice": round(rms_db(ph_voice[a:b]), 1),
                     "bed": round(rms_db(ph_bed[a:b]), 1) if has_bed else None}
        parts[k_]["voice_over_bed_db"] = round(parts[k_]["voice"] - parts[k_]["bed"], 1) if has_bed else None
    margin = min(v["voice_over_bed_db"] for k_, v in parts.items() if k_ != "way: tail") if has_bed else None
    if has_bed:
        assert margin >= MIN_LAST_MARGIN_DB, ("lesson 18: the closing sentence under +12 dB over the bed in 300-4000 Hz", parts)
    vm = np.repeat(voiced, hop)[:n]
    vm = np.pad(vm, (0, max(0, n - len(vm)))).astype(bool) & (t < closing_s)
    duck_report = {"target_db": DUCK_DB, "median_bed_attenuation_while_voiced_db": round(float(np.median((att_db + lift)[vm])), 1),
                   "p10_p90_db": [round(float(np.percentile((att_db + lift)[vm], 10)), 1), round(float(np.percentile((att_db + lift)[vm], 90)), 1)],
                   "applies": has_bed}
    chord_meas = measured_onset(bed_final.mean(axis=1), chord_film_actual, 0.06) if has_bed else None
    ending = {
        "release_s": rel_s, "release_frame": rel_f,
        "release_definition": "timeline.json way_end_seconds: the last voiced 10 ms (-40 dB re. the narration max) of s5 (the end of 'way')",
        "chord": ("the bed's LAST TONIC attack found from the audio (lesson 26)" if has_bed else
                  "NO BED YET: chord_frame is the planned release + 0.15 s; the bed's last tonic will be aligned to it (lesson 26) when bed_raw.mp3 lands"),
        "chord_film_s": round(chord_film_actual, 4), "chord_measured_on_premix_bed_s": round(chord_meas, 4) if chord_meas else None,
        "chord_after_release_s": round(chord_film_actual - rel_s, 3), "chord_frame": K["chordFrame"],
        "duck_release_s": [round(r0, 3), round(r1, 3)],
        "closing_duck": {"db": CLOSING_DUCK_DB, "ramp_from_s": round(but_on - CLOSING_LEAD_S, 3), "full_from_s": round(but_on - 0.15, 3), "from_word": "But (lesson 44)"},
        "end_duck": {"db": END_DUCK_DB, "from_s": round(g_on - END_DUCK_IN_S, 3)},
        "end_lift": {"db": END_LIFT_DB, "band_hz": [300, 4000], "film_s": [round(g_on - 0.01, 3), round(rel_s + 0.01, 3)]},
        "ring_lift": {"db": RING_LIFT_DB, "from_s": round(chord_film_actual + 0.15, 3)},
        "way_lift": way_metric, "s5_section_gain_db": S5_GAIN_DB,
        "closing_words_300_4000": parts, "closing_min_margin_db": margin,
        "closing_min_margin_note": None if has_bed else "no bed: not measurable from the stems yet; written as a number (>= 12 asserted) when bed_raw.mp3 lands (lesson 49)",
        "limiter_max_reduction_on_way_db": lim_way_db,
        "mix_rms_by_100ms_after_chord_dbfs": [round(rms_db(mix[int(chord_film_actual * SR) + i * w100: int(chord_film_actual * SR) + (i + 1) * w100]), 1) for i in range((n - int(chord_film_actual * SR)) // w100)],
        "settle_after_chord_s": round(total_s - chord_film_actual, 3),
        "nothing_under_closing_line": "asserted: the SFX lane is silent from 'But' - 0.05 s to the end",
    }
    report = {
        "total_seconds": round(total_s, 4), "total_frames": total_frames, "samples": n, "sample_rate": SR, "channels": 2,
        "narration_source": "assets/audio/narration/clean/sN.wav (THE CLEAN WAVs, process_narration.py)",
        "bed_present": has_bed,
        "frames": K,
        "motion": {"SEAT_F": SEAT_F, "WINDOW_OPEN_F": WINDOW_OPEN_F, "WINDOW_CLOSE_F": WINDOW_CLOSE_F, "XFADE_F": XFADE_F, "CLIMB_F": CLIMB_F,
                   "BEAM_F": BEAM_F, "TICK_STEP_F": TICK_STEP_F, "FADE_F": FADE_F},
        "music": {**music_report, "ducking_measured": duck_report},
        "ending": ending,
        "sfx_processing": {"X1": f"as is (98 % in band); its 10 %-of-peak onset ({w_on:.3f} s) on the first moving frame", "X2": f"+ 1-3 kHz body + with_harmonics: {boom_mode}; peak {BOOM_PEAK_S} s on the seat",
                           "X3": f"ONE tick cut {TICK_CUT} s + 1-3 kHz body + with_harmonics: {tick_mode}; peak {tick_peak:.3f} s in the cut",
                           "X4": f"shaped {HUM_LEN_S} s ({HUM_IN_S} s in / {HUM_OUT_S} s out) + with_harmonics: {hum_mode}; start-aligned", "X5": f"0-{SHIMMER_LEN_S} s + with_harmonics: {shimmer_mode}; start-aligned",
                           "X6": f"0-{TINK_LEN_S} s normalised, its attack is sample 0; start-aligned"},
        "sfx": cues,
        "master_gain_db": round(gain_total, 2),
        "limiter": {"threshold_dbfs": LIMIT_DBFS, "lookahead_ms": 5, "release_ms": 80, "oversampling": 4},
        "floor_lift_max_db": round(floor_lift_max_db, 1),
        "soundtrack_lufs": integ, "soundtrack_true_peak_dbfs": tpk,
        "voice_rms_by_section_dbfs": sec_lufs,
        "min_window": min_window,
        "note": "Premix at the delivery loudness (-14 LUFS integrated, TP <= -1 dBFS). All anchors from artifacts/timeline.json."
                + ("" if has_bed else " NO BED (M1 pending): voice + SFX only; rerun after assets/music/bed_raw.mp3 lands."),
    }
    (P / "artifacts/soundtrack_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(f"integrated {integ} LUFS, true peak {tpk} dBFS, master gain {gain_total:+.2f} dB; bed: {'present' if has_bed else 'NONE'}")
    print("chord film", round(chord_film_actual, 3), "after release", round(chord_film_actual - rel_s, 3), "But", round(but_on, 3))
    print("way", way_metric["gain_db"], "dB, under median", way_metric["way_under_median_before_db"], "->", way_metric["way_under_median_after_db"])
    for k_, v in parts.items():
        print(f"  {k_:<30} voice {v['voice']:6.1f} bed {v['bed']}  over {v['voice_over_bed_db']}")
    for c in cues:
        fb = c["final_phone_band_dbfs"]
        print(f'{c["id"]:<4}{c["name"]:<16} f{c["frame"]:5d} at {c["placed_at_s"]:7.3f}  band {fb["sfx"]:6.1f}  hit30 {fb.get("hit_30ms_sfx_dbfs")}')
    print("floor lift max", round(floor_lift_max_db, 1), "min window", min_window["min_100ms_rms_dbfs"], "at f", min_window["at_frame"], "tail", tail[-4:])


if __name__ == "__main__":
    main()
