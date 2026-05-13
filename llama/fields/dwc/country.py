from dataclasses import dataclass, field
from typing import Any

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.vocab.administrative_unit import US_COUNTY, US_STATE, USA

COUNTRY: str = compress("""
    `country` (str):
    Extract the country where the specimen was collected.
    Return the full country name (e.g., 'United States', 'Canada', 'Mexico'),
    not an abbreviation or acronym.
    If the country is not stated but can be inferred from the state,
    province, or locality, return the inferred country.
    If no country information is available, return an empty string.
    """)


@dataclass
class Country(BaseField):
    country: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.country = fix_values.to_str(self.country).title()

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Make a blank country = USA if state or county is known to be in the US."""
        self.country = USA.get(self.country, self.country)
        us_county = fix_values.to_str(record.get("county", ""))
        us_county = us_county.lower() in US_COUNTY
        us_state = fix_values.to_str(record.get("stateProvince", ""))
        us_state = us_state.lower() in US_STATE
        if not self.country and (us_county or us_state):
            self.country = "United States"
        self.country = self.country.title()
