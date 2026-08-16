from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class Sex(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the sex of the individual flower(s) or inflorescence on the specimen
        """
    # --------------

    sex: str = ""

    def __post_init__(self, text: str) -> None:
        self.sex = self.hallucinated_str(self.sex, text)
