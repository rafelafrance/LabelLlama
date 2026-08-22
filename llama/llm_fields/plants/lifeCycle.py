from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class LifeCycle(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract life-cycle or duration terms such as annual, biennial, perennial,
        monocarpic, or short-lived perennial when explicitly stated.
        """
    # --------------

    lifeCycle: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeCycle = self.hallucinated_str(self.lifeCycle, text)
