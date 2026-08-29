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
        raw = self.to_str(self.decimalLongitude)
        long = self.to_float(self.normalize_decimal_comma(raw))
        # Clear values that are not a valid longitude (e.g. 200.0, or a
        # malformed number the decimal-comma rule did not resolve).
        self.decimalLongitude = "" if long is None or abs(long) > 180 else long
