from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class SpecificEpithet(ExtractedField):
    specificEpithet: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.specificEpithet = self.to_str(self.specificEpithet).lower()
