import dspy
from dspy import InputField, OutputField, Signature

from llama.common import fix_values
from llama.postprocess.base_action import BaseAction, FieldData


class ElevationSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    field_value = InputField()

    elevationValues: list[float] = OutputField(
        default=[],
        desc=(
            "The elevation values. More than one value could be an elevation range "
            "or it could be the same elevation reported in different units."
        ),
    )
    elevationUnits: list[str] = OutputField(
        default=[],
        desc=(
            "The elevation units. There may be more than one units reported when the "
            "same value is reported in different units."
        ),
    )
    elevationEstimated: bool = OutputField(
        default=False,
        desc="Is this an estimated elevation?",
    )


class Elevation(BaseAction):
    def __init__(self, input_name: str) -> None:
        super().__init__(input_name)
        self.predictor = dspy.Predict(ElevationSig)

    def all_output_names(self) -> list[str]:
        return [
            self.input_name,
            "elevation",
            "maxElevation",
            "elevationUnits",
            "elevationEstimated",
        ]

    def preprocess_field(self, field_data: FieldData) -> None:
        field_value = field_data.input_field[self.input_name]
        field_data.output_field[self.output_name] = fix_values.to_str(field_value)

        field_data.input_field["elevationValues"] = fix_values.to_list_of_floats(
            field_data.input_field["elevationValues"]
        )
        field_data.input_field["elevationUnits"] = fix_values.to_list_of_strs(
            field_data.input_field["elevationUnits"]
        )
        field_data.input_field["elevationEstimated"] = fix_values.to_bool(
            field_data.input_field["elevationEstimated"]
        )

    def predict(self, field_data: FieldData) -> None:
        predicted = {}
        if not all(field_data.input_field.get(k) for k in ElevationSig.output_fields):
            predicted = self.predictor(
                field_value=field_data.output_field[self.output_name],
            )

        for key in ElevationSig.output_fields:
            field_data.input_field[key] = field_data.input_field.get(
                key,
            ) or predicted.get(key)

    def postprocess(self, field_data: FieldData) -> None:
        print(field_data.input_field["elevationValues"])
        print(field_data.input_field["elevationUnits"])
        print(field_data.input_field["elevationEstimated"])
        field = field_data.output_field[self.output_name]

        if field:
            field = field.split()
            field = [w for w in field if not w.lower().startswith("el")]
            field = [w for w in field if not w.lower().startswith("alt")]
            field = [w for w in field if not w.lower().startswith("blev")]
            field = " ".join(field)

        self.create_subfields(field_data)

        field_data.output_field[self.input_name] = field

    @staticmethod
    def create_subfields(field_data: FieldData) -> None:
        values = field_data.input_field["elevationValues"]
        units = field_data.input_field["elevationUnits"]

        if len(values) > len(units):
            units = [u for u in units for _ in range(2)]

        pairs = list(zip(values, units, strict=False))

        # Remove feet values & units if there are any values in meters
        if any(u[0].lower() == "m" for u in units):
            pairs = [
                (v, u)
                for v, u in zip(values, units, strict=False)
                if u[0].lower() == "m"
            ]

        field_data.output_field["elevation"] = pairs[0][0]
        field_data.output_field["maxElevation"] = pairs[1][0] if len(pairs) > 1 else ""
        field_data.output_field["elevationUnits"] = pairs[0][1]
        field_data.output_field["elevationEstimated"] = field_data.input_field[
            "elevationEstimated"
        ]
