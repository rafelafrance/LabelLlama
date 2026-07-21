from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Country(BaseField):
    country: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.country = fix_parses.title_with_exceptions(self.country)
