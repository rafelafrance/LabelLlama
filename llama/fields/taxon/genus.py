from dataclasses import dataclass
from typing import Any

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Genus(BaseField):
    genus: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.genus = fix_parses.to_str(self.genus).capitalize()

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Get the genus from the scientific name if it is missing here."""
        if not self.genus:
            words = record["scientificName"].split()
            self.genus = words[0].capitalize() if len(words) > 0 else ""
