from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class VernacularName(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the vernacular (common) name of the species collected
        """
    # --------------

    vernacularName: str = ""

    def __post_init__(self, text: str) -> None:
        self.vernacularName = self.hallucinated_str(self.vernacularName, text)
