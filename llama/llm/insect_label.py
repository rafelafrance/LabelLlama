from dspy import InputField, OutputField, Signature

from llama.fields.common import suborder
from llama.fields.dwc import (
    country,
    county,
    elevation,
    event_date,
    family,
    genus,
    habitat,
    identified_by,
    identified_by_id,
    island,
    island_group,
    locality,
    municipality,
    occurrence_id,
    occurrence_remarks,
    record_number,
    recorded_by,
    scientific_name,
    scientific_name_authorship,
    sex,
    specific_epithet,
    state_province,
    subgenus,
    verbatim_latitude,
    verbatim_longitude,
    water_body,
)


class InsectLabel(Signature):
    """
    Extract structured biological and collection metadata from insect label text.

    This signature processes OCRed or transcribed insect labels and extracts
    Darwin Core fields (taxonomy, geolocation, collection event) and insect specific
    fields like (sex).

    Extraction rules:

    - **Verbatim fidelity**: Preserve the original text exactly as it appears on the
      label. Do not expand abbreviations, correct spelling, normalize punctuation,
      add/remove whitespace, or rephrase in any way.
    - **No inference**: Only extract information explicitly present in the source text.
      Do not infer, summarize, categorize, or add any new information.
    - **Missing data**: If a field cannot be found in the text, return the default
      value defined for that field.
    - **Plain text output**: Return raw UTF-8 text only. Do not include HTML tags or
      entities, Markdown formatting, MATHML, or any other markup.
    - **No hallucination**: Never fabricate data not present in the source.
    """

    text: str = InputField(desc="Insect label text")

    scientificName: list[str] = OutputField(desc=scientific_name.SCIENTIFIC_NAME)
    scientificNameAuthorship: str = OutputField(
        desc=scientific_name_authorship.SCIENTIFIC_NAME_AUTHORSHIP
    )
    suborder: str = OutputField(desc=suborder.SUBORDER)
    family: str = OutputField(desc=family.FAMILY)
    genus: str = OutputField(desc=genus.GENUS)
    subgenus: str = OutputField(desc=subgenus.SUBGENUS)
    specificEpithet: str = OutputField(desc=specific_epithet.SPECIFIC_EPITHET)
    verbatimEventDate: str = OutputField(desc=event_date.EVENT_DATE)
    locality: str = OutputField(desc=locality.LOCALITY)
    habitat: str = OutputField(desc=habitat.HABITAT)
    sex: str = OutputField(desc=sex.SEX)
    verbatimElevation: str = OutputField(desc=elevation.VERBATIM_ELEVATION)
    elevationValues: list[float] = OutputField(desc=elevation.ELEVATION_VALUES)
    elevationUnits: list[str] = OutputField(desc=elevation.ELEVATION_UNITS)
    elevationEstimated: bool = OutputField(desc=elevation.ELEVATION_ESTIMATED)
    verbatimLatitude: str = OutputField(desc=verbatim_latitude.VERBATIM_LATITUDE)
    verbatimLongitude: str = OutputField(desc=verbatim_longitude.VERBATIM_LONGITUDE)
    recorded_by: str = OutputField(desc=recorded_by.RECORDED_BY)
    recordNumber: str = OutputField(desc=record_number.RECORD_NUMBER)
    identifiedBy: str = OutputField(desc=identified_by.IDENTIFIED_BY)
    identifiedByID: str = OutputField(desc=identified_by_id.IDENTIFIED_BY_ID)
    occurrenceID: str = OutputField(desc=occurrence_id.OCCURRENCE_ID)
    country: str = OutputField(desc=country.COUNTRY)
    stateProvince: str = OutputField(desc=state_province.STATE_PROVINCE)
    county: str = OutputField(desc=county.COUNTY)
    municipality: str = OutputField(desc=municipality.MUNICIPALITY)
    waterBody: str = OutputField(desc=water_body.WATER_BODY)
    island: str = OutputField(desc=island.ISLAND)
    islandGroup: str = OutputField(desc=island_group.ISLAND_GROUP)
    occurrenceRemarks: str = OutputField(desc=occurrence_remarks.OCCURRENCE_REMARKS)
