import re

import dspy

from llama.data_formats.herbarium_sheet import HerbariumSheet
from llama.data_formats.ocr_image import OcrImage

type SpecimenType = HerbariumSheet | OcrImage

SPECIMEN_TYPES = {
    "herbarium": HerbariumSheet,
    "ocr": OcrImage,
}


class DwcExtract(dspy.Module):
    def __init__(self, specimen_type: str) -> None:
        self.specimen_type = SPECIMEN_TYPES[specimen_type]

        self.filter_pattern = self.setup_filter_pattern()

        self.predictor = dspy.Predict(self.specimen_type)

    def setup_filter_pattern(self) -> re.Pattern:
        # Set up the line filter
        lines_to_filter = [
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

        Labels have limited space so sentences are split across multiple lines.
        The models tend to do better if there are no line breaks in a sentence.
        It is better to have long text than short broken phrases. If there are two
        or more line breaks in a row then the break is likely to have semantic meaning.
        """
        text = re.sub(r"\n\s*\n", "<br>", text)
        text = text.replace("\n", " ")
        text = text.replace("<br>", "\n\n")
        return text

    def forward(self, text: str) -> SpecimenType:
        text = self.filter_lines(text)
        text = self.join_lines(text)
        specimen = self.predictor(text)
        return specimen
