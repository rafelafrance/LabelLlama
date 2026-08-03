from dataclasses import dataclass, field

from llama.fields.extracted_field import ExtractedField


@dataclass
class PlantSizes(ExtractedField):
    plantSizes: list[str] | str = field(default_factory=list)

    def __post_init__(self, text: str) -> None:
        del text
        self.plantSizes = self.to_list_of_strs(self.plantSizes)
        self.plantSizes = self.reduce_str_list(self.plantSizes)
