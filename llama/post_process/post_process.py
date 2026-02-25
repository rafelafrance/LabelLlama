import re


def remove_chars(
    value: str, *, leading: str = "", trailing: str = "", anywhere: str = ""
) -> str:
    value = value or ""
    for char in leading:
        value = value.removeprefix(char)
    for char in trailing:
        value = value.removesuffix(char)
    for char in anywhere:
        value = value.replace(char, "")
    return value


def no_hallucination(value: str, text: str) -> str:
    return value if value in text else ""


# #############################################################################
def associated_taxa(value: str, _text: str) -> str:
    return remove_chars(value, trailing=".", anywhere="*")


def county(value: str, _text: str) -> str:
    value = remove_chars(value, trailing=".")
    # Remove label
    value = re.sub(r"\s(co\.?|county)$", "", value, flags=re.IGNORECASE)
    return value.title()


def country(value: str, text: str) -> str:
    value = remove_chars(value, trailing=".")
    value = no_hallucination(value, text)
    value = "U.S.A." if value == "U.S.A" else value  # Keep the dot in this case
    return value


def elevation(value: str, _text: str) -> str:
    value = value or ""
    # Remove label
    value = re.sub(
        r"\s*(elevation|elev[.:]*|el[.:]*|altitude|alt[.:]*)\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )
    return value


def event_date(value: str, _text: str) -> str:
    value = value or ""
    # Remove label
    value = re.sub(r"\s*(date[.:]*)\s*", "", value, flags=re.IGNORECASE)
    return value


def family(value: str, text: str) -> str:
    value = remove_chars(value, trailing=".")
    value = value.split().pop() if value else ""
    value = no_hallucination(value, text)
    return value.title()


def habitat(value: str, _text: str) -> str:
    value = value or ""
    # Remove label
    value = re.sub(r"\s*(habitat[:,;]*)\s*", "", value, flags=re.IGNORECASE)
    return value


def record_number(value: str, _text: str) -> str:
    value = value or ""
    # Remove label
    value = re.sub(r"\s*(No[:,;]*)\s*", "", value, flags=re.IGNORECASE)
    return value


def scientific_name(value: str, _text: str) -> str:
    value = remove_chars(value, trailing=".")
    if not value:
        return ""
    genus, species = value.split()[:2]  # Remove authors & subspecies etc.
    genus = genus.title()
    species = species.lower()
    return f"{genus} {species}"


def state_province(value: str, text: str) -> str:
    value = remove_chars(value, trailing=".")
    value = no_hallucination(value, text)
    return value.title()


def trs(value: str, _text: str) -> str:
    return remove_chars(value, trailing=".")


def utm(value: str, _text: str) -> str:
    return remove_chars(value, leading="(", trailing=").")
