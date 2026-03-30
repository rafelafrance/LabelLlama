from pathlib import Path

import pandas as pd

COUNTRY_CSV: Path = Path(__file__).parent / "terms" / "countries.csv"
USA_CSV: Path = Path(__file__).parent / "terms" / "us_locations.csv"
CA_CSV: Path = Path(__file__).parent / "terms" / "ca_provinces.csv"

# -----------------------------------------------------------------------
COUNTRY_ROWS = pd.read_csv(COUNTRY_CSV).to_dict(orient="records")
COUNTRY: dict[str, str] = {
    r["country"].lower(): r["country"].title() for r in COUNTRY_ROWS
}

# -----------------------------------------------------------------------
USA_ROWS = pd.read_csv(USA_CSV).to_dict(orient="records")

USA: dict[str, str] = {
    r["pattern"]: r["replace"] for r in USA_ROWS if r["label"] == "country"
}

US_STATE: dict[str, str] = {
    r["pattern"].lower(): r["replace"]
    for r in USA_ROWS
    if r["label"] in ("us_state", "us_state-us_county")
}

US_COUNTY = {
    r["pattern"].lower(): r["pattern"].title()
    for r in USA_ROWS
    if r["label"] in ("us_county", "us_state-us_county")
}

# -----------------------------------------------------------------------
CA_ROWS = pd.read_csv(CA_CSV).to_dict(orient="records")

CA_PROVINCE: dict[str, str] = {r["province"]: r["replace"] for r in CA_ROWS}
