from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Habit(ExtractedField):
    habit: str = ""

    def __post_init__(self, text: str) -> None:
        self.habit = self.hallucinated_str(self.habit, text)
