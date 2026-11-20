import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.corpus import fetch_corpus

if __name__ == "__main__":
    for name, path in fetch_corpus().items():
        print(f"{name}: {path}")