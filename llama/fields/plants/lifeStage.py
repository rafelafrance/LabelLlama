from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class LifeStage(ExtractedField):
    lifeStage: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeStage = self.hallucinated_str(self.lifeStage, text)
