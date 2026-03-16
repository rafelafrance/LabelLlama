import re

from llama.lm.preprocess import filter_lines


def join_lines(doc_text: str) -> str:
    """
    Join lines of text.

    Labels have limited space, so sentences are split across multiple lines.
    The models tend to do better if there are no line breaks in a sentence.
    If there are two or more line breaks in a row then the break is likely to have
    semantic meaning.
    """
    doc_text = re.sub(r"\n\s*\n", "<br>", doc_text)
    doc_text = doc_text.replace("\n", " ")
    doc_text = doc_text.replace("<br>", "\n\n")
    return doc_text


def clean_text(doc_text: str) -> str:
    doc_text = filter_lines(doc_text)
    doc_text = join_lines(doc_text)
    return doc_text
