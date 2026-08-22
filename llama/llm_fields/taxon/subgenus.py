from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Subgenus(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the subgenus name when explicitly present, usually in parentheses after
        the genus. Do not include the genus, species epithet, or authorship.
        """
    # --------------

    subgenus: str = ""

    def __post_init__(self, text: str) -> None:
        self.subgenus = self.hallucinated_str(self.subgenus, text)
