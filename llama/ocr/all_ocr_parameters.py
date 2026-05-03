from textwrap import dedent
from typing import Any

HERBARIUM_V1 = dedent("""
    You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label and stamp on the specimen.
    This includes text from both typewritten and handwritten labels.
    It also includes text from stamps and smaller labels.
      ✅ I want ALL of the text.
      ✅ I only want UTF-8 text without markup.
      ❌ DO NOT include HTML tags.
      ❌ DO NOT include markdown tags.
      ❌ DO NOT get confused by the specimen itself which is in the center of the image.
      ❌ Do not hallucinate!
    """)

ORIGINAL = dedent("""
    You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label on the specimen.
    This includes text from both typewritten and handwritten labels.
    Do not get confused by the specimen itself which is in the center of the image.
    I want plain text without HTML or markdown tags.
    Do not hallucinate.
    """)


DEFAULT_MODEL: dict[str, Any] = {
    "prompt": HERBARIUM_V1,
}
ALL_OCR_MODELS: dict[str, dict] = {
    "chandra-ocr-2": {"prompt": HERBARIUM_V1},
    "default": DEFAULT_MODEL,
}


def get_parameters(model: str) -> dict[str, Any]:
    model = model.rsplit("/", maxsplit=1)[-1]
    return ALL_OCR_MODELS.get(model, DEFAULT_MODEL)
