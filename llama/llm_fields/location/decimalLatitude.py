import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField

# A southern hemisphere marker, in front of or behind the number.
SOUTHERN = re.compile(r"[sS]\s*\d|\d\s*[sS]")


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
        # "S45.5" and "45.5 S" are the southern hemisphere, so negative.
        if lat is not None and SOUTHERN.search(raw):
            lat = -abs(lat)
        # Clear values that are not a valid latitude (e.g. 95.0, or a
        # malformed number the decimal-comma rule did not resolve).
        self.decimalLatitude = "" if lat is None or abs(lat) > 90 else lat
