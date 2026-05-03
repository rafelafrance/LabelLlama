def compress(text: str) -> str:
    return " ".join(text.split())


def clean_response(text: str) -> str:
    text = text.strip()
    return text

