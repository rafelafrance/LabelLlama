from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class CollectionCode(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the collection code — the name, acronym, coden, or initialism
        identifying the collection or data set from which the record was derived
        """
    # --------------

    collectionCode: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.collectionCode = self.to_str(self.collectionCode)
