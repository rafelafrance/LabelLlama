import re
from typing import Any

import dspy

from llama.signatures.all_signatures import SIGNATURES, AnySignature


class DwcExtract(dspy.Module):
    def __init__(self, signature: str) -> None:
        self.signature: AnySignature = SIGNATURES[signature]

        self.filter_pattern = self.setup_filter_pattern()

        self.predictor = dspy.Predict(self.signature)
        self.input_fields = self.signature.input_fields
        self.output_fields = self.signature.output_fields
        self.input_names: list[str] = list(self.input_fields.keys())
        self.output_names: list[str] = list(self.output_fields.keys())

    def forward(self, text: str) -> AnySignature:
        text = self.filter_lines(text)
        text = self.join_lines(text)
        specimen = self.predictor(text=text)
        return specimen

    def setup_filter_pattern(self) -> re.Pattern:
        """Build a regular expression for deleting lines from OCR text."""
        lines_to_filter: list[str] = [
            "academy",
            "academ",
            "botanic garden",
            "botanical",
            "center for",
            "database",
            "department of",
            "forest service",
            "government",
            "herbaria",
            "herbarium",
            "plant biology",
            "sciences",
            "university",
        ]
        filter_pattern = [rf"\b{e}\b" for e in lines_to_filter]

        filter_pattern = re.compile(
            f"({'|'.join(filter_pattern)})", flags=re.IGNORECASE
        )
        return filter_pattern

    def filter_lines(self, text: str) -> str:
        """
        Remove lines in the text that have certain words or phrases.

        These words/phrases are typically label headers or footers and "confuse"
        the language model with irrelevant data, so I remove them.
        """
        lines = [ln for ln in text.splitlines() if not self.filter_pattern.search(ln)]
        text = "\n".join(lines)
        return text

    def join_lines(self, text: str) -> str:
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

    def dict2example(self, dct: dict[str, Any]) -> dspy.Example:
        example: dspy.Example = dspy.Example(**dct).with_inputs(*self.input_names)
        return example
