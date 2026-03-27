from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField
from llama.postprocess.county import County
from llama.postprocess.state_province import StateProvince


@dataclass
class Country(BaseField):
    usa_csv: ClassVar[Path] = Path(__file__).parent / "terms" / "us_locations.csv"
    usa_country: ClassVar[set[str] | None] = None

    country: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.country = fix_values.to_str(self.country)

    @classmethod
    def setup_field(cls) -> None:
        usa = pd.read_csv(cls.usa_csv).to_dict(orient="records")
        cls.usa_country = {r["pattern"] for r in usa if r["label"] == "country"}

    @classmethod
    def cross_field_score(
        cls, expect: Any, actual: Any, actual_record: dict[str, Any]
    ) -> float:
        expect_usa = expect.lower() in cls.usa_country
        is_usa = actual.lower() in cls.usa_country
        us_county = actual_record.get("county", "").lower() in County.us_county
        us_state = (
            actual_record.get("stateProvince", "").lower() in StateProvince.us_state
        )
        if expect_usa and is_usa:
            return 1.0
        if not expect_usa:
            return 1.0 if is_usa and (us_county or us_state) else 0.0
        return 0.0
