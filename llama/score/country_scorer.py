from dataclasses import dataclass
from typing import Any

from llama.score.base_scorer import BaseScorer
from llama.vocab.administrative_unit import US_COUNTY, US_STATE, USA


@dataclass
class CountryScorer(BaseScorer):
    def cross_field_score(
        self, expect: Any, actual: Any, actual_record: dict[str, Any]
    ) -> None:
        actual_usa = actual.lower() in USA
        us_county = actual_record.get("county", "").lower() in US_COUNTY
        us_state = actual_record.get("stateProvince", "").lower() in US_STATE

        # OK if expect is empty and predicted USA and is a US county or state
        if not expect and actual_usa and (us_county or us_state):
            self.cross_field = 1.0

        self.cross_field = 0.0
