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
        raw = self.to_str(self.decimalLatitude)
        lat = self.to_float(self.normalize_decimal_comma(raw))
        # Clear values that are not a valid latitude (e.g. 95.0, or a
        # malformed number the decimal-comma rule did not resolve).
        self.decimalLatitude = "" if lat is None or abs(lat) > 90 else lat
