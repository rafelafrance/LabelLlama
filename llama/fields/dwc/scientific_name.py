import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SCIENTIFIC_NAME: str = compress("""
    `scientificName` (list[str]):
    Extract the scientific (binomial) name of the specimen.
    Format as 'Genus species' with Genus capitalized and species lowercase.
    Include the species epithet only — do not include subspecies, varieties,
    or any authorship citations (e.g., 'L.', 'Smith & Jones').
    If the specimen is identified only to genus, return the genus name alone.
    If marked as unidentified (e.g., 'sp.', 'spp.'), include that notation.
    For hybrids, include the hybrid symbol (×) if present in the source text.
    """)


@dataclass
class ScientificName(BaseField):
    scientificName: list[str] | str = field(default_factory=list, metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.scientificName = fix_values.to_list_of_strs(self.scientificName)
        self.scientificName = [c for n in self.scientificName if (c := self.clean(n))]
        self.scientificName = fix_values.reduce_str_list(self.scientificName)

    @staticmethod
    def clean(value: str) -> str:
        value = fix_values.to_str(value)
        value = re.sub(r"[^\w\s]", "", value).strip()

        words = value.split()
        if len(words) == 0:
            value = ""
        elif len(words) == 1:
            value = words[0].capitalize()
        else:
            genus, species, *_ = words
            value = f"{genus.capitalize()} {species.lower()}"

        return value
