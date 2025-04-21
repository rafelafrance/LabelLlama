#!/usr/bin/env python3

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import ClassVar

import customtkinter as ctk
from pylib import const
from pylib.sheet_box import CONTENTS, Box
from pylib.sheet_page import Page
from pylib.spin_box import Spinner

COLOR_LIST = """ red blue green black purple orange cyan olive pink gray """.split()
COLOR = dict(zip(CONTENTS, COLOR_LIST, strict=False))


class App(ctk.CTk):
    row_span: ClassVar[int] = 10

    def __init__(self):
        super().__init__()

        self.curr_dir = "."
        self.image_dir = None
        self.canvas = None
        self.pages = []
        self.dirty = False
        self.dragging = False

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Outline labels on images of herbarium sheets")

        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=0)
        self.grid_rowconfigure(9, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.image_frame = ctk.CTkFrame(master=self)
        self.image_frame.grid(row=0, column=0, rowspan=self.row_span, sticky="nsew")

        self.image_button = ctk.CTkButton(
            master=self,
            text="Choose image directory",
            command=self.get_image_dir,
            font=const.FONT,
        )
        self.image_button.grid(row=0, column=1, padx=16, pady=16)

        self.load_button = ctk.CTkButton(
            master=self, text="Load", command=self.load, font=const.FONT
        )
        self.load_button.grid(row=1, column=1, padx=16, pady=16)

        self.save_button = ctk.CTkButton(
            master=self,
            text="Save",
            command=self.save,
            state="disabled",
            font=const.FONT,
        )
        self.save_button.grid(row=2, column=1, padx=16, pady=16)

        self.spinner = Spinner(master=self, command=self.change_page, width=140)
        self.spinner.grid(row=3, column=1, padx=16, pady=16)

        self.action = tk.StringVar()
        self.action.set("add")
        self.radio_add = ctk.CTkRadioButton(
            master=self,
            variable=self.action,
            text="add",
            value="add",
            font=const.FONT,
        )
        self.radio_del = ctk.CTkRadioButton(
            master=self,
            variable=self.action,
            text="delete",
            value="delete",
            font=const.FONT,
        )
        self.radio_content = ctk.CTkRadioButton(
            master=self,
            variable=self.action,
            text="change content type",
            value="content",
            font=const.FONT,
        )
        self.content_label = ctk.CTkLabel(
            master=self,
            text="Label content type",
            width=200,
            font=const.FONT,
        )
        self.content = tk.StringVar()
        self.content.set(CONTENTS[0])
        self.content_combo = ctk.CTkComboBox(
            master=self,
            values=CONTENTS,
            variable=self.content,
            font=const.FONT,
            dropdown_font=const.FONT,
        )
        self.radio_add.grid(row=4, column=1, padx=16, pady=16)
        self.radio_del.grid(row=5, column=1, padx=16, pady=16)
        self.radio_content.grid(row=6, column=1, padx=16, pady=16)
        self.content_label.grid(row=7, column=1, padx=16, pady=1)
        self.content_combo.grid(row=8, column=1, padx=16, pady=1)

        self.protocol("WM_DELETE_WINDOW", self.safe_quit)

    @property
    def index(self):
        return self.spinner.get() - 1

    @property
    def page(self):
        return self.pages[self.index]

    def change_page(self):
        if self.pages:
            self.display_page()

    def display_page(self):
        canvas_height = self.image_frame.winfo_height()
        self.page.resize(canvas_height)
        self.canvas.delete("all")
        self.canvas.create_image((0, 0), image=self.page.photo, anchor="nw")
        self.display_page_boxes()
        self.action.set("add")

    def display_page_boxes(self):
        self.clear_page_boxes()
        for box in self.page.boxes:
            self.canvas.create_rectangle(
                box.x0,
                box.y0,
                box.x1,
                box.y1,
                outline=COLOR[box.content],
                width=4,
            )

    def clear_page_boxes(self):
        for i, id_ in enumerate(self.canvas.find_all()):
            if i:  # First object is the page itself
                self.canvas.delete(id_)

    def on_canvas_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.pages and self.action.get() == "add":
            self.dirty = True
            content = self.content.get()
            color = COLOR[content]
            id_ = self.canvas.create_rectangle(0, 0, 1, 1, outline=color, width=4)
            self.page.boxes.append(Box(id=id_, x0=x, y0=y, x1=x, y1=y, content=content))
            self.dragging = True
        elif self.pages and self.action.get() == "delete":
            self.dirty = True
            self.page.filter_delete(x, y)
            self.display_page_boxes()
            self.action.set("add")
        elif self.pages and self.action.get() == "content":
            self.dirty = True
            box = self.page.find(x, y, "smallest")
            if box:
                box.content = self.content.get()
                self.display_page_boxes()

    def on_canvas_move(self, event):
        if self.dragging and self.pages and self.action.get() == "add":
            box = self.page.boxes[-1]
            box.x1 = self.canvas.canvasx(event.x)
            box.y1 = self.canvas.canvasy(event.y)
            self.canvas.coords(box.id, box.x0, box.y0, box.x1, box.y1)

    def on_canvas_release(self, _):
        if self.dragging and self.pages and self.action.get() == "add":
            self.page.filter_size()
            self.display_page_boxes()
            self.dragging = False

    def save(self):
        if not self.pages:
            return

        path = tk.filedialog.asksaveasfilename(
            initialdir=self.curr_dir,
            title="Save image boxes",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )

        if not path:
            return

        path = Path(path)
        self.curr_dir = path.parent
        self.dirty = False

        output = [p.as_dict() for p in self.pages]

        with path.open("w") as out_json:
            json.dump(output, out_json, indent=4)

    def load(self):
        path = filedialog.askopenfilename(
            initialdir=self.curr_dir,
            title="Load image boxes",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )
        if not path:
            return

        path = Path(path)
        self.curr_dir = path.parent

        if self.canvas is None:
            self.setup_canvas()
        canvas_height = self.image_frame.winfo_height()

        with path.open() as in_json:
            json_pages = json.load(in_json)

        self.dirty = False
        self.pages = []
        try:
            for page_data in json_pages:
                page = Page.load_json(page_data, canvas_height)
                self.pages.append(page)

            self.spinner_update(len(self.pages))
            self.save_button.configure(state="normal")
            self.display_page()

        except KeyError:
            messagebox.showerror(
                title="Load error",
                message="Could not load the JSON file",
            )
            self.pages = []
            self.save_button.configure(state="disabled")
            self.spinner_clear()
            self.canvas.delete("all")

    def setup_canvas(self):
        self.update()

        self.canvas = ctk.CTkCanvas(
            master=self.image_frame,
            width=self.image_frame.winfo_width(),
            height=self.image_frame.winfo_height(),
            background="black",
            cursor="cross",
        )
        self.canvas.grid(row=0, column=0, rowspan=self.row_span, sticky="nsew")

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def get_image_dir(self):
        image_dir = filedialog.askdirectory(
            initialdir=self.curr_dir,
            title="Choose image directory",
        )
        if not image_dir:
            return

        if self.canvas is None:
            self.setup_canvas()

        self.curr_dir = image_dir
        self.image_dir = Path(image_dir)
        self.dirty = False

        paths = [
            p
            for p in sorted(self.image_dir.glob("*"))
            if p.suffix.lower() in (".png", ".jpg", ".jpeg")
        ]

        if paths:
            paths = sorted(p.name for p in paths)
            self.spinner_update(len(paths))
            canvas_height = self.image_frame.winfo_height()
            self.pages = [Page(self.image_dir / p, canvas_height) for p in paths]
            self.save_button.configure(state="normal")
            self.display_page()
        else:
            self.pages = []
            self.save_button.configure(state="disabled")
            self.spinner_clear()
            self.canvas.delete("all")

    def spinner_update(self, high):
        self.spinner.low = 1
        self.spinner.high = high
        self.spinner.set(1)

    def spinner_clear(self):
        self.spinner.low = 0
        self.spinner.high = 0
        self.spinner.set(0)

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
