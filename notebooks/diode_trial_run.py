import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Extract Darwin Core information from images sent by the DiODE team""")
    return


@app.cell
def _():
    import argparse
    import json
    import os
    from pathlib import Path
    from pprint import pp

    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    from numpy import typing as npt
    from PIL import Image, ImageOps

    from llama.data_formats import (
        bug_label, data_util, label_types, simple_label, image_with_labels
    )
    from llama.model_utils import extract_dwc, model_utils, ocr_utils
    from llama.pylib import darwin_core
    return (
        Image,
        ImageOps,
        Path,
        argparse,
        data_util,
        extract_dwc,
        image_with_labels,
        json,
        mo,
        model_utils,
        ocr_utils,
        os,
        pd,
        plt,
        simple_label,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Image display functions""")
    return


@app.cell
def _(plt, simple_label):
    def one_up(label: simple_label.SimpleLabel) -> None:
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(8, 8))

        ax.imshow(label.image, cmap=plt.cm.gray)
        ax.axis("off")

        plt.show()
    return (one_up,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Read images""")
    return


@app.cell
def _(Image, ImageOps, Path, one_up, os, simple_label):
    print(f"cwd = {os.getcwd()}")

    image_dir = Path("../data/geode/Label Test RMNH/")

    image_paths = list(image_dir.glob("*.jpg"))
    image_paths += list(image_dir.glob("*.JPG"))
    image_paths = sorted(image_paths)
    print(f"image count = {len(image_paths)}")

    labels = []
    for p in image_paths:
        image = Image.open(p).convert("L")
        image = ImageOps.exif_transpose(image, in_place=False)
        labels.append(simple_label.SimpleLabel(image=image, path=p))

    one_up(labels[0])
    return (labels,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## OCR images""")
    return


@app.cell
def _(image_with_labels, labels, model_utils, ocr_utils, one_up):
    def ocr_all_labels(labels):
        model, processor = ocr_utils.setup_ocr()
        for i, lb in enumerate(labels):
            text = ocr_utils.ocr_label(lb.image, model, processor, image_with_labels.PROMPT)
            lb.text = text
            print("\n", i, "=" * 80)
            one_up(lb)
            for ln in text:
                print(ln)

        model_utils.release_gpu_memory_hf(model)


    ocr_all_labels(labels)
    return


@app.cell
def _(Path, json, labels):
    label_json_path = Path("../data/diode/trial_run_ocr_text_2.json")
    label_json = [lb.as_dict() for lb in labels]
    with label_json_path.open("w") as f:
        json.dump(label_json, f, indent=4)
    return (label_json_path,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Extract information from the OCRed text""")
    return


@app.cell
def _(Path):
    anno_json = Path("../data/diode/trial_run_annotations_2.json")
    return (anno_json,)


@app.cell
def _(anno_json, argparse, extract_dwc, label_json_path):
    args = argparse.Namespace(
        label_type="bug",
        label_json=label_json_path,
        annotations_json=anno_json,
        # Defaults
        model="ollama_chat/gemma3:27b",
        api_base="http://localhost:11434",
        api_key=None,
        limit=0,
    )

    extract_dwc.extract_info(args)
    return


@app.cell
def _(mo):
    mo.md(r"""## Post-process extracted data""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r""" """)
    return


@app.cell
def _(Path, anno_json, data_util, json, pd):
    with anno_json.open() as ff:
        extracts = json.load(ff)

    formatted = data_util.lift_annotations(extracts)

    df = pd.DataFrame(formatted)

    formatted_csv = Path("../data/diode/trial_run_annotations_2.csv")

    df.to_csv(formatted_csv, index=False)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
