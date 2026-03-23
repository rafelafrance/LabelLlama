from dataclasses import dataclass, field
from typing import Any, ClassVar

import dspy
from dspy import InputField, OutputField, Signature

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class UtmSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    utm = InputField()

    utmNorthing: str = OutputField(
        default="",
        desc=(
            "The northing portion of the UTM. "
            'It is a number (possibly negative, or a decimal) followed by an "N". '
            'It will look like: "3845372N", '
            '"4057.6 N", "3968400 N", "N 4253279", "4N"'
        ),
    )
    utmEasting: str = OutputField(
        default="",
        desc=(
            "The easting portion of the UTM. "
            'It is a number (possibly negative, or a decimal) followed by an "E". '
            'Examples look like "E 642700", "E66", '
            '"509257E", "- 0484145E", "546936", "368.2 E", "6E"'
        ),
    )
    utmZone: str = OutputField(
        default="",
        desc=(
            'The zone portion of the UTM. It will look like: "10S", "11", "8N", '
            '"Zone 11S;", "NH", "16P", "LJ".'
        ),
    )


@dataclass
class Utm(BaseField):
    predictor: ClassVar[Any] = dspy.Predict(UtmSig)

    utm: str = field(default="", metadata=BOTH)
    utmNorthing: str = field(default="", metadata=BOTH)
    utmEasting: str = field(default="", metadata=BOTH)
    utmZone: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        # Setup the utm so it is valid input for further processing
        self.utm = fix_values.to_str(self.utm)

        # Only run the model if an input field is empty
        # Input for this class is actually an output from the LM moddel class
        if self.utm and any(not getattr(self, name) for name in UtmSig.output_fields):
            predicted = self.predictor(utm=self.utm)

            # Only fill fields without a previous value, i.e. default to previous LLM
            self.utmNorthing = self.utmNorthing or predicted.get("utmNorthing", "")
            self.utmEasting = self.utmEasting or predicted.get("utmEasting", "")
            self.utmZone = self.utmZone or predicted.get("utmZone", "")

        # Make sure a language model didn't do something silly
        self.utmNorthing = fix_values.to_str(self.utmNorthing)
        self.utmEasting = fix_values.to_str(self.utmEasting)
        self.utmZone = fix_values.to_str(self.utmZone)

        # Remove the E or N for the easting or northing field
        self.utmNorthing = self.utmNorthing.lower().replace("n", "")
        self.utmEasting = self.utmEasting.lower().replace("e", "")

        # Remove the zone label
        words = self.utmZone.split()
        words = [w for w in words if not w.lower().startswith("zone")]
        words = [w for w in words if w.lower() not in ("z", "z.")]
        self.utmZone = " ".join(words)
