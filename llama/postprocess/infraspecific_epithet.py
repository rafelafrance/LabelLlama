from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class InfraspecificEpithet(BaseField):
    infraspecificEpithet: str | None = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.infraspecificEpithet = fix_values.to_str(self.infraspecificEpithet).lower()
