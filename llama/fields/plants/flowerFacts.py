from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class FlowerFacts(ExtractedField):
    flowerFacts: list[str] | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.flowerFacts = self.to_list_of_strs(self.flowerFacts)
        self.flowerFacts = self.reduce_str_list(self.flowerFacts)
