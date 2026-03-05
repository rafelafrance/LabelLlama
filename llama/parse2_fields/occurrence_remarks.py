from typing import Any

from dspy import InputField, OutputField, Signature

from llama.parse2_fields import postprocess
from llama.parse2_fields.field_action import FieldAction


class OccurrenceRemarksSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    text: str = InputField()

    occurrenceRemarksSig: list[float] = OutputField(
        default=[],
        desc=(
            "Need to separate occurrence remarks."
        ),
    )


class OccurrenceRemarks(FieldAction):
    def __init__(self, verbatim: str) -> None:
        super().__init__(verbatim)
        self.verbatim = verbatim
        # self.predictor = dspy.Predict(OccurrenceRemarksSig)

    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        postprocess.clean_empties(subfields)
        return subfields
