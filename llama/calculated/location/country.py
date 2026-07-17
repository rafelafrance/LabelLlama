from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField
from llama.vocab.administrative_unit import US_COUNTY, US_STATE, USA


@dataclass
class Country(CalculatedField):
    country: str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        """Make a blank country = USA if state or county is known to be in the US."""
        self.country = USA.get(self.country, self.country)
        us_county = record.get("county", "")
        us_county = us_county.lower() in US_COUNTY
        us_state = record.get("stateProvince", "")
        us_state = us_state.lower() in US_STATE
        if not self.country and (us_county or us_state):
            self.country = "United States"
        self.country = self.country
