import marimo

__generated_with = "0.16.2"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""# Test processing Lightning Bug images""")
    return


@app.cell
def _():
    import argparse
    import json
    import os
    import tempfile
    from pathlib import Path

    import Levenshtein
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy.typing as npt
    import torch
    from PIL import Image
    from skimage import io
    from transformers import AutoModelForImageTextToText, AutoProcessor

    from llama.data_formats import image_slice, image_with_labels
    from llama.line_align import char_sub_matrix, label_builder
    from llama.line_align.align import LineAlign
    from llama.model_utils import extract_dwc
    return (
        Levenshtein,
        LineAlign,
        Path,
        argparse,
        char_sub_matrix,
        extract_dwc,
        image_slice,
        image_with_labels,
        io,
        json,
        label_builder,
        mo,
        npt,
        os,
        plt,
    )


@app.cell
def _(mo):
    mo.md(r"""## Get test images""")
    return


@app.cell
def _(Path, io, os):
    print(f"cwd = {os.getcwd()}")

    image_dir = Path("../data/lightning_bug/Transcribed_Labels/00000XXXX/0000000XX")

    image_paths = sorted(image_dir.glob("*.jpg"))
    print(f"image count = {len(image_paths)}")

    target_image = 0
    data = io.imread(image_paths[target_image], as_gray=True)
    return data, image_paths


@app.cell
def _(mo):
    mo.md(r"""## Image display functions""")
    return


@app.cell
def _(npt, plt):
    def one_up(output_image: npt.NDArray) -> None:
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(10, 10))

        ax.imshow(output_image, cmap=plt.cm.gray)
        ax.axis("off")

        plt.show()


    def two_up(input_image: npt.NDArray, output_image: npt.NDArray, output_title="after"):
        fig, axes = plt.subplots(
            nrows=1, ncols=2, sharex=True, sharey=True, figsize=(16, 8)
        )
        ax = axes.ravel()

        ax[0].imshow(input_image, cmap=plt.cm.gray)
        ax[0].set_title("before")
        ax[0].axis("off")

        ax[1].imshow(output_image, cmap=plt.cm.gray)
        ax[1].set_title(output_title)
        ax[1].axis("off")

        plt.show()
        return output_image
    return (one_up,)


@app.cell
def _(mo):
    mo.md(r"""## Read in a set of scanned labels for testing""")
    return


@app.cell
def _(data, image_slice, one_up):
    def slice_labels_out_of_image(data):
        one_up(data)

        columns = image_slice.get_image_columns(data)
        print(f"column count = {len(columns)}")

        labels = []
        for c in columns:
            labels += image_slice.get_labels(data, c)

        print(f"label count = {len(labels)}")

        return labels


    labels = slice_labels_out_of_image(data)
    return (labels,)


@app.cell
def _(mo):
    mo.md(r"""## OCR the label images""")
    return


@app.cell
def _(image_with_labels, labels, lm_utils, ocr_utils, one_up):
    def ocr_all_labels(labels):
        model, processor = ocr_utils.setup_ocr()
        for i, lb in enumerate(labels):
            text = ocr_utils.ocr_label(lb.image, model, processor, image_with_labels.PROMPT)
            lb.text = text
            if i % 10 == 0:
                print("\n", i, "=" * 80)
                one_up(lb.image)
                for ln in text:
                    print(ln)

        lm_utils.release_gpu_memory_hf(model)


    ocr_all_labels(labels)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Group the images into sets that hold different views of the same label

    sets when visually examined:

    - labels[0:11]
    - labels[11:19]
    - labels[19:33]
    - labels[33:49]
    - labels[49:65]
    - labels[65:80]
    - labels[80:90]
    - labels[90:104]
    """
    )
    return


@app.cell
def _(Levenshtein, image_slice, labels):
    def split_with_levenshtein(labels, threshold=0.85) -> list[list[image_slice.ImageArea]]:
        beg = 0
        idx = []
        for end, (area1, area2) in enumerate(zip(labels[:-1], labels[1:])):
            text1 = "\n".join(area1.text)
            text2 = "\n".join(area2.text)
            dist = Levenshtein.distance(text1, text2)
            norm = dist / max(len(text1), len(text2))
            if norm > threshold:
                idx.append((beg, end + 1))
                beg = end + 1
        idx.append((beg, len(labels)))

        for i in idx:
            print(f"label set: {i}")

        label_sets = [labels[i[0] : i[1]] for i in idx]
        return label_sets


    label_sets = split_with_levenshtein(labels)
    return (label_sets,)


@app.cell
def _(mo):
    mo.md(r"""## Perform a multiple sequence alignment on the OCRed text""")
    return


@app.cell
def _(
    LineAlign,
    Path,
    char_sub_matrix,
    image_paths,
    json,
    label_builder,
    label_sets,
):
    def align(label_set):
        matrix = char_sub_matrix.get()
        aligner = LineAlign(substitutions=matrix)
        texts = [" ".join(lb.text) for lb in label_set]
        results = aligner.align(texts)
        return results


    def find_consensus_text(label_sets, label_json_path):
        label_json = []

        for j, label_set in enumerate(label_sets):
            result = align(label_set)
            result = label_builder.filter_lines(result, threshold=32)
            cons = label_builder.consensus(result)
            cons_text = label_builder.substitute(cons)
            print()
            print(j, "=" * 80)
            for line in result:
                line = " ".join(line.split())
                print(line)
            print("-" * 40)
            print(cons_text)
            label_json.append({
                "path": str(image_paths[0]),
                "text": cons_text,
            })
        return label_json


    label_json_path = Path("../data/lightning_bug/trial_run_consensus.json")
    label_json = find_consensus_text(label_sets, label_json_path)

    with label_json_path.open("w") as f:
        json.dump(label_json, f, indent=4)
    return (label_json_path,)


@app.cell
def _(mo):
    mo.md(r"""## Run a small language model (SLM) on consensus text to get information""")
    return


@app.cell
def _(Path, argparse, extract_dwc, label_json_path):
    args = argparse.Namespace(
        label_type="bug",
        label_json=Path(label_json_path),
        annotations_json=Path("../data/lightning_bug/trial_run_annotations.json"),
        # Defaults
        model="ollama_chat/gemma3:27b",
        api_base="http://localhost:11434",
        api_key=None,
        limit=0,
    )

    extract_dwc.extract_info(args)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
