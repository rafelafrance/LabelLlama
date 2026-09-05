from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class DecimalLatitude(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only decimal latitude coordinates already present in the text. Do not
        convert coordinates.
        """
    # --------------

    decimalLatitude: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        lat = self.to_float(self.decimalLatitude)
        self.decimalLatitude = lat if lat is not None else ""
