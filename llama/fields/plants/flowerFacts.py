from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class FlowerFacts(BaseField):
    flowerFacts: list[str] | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.flowerFacts = fix_parses.to_list_of_strs(self.flowerFacts)
        self.flowerFacts = fix_parses.reduce_str_list(self.flowerFacts)
