"""Connector for Corpus Christi ArcGIS Open Data portal (public).

Fetches publicly available datasets for realistic category distributions.
Falls back to a cached local sample if the API is unreachable.
"""

import csv
import io
import json
from pathlib import Path

import httpx

CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "public_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CC_ARCGIS_BASE = "https://opendata.arcgis.com/api/v3/datasets"
CC_SERVICE_REQUESTS_URL = (
    "https://services1.arcgis.com/XBhYkoXKJCRHbe7M/arcgis/rest/services/"
    "Service_Requests_Public/FeatureServer/0/query"
)

CACHED_CATEGORIES_FILE = CACHE_DIR / "cc_service_categories.json"


DEFAULT_CATEGORIES = [
    {"category": "Streets & Traffic", "weight": 0.22},
    {"category": "Water / Wastewater", "weight": 0.18},
    {"category": "Code Enforcement", "weight": 0.15},
    {"category": "Parks & Recreation", "weight": 0.08},
    {"category": "Solid Waste", "weight": 0.12},
    {"category": "Animal Control", "weight": 0.07},
    {"category": "Drainage / Storm Water", "weight": 0.06},
    {"category": "Building Permits", "weight": 0.05},
    {"category": "General Information", "weight": 0.04},
    {"category": "Police Non-Emergency", "weight": 0.03},
]

DEFAULT_LOCATIONS = [
    "Southside", "Westside", "Flour Bluff", "Calallen",
    "Downtown", "North Beach", "Padre Island", "Annaville",
    "London", "Robstown Rd corridor",
]


def fetch_service_categories() -> list[dict]:
    """Try to fetch categories from Corpus Christi ArcGIS; return cached or default on failure."""
    if CACHED_CATEGORIES_FILE.exists():
        try:
            return json.loads(CACHED_CATEGORIES_FILE.read_text())
        except Exception:
            pass

    try:
        params = {
            "where": "1=1",
            "outFields": "CATEGORY",
            "returnDistinctValues": "true",
            "f": "json",
        }
        resp = httpx.get(CC_SERVICE_REQUESTS_URL, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            features = data.get("features", [])
            cats = [f["attributes"]["CATEGORY"] for f in features if f.get("attributes", {}).get("CATEGORY")]
            if cats:
                total = len(cats)
                from collections import Counter
                counts = Counter(cats)
                result = [{"category": k, "weight": round(v / total, 3)} for k, v in counts.most_common()]
                CACHED_CATEGORIES_FILE.write_text(json.dumps(result, indent=2))
                return result
    except Exception:
        pass

    CACHED_CATEGORIES_FILE.write_text(json.dumps(DEFAULT_CATEGORIES, indent=2))
    return DEFAULT_CATEGORIES


def get_locations() -> list[str]:
    return DEFAULT_LOCATIONS
