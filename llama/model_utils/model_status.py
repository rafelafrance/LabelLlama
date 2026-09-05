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
