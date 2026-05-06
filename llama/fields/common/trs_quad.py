from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

TRS_QUAD: str = compress("""
    `trsQuad` (str):
    Extract the quadrangle (quad) name associated with the TRS coordinates.
    The quad may appear before or after the other TRS fields. Examples:
    'USGS Wahtoke 7 1/2 quad', 'Yountville Quad', 'Chicken Hawk Hill quadrangle',
    'Mt. Ingalls quad.'. Return only the quad name, not the 'quad' label.
    If no quadrangle is mentioned, return an empty string.
    """)


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
