import re

import dspy
from dspy import InputField, OutputField, Signature

from llama.common import fix_values
from llama.postprocess.base_action import BaseAction, FieldData


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


class Trs(BaseAction):
    def __init__(self, input_name: str) -> None:
        super().__init__(input_name)
        self.predictor = dspy.Predict(TrsSig)

    def all_output_names(self) -> list[str]:
        return [
            self.input_name, "trsTownship", "trsRange", "trsSection", "trsQuad"
        ]

    def preprocess_field(self, field_data: FieldData) -> None:
        field_value = field_data.input_field[self.input_name]
        field_data.output_field[self.output_name] = fix_values.to_str(field_value)

        field_data.input_field["trsTownship"] = fix_values.to_str(
            field_data.input_field["trsTownship"]
        )
        field_data.input_field["trsRange"] = fix_values.to_str(
            field_data.input_field["trsRange"]
        )
        field_data.input_field["trsSection"] = fix_values.to_str(
            field_data.input_field["trsSection"]
        )
        field_data.input_field["trsQuad"] = fix_values.to_str(
            field_data.input_field["trsQuad"]
        )

    def predict(self, field_data: FieldData) -> None:
        predicted = {}
        if not all(field_data.input_field.get(k) for k in TrsSig.output_fields):
            predicted = self.predictor.predict(
                field_value=field_data.input_field[self.output_name]
            )

        field_data.output_field[self.input_name] = field_data.output_field[
            self.input_name
        ]

        for key in TrsSig.output_fields:
            field_data.input_field[key] = (
                field_data.input_field.get(key) or predicted.get(key)
            )

    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.input_name]
        field_data.output_field[self.input_name] = field

        self.create_subfields(field_data)

    @staticmethod
    def create_subfields(field_data: FieldData) -> None:
        township = re.sub(
            r"^t\s*", "", field_data.input_field["township"], flags=re.IGNORECASE
        )
        range_ = re.sub(
            r"^r\s*", "", field_data.input_field["range"], flags=re.IGNORECASE
        )

        # Remove section label
        sect = field_data.input_field["section"]
        if sect:
            sect = sect.split()
            sect = [s for s in sect if not s.lower().startswith("sec")]
            sect = [s for s in sect if s.lower() not in ("s", "s.")]
            sect = " ".join(sect)

        # Remove quad label
        quad = field_data.input_field["quad"]
        if quad:
            quad = quad.split()
            quad = [q for q in quad if not q.lower().startswith("quad")]
            quad = [q for q in quad if q.lower() not in ("q", "q.")]
            quad = " ".join(quad)

        field_data.output_field["trsTownship"] = township
        field_data.output_field["trsRange"] = range_
        field_data.output_field["trsSection"] = sect
        field_data.output_field["trsQuad"] = quad
