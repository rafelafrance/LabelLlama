import re
from typing import Any

import dspy
from dspy import InputField, OutputField, Signature

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


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
        self.verbatim = verbatim
        self.predictor = dspy.Predict(UtmSig)

    def preprocess(self, field_value: str, _doc_text: str) -> str:
        return re.sub(r"(?<!\s)-", " ", field_value)

    def postprocess(self, subfields: dict[str, Any], _doc_text: str) -> dict[str, Any]:
        utm = subfields["utm"]
        northing = subfields["northing"]
        easting = subfields["easting"]

        # Remove section label
        zone = subfields["zone"]
        if zone:
            zone = subfields["zone"].split()
            zone = [z for z in zone if not z.lower().startswith("zone")]
            zone = [z for z in zone if z.lower() not in ("z", "z.")]
            zone = " ".join(zone)

        data = {"utm": utm, "zone": zone, "northing": northing, "easting": easting}
        postprocess.clean_empties(data)
        return data
