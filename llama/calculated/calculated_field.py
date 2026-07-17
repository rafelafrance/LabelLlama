from dataclasses import InitVar, dataclass, field
from typing import Any, ClassVar

import Levenshtein


@dataclass
class CalculatedField:
    # --------------
    scoring_method: ClassVar[str] = "LR"
    # --------------

    record: InitVar[dict[str, Any]] = field(default_factory=dict)

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        actual = str(actual).strip()
        expect = str(expect).strip()

        return Levenshtein.ratio(expect, actual)
