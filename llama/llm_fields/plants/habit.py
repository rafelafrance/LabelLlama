from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Habit(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the plant's habit or general growth form/shape
        """
    # --------------

    habit: str = ""

    def __post_init__(self, text: str) -> None:
        self.habit = self.hallucinated_str(self.habit, text)
