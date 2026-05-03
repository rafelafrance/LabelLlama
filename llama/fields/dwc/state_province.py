from dataclasses import dataclass, field

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

STATE_PROVINCE: str = compress(
    """The state or province where the specimen was collected."""
)


@dataclass
class StateProvince(BaseField):
    stateProvince: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.stateProvince = fix_values.hallucinated_str(self.stateProvince, text)
