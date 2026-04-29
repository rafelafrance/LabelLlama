from dspy import InputField, OutputField, Signature

from llama.fields.dwc import (
    abundance,
    associated_taxa,
    collector,
    collector_number,
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
    infraspecific_name_authorship,
    latitude,
    longitude,
    municipality,
    occurrence_remarks,
    scientific_name,
    scientific_name_authorship,
    state_province,
)
from llama.fields.dwc import locality as locality_  # Quiet the linter
from llama.fields.dwc import trs as trs_  # Linter BS
from llama.fields.dwc import utm as utm_  # Linter BS
from llama.fields.plants import (
    flower_color,
    flower_present,
    fruit_color,
    fruit_present,
    habit,
    life_form,
    life_stage,
    plant_height,
    woodiness,
)


class HerbariumSheet(Signature):
    """
    Analyze text from herbarium sheets and extract this information.

    I need the text exactly as it appears in the text.
    Leave abbreviations exactly as they are.
    If the data field is not found in the text return the default value.

    I want plain text:
      ✅ Use UTF-8 characters only.
      ❌ DO NOT change the text in any way.
      ❌ DO NOT add or delete any punctuation and do not add or delete any spaces.
      ❌ DO NOT include HTML tags
      ❌ DO NOT include HTML entities
      ❌ DO NOT include MATHML tags,
      ❌ DO NOT include Markdown tags.
      ❌ DO NOT add or infer any new information.
      ❌ DO NOT rephrase, summarize, or infer meaning.
      ❌ DO NOT turn phrases into lists or categories.
      ✅ Use exact phrases from the label text only.

    ❌ Do not hallucinate!
    """

    text = InputField()

    scientificName: str = OutputField(
        desc=scientific_name.SCIENTIFIC_NAME,
    )
    scientificNameAuthorship: str = OutputField(
        desc=scientific_name_authorship.SCIENTIFIC_NAME_AUTHORSHIP,
    )
    infraspecificEpithet: str = OutputField(
        desc=infraspecific_epithet.INFRASPECIFIC_EPITHET,
    )
    infraspecificNameAuthorship: str = OutputField(
        desc=infraspecific_name_authorship.INFRASPECIFIC_NAME_AUTHORSHIP,
    )
    family: str = OutputField(
        desc=family.FAMILY,
    )
    associatedTaxa: str = OutputField(
        desc=associated_taxa.ASSOCIATED_TAXA,
    )
    verbatimEventDate: str = OutputField(
        desc=event_date.VERBATIM_EVENT_DATE,
    )
    collector: str = OutputField(
        desc=collector.COLLECTOR,
    )
    collectorNumber: str = OutputField(
        desc=collector_number.COLLECTOR_NUMBER,
    )
    identifiedBy: str = OutputField(
        desc=identified_by.IDENTIFIED_BY,
    )
    dateIdentified: str = OutputField(
        desc=date_identified.DATE_IDENTIFIED,
    )
    country: str = OutputField(
        desc=country.COUNTRY,
    )
    stateProvince: str = OutputField(
        desc=state_province.STATE_PROVINCE,
    )
    county: str = OutputField(
        desc=county.COUNTY,
    )
    municipality: str = OutputField(
        desc=municipality.MUNICIPALITY,
    )
    verbatimElevation: str = OutputField(
        desc=elevation.VERBATIM_ELEVATION,
    )
    elevationValues: list[float] = OutputField(
        desc=elevation.ELEVATION_VALUES,
    )
    elevationUnits: list[str] = OutputField(
        desc=elevation.ELEVATION_UNITS,
    )
    elevationEstimated: bool = OutputField(
        desc=elevation.ELEVATION_ESTIMATED,
    )
    verbatimLatitude: str = OutputField(
        desc=latitude.VERBATIM_LATITUDE,
    )
    verbatimLongitude: str = OutputField(
        desc=longitude.VERBATIM_LONGITUDE,
    )
    geodeticDatum: str = OutputField(
        desc=geodetic_datum.GEODETIC_DATUM,
    )
    trs: str = OutputField(
        desc=trs_.TRS,
    )
    trsTownship: str = OutputField(
        desc=trs_.TRS_TOWNSHIP,
    )
    trsRange: str = OutputField(
        desc=trs_.TRS_RANGE,
    )
    trsSection: str = OutputField(
        desc=trs_.TRS_SECTION,
    )
    trsQuad: str = OutputField(
        desc=trs_.TRS_QUAD,
    )
    utm: str = OutputField(
        desc=utm_.UTM,
    )
    utmNorthing: str = OutputField(
        desc=utm_.UTM_NORTHING,
    )
    utmEasting: str = OutputField(
        desc=utm_.UTM_EASTING,
    )
    utmZone: str = OutputField(
        desc=utm_.UTM_ZONE,
    )
    locality: str = OutputField(
        desc=locality_.LOCALITY,
    )
    habitat: str = OutputField(
        desc=habitat.HABITAT,
    )
    flowersPresent: bool = OutputField(
        desc=flower_present.FLOWERS_PRESENT,
    )
    fruitPresent: bool = OutputField(
        desc=fruit_present.FRUIT_PRESENT,
    )
    flowerColor: str = OutputField(
        desc=flower_color.FLOWER_COLOR,
    )
    fruitColor: str = OutputField(
        desc=fruit_color.FRUIT_COLOR,
    )
    plantHeight: str = OutputField(
        desc=plant_height.PLANT_HEIGHT,
    )
    habit: str = OutputField(
        desc=habit.HABIT,
    )
    lifeForm: str = OutputField(
        desc=life_form.LIFE_FORM,
    )
    abundance: str = OutputField(
        desc=abundance.ABUNDANCE,
    )
    occurrenceRemarks: str = OutputField(
        desc=occurrence_remarks.OCCURRENCE_REMARKS,
    )
    woodiness: str = OutputField(
        desc=woodiness.WOODINESS,
    )
    lifeStage: str = OutputField(
        desc=life_stage.LIFE_STAGE,
    )
