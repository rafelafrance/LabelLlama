from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class VerbatimLongitude(ExtractedField):
    verbatimLongitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimLongitude = self.to_str(self.verbatimLongitude)
