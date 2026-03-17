from dspy import InputField, OutputField, Signature

from old.llama.pylib import postprocess
from llama.postprocess.field_action import FieldAction, FieldData


class OccurrenceRemarksSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    doc_text = InputField()

    occurrenceRemarksSig: list[float] = OutputField(
        default=[],
        desc=(
            "Need to separate occurrence remarks."
        ),
    )


class OccurrenceRemarks(FieldAction):
    pass
