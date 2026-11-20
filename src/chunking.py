from src.models import Block
import re

def _split_sentences(text: str) -> list[str]:
    return re.split(r"(?<=[.;:!?])\s+", text)

def _split_text(text: str, max_words: int, kind: str = "para") -> list[Block]:
    sentences = _split_sentences(text)
    blocks: list[Block] = []
    current: list[str] = []
    size = 0
    for s in sentences:
        w = len(s.split())
        if w > max_words:
            # A single sentence exceeds the limit — flush and word-split it.
            # Unavoidable here; sentence boundary cannot be preserved.
            if current:
                blocks.append(Block(kind, " ".join(current)))
                current, size = [], 0
            tokens = s.split()
            for i in range(0, len(tokens), max_words):
                blocks.append(Block(kind, " ".join(tokens[i:i + max_words])))
            continue
        if current and size + w > max_words:
            blocks.append(Block(kind, " ".join(current)))
            current, size = [], 0
        current.append(s)
        size += w
    if current:
        blocks.append(Block(kind, " ".join(current)))
    return blocks

def split_table(rows: list[list[str]], max_words: int) -> list[Block]:
    """Split a table by rows, repeating the header row in every piece.

    Rows are never cut. If even a header-only table is too big, return it
    whole — split_block() will fall through to text splitting.
    """
    if len(rows) <= 1:
        return [Block.from_rows(rows)]

    header, body = rows[0], rows[1:]
    header_words = len(" | ".join(header).split())
    if header_words >= max_words:
        return [Block.from_rows(rows)]

    groups: list[list[list[str]]] = []
    current: list[list[str]] = []
    size = header_words
    for row in body:
        row_words = len(" | ".join(row).split())
        if current and size + row_words > max_words:
            groups.append(current)
            current, size = [], header_words
        current.append(row)
        size += row_words
    if current:
        groups.append(current)
    return [Block.from_rows([header, *g]) for g in groups]


def split_block(block: Block, max_words: int) -> list[Block]:
    """Return one or more blocks, each <= max_words rendered tokens.

    Tries to keep table structure (split by row). Falls back to plain text
    splitting only when structure cannot be preserved.
    """
    if block.words <= max_words:
        return [block]

    if block.rows is not None:
        pieces = split_table(block.rows, max_words)
        # If table splitting could not actually shrink it (single-row
        # oversized table, or header alone is over limit), fall back to text.
        if len(pieces) == 1 and pieces[0].words > max_words:
            return _split_text(pieces[0].text, max_words, kind="table")
        return pieces

    return _split_text(block.text, max_words)


def overlap_tail(blocks: list[Block], overlap_words: int) -> list[Block]:
    tail, size = [], 0
    for block in reversed(blocks):
        if size + block.words > overlap_words:
            break
        tail.insert(0, block)
        size += block.words
    return tail


def pack(
    blocks: list[Block], max_words: int, overlap_words: int
) -> list[list[Block]]:
    groups: list[list[Block]] = []
    current: list[Block] = []
    size = 0
    for block in blocks:
        if current and size + block.words > max_words:
            groups.append(current)
            current = overlap_tail(current, overlap_words)
            size = sum(b.words for b in current)
            # If the next block still doesn't fit, drop overlap entirely
            # rather than overflow and get word-cut by _hard_split.
            if size + block.words > max_words:
                current = []
                size = 0
        current.append(block)
        size += block.words
    if current:
        groups.append(current)
    return groups


def is_void(text: str) -> bool:
    return text.lower().strip(" .") in {"", "void"}


def _hard_split(text: str, max_words: int, overlap_words: int) -> list[str]:
    """Final safety net: the joined group text must be <= max_words."""
    tokens = text.split()
    if len(tokens) <= max_words:
        return [text]
    step = max(1, max_words - overlap_words)
    out: list[str] = []
    for i in range(0, len(tokens), step):
        out.append(" ".join(tokens[i:i + max_words]))
        if i + max_words >= len(tokens):
            break
    return out


def chunk_section(section, max_words: int, overlap_words: int) -> list[str]:
    pieces = [p for b in section.blocks for p in split_block(b, max_words)]
    groups = pack(pieces, max_words, overlap_words)

    out: list[str] = []
    for g in groups:
        text = "\n".join(b.text for b in g)
        if is_void(text):
            continue
        out.extend(_hard_split(text, max_words, overlap_words))
    return out