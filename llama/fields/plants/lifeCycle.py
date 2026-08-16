from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class LifeCycle(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the plant's life cycle or duration (how long the plant lives over the
        course of its lifetime)
        """
    # --------------

    lifeCycle: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeCycle = self.hallucinated_str(self.lifeCycle, text)
