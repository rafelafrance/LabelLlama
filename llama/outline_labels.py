#!/usr/bin/env python3

import json
import tkinter as tk
from pathlib import Path
from tkinter import Event, filedialog, messagebox, ttk
from typing import ClassVar

from pylib import const
from pylib.label_box import CONTENTS, Box
from pylib.label_page import Page
from pylib.spin_box import Spinner

STYLE_LIST = [
    {"background": "red", "foreground": "white", "font": const.FONT_SM},
    {"background": "blue", "foreground": "white", "font": const.FONT_SM},
    {"background": "green", "foreground": "white", "font": const.FONT_SM},
    {"background": "black", "foreground": "white", "font": const.FONT_SM},
    {"background": "purple", "foreground": "white", "font": const.FONT_SM},
    {"background": "orange", "foreground": "black", "font": const.FONT_SM},
    {"background": "cyan", "foreground": "black", "font": const.FONT_SM},
    {"background": "olive", "foreground": "black", "font": const.FONT_SM},
    {"background": "pink", "foreground": "black", "font": const.FONT_SM},
    {"background": "gray", "foreground": "black", "font": const.FONT_SM},
]
COLOR = {c: v["background"] for c, v in zip(CONTENTS, STYLE_LIST, strict=False)}


class App(tk.Tk):
    rows: ClassVar[tuple[int]] = tuple(range(6 + len(CONTENTS)))
    row_span: ClassVar[int] = len(rows) + 1

    def __init__(self) -> None:
        super().__init__()

        self.curr_dir = "../llama"
        self.image_dir: Path = Path()
        self.canvas: tk.Canvas | None = None
        self.pages = []
        self.dirty = False
        self.dragging = False

        self.title("Outline labels on images of herbarium sheets")

        self.grid_rowconfigure(self.rows, weight=0)
        self.grid_rowconfigure(self.row_span, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.image_frame = ttk.Frame(self)
        self.image_frame.grid(row=0, column=0, rowspan=self.row_span + 1, sticky="nsew")

        self.control_frame = ttk.Frame(self, relief="sunken", borderwidth=2)
        self.control_frame.grid(
            row=0, column=1, rowspan=self.row_span + 1, sticky="nsew"
        )

        self.image_button = tk.Button(
            self.control_frame,
            text="Choose image directory",
            command=self.get_image_dir,
            font=const.FONT_SM,
        )
        self.image_button.grid(row=0, column=1, padx=16, pady=16)

        self.load_button = tk.Button(
            self.control_frame, text="Load", command=self.load, font=const.FONT_SM
        )
        self.load_button.grid(row=1, column=1, padx=16, pady=16)

        self.save_button = tk.Button(
            self.control_frame,
            text="Save",
            command=self.save,
            state="disabled",
            font=const.FONT_SM,
        )
        self.save_button.grid(row=2, column=1, padx=16, pady=16)

        self.sheet = ttk.Label(self.control_frame, text="", font=const.FONT_SM)
        self.sheet.grid(row=3, column=1, padx=16, pady=16, sticky="ew")

        self.spinner = Spinner(self.control_frame, command=self.change_page, width=140)
        self.spinner.grid(row=4, column=1, padx=16, pady=16)

        self.content_label = ttk.Label(
            self.control_frame, text="Label content type", font=const.FONT_SM
        )
        self.content_label.grid(row=6, column=1, padx=16, pady=16, sticky="ew")

        self.content = tk.StringVar()
        self.content.set(CONTENTS[0])

        style = ttk.Style(self)
        for i, (content, opts) in enumerate(zip(CONTENTS, STYLE_LIST, strict=False), 7):
            name = f"{content}.TRadiobutton"
            style.configure(name, **opts)
            radio = ttk.Radiobutton(
                self.control_frame,
                text=content,
                value=content,
                variable=self.content,
                style=name,
            )
            radio.grid(sticky="w", row=i, column=1, padx=32, pady=8)

        self.protocol("WM_DELETE_WINDOW", self.safe_quit)
        self.focus()
        self.unbind_all("<<NextWindow>>")

    @property
    def index(self) -> int:
        return self.spinner.get() - 1

    @property
    def page(self) -> Page:
        return self.pages[self.index]

    def change_page(self) -> None:
        if self.pages:
            self.display_page()

    def display_page(self) -> None:
        canvas_height = self.image_frame.winfo_height()
        self.page.resize(canvas_height)
        self.canvas.delete("all")
        self.canvas.create_image((0, 0), image=self.page.photo, anchor="nw")
        self.display_page_boxes()

        self.sheet.configure(text=Path(self.page.path).name)

    def display_page_boxes(self) -> None:
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

    def clear_page_boxes(self) -> None:
        for i, id_ in enumerate(self.canvas.find_all()):
            if i != 0:  # First object is the page itself
                self.canvas.delete(id_)

    def on_canvas_press(self, event: Event) -> None:
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.dirty = True
        content = self.content.get()
        color = COLOR[content]
        id_ = self.canvas.create_rectangle(0, 0, 1, 1, outline=color, width=4)
        self.page.boxes.append(Box(id_=id_, x0=x, y0=y, x1=x, y1=y, content=content))
        self.dragging = True

    def on_canvas_move(self, event: Event) -> None:
        if self.dragging and self.pages:
            box = self.page.boxes[-1]
            box.x1 = self.canvas.canvasx(event.x)
            box.y1 = self.canvas.canvasy(event.y)
            self.canvas.coords(box.id, box.x0, box.y0, box.x1, box.y1)

    def on_canvas_release(self, _: Event) -> None:
        if self.dragging and self.pages:
            self.page.filter_size()
            self.display_page_boxes()
            self.dragging = False

    def on_delete_box(self, event: Event) -> None:
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.dirty = True
        self.page.filter_delete(x, y)
        self.display_page_boxes()

    def save(self) -> None:
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

    def load(self) -> None:
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

    def setup_canvas(self) -> None:
        self.update()

        self.canvas = tk.Canvas(
            self.image_frame,
            width=self.image_frame.winfo_width(),
            height=self.image_frame.winfo_height(),
            background="black",
            cursor="cross",
        )
        self.canvas.grid(row=0, column=0, rowspan=self.row_span, sticky="nsew")

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<ButtonRelease-3>", self.on_delete_box)  # right-click

    def get_image_dir(self) -> None:
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

    def spinner_update(self, high: int) -> None:
        self.spinner.low = 1
        self.spinner.high = high
        self.spinner.set(1)

    def spinner_clear(self) -> None:
        self.spinner.low = 0
        self.spinner.high = 0
        self.spinner.set(0)

    def safe_quit(self) -> None:
        if self.dirty:
            yes = messagebox.askyesno(
                self.title(),
                "Are you sure you want to exit without saving?",
            )
            if not yes:
                return
        self.destroy()


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
