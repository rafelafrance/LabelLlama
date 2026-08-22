from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Genus(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the genus name applied to the specimen. Do not include subgenus, species
        epithet, authorship, qualifiers, or higher taxon names.
        """
    # --------------

    genus: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.genus = self.to_str(self.genus).capitalize()
