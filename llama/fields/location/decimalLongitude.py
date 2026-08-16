from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class DecimalLongitude(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the decimal longitude at which the specimen was collected
        """
    # --------------

    decimalLongitude: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        long = self.to_float(self.decimalLongitude)
        self.decimalLongitude = long if long is not None else ""
