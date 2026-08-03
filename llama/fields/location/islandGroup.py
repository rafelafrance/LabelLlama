from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class IslandGroup(ExtractedField):
    islandGroup: str = ""

    def __post_init__(self, text: str) -> None:
        self.islandGroup = self.hallucinated_str(self.islandGroup, text)
