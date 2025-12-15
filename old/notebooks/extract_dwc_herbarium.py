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
    3. I do a final formatting pass on the data from step 2.

    This notebook is about step 2, capturing text into structured fields.
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
    from shutil import copyfile

    import dspy
    import duckdb

    from llama.data_formats import specimen_types
    return Path, dataclass, datetime, dspy, duckdb, specimen_types


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
def _(Path):
    specimen_type = "herbarium"

    db_path = Path("data/herbarium/labelllama_herbarium.duckdb")

    # db_backup = Path("data/herbarium/labelllama_herbarium_2025-12-11b.duckdb")

    # copyfile(src=db_backup, dst=db_path)
    return (db_path,)


@app.cell
def _(Path, duckdb, specimen_types):
    def create_dwc_tables(db_path: Path, specimen_type: str) -> None:
        # Fields specific to the specimen type
        spec_type = specimen_types.SPECIMEN_TYPES[specimen_type]
        fields = [f"{f} char[]," for f in spec_type.output_fields]
        fields = "\n".join(fields)

        sql = f"""
            create sequence if not exists dwc_run_seq;
            create table if not exists dwc_run (
                dwc_run_id integer primary key default nextval('dwc_run_seq'),
                prompt        char,
                model         char,
                api_host      char,
                notes         char,
                temperature   float,
                max_tokens    integer,
                specimen_type char,
                dwc_run_elapsed interval,
                dwc_run_started timestamptz default current_localtimestamp(),
            );

            create sequence if not exists dwc_id_seq;
            create table if not exists dwc (
                dwc_id integer primary key default nextval('dwc_id_seq'),
                dwc_run_id  integer references dwc_run(dwc_run_id),
                pre_dwc_id  integer references pre_dwc(pre_dwc_id),
                dwc_elapsed interval,
                {fields}
            );
            """

        with duckdb.connect(db_path) as cxn:
            cxn.execute(sql)
    return (create_dwc_tables,)


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
        db_path: Path = db_path  # Output dwc info to this database
        specimen_type: str = ""
        cache: bool = False  # Use cached records?
        # Model parameters
        model_name: str = "lm_studio/google/gemma-3-27b"
        api_host: str = "http://localhost:1234/v1"  # URL for the LM model
        api_key: str | None = None
        context_length: int = 4096  # Model's context length
        temperature: float = 0.1  # Model's temperature
        notes: str = ""  # Information about the OCR run
    return (Args,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Code dealing with information extraction
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The record selection query will definitely change a lot, so I'm pulling it out of the extract_dwc function where it will get buried.
    """)
    return


@app.cell
def _(Path, duckdb):
    def select_records(db_path: Path) -> list:
        sql = """select * from pre_dwc where pre_dwc_run_id in (1);"""

        with duckdb.connect(db_path) as cxn:
            return cxn.execute(sql).pl()
    return (select_records,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Extract the information.
    """)
    return


@app.cell
def _(
    Args,
    create_dwc_tables,
    datetime,
    dspy,
    duckdb,
    mo,
    select_records,
    specimen_types,
):
    def extract_dwc(args: Args) -> None:
        create_dwc_tables(args.db_path, args.specimen_type)

        spec_type = specimen_types.SPECIMEN_TYPES[args.specimen_type]

        names = ", ".join(f"{f}" for f in spec_type.output_fields)
        vars_ = ", ".join(f"${f}" for f in spec_type.output_fields)
        insert_dwc = f"""
            insert into dwc
                (dwc_run_id, pre_dwc_id, dwc_elapsed, {names})
                values ($dwc_run_id, $pre_dwc_id, $dwc_elapsed, {vars_});
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

        with duckdb.connect(args.db_path) as cxn:
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

            pre_dwc_input = select_records(args.db_path)
            rows = pre_dwc_input.rows(named=True)

            for pre_dwc_rec in mo.status.progress_bar(rows, title="DwC Progress"):
                rec_began = datetime.now()

                prediction = predictor(text=pre_dwc_rec["pre_dwc_text"])

                cxn.execute(
                    insert_dwc,
                    {
                        "dwc_run_id": run_id,
                        "pre_dwc_id": pre_dwc_rec["pre_dwc_id"],
                        "dwc_elapsed": datetime.now() - rec_began,
                    }
                    | prediction.toDict(),
                )

            cxn.execute(
                "update dwc_run set dwc_run_elapsed = ? where dwc_run_id = ?;",
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
    This is a vanillia set of parameters using a 27b parameter model. I'm going to use these records to create a gold standard for scoring models.
    """)
    return


@app.cell
def _(Args):
    args1 = Args(
        specimen_type="herbarium",
        model_name="lm_studio/google/gemma-3-27b",
    )
    # extract_dwc(args1)
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Try a phi-4 model.
    """)
    return


@app.cell
def _(Args, extract_dwc):
    args3 = Args(
        specimen_type="herbarium",
        model_name="lm_studio/microsoft/phi-4",
    )
    extract_dwc(args3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Try a new granite model.
    """)
    return


@app.cell
def _(Args, extract_dwc):
    args4 = Args(
        specimen_type="herbarium",
        model_name="lm_studio/unsloth/granite-4.0-h-small-GGUF/granite-4.0-h-small-Q4_K_S.gguf",
    )
    extract_dwc(args4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Try a largish model 70b parameters.
    """)
    return


@app.cell
def _(Args, extract_dwc):
    args5 = Args(
        specimen_type="herbarium",
        model_name="lm_studio/meta/llama-3.3-70b",
    )
    extract_dwc(args5)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
