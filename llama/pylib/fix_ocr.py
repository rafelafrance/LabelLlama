import html
import re

from markdownify import markdownify as md

# Words/phrases typically found in label headers or footers that "confuse" the
# language model with irrelevant data. Kept at module level so callers can
# extend or override them without editing filter_lines.
FILTER_WORDS: tuple[str, ...] = (
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
)


def setup_filter_pattern(
    words: tuple[str, ...] = FILTER_WORDS,
) -> re.Pattern[str]:
    """Build a regular expression for deleting lines from OCR text."""
    pattern = [rf"\b{word}\b" for word in words]
    return re.compile(f"({'|'.join(pattern)})", flags=re.IGNORECASE)


FILTER_PATTERN: re.Pattern[str] = setup_filter_pattern()


def filter_lines(text: str, pattern: re.Pattern[str] = FILTER_PATTERN) -> str:
    """
    Remove lines in the text that contain any of the filter words/phrases.

    These words/phrases are typically label headers or footers and "confuse"
    the language model with irrelevant data, so I remove them. Pass a custom
    `pattern` (built by setup_filter_pattern) to extend or override the defaults.
    """
    lines = [ln for ln in text.splitlines() if not pattern.search(ln)]
    text = "\n".join(lines)
    text = text.strip()
    return text


def remove_identical_lines(text: str) -> str:
    """
    Remove any line that has already appeared earlier in the text.

    Sometimes the OCR model will get stuck in a loop and repeat the same line over
    and over again. Even with a max output tokens setting this can get fairly
    long. This removes duplicate lines.

    Note that the dedup is global, not just for consecutive repeats: any line that
    has appeared before is dropped, wherever it occurs.

    Note also that I want to keep blank lines or lines with all spaces, but I'll
    still strip the spaces at the ends of the line. See the join_lines function
    for why I want to keep empty lines.
    """
    seen = set()
    lines = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln not in seen:
            seen.add(ln)
            lines.append(ln)
    text = "\n".join(lines)
    text = text.strip()
    return text


def join_lines(text: str) -> str:
    """
    Join lines of text if there is only one line break (return) between them.

    Labels have limited horizontal space, so sentences are split across multiple
    lines. However, the models tend to do better if there are no line breaks in a
    sentence. If there are two or more line breaks in a row then the break is
    likely to have semantic meaning, but if there is only one break then it
    probably doesn't.
    """
    # Use a NUL sentinel, which cannot appear in OCR text, rather than a literal
    # "<br>", so any pre-existing "<br>" content is left untouched.
    text = re.sub(r"\n\s*\n", "\x00", text)
    text = text.replace("\n", " ")
    text = text.replace("\x00", "\n\n")
    text = text.strip()
    return text


def fix_entities(text: str) -> str:
    """Change HTML entities and <br> tags to their character equivalents."""
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
    text = html.unescape(text)
    # Normalize a non-breaking space (&nbsp;) to a regular space.
    text = text.replace("\xa0", " ")
    text = text.strip()
    return text


def prepare_for_parse(text: str) -> str:
    """Prepare OCR results for running them thru an LLM."""
    text = remove_identical_lines(fix_entities(text))
    text = filter_lines(text)
    text = join_lines(text)
    text = text.strip()
    return text


def clean_ocr(text: str) -> str:
    """Clean OCR results."""
    text = remove_identical_lines(fix_entities(text))
    text = text.strip()
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

    # Remove bold/italic markdown markers, but only when they sit at a
    # whitespace or string boundary so snake_case tokens (e.g. "my_file_name",
    # "BRCA_1") and arithmetic like "2 * 3 * 4" are left intact.
    text = re.sub(r"(?<!\S)([*_]+)(\S.*?)\1(?!\S)", r"\2", text)

    text = text.strip()
    return text
