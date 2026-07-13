from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class GeodeticDatum(BaseField):
    geodeticDatum: str = ""

    def __post_init__(self) -> None:
        self.geodeticDatum = fix_parses.to_str(self.geodeticDatum)
