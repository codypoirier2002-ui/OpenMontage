#!/usr/bin/env bash
# Render stills of LifespanColumn, one at a time (4-core machine).
#   ./still.sh <frame> [<frame> ...]        -> renders/stills/f<NNNN>.png
#   OUT_DIR=/some/dir ./still.sh 300 700    -> custom output directory
#   SCALE=0.5 ./still.sh 300                -> half-size still (faster)
# Frames are ABSOLUTE frames of the composition (props.timeline.total_frames).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSER="$HERE/../../remotion-composer"
LINK="$COMPOSER/projects/how-long-can-anything-last"
OUT_DIR="${OUT_DIR:-$HERE/renders/stills}"
SCALE="${SCALE:-1}"
BROWSER="${REMOTION_BROWSER_EXECUTABLE:-/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell}"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"   # absolute: the render runs from remotion-composer/
if [ ! -L "$LINK" ]; then
  echo "remotion-composer/projects/how-long-can-anything-last is not a symlink (video_compose staged a copy?)." >&2
  echo "Restore: rm -rf \"$LINK\" && ln -s ../../projects/how-long-can-anything-last \"$LINK\"" >&2
  exit 1
fi
cd "$COMPOSER"
for F in "$@"; do
  OUT="$OUT_DIR/f$(printf '%04d' "$F").png"
  npx remotion still projects/how-long-can-anything-last/index.tsx LifespanColumn "$OUT" \
    --frame="$F" --scale="$SCALE" \
    --props=../projects/how-long-can-anything-last/artifacts/props.json \
    --public-dir=../projects/how-long-can-anything-last/public \
    --config=projects/how-long-can-anything-last/remotion.config.ts \
    --browser-executable="$BROWSER" --log=error
  echo "$OUT"
done
