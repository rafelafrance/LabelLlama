from dataclasses import dataclass
from typing import Any

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Genus(ExtractedField):
    genus: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.genus = fix_parses.to_str(self.genus).capitalize()
