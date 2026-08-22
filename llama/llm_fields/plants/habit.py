from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Habit(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the plant habit or general growth form as written, such as tree, shrub,
        herb, vine, grass, forb, rosette, clump-forming, or prostrate.
        """
    # --------------

    habit: str = ""

    def __post_init__(self, text: str) -> None:
        self.habit = self.hallucinated_str(self.habit, text)
