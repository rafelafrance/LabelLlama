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
    @classmethod
    def get_input_fields(cls) -> list[str]:
        return [
            f.name
            for f in fields(cls)
            if f.metadata.get("in_out") in (InOut.IN, InOut.BOTH)
        ]

    @classmethod
    def get_output_fields(cls) -> list[str]:
        return [
            f.name
            for f in fields(cls)
            if f.metadata.get("in_out") in (InOut.OUT, InOut.BOTH)
        ]
