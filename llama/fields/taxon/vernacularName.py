from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class VernacularName(ExtractedField):
    vernacularName: str = ""

    def __post_init__(self, text: str) -> None:
        self.vernacularName = self.hallucinated_str(self.vernacularName, text)
