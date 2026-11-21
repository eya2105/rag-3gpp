from pathlib import Path

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

BASE_URL = "https://www.3gpp.org/ftp/Specs/archive"

SPECS = {
    "TS 23.501": {
        "series": "23_series",
        "number": "23.501",
        "version": "18.12.0",
        "filename": "23501-ic0.zip",
    },
    "TS 24.501": {
        "series": "24_series",
        "number": "24.501",
        "version": "18.14.0",
        "filename": "24501-ie0.zip",
    },
}

# Chunking 
RELEASE = "Rel-18"
CHUNKS_PATH = PROCESSED_DIR / "chunks.jsonl"

CHUNK_MAX_WORDS = 250
CHUNK_OVERLAP_WORDS = 40
EXCLUDED_TITLES = {"Foreword", "References"}

# Groq OpenAI-compatible API.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "qwen/qwen3.8-27b"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_DIR = ROOT / "storage" / "faiss"
DATABASE_PATH = ROOT / "data" / "conversations.db"