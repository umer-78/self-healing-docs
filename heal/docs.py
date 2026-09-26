"""The docs side: markdown split into sections by heading, and the code each section uses.

A change makes a section stale when the section still uses what the change took away: a call
to a removed function or class, or a removed keyword argument passed to the function that
lost it. A section that uses a changed function is a suspect even when nothing it says is
wrong yet (a new parameter may need documenting)."""
import re


def sections(markdown, path=""):
    """[(heading path, text)]"""
    out, trail, buf, fenced = [], [], [], False
    for line in markdown.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        m = None if fenced else re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            if buf:
                out.append((" > ".join(trail) or path, "\n".join(buf)))
            level = len(m.group(1))
            trail = trail[: level - 1] + [m.group(2).strip()]
            buf = []
        else:
            buf.append(line)
    if buf:
        out.append((" > ".join(trail) or path, "\n".join(buf)))
    return out


def calls(text, name):
    """The argument lists of every call to `name` in the text (a call may span lines)."""
    out = []
    for m in re.finditer(rf"(?<![\w]){re.escape(name)}\(", text):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            depth += {"(": 1, ")": -1}.get(text[i], 0)
            i += 1
        out.append(text[m.end(): i - 1])
    return out


def mentions(text, name, package=""):
    """A call or a code mention of a top-level name: `name(`, `package.name`, or `name` in backticks.
    `other.name` (another library's class of the same name) does not count."""
    qualified = rf"|(?<![\w.]){re.escape(package)}\.{re.escape(name)}\b" if package else ""
    return bool(re.search(rf"(?<![\w.]){re.escape(name)}\(|`{re.escape(name)}`{qualified}", text))


def stale(section_text, change, name, heading=""):
    """What in this section the change made wrong, or "". A removed method only counts where the
    section names its class: docs calling `.read()` or `asyncio.run()` may mean anything else."""
    qual = change["item"].split(":", 1)[1]
    if change["kind"] == "removed" and "." in qual:
        cls = qual.split(".")[0]
        if re.search(rf"(?<![\w]){re.escape(cls)}(?![\w])", heading + "\n" + section_text) and \
                re.search(rf"\.{re.escape(name)}\(|`{re.escape(name)}\(?\)?`", section_text):
            return f"uses {cls}.{name}, which was removed"
        return ""
    if change["kind"] == "removed" and mentions(section_text, name, change["item"].split(".")[0]):
        return f"uses {name}, which was removed"
    if change["kind"] == "parameter removed":
        for args in calls(section_text, name):
            if re.search(rf"(?<![\w]){re.escape(change['param'])}\s*=", args):
                return f"passes {change['param']}= to {name}(), which no longer takes it"
    return ""


def heal(section_text, change, name):
    """A mechanical fix when the change is a rename; None when it needs a person (or an LLM)."""
    if change["kind"] == "parameter removed" and change.get("renamed_to"):
        fixed = section_text
        for args in calls(section_text, name):
            new = re.sub(rf"(?<![\w]){re.escape(change['param'])}(\s*=)", change["renamed_to"] + r"\1", args)
            fixed = fixed.replace(f"{name}({args})", f"{name}({new})")
        return fixed if fixed != section_text else None
    return None
