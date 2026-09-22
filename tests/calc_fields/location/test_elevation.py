import unittest

from llama.calc_fields.location.elevation import Elevation


def make_elevation(verbatim: str) -> Elevation:
    return Elevation({"verbatimElevation": verbatim}, "")


class TestElevation(unittest.TestCase):
    def test_elevation_01(self) -> None:
        """A metric elevation keeps its value and unit."""
        e = make_elevation("100 m")
        assert e.elevation == 100.0
        assert e.minimumElevationInMeters == 100.0
        assert e.maximumElevationInMeters == ""
        assert e.elevationUnits == "m"
        assert e.elevationEstimated is False

    def test_elevation_02(self) -> None:
        """An imperial elevation also gains a metres value."""
        e = make_elevation("3000 ft")
        assert e.elevation == 3000.0
        self.assertAlmostEqual(e.minimumElevationInMeters, 914.4)
        assert e.maximumElevationInMeters == ""
        assert e.elevationUnits == "ft"

    def test_elevation_03(self) -> None:
        """The word "about" marks the elevation as estimated."""
        assert make_elevation("about 100 m").elevationEstimated is True
        assert make_elevation("100 m").elevationEstimated is False

    def test_elevation_04(self) -> None:
        """Mixed units keep only the metric reading."""
        e = make_elevation("100 m 1000 ft")
        assert e.minimumElevationInMeters == 100.0
        assert e.maximumElevationInMeters == ""
        assert e.elevationUnits == "m"

    def test_elevation_05(self) -> None:
        """An elevation without a unit yields no values."""
        e = make_elevation("100")
        assert e.elevation == ""
        assert e.minimumElevationInMeters == ""
        assert e.maximumElevationInMeters == ""
        assert e.elevationUnits == ""
        assert e.elevationEstimated == ""

    def test_elevation_06(self) -> None:
        """An empty elevation yields no values."""
        e = make_elevation("")
        assert e.elevation == ""
        assert e.elevationUnits == ""

    def test_elevation_07(self) -> None:
        """A range gives the low and high values in metres."""
        e = make_elevation("100-200 m")
        assert e.elevation == 100.0
        assert e.minimumElevationInMeters == 100.0
        assert e.maximumElevationInMeters == 200.0

    def test_elevation_08(self) -> None:
        """Meters must come after miles in the vocab/terms/unit_terms.csv."""
        e = make_elevation("100 mi")
        self.assertAlmostEqual(e.minimumElevationInMeters, 160934.4)
        assert e.elevationUnits == "mi"

    def test_elevation_09(self) -> None:
        """Meters must come after millimeters in the vocab/terms/unit_terms.csv."""
        e = make_elevation("100 mm")
        self.assertAlmostEqual(e.minimumElevationInMeters, 0.1)
        assert e.elevationUnits == "mm"


if __name__ == "__main__":
    unittest.main()
