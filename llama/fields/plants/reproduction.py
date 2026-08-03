from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Reproduction(ExtractedField):
    reproduction: str = ""

    def __post_init__(self, text: str) -> None:
        self.reproduction = self.hallucinated_str(self.reproduction, text)
