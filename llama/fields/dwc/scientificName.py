import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class ScientificName(BaseField):
    scientificName: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.scientificName = fix_values.to_str(self.scientificName)
        self.scientificName = re.sub(r"[^\w\s]", "", self.scientificName).strip()

        words = self.scientificName.split()
        if len(words) == 0:
            self.scientificName = ""
        elif len(words) == 1:
            self.scientificName = words[0].capitalize()
        else:
            genus, species, *_ = words
            self.scientificName = f"{genus.capitalize()} {species.lower()}"
