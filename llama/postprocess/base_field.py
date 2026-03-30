from dataclasses import dataclass, fields
from enum import Enum
from typing import Any


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
    def setup_field(cls) -> None:
        pass

    def run_field_model(self) -> None:
        pass

    def cross_field_update(self, record: dict[str, Any]) -> None:
        del record

    @classmethod
    def get_input_subfields(cls) -> list[str]:
        return [
            f.name
            for f in fields(cls)
            if f.metadata.get("in_out") in (InOut.IN, InOut.BOTH)
        ]

    @classmethod
    def get_output_subfields(cls) -> list[str]:
        return [
            f.name
            for f in fields(cls)
            if f.metadata.get("in_out") in (InOut.OUT, InOut.BOTH)
        ]
