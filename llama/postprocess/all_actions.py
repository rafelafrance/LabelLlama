from typing import Any

from llama.postprocess.associated_taxa import AssociatedTaxa
from llama.postprocess.country import Country
from llama.postprocess.county import County
from llama.postprocess.date_identified import DateIdentified
from llama.postprocess.elevation import Elevation
from llama.postprocess.event_date import EventDate
from llama.postprocess.family import Family
from llama.postprocess.geodetic_datum import GeodeticDatum
from llama.postprocess.habitat import Habitat
from llama.postprocess.identified_by import IdentifiedBy
from llama.postprocess.infraspecific_epithet import InfraspecificEpithet
from llama.postprocess.infraspecific_name_authorship import (
    InfraspecificNameAuthorship,
)
from llama.postprocess.latitude import Latitude
from llama.postprocess.locality import Locality
from llama.postprocess.longitude import Longitude
from llama.postprocess.municipality import Municipality
from llama.postprocess.occurrence_remarks import OccurrenceRemarks
from llama.postprocess.record_number import RecordNumber
from llama.postprocess.recorded_by import RecordedBy
from llama.postprocess.scientific_name import ScientificName
from llama.postprocess.scientific_name_authorship import ScientificNameAuthorship
from llama.postprocess.state_province import StateProvince
from llama.postprocess.trs import Trs
from llama.postprocess.utm import Utm

FIELD_ACTIONS: dict[str, Any] = {
    "scientificName": ScientificName,
    "scientificNameAuthorship": ScientificNameAuthorship,
    "infraspecificEpithet": InfraspecificEpithet,
    "infraspecificNameAuthorship": InfraspecificNameAuthorship,
    "family": Family,
    "associatedTaxa": AssociatedTaxa,
    #
    "recordNumber": RecordNumber,
    "verbatimEventDate": EventDate,
    "recordedBy": RecordedBy,
    "identifiedBy": IdentifiedBy,
    "dateIdentified": DateIdentified,
    #
    "habitat": Habitat,
    "occurrenceRemarks": OccurrenceRemarks,
    #
    "locality": Locality,
    "country": Country,
    "stateProvince": StateProvince,
    "county": County,
    "municipality": Municipality,
    "geodeticDatum": GeodeticDatum,
    "trs": Trs,
    "utm": Utm,
    "verbatimLatitude": Latitude,
    "verbatimLongitude": Longitude,
    "verbatimElevation": Elevation,
    #
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
