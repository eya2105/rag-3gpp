import json
from dataclasses import asdict
from pathlib import Path

from config import (
    CHUNK_MAX_WORDS, CHUNK_OVERLAP_WORDS, CHUNKS_PATH,
    EXCLUDED_TITLES, RAW_DIR, RELEASE, SPECS,
)
from src.chunking import chunk_section
from src.models import Chunk
from src.parsing import parse_sections


def ingest_spec(name: str, spec: dict) -> list[Chunk]:
    path = RAW_DIR / Path(spec["filename"]).with_suffix(".docx")
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run scripts/download_specs.py first."
        )
    code = spec["number"].replace(".", "")
    chunks: list[Chunk] = []

    for section in parse_sections(path):
        if section.level == 1 and section.title in EXCLUDED_TITLES:
            continue
        for text in chunk_section(section, CHUNK_MAX_WORDS, CHUNK_OVERLAP_WORDS):
            chunks.append(Chunk(
                id=f"{code}-{len(chunks):05d}",
                spec=name,
                release=RELEASE,
                version=spec["version"],
                section=section.number,
                title=section.title,
                breadcrumb=section.breadcrumb,
                text=text,
            ))
    return chunks


def ingest_all() -> list[Chunk]:
    return [c for name, spec in SPECS.items() for c in ingest_spec(name, spec)]


def save_chunks(chunks: list[Chunk], path: Path = CHUNKS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")


def load_chunks(path: Path = CHUNKS_PATH) -> list[Chunk]:
    with open(path, encoding="utf-8") as f:
        return [Chunk(**json.loads(line)) for line in f]