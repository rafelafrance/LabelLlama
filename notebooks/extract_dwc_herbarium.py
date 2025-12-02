import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Extract Darwin Core (DwC) fields from OCRed text

    I am currently using 2 models for extracting text from images of museum specimens.

    1. First I use an OCR model to get all of the text from labels etc. on the museum specimen image.
    2. Next I use another model that extracts Darwin Core fields from the text gotten in step 1.
    3. I do a final formatting pass on the data from step #2.

    This notebook is about step #2, capturing text into structured fields.
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from dataclasses import dataclass
    from datetime import datetime, timedelta
    from pathlib import Path
    from shutil import copyfile

    import dspy
    import duckdb
    import polars as pl

    from llama.data_formats import specimen_types
    return Path, copyfile, dataclass, datetime, dspy, duckdb, specimen_types


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
    ## Set up tables used to store extracted DwC information.

    I have learned from other projects that having dozens of CSV files is just horrible. I know they usually not planned and grow orgaincally, but I'm going for a database upfront. A DB also allows me to store metadata in the same location as the bulk of the data. And duckdb is nifty.

    This notebook is currently under development, so start each run from a known backup.
    """)
    return


@app.cell
def _(Path, copyfile):
    specimen_type = "herbarium"

    db_path = Path("data/herbarium/labelllama_herbarium.duckdb")

    db_backup = Path("data/herbarium/labelllama_herbarium_2025-11-30.duckdb")

    copyfile(src=db_backup, dst=db_path)
    return db_path, specimen_type


@app.cell
def _(Path, db_path, duckdb, specimen_type, specimen_types):
    def create_dwc_tables(db_path: Path, specimen_type: str) -> None:
        # Fields specific to the specimen type
        spec_type = specimen_types.SPECIMEN_TYPES[specimen_type]
        fields = [f"{f} char[]," for f in spec_type.output_fields.keys()]
        fields = "\n".join(fields)

        sql = f"""
            create sequence if not exists dwc_run_seq;
            create table if not exists dwc_run (
                dwc_run_id integer primary key default nextval('dwc_run_seq'),
                prompt         char,
                model          char,
                api_host       char,
                notes          char,
                temperature    float,
                max_tokens     integer,
                specimen_type  char,
                elapsed        interval,
                time_started   timestamptz default current_localtimestamp(),
            );

            create sequence if not exists dwc_id_seq;
            create table if not exists dwc (
                dwc_id integer primary key default nextval('dwc_id_seq'),
                dwc_run_id   integer references dwc_run(dwc_run_id),
                ocr_id       integer references ocr(ocr_id),
                {fields}
                elapsed      interval,
                time_started timestamptz default current_localtimestamp(),
            );
            """

        with duckdb.connect(db_path) as cxn:
            cxn.execute(sql)


    create_dwc_tables(db_path, specimen_type)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a data class for arguments. There are a lot of parameters for the information extraction process and it is convenient to put them into a single structure. This will also help with argparse setup when I migrate this code to a script.
    """)
    return


@app.cell
def _(Path, dataclass, db_path):
    @dataclass
    class Args:
        db: Path = db_path  # Output dwc info to this database
        specimen_type: str = ""
        cache: bool = False  # Use cached records?
        # Model parameters
        model_name: str = (
            "lm_studio/bartowski/google_gemma-3-27b-it-GGUF"
            "/google_gemma-3-27b-it-Q4_K_S.gguf"
        )
        api_host: str = "http://localhost:1234/v1"  # URL for the LM model
        api_key: str | None = None
        context_length: int = 4096  # Model's context length
        temperature: float = 0.1  # Model's temperature
        notes: str = ""  # Information about the OCR run
    return (Args,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Code dealing with record selection
    """)
    return


@app.cell
def _(Path, db_path, duckdb):
    def select_records(db_path: Path) -> list:
        sql = "select * from ocr where ocr_run_id in (6, 7) and ocr_text <> '';"

        with duckdb.connect(db_path) as cxn:
            return cxn.execute(sql).pl()


    ocr_input = select_records(db_path)
    return (ocr_input,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Extract the information.
    """)
    return


@app.cell
def _(Args, datetime, dspy, duckdb, mo, ocr_input, specimen_types):
    def extract_dwc(args: Args) -> None:
        spec_type = specimen_types.SPECIMEN_TYPES[args.specimen_type]
        names = ", ".join(f"{f}" for f in spec_type.output_fields.keys())
        vars = ", ".join(f"${f}" for f in spec_type.output_fields.keys())

        insert_dwc = f"""
            insert into dwc
                (dwc_run_id, ocr_id, elapsed, {names})
                values ($dwc_run_id, $ocr_id, $elapsed, {vars});
            """

        job_began = datetime.now()

        lm = dspy.LM(
            args.model_name,
            api_base=args.api_host,
            api_key=args.api_key,
            temperature=args.temperature,
            max_tokens=args.context_length,
            cache=args.cache,
        )
        dspy.configure(lm=lm)

        predictor = dspy.Predict(spec_type)

        adapter = dspy.ChatAdapter()
        prompt = adapter.format(
            predictor.signature,
            demos=predictor.demos,
            inputs={k: f"{{{k}}}" for k in predictor.signature.input_fields},
        )

        with duckdb.connect(args.db) as cxn:
            run_id = cxn.execute(
                """
                insert into dwc_run (
                    prompt, model, api_host, notes, temperature,
                    max_tokens, specimen_type
                )
                values (?, ?, ?, ?, ?, ?, ?)
                returning dwc_run_id;
                """,
                [
                    prompt,
                    args.model_name,
                    args.api_host,
                    args.notes.strip(),
                    args.temperature,
                    args.context_length,
                    args.specimen_type,
                ],
            ).fetchone()[0]

            rows = ocr_input.rows(named=True)
            for ocr_rec in mo.status.progress_bar(rows, title="DwC Progress"):
                rec_began = datetime.now()

                prediction = predictor(text=ocr_rec["ocr_text"])

                cxn.execute(
                    insert_dwc,
                    {
                        "dwc_run_id": run_id,
                        "ocr_id": ocr_rec["ocr_id"],
                        "elapsed": datetime.now() - rec_began,
                    }
                    | prediction.toDict(),
                )

            cxn.execute(
                "update dwc_run set elapsed = ? where dwc_run_id = ?;",
                [datetime.now() - job_began, run_id],
            )
    return (extract_dwc,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Darwin Core runs
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is a vanillia set of parameters using a 27b parameter model.
    """)
    return


@app.cell
def _(Args, extract_dwc):
    args1 = Args(
        specimen_type="herbarium",
        model_name="lm_studio/google/gemma-3-27b",
    )
    extract_dwc(args1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Try a smaller, 12b parameter model.
    """)
    return


@app.cell
def _(Args, extract_dwc):
    args2 = Args(
        specimen_type="herbarium",
        model_name="lm_studio/google/gemma-3-12b",
    )
    extract_dwc(args2)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
