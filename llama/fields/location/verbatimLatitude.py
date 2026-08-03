from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class VerbatimLatitude(ExtractedField):
    verbatimLatitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimLatitude = self.to_str(self.verbatimLatitude)
