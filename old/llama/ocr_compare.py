#!/usr/bin/env python3

import json
from pathlib import Path
from pprint import pp

import lmstudio as lms

SERVER_API_HOST = "localhost:1234"

start = 50
end = 100

jsonl = Path("data/herbarium/compare_ocr_models_2025-11-05.jsonl")

prompt = """
You are given images of museum specimens with labels.
I want you to extract all of the text from every label on the specimen.
This includes text from both typewritten and handwritten labels.
Do not get confused by the specimen itself which will be in the center of the page.
Do not hallucinate.
"""

model_names = [
    "mradermacher/olmocr-7b-0825",
    "google/gemma-3-27b",
    "noctrex/Chandra-OCR-GGUF",
]

image_dir = Path("data/herbarium/sheets_001/")
image_paths = sorted(image_dir.glob("*.jpg"))
if end and start:
    image_paths = image_paths[start:end]

with lms.Client(SERVER_API_HOST) as client, jsonl.open("a") as fout:
    for model_name in model_names:
        model = client.llm.model(model_name)
        for i, image_path in enumerate(image_paths):
            handle = client.files.prepare_image(image_path)
            chat = lms.Chat()
            chat.add_user_message(prompt, images=[handle])
            prediction = model.respond(chat)

            result = {
                "model_name": model_name,
                "image_path": str(image_path),
                "prediction": str(prediction),
            }
            print()
            print(i)
            pp(result)
            fout.write(json.dumps(result))
            fout.write("\n")
            fout.flush()
