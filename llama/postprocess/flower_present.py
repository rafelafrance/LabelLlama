from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class FlowersPresent(BaseField):
    flowersPresent: bool = field(default=False, metadata=BOTH)

    def __post_init__(self) -> None:
        self.flowersPresent = fix_values.to_bool(self.flowersPresent)
