from dataclasses import dataclass, field
from typing import Any

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField
from llama.vocab.administrative_unit import US_COUNTY, US_STATE, USA


@dataclass
class Country(BaseField):
    country: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.country = fix_values.to_str(self.country)

    def cross_field_update(self, record: dict[str, Any]) -> None:
        self.country = USA.get(self.country, self.country)
        us_county = record.get("county", "").lower() in US_COUNTY
        us_state = record.get("stateProvince", "").lower() in US_STATE
        if not self.country and (us_county or us_state):
            self.country = "USA"
