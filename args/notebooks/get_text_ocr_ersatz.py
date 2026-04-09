import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", css_file="")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # OCR images of herbarium sheets

    **Note** These OCR job parameters are reconstructed after the fact.
    They are here to give you an idea of how I went about creating this data not as a
    100% accurate reprentation of what happened -- that ship has sailed.
    """)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from pathlib import Path

    from llama import get_text
    from llama.common.args_util import to_args

    return Path, get_text, to_args


@app.cell
def _(Path):
    doc_tsv = Path("data/herbarium/ocr_text.tsv")
    return (doc_tsv,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## OCR jobs
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The initial run.
    """)


@app.cell
def _(doc_tsv, get_text, to_args):
    args1 = get_text.parse_args(
        to_args(
            doc_tsv=doc_tsv,
            image_dir="./data/herbarium/sheets_001",
        )
    )
    # get_text.ocr_images(args1)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Firefox keeps dying on me. It's happened with both jupyter and marimo.
    It appears to be related to a memory leak with lmstudio
    [bug](https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/1209).
    The server is holding onto data.
    the data that aleady exists.
    """)


@app.cell
def _(doc_tsv, get_text, to_args):
    args2 = get_text.parse_args(
        to_args(
            doc_tsv=doc_tsv,
            image_dir="./data/herbarium/sheets_001",
            notes=(
                "The job keeps crashing on me due to an lmstudio bug. "
                "Capture remaining sheets from job 1."
            ),
        )
    )
    # get_text.ocr_images(args2)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's see if we can pick up some of those errors using a gemma-3 model.
    """)


app._unparsable_cell(
    r"""
    args3 = get_text.parse_args(
        to_args(
            doc_tsv=doc_tsv",
            image_dir="./data/herbarium/sheets_001",
            model="google/gemma-3-27b",
            notes="Try a difference model on sheets that errored before on jobs 1 & 2.",
        )
    )
    # get_text.ocr_images(args3)
    """,
    name="_",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A new tranche of 33 images dropped (2025-11-18). Add them to the dataset.
    They're all supposed to have either a TRS or a UTM.
    It looks like it's almost exclusively TRSs.
    """)


@app.cell
def _(doc_tsv, get_text, to_args):
    args4 = get_text.parse_args(
        to_args(
            doc_tsv=doc_tsv,
            image_dir="./data/herbarium/sheets_001",
            notes="""A new group of sheet images.""",
        )
    )
    # get_text.ocr_images(args4)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There were 3/33 records that errored out.
    That's a very high percentage.
    Now try tweaking the parameters and using a different model.
    """)


@app.cell
def _(doc_tsv, get_text, to_args):
    args5 = get_text.parse_args(
        to_args(
            doc_tsv=doc_tsv,
            image_dir="./data/herbarium/CoordinateExamplesNov25",
            model="google/gemma-3-27b",
            context_length=8192,
            notes="""Retry errored sheets in job 5 with a new model and params.""",
        )
    )
    # get_text.ocr_images(args5)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is a larger set (~1500) of images that contain UTM and TRS notations.
    """)


@app.cell
def _(doc_tsv, get_text, to_args):
    args6 = get_text.parse_args(
        to_args(
            doc_tsv=doc_tsv,
            image_dir="./data/herbarium/utm_trs_test",
            notes="""A set of herbarium sheets that contain TRS & UTM notations.""",
        )
    )
    # get_text.ocr_images(args6)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    _Mea culpa_. I forgot to prevent my computer from sleeping,
    so the job died part of the way thru. Restarting.
    """)


@app.cell
def _(doc_tsv, get_text, to_args):
    args7 = get_text.parse_args(
        to_args(
            doc_tsv=doc_tsv,
            image_dir="./data/herbarium/utm_trs_test",
            notes="""A set of herbarium sheets that contain TRS & UTM notations.
                continued""",
        )
    )
    # get_text.ocr_images(args7)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Process the errors for the TRS & UTM dataset.
    """)


@app.cell
def _(doc_tsv, get_text, to_args):
    args8 = get_text.parse_args(
        to_args(
            doc_tsv=doc_tsv,
            image_dir="./data/herbarium/utm_trs_test",
            model="google/gemma-3-27b",
            context_length=8192,
            notes="Retry errored sheets in ocr_run_id 5 with a new model and params.",
        )
    )
    # get_text.ocr_images(args8)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Did I OCR all of the images?
    """)


@app.cell
def _(Path, doc_tsv, get_text):
    actual = set(get_text.get_docs_read(doc_tsv))

    expected = set(Path("./data/herbarium/sheets_001/").glob("*.jpg"))
    expected |= set(Path("./data/herbarium/CoordinateExamplesNov25/").glob("*.jpg"))
    expected |= set(Path("./data/herbarium/utm_trs_test/").glob("*.jpg"))

    print(f"{len(actual)=}")
    print(f"{len(expected)=}")

    len(actual) == len(expected)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
