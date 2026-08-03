from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class CollectionCode(ExtractedField):
    collectionCode: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.collectionCode = self.to_str(self.collectionCode)
