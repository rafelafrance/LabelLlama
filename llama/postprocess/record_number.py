import re
from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class RecordNumber(BaseField):
    recordNumber: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.recordNumber = fix_values.to_str(self.recordNumber)

        self.recordNumber = re.sub(r"(#|Nº)", "", self.recordNumber)

        # Remove the record number label
        words = self.recordNumber.split()
        words = [s for s in words if not s.lower().startswith("no")]
        words = [s for s in words if not s.lower().startswith("num")]
        words = [s for s in words if not s.lower().startswith("rec")]
        self.recordNumber = " ".join(words)
