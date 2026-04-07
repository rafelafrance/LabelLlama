import re
from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, HIDE, BaseField


@dataclass
class CollectorNumber(BaseField):
    collectorNumber: str = field(default="", metadata=BOTH | HIDE)
    recordNumber: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.collectorNumber = fix_values.to_str(self.collectorNumber)
        self.collectorNumber = re.sub(r"(#|Nº)", "", self.collectorNumber)

        # Remove the record number label
        words = self.collectorNumber.split()
        words = [s for s in words if not s.lower().startswith("no")]
        words = [s for s in words if not s.lower().startswith("num")]
        words = [s for s in words if not s.lower().startswith("rec")]
        self.collectorNumber = " ".join(words)
        self.recordNumber = self.collectorNumber
