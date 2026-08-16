from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class FlowerFacts(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract information about flowers, excluding the flower color
        (which belongs in `flowerColor`)
        """
    # --------------

    flowerFacts: list[str] | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.flowerFacts = self.to_list_of_strs(self.flowerFacts)
        self.flowerFacts = self.reduce_str_list(self.flowerFacts)
