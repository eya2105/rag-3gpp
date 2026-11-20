import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

from config import BASE_URL, RAW_DIR, SPECS


def spec_url(spec: dict) -> str:
    return f"{BASE_URL}/{spec['series']}/{spec['number']}/{spec['filename']}"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar:
            for chunk in r.iter_content(chunk_size=1 << 16):
                f.write(chunk)
                bar.update(len(chunk))


def extract_docx(zip_path: Path, out_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path) as z:
        docx_names = [n for n in z.namelist() if n.lower().endswith(".docx")]
        if not docx_names:
            raise RuntimeError(f"No .docx found in {zip_path.name}")
        z.extract(docx_names[0], out_dir)
        return out_dir / docx_names[0]


def fetch_corpus() -> dict[str, Path]:
    paths = {}
    for name, spec in SPECS.items():
        zip_path = RAW_DIR / spec["filename"]
        if not zip_path.exists():
            download(spec_url(spec), zip_path)
        paths[name] = extract_docx(zip_path, RAW_DIR)
    return paths