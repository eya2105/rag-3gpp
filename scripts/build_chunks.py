import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import CHUNKS_PATH
from src.ingestion import ingest_all, save_chunks

if __name__ == "__main__":
    chunks = ingest_all()
    save_chunks(chunks)
    print(f"{len(chunks)} chunks written to {CHUNKS_PATH}")