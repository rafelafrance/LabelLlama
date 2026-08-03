from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Municipality(ExtractedField):
    municipality: str = ""

    def __post_init__(self, text: str) -> None:
        self.municipality = self.hallucinated_str(self.municipality, text)
