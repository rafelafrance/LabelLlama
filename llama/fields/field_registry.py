from typing import Any

from llama.fields.dwc.abundance import Abundance
from llama.fields.dwc.associated_taxa import AssociatedTaxa
from llama.fields.dwc.collector import Collector
from llama.fields.dwc.collector_number import CollectorNumber
from llama.fields.dwc.country import Country
from llama.fields.dwc.county import County
from llama.fields.dwc.date_identified import DateIdentified
from llama.fields.dwc.elevation import Elevation
from llama.fields.dwc.event_date import EventDate
from llama.fields.dwc.family import Family
from llama.fields.dwc.geodetic_datum import GeodeticDatum
from llama.fields.dwc.habitat import Habitat
from llama.fields.dwc.identified_by import IdentifiedBy
from llama.fields.dwc.infraspecific_epithet import InfraspecificEpithet
from llama.fields.dwc.infraspecific_name_authorship import (
    InfraspecificNameAuthorship,
)
from llama.fields.dwc.latitude import Latitude
from llama.fields.dwc.locality import Locality
from llama.fields.dwc.longitude import Longitude
from llama.fields.dwc.municipality import Municipality
from llama.fields.dwc.occurrence_remarks import OccurrenceRemarks
from llama.fields.dwc.scientific_name import ScientificName
from llama.fields.dwc.scientific_name_authorship import ScientificNameAuthorship
from llama.fields.dwc.state_province import StateProvince
from llama.fields.dwc.trs import Trs
from llama.fields.dwc.utm import Utm
from llama.fields.plants.flower_color import FlowerColor
from llama.fields.plants.flower_present import FlowersPresent
from llama.fields.plants.fruit_color import FruitColor
from llama.fields.plants.fruit_present import FruitPresent
from llama.fields.plants.habit import Habit
from llama.fields.plants.leaf_margin import LeafMargin
from llama.fields.plants.leaf_shape import LeafShape
from llama.fields.plants.plant_height import PlantHeight
from llama.fields.plants.sizes import Sizes

# This also is the base order of fields in reports
FIELD_REGISTRY: dict[str, Any] = {
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
    "plantSize": Sizes,
    "habit": Habit,
    "leafShape": LeafShape,
    "leafMargin": LeafMargin,
}
