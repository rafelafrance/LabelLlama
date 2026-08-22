from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class LeafMargin(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract leaf-margin descriptions, such as entire, toothed, serrate, crenate,
        lobed, revolute, or undulate. Do not include overall leaf shape.
        """
    # --------------

    leafMargin: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafMargin = self.hallucinated_str(self.leafMargin, text)
