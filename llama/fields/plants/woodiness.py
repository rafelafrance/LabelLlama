from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class Woodiness(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the degree of woodiness of the plant (whether the stem is woody or
        herbaceous)
        """
    # --------------

    woodiness: str = ""

    def __post_init__(self, text: str) -> None:
        self.woodiness = self.hallucinated_str(self.woodiness, text)
