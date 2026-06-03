from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class ScientificNameAuthorship(BaseField):
    scientificNameAuthorship: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.scientificNameAuthorship = fix_values.to_str(self.scientificNameAuthorship)
        self.scientificNameAuthorship = fix_values.clean_str_ends(
            self.scientificNameAuthorship
        )
