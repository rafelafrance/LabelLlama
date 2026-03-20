from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import OUT, BaseField


@dataclass
class Municipality(BaseField):
    municipality: str = field(default="", metadata=OUT)

    def __post_init__(self) -> None:
        self.municipality = fix_values.to_str(self.municipality)
