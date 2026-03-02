import re

from llama.parse1_text.preprocess import filter_lines


def join_lines(text: str) -> str:
    """
    Join lines of text.

    Labels have limited space, so sentences are split across multiple lines.
    The models tend to do better if there are no line breaks in a sentence.
    If there are two or more line breaks in a row then the break is likely to have
    semantic meaning.
    """
    text = re.sub(r"\n\s*\n", "<br>", text)
    text = text.replace("\n", " ")
    text = text.replace("<br>", "\n\n")
    return text


def clean_text(text: str) -> str:
    text = filter_lines(text)
    text = join_lines(text)
    return text
