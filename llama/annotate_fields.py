#!/usr/bin/env python3

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from typing import ClassVar

import customtkinter as ctk
from pylib import const

STYLE_LIST = [
    {"background": "red"},
    {"background": "blue"},
    {"background": "green"},
    {"background": "black"},
    {"background": "purple"},
    {"background": "orange"},
    {"background": "cyan"},
    {"background": "olive"},
    {"background": "pink"},
    {"background": "gray"},
]

COLOR_LIST = [v["background"] for v in STYLE_LIST]


class App(ctk.CTk):
    row_span: ClassVar[int] = 10

    def __init__(self):
        super().__init__()

        self.curr_dir = "."
        self.ocr_jsonl: Path = Path()
        self.annotations = []
        self.dirty = False

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Annotate fields on OCRed label text")

        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=0)
        self.grid_rowconfigure(9, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.text_frame = ctk.CTkFrame(master=self)
        self.text_frame.grid(row=0, column=0, rowspan=self.row_span, sticky="nsew")

        self.text = ScrolledText(self.text_frame, font=const.FONT_SM)
        self.text.pack(fill="both", expand=True)
        self.text.insert(tk.INSERT, "")
        self.text.bind("<ButtonRelease-1>", self.on_add_release)  # left-click = add
        self.text.bind("<ButtonRelease-3>", self.on_delete_release)  # right-click = del
        self.tags = self.built_tags()

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
        self.annotation.set(COLOR_LIST[0])
        self.annotation_combo = ctk.CTkComboBox(
            master=self,
            values=COLOR_LIST,
            variable=self.annotation,
            font=const.FONT,
            dropdown_font=const.FONT,
        )
        self.annotation_label.grid(row=7, column=1, padx=16, pady=1)
        self.annotation_combo.grid(row=8, column=1, padx=16, pady=1)

        self.protocol("WM_DELETE_WINDOW", self.safe_quit)
        self.focus()
        self.unbind_all("<<NextWindow>>")

    def built_tags(self):
        self.text.tag_config("scientificName", background="red")
        return {"scientificName": {"background": "red"}}

    def on_add_release(self, _event):
        if not (select := self.text.tag_ranges("sel")):
            return

        beg = self.text.index(tk.SEL_FIRST)
        end = self.text.index(tk.SEL_LAST)

        # Strip whitespace from tags
        selected = self.text.get(*select)
        trimmed = selected.lstrip()
        beg = self.text.index(beg + f" + {len(selected) - len(trimmed)} chars")
        end = self.text.index(beg + f" + {len(trimmed.rstrip())} chars")

        # No empty tags
        if self.text.compare(beg, "==", end):
            return

        # No tags in the header
        if self.text.tag_nextrange("header", beg, end):
            return

        self.text.tag_add("scientificName", beg, end)

    def on_delete_release(self, _event):
        # Remove tags with a right click
        tag = self.text.tag_prevrange("scientificName", tk.CURRENT)
        if not tag:
            return
        if self.text.compare(tag[0], "<=", tk.CURRENT) and self.text.compare(
            tk.CURRENT, "<=", tag[1]
        ):
            self.text.tag_remove("scientificName", *tag)

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

        tags = []
        for lb in ocr:
            self.annotations.append(
                {
                    "Source-File": lb["Source-File"],
                    "text": lb["text"],
                    "annotations": [],
                }
            )
            src = Path(lb["Source-File"])

            self.text.configure(state="normal")
            tags.append(self.text.index(tk.CURRENT))
            self.text.insert(tk.INSERT, "=" * 72)
            self.text.insert(tk.INSERT, "\n")
            self.text.insert(tk.INSERT, f"{src.name}")
            self.text.insert(tk.INSERT, "\n")
            self.text.insert(tk.INSERT, "=" * 72)
            self.text.insert(tk.INSERT, "\n")
            tags.append(self.text.index(tk.CURRENT))
            self.text.insert(tk.INSERT, lb["text"])
            self.text.insert(tk.INSERT, "\n")

        self.text.configure(state="disabled")

        # Can't add these tags in the loop
        for tag in tags:
            self.text.tag_add("header", tag)

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
            self.annotations = json.load(f)

    def save(self):
        if not self.annotations:
            return

        path = tk.filedialog.asksaveasfilename(
            initialdir=self.curr_dir,
            title="Save annotations",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )

        if not path:
            return

        path = Path(path)
        self.curr_dir = path.parent
        self.dirty = False

        with path.open("w") as f:
            json.dump(self.annotations, f, indent=4)

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
