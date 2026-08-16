from dataclasses import dataclass, field
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class PlantSizes(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract dimensions of individual plant parts and structures, excluding the
        overall plant height (which belongs in `plantHeight`)
        """
    # --------------

    plantSizes: list[str] | str = field(default_factory=list)

    def __post_init__(self, text: str) -> None:
        del text
        self.plantSizes = self.to_list_of_strs(self.plantSizes)
        self.plantSizes = self.reduce_str_list(self.plantSizes)
