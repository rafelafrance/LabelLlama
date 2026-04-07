from dataclasses import InitVar, dataclass, fields
from enum import Flag, auto
from typing import Any


class Flags(Flag):
    IN = auto()
    OUT = auto()
    HIDE = auto()


IN = {"in_out": Flags.IN}
OUT = {"in_out": Flags.OUT}
BOTH = {"in_out": Flags.IN | Flags.OUT}
HIDE = {"visible": Flags.HIDE}


@dataclass
class BaseField:
    text: InitVar[str] = ""

    @classmethod
    def setup_postprocessing(cls) -> None:
        pass

    @classmethod
    def cleanup_postprocessing(cls) -> None:
        pass

    def run_field_model(self) -> None:
        pass

    def cross_field_update(self, record: dict[str, Any]) -> None:
        del record

    @classmethod
    def get_input_subfields(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.metadata.get("in_out", 0) & Flags.IN]

    @classmethod
    def get_output_subfields(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.metadata.get("in_out", 0) & Flags.OUT]

    @classmethod
    def get_visible_subfields(cls) -> list[str]:
        return [
            f.name
            for f in fields(cls)
            if f.metadata.get("in_out", 0) & Flags.OUT
            and not f.metadata.get("visible", 1) & Flags.HIDE
        ]
