from dataclasses import dataclass, field, fields
from typing import Any

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField
from llama.vocab.administrative_unit import US_COUNTY, US_STATE, USA

COUNTRY: str = compress("""The country where the specimen was collected.""")


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

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        actual_usa = actual.lower() in USA
        us_county = record.get("county", "").lower() in US_COUNTY
        us_state = record.get("stateProvince", "").lower() in US_STATE

        # OK if expect is empty and predicted USA and is a US county or state
        if not expect and actual_usa and (us_county or us_state):
            return 1.0

        return BaseField.score(expect, actual, record)  # Default to edit distance


DEFAULTS = DotDict({f.name: f.default for f in fields(Country)})
