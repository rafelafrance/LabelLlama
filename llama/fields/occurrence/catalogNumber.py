from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class CatalogNumber(BaseField):
    catalogNumber: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.catalogNumber = fix_values.to_str(self.catalogNumber)
