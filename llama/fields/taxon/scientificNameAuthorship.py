from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class ScientificNameAuthorship(ExtractedField):
    scientificNameAuthorship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.scientificNameAuthorship = self.to_str(self.scientificNameAuthorship)
        self.scientificNameAuthorship = self.clean_str_ends(
            self.scientificNameAuthorship
        )
