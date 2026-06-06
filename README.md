# Label Llama

**This project is under heavy development.**

- [How to set up LabelLlama](#how-to-set-up-labelllama)
- [OCR images of museum specimens](#ocr-images-of-museum-specimens)
- [Extract terms with an LLM](#extract-terms-with-an-llm)
- [Clean LLM output](#clean-llm-output)

## The view from 30,000 feet

Extract information from labels on images of museum specimens.

### Given images of museum specimens

![Herbarium Sheet](assets/sheet.jpg)

### OCR text on the images

![OCRed Text](assets/show_ocr_text.png)

OCRed text from the label on the lower right of the sheet.

### Find text text in the labels

![text.png|Label Text](assets/text.png)

This is clearly from another sheet and label.
The colors indicate text matched to fields.

### Output text to structured fields

![Label Traits](assets/traits.png)

The text is formatted and placed into named fields using the Darwin Core format.

## How to set up LabelLlama

You will need the python environment package manager called `uv` as well as `git`.

### Step 1: Clone this repository

```bash
git clone https://github.com/rafelafrance/LabelLlama.git
cd LabelLlama
git checkout v0.1.1
```

This project is under **heavy** development, tag `v0.1.1` will pin the code to a known state.

### Step 2: Set up the environment using `uv`

```bash
uv sync
```

### Step 3: Set up LM-Studio to run local models

`lmstudio` is a wrapper and GUI around the `llamma.cpp` library.
The GUI is convenient for downloading and running models locally.
Note you may run LM-Studio headless with `lms daemon`.
Of, course you don't have to run any models locally.
I use local models to OCR text on images of specimens and cleaning LM output some fields.

You can get the LM-Studio GUI and daemon [here](https://lmstudio.ai/)

## OCR images of museum specimens

### Start local OCR model

I run a local model to OCR images. I use (for now) Chandra-OCR on the LM-Studio daemon.

```bash
lms daemon up
lms server start
```

### OCR script arguments

The important arguments for running the OCR script are shown below.

- --image-dir: A directory full of museum specimen images that you want to OCR.
- --docs: Put the OCRed text into this file.
- --model: Use this model for the OCR.

Note that the script will append to the --docs file so that you may rerun the
script after an error or combine the output from multiple runs into a single file.

The output CSV has 3 columns.

1. The "source" path, which is the image path in this case.
2. How long it took the OCR to run, "elapsed".
3. The OCR text itself, "text".

## Extract terms with an LLM

`parse_text.py` gets the raw field extracts from a Large Language Model (LLM).
The fields will contain hallucinations, interpretations, and odd notations,
all of which I try to fix in the next step.

The important arguments for this process are:

- --docs: demo/ocr_demo_docs.csv The output from the OCR script.
- --out-file: demo/lm_extracts.csv Where to put the extraction output.
- --model: "openai/gpt-5-nano" The LLM to use.
- --api-key: The key required to run the LLM.
- --threads: 5 You can parallelize the process, which speeds things up.
- --signature: herbarium The fields to extract from the OCRed text.

You will need to set up an account with payment information to get the API key.
In this case it would be with OpenAI.

Note that the "text" column in the output file may be different from the raw input
in the OCR file. I run a text preprocessing step before sending it to the LLM.
I remove obvious header and footers. I also join lines of text if there
is only one line break (return) between them. Labels have limited horizontal space,
so sentences are split across multiple lines. However, the models tend to do better
if there are no line breaks in a sentence. If there are two or more line breaks
in a row then the breaks are likely to have semantic meaning,
but if there is only one break then it probably doesn't.
I want to record the exact text given to the LLM.

## Clean LLM output

This is where I clean up the oddities in the output from the LLM and put it into a usable format.
The important arguments for this script are:

- --in-file: demo/lm_extracts.csv This is the output from the `parse_text.py` script.
- --out-file: demo/lm_extracts_post.csv Output the cleaned results to this file.
