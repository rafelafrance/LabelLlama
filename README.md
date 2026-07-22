# Label Llama

## The view from 30,000 feet

Extract information from labels on images of museum specimens.

### Given images of museum specimens

### Output text to structured fields

The text is formatted and placed into named fields using the Darwin Core standard.

## How to set up LabelLlama

You will need the python environment package manager called `uv` as well as `git`.

### Step 1: Clone this repository

```bash
git clone https://github.com/rafelafrance/LabelLlama.git
cd LabelLlama
uv sync
```

### Step 3: Set up a server to run local models

#### LMStudio

lmstudio`is a wrapper and GUI around the`llama.cpp`library.
The GUI is convenient for downloading and running models locally.
Note you may run LM-Studio headless with`lms daemon`.
Of, course you don't have to run any models locally.
I use local models to OCR text on images of specimens and cleaning LM output some fields.

You can get the LM-Studio GUI and daemon [here](https://lmstudio.ai/)

```bash
lms daemon up
lms server start
lms load my-model
```

#### llama.cpp

Look at [server_llama_cpp.bash](https://github.com/rafelafrance/LabelLlama/blob/main/args/server_llama_cpp.bash) to see how I run a local server with llama.cpp.

### Extract information

This is the script that takes an image of a museum specimen and extracts label text directly from that.
