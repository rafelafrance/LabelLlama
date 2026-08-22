from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class VernacularName(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the vernacular or common name applied to the specimen exactly as written.
        Do not translate or invent a common name from the scientific name.
        """
    # --------------

    vernacularName: str = ""

    def __post_init__(self, text: str) -> None:
        self.vernacularName = self.hallucinated_str(self.vernacularName, text)
