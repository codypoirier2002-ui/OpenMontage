#!/usr/bin/env bash
# Scaffold a new channel video from the kit (docs/channel/kit/template).
#   bash docs/channel/scripts/new_project.sh <project-id> <CompositionName>
# Creates projects/<id>/ with the kit's boilerplate + channel-standard overlay (ids substituted), the folder layout,
# and the remotion-composer/projects/<id> symlink. The foundation agent then writes only the per-video files listed in
# docs/channel/kit/KIT.md (theme.ts, time.ts, types.ts, Composition.tsx, shared/ engines, the build_*.py scripts).
set -euo pipefail
ID="${1:?usage: new_project.sh <project-id> <CompositionName>}"
COMP="${2:?usage: new_project.sh <project-id> <CompositionName>}"
[[ "$ID" =~ ^[a-z0-9-]+$ ]] || { echo "project id must be lowercase-kebab" >&2; exit 1; }
[[ "$COMP" =~ ^[A-Z][A-Za-z0-9]+$ ]] || { echo "composition name must be PascalCase" >&2; exit 1; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
KIT="$ROOT/docs/channel/kit/template"
P="$ROOT/projects/$ID"
LINK="$ROOT/remotion-composer/projects/$ID"
[ -e "$P/theme.ts" ] && { echo "$P already has a build (theme.ts); not overwriting" >&2; exit 1; }
mkdir -p "$P"/{artifacts,assets/{audio/narration,images,video,music,sfx},public/{audio,stills,fonts},renders/review,scenes,shared,overlay}
cp -r --update=none "$KIT"/. "$P"/
grep -rlZ -e __PID__ -e __COMP__ "$P" --include="*.ts" --include="*.tsx" --include="*.json" --include="*.cjs" --include="*.sh" |
  xargs -0 -r sed -i "s/__PID__/$ID/g; s/__COMP__/$COMP/g"
chmod +x "$P/still.sh" "$P/stills.cjs"
[ -L "$LINK" ] || ln -s "../../projects/$ID" "$LINK"
echo "scaffolded $P (composition $COMP), symlink $LINK"
echo "next: write theme.ts / time.ts / types.ts / Composition.tsx / shared engines per docs/channel/kit/KIT.md"
