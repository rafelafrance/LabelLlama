from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class DecimalLongitude(ExtractedField):
    decimalLongitude: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        long = self.to_float(self.decimalLongitude)
        self.decimalLongitude = long if long is not None else ""
