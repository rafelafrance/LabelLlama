import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


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
