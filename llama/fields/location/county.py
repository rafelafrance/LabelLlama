import re
from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class County(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the county, parish, or equivalent second-level administrative division
        where the specimen was collected
        """
    # --------------

    county: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.county = self.to_str(self.county)

        # Remove the county label
        self.county = re.sub(r"\b(co\.?|county)$", "", self.county, flags=re.IGNORECASE)
        self.county = self.county.strip()
