from dataclasses import dataclass
from typing import Any

import Levenshtein
from rapidfuzz import fuzz


@dataclass
class BaseScorer:
    edit_dist: float = 0.0
    fuzzy_dist: float = 0.0
    cross_field: float = 0.0

    def cross_field_score(
        self, expect: Any, actual: Any, actual_record: dict[str, Any]
    ) -> None:
        self.cross_field = 0.0

    def fuzzy_score(self, expect: str, actual: str) -> None:
        self.fuzzy_dist = 0.0

    def edit_distance(self, expect: str, actual: str) -> None:
        expect = str(expect)
        actual = str(actual)
        self.edit_dist = Levenshtein.ratio(expect, actual)

    @property
    def score(self) -> float:
        return max(self.edit_dist, self.fuzzy_dist, self.cross_field)


@dataclass
class FuzzyScorer(BaseScorer):
    def fuzzy_score(self, expect: str, actual: str) -> None:
        expect = str(expect)
        actual = str(actual)
        self.fuzzy_dist = fuzz.partial_ratio(expect, actual) / 100.0
