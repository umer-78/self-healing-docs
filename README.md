# self-healing-docs

A GitHub Action that stops a pull request from leaving documentation wrong. It works in four stages:

1. It reads the package's public API from source, as function, class and method signatures, using `ast`.
2. It splits the markdown docs into sections by heading.
3. For each signature the pull request removes (a function, class, method or parameter), it finds the sections that still use it: a call to the removed function, or the removed keyword passed to the function that lost it.
4. It fails the check with the section, the reason and, where the change is a rename, a patch.

Rewriting prose for deeper changes is left to a person or an LLM.

## Results: replaying httpx's history

`python -m heal bench` clones [httpx](https://github.com/encode/httpx) and replays every first-parent commit up to a pinned one, with the check running as it would have on each change. It takes about 70 seconds.

- **Breaking API changes the docs were using:** 38.
- **Docs updated in the same commit:** 13 (a third).
- **Changes that left doc sections stale:** 25, covering 33 sections. Of those sections:
  - **15 were fixed later,** after a median of 52 days.
  - **13 became right again because the removed name came back to the code.** For example, `Client` was renamed away in 2019 and reintroduced 10 days later.
  - **5 are still flagged at the pinned commit.** Checked by hand:
    - 2 are real. `docs/api.md` still lists `Response.next()` and `Response.anext()`, which were removed.
    - 3 are false alarms. The compatibility guide quotes the *requests* library's `send(allow_redirects=False)`, twice, and a log line prints the standard library's `SSLContext(...)`.
- **Argument renames the docs used:** 11 sections, such as `http_versions` → `http2` and `allow_redirects` → `follow_redirects`. The mechanical rename fix matches the maintainers' own edit in 8.

Every finding, with the commit and how long it stayed stale, is in `results/bench.md`.

What this says about the check:

- **It would have caught what went stale.** 15 of the 33 stale sections were later fixed by the maintainers themselves, taking days to years.
- **Its false alarms are specific.** It confuses another library's identically named API, quoted in a comparison guide or in log output. These come from name matching.
- **What reduces them:** a reviewer's ignore list, or an LLM pass over the flagged section.

## How it works

- `heal/code.py`: the public API of every module, meaning functions, classes (constructor parameters) and public methods, plus the signature changes between two snapshots.
  - An item that moves between modules has not been removed.
  - A removal only counts if nothing public in the whole package still goes by that name.
- `heal/docs.py`: sections by heading (code comments are not headings), and staleness.
  - A removed method only counts where the section names its class, so `asyncio.run()` is not httpx's `run()`.
  - `other.Name` is not the package's `Name`.
  - The rename patch is in `heal()`.
- `heal/history.py`: the git side. It covers what a range changed (`check`, used by the Action) and the full-history replay.
- `action.yml`: the composite Action.

Use it on a repository's pull requests:

```yaml
on: pull_request
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: {fetch-depth: 0}
      - uses: umer-78/self-healing-docs@main
        with: {package: mypackage}
```

Or locally: `python -m heal check --base origin/main --package mypackage` exits 1 and lists stale sections with fixes.

```bash
pip install -e '.[dev]'
pytest -q
python -m heal bench
```

The replay clones httpx into `~/.cache/heal`; nothing is committed.
