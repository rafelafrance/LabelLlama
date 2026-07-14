from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Abundance(BaseField):
    abundance: str = ""

    def __post_init__(self, text: str) -> None:
        self.abundance = fix_parses.hallucinated_str(self.abundance, text)
        self.abundance = fix_parses.remove_trailing_punct(self.abundance)
