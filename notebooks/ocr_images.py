import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium", css_file="marimo_custom.css")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # OCR a directory of images

    I am currently using 2 models for extracting text from images of museum specimens.

    1. First I use an OCR model to get all of the text from labels etc. on the museum specimen image.
    2. Next I use another model that extracts Darwin Core fields from the text gotten in step 1.

    This notebook is about step #1, transforming images into text.
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import argparse
    import csv
    import io
    import textwrap
    import warnings
    from collections import defaultdict
    from collections.abc import Iterable
    from dataclasses import InitVar, asdict, dataclass
    from datetime import datetime, timedelta
    from enum import IntEnum
    from pathlib import Path

    import duckdb
    import lmstudio as lms
    import polars as pl
    return Path, dataclass, datetime, duckdb, lms


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I like to know where the notebook thinks it's located so I get the paths right.
    """)
    return


@app.cell
def _(Path):
    Path().cwd()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Set up a database and tables used to store OCR information.

    I have learned from other projects that having dozens of CSV files is just horrible. I know they usually not planned and grow orgaincally, but I'm going for a database upfront. A DB also allows me to store metadata in the same location as the bulk of the data. And duckdb seems chic.
    """)
    return


@app.cell
def _(duckdb):
    cxn = duckdb.connect("data/herbarium/labelllama_herbarium.db")
    return (cxn,)


@app.cell
def _(cxn, mo):
    _df = mo.sql(
        f"""
        create sequence if not exists ocr_run_seq;
        create table if not exists ocr_run (
            ocr_run_id integer primary key default nextval('ocr_run_seq'),
            prompt         char,
            model          char,
            api_host       char,
            temperature    float,
            context_length integer,
            elapsed        interval,
            stamp          timestamptz,
        );

        create sequence if not exists ocr_id_seq;
        create table if not exists ocr (
            ocr_id integer primary key default nextval('ocr_id_seq'),
            ocr_run_id integer,
            image      char,
            text       char,
            error      char,
            elapsed    interval,
            stamp      timestamptz,
        );
        """,
        engine=cxn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a data class for arguments. There are a lot of parameters for the OCR process and it's convenient to put them into a single structure. This will also help with argparse setup when I migrate this code to a script.
    """)
    return


@app.cell
def _(Path, dataclass):
    @dataclass
    class Args:
        image_dir: Path  # Images of museum specimens are in this directory
        db: Path  # Output OCRed text to this database
        # Model parameters
        model_name: str = "noctrex/Chandra-OCR-GGUF/Chandra-OCR-Q4_K_S.gguf"
        api_host: str = "localhost:1234"  # URL for the LM model
        context_length: int = 4096  # Model's context length
        temperature: float = 0.1  # Model's temperature
        # Parameters for restarting the OCR process
        first: int | None = None  # Used for restarts. None == first
        last: int | None = None  # Used to stop early. None == last
        missing: bool = False  # Process all images in image_dir but not in ocr_csv
        retry: bool = False  # Retry all images where all previous attempts errored out
    return (Args,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Code dealing with record selection

    Get all image paths in the database. I don't think that Marimo will rerun this cell after inserts, I should verify this.
    """)
    return


@app.cell
def _(cxn, mo, ocr):
    all_records = mo.sql(
        f"""
        select * from ocr;
        """,
        engine=cxn
    )
    return (all_records,)


@app.cell
def _(all_records, cxn, mo):
    all_images = mo.sql(
        f"""
        select distinct image from all_records;
        """,
        engine=cxn
    )
    return (all_images,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Get records that only have errors. I.e. not successfully OCRed even once. Note that errors do not go away they are "overwritten" by later successful OCR attempts, typically with changed model parameters or a different model.
    """)
    return


@app.cell
def _(all_records, cxn, mo):
    all_errors = mo.sql(
        f"""
        select image, max(text) as top
            from all_records
            group by image
            having top = '';
        """,
        engine=cxn
    )
    return (all_errors,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Filter images by:

    - Record indexes using --first & --last arguments.
    - Missing images. The job crashed and you want all remaining images using the --missing flag.
    - The --retry flag only selects images that have never successfully OCRed, i.e. they always errored out. I use this to try a different model and/or parameters on the problem images.
    """)
    return


@app.cell
def _(Args, Path, all_errors, all_images):
    def filter_images(args: Args) -> list[Path]:
        image_paths = sorted(args.image_dir.glob("*.jpg"))

        # Get by indexes: --first & --last
        image_paths = image_paths[args.first : args.last]

        # Only get --missing image paths, images not already in the DB
        if args.missing:
            completed = {r[0] for r in all_images}
            image_paths = [p for p in image_paths if str(p) not in completed]

        # Get images to --retry, images with only errors
        if args.retry:
            errored = {r[0] for r in all_errors}
            image_paths = [p for p in image_paths if str(p) in errored]

        return image_paths
    return (filter_images,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup a local small language model (SLM)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A reasonable starting prompt. I will try variations on this later.
    """)
    return


@app.cell
def _():
    prompt = " ".join(
        """
        You are given an image of a museum specimen with labels.
        I want you to extract all of the text from every label on the specimen.
        This includes text from both typewritten and handwritten labels.
        Do not get confused by the specimen itself which is in the center of the image.
        I want plain text without HTML or markdown tags.
        Do not hallucinate.
        """.split()
    )
    return (prompt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create the model.
    """)
    return


@app.cell
def _(lms):
    def setup_model(
        client: lms.Client, model_name: str, temperature: float, context_length: int
    ) -> lms.llm:
        return client.llm.model(
            model_name,
            config={
                "temperature": temperature,
                "contextLength": context_length,
            },
        )
    return (setup_model,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Prepare an image and its prompt for sending to the server.
    """)
    return


@app.cell
def _(Path, lms):
    def build_chat_message(client: lms.Client, image_path: Path, prompt: str) -> lms.Chat:
        handle = client.files.prepare_image(image_path)
        chat = lms.Chat()
        chat.add_user_message(prompt, images=[handle])
        return chat
    return (build_chat_message,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    OCR an image and check for errors.
    """)
    return


@app.cell
def _(lms):
    def ocr_one_image(model: lms.llm, chat: lms.Chat) -> tuple[str, str]:
        ocr_text, ocr_error = "", ""
        try:
            ocr_text = model.respond(chat)
        except lms.LMStudioServerError as err:
            ocr_error = f"Server error: {err}"
        return str(ocr_text), ocr_error
    return (ocr_one_image,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Prepared SQL statements does not seem to be something that Marimo does with an SQL cell, so I have to do it the old fashioned way.
    """)
    return


@app.cell
def _():
    insert_run = """
        insert into ocr_run
            (prompt, model, api_host, temperature, context_length, stamp)
            values (?, ?, ?, ?, ?, current_localtimestamp())
            returning ocr_run_id;
    """

    insert_ocr = """
        insert into ocr
            (ocr_run_id, image, text, error, elapsed, stamp)
            values (?, ?, ?, ?, ?, current_localtimestamp());
    """

    update_run = """
        update ocr_run set elapsed = ? where ocr_run_id = ?;
    """
    return insert_ocr, insert_run, update_run


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    OCR all images.
    """)
    return


@app.cell
def _(
    Args,
    build_chat_message,
    cxn,
    datetime,
    filter_images,
    insert_ocr,
    insert_run,
    lms,
    mo,
    ocr_one_image,
    prompt,
    setup_model,
    update_run,
):
    def ocr_images(args: Args) -> None:
        job_began = datetime.now()

        with lms.Client(args.api_host) as client:
            image_paths = filter_images(args)

            run_id = cxn.execute(
                insert_run,
                [
                    prompt,
                    args.model_name,
                    args.api_host,
                    args.temperature,
                    args.context_length,
                ],
            ).fetchone()[0]

            model = setup_model(
                client, args.model_name, args.temperature, args.context_length
            )

            for image_path in mo.status.progress_bar(image_paths, title="OCR Progress"):
                rec_began = datetime.now()

                chat = build_chat_message(client, image_path, prompt)

                ocr_text, ocr_error = ocr_one_image(model, chat)

                cxn.execute(
                    insert_ocr,
                    [
                        run_id,
                        str(image_path),
                        ocr_text,
                        ocr_error,
                        datetime.now() - rec_began,
                    ],
                )

            job_elapsed = datetime.now() - job_began
            cxn.execute(update_run, [job_elapsed, run_id])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## OCR runs
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The initial run.
    """)
    return


@app.cell
def _(Args, Path):
    args1 = Args(
        image_dir=Path("./data/herbarium/sheets_001"),
        db=Path("./data/herbarium/labelllama_herbarium.db"),
    )
    # ocr_images(args1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Firefox keep dying on me. It's happened with both jupyter and marimo. It appears to be related to a memory leak with lmstudio [bug](https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/1209). The server is holding onto data. I've created the `--missing` parameter so I can restart a job without overwriting the data that exists.
    """)
    return


@app.cell
def _(Args, Path):
    args2 = Args(
        image_dir=Path("./data/herbarium/sheets_001"),
        db=Path("./data/herbarium/labelllama_herbarium.db"),
        missing=True,  # Process only missing records
    )
    # ocr_images(args2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's see if we can pick up some of those errors using a gemma-3 model.
    """)
    return


@app.cell
def _(Args, Path):
    args3 = Args(
        image_dir=Path("./data/herbarium/sheets_001"),
        db=Path("./data/herbarium/labelllama_herbarium.db"),
        model_name="google/gemma-3-27b",  # New model
        retry=True,  # Only try sheets that always errored before
    )
    # ocr_images(args3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A new tranche of 33 images dropped (2025-11-18). Add them to the dataset. They're all supposed to have either a TRS or a UTM. It looks like it's almost exclusively TRSs.
    """)
    return


@app.cell
def _(Args, Path):
    args4 = Args(
        image_dir=Path("./data/herbarium/CoordinateExamplesNov25"),  # New dir
        db=Path("./data/herbarium/labelllama_herbarium.db"),
    )
    # ocr_images(args4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There were 3/33 records that errored out. That's a very high percentage. Now try tweaking the parameters and using a different model.
    """)
    return


@app.cell
def _(Args, Path):
    args5 = Args(
        image_dir=Path("./data/herbarium/CoordinateExamplesNov25"),
        db=Path("./data/herbarium/labelllama_herbarium.db"),
        model_name="google/gemma-3-27b",  # New model
        retry=True,  # Retry errored records with different parameters
        context_length=8192,  # Doubled the context
    )
    # ocr_images(args5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    No errors remain.
    """)
    return


@app.cell
def _(all_errors):
    len(all_errors)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Examine the results.
    """)
    return


@app.cell
def _(all_records, mo):
    image_idx = mo.ui.slider(
        1,
        len(all_records),
        full_width=True,
        debounce=True,
        show_value=True,
    )
    image_idx
    return (image_idx,)


@app.cell
def _(cxn, image_idx, mo):
    image_rec = cxn.execute(
        "select * from all_records where ocr_id = ?",
        [image_idx.value],
    ).df()

    print(image_rec.at[0, "text"])
    mo.image(src=image_rec.at[0, "image"])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
