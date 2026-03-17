import re

import dspy
from dspy import InputField, OutputField, Signature

from old.llama.pylib import postprocess
from llama.postprocess.field_action import FieldAction, FieldData


class TrsSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    doc_text = InputField()

    township: str = OutputField(
        default="",
        desc=(
            'The township portion of the TRS. It will look like: "T28N" or "T 32 N". '
            'The letter "T" followed by a few digits and then an "N" or "S" compass '
            "direction."
        ),
    )
    range: str = OutputField(
        default="",
        desc=(
            'The range portion of the TRS. It will look like: "R23E" or "R 1 W". '
            'The letter "R" followed by a few digits and then an "E" or "W" compass '
            "direction."
        ),
    )
    section: str = OutputField(
        default="",
        desc=(
            'The section portion of the TRS. Examples look like "1/4 S10", '
            '"se1/4 ne1/4  sec 12", "SE ¼ Section 17", "NW¼ of sec. 8", "section 18" '
            '"S8 (SE¼)", "south-east corner section 7"'
        ),
    )
    quad: str = OutputField(
        default="",
        desc=(
            "The quad (quadrangle) portion of the TRS. It may be at the beginning or "
            'end of the TRS. Examples look like: "USGS Wahtoke 7 1/2 quad", '
            '"Yountville Quad", "Chicken Hawk Hill quadrangle", "Mt. Ingalls quad."'
        ),
    )


class Trs(FieldAction):
    def __init__(self, verbatim: str) -> None:
        super().__init__(verbatim)
        self.predictor = dspy.Predict(TrsSig)

    def predict(self, field_data: FieldData) -> None:
        predicted = {}
        if not all(field_data.old.get(k) for k in TrsSig.output_fields):
            predicted = self.predictor.predict(field_value=field_data.old[self.name])

        field_data.new[self.verbatim] = field_data.new[self.verbatim]

        for key in TrsSig.output_fields:
            field_data.old[key] = field_data.old.get(key) or predicted.get(key)

    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.verbatim]

        # Remove section label
        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("sec")]
            field = [s for s in field if s.lower() not in ("s", "s.")]
            field = " ".join(field)

        # Remove quad label
        if field:
            field = field.split()
            field = [q for q in field if not q.lower().startswith("quad")]
            field = [q for q in field if q.lower() not in ("q", "q.")]
            field = " ".join(field)

        field_data.new[self.verbatim] = field

        # township = re.sub(r"^t\s*", "", subfields["township"], flags=re.IGNORECASE)
        # range_ = re.sub(r"^r\s*", "", subfields["range"], flags=re.IGNORECASE)

        # trs = {
        #     "trs": doc_text,
        #     "township": township,
        #     "range": range_,
        #     "section": sect,
        #     "quad": quad,
        # }
        # postprocess.clean_empties(trs)
        # return trs
