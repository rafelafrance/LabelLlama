import re

# from bs4 import BeautifulSoup


def compress(text: str) -> str:
    return " ".join(text.split())


def dedent(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln]
    return "\n".join(lines)


def clean_response(text: str) -> str:
    text = re.sub(
        r" ^ .*? ( </think> | ```json ) ",
        "",
        str(text),
        flags=re.IGNORECASE | re.VERBOSE | re.DOTALL,
    )
    text = text.removesuffix("```")
    text = text.strip()
    return text


def strip_html(text: str) -> str:
    # TODO: Parse chandra-ocr-2 output
    text = clean_response(text)
    # text = re.sub(r"<br\s?/?>", r"\n\n", text)
    # soup = BeautifulSoup(text, "lxml")
    # text = soup.get_text(" ", strip=False)
    # text = text.strip()
    return text
