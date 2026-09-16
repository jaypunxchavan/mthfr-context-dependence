"""Idempotent audit-log appending.

The naive approach -- rebuild the full entry every run and append it --
duplicates content every time the write-up generator reruns without new
underlying data, since nothing checked whether a line was already logged.
This happened six times in one project before being caught.

append_new_lines only writes lines that don't already appear anywhere in
the file (exact match, whitespace-normalized). A header is written only
if at least one line in the batch is genuinely new.
"""
from pathlib import Path
from datetime import date


def append_new_lines(audit_path, header_title, lines):
    """
    audit_path: Path to audit_log.md
    header_title: e.g. "Robustness follow-ups" -- used only if something
                  new is actually written
    lines: list of candidate '- ...' strings

    Returns the number of lines actually written (0 if everything in
    `lines` was already present).
    """
    audit_path = Path(audit_path)
    existing = audit_path.read_text() if audit_path.exists() else ""
    existing_normalized = {ln.strip() for ln in existing.splitlines() if ln.strip()}

    new_lines = [ln for ln in lines if ln.strip() not in existing_normalized]
    if not new_lines:
        return 0

    today = date.today().isoformat()
    block = [f"\n### {today} — {header_title}\n"] + new_lines
    with open(audit_path, "a") as f:
        f.write("\n".join(block) + "\n")
    return len(new_lines)
