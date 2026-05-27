import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import logging
    import requests
    import concurrent.futures as conc
    from datetime import datetime
    from pathlib import Path

    import polars as pl

    from llama.pylib import prompt_util, str_util, timer

    return (prompt_util,)


@app.cell
def _(mo):
    model = mo.ui.text(label="Model", value="qwen/qwen3.6-27b")
    api_host = mo.ui.text(label="API host", value="http://localhost:1234/v1")
    temperature = mo.ui.number(
        label="Temperature", start=0.0, stop=2.0, step=0.1, value=0.1
    )
    threads = mo.ui.number(label="Threads", start=1, stop=100, step=1, value=2)
    mo.vstack([model, api_host, temperature, threads])
    return


@app.cell
def _(mo):
    prompt = mo.ui.file_browser(
        initial_path="prompts/fields",
        filetypes=[".md", ".txt"],
        multiple=False,
        label="Prompt",
    )
    prompt
    return (prompt,)


@app.cell
def _(mo, prompt, prompt_util):
    sys_prompt, field_names = prompt_util.read_lm_prompt(prompt.value[0].path)
    mo.md(sys_prompt)
    return (field_names,)


@app.cell
def _(field_names, mo, prompt_util):
    field_prompt = prompt_util.build_field_prompts(field_names)
    mo.md(field_prompt)
    return


@app.cell
def _(field_names, mo, prompt_util):
    field_template = prompt_util.build_field_template(field_names)
    mo.md(field_template)
    return


@app.cell
def _(mo):
    docs = mo.ui.file_browser(
        initial_path="data",
        filetypes=[".csv", ".tsv"],
        multiple=False,
        label="Label CSV",
    )
    docs
    return


if __name__ == "__main__":
    app.run()
