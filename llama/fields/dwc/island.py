from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

ISLAND: str = compress("""
    `island` (str):
    Extract the name(s) of the island(s) on or near which the specimen was
    collected. Return a list if multiple islands are mentioned.
        ✅ Include: named islands ('Hawaii', 'Isla de la Juventud', 'Jeju',
            'Vancouver Island', 'Isle of Wight'), atolls, cays, islets,
            and peninsulas when treated as islands on the label.
        ❌ DO NOT include island groups or archipelagos (e.g., 'Galápagos',
            'West Indies', 'Austral Islands') — those belong to islandGroup.
        ❌ DO NOT include country, state/province, or other administrative
            divisions — those have their own fields.
        ❌ DO NOT include general locality descriptions — those belong to
            locality.
    If no island is stated, return an empty string.
    """)


@dataclass
class Island(BaseField):
    island: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.island = fix_values.hallucinated_str(self.island, text)
