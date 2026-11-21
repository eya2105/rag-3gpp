import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.ingestion import load_chunks
from src.rag import build_faiss_index


if __name__ == "__main__":
    chunks = load_chunks()
    index = build_faiss_index(chunks)
    print(f"{len(chunks)} chunks indexed in FAISS")
