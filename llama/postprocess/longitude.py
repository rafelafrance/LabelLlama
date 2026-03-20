from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import OUT, BaseField


@dataclass
class Longitude(BaseField):
    verbatimLongitude: str = field(default="", metadata=OUT)

    def __post_init__(self) -> None:
        self.verbatimLongitude = fix_values.to_str(self.verbatimLongitude)
