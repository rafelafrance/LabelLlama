from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Reproduction(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract plant reproductive-system terms such as monoecious, dioecious,
        bisexual, staminate, pistillate, perfect flowers, or sterile when stated.
        """
    # --------------

    reproduction: str = ""

    def __post_init__(self, text: str) -> None:
        self.reproduction = self.hallucinated_str(self.reproduction, text)
