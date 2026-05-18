from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

VERNACULAR_NAME: str = compress("""
    `vernacularName` (str):
    Extract the vernacular (or common) name of the species collected.
    Vernacular names are non-scientific names used by local people,
    often in English or other languages (e.g., 'White Oak', 'Mountain
    Lion', 'California Poppy', 'Red-tailed Hawk').
        ✅ Include: common names, trade names, and local language names.
            Preserve the name exactly as written, including any hyphens
            or apostrophes (e.g., 'Red-tailed Hawk', 'O'Malley's fern').
        ❌ DO NOT include: the scientific (Latin) name — that belongs in
            scientificName. Do not mix scientific and common names.
        ❌ DO NOT include: taxonomic ranks or labels (e.g., 'common name:',
            'vernacular:', 'nom. vulg.').
    If multiple vernacular names are present, return the primary one.
    If no vernacular name is stated, return an empty string.
    """)


@dataclass
class VernacularName(BaseField):
    vernacularName: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.vernacularName = fix_values.hallucinated_str(self.vernacularName, text)
