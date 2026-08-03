from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Latitude(ExtractedField):
    latitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.latitude = self.to_str(self.latitude)
