import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class County(BaseField):
    county: str = ""

    def __post_init__(self) -> None:
        self.county = fix_parses.to_str(self.county)

        # Remove the county label
        self.county = re.sub(r"\b(co\.?|county)$", "", self.county, flags=re.IGNORECASE)
        self.county = self.county.strip()
