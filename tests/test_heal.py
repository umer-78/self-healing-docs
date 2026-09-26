import subprocess

from heal.code import api, changes
from heal.docs import heal, sections, stale
from heal.history import check

V1 = "def fetch(url, timeout=5, verify=True):\n    pass\n\nclass Client:\n    def __init__(self, base=None):\n        pass\n    def close(self):\n        pass\n"
V2 = "def fetch(url, timeout=5, check_ssl=True):\n    pass\n\nclass Client:\n    def __init__(self, base=None):\n        pass\n"
DOC = ("# Guide\n\n## Fetching\n\n```python\n# a comment, not a heading\nfetch(\n    'https://x',\n    verify=False,\n)\n```\n\n"
       "## Clients\n\nCall `Client.close()` when done.\n\n## Other\n\nUse `asyncio.run(main())`.\n")


def test_api_and_changes():
    before, after = api(V1, "pkg.core"), api(V2, "pkg.core")
    assert before["pkg.core:fetch"] == ["url", "timeout", "verify"] and "pkg.core:Client.close" in before
    found = changes(before, after)
    assert {"item": "pkg.core:fetch", "kind": "parameter removed", "param": "verify", "renamed_to": "check_ssl"} in found
    assert {"item": "pkg.core:Client.close", "kind": "removed"} in found
    moved = changes({"a:thing": []}, {"b:thing": []})
    assert moved == []


def test_sections_skip_code_comments_and_staleness_is_specific():
    heads = [h for h, _ in sections(DOC)]
    assert heads == ["Guide", "Guide > Fetching", "Guide > Clients", "Guide > Other"]
    text = dict(sections(DOC))
    rename = {"item": "pkg.core:fetch", "kind": "parameter removed", "param": "verify", "renamed_to": "check_ssl"}
    assert "passes verify=" in stale(text["Guide > Fetching"], rename, "fetch")
    assert "check_ssl=False" in heal(text["Guide > Fetching"], rename, "fetch")
    close = {"item": "pkg.core:Client.close", "kind": "removed"}
    assert stale(text["Guide > Clients"], close, "close") == "uses Client.close, which was removed"
    assert stale(text["Guide > Other"], {"item": "pkg.x:Runner.run", "kind": "removed"}, "run") == ""


def test_check_a_pull_request(tmp_path):
    run = lambda *a: subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)
    (tmp_path / "pkg").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "pkg" / "core.py").write_text(V1)
    (tmp_path / "docs" / "guide.md").write_text(DOC)
    run("init", "-q")
    run("-c", "user.email=t@t", "-c", "user.name=t", "add", ".")
    run("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "v1")
    (tmp_path / "pkg" / "core.py").write_text(V2)
    run("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "v2")
    found = check(tmp_path, "HEAD~1", "HEAD", "pkg")
    assert {s["section"] for _, s in found} == {"Guide > Fetching", "Guide > Clients"}
    assert any(s["fix"] and "check_ssl=False" in s["fix"] for _, s in found)
