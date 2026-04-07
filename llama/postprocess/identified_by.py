from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class IdentifiedBy(BaseField):
    identifiedBy: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedBy = fix_values.to_str(self.identifiedBy)
