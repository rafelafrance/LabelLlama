import re


def associated_taxa(value: str, _text: str) -> str:
    if not value:
        return ""
    value = value.removesuffix(".")
    return value


def county(value: str, _text: str) -> str:
    if not value:
        return ""
    value = re.sub(r"\s(co\.?|county)$", "", value, flags=re.IGNORECASE)
    return value.title()


def elevation(value: str, _text: str) -> str:
    if not value:
        return ""
    value = re.sub(
        r"(elevation|elev[.:]?|altitude|alt[.:])\s?", "", value, flags=re.IGNORECASE
    )
    return value


def family(value: str, text: str) -> str:
    if not value or value not in text:
        return ""
    return value.title()


def scientific_name(value: str, _text: str) -> str:
    if not value:
        return ""
    value = value.removesuffix(".")
    genus, species = value.split()[:2]
    genus = genus.title()
    species = species.lower()
    return f"{genus} {species}"
