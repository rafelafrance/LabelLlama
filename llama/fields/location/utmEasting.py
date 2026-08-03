from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField

# Remove these extra values
EMPTY_NE: tuple = ("0", "0.0")


@dataclass
class UtmEasting(ExtractedField):
    utmEasting: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utmEasting = self.to_str(self.utmEasting)
        self.utmEasting = self.utmEasting.lower().replace("e", "")
        self.utmEasting = "" if self.utmEasting in EMPTY_NE else self.utmEasting
