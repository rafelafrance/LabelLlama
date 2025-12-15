import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor
    return AutoModelForImageTextToText, AutoProcessor, torch


@app.cell
def _():
    prompt = """
    You are given images of herbarium specimens of plants.
    I want you to extract all of the written text from every
    label on the sheet. This includes text from typewritten, handwritten, barcodes,
    QR-codes, and stamps. Do not get confused by the plant itself which will be
    in the center of the page.
    Do not hallucinate.
    """
    return (prompt,)


@app.cell
def _():
    model_id = "allenai/olmOCR-7B-0825"
    return (model_id,)


@app.cell
def _(AutoModelForImageTextToText, AutoProcessor, model_id, torch):
    processor = AutoProcessor.from_pretrained(model_id)
    model = (
        AutoModelForImageTextToText.from_pretrained(model_id, dtype=torch.float16)
        .to("cuda")
        .eval()
    )
    return model, processor


@app.cell
def _():
    sheet_dir = "/home/rafe/work/LabelLlama/data/herbarium/sheets_001/"
    return (sheet_dir,)


@app.cell
def _(prompt, sheet_dir):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": sheet_dir + "803231.jpg",
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    return (messages,)


@app.cell
def _(messages, model, processor):
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
    return (inputs,)


@app.cell
def _(inputs, model, processor, torch):
    torch.cuda.empty_cache()

    output_ids = model.generate(**inputs, max_new_tokens=10_000)
    generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(inputs.input_ids, output_ids, strict=False)
    ]
    output_text = processor.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
    )
    return (output_text,)


@app.cell
def _(output_text):
    for line in output_text:
        print("=" * 80)
        print(line)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
