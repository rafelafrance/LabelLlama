import re
from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

FLOWERS_PRESENT: str = compress("""Are there flowers on the plant?""")


@dataclass
class FlowersPresent(BaseField):
    flowersPresent: bool | str | None = field(default=False, metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.flowersPresent = fix_values.to_bool(self.flowersPresent)

        # Handle the case where the word "flowers" is being used as true
        if not self.flowersPresent:
            string = fix_values.to_str(self.flowersPresent)
            self.flowersPresent = bool(
                re.search(r"(fls|flower|fl)", string, flags=re.IGNORECASE)
            )

        self.flowersPresent = self.flowersPresent or ""


DEFAULTS = DotDict({f.name: f.default for f in fields(FlowersPresent)})
