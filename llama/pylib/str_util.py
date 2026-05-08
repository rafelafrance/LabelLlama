import re


def compress(text: str) -> str:
    return " ".join(text.split())


def clean_response(text: str) -> str:
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
