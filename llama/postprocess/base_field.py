from dataclasses import dataclass, fields
from enum import Enum


class InOut(Enum):
    IN = 1
    OUT = 2
    BOTH = 3


IN = {"in_out": InOut.IN}
OUT = {"in_out": InOut.OUT}
BOTH = {"in_out": InOut.BOTH}


@dataclass
class BaseField:
    def get_input_fields(self) -> list[str]:
        return [
            f.name for f in fields(self)
            if f.metadata.get("in_out", 0) in (InOut.IN, InOut.BOTH)
        ]

    def get_output_fields(self) -> list[str]:
        return [
            f.name for f in fields(self)
            if f.metadata.get("in_out", 0) in (InOut.OUT, InOut.BOTH)
        ]