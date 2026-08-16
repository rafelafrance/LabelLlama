from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class CatalogNumber(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the catalog number — the unique identifier for the specimen or record
        within its collection or data set
        """
    # --------------

    catalogNumber: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.catalogNumber = self.to_str(self.catalogNumber)
