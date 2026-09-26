"""Git side: what a commit (or a pull request's range) changed in the public API, and which doc
sections that left stale; and, replaying a project's history, what happened to them after."""
import os
import subprocess
from pathlib import Path

from .code import api, changes, short
from .docs import calls, heal, sections, stale

BREAKING = ("removed", "parameter removed")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout


def show(repo, rev, path):
    return git(repo, "show", f"{rev}:{path}")


def module(path):
    return path[:-3].replace("/", ".")


def api_at(repo, rev, files):
    out = {}
    for f in files:
        out.update(api(show(repo, rev, f), module(f)))
    return out


def doc_files(repo, rev, docs=("docs/", "README.md")):
    return [f for f in git(repo, "ls-tree", "-r", "--name-only", rev).splitlines()
            if f.endswith(".md") and f.startswith(docs)]


def source_files(names):
    return [f for f in names if f.endswith(".py") and "/tests/" not in f and not os.path.basename(f).startswith("test_")]


def api_changes(repo, base, head, package):
    """Signature changes in the files a range touched. A removal only counts if nothing public in the
    whole package still goes by that name (or, for a parameter, still takes it under that name):
    docs saying `read()` may mean any class's read()."""
    files = source_files(git(repo, "diff", "--name-only", base, head, "--", package).splitlines())
    found = changes(api_at(repo, base, files), api_at(repo, head, files)) if files else []
    if not any(c["kind"] in BREAKING for c in found):
        return found
    everything = api_at(repo, head, source_files(git(repo, "ls-tree", "-r", "--name-only", head, "--", package).splitlines()))
    names = {}
    for k, ps in everything.items():
        names.setdefault(short(k), set()).update(ps)
    keep = lambda c: not ((c["kind"] == "removed" and short(c["item"]) in names) or
                          (c["kind"] == "parameter removed" and c["param"] in names.get(short(c["item"]), set())))
    return [c for c in found if keep(c)]


def stale_sections(repo, rev, change, files=None):
    name = short(change["item"])
    out = []
    for f in files or doc_files(repo, rev):
        for heading, text in sections(show(repo, rev, f), f):
            why = stale(text, change, name, heading)
            if why:
                out.append({"file": f, "section": heading, "why": why, "fix": heal(text, change, name)})
    return out


def check(repo, base, head, package):
    """[(change, stale section)] a range leaves behind: what a pull request would be told."""
    return [(c, s) for c in api_changes(repo, base, head, package) if c["kind"] in BREAKING
            for s in stale_sections(repo, head, c)]


def replay(repo, package):
    """Every breaking API change in first-parent history that the docs were using, and its fate."""
    commits = git(repo, "log", "--first-parent", "--reverse", "--format=%H %ct", "--", package).split("\n")
    events = []
    for line in filter(None, commits):
        commit, when = line.split()
        parent = git(repo, "rev-parse", f"{commit}^").strip()
        if not parent:
            continue
        for change in api_changes(repo, parent, commit, package):
            if change["kind"] not in BREAKING:
                continue
            before = stale_sections(repo, parent, change)       # sections using what this commit takes away
            if not before:
                continue
            after = stale_sections(repo, commit, change)
            event = {"commit": commit[:10], "time": int(when), "change": change, "used_in": len(before), "stale": after}
            if change.get("renamed_to"):            # would the mechanical fix have matched what the maintainers wrote?
                edited = {f: show(repo, commit, f) for f in {b["file"] for b in before}}
                event["renames"] = [{"file": b["file"], "suggested": b["fix"] is not None,
                                     "matched": b["fix"] is not None and any(
                                         f"{change['renamed_to']}=" in a.replace(" ", "")
                                         for a in calls(edited[b["file"]], short(change["item"])))} for b in before]
            back = restored(repo, commit, change, package)
            for s in after:
                s.update(fixed_after(repo, commit, change, s["file"]))
                if back and (not s["fixed"] or back["days_later"] < s["days_later"]):
                    s.update(fixed=False, restored=True, **{k: back[k] for k in ("commits_later", "days_later")})
            events.append(event)
    return events


def fixed_after(repo, commit, change, path):
    """When the file stopped using what the change removed: commits and days later, or never."""
    history = git(repo, "log", "--reverse", "--format=%H %ct", f"{commit}..HEAD", "--", path).split("\n")
    start = int(git(repo, "show", "-s", "--format=%ct", commit).strip())
    for n, line in enumerate(filter(None, history), 1):
        rev, when = line.split()
        if not stale_sections(repo, rev, change, [path]) :
            text = show(repo, rev, path)
            return {"fixed": True, "commits_later": n, "days_later": (int(when) - start) / 86400, "fixed_text": text}
    return {"fixed": False}


def restored(repo, commit, change, package):
    """When a removed function or class came back to the package, if it did (then the docs were right again)."""
    if change["kind"] != "removed" or "." in change["item"].split(":", 1)[1]:
        return None
    name = short(change["item"])
    start = int(git(repo, "show", "-s", "--format=%ct", commit).strip())
    for n, line in enumerate(filter(None, git(repo, "log", "--reverse", "--format=%H %ct", "-G", rf"^\s*(def|class) {name}\b",
                                              f"{commit}..HEAD", "--", package).split("\n")), 1):
        rev, when = line.split()
        if git(repo, "grep", "-q", "-E", rf"^\s*(def|class) {name}\b", rev, "--", package) is not None and \
                subprocess.run(["git", "-C", str(repo), "grep", "-q", "-E", rf"^(def|class) {name}\b", rev, "--", package]).returncode == 0:
            return {"commits_later": n, "days_later": (int(when) - start) / 86400}
    return None
