import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.rag import answer_question


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--model")
    args = parser.parse_args()

    try:
        print(answer_question(args.question, args.limit, args.model))
    except Exception as error:
        print(f"Query failed: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
