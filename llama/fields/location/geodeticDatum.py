from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class GeodeticDatum(BaseField):
    geodeticDatum: str = ""

    def __post_init__(self, text: str) -> None:
        self.geodeticDatum = fix_parses.hallucinated_str(self.geodeticDatum, text)
