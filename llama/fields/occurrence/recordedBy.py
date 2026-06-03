import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class RecordedBy(BaseField):
    recordedBy: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.recordedBy = fix_values.to_str(self.recordedBy)

        # Remove the collector label
        self.recordedBy = re.sub(r"^(collector|coll?)\b[.:,;]?\s+", "", self.recordedBy)
