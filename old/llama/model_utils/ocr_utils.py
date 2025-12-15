import tempfile
from typing import Any

import torch

from PIL import Image
from transformers import (
    AutoModelForImageTextToText,
    AutoProcessor,
    Qwen3VLMoeForConditionalGeneration,
)


def setup_ocr(model_id: str = "allenai/olmOCR-7B-0825") -> tuple[Any, Any]:
    processor = AutoProcessor.from_pretrained(model_id)
    model = (
        AutoModelForImageTextToText.from_pretrained(model_id, dtype=torch.float16)
        .to("cuda")
        .eval()
    )
    return model, processor


def setup_ocr_new(
    model_id: str = "Qwen/Qwen3-VL-30B-A3B-Instruct",
) -> tuple[Any, Any]:
    model = Qwen3VLMoeForConditionalGeneration.from_pretrained(
        model_id, dtype="auto", device_map="auto"
    )
    processor = AutoProcessor.from_pretrained(model_id)
    return model, processor


def ocr_sheet(
    sheet: Image,
    model: Any,
    processor: Any,
    prompt: str,
    max_new_tokens: int = 16384,
) -> None:
    with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
        sheet.save(f.name)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": f.name,
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    )
    generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :]
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids, strict=True)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )
    print(output_text)


def ocr_label(
    label: Image,
    model: Any,
    processor: Any,
    prompt: str,
    max_new_tokens: int = 16384,
) -> list[str]:
    with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
        label.save(f.name)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": f.name,
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to("cuda" if torch.cuda.is_available() else "cpu")

        output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(inputs.input_ids, output_ids, strict=False)
        ]
        output_text = processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
        return output_text
