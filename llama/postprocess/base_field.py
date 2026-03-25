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

    @classmethod
    def cross_field_score(
        cls, expect: Any, actual: Any, actual_record: dict[str, Any]
    ) -> float:
        return 0.0

    @staticmethod
    def fuzzy_score(expect: str, actual: str) -> float:
        return 0.0

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
