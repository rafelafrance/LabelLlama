import marimo

__generated_with = "0.16.5"
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
    from dataclasses import dataclass, field
    from pathlib import Path
    from pprint import pp

    import Levenshtein
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import torch
    from numpy.typing import NDArray
    from skimage import io

    from llama.data_formats import image_slice, image_with_labels
    from llama.line_align import char_sub_matrix, label_builder
    from llama.line_align.align import LineAlign
    from llama.model_utils import extract_dwc, ocr_utils, model_utils
    return (
        Levenshtein,
        LineAlign,
        NDArray,
        Path,
        argparse,
        char_sub_matrix,
        dataclass,
        extract_dwc,
        image_slice,
        image_with_labels,
        io,
        json,
        label_builder,
        mo,
        model_utils,
        ocr_utils,
        os,
        pd,
        plt,
        torch,
    )


@app.cell
def _(os):
    # Do this so we can get the paths right for saving and reading data
    print(f"cwd = {os.getcwd()}")
    return


@app.cell
def _(torch):
    torch.cuda.is_available()
    return


@app.cell
def _(mo):
    mo.md(r"""## Image display functions""")
    return


@app.cell
def _(NDArray, plt):
    def one_up(output_image: NDArray) -> None:
        """Display an image."""
        _, ax = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(10, 10))

        ax.imshow(output_image, cmap=plt.cm.gray)
        ax.axis("off")

        plt.show()
    return (one_up,)


@app.cell
def _(mo):
    mo.md(r"""## Read in a set of scanned labels for testing""")
    return


@app.cell
def _(image_slice, one_up):
    def slice_labels_out_of_image(data):
        one_up(data)

        columns = image_slice.get_image_columns(data)
        print(f"column count = {len(columns)}")

        labels = []
        for c in columns:
            labels += image_slice.get_labels(data, c)

        print(f"label count = {len(labels)}")

        return labels
    return (slice_labels_out_of_image,)


@app.cell
def _(mo):
    mo.md(r"""## OCR the label images""")
    return


@app.cell
def _(image_with_labels, label_builder, model_utils, ocr_utils, one_up):
    def ocr_all_labels(labels):
        model, processor = ocr_utils.setup_ocr()
        for i, lb in enumerate(labels):
            text = ocr_utils.ocr_label(lb.image, model, processor, image_with_labels.PROMPT)
            text = [label_builder.post_process_text(t) for t in text]
            lb.text = text
            print("\n", i, "=" * 80)
            if i % 10 == 0:
                one_up(lb.image)
            for ln in text:
                print(ln)

        model_utils.release_gpu_memory_hf(model)
    return (ocr_all_labels,)


@app.cell
def _(mo):
    mo.md(r"""## Group the images into sets that hold different views of the same label""")
    return


@app.cell
def _(dataclass, image_slice):
    @dataclass
    class SimilarLabels:
        labels: list[image_slice.ImageArea]
        indexes: list[int]
    return (SimilarLabels,)


@app.cell
def _(Levenshtein, SimilarLabels):
    def split_with_levenshtein(labels, threshold=0.85) -> list[SimilarLabels]:
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

        label_sets = [
            SimilarLabels(labels=labels[i[0] : i[1]], indexes=list(range(i[0], i[1])))
            for i in idx
        ]
        return label_sets
    return (split_with_levenshtein,)


@app.cell
def _(mo):
    mo.md(r"""## Perform a multiple sequence alignment on the OCRed text""")
    return


@app.cell
def _(LineAlign, char_sub_matrix, image_slice):
    def align_texts(label_set: image_slice.ImageArea):
        matrix = char_sub_matrix.get()
        aligner = LineAlign(substitutions=matrix)
        texts = [" ".join(lb.text) for lb in label_set]
        aligned = aligner.align(texts)
        return aligned
    return (align_texts,)


@app.cell
def _(Path, SimilarLabels, align_texts, label_builder, result):
    def find_consensus_text(label_sets: SimilarLabels, image_path: Path):
        label_json = []

        for j, label_set in enumerate(label_sets):
            aligned = align_texts(label_set.labels)
            filtered = label_builder.filter_lines(aligned, threshold=32)
            cons = label_builder.find_consensus(filtered)
            print()
            print(j, "=" * 80)
            for line in result:
                line = " ".join(line.split())
                print(line)
            print("-" * 40)
            print(cons)
            label_json.append(
                {
                    "path": str(image_path),
                    "text": cons,
                    "indexes": label_set.indexes,
                    "aligned": aligned,
                }
            )
        return label_json
    return (find_consensus_text,)


@app.cell
def _(mo):
    mo.md(r"""## Run a batch of images""")
    return


@app.cell
def _(Path):
    # Choose a set of images for testing
    image_dir = Path("../data/lightning_bug/Transcribed_Labels/00000XXXX/0000000XX")
    output_dir = Path("../data/lightning_bug/trial_run_2")

    image_paths = sorted(image_dir.glob("*.jpg"))
    print(f"image count = {len(image_paths)}")
    return image_paths, output_dir


@app.cell
def _(
    argparse,
    extract_dwc,
    find_consensus_text,
    image_paths,
    io,
    json,
    ocr_all_labels,
    output_dir,
    slice_labels_out_of_image,
    split_with_levenshtein,
):
    for target_image in image_paths:
        print()
        print("#" * 80)
        print(target_image.stem)
        print()

        data = io.imread(target_image, as_gray=True)
        consensus_path = output_dir / f"{target_image.stem}_consensus.json"
        annotations_path = output_dir / f"{target_image.stem}_annotations.json"

        labels = slice_labels_out_of_image(data)

        ocr_all_labels(labels)

        label_sets = split_with_levenshtein(labels)

        consensus_text = find_consensus_text(label_sets, target_image)

        with consensus_path.open("w") as fout:
            json.dump(consensus_text, fout, indent=4)

        args = argparse.Namespace(
            label_type="bug",
            label_json=consensus_path,
            annotations_json=annotations_path,
            # Defaults
            model="ollama_chat/gemma3:27b",
            api_base="http://localhost:11434",
            api_key=None,
            limit=0,
            temperature=None,
            max_tokens=None,
        )

        extract_dwc.extract_info(args)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r""" """)
    return


@app.cell
def _(mo):
    mo.md(r"""## Format the results""")
    return


@app.cell
def _(json, output_dir, pd):
    annotation_paths = sorted(output_dir.glob("*annotations*"))
    consensus_paths = sorted(output_dir.glob("*consensus*"))
    csv_path = output_dir / "annotations.csv"

    annotations, consensus = [], []
    for anno_path, cons_path in zip(annotation_paths, consensus_paths, strict=True):
        with anno_path.open() as fin:
            annotations += json.load(fin)

        with cons_path.open() as fin:
            consensus += json.load(fin)

        for anno, cons in zip(annotations, consensus, strict=True):
            if anno["path"] != cons["path"]:
                print("ERROR!")
            anno["indexes"] = cons["indexes"]
            anno["aligned"] = cons["aligned"]

    df = pd.DataFrame(annotations)
    df.to_csv(csv_path, index=False)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
