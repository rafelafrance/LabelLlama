from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import pandas as pd

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class StateProvince(BaseField):
    usa_csv: ClassVar[Path] = Path(__file__).parent / "terms" / "us_locations.csv"
    us_state: ClassVar[set[str] | None] = None

    stateProvince: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.stateProvince = fix_values.to_str(self.stateProvince)

    @classmethod
    def setup_field(cls) -> None:
        usa = pd.read_csv(cls.usa_csv).to_dict(orient="records")
        cls.us_state = {
            r["pattern"].lower() for r in usa if
            r["label"] in ("us_state", "us_state-us_county")
        }
