import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import CHUNKS_PATH, FAISS_DIR
from src.corpus import fetch_corpus
from src.ingestion import ingest_all, load_chunks, save_chunks
from src.rag import build_faiss_index


def ensure_corpus() -> None:
    fetch_corpus()

    if not CHUNKS_PATH.exists():
        chunks = ingest_all()
        save_chunks(chunks)
        print(f"Created {len(chunks)} chunks")
    else:
        chunks = load_chunks()
        print(f"Using existing {len(chunks)} chunks at {CHUNKS_PATH}")

    if not (FAISS_DIR / "index.faiss").exists():
        build_faiss_index(chunks)
        print(f"Built FAISS index with {len(chunks)} chunks")


if __name__ == "__main__":
    ensure_corpus()

    import subprocess

    subprocess.run(
        [
            "python",
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.address",
            "0.0.0.0",
            "--server.port",
            "8501",
            "--server.headless",
            "true",
        ],
        check=True,
    )
