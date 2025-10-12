# import base64
import tempfile

# from io import BytesIO
from typing import Any

import torch

# from olmocr.data.renderpdf import render_pdf_to_base64png
# from olmocr.prompts.anchor import get_anchor_text
from PIL import Image
from transformers import (
    AutoModelForImageTextToText,
    AutoProcessor,
    # Qwen2VLForConditionalGeneration,
)


def setup_ocr(
    model_id: str = "allenai/olmOCR-7B-0825", max_new_tokens: int | None = None
) -> tuple[Any, Any]:
    processor = AutoProcessor.from_pretrained(model_id, max_new_tokens=max_new_tokens)
    model = (
        AutoModelForImageTextToText.from_pretrained(model_id, torch_dtype=torch.float16)
        .to("cuda")
        .eval(),
    )
    return model, processor


# def setup_ocr_new(
#     model_id: str = "mradermacher/olmOCR-7B-0825-GGUF",
# ) -> tuple[Any, Any]:
#     model = Qwen2VLForConditionalGeneration.from_pretrained(
#         model_id, torch_dtype=torch.bfloat16
#     ).eval()
#     processor = ""
#     return model, processor


def ocr_label(label: Image, model: Any, processor: Any, prompt: str) -> list[str]:
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
        ).to(model.device)

        output_ids = model.generate(**inputs, max_new_tokens=10_000)
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
