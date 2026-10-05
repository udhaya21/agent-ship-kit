#!/usr/bin/env python3
"""PreToolUse: warn at a measured context size instead of a judged one.

Context is the last assistant turn's input side (input + cache reads + cache
writes), read off the transcript. Every request re-reads it, so context size
drives cost. Warns once per threshold per session and never blocks.
Thresholds and the on/off switch come from the plugin options.
"""
import json
import os
import sys

def _opt(name, default):
    return os.environ.get("CLAUDE_PLUGIN_OPTION_" + name) or default


def _tokens(name, default_k):
    try:
        return int(float(_opt(name, default_k)) * 1000)
    except (ValueError, OverflowError):
        return default_k * 1000


THRESHOLDS = [
    (_tokens("CONTEXT_HANDOFF_K", 200), "handoff"),
    (_tokens("CONTEXT_HARD_K", 300), "hard"),
]
TAIL_BYTES = 256 * 1024
STATE_DIR = os.path.join(
    os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.expanduser("~/.claude/cache"),
    "context-guard")
AUDIT = os.path.join(STATE_DIR, "audit.log")


def audit(path, session, ctx, verdict):
    """One line per run, so "never ran" and "ran and stayed quiet" differ.
    Inside a subagent the hook sees the parent's transcript, not its own."""
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(AUDIT, "a") as fh:
            fh.write("%s\t%s\t%s\t%s\n" % (session[:8], ctx, verdict, path))
    except OSError:
        pass


def allow(payload=None):
    if payload:
        print(json.dumps(payload))
    sys.exit(0)


def context_size(path):
    """Input-side tokens of the most recent assistant turn, or None."""
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as fh:
            if size > TAIL_BYTES:
                fh.seek(size - TAIL_BYTES)
                fh.readline()          # drop the partial line
            lines = fh.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return None

    for line in reversed(lines):
        if '"usage"' not in line:
            continue
        try:
            msg = (json.loads(line).get("message") or {})
        except ValueError:
            continue
        u = msg.get("usage")
        if not isinstance(u, dict) or "output_tokens" not in u:
            continue
        return (u.get("input_tokens", 0)
                + u.get("cache_read_input_tokens", 0)
                + u.get("cache_creation_input_tokens", 0))
    return None


def already_warned(session):
    try:
        with open(os.path.join(STATE_DIR, session)) as fh:
            return int(fh.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def record(session, level):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(os.path.join(STATE_DIR, session), "w") as fh:
            fh.write(str(level))
    except OSError:
        pass


def main():
    if _opt("CONTEXT_GUARD", "true").lower() == "false":
        allow()
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()

    path = data.get("transcript_path")
    session = (data.get("session_id") or "").replace("/", "_")
    if not path or not session:
        allow()

    ctx = context_size(path)
    if ctx is None:
        audit(path, session, "-", "no-usage")
        allow()

    crossed = [(t, kind) for t, kind in THRESHOLDS if ctx >= t]
    if not crossed:
        audit(path, session, ctx, "under")
        allow()
    level, kind = crossed[-1]
    if already_warned(session) >= level:
        audit(path, session, ctx, "already-warned")
        allow()
    record(session, level)
    audit(path, session, ctx, "warn-" + kind)

    k = f"{ctx // 1000}k"
    if kind == "hard":
        note = (
            f"CONTEXT {k} - past the hard stop. Write the handoff note now "
            f"(delegation-rules skill, 'Context budget'): task, what's done, what's open, "
            f"file paths and line numbers touched, gotchas and how they resolved, "
            f"the single next action. Save durable findings to memory first. "
            f"Then tell the user this session is handing off."
        )
    else:
        note = (
            f"CONTEXT {k} - handoff trigger reached (delegation-rules skill, 'Context budget'). "
            f"Finish the task in flight, then hand off rather than starting new work here. "
            f"If the next task is unrelated to this one, /clear instead - a fresh session "
            f"re-reads a small prefix; this one re-reads {k} on every request."
        )

    allow({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": note,
        },
        "systemMessage": f"context-guard: {k} - {kind} threshold",
    })


main()
