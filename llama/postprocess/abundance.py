from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class Abundance(BaseField):
    abundance: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.abundance = fix_values.to_str(self.abundance)
        self.abundance = fix_values.remove_trailing_punct(self.abundance)
