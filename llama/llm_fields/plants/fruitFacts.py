from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class FruitFacts(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract fruit-related notes other than color, such as fruit presence, maturity,
        size, shape, texture, quantity, or dehiscence. Put fruit color in fruitColor
        instead.
        """
    # --------------

    fruitFacts: list[str] | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.fruitFacts = self.to_list_of_strs(self.fruitFacts)
        self.fruitFacts = self.reduce_str_list(self.fruitFacts)
