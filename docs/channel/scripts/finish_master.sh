#!/usr/bin/env bash
# Master v2 (fixes from the independent master QA):
#  - video: Remotion writes yuvj420p FULL range with the BT.601 (bt470bg) matrix -> convert BOTH range and matrix (accurate_rnd: no 2-level darkening)
#           to BT.709 tv range (v1 converted the range only and mis-tagged 601 data as 709).
#  - audio: built from the frame-aligned premix WAV (public/audio/soundtrack.wav), not Remotion's AAC: no 42.7 ms
#           priming lag, no double AAC encode. One CONSTANT gain to -14 LUFS + a peak limiter (v1's loudnorm fell back
#           to dynamic mode, squashed the hook and its end-of-file flush left a 77 ms timestamp hole at 48.04 s).
#           asetpts=N/SR/TB keeps the timestamps continuous; latency=true removes the limiter's 4 ms lookahead delay.
set -euo pipefail
# Usage: P=projects/<id> RAW=$P/renders/<raw>.mp4 OUT=$P/renders/<id>.mp4 bash finish_master.sh  (WAV defaults to the premix)
P=${P:?set P=/home/user/OpenMontage/projects/<project-id>}
RAW=${RAW:?set RAW=$P/renders/<name>_raw.mp4}
WAV=${WAV:-$P/public/audio/soundtrack.wav}
OUT=${OUT:?set OUT=$P/renders/<project-id>.mp4}

I=$(ffmpeg -hide_banner -i "$WAV" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
G=$(python3 -c "print(round(-14.0 - ($I), 2))")
echo "premix I=$I LUFS -> constant gain ${G} dB"

ffmpeg -loglevel error -y -i "$RAW" -i "$WAV" -map 0:v:0 -map 1:a:0 -map_metadata -1 \
  -vf "scale=in_range=full:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709:flags=accurate_rnd+full_chroma_int,format=yuv420p" \
  -c:v libx264 -preset slow -crf 18 -maxrate 20M -bufsize 25M -profile:v high -level:v 4.0 -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 -g 60 \
  -af "volume=${G}dB,alimiter=limit=0.79:attack=4:release=60:level=false:latency=true,asetpts=N/SR/TB" \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$OUT"

echo "== $OUT"
ffprobe -v error -show_entries stream=codec_name,profile,level,width,height,pix_fmt,color_range,color_space,color_primaries,color_transfer,sample_rate,channels,duration,nb_frames -show_entries format=duration,size,bit_rate -of compact "$OUT"
ffmpeg -v error -err_detect explode -i "$OUT" -f null - && echo "strict decode clean"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | sed -n '/Summary/,$p' | tr -s ' \n' ' '; echo
echo "AAC packet durations (count by duration):"
ffprobe -v error -select_streams a:0 -show_entries packet=duration -of csv=p=0 "$OUT" | sort | uniq -c | sort -rn | head -5
echo "silences >0.7s:"; ffmpeg -hide_banner -i "$OUT" -af silencedetect=n=-45dB:d=0.7 -f null - 2>&1 | grep -E "silence_(start|end)" || echo none
