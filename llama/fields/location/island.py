from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Island(ExtractedField):
    island: str = ""

    def __post_init__(self, text: str) -> None:
        self.island = self.hallucinated_str(self.island, text)
