import dspy
from dspy import InputField, OutputField, Signature

from llama.postprocess.field_action import FieldAction, FieldData


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


class Elevation(FieldAction):
    def __init__(self, verbatim: str) -> None:
        super().__init__(verbatim)
        self.predictor = dspy.Predict(ElevationSig)

    def predict(self, field_data: FieldData) -> None:
        predicted = {}
        if not all(field_data.old.get(k) for k in ElevationSig.output_fields):
            predicted = self.predictor.predict(field_value=field_data.old[self.name])

        field_data.new[self.verbatim] = field_data.new[self.verbatim]

        for key in ElevationSig.output_fields:
            field_data.old[key] = field_data.old.get(key) or predicted.get(key)

    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.verbatim]

        if field:
            field = field.split()
            field = [w for w in field if not w.lower().startswith("el")]
            field = [w for w in field if not w.lower().startswith("alt")]
            field = [w for w in field if not w.lower().startswith("blev")]
            field = " ".join(field)

        field_data.new[self.verbatim] = field


        # values = subfields["elevationValues"]
        # units = subfields["elevationUnits"]
        #
        # if not units:
        #     return {}
        #
        # if len(values) > len(units):
        #     units = [u for u in units for _ in range(2)]
        #
        # pairs = list(zip(values, units, strict=False))
        #
        # # Remove feet values & units if there are any values in meters
        # if any(u[0].lower() == "m" for u in units):
        #     pairs = [
        #         (v, u)
        #         for v, u in zip(values, units, strict=False)
        #         if u[0].lower() == "m"
        #     ]
        #
        # return {
        #     "verbatimElevation": subfields[self.field_name],
        #     "elevation": pairs[0][0],
        #     "maxElevation": pairs[1][0] if len(pairs) > 1 else "",
        #     "elevationUnits": pairs[0][1],
        #     "elevationEstimated": subfields["elevationEstimated"],
        # }
