import re


def setup_filter_pattern() -> re.Pattern:
    """Build a regular expression for deleting lines from OCR text."""
    lines_to_filter: list[str] = [
        "academy",
        "academ",
        "botanic garden",
        "botanical",
        "center for",
        "database",
        "department of",
        "forest service",
        "government",
        "herbaria",
        "herbarium",
        "plant biology",
        "sciences",
        "university",
    ]
    filter_pattern = [rf"\b{e}\b" for e in lines_to_filter]

    filter_pattern = re.compile(f"({'|'.join(filter_pattern)})", flags=re.IGNORECASE)
    return filter_pattern


FILTER_PATTERN: re.Pattern[str] = setup_filter_pattern()


def filter_lines(text: str) -> str:
    """
    Remove lines in the text that have certain words or phrases.

    These words/phrases are typically label headers or footers and "confuse"
    the language model with irrelevant data, so I remove them.
    """
    lines = [ln for ln in text.splitlines() if not FILTER_PATTERN.search(ln)]
    text = "\n".join(lines)
    return text


