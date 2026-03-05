from typing import Any

from llama.parse2_fields.associated_taxa import AssociatedTaxa
from llama.parse2_fields.country import Country
from llama.parse2_fields.date_identified import DateIdentified
from llama.parse2_fields.elevation import Elevation
from llama.parse2_fields.event_date import EventDate
from llama.parse2_fields.family import Family
from llama.parse2_fields.geodetic_datum import GeodeticDatum
from llama.parse2_fields.habitat import Habitat
from llama.parse2_fields.identified_by import IdentifiedBy
from llama.parse2_fields.infraspecific_epithet import InfraspecificEpithet
from llama.parse2_fields.infraspecific_name_authorship import (
    InfraspecificNameAuthorship,
)
from llama.parse2_fields.latitude import Latitude
from llama.parse2_fields.locality import Locality
from llama.parse2_fields.longitude import Longitude
from llama.parse2_fields.municipality import Municipality
from llama.parse2_fields.occurrence_remarks import OccurrenceRemarks
from llama.parse2_fields.record_number import RecordNumber
from llama.parse2_fields.recorded_by import RecordedBy
from llama.parse2_fields.scientific_name import ScientificName
from llama.parse2_fields.scientific_name_authorship import ScientificNameAuthorship
from llama.parse2_fields.state_province import StateProvince
from llama.parse2_fields.trs import Trs
from llama.parse2_fields.utm import Utm

FIELD_ACTIONS: dict[str, Any] = {
    "associatedTaxa": AssociatedTaxa,
    "country": Country,
    "county": Country,
    "dateIdentified": DateIdentified,
    "family": Family,
    "geodeticDatum": GeodeticDatum,
    "habitat": Habitat,
    "identifiedBy": IdentifiedBy,
    "infraspecificEpithet": InfraspecificEpithet,
    "infraspecificNameAuthorship": InfraspecificNameAuthorship,
    "locality": Locality,
    "municipality": Municipality,
    "occurrenceRemarks": OccurrenceRemarks,
    "recordNumber": RecordNumber,
    "recordedBy": RecordedBy,
    "scientificName": ScientificName,
    "scientificNameAuthorship": ScientificNameAuthorship,
    "stateProvince": StateProvince,
    "trs": Trs,
    "utm": Utm,
    "verbatimElevation": Elevation,
    "verbatimEventDate": EventDate,
    "verbatimLatitude": Latitude,
    "verbatimLongitude": Longitude,

    # elevationValues: 1,
    # elevationUnits: 1,
    # elevationEstimated: 1,
    # township: 1,
    # range: 1,
    # section: 1,
    # quad: 1,
    # northing: 1,
    # easting: 1,
    # zone: 1,
    # flowersPresent: 1,
    # fruitPresent: 1,
    # flowerColor: 1,
    # fruitColor: 1,
    # plantHeight: 1,
    # plantSize: 1,
    # habit: 1,
    # abundance: 1,
    # leafShape: 1,
    # leafMargin: 1,
}
