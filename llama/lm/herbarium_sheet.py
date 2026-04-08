from dspy import InputField, OutputField, Signature

from llama.fields import (
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
    flower_color,
    flower_present,
    fruit_color,
    fruit_present,
    geodetic_datum,
    habit,
    habitat,
    identified_by,
    infraspecific_epithet,
    infraspecific_name_authorship,
    latitude,
    leaf_margin,
    leaf_shape,
    longitude,
    municipality,
    occurrence_remarks,
    plant_height,
    plant_size,
    scientific_name,
    scientific_name_authorship,
    state_province,
)
from llama.fields import (
    locality as locality_,
)
from llama.fields import (
    trs as trs_,
)
from llama.fields import (
    utm as utm_,
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
        default=scientific_name.DEFAULTS["scientificName"],
        desc=scientific_name.SCIENTIFIC_NAME,
    )
    scientificNameAuthorship: str = OutputField(
        default=scientific_name.DEFAULTS["scientificNameAuthorship"],
        desc=scientific_name_authorship.SCIENTIFIC_NAME_AUTHORSHIP,
    )
    infraspecificEpithet: str = OutputField(
        default=infraspecific_epithet.DEFAULTS["infraspecificEpithet"],
        desc=infraspecific_epithet.INFRASPECIFIC_EPITHET,
    )
    infraspecificNameAuthorship: str = OutputField(
        default=infraspecific_name_authorship.DEFAULTS["infraspecificNameAuthorship"],
        desc=infraspecific_name_authorship.INFRASPECIFIC_NAME_AUTHORSHIP,
    )
    family: str = OutputField(
        default=family.DEFAULTS["family"],
        desc=family.FAMILY,
    )
    associatedTaxa: str = OutputField(
        default=associated_taxa.DEFAULTS["associatedTaxa"],
        desc=associated_taxa.ASSOCIATED_TAXA,
    )
    verbatimEventDate: str = OutputField(
        default=event_date.DEFAULTS["verbatimEventDate"],
        desc=event_date.VERBATIM_EVENT_DATE,
    )
    collector: str = OutputField(
        default=collector.DEFAULTS["collector"],
        desc=collector.COLLECTOR,
    )
    collectorNumber: str = OutputField(
        default=collector_number.DEFAULTS["collectorNumber"],
        desc=collector_number.COLLECTOR_NUMBER,
    )
    identifiedBy: str = OutputField(
        default=identified_by.DEFAULTS["identifiedBy"],
        desc=identified_by.IDENTIFIED_BY,
    )
    dateIdentified: str = OutputField(
        default=date_identified.DEFAULTS["dateIdentified"],
        desc=date_identified.DATE_IDENTIFIED,
    )
    country: str = OutputField(
        default=country.DEFAULTS["country"],
        desc=country.COUNTRY,
    )
    stateProvince: str = OutputField(
        default=state_province.DEFAULTS["stateProvince"],
        desc=state_province.STATE_PROVINCE,
    )
    county: str = OutputField(
        default=county.DEFAULTS["county"],
        desc=county.COUNTY,
    )
    municipality: str = OutputField(
        default=municipality.DEFAULTS["municipality"],
        desc=municipality.MUNICIPALITY,
    )
    verbatimElevation: str = OutputField(
        default=elevation.DEFAULTS["verbatimElevation"],
        desc=elevation.VERBATIM_ELEVATION,
    )
    elevationValues: list[float] = OutputField(
        default=elevation.DEFAULTS["elevationValues"],
        desc=elevation.ELEVATION_VALUES,
    )
    elevationUnits: list[str] = OutputField(
        default=elevation.DEFAULTS["elevationUnits"],
        desc=elevation.ELEVATION_UNITS,
    )
    elevationEstimated: bool = OutputField(
        default=elevation.DEFAULTS["elevationEstimated"],
        desc=elevation.ELEVATION_ESTIMATED,
    )
    verbatimLatitude: str = OutputField(
        default=latitude.DEFAULTS["verbatimLatitude"],
        desc=latitude.VERBATIM_LATITUDE,
    )
    verbatimLongitude: str = OutputField(
        default=longitude.DEFAULTS["verbatimLongitude"],
        desc=longitude.VERBATIM_LONGITUDE,
    )
    geodeticDatum: str = OutputField(
        default=geodetic_datum.DEFAULTS["geodeticDatum"],
        desc=geodetic_datum.GEODETIC_DATUM,
    )
    trs: str = OutputField(
        default=trs_.DEFAULTS["trs"],
        desc=trs_.TRS,
    )
    trsTownship: str = OutputField(
        default=trs_.DEFAULTS["trsTownship"],
        desc=trs_.TRS_TOWNSHIP,
    )
    trsRange: str = OutputField(
        default=trs_.DEFAULTS["trsRange"],
        desc=trs_.TRS_RANGE,
    )
    trsSection: str = OutputField(
        default=trs_.DEFAULTS["trsSection"],
        desc=trs_.TRS_SECTION,
    )
    trsQuad: str = OutputField(
        default=trs_.DEFAULTS["trsQuad"],
        desc=trs_.TRS_QUAD,
    )
    utm: str = OutputField(
        default=utm_.DEFAULTS["utm"],
        desc=utm_.UTM,
    )
    utmNorthing: str = OutputField(
        default=utm_.DEFAULTS["utmNorthing"],
        desc=utm_.UTM_NORTHING,
    )
    utmEasting: str = OutputField(
        default=utm_.DEFAULTS["utmEasting"],
        desc=utm_.UTM_EASTING,
    )
    utmZone: str = OutputField(
        default=utm_.DEFAULTS["utmZone"],
        desc=utm_.UTM_ZONE,
    )
    locality: str = OutputField(
        default=locality_.DEFAULTS["locality"],
        desc=locality_.LOCALITY,
    )
    habitat: str = OutputField(
        default=habitat.DEFAULTS["habitat"],
        desc=habitat.HABITAT,
    )
    flowersPresent: bool = OutputField(
        default=flower_present.DEFAULTS["flowersPresent"],
        desc=flower_present.FLOWERS_PRESENT,
    )
    fruitPresent: bool = OutputField(
        default=fruit_present.DEFAULTS["fruitPresent"],
        desc=fruit_present.FRUIT_PRESENT,
    )
    flowerColor: str = OutputField(
        default=flower_color.DEFAULTS["flowerColor"],
        desc=flower_color.FLOWER_COLOR,
    )
    fruitColor: str = OutputField(
        default=fruit_color.DEFAULTS["fruitColor"],
        desc=fruit_color.FRUIT_COLOR,
    )
    plantHeight: str = OutputField(
        default=plant_height.DEFAULTS["plantHeight"],
        desc=plant_height.PLANT_HEIGHT,
    )
    plantSize: list[str] = OutputField(
        default=plant_size.DEFAULTS["plantSize"],
        desc=plant_size.PLANT_SIZE,
    )
    habit: str = OutputField(
        default=habit.DEFAULTS["habit"],
        desc=habit.HABIT,
    )
    abundance: str = OutputField(
        default=abundance.DEFAULTS["abundance"],
        desc=abundance.ABUNDANCE,
    )
    leafShape: str = OutputField(
        default=leaf_shape.DEFAULTS["leafShape"],
        desc=leaf_shape.LEAF_SHAPE,
    )
    leafMargin: str = OutputField(
        default=leaf_margin.DEFAULTS["leafMargin"],
        desc=leaf_margin.LEAF_MARGIN,
    )
    occurrenceRemarks: str = OutputField(
        default=occurrence_remarks.DEFAULTS["occurrenceRemarks"],
        desc=occurrence_remarks.OCCURRENCE_REMARKS,
    )
