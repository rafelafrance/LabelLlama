from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class FlowerColor(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the color(s) of the flowers of the specimen
        """
    # --------------

    flowerColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.flowerColor = self.hallucinated_str(self.flowerColor, text)
        self.flowerColor = self.remove_trailing_punct(self.flowerColor)
