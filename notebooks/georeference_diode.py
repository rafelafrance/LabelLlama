import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""#""")
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Experiment: Georeference Diode Insect Labels

    Labels on museum specimens often contain locality & administrative unit data.
    This is an experiment to see if we can get a language model to extract that data. 
    I'm trying to go from raw text to decimal latitudes and longitudes.

    Given:
    - OCRed text from a batch of labels

    The output fields are:
    - Verbatim coordinates
    - Decimal latitude
    - Decimal longitude
    - Geodetic datum
    - Uncertainty in meters
    """
    )
    return


@app.cell
def _():
    import json
    from pathlib import Path

    import dspy
    from rich import print as rprint

    from llama.pylib import darwin_core as dwc
    return Path, dspy, dwc, json, rprint


@app.cell
def _(dspy):
    class Georeference(dspy.Signature):
        # Input fields
        text: str = dspy.InputField(default="", desc="Insect label text")
        prompt: str = dspy.InputField(default="", desc="Extract these traits")

        # Output fields
        verbatim_coordinates: str = dspy.OutputField(
            default="",
            desc="Verbatim coordinates",
            alias="dwc:verbatimCoordinates",
        )
        decimal_latitude: float = dspy.OutputField(
            default=-1.0,
            desc="Decimal latitude, values go from -90.0 to 90.0 inclusive",
            alias="dwc:decimalLatitude",
        )
        decimal_longitude: float = dspy.OutputField(
            default=-1.0,
            desc="Decimal latitude, values go from -180.0 to 180.0 inclusive",
            alias="dwc:decimalLongitude",
        )
        geodetic_datum: str = dspy.OutputField(
            default="",
            descr="Geodetic datum, or spatial reference system of the geographic coordinates",
            alias="dwc:geodeticDatum",
        )
        coordinate_uncertainty_in_meters: float = dspy.OutputField(
            default=-1.0,
            descr="How accurate are the decimal latitude and decimal longitude",
            alias="dwc:coordinateUncertaintyInMeters",
        )
    return (Georeference,)


@app.cell
def _(mo):
    mo.md(r"""This is used when presenting the data to the scientists.""")
    return


@app.cell
def _(Georeference):
    to_dwc = {
        field[0]: field[1].alias
        for field in Georeference.model_fields.items()
        if field[0] not in ("text", "prompt")
    }
    to_dwc
    return (to_dwc,)


@app.cell
def _():
    return


@app.cell
def _():
    prompt = """
    You are an assistant specializing in georeferencing locations using locality descriptions.
    You have been assigned a task for georeferencing coordinates in the domain of
    biogeography and ecology.
        Turn all locality and place data into a decimal latitude and decimal longitude.
        If it is not mentioned return an empty value. Do not hallucinate.
        """
    return (prompt,)


@app.cell
def _(Path, json):
    credentials_file = Path("data") / "credentials" / "openai.json"
    with credentials_file.open() as fcred:
        credentials = json.load(fcred)
    return (credentials,)


@app.cell
def _(credentials):
    model = "openai/gpt-5-mini"
    temperature = 1.0
    max_tokens = 16000
    api_key = credentials["key"]
    api_base = ""
    return api_key, max_tokens, model, temperature


@app.cell
def _(api_key, dspy, max_tokens, model, temperature):
    lm = dspy.LM(
        model,
        # api_base=api_base,
        api_key=api_key,
        cache=False,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    dspy.configure(lm=lm)
    return


@app.cell
def _(Georeference, dspy):
    extractor = dspy.Predict(Georeference.signature)
    return (extractor,)


@app.cell
def _(Path, json):
    input_json = Path("data") / "diode" / "olmocr_text_2.json"

    with input_json.open() as flab:
        label_data = json.load(flab)
    return (label_data,)


@app.cell
def _(dwc, extractor, label_data, prompt, rprint, to_dwc):
    predictions = []

    for i, label in enumerate(label_data, 1):
        rprint(f"[blue]{i} {'=' * 80}")
        rprint(f"[blue]{label['path']}")
        rprint(f"[blue]{label['text']}")

        pred = extractor(text=label["text"], prompt=prompt)

        rprint(f"[green]{pred}")

        as_dict = {
            "path": label["path"],
            "text": label["text"],
            "annotations": dwc.to_dwc_keys(pred.toDict(), to_dwc),
        }

        predictions.append(as_dict)

        if i > 1:
            break
    return (predictions,)


@app.cell
def _(Path, json, predictions):
    output_json = Path("data") / "diode" / "gpt5_mini_georeference_2.json"

    with output_json.open("w") as fout:
        fout.write(json.dumps(predictions, indent=4) + "\n")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
