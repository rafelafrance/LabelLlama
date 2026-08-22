from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Sex(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the sex of flowers, inflorescences, or plant individuals as written,
        such as staminate, pistillate, male, female, bisexual, or sterile.
        """
    # --------------

    sex: str = ""

    def __post_init__(self, text: str) -> None:
        self.sex = self.hallucinated_str(self.sex, text)
