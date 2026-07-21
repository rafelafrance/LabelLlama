from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class SpecificEpithet(BaseField):
    specificEpithet: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.specificEpithet = fix_parses.to_str(self.specificEpithet).lower()
