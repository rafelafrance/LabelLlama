from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class InfraspecificEpithet(BaseField):
    infraspecificEpithet: str = ""

    def __post_init__(self) -> None:
        self.infraspecificEpithet = fix_parses.to_str(self.infraspecificEpithet).lower()
