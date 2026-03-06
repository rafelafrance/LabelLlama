from typing import Any

import dspy
from dspy import InputField, OutputField, Signature

from llama.parse2_fields.field_action import FieldAction


class ElevationSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    text: str = InputField()

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
        self.verbatim = verbatim
        self.predictor = dspy.Predict(ElevationSig)

    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        """Remove feet measurements if both meters and feet are given."""
        values = subfields["elevationValues"]
        units = subfields["elevationUnits"]

        if not units:
            return {}

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

        return {
            "verbatimElevation": text,
            "elevation": pairs[0][0],
            "maxElevation": pairs[1][0] if len(pairs) > 1 else "",
            "elevationUnits": pairs[0][1],
            "elevationEstimated": subfields["elevationEstimated"],
        }
