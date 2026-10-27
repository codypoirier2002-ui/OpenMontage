#!/usr/bin/env bash
# preflight.sh - run FIRST in every channel video session, before any plan or paid call (lesson 50 / video 16).
#   bash docs/channel/scripts/preflight.sh [projects/<id>]
# Checks the local tooling the build needs (no tokens, ~5 s) and prints the connector checklist the agent must
# complete by hand: ONE read-only or estimate-only call per paid connector it will spend on. A denial there is a
# connector permission, not quota: stop, tell the user which connector and which tool, and do not retry or top up.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ok=0; bad=0
pass() { echo "PASS  $1"; ok=$((ok+1)); }
fail() { echo "FAIL  $1"; bad=$((bad+1)); }

have() { command -v "$1" >/dev/null 2>&1; }
for t in ffmpeg ffprobe node npx python3; do have "$t" && pass "$t $(command -v "$t")" || fail "$t missing"; done
[ -x "$ROOT/remotion-composer/node_modules/.bin/remotion" ] && pass "remotion cli in remotion-composer" || fail "remotion-composer not installed: cd remotion-composer && npm ci"
CHROME="$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | tail -1)"
[ -n "$CHROME" ] && pass "headless shell $CHROME (pass as --browser-executable; remotion.media is NOT reachable here)" || fail "no Playwright headless shell under /opt/pw-browsers (Remotion would try to download Chrome)"
python3 - <<'PY' && pass "python: numpy scipy PIL faster_whisper" || fail "python modules missing (numpy scipy pillow faster-whisper)"
import numpy, scipy, PIL, faster_whisper
PY
ls -d ~/.cache/huggingface/hub/models--Systran--faster-whisper-small.en >/dev/null 2>&1 && pass "faster-whisper small.en cached (run align with HF_HUB_OFFLINE=1)" || fail "faster-whisper small.en not cached: alignment will try the network"
have fc-list && fc-list 2>/dev/null | grep -qiE "IBM Plex|Saira" && pass "channel fonts installed system-wide" || echo "WARN  channel fonts not system-wide: the project's fetch_fonts.py must reach Google Fonts once (writes public/fonts)"
free_mb=$(df -Pm "$ROOT" | awk 'NR==2{print $4}'); [ "${free_mb:-0}" -gt 1500 ] && pass "disk ${free_mb} MB free" || fail "disk ${free_mb} MB free (< 1500): a full render + master needs ~1.5 GB; delete old renders/review first"
if [ -n "${1:-}" ]; then
  P="$ROOT/$1"
  [ -f "$P/artifacts/script.json" ] && pass "project $1 has artifacts/script.json" || echo "WARN  $1 has no script yet"
  for c in "$P"/checkpoint_*.json; do [ -f "$c" ] || continue
    python3 -c "import json,sys; d=json.load(open('$c')); print(('PASS' if d['status']=='completed' else 'WARN') + '  ' + d['stage'] + ': ' + d['status'] + (' (approved)' if d.get('human_approved') else ''))"
  done
fi
cat <<'TXT'

CONNECTOR CHECKLIST (do by hand, before the proposal; each is one call, read-only or estimate_only):
  - ElevenLabs full connector (images / video / music): creative_list_flows or creative_get_flow_node_types.
      "MCP tool call denied" = per-tool permission on the connector, not credits. Report it; the restricted connector
      (speech + SFX) still works; Creative Claw runs the same image and music models with the user's approval (d-011).
  - ElevenLabs restricted connector (speech + SFX): creative_list_voices.
  - Creative Claw: get_credits_balance, then estimate_generation for one still and one music bed.
  - Anything else the plan will spend on: its cheapest read-only call.
Write the outcome into the proposal's production_plan (provider per asset class, fallback order, unit prices) so a
denial later needs no new approval round. Estimate before every paid batch; one generation per asset; never re-roll.
TXT
echo; echo "preflight: $ok pass, $bad fail"; [ "$bad" -eq 0 ]
