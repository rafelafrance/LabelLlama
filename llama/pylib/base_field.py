from dataclasses import dataclass, fields
from typing import Any, ClassVar

import Levenshtein


@dataclass
class BaseField:
    # --------------
    scoring_method: ClassVar[str] = "LR"
    # --------------

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
