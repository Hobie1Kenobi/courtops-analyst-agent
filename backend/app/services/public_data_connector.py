import csv
from datetime import datetime
from pathlib import Path
from typing import Literal

import httpx


CACHE_ROOT = Path(__file__).resolve().parents[2] / "data" / "cache"
CITATIONS_FILENAME = "somerville_traffic_citations.csv"
METADATA_FILENAME = "somerville_traffic_citations.meta"

SOMERVILLE_CITATIONS_URL = (
    "https://data.somervillema.gov/api/views/3mqx-eye9/rows.csv?accessType=DOWNLOAD"
)


def ensure_cache_dir() -> None:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)


def get_cached_paths() -> tuple[Path, Path]:
    ensure_cache_dir()
    data_path = CACHE_ROOT / CITATIONS_FILENAME
    meta_path = CACHE_ROOT / METADATA_FILENAME
    return data_path, meta_path


def download_somerville_citations(force: bool = False) -> Path:
    """
    Download a public traffic citations dataset from Somerville, MA open data portal.

    The data is stored under data/cache with a simple metadata sidecar describing
    source URL and download timestamp. This is used only as a supplemental public
    dataset; no Corpus Christi or proprietary data is used.
    """
    data_path, meta_path = get_cached_paths()

    if data_path.exists() and not force:
        return data_path

    with httpx.stream("GET", SOMERVILLE_CITATIONS_URL, timeout=60.0) as resp:
        resp.raise_for_status()
        with data_path.open("wb") as f:
            for chunk in resp.iter_bytes():
                f.write(chunk)

    meta = {
        "source": SOMERVILLE_CITATIONS_URL,
        "downloaded_at_utc": datetime.utcnow().isoformat(),
        "description": "Somerville, MA Police Data: Traffic Citations (public open data).",
        "license": "ODbL 1.0 (see Somerville open data portal).",
    }
    with meta_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for key, value in meta.items():
            writer.writerow([key, value])

    return data_path

