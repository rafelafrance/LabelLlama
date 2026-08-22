from llama.calc_fields.event.eventDate import EventDate
from llama.calc_fields.location.country import Country
from llama.calc_fields.location.elevation import Elevation
from llama.calc_fields.location.locality import Locality
from llama.calc_fields.plants.flowersPresent import FlowersPresent
from llama.calc_fields.plants.fruitPresent import FruitPresent
from llama.calc_fields.taxon.family import Family
from llama.calc_fields.taxon.genus import Genus
from llama.calc_fields.taxon.specificEpithet import SpecificEpithet


def test_event_date_is_calculated_from_verbatim_event_date() -> None:
    field = EventDate(cleaned_rec={"verbatimEventDate": "Jan 30, 1922"})
    assert field.eventDate == "1922-01-30"


def test_event_date_handles_date_ranges() -> None:
    field = EventDate(cleaned_rec={"verbatimEventDate": "Jan 1922|Feb 1922"})
    assert field.eventDate == "1922-01 to 1922-02"


def test_country_is_inferred_from_us_state_when_blank() -> None:
    field = Country(cleaned_rec={"stateProvince": "Texas"})
    assert field.country == "United States"


def test_country_is_inferred_from_us_county_when_blank() -> None:
    field = Country(cleaned_rec={"county": "Yolo"})
    assert field.country == "United States"


def test_country_normalizes_usa_variants() -> None:
    field = Country(country="usa", cleaned_rec={})
    assert field.country == "USA"


def test_locality_removes_higher_geography() -> None:
    field = Locality(
        locality="UNITED STATES: Texas, Cameron Co., pond near canal",
        cleaned_rec={
            "country": "United States",
            "stateProvince": "Texas",
            "county": "Cameron",
        },
    )
    assert field.locality == "pond near canal"


def test_empty_elevation_clears_all_elevation_outputs() -> None:
    field = Elevation(cleaned_rec={})
    assert field.elevation == ""
    assert field.minimumElevationInMeters == ""
    assert field.maximumElevationInMeters == ""
    assert field.elevationUnits == ""
    assert field.elevationEstimated == ""


def test_flowers_present_is_calculated_from_flower_color() -> None:
    field = FlowersPresent(cleaned_rec={"flowerColor": "yellow"})
    assert field.flowersPresent is True


def test_flowers_present_stays_blank_without_flower_evidence() -> None:
    field = FlowersPresent(cleaned_rec={})
    assert field.flowersPresent == ""


def test_fruit_present_is_calculated_from_fruit_facts() -> None:
    field = FruitPresent(cleaned_rec={"fruitFacts": "achenes mature"})
    assert field.fruitPresent is True


def test_fruit_present_stays_blank_without_fruit_evidence() -> None:
    field = FruitPresent(cleaned_rec={})
    assert field.fruitPresent == ""


def test_genus_is_calculated_from_scientific_name() -> None:
    field = Genus(cleaned_rec={"scientificName": "salix alba"})
    assert field.genus == "Salix"


def test_genus_preserves_existing_value() -> None:
    field = Genus(genus="Populus", cleaned_rec={"scientificName": "Salix alba"})
    assert field.genus == "Populus"


def test_specific_epithet_is_calculated_from_scientific_name() -> None:
    field = SpecificEpithet(cleaned_rec={"scientificName": "Salix ALBA"})
    assert field.specificEpithet == "alba"


def test_specific_epithet_preserves_existing_value() -> None:
    field = SpecificEpithet(
        specificEpithet="nigra",
        cleaned_rec={"scientificName": "Salix alba"},
    )
    assert field.specificEpithet == "nigra"


def test_family_is_calculated_from_scientific_name_genus() -> None:
    field = Family(cleaned_rec={"scientificName": "Salix alba"})
    assert field.family == "Salicaceae"


def test_family_preserves_existing_value() -> None:
    field = Family(
        family="Existingaceae",
        cleaned_rec={"scientificName": "Salix alba"},
    )
    assert field.family == "Existingaceae"
