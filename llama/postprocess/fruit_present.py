import re
from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class FruitPresent(BaseField):
    fruitPresent: bool | None = field(default=False, metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.fruitPresent = fix_values.to_bool(self.fruitPresent)

        # Handle the case where the word "fruits" is being used as true
        if not self.fruitPresent:
            string = fix_values.to_str(self.fruitPresent)
            self.fruitPresent = bool(
                re.search(r"(fr|fruit)", string, flags=re.IGNORECASE)
            )
