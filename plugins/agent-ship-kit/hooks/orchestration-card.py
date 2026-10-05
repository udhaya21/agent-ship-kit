#!/usr/bin/env python3
"""UserPromptSubmit: put the delegation-rules kickoff card in front of the model.

Skills load on demand and can be skipped; this surfaces the routing decision
when the turn is planned. Slash commands and replies of three words or fewer
are skipped. Off when the plugin option orchestration_card is false.
"""
import json
import os
import sys

CARD = """<orchestration-kickoff>
Non-trivial task: do it on this loop with skills. Declare a pass/fail bar first.
Load the delegation-rules skill before spawning any agent, fork, workflow or codex call.
Delegate only for parallel independent work, digest-only analysis, or independent review by a different model before push. Prefer forks.
Bound delegations: short -> a real timeout; long -> run in the background with a deadline, then stop it if still running.
</orchestration-kickoff>"""



def main():
    if os.environ.get("CLAUDE_PLUGIN_OPTION_ORCHESTRATION_CARD", "true").lower() == "false":
        return
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    prompt = (payload.get("prompt") or "").strip()
    if not prompt or prompt.startswith("/") or len(prompt.split()) <= 3:
        return
    print(CARD)


if __name__ == "__main__":
    main()
