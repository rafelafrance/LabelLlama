from typing import NamedTuple

import Levenshtein


class Distance(NamedTuple):
    dist: int
    idx1: int
    idx2: int


def levenshtein_all(strings: list[str]) -> list[Distance]:
    """
    Compute a Levenshtein distance for every pair of strings in the list.

    @param strings A list of strings to compare.
    @return A sorted list of Distance objects, each contain:
        - dist: The Levenshtein distance of the pair of strings.
        - idx1: The index of the first string compared.
        - idx2: The index of the second string compared.
        The Distance objects are sorted by distance.
    """
    results: list[Distance] = []

    len_ = len(strings)

    for i in range(len_ - 1):
        for j in range(i + 1, len_):
            dist = Levenshtein.distance(strings[i], strings[j])
            results.append(Distance(dist, i, j))

    results = sorted(results, key=lambda r: (r.dist, r.idx1, r.idx2))

    return results
