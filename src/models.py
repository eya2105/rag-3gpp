from dataclasses import dataclass, field


@dataclass
class Block:
    kind: str
    text: str
    rows: list[list[str]] | None = None

    @property
    def words(self) -> int:
        # Rendered word count — matches exactly what the embedding model sees.
        # For tables, this includes the '|' separators, which is deliberate:
        # pack() and split_table() must agree with inspect_chunks.py.
        return len(self.text.split())

    @classmethod
    def from_rows(cls, rows: list[list[str]]) -> "Block":
        text = "\n".join(" | ".join(r) for r in rows)
        return cls("table", text, rows)


@dataclass
class Section:
    level: int
    number: str
    title: str
    breadcrumb: str
    blocks: list[Block] = field(default_factory=list)


@dataclass
class Chunk:
    id: str
    spec: str
    release: str
    version: str
    section: str
    title: str
    breadcrumb: str
    text: str