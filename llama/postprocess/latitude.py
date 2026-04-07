from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class Latitude(BaseField):
    verbatimLatitude: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimLatitude = fix_values.to_str(self.verbatimLatitude)
