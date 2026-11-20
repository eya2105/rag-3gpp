import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from collections import Counter
from docx import Document
from config import RAW_DIR

for path in sorted(RAW_DIR.glob("*.docx")):
    doc = Document(path)
    styles = Counter(p.style.name for p in doc.paragraphs)
    heads = [p for p in doc.paragraphs if p.style.name.startswith("Heading")]

    print("=" * 70)
    print(path.name)
    print(f"  paragraphs : {len(doc.paragraphs)}")
    print(f"  headings   : {len(heads)}")
    print(f"  style counts: {dict(styles.most_common())}")
    print("  first 15 headings (style | text):")
    for p in heads[:15]:
        text = p.text.replace("\t", " ").strip()
        print(f"    {p.style.name:<10} | {text[:80]}")
    print("  all heading styles present:",
          sorted({p.style.name for p in heads}))