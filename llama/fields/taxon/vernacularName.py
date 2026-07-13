from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class VernacularName(BaseField):
    vernacularName: str = ""

    def __post_init__(self) -> None:
        self.vernacularName = fix_parses.to_str(self.vernacularName)
