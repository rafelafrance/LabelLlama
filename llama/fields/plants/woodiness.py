from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Woodiness(ExtractedField):
    woodiness: str = ""

    def __post_init__(self, text: str) -> None:
        self.woodiness = self.hallucinated_str(self.woodiness, text)
