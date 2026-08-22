from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class DecimalLongitude(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only decimal longitude coordinates already present in the text. Do not
        convert coordinates.
        """
    # --------------

    decimalLongitude: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        long = self.to_float(self.decimalLongitude)
        self.decimalLongitude = long if long is not None else ""
