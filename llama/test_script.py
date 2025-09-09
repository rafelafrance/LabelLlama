#!/usr/bin/env python3

import torch
from transformers import AutoModelForImageTextToText, AutoProcessor

model_id = "allenai/olmOCR-7B-0725"
processor = AutoProcessor.from_pretrained(model_id)
model = (
    AutoModelForImageTextToText.from_pretrained(model_id, torch_dtype=torch.float16)
    .to("cuda")
    .eval()
)


PROMPT = """
    Below is the image of one page of a herbarium sheet that contains an image of a
    plant and some informational labels, stamps, and barcodes.
    Find all labels, barcodes, and stamps and return all of text on them.
    Ignore the image of the plant.
    If there is no text at all that you think you should read, you can output null.
    Do not hallucinate.
    """

sheet_dir = "/home/rafe/work/language_models/LabelLlama/data/herbarium/sheets_001/"

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": sheet_dir + "800097.jpg",
            },
            {"type": "text", "text": PROMPT},
        ],
    }
]

text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device)

output_ids = model.generate(**inputs, max_new_tokens=10_000)
generated_ids = [
    output_ids[len(input_ids) :]
    for input_ids, output_ids in zip(inputs.input_ids, output_ids, strict=False)
]
output_text = processor.batch_decode(
    generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
)
for text in output_text:
    print("=" * 80)
    print(text)
