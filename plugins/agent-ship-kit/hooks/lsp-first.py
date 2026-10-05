#!/usr/bin/env python3
"""PreToolUse: steer bare code-symbol searches to the LSP tool.

Blocks only when LSP could actually answer the question: a bare
camelCase/PascalCase identifier searched across source files.

Analysis is per grep invocation, not per command, so one exempt grep in a
compound command does not excuse the others. Greps quoted as text or sitting
inside a heredoc body are not invocations and are ignored.

Escape hatch: include `text-search` in the command or pattern.
Off unless the plugin option lsp_first is true.
"""
import json
import os
import re
import sys

ESCAPE = "text-search"
SEARCHER = r"(?:^|[\s|;&(])(?:rtk\s+)?(?:grep|egrep|fgrep|rg|ag)(?:\s|$)"
SPLIT = r";|&&|\|\||\n"          # pipelines; a single | stays inside a segment

SOURCE_EXT = {"ts", "tsx", "js", "jsx", "mjs", "cjs", "mts", "cts",
              "java", "go", "py", "pyi", "kt", "kts"}
NON_SOURCE = re.compile(
    r"\.(json|ya?ml|graphql|gql|env|md|mdx|lock|txt|csv|log|html|css|scss|sql|toml|ini|xml|sh)\b"
    r"|\.d\.ts\b"
    r"|(^|/)(dist|build|out|coverage|node_modules|\.next|\.git)(/|$)"
    r"|(^|/)\.env", re.I)


def allow():
    sys.exit(0)


def deny(term):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            f"'{term}' is a code symbol in source files - use LSP, not text search.\n"
            f"  1. ToolSearch(\"select:LSP\") if not loaded.\n"
            f"  2. workspaceSymbol query='{term}', then goToDefinition.\n"
            f"  3. findReferences for all usages.\n"
            f"WARM-UP TRAP: tsserver's findReferences only searches files already in "
            f"its project graph. Cold it silently under-reports - open a known consumer "
            f"first (goToDefinition from an import), then re-run.\n"
            f"If this is genuinely a text search, add `text-search` to the command."
        ),
    }}))
    sys.exit(0)


def strip_heredocs(cmd):
    """Blank heredoc bodies; their contents are data, not commands."""
    out, lines, i = [], cmd.split("\n"), 0
    while i < len(lines):
        out.append(lines[i])
        m = re.search(r"<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?", lines[i])
        if m:
            term, i = m.group(1), i + 1
            while i < len(lines) and lines[i].strip() != term:
                out.append("")
                i += 1
            if i < len(lines):
                out.append(lines[i])
        i += 1
    return "\n".join(out)


def mask_quotes(s):
    """Same-length copy with quoted spans blanked, so positions still map."""
    res, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in "'\"":
            j = s.find(c, i + 1)
            if j == -1:
                res.append("X" * (n - i))
                break
            res.append("X" * (j - i + 1))
            i = j + 1
        else:
            res.append(c)
            i += 1
    return "".join(res)


def is_symbol(tok):
    tok = tok.strip().strip("\"'")
    if not tok or re.search(r"[\s.*+?\[\]{}()|^$\\/@:,=]", tok):
        return False
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{3,}", tok):
        return False
    return bool(re.search(r"[a-z][A-Z]", tok))


def qualifies(term, scope):
    if not is_symbol(term):
        return False
    if NON_SOURCE.search(scope):
        return False
    exts = set(re.findall(r"\.([A-Za-z]+)\b", scope))
    return not (exts and not (exts & SOURCE_EXT))


def check_segment(seg_raw, seg_masked):
    """Return the offending term in this pipeline segment, else None."""
    if re.search(r"\bgit\s+(grep|log|show|diff)\b", seg_masked):
        return None
    for m in re.finditer(SEARCHER, seg_masked):
        # grep downstream of a pipe filters command output; LSP is irrelevant.
        if "|" in seg_masked[:m.start() + 1]:
            continue
        rest_raw = seg_raw[m.end():]
        rest_masked = seg_masked[m.end():]
        cut = rest_masked.find("|")
        if cut != -1:
            rest_raw = rest_raw[:cut]
        term, scope = None, []
        for tok in re.findall(r"'[^']*'|\"[^\"]*\"|\S+", rest_raw):
            if tok.startswith("-"):
                scope.append(tok)
            elif term is None:
                term = tok
            else:
                scope.append(tok)
        if term and qualifies(term, " ".join(scope)):
            return term.strip().strip("\"'")
    return None


def main():
    if os.environ.get("CLAUDE_PLUGIN_OPTION_LSP_FIRST", "false").lower() != "true":
        allow()
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}

    if tool == "Grep":
        term = (ti.get("pattern") or "").strip()
        ftype = ti.get("type")
        scope = " ".join([str(ti.get("path") or ""), str(ti.get("glob") or ""),
                          f".{ftype}" if ftype else ""])
        if ESCAPE in f"{term} {scope}":
            allow()
        if qualifies(term, scope):
            deny(term)
        allow()

    if tool != "Bash":
        allow()

    cmd = ti.get("command") or ""
    if ESCAPE in cmd:
        allow()
    cmd = strip_heredocs(cmd)
    masked = mask_quotes(cmd)

    pos = 0
    for piece in re.split(f"({SPLIT})", masked):
        if not re.fullmatch(SPLIT, piece or ""):
            hit = check_segment(cmd[pos:pos + len(piece)], piece)
            if hit:
                deny(hit)
        pos += len(piece)
    allow()


main()
