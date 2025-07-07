#!/usr/bin/env python3

import json
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from typing import ClassVar, get_type_hints

import customtkinter as ctk
from pylib import const, darwin_core, info_extractor

IE_TYPES = {
    darwin_core.DWC[k]: v
    for k, v in get_type_hints(info_extractor.InfoExtractor).items()
    if k in info_extractor.OUTPUT_FIELDS
}

STYLE_LIST = [
    {"background": "red", "foreground": "white"},
    {"background": "blue", "foreground": "white"},
    {"background": "green", "foreground": "white"},
    {"background": "black", "foreground": "white"},
    {"background": "purple", "foreground": "white"},
    {"background": "olive", "foreground": "white"},
    {"background": "gray", "foreground": "white"},
    {"background": "orange"},
    {"background": "cyan"},
    {"background": "pink"},
    {"background": "red", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "blue", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "green", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "black", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "purple", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "olive", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "gray", "foreground": "yellow", "font": const.FONT_SM2},
    {"background": "orange", "font": const.FONT_SM2},
    {"background": "cyan", "font": const.FONT_SM2},
    {"background": "pink", "font": const.FONT_SM2},
]

DWC = list(darwin_core.DWC.values())


class App(ctk.CTk):
    row_span: ClassVar[int] = 10

    def __init__(self):
        super().__init__()

        self.curr_dir = "."
        self.ocr_jsonl: Path = Path()
        self.labels = []
        self.dirty = False

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Annotate fields on OCRed label text")

        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=0)
        self.grid_rowconfigure(9, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=280)

        self.text_frame = ctk.CTkFrame(master=self)
        self.text_frame.grid(row=0, column=0, rowspan=self.row_span, sticky="nsew")

        self.text = ScrolledText(self.text_frame, font=const.FONT_SM)
        self.text.pack(fill="both", expand=True)
        self.text.insert(tk.INSERT, "")
        self.text.bind("<ButtonRelease-1>", self.on_add_annotation)  # left-click
        self.text.bind("<ButtonRelease-3>", self.on_delete_annotation)  # right-click
        self.tooltip = tk.Label(self, text="")
        for dwc, opts in zip(DWC, STYLE_LIST, strict=False):
            self.text.tag_config(dwc, **opts)
            self.text.tag_bind(dwc, "<Enter>", self.show_tooltip)
            self.text.tag_bind(dwc, "<Leave>", self.hide_tooltip)

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
        self.annotation = tk.StringVar()
        self.annotation.set(DWC[0])
        self.annotation_combo = ctk.CTkComboBox(
            master=self,
            values=DWC,
            variable=self.annotation,
            font=const.FONT,
            dropdown_font=const.FONT,
            width=260,
        )
        self.annotation_label.grid(row=7, column=1, padx=16, pady=1)
        self.annotation_combo.grid(row=8, column=1, padx=16, pady=1)

        self.protocol("WM_DELETE_WINDOW", self.safe_quit)
        self.focus()
        self.unbind_all("<<NextWindow>>")

    def show_tooltip(self, event):
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

        self.text.tag_add(self.annotation_combo.get(), beg, end)

    def on_delete_annotation(self, _event):
        names = self.text.tag_names(tk.CURRENT)
        name = next((lb for lb in names if lb not in ("header", "sel")), "")
        if not name:
            return
        if tag := self.text.tag_prevrange(name, tk.CURRENT):
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

        for results in ocr:
            label = {
                "Source-File": results["Source-File"],
                "text": results["text"],
                "header-location": [],
                "text-location": [],
                "annotations": defaultdict(list),
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

        for result in annotations:
            label = {
                "Source-File": result["Source-File"],
                "text": result["text"],
                "header-location": [],
                "text-location": [],
                "annotations": {},
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
        text_beg, text_end = label["text-location"]
        tag_beg = self.text.search(val, text_beg, text_end)
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
                print(f"{lb['Source-File']}")
                print(f"{beg=} {end=} {value=}\n")

        path = Path(path)
        self.curr_dir = path.parent
        self.dirty = False

        annotations = []
        for lb in self.labels:
            anno = {"Source-File": lb["Source-File"], "text": lb["text"]}
            for dwc in DWC:
                print(IE_TYPES[dwc], type(IE_TYPES[dwc]))
                if IE_TYPES[dwc] is str:
                    anno[dwc] = lb["annotations"].get(dwc, [""])[0]
                else:
                    anno[dwc] = lb["annotations"].get(dwc, [])

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
