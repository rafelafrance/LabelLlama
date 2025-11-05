import dspy

PROMPT = """
    Below is the image if a museum specimen and some informational
    labels, stamps, and barcodes.
    Find ALL labels, barcodes, and stamps and return ALL of text on them.
    There are often several labels and barcodes.
    Ignore the museum specimen itself.
    Just return the plain text representation on this image as if you were reading it
    naturally.
    If there are any female or male symbols convert them into text.
    Read any natural handwriting as well as typwritten labels.
    Do not hallucinate.
    """


class ImageWithLabels(dspy.Signature):
    """Extract label text from an image of a herbarium sheet."""

    # Input fields
    image: dspy.Image = dspy.InputField(default="", desc="Image of a herbarium sheet")
    prompt: str = dspy.InputField(default="", desc="Extract text")

    # Output fields -- Just capturing the text for now
    text: list[str] = dspy.OutputField(default=[], desc="Label text")


INPUT_FIELDS = ("image", "prompt")
OUTPUT_FIELDS = [t for t in vars(ImageWithLabels()) if t not in INPUT_FIELDS]
