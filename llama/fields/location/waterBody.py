from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class WaterBody(BaseField):
    waterBody: str = ""

    def __post_init__(self, text: str) -> None:
        self.waterBody = fix_parses.hallucinated_str(self.waterBody, text)
