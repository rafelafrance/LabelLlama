# Label Llama

Label Llama uses LLMs to digitize information from labels on images of museum specimens.
It OCRs the labels, extracts the text into named Darwin Core fields, cleans the field values,
and provides reports that compare the results.

The fields follow the[Darwin Core](https://dwc.tdwg.org/) standard, so the output is compatible with natural history data repositories.

## What it does

Given an image of a herbarium sheet (or an insect diode):

1. **OCR** — transcribe all of the label text.
2. **Parse** — extract the text into named Darwin Core fields.
3. **Clean** — refine the field values, and calculate field values from the other fields.

### Example: from sheet to fields

An input image of a herbarium sheet:

![Herbarium sheet](assets/sheet.jpg)

The OCR step transcribes the label text:

![OCRed label text](assets/show_ocr_text.png)

The parse step maps spans of the text to Darwin Core fields:

![Fields in the OCRed text](assets/text.png)

The clean step produces the final fields and values:

![Cleaned Darwin Core fields](assets/traits.png)

## The pipeline

Each stage is a standalone script. The scripts exchange plain CSV files,
so you can run them in any order or mix and match model runs.

| Stage             | Script                  | Input           | Output                                                      |
| ----------------- | ----------------------- | --------------- | ----------------------------------------------------------- |
| OCR               | `llama/ocr_images.py`   | specimen images | CSV with a `text` column holding the transcribed labels     |
| Parse from text   | `llama/parse_text.py`   | OCR CSV         | CSV with one column per field                               |
| Parse from images | `llama/parse_images.py` | specimen images | CSV with one column per field (multimodal model, skips OCR) |
| Clean             | `llama/clean_fields.py`   | parsed CSV      | CSV with cleaned field values and calculated fields         |

### There are 2 workflows

![LabelLlama work flows](assets/LL.jpg)

1. A 3-step workflow (works well locally)
   1. OCR text from images (ocr_images.py)
   2. Parse text (parse_text.py)
   3. Clean parsed data (clean_fields.py)
2. A 2-step workflow (if you have a larger model)
   1. You can parse data from an image directly (parse_images.py)
   2. Clean parsed text (clean_fields.py)

### Prompts and fields

The prompt markdown files in `prompts/` declare which fields a run extracts. Each field is a link to a Python class:

- `llama/llm_fields/` — _LLM fields_: the class holds the instructions sent to the LLM model and validates its answer.
- `llama/calc_fields/` — _calculated fields_: deterministic code that derives the value from other fields.

The current prompt files are:

- `ocr_v1.md` and `ocr_v2.md` for OCR,
- `herbarium_v2.md` for herbarium sheets, and `diode_v2.md` for dragonflies using the 3-step workflow
- `diode_one_v1.md` for dragonflies using the 2-step workflow

`llama/reports/show_prompt.py` prints the full system message that a prompt file produces.

### Reports

The scripts in `llama/reports/` compare and visualize the output of model runs:

| Script                       | What it does                                                                       |
| ---------------------------- | ---------------------------------------------------------------------------------- |
| `compare_ocr.py`             | Side-by-side comparison of the OCR text from two model runs (stdout).              |
| `compare_parses.py`          | Side-by-side comparison of parsed fields from several model runs (stdout).         |
| `compare_output_gold.py`     | Scores parsed output against a gold standard file; writes a CSV report.            |
| `compare_output_gbif.py`     | Scores cleaned output against GBIF occurrence data; writes an ODS report.          |
| `compare_output_majority.py` | Picks the winning field value across several model runs; writes an ODS report.     |
| `show_pipeline.py`           | Single-file HTML report showing each image, its OCRed text, and the parsed fields. |
| `show_prompt.py`             | Prints the system message that a prompt markdown file produces.                    |

### Data utilities

The scripts in `llama/data_utils/` help build the input data:

- `util_get_gbif_data.py` — narrows the large GBIF dump TSVs down to the
  images you downloaded.
- `util_image_download.py` — downloads specimen images from a GBIF
  multimedia TSV.
- `util_merge_files.py` — combines multiple files (`*.csv`, `*.tsv`, etc.)
  into a single file.

## How to set up LabelLlama

You will need the python environment package manager called `uv` as well
as `git`.

### Step 1: Clone this repository

```bash
git clone https://github.com/rafelafrance/LabelLlama.git
cd LabelLlama
uv sync
```

### Step 2: (Optional) Set up a server to run local models

You don't have to run any models locally; hosted models work too.

#### LM Studio

LM Studio is a wrapper and GUI around the `llama.cpp` library.
The GUI is convenient for downloading and running models locally.
Note you may run LM Studio headless with `lms daemon`.

You can get the LM Studio GUI and daemon [here](https://lmstudio.ai/).

```bash
lms daemon up
lms server start
lms load my-model
```

#### llama.cpp

You can run `llama-server` directly from the
[llama.cpp](https://github.com/ggml-org/llama.cpp) project; the scripts
in `args/` show the options I use.

### Step 3: Extract information

Run the pipeline stages in order, or skip straight to the stage you
want. For example, for a batch of herbarium sheets:

```bash
uv run llama/ocr_images.py \
    --image-glob "data/my_sheets/images/*.jpg" \
    --ocr-file data/my_sheets/ocr.csv \
    --prompt-md prompts/ocr_v2.md \
    --model-id allenai/olmocr-2-7b

uv run llama/parse_text.py \
    --ocr-file data/my_sheets/ocr.csv \
    --parsed-file data/my_sheets/parsed.csv \
    --prompt-md prompts/herbarium_v2.md \
    --model-id "gpt-5-nano-2025-08-07" \
    --threads 20

uv run llama/clean_fields.py \
    --parsed-file data/my_sheets/parsed.csv \
    --clean-file data/my_sheets/clean.csv \
    --prompt-md prompts/herbarium_v2.md \
    --model-id "gpt-5-nano-2025-08-07"
```

For local models, add `--api-host` pointing at your server, e.g.
`--api-host http://localhost:1234/v1`.

## The data directory

CSV input and output files live under `data/`, organized per batch.
The bash scripts in `args/` are the real-world examples: each one is a
recorded invocation of a script for a specific data batch, and the
`--log-file` options in them record what was run.
