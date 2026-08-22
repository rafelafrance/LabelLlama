from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class FlowerFacts(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract flower-related notes other than color, such as flower presence, size,
        shape, scent, arrangement, or openness. Put flower color in flowerColor instead.
        """
    # --------------

    flowerFacts: list[str] | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.flowerFacts = self.to_list_of_strs(self.flowerFacts)
        self.flowerFacts = self.reduce_str_list(self.flowerFacts)
