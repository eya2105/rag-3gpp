import argparse
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.ingestion import load_chunks


def stats(chunks):
    by_spec = defaultdict(list)
    for c in chunks:
        by_spec[c.spec].append(c)
    for spec, items in by_spec.items():
        words = [len(c.text.split()) for c in items]
        print(f"{spec}: {len(items)} chunks, {len({c.section for c in items})} sections")
        print(f"  words  mean={statistics.mean(words):.0f}  median={statistics.median(words):.0f}  max={max(words)}")
        print(f"  no section number: {sum(1 for c in items if not c.section)}")


def show(chunks, limit):
    for c in chunks[:limit]:
        print("-" * 70)
        print(f"{c.id} | {c.spec} {c.release} | §{c.section} | {len(c.text.split())} words")
        print(c.breadcrumb)
        print(c.text[:700])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--section")
    ap.add_argument("--grep")
    ap.add_argument("--limit", type=int, default=3)
    args = ap.parse_args()

    chunks = load_chunks()
    if not (args.spec or args.section or args.grep):
        stats(chunks)
    else:
        if args.spec:
            chunks = [c for c in chunks if c.spec == args.spec]
        if args.section:
            chunks = [c for c in chunks if c.section == args.section]
        if args.grep:
            chunks = [c for c in chunks if args.grep.lower() in c.text.lower()]
        print(f"{len(chunks)} matches")
        show(chunks, args.limit)