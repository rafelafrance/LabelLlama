from typing import Any

from llama.postprocess.abundance import Abundance
from llama.postprocess.associated_taxa import AssociatedTaxa
from llama.postprocess.country import Country
from llama.postprocess.county import County
from llama.postprocess.date_identified import DateIdentified
from llama.postprocess.elevation import Elevation
from llama.postprocess.event_date import EventDate
from llama.postprocess.family import Family
from llama.postprocess.flower_color import FlowerColor
from llama.postprocess.flower_present import FlowersPresent
from llama.postprocess.fruit_color import FruitColor
from llama.postprocess.fruit_present import FruitPresent
from llama.postprocess.geodetic_datum import GeodeticDatum
from llama.postprocess.habit import Habit
from llama.postprocess.habitat import Habitat
from llama.postprocess.identified_by import IdentifiedBy
from llama.postprocess.infraspecific_epithet import InfraspecificEpithet
from llama.postprocess.infraspecific_name_authorship import (
    InfraspecificNameAuthorship,
)
from llama.postprocess.latitude import Latitude
from llama.postprocess.leaf_margin import LeafMargin
from llama.postprocess.leaf_shape import LeafShape
from llama.postprocess.locality import Locality
from llama.postprocess.longitude import Longitude
from llama.postprocess.municipality import Municipality
from llama.postprocess.occurrence_remarks import OccurrenceRemarks
from llama.postprocess.plant_height import PlantHeight
from llama.postprocess.plant_size import PlantSize
from llama.postprocess.record_number import RecordNumber
from llama.postprocess.recorded_by import RecordedBy
from llama.postprocess.scientific_name import ScientificName
from llama.postprocess.scientific_name_authorship import ScientificNameAuthorship
from llama.postprocess.state_province import StateProvince
from llama.postprocess.trs import Trs
from llama.postprocess.utm import Utm

# This also is the base order of fields in reports
ALL_ACTIONS: dict[str, Any] = {
    "scientificName": ScientificName,
    "scientificNameAuthorship": ScientificNameAuthorship,
    "infraspecificEpithet": InfraspecificEpithet,
    "infraspecificNameAuthorship": InfraspecificNameAuthorship,
    "family": Family,
    "associatedTaxa": AssociatedTaxa,
    "recordNumber": RecordNumber,
    "verbatimEventDate": EventDate,
    "recordedBy": RecordedBy,
    "identifiedBy": IdentifiedBy,
    "dateIdentified": DateIdentified,
    "habitat": Habitat,
    "occurrenceRemarks": OccurrenceRemarks,
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
    "abundance": Abundance,
    "flowersPresent": FlowersPresent,
    "flowerColor": FlowerColor,
    "fruitPresent": FruitPresent,
    "fruitColor": FruitColor,
    "plantHeight": PlantHeight,
    "plantSize": PlantSize,
    "habit": Habit,
    "leafShape": LeafShape,
    "leafMargin": LeafMargin,
}
