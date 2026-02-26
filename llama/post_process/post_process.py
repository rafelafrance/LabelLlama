import re
from typing import Any

from spacy import Language

from llama.traiter.rules.elevation import Elevation
from llama.traiter.rules.number import Number

ENABLE_PIPES: list[str] = ["tagger", "parser", "attribute_ruler", "lemmatizer"]


def remove_chars(
    dwc_field: str, *, leading: str = "", trailing: str = "", anywhere: str = ""
) -> str:
    dwc_field = dwc_field or ""
    for char in leading:
        dwc_field = dwc_field.removeprefix(char)
    for char in trailing:
        dwc_field = dwc_field.removesuffix(char)
    for char in anywhere:
        dwc_field = dwc_field.replace(char, "")
    return dwc_field


def no_hallucination(dwc_field: str, ocr_text: str) -> str:
    return dwc_field if dwc_field in ocr_text else ""


# #############################################################################
def associated_taxa(
    dwc_field: str, _dwc_row: dict[str, Any], _ocr_text: str, _nlp: Language
) -> str:
    return remove_chars(dwc_field, trailing=".", anywhere="*")


def county(
    dwc_field: str, _dwc_row: dict[str, Any], _ocr_text: str, _nlp: Language
) -> str:
    dwc_field = remove_chars(dwc_field, trailing=".")
    # Remove label
    dwc_field = re.sub(r"\s(co\.?|county)$", "", dwc_field, flags=re.IGNORECASE)
    return dwc_field.title()


def country(
    dwc_field: str, _dwc_row: dict[str, Any], ocr_text: str, _nlp: Language
) -> str:
    dwc_field = remove_chars(dwc_field, trailing=".")
    dwc_field = no_hallucination(dwc_field, ocr_text)
    dwc_field = "U.S.A." if dwc_field == "U.S.A" else dwc_field  # Keep dot in this case
    return dwc_field


def elevation(
    dwc_field: str, dwc_row: dict[str, Any], _ocr_text: str, nlp: Language
) -> str:
    enable_pipes = ENABLE_PIPES + Elevation.enable_pipes + Number.enable_pipes
    with nlp.select_pipes(enable=enable_pipes):
        doc = nlp(dwc_field)

    dwc_row |= doc.ents[0]._.trait.to_dict()

    # Remove label
    dwc_field = re.sub(
        r"\s*(elevation|elev[.:]*|el[.:]*|altitude|alt[.:]*)\s*",
        "",
        dwc_field,
        flags=re.IGNORECASE,
    )
    return dwc_field


def event_date(
    dwc_field: str, _dwc_row: dict[str, Any], _ocr_text: str, _nlp: Language
) -> str:
    # Remove label
    dwc_field = re.sub(r"\s*(date[.:]*)\s*", "", dwc_field, flags=re.IGNORECASE)
    return dwc_field


def family(
    dwc_field: str, _dwc_row: dict[str, Any], ocr_text: str, _nlp: Language
) -> str:
    dwc_field = remove_chars(dwc_field, trailing=".")
    dwc_field = dwc_field.split().pop() if dwc_field else ""
    dwc_field = no_hallucination(dwc_field, ocr_text)
    return dwc_field.title()


def habitat(
    dwc_field: str, _dwc_row: dict[str, Any], _ocr_text: str, _nlp: Language
) -> str:
    # Remove label
    dwc_field = re.sub(r"\s*(habitat[:,;]*)\s*", "", dwc_field, flags=re.IGNORECASE)
    return dwc_field


def record_number(
    dwc_field: str, _dwc_row: dict[str, Any], _ocr_text: str, _nlp: Language
) -> str:
    # Remove label
    dwc_field = re.sub(r"\s*(No[:,;]*)\s*", "", dwc_field, flags=re.IGNORECASE)
    return dwc_field


def scientific_name(
    dwc_field: str, _dwc_row: dict[str, Any], _ocr_text: str, _nlp: Language
) -> str:
    dwc_field = remove_chars(dwc_field, trailing=".")
    if not dwc_field:
        return ""
    genus, species = dwc_field.split()[:2]  # Remove authors & subspecies etc.
    genus = genus.title()
    species = species.lower()
    return f"{genus} {species}"


def state_province(
    dwc_field: str, _dwc_row: dict[str, Any], ocr_text: str, _nlp: Language
) -> str:
    dwc_field = remove_chars(dwc_field, trailing=".")
    dwc_field = no_hallucination(dwc_field, ocr_text)
    return dwc_field.title()


def trs(
    dwc_field: str, _dwc_row: dict[str, Any], _ocr_text: str, _nlp: Language
) -> str:
    return remove_chars(dwc_field, trailing=".")


def utm(
    dwc_field: str, _dwc_row: dict[str, Any], _ocr_text: str, _nlp: Language
) -> str:
    return remove_chars(dwc_field, leading="(", trailing=").")
