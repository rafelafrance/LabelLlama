from llama.score.base_scorer import BaseScorer, FuzzyScorer
from llama.score.country_scorer import CountryScorer
from llama.score.family_scorer import FamilyScorer

ALL_SCORERS = {
    "country": CountryScorer,
    "family": FamilyScorer,
    "habitat": FuzzyScorer,
    "locality": FuzzyScorer,
    "occurrenceRemarks": FuzzyScorer,
}


def get_scorer(field_name):
    return ALL_SCORERS.get(field_name, BaseScorer)