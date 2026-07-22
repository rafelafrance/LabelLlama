import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class RecordedBy(ExtractedField):
    recordedBy: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.recordedBy = fix_parses.to_str(self.recordedBy)

        # Remove the collector label
        self.recordedBy = re.sub(r"^(collector|coll?)\b[.:,;]?\s+", "", self.recordedBy)
        self.recordedBy = self.recordedBy.strip()
