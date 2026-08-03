from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Longitude(ExtractedField):
    longitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.longitude = self.to_str(self.longitude)
