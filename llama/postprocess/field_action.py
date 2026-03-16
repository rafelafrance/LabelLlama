from typing import Any


class FieldAction:
    def __init__(self, verbatim: str) -> None:
        self.verbatim = verbatim
        self.predictor = lambda field_value: {self.field_name(): field_value}

    def field_name(self) -> str:
        name = self.__class__.__name__
        return name[0].lower() + name[1:]

    def preprocess(self, field_value: str, doc_text: str) -> str:
        return field_value

    def postprocess(self, subfields: dict[str, Any], doc_text: str) -> dict[str, Any]:
        return subfields

    def __call__(
        self, field_value: str, subfields: dict[str, Any], doc_text: str
    ) -> dict[str, Any]:
        field_value = self.preprocess(field_value=field_value, doc_text=doc_text)
        subfields = self.predictor(field_value=field_value)
        subfields = self.postprocess(subfields=subfields, doc_text=doc_text)
        return subfields
