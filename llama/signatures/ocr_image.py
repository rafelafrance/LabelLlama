import dspy


class OcrImage(dspy.Signature):
    """
    You are given an image of a museum specimen with labels.
    I want you to extract all the text from every label on the specimen.
    This includes text from both typewritten and handwritten labels.
    Do not get confused by the specimen itself which is in the center of the image.
    I want plain text without HTML or Markdown tags.
    """

    image: dspy.Image = dspy.InputField(default="", desc="Image of a museum specimen")
    text: str = dspy.OutputField(default=[], desc="Label text")

