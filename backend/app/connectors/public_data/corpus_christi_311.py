"""Stub adapter for Corpus Christi 311-style service requests.

Since the city's 311 data may not be directly accessible without authentication,
this module provides a synthetic dataset generator shaped by publicly available
category distributions from the city's service request pages.
"""

import random
from datetime import date, timedelta


CC_311_CATEGORIES = [
    "Pothole Repair",
    "Water Leak",
    "Overgrown Lot (Code Enforcement)",
    "Street Light Out",
    "Trash Pickup Missed",
    "Animal Running Loose",
    "Graffiti Removal",
    "Abandoned Vehicle",
    "Sewer Issue",
    "Noise Complaint",
    "Illegal Dumping",
    "Drainage Blocked",
    "Park Maintenance",
    "Traffic Signal Issue",
    "Permit Inquiry",
]

CC_NEIGHBORHOODS = [
    "Southside", "Westside", "Flour Bluff", "Calallen",
    "Downtown", "Padre Island", "North Beach",
]

PRIORITY_WEIGHTS = {"low": 0.3, "medium": 0.45, "high": 0.2, "critical": 0.05}


def generate_synthetic_311_records(
    rng: random.Random,
    count: int = 80,
    reference_date: date | None = None,
) -> list[dict]:
    ref = reference_date or date.today()
    priorities = list(PRIORITY_WEIGHTS.keys())
    weights = list(PRIORITY_WEIGHTS.values())
    records = []
    for i in range(count):
        days_ago = rng.randint(0, 180)
        records.append({
            "request_id": f"SR-{ref.year}-{10000 + i}",
            "category": rng.choice(CC_311_CATEGORIES),
            "neighborhood": rng.choice(CC_NEIGHBORHOODS),
            "priority": rng.choices(priorities, weights=weights, k=1)[0],
            "status": rng.choice(["open", "in_progress", "closed"]),
            "created_date": (ref - timedelta(days=days_ago)).isoformat(),
            "description": f"Synthetic 311 request #{i} for demo purposes.",
        })
    return records
