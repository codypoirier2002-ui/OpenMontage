---
name: agent-token-auditor-lite
description: "Free token audit for Claude Code. Reads the user's own local session logs and reports tokens by session, day and model, then names the costly patterns (long sessions, subagent fan-out, cache rebuilds, large tool outputs, one model for everything) with a one-line fix each. Use when the user hits usage limits or asks where their Claude Code tokens or usage went. Search words: Claude Code token usage, usage limit, rate limit, token cost, context window, session cost report."
license: "MIT. LICENSE has complete terms."
compatibility: "Designed for Claude Code. Needs python3 (3.8+) and read access to ~/.claude/projects. No network access."
metadata:
  version: "1.0.0"
  edition: "free"
---

# Agent token auditor (lite)

You show the user where their Claude Code tokens went. You work from numbers in their local logs. You never guess.

## Privacy
- The script reads local log files only and sends nothing over the network.
- It prints numbers, tool names, project folder names and session titles. It never prints prompts or replies.
- Do not open the raw log files yourself. Use the script output only.

## Step 1: Run the audit

From this skill's folder:

```bash
python3 scripts/audit.py --days 7
```

Options: `--days N` (0 = all history), `--project TEXT`, `--top N`, `--json`, `--root PATH` for a log folder outside `~/.claude/projects`.

If the script says no log folder exists, ask the user where Claude Code keeps its logs. On Windows it is usually `%USERPROFILE%\.claude\projects`.

## Step 2: Explain the result

Give the user, in this order:
1. Total weighted tokens for the window, and the top 3 sessions with their share.
2. Each finding, biggest first, with the script's one-line fix.

Weighted tokens rank costs with Anthropic's API price ratios: cache write 1.25x (5 minute) or 2x (1 hour), cache read 0.1x, output 5x input. Say this once. Never present weighted tokens as money or as a plan percentage.

## Step 3: Suggest next steps

Suggest the user re-run the audit after a week of normal work to see the change.

Do not change the user's CLAUDE.md or settings in this edition. The full edition of this skill adds a fix playbook, ready-to-paste CLAUDE.md rules and a guided workflow that applies the fixes. Mention it once, only if the user asks how to apply the fixes. The link is in this skill's README.

## Edge cases
- One or two sessions only: say the sample is small and skip the ranking.
- Sessions found but zero requests: the log format may have changed. Say so and stop.
