from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Reproduction(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the plant's breeding system (how sexual organs are distributed among
        flowers and individuals across the population)
        """
    # --------------

    reproduction: str = ""

    def __post_init__(self, text: str) -> None:
        self.reproduction = self.hallucinated_str(self.reproduction, text)
