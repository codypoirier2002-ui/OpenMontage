# agent-token-auditor-lite

See where your Claude Code tokens go. Free.

This skill reads your own local Claude Code session logs. It ranks your sessions by cost and names the habits that cost the most, with a one-line fix for each.

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

As a Claude Code plugin, from inside Claude Code:

```text
/plugin install agent-token-auditor-lite --marketplace MalikKhaledSaid/agent-skills
```

Or copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` in a project. Then ask your agent: "Audit my token use for the last 7 days."

You can also run the script by hand:

```bash
python3 scripts/audit.py --days 7
```

## What the report shows
- Totals: input, cache write, cache read and output tokens, plus weighted tokens.
- Your top sessions by share, with peak context and subagent share.
- Use by day and by model.
- Findings, biggest first: long sessions, subagent fan-out, cache rebuilds, large tool outputs, one model for everything.

## Privacy
- Reads files under `~/.claude/projects` only. Sends nothing anywhere.
- Prints numbers, tool names, project folder names and session titles. It never prints your prompts or replies.

## How costs are ranked
Weighted tokens are input-token equivalents. The weights follow Anthropic's API price ratios: cache write 1.25x (5 minute) or 2x (1 hour), cache read 0.1x, output 5x input. Subscription plans meter usage in their own way. Weighted tokens rank sessions against each other. They are not a bill or a plan percentage.

## Full edition
The full edition, agent-token-auditor, adds:
- A fix playbook for each finding.
- Ready-to-paste CLAUDE.md rules.
- A guided workflow where your agent proposes the fixes for your setup and applies them once you agree.

**[Get the full edition, $9 (one-time)](https://buy.polar.sh/polar_cl_a3PsNiRzvZ4szsrbQS1eHOvKSEymZvFHIGegX0Q2rJT)**. Checkout and tax handling by Polar. Delivered as a ZIP download.

## Requirements
Python 3.8 or later, standard library only. Tested on macOS with the Claude Code log format of October 2026.

## License
MIT. See LICENSE.
