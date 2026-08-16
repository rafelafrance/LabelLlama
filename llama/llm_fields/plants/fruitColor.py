from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class FruitColor(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the color(s) of the fruits of the specimen
        """
    # --------------

    fruitColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.fruitColor = self.hallucinated_str(self.fruitColor, text)
        self.fruitColor = self.remove_trailing_punct(self.fruitColor)
