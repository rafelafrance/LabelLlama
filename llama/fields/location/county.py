import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class County(ExtractedField):
    county: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.county = fix_parses.to_str(self.county)

        # Remove the county label
        self.county = re.sub(r"\b(co\.?|county)$", "", self.county, flags=re.IGNORECASE)
        self.county = self.county.strip()
