import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, HIDE, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

IDENTIFIED_BY_ID: str = compress("""
    `identifiedByID` (str):
    Extract the globally unique identifier for the person, people, groups,
    or organizations responsible for assigning the taxon to the subject.
    If no identified by ID is present, return an empty string.
    """)


@dataclass
class IdentifiedByID(BaseField):
    identifiedByID: str = field(default="", metadata=BOTH | HIDE)

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedByID = fix_values.to_str(self.identifiedByID)
        self.identifiedByID = re.sub(r"(#|Nº)", "", self.identifiedByID)

        # Remove the record number label
        words = self.identifiedByID.split()
        words = [s for s in words if not s.lower().startswith("no")]
        words = [s for s in words if not s.lower().startswith("num")]
        words = [s for s in words if not s.lower().startswith("rec")]
        self.identifiedByID = " ".join(words)
