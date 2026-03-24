from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class InfraspecificEpithet(BaseField):
    infraspecificEpithet: list[str] | str | None = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        values = fix_values.to_list_of_strs(self.infraspecificEpithet)
        values = [v.lower() for v in values]
        self.infraspecificEpithet = fix_values.reduce_list(values)
