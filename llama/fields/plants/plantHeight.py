from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class PlantHeight(ExtractedField):
    plantHeight: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.plantHeight = self.to_str(self.plantHeight)
