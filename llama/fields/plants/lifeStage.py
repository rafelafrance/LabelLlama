from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class LifeStage(ExtractedField):
    lifeStage: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeStage = fix_parses.hallucinated_str(self.lifeStage, text)
