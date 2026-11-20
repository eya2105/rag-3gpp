import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from src.models import Block, Section

HEADING_STYLE = re.compile(r"^Heading ([1-9])$")
ANNEX = re.compile(r"^(?P<number>Annex [A-Z])\b[^:]*:?\s*(?P<title>.*)$")

# Each dotted component may carry a letter suffix, at any level:
#   4.2.5a, 5.35A, 5.20b.1, 4.5.2A.1, 9.11.3.44A
# Annex-style numbers: A.3.2, B.1.4
NUMBERED = re.compile(
    r"^(?P<number>\d+[A-Za-z]?(?:\.\d+[A-Za-z]?)*"
    r"|[A-Z](?:\.\d+[A-Za-z]?)+)"
    r"(?:\s+(?P<title>.+))?$"
)

# Fallback for headings where the number and title are glued together,
# e.g. "4.5.2ADetermination of the a" (a known 3GPP docx formatting bug).
# Matches the longest number+suffix followed by an uppercase-starting word.
NUMBERED_RELAXED = re.compile(
    r"^(?P<number>\d+[A-Za-z]?(?:\.\d+[A-Za-z]?)*)(?=[A-Z][a-z])"
)


def clean(text: str) -> str:
    return " ".join(text.split())


def iter_body(doc):
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def parse_heading(text: str, style_level: int) -> tuple[int, str, str]:
    if m := ANNEX.match(text):
        return 1, m["number"], m["title"].strip()
    if m := NUMBERED.match(text):
        return style_level, m["number"], (m["title"] or "").strip()
    if m := NUMBERED_RELAXED.match(text):
        rest = text[len(m["number"]):].strip()
        return style_level, m["number"], rest
    return style_level, "", text


def table_block(table: Table) -> Block | None:
    rows: list[list[str]] = []
    for row in table.rows:
        cells, previous = [], None
        for cell in row.cells:
            if cell._tc is previous:
                continue
            previous = cell._tc
            cells.append(clean(cell.text))
        # Strip trailing empty cells — 3GPP tables often have a spurious
        # extra empty cell on the right that yields " | " trailing pipes.
        while cells and not cells[-1]:
            cells.pop()
        if any(cells):
            rows.append(cells)
    return Block.from_rows(rows) if rows else None

def paragraph_blocks(par: Paragraph) -> list[Block]:
    """3GPP docx uses <w:br/> soft breaks to make what looks like multiple
    lines inside one paragraph (abbreviation lists, procedure steps, IE
    tables rendered as tab-separated text). Split on those so packing
    respects entry boundaries."""
    raw = par.text  # '\n' where <w:br/> appeared
    lines = [clean(ln) for ln in raw.split("\n") if clean(ln)]
    if not lines:
        return []
    return [Block("para", ln) for ln in lines]

def parse_sections(path: Path) -> list[Section]:
    """Walk the docx and return a flat list of Section objects, one per Heading N."""
    doc = Document(path)
    sections: list[Section] = []
    stack: list[tuple[int, str]] = []          # (level, label) for breadcrumb
    current: Section | None = None

    for item in iter_body(doc):
        if isinstance(item, Table):
            block = table_block(item)
        else:
            text = clean(item.text)
            style = item.style.name
            if not text or style.startswith("toc"):
                continue
            if m := HEADING_STYLE.match(style):
                level, number, title = parse_heading(text, int(m[1]))
                label = f"{number} {title}".strip()
                stack = [s for s in stack if s[0] < level] + [(level, label)]
                current = Section(level, number, title, " > ".join(l for _, l in stack))
                sections.append(current)
                continue
            if current:
                current.blocks.extend(paragraph_blocks(item))
            continue

        if current and block:
            current.blocks.append(block)

    return sections