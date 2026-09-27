"""python -m heal.demo   write the live demo's data (docs/data.json): results/summary.json plus the pinned
commit's date (from the bench's httpx clone), so the page can draw how long each doc section stayed wrong."""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(out=ROOT / "docs"):
    summary = json.loads((ROOT / "results" / "summary.json").read_text())
    clone = Path(os.environ.get("HEAL_DATA", Path.home() / ".cache" / "heal")) / "httpx"
    summary["pin_time"] = int(subprocess.run(["git", "-C", str(clone), "log", "-1", "--format=%ct", summary["pin"]],
                                             capture_output=True, text=True, check=True).stdout)
    out.mkdir(exist_ok=True)
    (out / "data.json").write_text(json.dumps(summary, indent=1))
    print(f"wrote {out / 'data.json'}: {len(summary['events'])} breaking changes")


if __name__ == "__main__":
    build()
