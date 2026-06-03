from dataclasses import InitVar, dataclass, fields
from typing import Any

import Levenshtein


@dataclass
class BaseField:
    text: InitVar[str] = ""

    def cross_field_update(self, record: dict[str, Any]) -> None:
        del record

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Get all of the field names within a class."""
        return [f.name for f in fields(cls)]

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        actual = str(actual).strip()
        expect = str(expect).strip()

        return Levenshtein.ratio(expect, actual)
