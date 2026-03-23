import re
from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class ScientificName(BaseField):
    scientificName: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.scientificName = fix_values.to_str(self.scientificName)
        self.scientificName = re.sub(r"[^\w\s]", "", self.scientificName).strip()

        words = self.scientificName.split()
        if len(words) == 0:
            self.scientificName = ""
        elif len(words) == 1:
            self.scientificName = words[0].title()
        else:
            genus, species, *_ = words
            self.scientificName = f"{genus.title()} {species.lower()}"
