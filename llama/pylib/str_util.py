import re


def compress(text: str) -> str:
    return " ".join(text.split())


def clean_ocr(text: str) -> str:
    """Fix markup nonsense from the OCR engines."""
    text = re.sub(r"<br/?>", "\n", text)
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = text.strip()
    return text


def webify(text: str) -> str:
    """Convert text into a closer approximation of an HTML string."""
    text = text.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
    text = text.replace("\n", "<br/>")
    return text


def llm_reply_to_dict(content: str, columns: list[str]) -> dict:
    """Convert a LM reply in prompt_util.get_field_template format to a dict."""
    # Get field names and the values
    splits = re.split(r"^<< ## (\w+) ## >>$", content, flags=re.MULTILINE)

    # Remove first blank split
    if splits[0].strip() == "":
        splits = splits[1:]

    # Try to match field names with values
    as_dict = {
        k: v.strip()
        for k, v in zip(splits[::2], splits[1::2], strict=False)
        if k in columns
    }

    return as_dict

