import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import base64
    import logging
    import requests
    import concurrent.futures as concur
    from datetime import datetime
    from pathlib import Path

    import polars as pl

    from llama.pylib import prompt_util, str_util, timer

    return (
        Path,
        base64,
        concur,
        datetime,
        logging,
        pl,
        prompt_util,
        requests,
        str_util,
        timer,
    )


@app.cell
def _(mo):
    model = mo.ui.text(label="Model", value="chandra-ocr")
    api_host = mo.ui.text(label="API host", value="http://localhost:1234/v1")
    temperature = mo.ui.number(
        label="Temperature", start=0.0, stop=2.0, step=0.1, value=0.1
    )
    threads = mo.ui.number(label="Threads", start=1, stop=100, step=1, value=2)

    mo.vstack([model, api_host, temperature, threads])
    return api_host, model, temperature, threads


@app.cell
def _(Path, mo, prompt_util):
    prompt_default = Path("prompts") / "ocr.md"
    sys_prompt = prompt_util.read_prompt(prompt_default)
    mo.md(sys_prompt)
    return (sys_prompt,)


@app.cell
def _(mo):
    image_files = mo.ui.file_browser(label="Images", initial_path="data")
    image_files
    return (image_files,)


@app.cell
def _(base64, datetime, logging, requests, str_util, timer):
    from xai_sdk.chat import file


    def ocr_one_image(
        file_path: str,
        api_host: str,
        model_name: str,
        sys_prompt: str,
        temp: float,
    ) -> dict:
        """Run OCR on an image via the OpenAI-compatible API."""
        # Encode the image as base64
        with open(file_path, "rb") as f:
            base64_img = base64.b64encode(f.read()).decode("utf-8")

        began = datetime.now()

        url = f"{api_host}/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_img}",
                                "detail": "high",
                            },
                        },
                    ],
                },
            ],
            "temperature": temp,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            text = str_util.clean_ocr(content)
            status = "success"

        except Exception as e:
            logging.exception("API error")
            status = "error"
            text = str(e)

        result = {
            "status": status,
            "source": file_path,
            "text": text,
            "elapsed": str(timer.elapsed(began)),
        }
        return result

    return (ocr_one_image,)


@app.cell
def _(
    api_host,
    concur,
    df_results,
    image_files,
    mo,
    model,
    ocr_one_image,
    pl,
    polars,
    sys_prompt,
    temperature,
    threads,
):
    def ocr_images() -> polars.DataFrame:
        results = []

        if not image_files.value:
            mo.md("No images selected. Please select images above to begin OCR processing.")
            mo.ui.dataframe(df_results)
            return

        with mo.status.progress_bar(total=len(image_files.value), title="Images") as bar:
            with concur.ThreadPoolExecutor(max_workers=threads.value) as executor:
                futures = {
                    executor.submit(
                        ocr_one_image,
                        f.path,
                        api_host.value,
                        model.value,
                        sys_prompt,
                        temperature.value,
                    ): f.path
                    for f in image_files.value
                }
                for future in concur.as_completed(futures):
                    results.append(future.result())
                    bar.update()

        results = [r for r in results if r["status"] != "error"]
        results = sorted(results, key=lambda r: r["source"])

        df_results = pl.DataFrame(results)
        df_results = df_results.select(["source", "text", "elapsed"])
        return df_results

    return (ocr_images,)


@app.cell
def _(ocr_images):
    output_df = ocr_images()
    output_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    TODO:
    - Display OCR results along side of the image
    - Format the input controls, they look terrible
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
