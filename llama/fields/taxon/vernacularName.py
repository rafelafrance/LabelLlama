from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class VernacularName(BaseField):
    vernacularName: str = ""

    def __post_init__(self, text: str) -> None:
        self.vernacularName = fix_parses.hallucinated_str(self.vernacularName, text)
