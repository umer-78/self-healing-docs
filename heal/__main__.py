"""python -m heal check --base REV [--head REV] --package DIR [--repo PATH]   stale docs a change leaves; exit 1 if any
python -m heal bench                                                        replay httpx's history, written to results/"""
import argparse
import sys


def main(argv=None):
    ap = argparse.ArgumentParser(prog="heal")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--repo", default=".")
    c.add_argument("--base", required=True)
    c.add_argument("--head", default="HEAD")
    c.add_argument("--package", required=True)
    sub.add_parser("bench")
    args = ap.parse_args(argv)
    if args.cmd == "bench":
        from .bench import bench
        print(bench())
        return 0
    from .history import check
    found = check(args.repo, args.base, args.head, args.package)
    for change, s in found:
        print(f"{s['file']} > {s['section']}: {s['why']} ({change['item']})")
        if s["fix"]:
            print("  suggested fix: rename the argument in the example (patch below)\n" + s["fix"])
    if not found:
        print("No doc section uses anything this change removes.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
