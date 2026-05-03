from dataclasses import dataclass, field

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

SIZES: str = compress("""
    Other sizes of the plant and plant parts like plant width, or flower size, etc.
    """)


@dataclass
class Sizes(BaseField):
    sizes: list[str] | str | None = field(default_factory=list, metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.sizes = fix_values.to_list_of_strs(self.sizes)
        self.sizes = fix_values.reduce_str_list(self.sizes)
