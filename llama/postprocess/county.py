import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import pandas as pd

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class County(BaseField):
    usa_csv: ClassVar[Path] = Path(__file__).parent / "terms" / "us_locations.csv"
    us_county: ClassVar[set[str] | None] = None

    county: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.county = fix_values.to_str(self.county)

        # Remove the county label
        self.county = re.sub(r"\s(co\.?|county)$", "", self.county, flags=re.IGNORECASE)

        self.county = self.county.title()

    @classmethod
    def setup_field(cls) -> None:
        usa = pd.read_csv(cls.usa_csv).to_dict(orient="records")
        cls.us_county = {
            r["pattern"].lower() for r in usa if
            r["label"] in ("us_county", "us_state-us_county")
        }
