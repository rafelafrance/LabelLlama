from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

ISLAND_GROUP: str = compress("""
    `islandGroup` (str):
    Extract the name of the island group, archipelago, or atoll group where
    the specimen was collected.
        ✅ Include: archipelagos ('Galápagos', 'Aleutian Islands', 'Lesser
            Antilles', 'Austral Islands'), island groups ('West Indies',
            'Mariana Islands', 'Bismarck Archipelago'), atoll groups,
            and named clusters of islands.
        ❌ DO NOT include individual island names (e.g., 'Hawaii',
            'Vancouver Island', 'Isla de la Juventud') — those belong to
            island.
        ❌ DO NOT include country, state/province, or other administrative
            divisions — those have their own fields.
        ❌ DO NOT include general locality descriptions — those belong to
            locality.
    If no island group is stated, return an empty string.
    """)


@dataclass
class IslandGroup(BaseField):
    islandGroup: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.islandGroup = fix_values.hallucinated_str(self.islandGroup, text)
