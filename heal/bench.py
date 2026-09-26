"""Replaying a real project's history: httpx, from its first commit to a pinned one.

For every first-parent commit that removed a public function, class or method, or a parameter,
that the docs were using: did the same commit update the docs; if not, which sections went
stale, how long they stayed stale, and would the suggested fix have matched the maintainers'?
"""
import json
import os
import statistics
import subprocess
from pathlib import Path

from .history import replay

REPO = "https://github.com/encode/httpx"
PIN = "b5addb64f0161ff6bfe94c124ef76f6a1fba5254"
RESULTS = Path(__file__).resolve().parent.parent / "results"


def checkout():
    path = Path(os.environ.get("HEAL_DATA", Path.home() / ".cache" / "heal")) / "httpx"
    if not (path / ".git").exists():
        subprocess.run(["git", "clone", "-q", REPO, str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "checkout", "-q", "--detach", PIN], check=True)
    return path


def bench():
    events = replay(checkout(), "httpx")
    stale = [(e, s) for e in events for s in e["stale"]]
    fixed = [(e, s) for e, s in stale if s["fixed"]]
    back = [(e, s) for e, s in stale if s.get("restored")]
    renames = [r for e in events for r in e.get("renames", [])]
    lines = ["## httpx, whole history", "",
             f"- Breaking API changes the docs were using: {len(events)}",
             f"- Docs updated in the same commit: {sum(not e['stale'] for e in events)}",
             f"- Left doc sections stale: {sum(bool(e['stale']) for e in events)} changes, {len(stale)} sections",
             f"- Of those sections, fixed later: {len(fixed)}"
             + (f", after a median of {statistics.median(s['commits_later'] for _, s in fixed):g} commits to the file and "
                f"{statistics.median(s['days_later'] for _, s in fixed):.0f} days" if fixed else ""),
             f"- Made right again by the code (the removed name came back): {len(back)}",
             f"- Still stale at the pinned commit: {len(stale) - len(fixed) - len(back)}",
             f"- Argument renames the docs used: {len(renames)} sections; the mechanical fix was suggested for "
             f"{sum(r['suggested'] for r in renames)} and matches the maintainers' own edit in {sum(r['matched'] for r in renames)}",
             "", "| Commit | Change | Doc section | Why | Fixed |", "|---|---|---|---|---|"]
    for e, s in stale:
        c = e["change"]
        what = f"{c['item']} {c['kind']}" + (f" `{c['param']}`" if "param" in c else "")
        when = (f"{s['commits_later']} commits, {s['days_later']:.0f} days later" if s["fixed"] else
                f"the name came back {s['days_later']:.0f} days later" if s.get("restored") else "not yet")
        lines.append(f"| {e['commit']} | {what} | {s['file']} > {s['section']} | {s['why']} | {when} |")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "bench.md").write_text("\n".join(lines) + "\n")
    for e in events:
        for s in e["stale"]:
            s.pop("fixed_text", None)
            s.pop("fix", None)
    (RESULTS / "summary.json").write_text(json.dumps({"repo": REPO, "pin": PIN, "events": events}, indent=1))
    return "\n".join(lines)
