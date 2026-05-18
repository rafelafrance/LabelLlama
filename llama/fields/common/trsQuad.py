from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class Trs(BaseField):
    trsQuad: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.trsQuad = fix_values.to_str(self.trsQuad)

        # Remove quad label
        words = self.trsQuad.split()
        words = [w for w in words if not w.lower().startswith("quad")]
        words = [w for w in words if w.lower() not in ("q", "q.")]
        self.trsQuad = " ".join(words)
