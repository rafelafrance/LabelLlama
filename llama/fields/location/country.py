from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Country(ExtractedField):
    country: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.country = self.title_with_exceptions(self.country)
