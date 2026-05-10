from typing import Any

from llama.fields.common.suborder import Suborder
from llama.fields.dwc.country import Country
from llama.fields.dwc.county import County
from llama.fields.dwc.decimal_latitude import DecimalLatitude
from llama.fields.dwc.decimal_longitude import DecimalLongitude
from llama.fields.dwc.elevation import Elevation
from llama.fields.dwc.event_date import EventDate
from llama.fields.dwc.family import Family
from llama.fields.dwc.genus import Genus
from llama.fields.dwc.habitat import Habitat
from llama.fields.dwc.identified_by import IdentifiedBy
from llama.fields.dwc.island import Island
from llama.fields.dwc.island_group import IslandGroup
from llama.fields.dwc.locality import Locality
from llama.fields.dwc.municipality import Municipality
from llama.fields.dwc.occurrence_id import OccurrenceID
from llama.fields.dwc.occurrence_remarks import OccurrenceRemarks
from llama.fields.dwc.record_number import RecordNumber
from llama.fields.dwc.recorded_by import RecordedBy
from llama.fields.dwc.scientific_name import ScientificName
from llama.fields.dwc.scientific_name_authorship import ScientificNameAuthorship
from llama.fields.dwc.sex import Sex
from llama.fields.dwc.specific_epithet import SpecificEpithet
from llama.fields.dwc.state_province import StateProvince
from llama.fields.dwc.subgenus import Subgenus
from llama.fields.dwc.verbatim_latitude import VerbatimLatitude
from llama.fields.dwc.verbatim_longitude import VerbatimLongitude
from llama.fields.dwc.vernacular_name import VernacularName
from llama.fields.dwc.water_body import WaterBody

# This also is the base order of fields in reports
INSECT_FIELDS: dict[str, Any] = {
    "scientificName": ScientificName,
    "scientificNameAuthorship": ScientificNameAuthorship,
    "suborder": Suborder,
    "family": Family,
    "genus": Genus,
    "subgenus": Subgenus,
    "specificEpithet": SpecificEpithet,
    "vernacularName": VernacularName,
    "verbatimEventDate": EventDate,
    "locality": Locality,
    "habitat": Habitat,
    "sex": Sex,
    "verbatimElevation": Elevation,
    "verbatimLatitude": VerbatimLatitude,
    "verbatimLongitude": VerbatimLongitude,
    "decimalLatitude": DecimalLatitude,
    "decimalLongitude": DecimalLongitude,
    "recordedBy": RecordedBy,
    "recordNumber": RecordNumber,
    "identifiedBy": IdentifiedBy,
    "identifiedByID": IdentifiedBy,
    "occurrenceID": OccurrenceID,
    "country": Country,
    "stateProvince": StateProvince,
    "county": County,
    "municipality": Municipality,
    "waterBody": WaterBody,
    "island": Island,
    "islandGroup": IslandGroup,
    "occurrenceRemarks": OccurrenceRemarks,
}
