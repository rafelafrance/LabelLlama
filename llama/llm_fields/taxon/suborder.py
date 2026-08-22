from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Suborder(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the taxonomic suborder explicitly stated for the specimen. Do not infer
        suborder from family, genus, or common name.
        """
    # --------------

    suborder: str = ""

    def __post_init__(self, text: str) -> None:
        self.suborder = self.hallucinated_str(self.suborder, text)
