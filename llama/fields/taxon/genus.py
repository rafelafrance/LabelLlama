from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Genus(ExtractedField):
    genus: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.genus = self.to_str(self.genus).capitalize()
