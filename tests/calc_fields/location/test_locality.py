import unittest

from llama.calc_fields.location.locality import Locality


class TestLocality(unittest.TestCase):
    def test_locality_01(self) -> None:
        actual = """UNITED STATES: Texas, Cameron . Pond near canal off CR 800"""
        expect = """Pond near canal off CR 800"""
        record = {
            "locality": actual,
            "country": "United States",
            "stateProvince": "Texas",
            "county": "Cameron",
        }
        assert Locality(record, actual).locality == expect
