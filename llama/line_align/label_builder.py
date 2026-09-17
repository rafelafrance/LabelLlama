import unicodedata
from collections import Counter
from copy import copy

from llama.line_align.align import GAP_CHAR
from llama.line_align.levenshtein import levenshtein_all

MIN_LEN = 2

# When there is no clear "winner" for a character in the multiple alignment of
# a set of strings I sort the characters by Unicode category as a tiebreaker
CATEGORY = {
    "Lu": 20,
    "Ll": 20,
    "Lt": 20,
    "Lm": 20,
    "Lo": 20,
    "Nd": 30,
    "Nl": 60,
    "No": 60,
    "Pc": 70,
    "Pd": 40,
    "Ps": 50,
    "Pe": 50,
    "Pi": 50,
    "Pf": 50,
    "Po": 10,
    "Sm": 99,
    "Sc": 90,
    "So": 90,
    "Zs": 80,
}

# As, above, but if a character has a category of "punctuation other" then I
# sort by the weight for the character itself
PO = {
    ".": 1,
    ",": 2,
    ":": 2,
    ";": 2,
    "!": 5,
    '"': 5,
    "'": 5,
    "*": 5,
    "/": 5,
    "%": 6,
    "&": 6,
}


def filter_lines(lines: list[str], threshold: int = 128) -> list[str]:
    """Filter out strings with a large distance from the others."""
    if len(lines) <= MIN_LEN:
        return copy(lines)

    # levenshtein_all() returns a sorted array of Distance named tuples/objects
    distances = levenshtein_all(lines)

    threshold += distances[0].dist  # Score cannot be more than best score + threshold

    order = {}  # Dicts preserve insertion order, sets do not
    for score, i, j in distances:
        if score > threshold:
            break
        order[i] = 1
        order[j] = 1

    ordered = [lines[k] for k in order]
    return ordered


def _char_key(char: str) -> tuple:
    """Get the character sort order."""
    order = CATEGORY.get(unicodedata.category(char), 100)
    order = PO.get(char, order)
    return order, char


def find_consensus(aligned: list[str]) -> str:
    """
    Build a consensus string from the aligned copies.

    Look at all characters of the multiple alignment and choose the most common one,
    using heuristics as a tiebreaker.
    """
    if not aligned:
        return ""

    longest = max(len(a) for a in aligned)
    aligned = [a + GAP_CHAR * (longest - len(a)) for a in aligned]

    cons = []
    for i in range(len(aligned[0])):
        counts = Counter(s[i] for s in aligned).most_common()
        top = counts[0][1]
        chars = [c[0] for c in counts if c[1] == top]
        chars = sorted(chars, key=_char_key)
        cons.append(chars[0])

    seq = "".join(cons)
    seq = seq.replace(GAP_CHAR, "")
    return seq
