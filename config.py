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