from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class FruitFacts(ExtractedField):
    fruitFacts: list[str] | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.fruitFacts = fix_parses.to_list_of_strs(self.fruitFacts)
        self.fruitFacts = fix_parses.reduce_str_list(self.fruitFacts)
