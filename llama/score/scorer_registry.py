from llama.fields.dwc.country import CountryScorer
from llama.fields.dwc.family import FamilyScorer
from llama.score.base_scorer import BaseScorer, FuzzyScorer

type Scorer = BaseScorer | FuzzyScorer | FamilyScorer | CountryScorer


SCORER_REGISTRY: dict[str, type[Scorer]] = {
    "country": CountryScorer,
    "family": FamilyScorer,
    "habitat": FuzzyScorer,
    "locality": FuzzyScorer,
    "occurrenceRemarks": FuzzyScorer,
}


def get_scorer(field_name: str) -> Scorer:
    return SCORER_REGISTRY.get(field_name, BaseScorer)()
