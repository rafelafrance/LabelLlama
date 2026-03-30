from pathlib import Path

import pandas as pd

TAXA_CSV: Path = Path(__file__).parent / "terms" / "genus_to_family.csv"
TAXA_ROWS = pd.read_csv(TAXA_CSV).to_dict(orient="records")

GENUS_TO_FAMILY: dict[str, str] = {r["genus"]: r["family"] for r in TAXA_ROWS}
