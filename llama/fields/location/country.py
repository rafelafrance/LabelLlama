from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Country(ExtractedField):
    country: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.country = fix_parses.title_with_exceptions(self.country)
