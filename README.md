# Label Llama

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
```

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
lms load chandra-ocr
```

Although these instructions are for LM-Studio, there is no reason why you can't use Ollama, or llama.cpp or an external server to OCR the images. LabelLlama doesn't care.
Just change the server parameters.

### OCR script arguments

|Option group|Argument|Type|Description|Default|Notes|
|:----:|:--------|:---|:----------|:------:|:------|
|I/O|--image-glob|glob|Get all images matching this glob/pattern. You may need to quote this argument.|required|An example: 'museum/data/images1/*.jpg'|
|I/O|--ocr-file|path|Put OCRed text into this file. This appends data to the file.|required|An example: data/museum/data/images1.csv|
|prompt|--prompt|path|A markdown file with a prompt used to OCR images.|prompts/ocr_v2.md||
|model|--model|string|Use this language model.|chandra-ocr|So, far this is the best local model for our OCR needs.|
|model|--api-host|string|URL for the language model.|http://localhost:1234/v1|The default is for LM-Studio, but you could use Ollama's or another URL here.|
|model|--threads|int|How many parallel threads to run.|2|Increase this if the model server is powerful enough.|
|model|--temperature|float|Model's temperature.|0.1|We don't want the model to get creative, so keep this low.|
|model|--max-tokens|int|The OCR model's response maximum tokens.|2048|2048 tokens is roughly 1.5K words, which is more than enough for most museum specimens. I keep this low to truncate model loops.|
|model|--timeout|int|How long to wait for the OCR model to complete in seconds.|120|2 minutes is a life time for OCR.|
|model|--convert-html|flag|If the OCR model insists on producting HTML output, you may want to convert it to text. Use this flag to trigger the conversion.|false|Chandra-2 does this.|
|logging|--log-file|path|Append logging notices to this file.|None|It also logs the script options so you may use this to keep track of what you did.|
|logging|--notes|string|Notes for logging.|None|They only appear in the log file.|
|debugging|--limit|int| Only OCR this many images.|None||

The output CSV has 4 columns.

1. The status which is "success" or "error".
2. The "source" path, which is the image path in this case.
3. How long it took the OCR to run, "elapsed".
4. The OCR text itself, "text".

## Extract terms with an LLM

`parse_text.py` gets the raw field extracts from a Large Language Model (LLM).
The fields will contain hallucinations, interpretations, and odd notations,
all of which I try to fix in the next step.

### Parse script arguments

|Option group|Argument|Type|Description|Default|Notes|
|:----:|:--------|:---|:----------|:------:|:------|
|I/O|--ocr-file|path|Parse label text from this file.|required|We need only 'source' and 'text' columns for valid input, so any CSV/TSV/JSON/JSONL file with those columns is fine.|
|I/O|--parse-file|path|Write the LM results to this file.|required|Handles (.json, .jsonl, .csv, .tsv)|
|prompt|-prompt|path|A markdown file with a prompt and list of fields to parse.|required|For example prompts/fields/herbarium.md.|
|model|-model|string|Use this language model.|lm_studio/google/gemma-4-26b-a4b|There is a speed vs. cost tradeoff between local and hosted models. Local models are cheaper but hosted models are much faster.
|model|--api-host|string|URL for the LM model.|http://localhost:1234/v1|The default is for LM-Studio, but I also use ChatGPT-nano and other server models.|
|model|--threads|int|How many parallel threads to run.|10|For ChatGPT-nano I will increase this to 20 or more, and for a local model I will reduce this to 4.|
|model|--temperature|float|Model's temperature.|None|We don't want the model to get creative, so keep this value low. Some hosted servers don't like this option so there is no default.|
|model|--timeout|int|How long to wait for the LM to respond in seconds.|120|2 minutes is a life time for parsing label text.|
|logging|-log-file|string|Append logging notices to this file.|None|It also logs the script arguments so you may use this to keep track of what you did.|
|logging|--notes|string|Notes for logging.|None|They only appear in the log file.|
|debugging|--limit|int|Limit to this many records.|None||

If you want to use a hosted server for this you need to set up an account with payment information. The host will give you an API key which you need to put into the `LabelLlama/.env` file.
```
LLM_API_KEY=sk-my-key-like-an-openai-key
```


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
