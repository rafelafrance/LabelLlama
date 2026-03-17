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


def filter_lines(doc_text: str) -> str:
    """
    Remove lines in the text that have certain words or phrases.

    These words/phrases are typically label headers or footers and "confuse"
    the language model with irrelevant data, so I remove them.
    """
    lines = [ln for ln in doc_text.splitlines() if not FILTER_PATTERN.search(ln)]
    doc_text = "\n".join(lines)
    return doc_text


def join_lines(doc_text: str) -> str:
    """
    Join lines of text.

    Labels have limited space, so sentences are split across multiple lines.
    The models tend to do better if there are no line breaks in a sentence.
    If there are two or more line breaks in a row then the break is likely to have
    semantic meaning.
    """
    doc_text = re.sub(r"\n\s*\n", "<br>", doc_text)
    doc_text = doc_text.replace("\n", " ")
    doc_text = doc_text.replace("<br>", "\n\n")
    return doc_text


def clean_text(doc_text: str) -> str:
    doc_text = filter_lines(doc_text)
    doc_text = join_lines(doc_text)
    return doc_text
