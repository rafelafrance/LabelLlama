from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class CatalogNumber(ExtractedField):
    catalogNumber: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.catalogNumber = self.to_str(self.catalogNumber)
