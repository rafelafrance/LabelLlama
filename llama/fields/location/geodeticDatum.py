from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class GeodeticDatum(ExtractedField):
    geodeticDatum: str = ""

    def __post_init__(self, text: str) -> None:
        self.geodeticDatum = self.hallucinated_str(self.geodeticDatum, text)
