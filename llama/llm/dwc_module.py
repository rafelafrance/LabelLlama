from datetime import datetime
from typing import Any

import dspy

from llama.pylib.preprocess import clean_text
from llama.llm.signature_registry import SIGNATURE_REGISTRY


class DwcModule(dspy.Module):
    def __init__(self, signature: str) -> None:
        super().__init__()
        self.signature = SIGNATURE_REGISTRY[signature]
        self.predictor = dspy.Predict(self.signature)

    def forward(self, text: str, source: str) -> dict[str, Any]:
        began = datetime.now()
        text = clean_text(text)
        prediction = self.predictor(text=text)
        return {
            "source": source,
            "text": text,
            "elapsed": str(datetime.now() - began),
            **prediction,
        }

    # def dict2example(self, dct: dict[str, Any]) -> dspy.Example:
    #     example: dspy.Example = dspy.Example(**dct).with_inputs(*self.input_names)
    #     return example
