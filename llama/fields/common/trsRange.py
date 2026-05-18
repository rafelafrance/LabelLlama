import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class Trs(BaseField):
    trsRange: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.trsRange = fix_values.to_str(self.trsRange)
        self.trsRange = re.sub(r"^r\s*", "", self.trsRange, flags=re.IGNORECASE)
