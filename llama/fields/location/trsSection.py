from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class TrsSection(BaseField):
    trsSection: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.trsSection = fix_values.to_str(self.trsSection)

        # Remove section label
        words = self.trsSection.split()
        words = [w for w in words if not w.lower().startswith("sec")]
        words = [w for w in words if w.lower() not in ("s", "s.")]
        self.trsSection = " ".join(words)
