from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Habit(ExtractedField):
    habit: str = ""

    def __post_init__(self, text: str) -> None:
        self.habit = fix_parses.hallucinated_str(self.habit, text)
