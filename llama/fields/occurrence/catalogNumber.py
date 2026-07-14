from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class CatalogNumber(BaseField):
    catalogNumber: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.catalogNumber = fix_parses.to_str(self.catalogNumber)
