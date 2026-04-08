from typing import Any

from llama.common import str_util

HERBARIUM_V1 = """ You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label and stamp on the specimen.
    This includes text from both typewritten and handwritten labels.
    It also includes text from stamps and smaller labels.
    ✅ I want ALL of the text.
    ✅ I only want UTF-8 text without markup.
    ❌ DO NOT get confused by the specimen itself which is in the center of the image.
    ❌ Do not hallucinate!
    """

ORIGINAL = """
    You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label on the specimen.
    This includes text from both typewritten and handwritten labels.
    Do not get confused by the specimen itself which is in the center of the image.
    I want plain text without HTML or markdown tags.
    Do not hallucinate.
    """


DEFAULT_MODEL: dict[str, Any] = {
    "prompt": HERBARIUM_V1,
    "cleaner": str_util.clean_response,
}
ALL_OCR_MODELS: dict[str, dict] = {
    "chandra-ocr-2": {"prompt": HERBARIUM_V1, "cleaner": str_util.strip_html},
    "default": DEFAULT_MODEL,
}


def get_parameters(model: str) -> dict[str, Any]:
    model = model.rsplit("/", maxsplit=1)[-1]
    return ALL_OCR_MODELS.get(model, DEFAULT_MODEL)
