from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

UTM_ZONE: str = compress("""
    `utmZone` (str):
    Extract the zone portion of the UTM coordinates. It will look like
    '10S', '11', '8N', 'Zone 11S', 'NH', '16P'. Return only the zone value,
    not the 'Zone' label.
    If no zone is present, return an empty string.
    """)


@dataclass
class Utm(BaseField):
    utmZone: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.utmZone = fix_values.to_str(self.utmZone)

        # Remove the zone label
        words = self.utmZone.split()
        words = [w for w in words if not w.lower().startswith("zone")]
        words = [w for w in words if w.lower() not in ("z", "z.")]
        self.utmZone = " ".join(words)
