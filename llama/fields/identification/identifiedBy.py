from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class IdentifiedBy(ExtractedField):
    identifiedBy: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedBy = self.to_str(self.identifiedBy)
