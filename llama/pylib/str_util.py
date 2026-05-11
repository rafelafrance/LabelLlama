import re


def compress(text: str) -> str:
    return " ".join(text.split())


def clean_response(text: str) -> str:
    text = text.strip()
    return text


def clean_ocr(text: str) -> str:
    """Fix markup nonsense from the OCR engines."""
    text = re.sub(r"<br/?>", "\n", text)
    text = text.strip()
    return text


def snake_to_camel(text: str) -> str:
    words = text.split("_")
    words = [words[0]] + [w.capitalize() for w in words[1:]]
    words = [w.upper() if w == "Id" else w for w in words]
    camel = "".join(words)
    return camel


def camel_to_snake(text: str) -> str:
    return re.sub(r"([A-Z]+)", r"_\1", text).lower()


def strip_json_fences(text: str) -> str:
    """
    Remove markdown code fences wrapping JSON content.

    Handles any language tag (json, python, text, etc.), extra whitespace,
    and varying numbers of backticks. Strips the outermost matching fence
    pair if present, otherwise returns the text unchanged.
    """
    stripped = text.strip()
    fence_re = re.compile(r"^(`{3,})(\w*)?\n(.*?)\n\s*\1\s*$", re.DOTALL)
    match = fence_re.match(stripped)
    if match:
        return match.group(3).strip()
    return stripped


def llm_reply_to_dict(content: str, fields: list[str]) -> dict:
    """Convert a LM reply in prompt_util.get_field_template format to JSON."""
    # Get field names and the values
    splits = re.split(r"^<< ## (\w+) ## >>$", content, flags=re.MULTILINE)

    # Remove first blank split
    if splits[0].strip() == "":
        splits = splits[1:]

    # Try to match field names with values
    as_dict = {
        k: v.strip()
        for k, v in zip(splits[::2], splits[1::2], strict=False)
        if k in fields
    }

    return as_dict


def to_positive_float(value: str | float) -> float | None:
    """Convert a string to a float stripping bad characters from the string first."""
    if isinstance(value, str):
        value = re.sub(r"[^\d./]", "", value) or ""
    try:
        return float(value)
    except ValueError, TypeError:
        return None


def to_positive_int(value: str | float) -> int | None:
    """Convert a string to an int stripping bad characters from the string first."""
    if isinstance(value, str):
        value = re.sub(r"[^\d./]", "", value) if value else ""
        value = re.sub(r"\.$", "", value)
    try:
        return int(value)
    except ValueError, TypeError:
        return None
