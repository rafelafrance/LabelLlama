#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageOps

from data_formats import data_util, image_with_labels, simple_label
from model_utils import extract_dwc, ocr_utils


def one_up(label: simple_label.SimpleLabel) -> None:
    _fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(8, 8))

    ax.imshow(label.image, cmap=plt.cm.gray)
    ax.axis("off")

    plt.show()


print(f"cwd = {Path.cwd()}")

# image_dir = Path("./data/geode/Label Test RMNH/")
#
# image_paths = list(image_dir.glob("*.jpg"))
# image_paths += list(image_dir.glob("*.JPG"))
# image_paths = sorted(image_paths)
# print(f"image count = {len(image_paths)}")
#
# labels = []
# for p in image_paths:
#     image = Image.open(p).convert("L")
#     image = ImageOps.exif_transpose(image, in_place=False)
#     labels.append(simple_label.SimpleLabel(image=image, path=p))

# one_up(labels[0])


def ocr_all_labels(labels: list[simple_label.SimpleLabel]) -> None:
    model, processor = ocr_utils.setup_ocr()
    for i, lb in enumerate(labels):
        text = ocr_utils.ocr_label(lb.image, model, processor, image_with_labels.PROMPT)
        lb.text = text
        print("\n", i, "=" * 80)
        # one_up(lb)
        for ln in text:
            print(ln)

    # model_utils.release_gpu_memory_hf(model)


# ocr_all_labels(labels)


label_json_path = Path("./data/diode/trial_run_ocr_text_2.json")
# label_json = [lb.as_dict() for lb in labels]
# with label_json_path.open("w") as f:
#     json.dump(label_json, f, indent=4)

anno_json = Path("./data/diode/trial_run_annotations_2.json")

# args = argparse.Namespace(
#     label_type="bug",
#     label_json=label_json_path,
#     annotations_json=anno_json,
#     # Defaults
#     model="ollama_chat/gemma3:27b",
#     api_base="http://localhost:11434",
#     api_key=None,
#     temperature=1.0,
#     max_tokens=1024,
#     limit=0,
# )

# extract_dwc.extract_info(args)

with anno_json.open() as ff:
    extracts = json.load(ff)

formatted = data_util.lift_annotations(extracts)

df = pd.DataFrame(formatted)

formatted_csv = Path("./data/diode/trial_run_annotations_2.csv")

df.to_csv(formatted_csv, index=False)
