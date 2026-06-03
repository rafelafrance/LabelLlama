from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class ScientificNameAuthorship(BaseField):
    scientificNameAuthorship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.scientificNameAuthorship = fix_values.to_str(self.scientificNameAuthorship)
        self.scientificNameAuthorship = fix_values.clean_str_ends(
            self.scientificNameAuthorship
        )
