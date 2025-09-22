#!/usr/bin/env python3


import torch
from transformers import AutoModelForImageTextToText, AutoProcessor

# from llama.data_formats import lightning_bug_label

PROMPT = """
Below is the image of museum labels of insects.
Just return the plain text representation of this document as if you were reading it
naturally.
Read any natural handwriting.
Do not hallucinate.
"""

model_id = "allenai/olmOCR-7B-0825"
processor = AutoProcessor.from_pretrained(model_id)
model = (
    AutoModelForImageTextToText.from_pretrained(model_id, torch_dtype=torch.float16)
    .to("cuda")
    .eval()
)

sheet_dir = (
    "/home/rafe/work/language_models/LabelLlama/data/lightning_bug/"
    "Transcribed_Labels/00000XXXX/0000000XX/"
)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": sheet_dir + "0000000XX_Page_00.jpg",
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
