#!/usr/bin/env python3

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import get_type_hints

import customtkinter as ctk
from pylib import const, darwin_core, info_extractor

IE_TYPES = {
    darwin_core.DWC[k]: v
    for k, v in get_type_hints(info_extractor.InfoExtractor).items()
    if k in info_extractor.OUTPUT_FIELDS
}

STYLE_LIST = [
    {"background": "red", "foreground": "white", "font": const.FONT_SM},
    {"background": "blue", "foreground": "white", "font": const.FONT_SM},
    {"background": "green", "foreground": "white", "font": const.FONT_SM},
    {"background": "black", "foreground": "white", "font": const.FONT_SM},
    {"background": "purple", "foreground": "white", "font": const.FONT_SM},
    {"background": "gray", "foreground": "white", "font": const.FONT_SM},
    {"background": "orange", "font": const.FONT_SM},
    {"background": "cyan", "font": const.FONT_SM},
    {"background": "pink", "font": const.FONT_SM},
    {"background": "red", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "blue", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "green", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "black", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "purple", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "olive", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "orange", "font": const.FONT_SM2},
    {"background": "cyan", "font": const.FONT_SM2},
    {"background": "pink", "font": const.FONT_SM2},
]

DWC = list(darwin_core.DWC.values())


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.curr_dir = "."
        self.ocr_jsonl: Path = Path()
        self.labels = []
        self.dirty = False

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Annotate fields on OCRed label text")

        rows = tuple(range(8 + len(DWC)))

        self.grid_rowconfigure(rows, weight=0)
        self.grid_rowconfigure(len(rows), weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=280)

        self.text_frame = ctk.CTkFrame(master=self)
        self.text_frame.grid(row=0, column=0, rowspan=len(rows) + 1, sticky="nsew")

        self.text = ScrolledText(self.text_frame, font=const.FONT_SM)
        self.text.pack(fill="both", expand=True)
        self.text.insert(tk.INSERT, "")
        self.text.bind("<ButtonRelease-1>", self.on_add_annotation)  # left-click
        self.text.bind("<ButtonRelease-3>", self.on_delete_annotation)  # right-click
        for dwc, opts in zip(DWC, STYLE_LIST, strict=False):
            self.text.tag_config(dwc, **opts)
            self.text.tag_bind(dwc, "<Enter>", self.show_tooltip)
            self.text.tag_bind(dwc, "<Leave>", self.hide_tooltip)

        self.tooltip = tk.Label(self, text="")

        self.jsonl_button = ctk.CTkButton(
            master=self,
            text="Import text",
            command=self.import_,
            font=const.FONT,
        )
        self.jsonl_button.grid(row=0, column=1, padx=16, pady=16)

        self.load_button = ctk.CTkButton(
            master=self,
            text="Load annotations",
            command=self.load,
            font=const.FONT,
        )
        self.load_button.grid(row=1, column=1, padx=16, pady=16)

        self.save_button = ctk.CTkButton(
            master=self,
            text="Save annotations",
            command=self.save,
            font=const.FONT,
        )
        self.save_button.grid(row=2, column=1, padx=16, pady=16)

        self.annotation_label = ctk.CTkLabel(
            master=self,
            text="Annotation type",
            width=200,
            font=const.FONT,
        )
        self.annotation_label.grid(row=7, column=1, padx=16, pady=16)

        self.annotation_value = tk.StringVar()
        self.annotation_value.set(DWC[0])

        style = ttk.Style(self)
        for i, (dwc, opts) in enumerate(zip(DWC, STYLE_LIST, strict=False), 8):
            name = f"{dwc}.TRadiobutton"
            style.configure(name, **opts)
            radio = ttk.Radiobutton(
                self, text=dwc, value=dwc, variable=self.annotation_value, style=name
            )
            radio.grid(sticky="w", row=i, column=1, padx=32, pady=8)

        self.protocol("WM_DELETE_WINDOW", self.safe_quit)
        self.focus()
        self.unbind_all("<<NextWindow>>")

    def show_tooltip(self, event):
        self.hide_tooltip(event)
        names = self.text.tag_names(tk.CURRENT)
        name = next((lb for lb in names if lb not in ("header", "sel")), "")
        self.tooltip = tk.Label(self, text=name)
        self.tooltip.place(x=event.x, y=event.y)

    def hide_tooltip(self, _event):
        self.tooltip.place_forget()

    def on_add_annotation(self, _event):
        if not (select := self.text.tag_ranges("sel")):
            return

        beg = self.text.index(tk.SEL_FIRST)

        # Strip whitespace from annotations
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

    def on_delete_annotation(self, _event):
        names = self.text.tag_names(tk.CURRENT)
        name = next((lb for lb in names if lb not in ("header", "sel")), "")
        if not name:
            return
        if tag := self.text.tag_prevrange(name, tk.CURRENT):
            self.dirty = True
            self.text.tag_remove(name, *tag)

    def import_(self):
        path = filedialog.askopenfilename(
            initialdir=self.curr_dir,
            title="Import OCRed text from JSONL file",
            filetypes=(("jsonl", "*.jsonl"), ("all files", "*")),
        )
        if not path:
            return

        path = Path(path)
        with path.open() as f:
            ocr = [json.loads(ln) for ln in f]

        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.labels = []

        for results in ocr:
            label = {
                "Source-File": results["Source-File"],
                "text": results["text"],
                "header-location": [],
                "text-location": [],
                "annotations": {k: [] for k in DWC},
            }

            self.build_header(label)
            self.build_text(label)
            self.labels.append(label)

        self.text.configure(state="disabled")

        self.add_header_tags()

    def add_header_tags(self):
        for lb in self.labels:
            beg, end = lb["header-location"]
            self.text.tag_add("header", beg, end)

    def build_text(self, label):
        beg = self.text.index(tk.CURRENT)
        self.text.insert(tk.INSERT, label["text"])
        end = self.text.index(tk.CURRENT)
        label["text-location"] = [beg, end]
        self.text.insert(tk.INSERT, "\n")

    def build_header(self, label):
        beg = self.text.index(tk.CURRENT)
        self.text.insert(tk.INSERT, "=" * 72)
        self.text.insert(tk.INSERT, "\n")
        self.text.insert(tk.INSERT, str(label["Source-File"]))
        self.text.insert(tk.INSERT, "\n")
        self.text.insert(tk.INSERT, "=" * 72)
        self.text.insert(tk.INSERT, "\n")
        end = self.text.index(tk.CURRENT)
        label["header-location"] = [beg, end]

    def load(self):
        path = filedialog.askopenfilename(
            initialdir=self.curr_dir,
            title="Load annotations",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )
        if not path:
            return

        path = Path(path)
        self.curr_dir = path.parent
        self.dirty = False

        with path.open() as f:
            annotations = json.load(f)

        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.labels = []

        for result in annotations:
            label = {
                "Source-File": result["Source-File"],
                "text": result["text"],
                "header-location": [],
                "text-location": [],
                "annotations": {k: [] for k in DWC},
            }

            self.build_header(label)
            self.build_text(label)

            for dwc, val in result.items():
                if dwc in ("Source-File", "text"):
                    continue
                if isinstance(val, list) and val:
                    for v in val:
                        self.load_tag(dwc, v, label)
                elif isinstance(val, list):
                    label["annotations"][dwc] = []
                elif val:
                    self.load_tag(dwc, val, label)
                else:
                    label["annotations"][dwc] = []

            self.labels.append(label)

        self.text.configure(state="disabled")

        self.add_header_tags()

    def load_tag(self, dwc, val, label):
        search_beg, text_end = label["text-location"]
        # Need to handle annotations with identical content
        while tag_beg := self.text.search(val, search_beg, text_end):
            names = set(self.text.tag_names(tag_beg))
            names -= {"header", "sel"}
            if not names:
                break
            search_beg = self.text.index(tag_beg + f" + {len(val)} chars")
        else:
            return
        tag_end = self.text.index(tag_beg + f" + {len(val)} chars")
        self.text.tag_add(dwc, tag_beg, tag_end)

    def save(self):
        path = tk.filedialog.asksaveasfilename(
            initialdir=self.curr_dir,
            title="Save annotations",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )

        if not path:
            return

        for dwc in DWC:
            indexes = self.text.tag_ranges(dwc)
            indexes = zip(indexes[0::2], indexes[1::2], strict=True)
            labels = (lb for lb in self.labels)
            lb = next(labels)
            for beg, end in indexes:
                while self.text.compare(beg, ">", lb["text-location"][1]):
                    lb = next(labels)
                value = self.text.get(beg, end)
                lb["annotations"][dwc].append(value)

        path = Path(path)
        self.curr_dir = path.parent
        self.dirty = False

        annotations = []
        for lb in self.labels:
            anno = {"Source-File": lb["Source-File"], "text": lb["text"]}
            for dwc in DWC:
                if not (field := lb["annotations"].get(dwc)):
                    continue
                anno[dwc] = field[0] if IE_TYPES[dwc] is str else field

            annotations.append(anno)

        with path.open("w") as f:
            json.dump(annotations, f, indent=4)

    def safe_quit(self):
        if self.dirty:
            yes = messagebox.askyesno(
                self.title(),
                "Are you sure you want to exit without saving?",
            )
            if not yes:
                return
        self.destroy()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
