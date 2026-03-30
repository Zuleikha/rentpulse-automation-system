"""
Local file storage utilities.
All results are saved to disk under data/ - no external DB required.
"""
import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

DATA_DIR = Path("data")
JOBS_DIR = DATA_DIR / "jobs"
RENTPULSE_DIR = DATA_DIR / "rentpulse"
SUPPORT_DIR = DATA_DIR / "support"
PAYMENTS_DIR = DATA_DIR / "payments"
CUSTOMERS_DIR = DATA_DIR / "customers"

TRACKER_FILE = JOBS_DIR / "job_applications.json"


def ensure_dirs() -> None:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    RENTPULSE_DIR.mkdir(parents=True, exist_ok=True)
    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    PAYMENTS_DIR.mkdir(parents=True, exist_ok=True)
    CUSTOMERS_DIR.mkdir(parents=True, exist_ok=True)


# ---- JSON helpers ----

def read_json(path: Path) -> Any:
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_to_json_list(path: Path, item: Dict) -> None:
    """Append one item to a JSON array file, stamped with saved_at."""
    existing = read_json(path)
    if not isinstance(existing, list):
        existing = []
    item = dict(item)
    item["saved_at"] = datetime.now().isoformat()
    existing.append(item)
    write_json(path, existing)


# ---- CSV helpers ----

def write_csv(path: Path, rows: List[Dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_csv_row(path: Path, row: Dict, fieldnames: List[str]) -> None:
    """Append a single row; writes header if file does not exist yet."""
    write_header = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow(row)
