from typing import Any


class FieldAction:
    def __init__(self, verbatim: str) -> None:
        self.verbatim = verbatim
        self.predictor = lambda text: {self.field_name(): text}

    def field_name(self) -> str:
        name = self.__class__.__name__
        return name[0].lower() + name[1:]

    def preprocess(self, text: str, ocr_text: str) -> str:
        return text

    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        return subfields

    def __call__(self, text: str, ocr_text: str) -> dict[str, Any]:
        cleaned = self.preprocess(text=text, ocr_text=ocr_text)
        subfields = self.predictor(text=cleaned)
        subfields = self.postprocess(subfields=subfields, text=text)
        return subfields
