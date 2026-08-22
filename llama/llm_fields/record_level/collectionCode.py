from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class CollectionCode(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the collection code only if explicitly present or unambiguous.
        """
    # --------------

    collectionCode: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.collectionCode = self.to_str(self.collectionCode)
