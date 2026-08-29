from llama.calc_fields.event.eventDate import EventDate
from llama.llm_fields.event.habitat import Habitat
from llama.llm_fields.event.verbatimEventDate import VerbatimEventDate
from llama.llm_fields.identification.dateIdentified import DateIdentified
from llama.llm_fields.insects.lifeStage import LifeStage as InsectLifeStage
from llama.llm_fields.location.country import Country
from llama.llm_fields.location.county import County
from llama.llm_fields.location.decimalLatitude import DecimalLatitude
from llama.llm_fields.location.decimalLongitude import DecimalLongitude
from llama.llm_fields.location.trsQuad import TrsQuad
from llama.llm_fields.location.trsSection import TrsSection
from llama.llm_fields.location.utmEasting import UtmEasting
from llama.llm_fields.location.utmNorthing import UtmNorthing
from llama.llm_fields.location.utmZone import UtmZone
from llama.llm_fields.occurrence.associatedTaxa import AssociatedTaxa
from llama.llm_fields.occurrence.recordedBy import RecordedBy
from llama.llm_fields.occurrence.recordNumber import RecordNumber
from llama.llm_fields.occurrence.sex import Sex
from llama.llm_fields.taxon.genus import Genus
from llama.llm_fields.taxon.scientificName import ScientificName
from llama.llm_fields.taxon.specificEpithet import SpecificEpithet


def test_scientific_name_keeps_only_genus_and_species() -> None:
    field = ScientificName(scientificName="LIBELLULA LUCTUOSA (Burmeister, 1839)")
    assert field.scientificName == "Libellula luctuosa"


def test_genus_and_specific_epithet_normalize_case() -> None:
    assert Genus(genus="salix").genus == "Salix"
    assert SpecificEpithet(specificEpithet="ALBA").specificEpithet == "alba"


def test_sex_symbols_and_pair_are_normalized() -> None:
    assert Sex(sex="♂").sex == "male"
    assert Sex(sex="♀").sex == "female"
    assert Sex(sex="pair").sex == "male & female"


def test_decimal_coordinates_keep_numbers_and_clear_invalid_values() -> None:
    assert DecimalLatitude(decimalLatitude="45.5").decimalLatitude == 45.5
    assert DecimalLatitude(decimalLatitude="not a coordinate").decimalLatitude == ""
    assert DecimalLongitude(decimalLongitude="-120.25").decimalLongitude == -120.25
    assert DecimalLongitude(decimalLongitude="not a coordinate").decimalLongitude == ""


def test_common_label_prefixes_are_removed() -> None:
    assert RecordNumber(recordNumber="No. 123").recordNumber == "123"
    assert Habitat(habitat="Habitat: sphagnum bog").habitat == "sphagnum bog"
    assert VerbatimEventDate(verbatimEventDate="Date: 1999-05-01").verbatimEventDate
    assert DateIdentified(dateIdentified="date: 2020").dateIdentified == "2020"


def test_county_suffix_is_removed() -> None:
    assert County(county="Orange Co.").county == "Orange"
    assert County(county="Yolo County").county == "Yolo"


def test_associated_taxa_removes_markers_and_trailing_punctuation() -> None:
    field = AssociatedTaxa(associatedTaxa="*Quercus alba.")
    assert field.associatedTaxa == "Quercus alba"


def test_hallucinated_values_are_cleared_when_source_text_is_available() -> None:
    field = InsectLifeStage("adult label text", lifeStage="larva")
    assert field.lifeStage == ""


def test_hallucinated_values_are_kept_without_source_text() -> None:
    field = InsectLifeStage(lifeStage="larva")
    assert field.lifeStage == "larva"


def test_verbatim_event_date_keeps_range_separator_for_event_date() -> None:
    field = VerbatimEventDate(verbatimEventDate="May 12 1999|June 1 1999")
    assert field.verbatimEventDate == "May 12 1999|June 1 1999"
    calc = EventDate({"verbatimEventDate": field.verbatimEventDate})
    assert calc.eventDate == "1999-05-12 to 1999-06-01"


def test_country_clears_llm_empty_notations() -> None:
    assert Country(country="None").country == ""
    assert Country(country="nan").country == ""
    assert Country(country="''").country == ""
    assert Country(country="(blank)").country == ""
    assert Country(country="[United States]").country == "United States"
    assert (
        Country(country="united states of america").country
        == "United States of America"
    )


def test_decimal_coordinates_reject_out_of_range_values() -> None:
    assert DecimalLatitude(decimalLatitude="95.0").decimalLatitude == ""
    assert DecimalLatitude(decimalLatitude="-95.0").decimalLatitude == ""
    assert DecimalLongitude(decimalLongitude="200.0").decimalLongitude == ""
    assert DecimalLatitude(decimalLatitude="45.5").decimalLatitude == 45.5
    assert DecimalLongitude(decimalLongitude="-120.25").decimalLongitude == -120.25


def test_collector_label_is_removed_regardless_of_case() -> None:
    assert RecordedBy(recordedBy="Coll. J. Smith 45").recordedBy == "J. Smith 45"
    assert RecordedBy(recordedBy="Collector: J. Smith").recordedBy == "J. Smith"
    assert (
        RecordedBy(recordedBy="Collins J. Smith 45").recordedBy == "Collins J. Smith 45"
    )


def test_trs_section_label_is_removed_regardless_of_case() -> None:
    assert TrsSection(trsSection="Sec 12").trsSection == "12"
    assert TrsSection(trsSection="S. 12").trsSection == "12"
    assert TrsSection(trsSection="NE1/4, Sec 12").trsSection == "NE1/4, 12"
    assert TrsSection(trsSection="NE1/4").trsSection == "NE1/4"


def test_trs_quad_label_is_removed_regardless_of_case() -> None:
    assert TrsQuad(trsQuad="Quad 5").trsQuad == "5"
    assert TrsQuad(trsQuad="quad 5").trsQuad == "5"


def test_utm_zone_label_is_removed_regardless_of_case() -> None:
    assert UtmZone(utmZone="Zone 10S").utmZone == "10S"
    assert UtmZone(utmZone="Z 10S").utmZone == "10S"
    assert UtmZone(utmZone="10S").utmZone == "10S"


def test_utm_hemisphere_marker_is_stripped() -> None:
    assert UtmEasting(utmEasting="123456 E").utmEasting == "123456"
    assert UtmEasting(utmEasting="123456E").utmEasting == "123456"
    assert UtmNorthing(utmNorthing="4567890 N").utmNorthing == "4567890"
    assert UtmNorthing(utmNorthing="4567890").utmNorthing == "4567890"
    assert UtmEasting(utmEasting="0").utmEasting == ""
