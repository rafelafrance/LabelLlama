from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class ScientificNameAuthorship(BaseField):
    scientificNameAuthorship: str = ""

    def __post_init__(self) -> None:
        self.scientificNameAuthorship = fix_parses.to_str(self.scientificNameAuthorship)
        self.scientificNameAuthorship = fix_parses.clean_str_ends(
            self.scientificNameAuthorship
        )
