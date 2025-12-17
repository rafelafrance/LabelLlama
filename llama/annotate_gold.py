#!/usr/bin/env python3

import argparse
import json
import textwrap
import tkinter as tk
from pathlib import Path
from tkinter import Event, filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any

import flet as ft

from llama.signatures.all_signatures import SIGNATURES

FONT = ("liberation sans", 16)
FONT_I = ("liberation sans", 16, "italic bold")

STYLE_LIST = [
    {"background": "brown", "foreground": "white", "font": FONT},
    {"background": "olive", "foreground": "white", "font": FONT},
    {"background": "teal", "foreground": "white", "font": FONT},
    {"background": "navy", "foreground": "white", "font": FONT},
    {"background": "red", "foreground": "white", "font": FONT},
    {"background": "orange", "font": FONT},
    {"background": "yellow", "font": FONT},
    {"background": "lime", "font": FONT},
    {"background": "green", "foreground": "white", "font": FONT},
    {"background": "cyan", "font": FONT},
    {"background": "blue", "foreground": "white", "font": FONT},
    {"background": "purple", "foreground": "white", "font": FONT},
    {"background": "magenta", "foreground": "white", "font": FONT},
    {"background": "gray", "font": FONT},
    {"background": "lavender", "font": FONT},
    {"background": "brown", "foreground": "yellow", "font": FONT_I},
    {"background": "olive", "foreground": "yellow", "font": FONT_I},
    {"background": "teal", "foreground": "yellow", "font": FONT_I},
    {"background": "navy", "foreground": "yellow", "font": FONT_I},
    {"background": "red", "foreground": "yellow", "font": FONT_I},
    {"background": "orange", "foreground": "navy", "font": FONT_I},
    {"background": "yellow", "foreground": "navy", "font": FONT_I},
    {"background": "lime", "foreground": "navy", "font": FONT_I},
    {"background": "green", "foreground": "yellow", "font": FONT_I},
    {"background": "cyan", "foreground": "navy", "font": FONT_I},
    {"background": "blue", "foreground": "yellow", "font": FONT_I},
    {"background": "purple", "foreground": "yellow", "font": FONT_I},
    {"background": "magenta", "foreground": "yellow", "font": FONT_I},
    {"background": "gray", "foreground": "navy", "font": FONT_I},
    {"background": "lavender", "foreground": "navy", "font": FONT_I},
]


def main(page: ft.Page) -> None:
    text = ft.Text(value="Hi there!", color="green")
    page.controls.append(text)
    page.update()


class App(tk.Tk):
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__()

        self.signature = SIGNATURES[args.specimen_type]
        sig = self.signature.model_fields
        self.fields = [
            k
            for k, v in sig.items()
            if v.json_schema_extra["__dspy_field_type"] == "output"
        ]

        self.rows: tuple[int] = tuple(range(8 + len(self.fields)))
        self.row_span: int = len(self.rows) + 1

        self.curr_dir = "."
        self.ocr_jsonl: Path = Path()
        self.labels = []
        self.dirty = False

        self.title("Annotate fields on OCRed label text")

        self.grid_rowconfigure(self.rows, weight=0)
        self.grid_rowconfigure(self.row_span, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.text_frame = ttk.Frame(master=self)
        self.text_frame.grid(row=0, column=0, rowspan=self.row_span + 1, sticky="nsew")

        self.control_frame = ttk.Frame(self, relief="sunken", borderwidth=2)
        self.control_frame.grid(
            row=0, column=1, rowspan=self.row_span + 1, sticky="nsew"
        )

        self.text = ScrolledText(self.text_frame, font=FONT)
        self.text.pack(fill="both", expand=True)
        self.text.insert(tk.INSERT, "")
        self.text.bind("<ButtonRelease-1>", self.on_add_annotation)  # left-click
        self.text.bind("<ButtonRelease-3>", self.on_delete_annotation)  # right-click
        for field, opts in zip(self.fields, STYLE_LIST, strict=False):
            self.text.tag_config(field, **opts)
            self.text.tag_bind(field, "<Enter>", self.show_tooltip)
            self.text.tag_bind(field, "<Leave>", self.hide_tooltip)

        self.tooltip = tk.Label(self, text="")

        self.load_button = tk.Button(
            self.control_frame,
            text="Load annotations",
            command=self.load,
            font=FONT,
        )
        self.load_button.grid(row=1, column=1, padx=16, pady=16)

        self.save_button = tk.Button(
            self.control_frame,
            text="Save annotations",
            command=self.save,
            font=FONT,
        )
        self.save_button.grid(row=2, column=1, padx=16, pady=16)

        self.annotation_label = tk.Label(
            self.control_frame,
            text="Annotation type",
            font=FONT,
        )
        self.annotation_label.grid(row=7, column=1, padx=16, pady=16)

        self.annotation_value = tk.StringVar()
        self.annotation_value.set(self.fields[0])

        style = ttk.Style(self)
        for i, (field, opts) in enumerate(
            zip(self.fields, STYLE_LIST, strict=False), 8
        ):
            name = f"{field}.TRadiobutton"
            style.configure(name, **opts)
            radio = ttk.Radiobutton(
                self.control_frame,
                text=field,
                value=field,
                variable=self.annotation_value,
                style=name,
            )
            radio.grid(sticky="w", row=i, column=1, padx=32, pady=8)

        self.protocol("WM_DELETE_WINDOW", self.safe_quit)
        self.focus()
        self.unbind_all("<<NextWindow>>")

    def show_tooltip(self, event: Event) -> None:
        self.hide_tooltip(event)
        names = self.text.tag_names(tk.CURRENT)
        name = next((lb for lb in names if lb not in ("header", "sel")), "")
        self.tooltip = tk.Label(self, text=name)
        self.tooltip.place(x=event.x, y=event.y)

    def hide_tooltip(self, _event: Event) -> None:
        self.tooltip.place_forget()

    def on_add_annotation(self, _event: Event) -> None:
        if not (select := self.text.tag_ranges("sel")):
            return

        beg = self.text.index(tk.SEL_FIRST)

        # Strip leading and trailing whitespace from annotations
        selected = self.text.get(*select)
        trimmed = selected.lstrip()
        beg = self.text.index(beg + f" + {len(selected) - len(trimmed)} chars")
        end = self.text.index(beg + f" + {len(trimmed.rstrip())} chars")

        # No empty annotations
        if self.text.compare(beg, "==", end):
            return

        # No annotations in the header
        idx = self.text.index(beg)
        while self.text.compare(idx, "<", end):
            if "header" in self.text.tag_names(idx):
                return
            idx = self.text.index(idx + " + 1 char")

        self.dirty = True
        self.text.tag_add(self.annotation_value.get(), beg, end)

    def on_delete_annotation(self, _event: Event) -> None:
        # Is the cursor on a valid tag?
        names = self.text.tag_names(tk.CURRENT)
        name = next((lb for lb in names if lb not in ("header", "sel")), "")
        if not name:
            return

        self.dirty = True

        # Remove the tag from current index to the start of the tag's span
        idx = self.text.index(tk.CURRENT)
        while name in self.text.tag_names(idx):
            self.text.tag_remove(name, idx)
            idx = self.text.index(idx + " - 1 char")

        # Remove tag from after the current index to the end of the tag's span
        idx = self.text.index(tk.CURRENT + " + 1 char")
        while name in self.text.tag_names(idx):
            self.text.tag_remove(name, idx)
            idx = self.text.index(idx + " + 1 char")

    def add_header_tags(self) -> None:
        for lb in self.labels:
            beg, end = lb["header-location"]
            self.text.tag_add("header", beg, end)

    def build_text(self, label: dict[str, Any]) -> None:
        beg = self.text.index(tk.CURRENT)
        self.text.insert(tk.INSERT, label["pre_dwc_text"])
        end = self.text.index(tk.CURRENT)
        label["text-location"] = [beg, end]
        self.text.insert(tk.INSERT, "\n")

    def build_header(self, i: int, label: dict[str, Any]) -> None:
        beg = self.text.index(tk.CURRENT)
        self.text.insert(tk.INSERT, "=" * 72)
        self.text.insert(tk.INSERT, "\n")
        self.text.insert(tk.INSERT, f"{i} {label['image_path']}")
        self.text.insert(tk.INSERT, "\n")
        self.text.insert(tk.INSERT, "=" * 72)
        self.text.insert(tk.INSERT, "\n")
        end = self.text.index(tk.CURRENT)
        label["header-location"] = [beg, end]

    def load(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=self.curr_dir,
            title="Load annotations",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )
        if not path:
            return

        self.title(f"Editing: {path}")

        path = Path(path)
        self.curr_dir = path.parent
        self.dirty = False

        with path.open() as f:
            annotations = json.load(f)

        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.labels = []

        for i, result in enumerate(annotations, 1):
            label = result | {
                "header-location": [],
                "text-location": [],
            }

            self.build_header(i, label)
            self.build_text(label)

            for field in self.fields:
                val = result[field]
                if isinstance(val, list) and val:
                    for v in val:
                        self.add_tag(field, v, label)
                elif isinstance(val, list):
                    label[field] = []
                elif val:
                    self.add_tag(field, val, label)
                else:
                    label[field] = []

            self.labels.append(label)

        self.text.configure(state="disabled")

        self.add_header_tags()

    def add_tag(self, field: str, val: Any, label: dict[str, Any]) -> None:
        search_beg, text_end = label["text-location"]
        # Need to handle annotations with identical content
        while tag_beg := self.text.search(val, search_beg, text_end):
            search_beg = self.text.index(tag_beg + f" + {len(val)} chars")

            # Is the text already tagged?
            names = set(self.text.tag_names(tag_beg))
            names -= {"header", "sel"}
            if names:
                continue

            # Is there a word break. \b does not work
            tag_end = self.text.index(tag_beg + f" + {len(val)} chars")
            before_idx = self.text.index(tag_beg + " - 1 char")

            before = self.text.get(before_idx)
            after = self.text.get(tag_end)

            if before.isalpha() or after.isalpha():
                continue

            # All checks passed
            self.text.tag_add(field, tag_beg, tag_end)

    def save(self) -> None:
        path = tk.filedialog.asksaveasfilename(
            initialdir=self.curr_dir,
            title="Save annotations",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )

        if not path:
            return

        # Remove old field data
        for lb in self.labels:
            for field in self.fields:
                lb[field] = []

        # Replace field data
        for field in self.fields:
            indexes = self.text.tag_ranges(field)
            indexes = zip(indexes[0::2], indexes[1::2], strict=True)
            labels = (lb for lb in self.labels)
            lb = next(labels)
            for beg, end in indexes:
                while self.text.compare(beg, ">", lb["text-location"][1]):
                    lb = next(labels)
                value = self.text.get(beg, end)
                if value not in lb[field]:
                    lb[field].append(value)

        path = Path(path)
        self.curr_dir = path.parent
        self.dirty = False

        annotations = []
        for lb in self.labels:
            anno = {k: v for k, v in lb.items() if k not in self.fields}
            anno |= {f: lb.get(f, []) for f in self.fields}
            annotations.append(anno)

        with path.open("w") as f:
            json.dump(annotations, f, indent=4)

    def safe_quit(self) -> None:
        if self.dirty:
            yes = messagebox.askyesno(
                self.title(),
                "Are you sure you want to exit without saving?",
            )
            if not yes:
                return
        self.destroy()


def tkinter_main() -> None:
    args = parse_args()
    app = App(args)
    app.mainloop()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            "Annotate fields in label text manually to create training data."
        ),
    )

    sigs = list(SIGNATURES.keys())
    arg_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    # ARGS = parse_args()
    # main(ARGS)
    ft.app(main)
