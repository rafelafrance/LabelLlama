from collections import defaultdict
from enum import StrEnum


class ModelStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "ERROR"
    UNKNOWN = ""

    @classmethod
    def normalize(cls, value: object) -> ModelStatus:
        status = str(value or "").strip().lower()
        match status:
            case "success":
                return cls.SUCCESS
            case "error":
                return cls.ERROR
            case _:
                return cls.UNKNOWN

    @classmethod
    def is_success(cls, value: object) -> bool:
        return cls.normalize(value) == cls.SUCCESS


class StatusCounts:
    def __init__(self) -> None:
        self.counts: defaultdict[ModelStatus, int] = defaultdict(int)

    def count(self, value: object) -> ModelStatus:
        status = ModelStatus.normalize(value)
        self.counts[status] += 1
        return status

    def get(self, value: object, default: int = 0) -> int:
        return self.counts.get(ModelStatus.normalize(value), default)

    def __getitem__(self, value: object) -> int:
        return self.counts[ModelStatus.normalize(value)]
