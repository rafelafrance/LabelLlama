from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class StateProvince(BaseField):
    stateProvince: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.stateProvince = fix_values.to_str(self.stateProvince).title()
