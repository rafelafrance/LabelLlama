import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium", css_file="marimo_custom.css")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # OCR a directory of images

    I am currently using 2 models for extracting text from images of museum specimens.

    1. First I use an OCR model to get all of the text from labels etc. on the museum specimen image.
    2. Next I use another model that extracts Darwin Core fields from the text gotten in step 1.
    3. I do a final formatting pass on the data from step #2.

    This notebook is about step #1, transforming images into text.
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from dataclasses import dataclass
    from datetime import datetime
    from pathlib import Path

    import duckdb
    import lmstudio as lms
    import polars as pl
    return Path, dataclass, datetime, duckdb, lms, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note:

    `export  POLARS_IMPORT_INTERVAL_AS_STRUCT=1`

    before running this notebook.
    """)
    return


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

    I have learned from other projects that having dozens of CSV files is just horrible. I know they usually not planned and grow orgaincally, but I'm going for a database up front. A DB also allows me to store metadata in the same location as the bulk of the data. And duckdb seems chic.
    """)
    return


@app.cell
def _(Path):
    db_path = Path("data/herbarium/labelllama_herbarium.duckdb")
    return (db_path,)


@app.cell
def _(Path, db_path, duckdb):
    def create_ocr_tables(db_path: Path) -> None:
        sql = f"""
            create sequence if not exists ocr_run_seq;
            create table if not exists ocr_run (
                ocr_run_id integer primary key default nextval('ocr_run_seq'),
                prompt         char,
                model          char,
                api_host       char,
                notes          char,
                temperature    float,
                context_length integer,
                ocr_run_elapsed interval,
                ocr_run_started timestamptz default current_localtimestamp(),
            );

            create sequence if not exists ocr_id_seq;
            create table if not exists ocr (
                ocr_id integer primary key default nextval('ocr_id_seq'),
                ocr_run_id   integer references ocr_run(ocr_run_id),
                image_path   char,
                ocr_text     char,
                ocr_error    char,
                ocr_elapsed  interval,
            );
            """

        with duckdb.connect(db_path) as cxn:
            cxn.execute(sql)


    create_ocr_tables(db_path)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a data class for arguments. There are a lot of parameters for the OCR process and it's convenient to put them into a single structure. This will also help with argparse setup when I migrate this code to a script.
    """)
    return


@app.cell
def _(Path, dataclass, db_path):
    @dataclass
    class Args:
        image_dir: Path  # Images of museum specimens are in this directory
        db: Path = db_path  # Output OCRed text to this database
        # Model parameters
        model_name: str = "noctrex/Chandra-OCR-GGUF/Chandra-OCR-Q4_K_S.gguf"
        api_host: str = "localhost:1234"  # URL for the LM model
        context_length: int = 4096  # Model's context length
        temperature: float = 0.1  # Model's temperature
        notes: str = ""  # Information about the OCR run
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
    """)
    return


@app.cell
def _(Path, duckdb, pl):
    def get_all_records(db_path: Path) -> pl.dataframe:
        with duckdb.connect(db_path) as cxn:
            return cxn.execute("select * from ocr;").pl()
    return (get_all_records,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Get all image paths in the database.
    """)
    return


@app.cell
def _(Path, duckdb, pl):
    def get_all_images(db_path: Path) -> pl.dataframe:
        with duckdb.connect(db_path) as cxn:
            all_images = cxn.execute("select distinct image_path from ocr;").pl()
        return all_images
    return (get_all_images,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Get records that only have errors. I.e. not successfully OCRed even once. Note that errors do not go away they are "overwritten" by later successful OCR attempts, typically with changed model parameters or a different model.
    """)
    return


@app.cell
def _(Path, duckdb, pl):
    def get_all_errors(db_path: Path) -> pl.dataframe:
        sql = """
            select image_path, max(ocr_text) as top
                from ocr
                group by image_path
                having top = '';
            """
        with duckdb.connect(db_path) as cxn:
            return cxn.execute(sql).pl()
    return (get_all_errors,)


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
def _(Args, Path, db_path, get_all_errors, get_all_images):
    def filter_images(args: Args) -> list[Path]:
        image_paths = sorted(args.image_dir.glob("*.jpg"))

        # Get by indexes: --first & --last
        image_paths = image_paths[args.first : args.last]

        # Only get --missing image paths, images not already in the DB
        if args.missing:
            completed = {r[0] for r in get_all_images(args.db).rows()}
            image_paths = [p for p in image_paths if str(p) not in completed]

        # Get images to --retry, images with only errors
        if args.retry:
            errored = {r[0] for r in get_all_errors(db_path).rows()}
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
    ## OCR all images.
    """)
    return


@app.cell
def _(Args, datetime, duckdb, filter_images, lms, mo, prompt):
    def ocr_images(args: Args) -> None:
        job_began = datetime.now()

        with lms.Client(args.api_host) as client, duckdb.connect(args.db) as cxn:
            image_paths = filter_images(args)

            run_id = cxn.execute(
                """
                insert into ocr_run
                    (prompt, model, api_host, notes, temperature, context_length)
                    values (?, ?, ?, ?, ?, ?)
                    returning ocr_run_id;
                """,
                [
                    prompt,
                    args.model_name,
                    args.api_host,
                    args.notes.strip(),
                    args.temperature,
                    args.context_length,
                ],
            ).fetchone()[0]

            model = client.llm.model(
                args.model_name,
                config={
                    "temperature": args.temperature,
                    "contextLength": args.context_length,
                },
            )

            for image_path in mo.status.progress_bar(image_paths, title="OCR Progress"):
                rec_began = datetime.now()

                handle = client.files.prepare_image(image_path)
                chat = lms.Chat()
                chat.add_user_message(prompt, images=[handle])

                ocr_text, ocr_error = "", ""
                try:
                    ocr_text = model.respond(chat)
                except lms.LMStudioServerError as err:
                    ocr_error = f"Server error: {err}"

                cxn.execute(
                    """
                    insert into ocr
                        (ocr_run_id, image_path, ocr_text, ocr_error, elapsed)
                        values (?, ?, ?, ?, ?);
                    """,
                    [
                        run_id,
                        str(image_path),
                        str(ocr_text),
                        ocr_error,
                        datetime.now() - rec_began,
                    ],
                )

            job_elapsed = datetime.now() - job_began
            cxn.execute(
                "update ocr_run set elapsed = ? where ocr_run_id = ?;",
                [job_elapsed, run_id],
            )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # OCR runs
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
    )
    # ocr_images(args1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Firefox keeps dying on me. It's happened with both jupyter and marimo. It appears to be related to a memory leak with lmstudio [bug](https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/1209). The server is holding onto data. I've created the `--missing` parameter so I can restart a job without overwriting the data that exists.
    """)
    return


@app.cell
def _(Args, Path):
    args2 = Args(
        image_dir=Path("./data/herbarium/sheets_001"),
        missing=True,  # Process only missing records
        notes="""
            The job keeps crashing on me due to an lmstudio bug.
            Capture remaining sheets from ocr_run_id 1.
            """,
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
        model_name="google/gemma-3-27b",  # New model
        retry=True,  # Only try sheets that always errored before
        notes="""
            Try a difference model on sheets that errored before on runs 1, 2, & 3.
            """,
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
        notes="""A new group of sheet images.""",
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
        model_name="google/gemma-3-27b",  # New model
        retry=True,  # Retry errored records with different parameters
        context_length=8192,  # Doubled the context
        notes="""Retry errored sheets in ocr_run_id 5 with a new model and params.""",
    )
    # ocr_images(args5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is a larger set (~1500) of images that contain UTM and TRS notations.
    """)
    return


@app.cell
def _(Args, Path):
    args6 = Args(
        image_dir=Path("./data/herbarium/utm_trs_test"),
        notes="""A set of herbarium sheets that contain TRS & UTM notations.""",
    )
    # ocr_images(args6)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    _Mea culpa_. I forgot to prevent my computer from sleeping, so the job died part of the way thru. Restarting.
    """)
    return


@app.cell
def _(Args, Path):
    args7 = Args(
        image_dir=Path("./data/herbarium/utm_trs_test"),
        notes="""A set of herbarium sheets that contain TRS & UTM notations. continued""",
        missing=True,  # Process only missing records
    )
    # ocr_images(args7)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Process the errors for the TRS & UTM dataset.
    """)
    return


@app.cell
def _(Args, Path):
    args8 = Args(
        image_dir=Path("./data/herbarium/utm_trs_test"),
        model_name="google/gemma-3-27b",  # New model
        retry=True,  # Retry errored records with different parameters
        context_length=8192,  # Doubled the context
        notes="""Retry errored sheets in ocr_run_id 5 with a new model and params.""",
    )
    # ocr_images(args8)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    No errors remain.
    """)
    return


@app.cell
def _(db_path, get_all_errors):
    len(get_all_errors(db_path))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Examine the results.
    """)
    return


@app.cell
def _(db_path, get_all_records, mo):
    image_idx = mo.ui.slider(
        1,
        len(get_all_records(db_path)),
        full_width=True,
        debounce=True,
        show_value=True,
    )
    image_idx
    return (image_idx,)


@app.cell
def _(db_path, duckdb, image_idx, mo):
    with duckdb.connect(db_path) as view_cxn:
        image_rec = view_cxn.execute(
            "select * from ocr where ocr_id = ?",
            [image_idx.value],
        ).df()

    print(image_rec.at[0, "ocr_text"])
    mo.image(src=image_rec.at[0, "image_path"])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
