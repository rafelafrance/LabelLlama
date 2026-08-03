from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class WaterBody(ExtractedField):
    waterBody: str = ""

    def __post_init__(self, text: str) -> None:
        self.waterBody = self.hallucinated_str(self.waterBody, text)
