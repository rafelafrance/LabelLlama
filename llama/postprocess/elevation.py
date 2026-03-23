from dataclasses import dataclass, field
from typing import Any, ClassVar

import dspy
from dspy import InputField, OutputField, Signature

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, IN, OUT, BaseField


class ElevationSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    verbatimElevation = InputField()

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


@dataclass
class Elevation(BaseField):
    predictor: ClassVar[Any] = dspy.Predict(ElevationSig)

    verbatimElevation: str = field(default="", metadata=BOTH)
    elevationValues: list[float] | None = field(default=None, metadata=IN)
    elevation: float | None = field(default=None, metadata=OUT)
    maxElevation: float | None = field(default=None, metadata=OUT)
    elevationUnits: list[str] | str | None = field(default=None, metadata=BOTH)
    elevationEstimated: bool | None = field(default=None, metadata=BOTH)

    def __post_init__(self) -> None:
        # Setup the verbatimElevation so it is valid input for further processing
        self.verbatimElevation = fix_values.to_str(self.verbatimElevation)

        # Only run the model if an input field is empty
        # Input for this class is actually an output from the LM moddel class
        if self.verbatimElevation and not (
            self.elevationValues and self.elevationUnits
        ):
            predicted = self.predictor(verbatimElevation=self.verbatimElevation)

            # Only fill fields without a previous value, i.e. default to previous LLM
            self.elevationValues = self.elevationValues or predicted.get(
                "elevationValues", ""
            )
            self.elevationUnits = self.elevationUnits or predicted.get(
                "elevationUnits", ""
            )
            self.elevationEstimated = self.elevationEstimated or predicted.get(
                "elevationEstimated", ""
            )

        # Make sure the language model didn't do something silly
        self.elevationValues = fix_values.to_list_of_floats(self.elevationValues)
        self.elevationUnits = fix_values.to_list_of_strs(self.elevationUnits)
        self.elevationEstimated = fix_values.to_bool(self.elevationEstimated)

        # Remove the label from verbatimElevation
        words = self.verbatimElevation.split()
        words = [w for w in words if not w.lower().startswith("el")]
        words = [w for w in words if not w.lower().startswith("alt")]
        self.verbatimElevation = " ".join(words)

        # Make sure every value has units
        if len(self.elevationValues) > len(self.elevationUnits):
            self.elevationUnits = [u for u in self.elevationUnits for _ in range(2)]

        # Pair up values and units
        pairs = list(zip(self.elevationValues, self.elevationUnits, strict=False))

        # Remove any pairs that are not for meters, if there actually are meters
        if any(p[1].lower().startswith("m") for p in pairs):
            pairs = [(v, u) for v, u in pairs if u[0].lower().startswith("m")]

        # If there are no pairs then something went wrong, usually with a model
        if not pairs:
            return

        # Now set the output fields based on the pairs or values and units
        self.elevation = pairs[0][0]
        self.maxElevation = pairs[1][0] if len(pairs) > 1 else None
        self.elevationUnits = pairs[0][1]
