import textwrap
from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path


def read_to_dict(
    path: Path, *, fill_na: Any = None, limit: int | None = None
) -> list[dict[str, Any]]:
    df = read_to_df(path)
    if fill_na is not None:
        df = df.fillna(fill_na)
    data = df.to_dict("records")
    data = data[:limit]
    return data


def read_to_df(path: Path) -> pd.DataFrame:
    df = None
    match path.suffix:
        case ".csv":
            df = pd.read_csv(path)
        case ".tsv":
            df = pd.read_csv(path, sep="\t")
        case ".json":
            df = pd.read_json(path)
        case ".jsonl":
            df = pd.read_json(path, lines=True)
        case _:
            raise ValueError(f"Unrecognized file extension: {path.suffix}")
    return df


def output_file(path: Path, data: list[dict[str, Any]]) -> None:
    df = pd.DataFrame(data).fillna("")

    match path.suffix:
        case ".csv" | ".tsv":
            sep = "\t" if path.suffix == ".tsv" else ","
            df.to_csv(path, sep=sep, index=False)
        case ".json" | ".jsonl":
            indent, lines = (4, False) if path.suffix == ".json" else (None, True)
            df.to_json(path, indent=indent, lines=lines, index=False)
        case ".html":
            html = html_template(df)
            with path.open("w") as out:
                out.write(html)
        case _:
            raise ValueError(f"Unrecognized file extension: {path.suffix}")


def html_template(df: pd.DataFrame) -> str:
    swap = ["text", "source"]
    cols = swap + [c for c in df.columns if c not in swap]
    df = df[cols]
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
