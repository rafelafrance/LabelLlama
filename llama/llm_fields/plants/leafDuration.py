from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class LeafDuration(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract leaf-duration terms such as evergreen, deciduous, semi-evergreen,
        annual leaves, or persistent leaves when explicitly stated.
        """
    # --------------

    leafDuration: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafDuration = self.hallucinated_str(self.leafDuration, text)
