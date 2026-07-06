import textwrap
from typing import TYPE_CHECKING, Any, Literal

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path


MODE = Literal["a", "w"]


def read_list_of_dicts(
    path: Path, *, fill_na: Any = None, limit: int | None = None
) -> list[dict[str, str]]:
    df = read_to_df(path)
    if fill_na is not None:
        df = df.fillna(fill_na)
    data = df.to_dict("records")
    data = data[:limit]
    return data


def read_to_df(path: Path, *, limit: int | None = None) -> pd.DataFrame:
    df = None
    match path.suffix:
        case ".csv":
            df = pd.read_csv(path, dtype=str).fillna("")
        case ".tsv":
            df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
        case ".json":
            df = pd.read_json(path).fillna("")
        case ".jsonl":
            df = pd.read_json(path, lines=True).fillna("")
        case ".html":
            dfs = pd.read_html(path)
            if not dfs:
                raise ValueError(f"Could not find a table in {path}")
            df = dfs[0].fillna("")
        case _:
            raise ValueError(f"Unrecognized file extension: {path.suffix}")
    if limit:
        df = df.head(limit)
    return df


def output_list_of_dicts(
    path: Path, data: list[dict[str, Any]], mode: MODE = "w"
) -> None:
    df = pd.DataFrame(data).fillna("")

    match path.suffix:
        case ".csv" | ".tsv":
            sep = "\t" if path.suffix == ".tsv" else ","
            df.to_csv(path, sep=sep, index=False, mode=mode)
        case ".json" | ".jsonl":
            indent, lines = (4, False) if path.suffix == ".json" else (None, True)
            df.to_json(path, indent=indent, lines=lines, index=False, mode=mode)
        case ".html":
            html = html_template(df)
            with path.open(mode) as out:
                out.write(html)
        case _:
            raise ValueError(f"Unrecognized file extension: {path.suffix}")


def html_template(df: pd.DataFrame) -> str:
    swap = ["text", "source"]
    cols = swap + [c for c in df.columns if c not in swap]
    df = df.reindex(cols, axis=1)
    html = df.to_html(
        index=False,
        border=1,
        float_format=lambda x: f"{x:0.2f}",
        escape=False,
        formatters={
            "source": lambda x: '<span class="source">' + x + "</span>",
            "text": lambda x: '<span class="text">' + x + "</span>",
        },
    )
    return textwrap.dedent(f"""\
        <html>
        <head>
            <style>
            table {{
                width: 60%;
                border-collapse: collapse;
                margin: 20px auto;
            }}
            th {{
                position: sticky;
                top: 0;
                background: lightgray;
                z-index: 1;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: center;
                z-index: 1;
            }}
            td:has(> span.text) {{
                min-width: 400px;
                background: #ececec;
            }}
            td:has(> span.source) {{
                overflow-wrap: break-word;
                max-width: 256px;
            }}
            th:first-child,
            td:first-child {{
                position: sticky;
                left: 0;
            }}
            th:first-child {{
                z-index: 3;
            }}
            .text {{
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            </style>
        </head>
        <body>
        <div>
            {html}
        </div>
        </body>
        </html>
        """)
