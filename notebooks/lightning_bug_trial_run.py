import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""# Test processing Lightning Bug images""")


@app.cell
def _():
    import os
    import tempfile
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import torch
    from PIL import Image
    from skimage import io
    from transformers import AutoModelForImageTextToText, AutoProcessor

    from llama.data_formats import image_with_labels
    from llama.line_align import char_sub_matrix, label_builder
    from llama.line_align.align import LineAlign
    from llama.pylib import image_slice

    return (
        AutoModelForImageTextToText,
        AutoProcessor,
        Image,
        LineAlign,
        Path,
        char_sub_matrix,
        image_slice,
        image_with_labels,
        io,
        label_builder,
        mo,
        os,
        plt,
        tempfile,
        torch,
    )


@app.cell
def _():
    MIN_LEN = 2


@app.cell
def _(mo):
    mo.md(r"""## Get test images""")


@app.cell
def _(os):
    os.getcwd()


@app.cell
def _(Path):
    image_dir = Path("../data/lightning_bug/Transcribed_Labels/00000XXXX/0000000XX")
    return (image_dir,)


@app.cell
def _(image_dir):
    image_paths = sorted(image_dir.glob("*.jpg"))
    len(image_paths)
    return (image_paths,)


@app.cell
def _(mo):
    mo.md(r"""## Image display functions""")


@app.cell
def _(Image, plt):
    def one_up(output_image: Image) -> None:
        fig, ax = plt.subplots(
            nrows=1, ncols=1, sharex=True, sharey=True, figsize=(16, 16)
        )

        ax.imshow(output_image, cmap=plt.cm.gray)
        # ax.set_title(output_title)
        ax.axis("off")

        plt.show()

    return (one_up,)


@app.cell
def _(plt):
    def two_up(input_image, output_image, output_title="after"):
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


@app.cell
def _(mo):
    mo.md(r"""## Read in a set of scanned labels for testing""")


@app.cell
def _(image_paths, io):
    image = io.imread(image_paths[0], as_gray=True)
    image.shape
    return (image,)


@app.cell
def _(image, one_up):
    one_up(image)


@app.cell
def _(mo):
    mo.md(r"""## Slice the test image into individual label images""")


@app.cell
def _(image, image_slice):
    strips = image_slice.get_image_columns(image)
    len(strips)
    return (strips,)


@app.cell
def _(strips):
    strip_image = strips[0]
    strip_image.as_image()


@app.cell
def _(image, image_slice, strips):
    areas = []
    for s in strips:
        areas += image_slice.get_image_areas(image, s)
    return (areas,)


@app.cell
def _(areas):
    area_image = areas[21]
    area_image.as_image()


@app.cell
def _(areas):
    len(areas)


@app.cell
def _(mo):
    mo.md(r"""## OCR the label images""")


@app.cell
def _(AutoModelForImageTextToText, AutoProcessor, torch):
    model_id = "allenai/olmOCR-7B-0825"
    processor = AutoProcessor.from_pretrained(model_id)
    model = (
        AutoModelForImageTextToText.from_pretrained(model_id, torch_dtype=torch.float16)
        .to("cuda")
        .eval()
    )
    return model, processor


@app.cell
def _(image_with_labels, model, processor, tempfile):
    def ocr_label(image) -> None:
        with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
            image.save(f.name)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": f.name,
                        },
                        {"type": "text", "text": image_with_labels.PROMPT},
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
                for input_ids, output_ids in zip(
                    inputs.input_ids, output_ids, strict=False
                )
            ]
            output_text = processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            return output_text

    return (ocr_label,)


@app.cell
def _(mo):
    mo.md(
        r"""## A failed experiment where I tried to preprocess the images before OCRing them"""
    )


@app.cell
def _():
    # for area in areas:
    #     before = area.image[area.north : area.south, area.west : area.east]
    #     after = lt.blur(before, sigma=2.0)
    #     after = lt.binarize_sauvola(after)
    #     after = lt.remove_small_holes(after)
    #     after = lt.binary_opening(after)
    #     two_up(before, after)
    #     after_image = Image.fromarray(after)
    #     before_text = ocr_label(area.as_image())
    #     after_text = ocr_label(after_image)
    #     print(before_text)
    #     print(after_text)
    #     # break
    return


@app.cell
def _(areas, ocr_label, one_up):
    for i, area in enumerate(areas):
        print("\n", i, "=" * 80)
        one_up(area.as_image())
        text = ocr_label(area.as_image())
        area.text = text
        for ln in text:
            print(ln)


@app.cell
def _(mo):
    mo.md(
        r"""## Split the images into sets that hold different views of the same label"""
    )


@app.cell
def _(areas):
    labels = [
        areas[0:11],
        areas[11:19],
        areas[19:33],
        areas[33:49],
        areas[49:65],
        areas[65:80],
        areas[80:90],
        areas[90:104],
    ]
    return (labels,)


@app.cell
def _(labels):
    [" ".join(lb.text) for lb in labels[2]]


@app.cell
def _(mo):
    mo.md(r"""## Perform a multiple sequence alignment on the OCRed text""")


@app.cell
def _(LineAlign, char_sub_matrix):
    def align(label):
        matrix = char_sub_matrix.get()
        aligner = LineAlign(substitutions=matrix)
        texts = [" ".join(lb.text) for lb in label]
        results = aligner.align(texts)
        return results

    return (align,)


@app.cell
def _(align, label_builder, labels):
    for label in labels:
        result = align(label)
        result = label_builder.filter_lines(result, threshold=32)
        cons = label_builder.consensus(result)
        cons_text = label_builder.substitute(cons)
        print()
        print("=" * 80)
        for line in result:
            line = " ".join(line.split())
            print(line)
        print("-" * 40)
        print(cons_text)


@app.cell
def _(mo):
    mo.md(
        r"""## Run a small language model (SML) on consensus text to get information"""
    )


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
