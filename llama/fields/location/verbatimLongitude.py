from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class VerbatimLongitude(BaseField):
    verbatimLongitude: str = ""

    def __post_init__(self) -> None:
        self.verbatimLongitude = fix_parses.to_str(self.verbatimLongitude)
