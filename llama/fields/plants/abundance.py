from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class Abundance(BaseField):
    abundance: str = ""

    def __post_init__(self, text: str) -> None:
        self.abundance = fix_values.hallucinated_str(self.abundance, text)
        self.abundance = fix_values.remove_trailing_punct(self.abundance)
