from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class DecimalLongitude(ExtractedField):
    decimalLongitude: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        long = fix_parses.to_float(self.decimalLongitude)
        self.decimalLongitude = long if long is not None else ""
