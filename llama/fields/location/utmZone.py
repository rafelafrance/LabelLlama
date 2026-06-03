from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class UtmZone(BaseField):
    utmZone: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.utmZone = fix_values.to_str(self.utmZone)

        # Remove the zone label
        words = self.utmZone.split()
        words = [w for w in words if not w.lower().startswith("zone")]
        words = [w for w in words if w.lower() not in ("z", "z.")]
        self.utmZone = " ".join(words)
