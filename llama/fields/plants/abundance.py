from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Abundance(ExtractedField):
    abundance: str = ""

    def __post_init__(self, text: str) -> None:
        self.abundance = self.hallucinated_str(self.abundance, text)
        self.abundance = self.remove_trailing_punct(self.abundance)
