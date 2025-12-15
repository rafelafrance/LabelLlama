import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import csv
    import json
    from pathlib import Path
    from pprint import pp

    import marimo as mo

    from llama.data_formats.label_types import flatten_dict
    return Path, csv, flatten_dict, json


@app.cell
def _(Path):
    data_dir = Path("../data/diode")

    json_files = {
        "gpt5": data_dir / "gpt5_annotations_2.json",
        "mini": data_dir / "gpt5_mini_annotations_2.json",
        "gemma": data_dir / "gemma3_annotations_2.json",
    }
    return data_dir, json_files


@app.cell
def _(json, json_files):
    with json_files["gpt5"].open() as f:
        gpt5_json = json.load(f)

    with json_files["mini"].open() as f:
        mini_json = json.load(f)

    with json_files["gemma"].open() as f:
        gemma_json = json.load(f)
    return gemma_json, gpt5_json, mini_json


@app.cell
def _(gemma_json, gpt5_json, mini_json):
    json_data = [gpt5_json, mini_json, gemma_json]
    return (json_data,)


@app.cell
def _(flatten_dict, json_data):
    out = []
    out.append(["key", "gpt-5", "gpt-5-mini", "gemma-3"])
    for gpt5, mini, gemma in zip(*json_data, strict=True):
        flatten_dict(gpt5)
        flatten_dict(mini)
        flatten_dict(gemma)

        if len(gpt5) != len(mini) or len(mini) != len(gemma):
            raise ValueError("JSON files are not aligned.")

        for k in gpt5.keys():
            if k in ("path", "text"):
                out.append([k, gpt5[k], "", ""])
            else:
                out.append([k, gpt5[k], mini[k], gemma[k]])
    return (out,)


@app.cell
def _(csv, data_dir, out):
    out_file = data_dir / "gpt5_gpt5mini_gemma3_comparison.csv"
    with out_file.open("w") as fout:
        writer = csv.writer(fout)
        for ln in out:
            writer.writerow(ln)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
