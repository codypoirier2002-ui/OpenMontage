#!/usr/bin/env python3
"""Token audit for Claude Code session logs.

Reads the JSONL transcripts that Claude Code keeps under ~/.claude/projects,
and prints a Markdown report: where the tokens went, and which habits cost
the most. Read-only. Prints numbers, tool names and file names only; it never
prints prompt or response text. Python 3.8+, standard library only.
"""
import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone

# Input-equivalent weights from Anthropic's published API price ratios:
# cache write 1.25x (5 min) or 2x (1 hour), cache read 0.1x, output 5x input.
# Subscription meters are not public; these weights rank costs, they do not bill.
W_INPUT, W_WRITE_5M, W_WRITE_1H, W_READ, W_OUTPUT = 1.0, 1.25, 2.0, 0.1, 5.0

LONG_CONTEXT = 150_000      # context size where a fresh session usually pays off
BIG_TOOL_RESULT = 20_000    # characters in one tool result
CACHE_REBUILD = 50_000      # cache write this large after turn 1 means the cache was lost


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def weighted(u):
    cc = u.get("cache_creation") or {}
    w1h = cc.get("ephemeral_1h_input_tokens")
    w5m = cc.get("ephemeral_5m_input_tokens")
    write = u.get("cache_creation_input_tokens", 0) or 0
    if w1h is None and w5m is None:
        w5m, w1h = write, 0
    return (
        (u.get("input_tokens", 0) or 0) * W_INPUT
        + (w5m or 0) * W_WRITE_5M
        + (w1h or 0) * W_WRITE_1H
        + (u.get("cache_read_input_tokens", 0) or 0) * W_READ
        + (u.get("output_tokens", 0) or 0) * W_OUTPUT
    )


def result_size(content):
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        total = 0
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                total += len(part.get("text", ""))
            elif isinstance(part, dict) and part.get("type") == "image":
                total += 0  # images are billed differently; skip
            else:
                total += len(json.dumps(part))
        return total
    return 0


def new_session():
    return {
        "requests": 0, "weighted": 0.0, "input": 0, "write": 0, "read": 0, "output": 0,
        "peak_ctx": 0, "long_ctx_weighted": 0.0, "rebuilds": 0, "rebuild_weighted": 0.0,
        "models": Counter(), "tools": Counter(), "big_results": Counter(),
        "subagent_weighted": 0.0, "subagent_files": 0, "first": None, "last": None, "days": Counter(),
        "title": None,
    }


def scan_file(path, sess, since, is_subagent, tool_names):
    seen = set()
    first_turn_done = False
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            kind = d.get("type")
            if kind == "custom-title" and d.get("customTitle"):
                sess["title"] = d["customTitle"]
            ts = parse_ts(d.get("timestamp"))
            if since and ts and ts < since:
                continue
            msg = d.get("message") if isinstance(d.get("message"), dict) else {}
            if kind == "assistant":
                for block in msg.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_names[block.get("id")] = block.get("name", "?")
                        sess["tools"][block.get("name", "?")] += 1
                mid = msg.get("id") or d.get("requestId") or d.get("uuid")
                u = msg.get("usage")
                if not u or mid in seen:
                    continue
                seen.add(mid)
                w = weighted(u)
                ctx = (u.get("input_tokens", 0) or 0) + (u.get("cache_creation_input_tokens", 0) or 0) \
                    + (u.get("cache_read_input_tokens", 0) or 0)
                sess["requests"] += 1
                sess["weighted"] += w
                sess["input"] += u.get("input_tokens", 0) or 0
                sess["write"] += u.get("cache_creation_input_tokens", 0) or 0
                sess["read"] += u.get("cache_read_input_tokens", 0) or 0
                sess["output"] += u.get("output_tokens", 0) or 0
                sess["models"][msg.get("model", "?")] += w
                if is_subagent:
                    sess["subagent_weighted"] += w
                else:
                    sess["peak_ctx"] = max(sess["peak_ctx"], ctx)
                    if ctx > LONG_CONTEXT:
                        sess["long_ctx_weighted"] += w
                    if first_turn_done and (u.get("cache_creation_input_tokens", 0) or 0) > CACHE_REBUILD:
                        sess["rebuilds"] += 1
                        sess["rebuild_weighted"] += w
                    first_turn_done = True
                if ts:
                    sess["days"][ts.date().isoformat()] += w
                    sess["first"] = min(sess["first"] or ts, ts)
                    sess["last"] = max(sess["last"] or ts, ts)
            elif kind == "user":
                content = msg.get("content")
                for block in content if isinstance(content, list) else []:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        if result_size(block.get("content")) > BIG_TOOL_RESULT:
                            sess["big_results"][tool_names.get(block.get("tool_use_id"), "?")] += 1


def collect(root, days, project_filter):
    since = datetime.now(timezone.utc) - timedelta(days=days) if days else None
    sessions = {}
    if not os.path.isdir(root):
        sys.exit(f"No log folder at {root}. Pass --root with the folder that holds your Claude Code projects.")
    for project in sorted(os.listdir(root)):
        pdir = os.path.join(root, project)
        if not os.path.isdir(pdir) or (project_filter and project_filter.lower() not in project.lower()):
            continue
        for name in os.listdir(pdir):
            if not name.endswith(".jsonl"):
                continue
            sid = name[:-6]
            sess = new_session()
            sess["project"] = project
            tool_names = {}
            scan_file(os.path.join(pdir, name), sess, since, False, tool_names)
            subdir = os.path.join(pdir, sid, "subagents")
            if os.path.isdir(subdir):
                for sub in os.listdir(subdir):
                    if sub.endswith(".jsonl"):
                        sess["subagent_files"] += 1
                        scan_file(os.path.join(subdir, sub), sess, since, True, {})
            if sess["requests"]:
                sessions[sid] = sess
    return sessions


def fmt(n):
    n = float(n)
    for unit, size in (("B", 1e9), ("M", 1e6), ("k", 1e3)):
        if abs(n) >= size:
            return f"{n / size:.1f}{unit}"
    return f"{n:.0f}"


def pct(part, whole):
    return f"{100 * part / whole:.0f}%" if whole else "0%"


def findings(sessions, total):
    out = []
    long_w = sum(s["long_ctx_weighted"] for s in sessions.values())
    if total and long_w / total > 0.2:
        worst = sorted(sessions.items(), key=lambda kv: -kv[1]["long_ctx_weighted"])[:3]
        out.append((long_w, "Long sessions",
                    f"{pct(long_w, total)} of weighted tokens came from turns with more than {fmt(LONG_CONTEXT)} tokens of context. "
                    "Every turn re-reads the whole conversation.",
                    "Write a hand-over note and start a fresh session when context passes 150k. Use /compact or /clear between tasks. "
                    "Worst: " + ", ".join(label(k, v) for k, v in worst)))
    sub_w = sum(s["subagent_weighted"] for s in sessions.values())
    if total and sub_w / total > 0.15:
        out.append((sub_w, "Subagent fan-out",
                    f"{pct(sub_w, total)} of weighted tokens ran inside subagents "
                    f"({sum(s['subagent_files'] for s in sessions.values())} subagent runs).",
                    "Cap parallel subagents at 2. Give each a narrow brief. Do small lookups in the main session."))
    rb_w = sum(s["rebuild_weighted"] for s in sessions.values())
    rb_n = sum(s["rebuilds"] for s in sessions.values())
    if total and rb_n and rb_w / total > 0.1:
        out.append((rb_w, "Cache rebuilds",
                    f"{rb_n} turns rewrote more than {fmt(CACHE_REBUILD)} tokens of cache after the first turn "
                    f"({pct(rb_w, total)} of weighted tokens). This happens after idle gaps, model switches or edits to early context.",
                    "Avoid waking long sessions after long idle gaps. Start a fresh session from a short brief instead. "
                    "Do not switch models in the middle of a long session."))
    big = Counter()
    for s in sessions.values():
        big.update(s["big_results"])
    if sum(big.values()) >= 5:
        top = ", ".join(f"{t} ({n})" for t, n in big.most_common(4))
        out.append((sum(big.values()) * BIG_TOOL_RESULT / 4, "Large tool outputs",
                    f"{sum(big.values())} tool results were longer than {BIG_TOOL_RESULT:,} characters. They stay in context for every later turn. Top: {top}.",
                    "Cap command output (`| tail -30`, `| head`, `grep`). Read files by line range. Ask web tools for a short answer."))
    models = Counter()
    for s in sessions.values():
        models.update(s["models"])
    if total and len(models) > 1:
        top_model, top_w = models.most_common(1)[0]
        if "opus" in top_model.lower() and top_w / total > 0.8:
            out.append((top_w * 0.3, "One model for everything",
                        f"{pct(top_w, total)} of weighted tokens used {top_model}.",
                        "Run routine work (formatting, lookups, simple edits, subagents) on a smaller model and keep the large one for design and hard bugs."))
    return sorted(out, key=lambda f: -f[0])


def label(sid, s):
    name = s.get("title") or sid[:8]
    return f"{name[:40]} (peak {fmt(s['peak_ctx'])})"


def report(sessions, days, top):
    total = sum(s["weighted"] for s in sessions.values())
    lines = [f"# Token audit ({'last %d days' % days if days else 'all time'})", ""]
    if not sessions:
        lines.append("No assistant turns found in this window.")
        return "\n".join(lines)
    reqs = sum(s["requests"] for s in sessions.values())
    lines += [
        "## Totals",
        f"- Sessions: {len(sessions)}. Model requests: {reqs:,}.",
        f"- Input {fmt(sum(s['input'] for s in sessions.values()))}, cache write {fmt(sum(s['write'] for s in sessions.values()))}, "
        f"cache read {fmt(sum(s['read'] for s in sessions.values()))}, output {fmt(sum(s['output'] for s in sessions.values()))}.",
        f"- Weighted tokens (input-equivalent): {fmt(total)}. Weights: cache write 1.25x or 2x, cache read 0.1x, output 5x.",
        "",
        "## Where it went",
        "",
        "| Rank | Session | Project | Share | Requests | Peak context | Subagent share |",
        "|---|---|---|---|---|---|---|",
    ]
    ranked = sorted(sessions.items(), key=lambda kv: -kv[1]["weighted"])
    for i, (sid, s) in enumerate(ranked[:top], 1):
        lines.append(f"| {i} | {(s.get('title') or sid[:8])[:40]} | {s['project'][-30:]} | {pct(s['weighted'], total)} | "
                     f"{s['requests']} | {fmt(s['peak_ctx'])} | {pct(s['subagent_weighted'], s['weighted'])} |")
    by_day = Counter()
    for s in sessions.values():
        by_day.update(s["days"])
    if by_day:
        lines += ["", "## By day (UTC)", ""]
        lines += [f"- {d}: {fmt(w)} ({pct(w, total)})" for d, w in sorted(by_day.items())[-14:]]
    models = Counter()
    for s in sessions.values():
        models.update(s["models"])
    lines += ["", "## By model", ""]
    lines += [f"- {m}: {pct(w, total)}" for m, w in models.most_common() if w >= total * 0.005]
    lines += ["", "## Findings, biggest first", ""]
    found = findings(sessions, total)
    if not found:
        lines.append("No costly pattern passed its threshold. Your usage looks lean.")
    for i, (_, title, what, fix) in enumerate(found, 1):
        lines += [f"### {i}. {title}", f"- What: {what}", f"- Fix: {fix}", ""]
    return "\n".join(lines)


FOOTER = ("\nFull edition, agent-token-auditor $9: a fix playbook for each finding and ready CLAUDE.md rules. "
          "https://buy.polar.sh/polar_cl_a3PsNiRzvZ4szsrbQS1eHOvKSEymZvFHIGegX0Q2rJT")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit Claude Code token use from local session logs.")
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"), help="folder with project log folders")
    ap.add_argument("--days", type=int, default=7, help="look back this many days (0 = all time)")
    ap.add_argument("--project", default="", help="only folders whose name contains this text")
    ap.add_argument("--top", type=int, default=10, help="sessions to list")
    ap.add_argument("--json", action="store_true", help="print a JSON summary instead of Markdown")
    args = ap.parse_args(argv)
    sessions = collect(args.root, args.days, args.project)
    if args.json:
        total = sum(s["weighted"] for s in sessions.values())
        print(json.dumps({
            "sessions": len(sessions),
            "weighted_tokens": round(total),
            "findings": [{"title": t, "what": w, "fix": f} for _, t, w, f in findings(sessions, total)],
            "top": [{"session": sid, "title": s.get("title"), "share": round(s["weighted"] / total, 3) if total else 0,
                     "peak_context": s["peak_ctx"]}
                    for sid, s in sorted(sessions.items(), key=lambda kv: -kv[1]["weighted"])[:args.top]],
        }, indent=2))
    else:
        print(report(sessions, args.days, args.top))
        print(FOOTER)


if __name__ == "__main__":
    main()
