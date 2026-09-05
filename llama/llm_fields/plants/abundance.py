from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Abundance(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the abundance or frequency of the specimen at the collection site
        """
    # --------------

    abundance: str = ""

    def __post_init__(self, text: str) -> None:
        self.abundance = self.hallucinated_str(self.abundance, text)
        self.abundance = self.remove_trailing_punct(self.abundance)
