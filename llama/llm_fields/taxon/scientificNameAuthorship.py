from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class ScientificNameAuthorship(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the authorship citation for the species-level scientific name
        """
    # --------------

    scientificNameAuthorship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.scientificNameAuthorship = self.to_str(self.scientificNameAuthorship)
        self.scientificNameAuthorship = self.clean_str_ends(
            self.scientificNameAuthorship
        )
