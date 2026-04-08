from dataclasses import dataclass, field
from typing import Any

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField
from llama.vocab.administrative_unit import US_COUNTY, US_STATE, USA


@dataclass
class Country(BaseField):
    country: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.country = fix_values.to_str(self.country)

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Make a blank country = USA if state or county is known to be in the US."""
        self.country = USA.get(self.country, self.country)
        us_county = fix_values.to_str(record.get("county", ""))
        us_county = us_county.lower() in US_COUNTY
        us_state = fix_values.to_str(record.get("stateProvince", ""))
        us_state = us_state.lower() in US_STATE
        if not self.country and (us_county or us_state):
            self.country = "USA"
