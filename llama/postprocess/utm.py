import re

import dspy
from dspy import InputField, OutputField, Signature

from old.llama.pylib import postprocess
from llama.postprocess.field_action import FieldAction, FieldData


class UtmSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    doc_text = InputField()

    northing: str = OutputField(
        default="",
        desc=(
            "The northing portion of the UTM. "
            'It is a number (possibly negative, or a decimal) followed by an "N". '
            'It will look like: "3845372N", '
            '"4057.6 N", "3968400 N", "N 4253279", "4N"'
        ),
    )
    easting: str = OutputField(
        default="",
        desc=(
            "The easting portion of the UTM. "
            'It is a number (possibly negative, or a decimal) followed by an "E". '
            'Examples look like "E 642700", '
            '"509257E", "- 0484145E", "546936", "368.2 E", "6E"'
        ),
    )
    zone: str = OutputField(
        default="",
        desc=(
            'The zone portion of the UTM. It will look like: "10S", "11", "8N", '
            '"Zone 11S;", "NH", "16P", "LJ".'
        ),
    )


class Utm(FieldAction):
    def __init__(self, verbatim: str) -> None:
        super().__init__(verbatim)
        self.predictor = dspy.Predict(UtmSig)

    def preprocess_field(self, field_data: FieldData) -> None:
        field = field_data.new[self.verbatim]
        field = re.sub(r"(?<!\s)-", " ", field)
        field_data.new[self.verbatim] = field

    def predict(self, field_data: FieldData) -> None:
        predicted = {}
        if not all(field_data.old.get(k) for k in UtmSig.output_fields):
            predicted = self.predictor.predict(field_value=field_data.old[self.name])

        field_data.new[self.verbatim] = field_data.new[self.verbatim]

        for key in UtmSig.output_fields:
            field_data.old[key] = field_data.old.get(key) or predicted.get(key)

    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.verbatim]

        if field:
            field = field.split()
            field = [z for z in field if not z.lower().startswith("zone")]
            field = [z for z in field if z.lower() not in ("z", "z.")]
            field = " ".join(field)

        field_data.new[self.verbatim] = field
