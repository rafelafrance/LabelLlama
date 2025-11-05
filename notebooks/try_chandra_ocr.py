import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        r"""The chandra_ocr model scores better than olmocr on most tests. I wanted to give it a try. However, there were issues getting it to run on this machine. AMD GPU using ROCm, etc. I think that I was just too early and will attempt it later when some of the kinks may get worked out."""
    )
    return


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    from PIL import Image
    # from transformers import AutoModel, AutoProcessor
    # from chandra.model.hf import generate_hf
    # from chandra.model.schema import BatchInputItem
    # from chandra.output import parse_markdown

    # from qwen_vl_utils import process_vision_info
    # from transformers import Qwen3VLForConditionalGeneration, Qwen3VLProcessor

    # from chandra.model.schema import BatchInputItem, GenerationResult
    # from chandra.model.util import scale_to_fit
    # from chandra.output import fix_raw
    # from chandra.prompts import PROMPT_MAPPING
    # from chandra.settings import setting
    return (mo,)


@app.cell
def _():
    # def load_model():
    #     device_map = "auto"
    #     if settings.TORCH_DEVICE:
    #         device_map = {"": settings.TORCH_DEVICE}

    #     kwargs = {
    #         "dtype": settings.TORCH_DTYPE,
    #         "device_map": device_map,
    #     }
    #     if settings.TORCH_ATTN:
    #         kwargs["attn_implementation"] = settings.TORCH_ATTN

    #     model = Qwen3VLForConditionalGeneration.from_pretrained(
    #         settings.MODEL_CHECKPOINT, **kwargs
    #     )
    #     model = model.eval()
    #     processor = Qwen3VLProcessor.from_pretrained(settings.MODEL_CHECKPOINT)
    #     model.processor = processor
    #     return model
    return


@app.cell
def _():
    # model = load_model()
    # model.processor = AutoProcessor.from_pretrained("datalab-to/chandra")

    # path = Path("data/herbarium/sheets_001/89248.jpg")
    # image = Image.open(path).convert("RGB")

    # batch = [BatchInputItem(image=image, prompt_type="ocr_layout")]

    # result = generate_hf(batch, model)[0]
    # markdown = parse_markdown(result.raw)
    # markdown
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
