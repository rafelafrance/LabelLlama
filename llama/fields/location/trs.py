from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Trs(ExtractedField):
    trs: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trs = self.to_str(self.trs)
