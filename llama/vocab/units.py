import csv
import re
from pathlib import Path

UNITS_CSV: Path = Path(__file__).parent / "terms" / "unit_terms.csv"
METERS = "m"

with UNITS_CSV.open() as f:
    reader = csv.DictReader(f)
    all_units = list(reader)
UNITS = {u["pattern"]: u["replace"] for u in all_units}

FACTOR_METER = {u["pattern"]: float(u["factor_cm"]) * 100.0 or 0.0 for u in all_units}

LENGTHS = re.compile(
    r"|".join([r["pattern"] for r in all_units if r["dimension"] == "length"]),
    flags=re.IGNORECASE,
)


def normalize(units: str) -> str:
    lc = units.lower()
    return UNITS.get(lc, lc)


def get_length_units(text: str) -> list[str]:
    units = [unit.lower() for unit in LENGTHS.findall(text)]
    units = [normalize(unit) for unit in units]
    return units


def to_meters(x: float, units: str) -> float:
    units = units.lower()
    meters = x * FACTOR_METER.get(units, 0.0)
    return meters
