#!/usr/bin/env python3
"""
Build query_history.json — an index of the user's past BigQuery queries, for the
dashboard's "My query history" browser + the --add-history flow.

Sources scanned:
  1. Claude Code transcripts  ~/.claude/projects/-Users-harnoor-chahal-ai/*.jsonl
     (Bash tool_use blocks whose input.command contains `bq query`)
  2. Saved *.sql files in    /Users/harnoor.chahal/ai
  3. SQL fences in           ~/.claude/projects/.../memory/reference_*.md

Output: ./query_history.json  ->  [{id, source, title, timestamp, sql, tables[], runnable}]

    python3 extract_history.py
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
AI_DIR = Path("/Users/harnoor.chahal/ai")
PROJ = Path("/Users/harnoor.chahal/.claude/projects/-Users-harnoor-chahal-ai")
TRANSCRIPTS = sorted(PROJ.glob("*.jsonl"))
MEMORY = PROJ / "memory"
OUT = HERE / "query_history.json"

FQN_RE = re.compile(r"`(fulfillment-dwh-production\.[\w\-]+\.[\w\-]+)`")
SQL_START_RE = re.compile(r"\b(WITH|SELECT|DECLARE)\b", re.IGNORECASE)
HEREDOC_RE = re.compile(r"<<-?\s*'?(\w+)'?\n(.*?)\n\1", re.DOTALL)
REDIRECT_RE = re.compile(r"<\s*([^\s|>]+\.sql)")
MAX_SQL = 6000


def tables_in(sql):
    return sorted(set(FQN_RE.findall(sql or "")))


def extract_sql(command):
    """Return (sql, runnable). Best-effort across heredoc / redirect / quoted-arg styles."""
    m = HEREDOC_RE.search(command)
    if m and SQL_START_RE.search(m.group(2)):
        return m.group(2).strip(), True

    m = REDIRECT_RE.search(command)
    if m:
        p = Path(m.group(1))
        if p.exists():
            txt = p.read_text(errors="ignore")
            return txt.strip(), bool(SQL_START_RE.search(txt))
        return command.strip(), False  # redirected file gone -> non-runnable

    m = SQL_START_RE.search(command)
    if m:
        frag = command[m.start():]
        # strip a trailing closing quote + anything after it (flags already precede the SQL)
        for q in ("'", '"'):
            idx = frag.rfind(q)
            if idx > 40:  # only if it looks like a real terminator, not inside SELECT
                frag = frag[:idx]
                break
        frag = frag.strip().rstrip("'\"").strip()
        return frag, bool(SQL_START_RE.search(frag))

    return command.strip(), False


def from_transcripts():
    out = []
    seen = set()
    for fp in TRANSCRIPTS:
        stem = fp.stem[:8]
        for i, line in enumerate(fp.read_text(errors="ignore").splitlines()):
            line = line.strip()
            if not line or '"bq query"' not in line and "bq query" not in line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = obj.get("message") or {}
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            ts = obj.get("timestamp", "")
            for blk in content:
                if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                    continue
                if blk.get("name") != "Bash":
                    continue
                cmd = (blk.get("input") or {}).get("command", "")
                if "bq query" not in cmd:
                    continue
                sql, runnable = extract_sql(cmd)
                if not sql or not SQL_START_RE.search(sql):
                    continue
                dedup = sql[:300]
                if dedup in seen:
                    continue
                seen.add(dedup)
                out.append({
                    "id": f"tx-{stem}-{i}",
                    "source": "transcript",
                    "title": (blk.get("input") or {}).get("description", "") or "(bq query)",
                    "timestamp": ts[:19].replace("T", " "),
                    "sql": sql[:MAX_SQL],
                    "tables": tables_in(sql),
                    "runnable": runnable,
                })
    return out


def from_sql_files():
    out = []
    for fp in sorted(AI_DIR.glob("*.sql")):
        txt = fp.read_text(errors="ignore")
        out.append({
            "id": f"sql-{fp.stem}",
            "source": "saved .sql",
            "title": fp.name,
            "timestamp": _mtime(fp),
            "sql": txt.strip()[:MAX_SQL],
            "tables": tables_in(txt),
            "runnable": bool(SQL_START_RE.search(txt)),
        })
    return out


def from_memory():
    out = []
    if not MEMORY.exists():
        return out
    fence = re.compile(r"```sql\n(.*?)```", re.DOTALL | re.IGNORECASE)
    for fp in sorted(MEMORY.glob("reference_*.md")):
        txt = fp.read_text(errors="ignore")
        for j, m in enumerate(fence.findall(txt)):
            sql = m.strip()
            if not SQL_START_RE.search(sql):
                continue
            out.append({
                "id": f"mem-{fp.stem}-{j}",
                "source": "memory",
                "title": fp.stem.replace("reference_", "").replace("_", " "),
                "timestamp": _mtime(fp),
                "sql": sql[:MAX_SQL],
                "tables": tables_in(sql),
                "runnable": True,
            })
    return out


def _mtime(fp):
    import datetime
    return datetime.datetime.fromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def main():
    items = from_transcripts() + from_sql_files() + from_memory()
    # newest first where timestamps exist
    items.sort(key=lambda h: h.get("timestamp", ""), reverse=True)
    OUT.write_text(json.dumps(items, indent=2) + "\n")
    runnable = sum(1 for h in items if h.get("runnable"))
    print(f"Wrote {OUT} — {len(items)} queries "
          f"({runnable} runnable, {len(items)-runnable} verbatim-only)")
    by_src = {}
    for h in items:
        by_src[h["source"]] = by_src.get(h["source"], 0) + 1
    for s, n in by_src.items():
        print(f"  {s}: {n}")


if __name__ == "__main__":
    main()
