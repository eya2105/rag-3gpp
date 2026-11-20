import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import CHUNK_MAX_WORDS
from src.ingestion import load_chunks

FUNCTION_WORDS = {
    "and", "or", "the", "a", "an", "of", "to", "in", "by", "as",
    "is", "are", "was", "were", "be", "been", "being",
    "for", "with", "on", "at", "from", "into", "onto", "over", "under",
    "that", "this", "these", "those", "which", "who", "whom", "whose",
    "shall", "will", "can", "may", "must", "should", "would", "could",
    "if", "when", "where", "while", "because", "but", "not", "no", "so",
    "than", "then", "also", "such", "any", "all", "some", "each", "every",
}

ENDINGS_THAT_ARE_FINE = set(".!?:;|\"'")
LIST_CONTINUATIONS = {"and", "or", "then"}


def _last_word(text: str) -> str:
    words = text.rstrip().split()
    return words[-1].lower().strip(".,;:()[]\"'") if words else ""


def _is_mid_sentence_cut(text: str) -> bool:
    t = text.rstrip()
    if not t:
        return False
    if t[-1] in ENDINGS_THAT_ARE_FINE:
        return False
    words = t.split()
    if len(words) >= 2 and words[-2].endswith(";"):
        if _last_word(t) in LIST_CONTINUATIONS:
            return False
    return _last_word(t) in FUNCTION_WORDS


def check_size_cap(chunks):
    max_w = max((len(c.text.split()) for c in chunks), default=0)
    return max_w <= CHUNK_MAX_WORDS, f"max={max_w}w (cap {CHUNK_MAX_WORDS}w)"


def check_no_empty_sections(chunks):
    empty = sum(1 for c in chunks if not c.section)
    return empty == 0, f"{empty} chunks without section"


def check_mid_sentence(chunks):
    flagged = [
        c for c in chunks
        if len(c.text.split()) > 40 and _is_mid_sentence_cut(c.text)
    ]
    pct = 100 * len(flagged) / len(chunks) if chunks else 0
    return pct < 1.0, f"{len(flagged)}/{len(chunks)} ({pct:.2f}%)"


def check_abbrev_blocks(chunks, section: str = "3.2"):
    sec = [c for c in chunks if c.section == section]
    bad = [
        c.id for c in sec
        if len(c.text.rstrip().split("\n")[-1].split()) < 2
    ]
    return len(bad) == 0, f"{len(sec)} chunks, {len(bad)} incomplete last lines"


def check_table_rows(chunks, section: str = "9.11.3.2"):
    sec = [c for c in chunks if c.section == section]
    bad = []
    for c in sec:
        last = c.text.rstrip().split("\n")[-1]
        if "|" in last:
            continue
        if last.startswith(("Table", "Figure", "Cause", "Any other", "The ")):
            continue
        bad.append(c.id)
    return len(bad) == 0, f"{len(sec)} chunks, {len(bad)} incomplete last lines"


def print_corpus_summary(chunks) -> None:
    by_spec: dict[str, list] = {}
    for c in chunks:
        by_spec.setdefault(c.spec, []).append(c)
    for spec, items in sorted(by_spec.items()):
        words = [len(c.text.split()) for c in items]
        print(f"  {spec}: {len(items)} chunks, "
              f"{len({c.section for c in items})} sections, "
              f"median={statistics.median(words):.0f}w, max={max(words)}w")


def tail_distribution(chunks) -> Counter:
    counter: Counter = Counter()
    for c in chunks:
        if len(c.text.split()) > 40 and _is_mid_sentence_cut(c.text):
            counter[_last_word(c.text)] += 1
    return counter


def main() -> None:
    chunks = load_chunks()
    print(f"Verifying {len(chunks)} chunks\n")

    print("Corpus summary:")
    print_corpus_summary(chunks)
    print()

    checks = [
        ("Size cap respected",          check_size_cap(chunks)),
        ("All chunks have section",     check_no_empty_sections(chunks)),
        ("Mid-sentence cuts < 1%",      check_mid_sentence(chunks)),
        ("§3.2 abbreviations intact",   check_abbrev_blocks(chunks)),
        ("§9.11.3.2 table rows intact", check_table_rows(chunks)),
    ]

    all_pass = True
    for name, (ok, msg) in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {msg}")
        all_pass = all_pass and ok

    counter = tail_distribution(chunks)
    if counter:
        print("\nMid-sentence tail distribution (documented, not a bug):")
        for word, n in counter.most_common(5):
            print(f"  {word:8s} {n}")

    print()
    print("ALL CHECKS PASS" if all_pass else "SOME CHECKS FAILED")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()