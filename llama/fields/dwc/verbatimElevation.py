from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class VerbatimElevation(BaseField):
    verbatimElevation: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimElevation = fix_values.to_str(self.verbatimElevation)

        # Remove the label
        words = self.verbatimElevation.split()
        words = [w for w in words if not w.lower().startswith("el")]
        words = [w for w in words if not w.lower().startswith("alt")]
        self.verbatimElevation = " ".join(words)
