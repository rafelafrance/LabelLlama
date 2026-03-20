from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class ScientificName(BaseField):
    scientificName: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.scientificName = fix_values.to_str(self.scientificName)
        genus, species, *_ = self.scientificName.split()
        self.scientificName = f"{genus.title()} {species.lower()}"