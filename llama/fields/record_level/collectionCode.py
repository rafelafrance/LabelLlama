from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class CollectionCode(BaseField):
    collectionCode: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.collectionCode = fix_values.to_str(self.collectionCode)
