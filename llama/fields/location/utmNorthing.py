from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField

# Remove these extra values
EMPTY_NE: tuple = ("0", "0.0")


@dataclass
class UtmNorthing(ExtractedField):
    utmNorthing: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utmNorthing = self.to_str(self.utmNorthing)
        self.utmNorthing = self.utmNorthing.lower().replace("n", "")
        self.utmNorthing = "" if self.utmNorthing in EMPTY_NE else self.utmNorthing
