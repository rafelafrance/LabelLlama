from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class WaterBody(BaseField):
    waterBody: str = ""

    def __post_init__(self) -> None:
        self.waterBody = fix_parses.to_str(self.waterBody)
