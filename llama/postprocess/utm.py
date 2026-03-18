import re

import dspy
from dspy import InputField, OutputField, Signature

from llama.postprocess.base_action import BaseAction, FieldData


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


class Utm(BaseAction):
    def __init__(self, input_name: str) -> None:
        super().__init__(input_name)
        self.predictor = dspy.Predict(UtmSig)

    def all_output_names(self) -> list[str]:
        return [self.input_name, "utmNorthing", "utmEasting", "utmZone"]

    def preprocess_field(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.input_name]
        field = re.sub(r"(?<!\s)-", " ", field)
        field_data.output_field[self.input_name] = field

    def predict(self, field_data: FieldData) -> None:
        predicted = {}
        if not all(field_data.input_field.get(k) for k in UtmSig.output_fields):
            predicted = self.predictor.predict(
                field_value=field_data.input_field[self.output_name]
            )

        field_data.output_field[self.input_name] = (
            field_data.output_field[self.input_name]
        )

        for key in UtmSig.output_fields:
            field_data.input_field[key] = (
                field_data.input_field.get(key) or predicted.get(key)
            )

    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.input_name]
        field_data.output_field[self.input_name] = field

        self.create_subfields(field_data)

    @staticmethod
    def create_subfields(field_data: FieldData) -> None:
        northing = field_data.input_field["utmNorthing"].lower()
        northing = northing.replace("n", "")

        easting = field_data.input_field["utmEasting"].lower()
        easting = easting.replace("e", "")

        zone = field_data.input_field["utmZone"]
        if zone:
            zone = zone.split()
            zone = [z for z in zone if not z.lower().startswith("zone")]
            zone = [z for z in zone if z.lower() not in ("z", "z.")]
            zone = " ".join(zone)

        field_data.output_field["utmNorthing"] = northing
        field_data.output_field["utmEasting"] = easting
        field_data.output_field["utmZone"] = zone

