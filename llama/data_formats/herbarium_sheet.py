import dspy

PROMPT = """
    Below is the image of a herbarium sheet that contains an image of a
    plant and some informational labels, stamps, and barcodes.
    Find all labels, barcodes, and stamps and return all of text on them.
    Ignore the image of the plant.
    Do not hallucinate.
    """


class HerbariumSheet(dspy.Signature):
    """Extract label text from an image of a herbarium sheet."""

    # Input fields
    image: dspy.Image = dspy.InputField(default="", desc="Image of a herbarium sheet")
    prompt: str = dspy.InputField(default="", desc="Extract text")

    # Output traits -- Just capturing the text for now
    text: list[str] = dspy.OutputField(default=[], desc="Label text")


INPUT_FIELDS = ("image", "prompt")
OUTPUT_FIELDS = [t for t in vars(HerbariumSheet()) if t not in INPUT_FIELDS]
