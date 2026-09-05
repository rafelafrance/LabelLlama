from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Utm(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the full Universal Transverse Mercator (UTM) coordinate string from the
        label
        """
    # --------------

    utm: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utm = self.to_str(self.utm)
