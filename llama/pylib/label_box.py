TOO_SMALL = 20
COORDS = tuple[int, int, int, int]

CONTENTS = [
    "typewritten",
    "handwritten",
    "mixed",
    "barcode",
    "qrcode",
    "stamp",
    "palette",
    "ruler",
    "envelope",
]


class Box:
    def __init__(self, x0, y0, x1, y1, content, id_=None) -> None:
        if any(a is None for a in (x0, y0, x1, y1, content)):
            raise ValueError
        self.x0: int = x0
        self.y0: int = y0
        self.x1: int = x1
        self.y1: int = y1
        self.content: str = content
        self.id = id_  # Needed for tkinter

    def __str__(self):
        return f"{self.x0=} {self.y0=} {self.x1=} {self.y1=} {self.content=} {self.id=}"

    def as_dict(self, image_height: int, canvas_height: int) -> dict:
        x0, y0, x1, y1 = self.restore_coords(image_height, canvas_height)
        return {
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1,
            "content": self.content,
        }

    def area(self) -> int:
        return abs(self.x1 - self.x0) * abs(self.y1 - self.y0)

    def too_small(self) -> bool:
        return abs(self.x1 - self.x0) < TOO_SMALL or abs(self.y1 - self.y0) < TOO_SMALL

    def point_hit(self, x, y) -> bool:
        x0, x1 = (self.x0, self.x1) if self.x1 > self.x0 else (self.x1, self.x0)
        y0, y1 = (self.y0, self.y1) if self.y1 > self.y0 else (self.y1, self.y0)
        return x0 <= x <= x1 and y0 <= y <= y1

    def restore_coords(self, image_height: int, canvas_height: int) -> COORDS:
        ratio = image_height / canvas_height
        x0 = int(ratio * self.x0)
        y0 = int(ratio * self.y0)
        x1 = int(ratio * self.x1)
        y1 = int(ratio * self.y1)
        return x0, y0, x1, y1

    def fit_to_canvas(self, image_height: int, canvas_height: int):
        ratio = canvas_height / image_height
        self.x0 = int(ratio * self.x0)
        self.y0 = int(ratio * self.y0)
        self.x1 = int(ratio * self.x1)
        self.y1 = int(ratio * self.y1)
