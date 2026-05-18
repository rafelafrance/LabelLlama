from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class InfraspecificEpithet(BaseField):
    infraspecificEpithet: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.infraspecificEpithet = fix_values.to_str(self.infraspecificEpithet).lower()
