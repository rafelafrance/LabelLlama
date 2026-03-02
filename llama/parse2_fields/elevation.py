from dspy import InputField, OutputField, Signature


class Elevation(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    text: str = InputField()

    values: list[float] = OutputField(
        default=[],
        desc="The elevation values. More than one value could be an elevation range "
             "or it could be the same elevation reported in different units.",
    )
    units: list[str] = OutputField(
        default=[],
        desc="The elevation units. There may be more than one units reported when the "
             "same value is reported in different units.",
    )
    estimated: bool = OutputField(
        default=False,
        desc="Is this an estimated elevation?",
    )
