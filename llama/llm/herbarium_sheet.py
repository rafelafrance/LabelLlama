import textwrap

from dspy import InputField, OutputField, Signature

from llama.fields.common import infraspecific_name_authorship
from llama.fields.common import trs as trs_
from llama.fields.common import utm as utm_
from llama.fields.dwc import (
    associated_taxa,
    collector,
    country,
    county,
    date_identified,
    elevation,
    event_date,
    family,
    geodetic_datum,
    habitat,
    identified_by,
    infraspecific_epithet,
    latitude,
    longitude,
    municipality,
    occurrence_remarks,
    record_number,
    scientific_name,
    scientific_name_authorship,
    state_province,
)
from llama.fields.dwc import locality as locality_  # Quiet the linter
from llama.fields.plants import (
    abundance,
    flower_color,
    flower_present,
    fruit_color,
    fruit_present,
    habit,
    life_form,
    life_stage,
    plant_height,
    reproduction,
    sex,
    woodiness,
)

HERBARIUM_SHEET = textwrap.dedent("""
    Extract structured botanical and collection metadata from herbarium label text.

    This signature processes OCR'd or transcribed herbarium sheet labels and extracts
    Darwin Core fields (taxonomy, geolocation, collection event) plus plant-specific
    morphological data (phenology, habit, life form, etc.).

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
    """)


class HerbariumSheet(Signature):
    """
    Extract structured botanical and collection metadata from herbarium label text.

    This signature processes OCR'd or transcribed herbarium sheet labels and extracts
    Darwin Core fields (taxonomy, geolocation, collection event) plus plant-specific
    morphological data (phenology, habit, life form, etc.).

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

    text = InputField()

    scientificName: list[str] = OutputField(desc=scientific_name.SCIENTIFIC_NAME)
    scientificNameAuthorship: str = OutputField(
        desc=scientific_name_authorship.SCIENTIFIC_NAME_AUTHORSHIP)
    infraspecificEpithet: str = OutputField(
        desc=infraspecific_epithet.INFRASPECIFIC_EPITHET)
    infraspecificNameAuthorship: str = OutputField(
        desc=infraspecific_name_authorship.INFRASPECIFIC_NAME_AUTHORSHIP)
    family: str = OutputField(desc=family.FAMILY)
    associatedTaxa: str = OutputField(desc=associated_taxa.ASSOCIATED_TAXA)
    verbatimEventDate: str = OutputField(desc=event_date.VERBATIM_EVENT_DATE)
    collector: str = OutputField(desc=collector.COLLECTOR)
    recordNumber: str = OutputField(desc=record_number.RECORD_NUMBER)
    identifiedBy: str = OutputField(desc=identified_by.IDENTIFIED_BY)
    dateIdentified: str = OutputField(desc=date_identified.DATE_IDENTIFIED)
    country: str = OutputField(desc=country.COUNTRY)
    stateProvince: str = OutputField(desc=state_province.STATE_PROVINCE)
    county: str = OutputField(desc=county.COUNTY)
    municipality: str = OutputField(desc=municipality.MUNICIPALITY)
    verbatimElevation: str = OutputField(desc=elevation.VERBATIM_ELEVATION)
    elevationValues: list[float] = OutputField(desc=elevation.ELEVATION_VALUES)
    elevationUnits: list[str] = OutputField(desc=elevation.ELEVATION_UNITS)
    elevationEstimated: bool = OutputField(desc=elevation.ELEVATION_ESTIMATED)
    verbatimLatitude: str = OutputField(desc=latitude.VERBATIM_LATITUDE)
    verbatimLongitude: str = OutputField(desc=longitude.VERBATIM_LONGITUDE)
    geodeticDatum: str = OutputField(desc=geodetic_datum.GEODETIC_DATUM)
    trs: str = OutputField(desc=trs_.TRS)
    trsTownship: str = OutputField(desc=trs_.TRS_TOWNSHIP)
    trsRange: str = OutputField(desc=trs_.TRS_RANGE)
    trsSection: str = OutputField(desc=trs_.TRS_SECTION)
    trsQuad: str = OutputField(desc=trs_.TRS_QUAD)
    utm: str = OutputField(desc=utm_.UTM)
    utmNorthing: str = OutputField(desc=utm_.UTM_NORTHING)
    utmEasting: str = OutputField(desc=utm_.UTM_EASTING)
    utmZone: str = OutputField(desc=utm_.UTM_ZONE)
    locality: str = OutputField(desc=locality_.LOCALITY)
    habitat: str = OutputField(desc=habitat.HABITAT)
    flowersPresent: bool = OutputField(desc=flower_present.FLOWERS_PRESENT)
    fruitPresent: bool = OutputField(desc=fruit_present.FRUIT_PRESENT)
    flowerColor: str = OutputField(desc=flower_color.FLOWER_COLOR)
    fruitColor: str = OutputField(desc=fruit_color.FRUIT_COLOR)
    plantHeight: str = OutputField(desc=plant_height.PLANT_HEIGHT)
    habit: str = OutputField(desc=habit.HABIT)
    lifeForm: str = OutputField(desc=life_form.LIFE_FORM)
    abundance: str = OutputField(desc=abundance.ABUNDANCE)
    woodiness: str = OutputField(desc=woodiness.WOODINESS)
    lifeStage: str = OutputField(desc=life_stage.LIFE_STAGE)
    sex: str = OutputField(desc=sex.PLANT_SEX)
    reproduction: str = OutputField(desc=reproduction.PLANT_REPRODUCTION)
    occurrenceRemarks: str = OutputField(desc=occurrence_remarks.OCCURRENCE_REMARKS)
