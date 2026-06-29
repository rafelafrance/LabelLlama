import re

from markdownify import markdownify as md


def setup_filter_pattern() -> re.Pattern:
    """Build a regular expression for deleting lines from OCR text."""
    lines_to_filter: list[str] = [
        "academ",
        "academy",
        "botanic garden",
        "botanical",
        "center for",
        "database",
        "department of",
        "forest service",
        "government",
        "herbaria",
        "herbarium",
        "museum of",
        "natural history",
        "plant biology",
        "sciences",
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


def remove_identical_lines(text: str) -> str:
    """
    Remove identical lines.

    Sometimes the OCR model will get stuck in a loop and repeat the same line over and
    over again. Even with a max output tokens setting this can get fairly long. This
    removes duplicate lines.

    Note that I want to keep blank lines or lines with all spaces, but I'll still strip
    the spaces at the ends of the line. See the join_lines function for why I want to
    keep empty lines.
    """
    seen = set()
    lines = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln not in seen:
            seen.add(ln)
            lines.append(ln)
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


def fix_entities(text: str) -> str:
    """Change entities and some HTML to characters."""
    text = re.sub(r"<br/?>", "\n", text)
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = text.strip()
    return text


def prepare_for_llm(text: str) -> str:
    """Prepare OCR results for running them thru an LLM."""
    text = fix_entities(text)
    text = remove_identical_lines(text)
    text = filter_lines(text)
    text = join_lines(text)
    return text


def clean_ocr(text: str) -> str:
    """Clean OCR results."""
    text = fix_entities(text)
    text = remove_identical_lines(text)
    return text


def html_to_md(text: str) -> str:
    """Convert HTML to markdown."""
    text = md(
        text,
        strip=["img"],
        escape_asterisks=False,
        escape_underscores=False,
        escape_misc=False,
    )
    return text
