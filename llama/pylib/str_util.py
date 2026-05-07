import re


def compress(text: str) -> str:
    return " ".join(text.split())


def clean_response(text: str) -> str:
    text = text.strip()
    return text


def snake_to_camel(text: str) -> str:
    words = text.split()
    return words[0] + "".join(word.capitalize() for word in words[1:])


def camel_to_snake(text: str) -> str:
    return re.sub("([A-Z]+)", r"_\1", text).lower()
