from llama.score.base_scorer import BaseScorer, FuzzyScorer
from llama.score.country_scorer import CountryScorer
from llama.score.family_scorer import FamilyScorer

type Scorer = BaseScorer | FuzzyScorer | FamilyScorer | CountryScorer


ALL_SCORERS: dict[str, type[Scorer]] = {
    "country": CountryScorer,
    "family": FamilyScorer,
    "habitat": FuzzyScorer,
    "locality": FuzzyScorer,
    "occurrenceRemarks": FuzzyScorer,
}


def get_scorer(field_name: str) -> Scorer:
    return ALL_SCORERS.get(field_name, BaseScorer)()
