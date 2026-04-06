HERBARIUM_V1 = """
    You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label on the specimen.
    This includes text from both typewritten and handwritten labels.
    ✅ I only want UTF-8 text without markup.
    ❌ DO NOT get confused by the specimen itself which is in the center of the image.
    ❌ Do not hallucinate!
    """


ALL_OCR = {
    "herbarium": HERBARIUM_V1,
}
