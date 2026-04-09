from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

STATE_PROVINCE: str = compress(
    """The state or province where the specimen was collected."""
)


@dataclass
class StateProvince(BaseField):
    stateProvince: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.stateProvince = fix_values.to_str(self.stateProvince).title()


DEFAULTS = DotDict({f.name: f.default for f in fields(StateProvince)})
