from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class IslandGroup(ExtractedField):
    islandGroup: str = ""

    def __post_init__(self, text: str) -> None:
        self.islandGroup = fix_parses.hallucinated_str(self.islandGroup, text)
