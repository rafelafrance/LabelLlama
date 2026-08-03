from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Utm(ExtractedField):
    utm: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utm = self.to_str(self.utm)
