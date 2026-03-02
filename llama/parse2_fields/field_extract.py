from typing import Any

import dspy
from dspy import Prediction

from llama.common.preprocess import clean_text
from llama.parse2_fields.all_signatures import FIELD_SIGNATURES


class FieldExtract(dspy.Module):
    def __init__(self, signature: str) -> None:
        super().__init__()
        self.signature = FIELD_SIGNATURES[signature]
        self.predictor = dspy.Predict(self.signature)

        self.input_fields = self.signature.input_fields
        self.output_fields = self.signature.output_fields
        self.input_names: list[str] = list(self.input_fields.keys())
        self.output_names: list[str] = list(self.output_fields.keys())

    def forward(self, text: str) -> Prediction:
        text = clean_text(text)
        prediction = self.predictor(text=text)
        return prediction

    def dict2example(self, dct: dict[str, Any]) -> dspy.Example:
        example: dspy.Example = dspy.Example(**dct).with_inputs(*self.input_names)
        return example
