from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class FlowerColor(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract flower color terms exactly as written. Do not include fruit, leaf, stem,
        or other plant-part colors.
        """
    # --------------

    flowerColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.flowerColor = self.hallucinated_str(self.flowerColor, text)
        self.flowerColor = self.remove_trailing_punct(self.flowerColor)
