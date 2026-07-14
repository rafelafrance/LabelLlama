from dataclasses import InitVar, dataclass, fields
from typing import Any, ClassVar

import Levenshtein


@dataclass
class BaseField:
    # --------------
    scoring_method: ClassVar[str] = "LR"
    # --------------

    text: InitVar[str] = ""

    def cross_field_update(self, record: dict[str, Any]) -> None:
        del record

    def __post_init__(self, text:str) -> None:
        """Stop LLM from setting the field value to the label (echo)."""
        del text

        first_field = self.get_field_names()[0]
        if getattr(self, first_field) == first_field:
            setattr(self, first_field, "")

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Get all of the field names within a class."""
        return [f.name for f in fields(cls)]

    @classmethod
    def get_visible_fields(cls) -> list[str]:
        """Get all visible field names within a class."""
        return [f.name for f in fields(cls) if not f.name.startswith("_")]

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        actual = str(actual).strip()
        expect = str(expect).strip()

        return Levenshtein.ratio(expect, actual)
