import unicodedata
from collections import Counter
from itertools import pairwise

import regex as re

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

# Substitutions performed on a consensus sequence
SUBSTITUTIONS = [
    # Remove gaps
    ("⋄", ""),
    # Replace underscores with spaces
    ("_", " "),
    # Replace ™ trademark with a double quote
    ("™", '"'),
    # Remove space before some punctuation: x . -> x.
    (r"(\S)\s+([;:.,°\)\]\}])", r"\1\2"),
    # Compress spaces
    (r"\s\s+", " "),
    # Convert single capital letter, punctuation to capital dot: L' -> L.
    (r"(\p{L}\s\p{Lu})\p{Po}", r"\1."),
    # Add spaces around an ampersand &
    (r"(\w)&", r"\1 &"),
    (r"&(\w)", r"& \1"),
    # Handle multiple dots ..
    (r"\.\.+", r"\."),
    # Confusion between dots . and colons :
    (r"::", r"\.:"),
    # Double single quotes '' should be a double quote "
    (r"['`]['`]", r"\""),
    # Replace @ and 0
    (r"(?<=\d)@(?=\d)", "0"),
    # October spelled with a zero
    ("0ct", "Oct"),
]


def filter_lines(lines: list[str], threshold: int = 128) -> list[str]:
    """Sort the lines by Levenshtein distance and filter out the outliers."""
    if len(lines) <= MIN_LEN:
        return lines

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
    cons = []
    for i in range(len(aligned[0])):
        counts = Counter(s[i] for s in aligned).most_common()
        top = counts[0][1]
        chars = [c[0] for c in counts if c[1] == top]
        chars = sorted(chars, key=_char_key)
        cons.append(chars[0])
    return "".join(cons)


def substitute(line: str) -> str:
    """Perform simple substitutions on a consensus string."""
    for old, new in SUBSTITUTIONS:
        line = re.sub(old, new, line)
    return line


def remove_repeated_suffix(text: str) -> str:
    """Remove repeated suffixes added by a lanuage model."""
    for i in range(-6, 0):  # Suffixes of length 6 to 1
        suffix = re.escape(text[i:])
        # Go thru the matches backwards to find the first repeated suffix
        matches = list(re.finditer(suffix, text))
        matches.reverse()
        suffixes_start = 0
        for m1, m2 in pairwise(matches):
            if m1.start() == m2.end():
                suffixes_start = m2.start()
            else:
                break
        if suffixes_start == 0:
            continue
        return text[:suffixes_start]

    return text


def post_process_text(text: str) -> str:
    text = text.strip()
    text = substitute(text)
    text = remove_repeated_suffix(text)
    text = text.strip()
    return text
