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


def join_lines(text: str) -> str:
    """
    Join lines of text if there is only one line break (return) between them.

    Labels have limited horizontal space, so sentences are split across multiple lines.
    However, the models tend to do better if there are no line breaks in a sentence.
    If there are two or more line breaks in a row then the break is likely to have
    semantic meaning, but if there is only one break then it probably doesn't.
    """
    text = re.sub(r"\n\s*\n", "<br>", text)
    text = text.replace("\n", " ")
    text = text.replace("<br>", "\n\n")
    text = text.strip()
    return text


def clean_text(text: str) -> str:
    text = filter_lines(text)
    text = join_lines(text)
    return text
