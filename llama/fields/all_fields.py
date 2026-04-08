from typing import Any

from llama.fields.abundance import Abundance
from llama.fields.associated_taxa import AssociatedTaxa
from llama.fields.collector import Collector
from llama.fields.collector_number import CollectorNumber
from llama.fields.country import Country
from llama.fields.county import County
from llama.fields.date_identified import DateIdentified
from llama.fields.elevation import Elevation
from llama.fields.event_date import EventDate
from llama.fields.family import Family
from llama.fields.flower_color import FlowerColor
from llama.fields.flower_present import FlowersPresent
from llama.fields.fruit_color import FruitColor
from llama.fields.fruit_present import FruitPresent
from llama.fields.geodetic_datum import GeodeticDatum
from llama.fields.habit import Habit
from llama.fields.habitat import Habitat
from llama.fields.identified_by import IdentifiedBy
from llama.fields.infraspecific_epithet import InfraspecificEpithet
from llama.fields.infraspecific_name_authorship import (
    InfraspecificNameAuthorship,
)
from llama.fields.latitude import Latitude
from llama.fields.leaf_margin import LeafMargin
from llama.fields.leaf_shape import LeafShape
from llama.fields.locality import Locality
from llama.fields.longitude import Longitude
from llama.fields.municipality import Municipality
from llama.fields.occurrence_remarks import OccurrenceRemarks
from llama.fields.plant_height import PlantHeight
from llama.fields.plant_size import PlantSize
from llama.fields.scientific_name import ScientificName
from llama.fields.scientific_name_authorship import ScientificNameAuthorship
from llama.fields.state_province import StateProvince
from llama.fields.trs import Trs
from llama.fields.utm import Utm

# This also is the base order of fields in reports
ALL_FIELDS: dict[str, Any] = {
    "scientificName": ScientificName,
    "scientificNameAuthorship": ScientificNameAuthorship,
    "infraspecificEpithet": InfraspecificEpithet,
    "infraspecificNameAuthorship": InfraspecificNameAuthorship,
    "family": Family,
    "associatedTaxa": AssociatedTaxa,
    "verbatimEventDate": EventDate,
    "collector": Collector,
    "recordedBy": Collector,
    "collectorNumber": CollectorNumber,
    "recordNumber": CollectorNumber,
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
