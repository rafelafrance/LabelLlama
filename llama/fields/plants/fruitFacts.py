from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class FruitFacts(ExtractedField):
    fruitFacts: list[str] | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.fruitFacts = self.to_list_of_strs(self.fruitFacts)
        self.fruitFacts = self.reduce_str_list(self.fruitFacts)
