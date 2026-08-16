from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class FruitFacts(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract information about fruits, excluding the fruit color
        (which belongs in `fruitColor`)
        """
    # --------------

    fruitFacts: list[str] | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.fruitFacts = self.to_list_of_strs(self.fruitFacts)
        self.fruitFacts = self.reduce_str_list(self.fruitFacts)
