from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class LifeCycle(ExtractedField):
    lifeCycle: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeCycle = fix_parses.hallucinated_str(self.lifeCycle, text)
