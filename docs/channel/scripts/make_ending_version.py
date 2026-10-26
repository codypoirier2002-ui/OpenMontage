"""Usage: python3 make_ending_version.py <project-id> <last frame of the opening line> <first voiced frame> <bed speed> <dither 0|1>
Then master with finish_master.sh (RAW/WAV pointed at renders/_ending_work/*).

Non-loop 'ending' version of a delivered loop video (no generation, no re-render):
full film + the opening line once more (frames 0..E, the sentence completes) + a 1.5 s hold on the last frame,
the music continuing from the matching point of bed_raw.mp3 and fading out, picture fading to black.
Picture comes from the raw Remotion render and audio from the premix, then the project's own mastering chain runs."""
import subprocess, sys, json
import numpy as np
from pathlib import Path

pid, E, voice_start, speed, noise = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5] == "1"
P = Path("/home/user/OpenMontage/projects") / pid
S = P / "renders/_ending_work"
S.mkdir(parents=True, exist_ok=True)
raw = next(p for p in [P / "renders/dig_raw.mp4", P / "renders/moon_raw.mp4"] if p.exists())
SR, FPS, HOLD = 48000, 30, 1.5


def dec(src, extra=()):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), *extra, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2).copy()


pre = dec(P / "public/audio/soundtrack.wav")
bed = dec(P / "assets/music/bed_raw.mp3", ["-af", f"asetrate={SR * speed},aresample={SR}"] if speed != 1 else [])
# where frame 0 sits in the bed: correlate the music-only lead-in (before the first word) against the bed
lead = pre[: int(voice_start / FPS * SR) - 480].mean(1)
b = bed[: 30 * SR].mean(1)
n = len(lead)
c = np.array([np.dot(lead, b[i:i + n]) / (np.linalg.norm(b[i:i + n]) + 1e-9) for i in range(0, len(b) - n, 48)])
i0 = int(np.argmax(c)) * 48
# refine to the sample
lo, hi = max(0, i0 - 96), i0 + 96
off = lo + int(np.argmax([np.dot(lead, b[i:i + n]) for i in range(lo, hi)]))
gain = np.dot(lead, b[off:off + n]) / np.dot(b[off:off + n], b[off:off + n])
print(f"{pid}: frame 0 = bed sample {off} ({off / SR:.3f} s), bed gain {20 * np.log10(abs(gain)):.1f} dB, corr {c.max():.3f}")

tE = (E + 1) / FPS                      # the appended opening runs frames 0..E inclusive
nE = int(round(tE * SR))
tail_n = int(HOLD * SR)
x_open = pre[:nE].copy()
tail = bed[off + nE: off + nE + tail_n] * gain
xf = 480                                 # 10 ms crossfade from the premix into the music-only tail
w = np.linspace(0, 1, xf)[:, None]
DUCK = 10 ** (-12 / 20)                  # the bed is still ducked under the last word: release it over 0.25 s
x_open[-xf:] = x_open[-xf:] * (1 - w) + bed[off + nE - xf: off + nE] * gain * DUCK * w
rel = int(0.25 * SR)
env = np.ones(tail_n); env[:rel] = DUCK + (1 - DUCK) * np.sin(np.linspace(0, np.pi / 2, rel)) ** 2
tail *= env[:, None]
tail *= np.cos(np.linspace(0, np.pi / 2, tail_n))[:, None] ** 2   # fade out over the hold
out = np.concatenate([pre, x_open, tail]).astype(np.float32)
wav = S / "soundtrack_ending.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(wav)],
               input=out.tobytes(), check=True)

# picture: full raw + raw frames 0..E + E held for HOLD s, fading to black over the last 1.0 s
total = len(pre) / SR
vraw = S / "raw_ending.mp4"
fc = (f"[0:v]split=2[a][b];[b]trim=start_frame=0:end_frame={E + 1},setpts=PTS-STARTPTS,"
      f"tpad=stop_mode=clone:stop_duration={HOLD},fade=t=out:st={tE + HOLD - 1.0:.4f}:d=1.0[o];[a][o]concat=n=2:v=1:a=0[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-filter_complex", fc, "-map", "[v]",
                "-c:v", "libx264", "-crf", "8", "-preset", "fast", "-pix_fmt", "yuvj420p", "-color_range", "pc",
                "-colorspace", "bt470bg", str(vraw)], check=True)
print(json.dumps({"film_s": round(total, 3), "ending_s": round(total + tE + HOLD, 3), "wav": str(wav), "raw": str(vraw)}))
