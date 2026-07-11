import csv
from pathlib import Path

UNITS_CSV: Path = Path(__file__).parent / "terms" / "unit_terms.csv"
METERS = "m"

with UNITS_CSV.open() as f:
    reader = csv.DictReader(f)
    UNITS = {r["pattern"]: r["replace"] for r in reader}


def normalize(units: str) -> str:
    lc = units.lower()
    return UNITS.get(lc, lc)
