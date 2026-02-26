import unittest

from llama.traiter.rules.elevation import Elevation
from tests.setup import parse


class TestElevation(unittest.TestCase):
    def test_elevation_01(self) -> None:
        """It handles metric units."""
        self.assertEqual(
            parse(""" Elevation: 1463m """),
            [Elevation(elevation=1463.0, units="m")],
        )

    def test_elevation_02(self) -> None:
        """It handles a measurement in different units."""
        self.assertEqual(
            parse(""" Elev: 782m. (2566 ft) """),
            [Elevation(elevation=782.0, units="m")],
        )

    def test_elevation_03(self) -> None:
        """It handles a range."""
        traits = parse(""" Elev. 9,500-9640 ft. """)
        self.assertEqual(traits[0].units, "m")
        self.assertAlmostEqual(traits[0].elevation, 2895.6)
        self.assertAlmostEqual(traits[0].elevation_high, 2938.272)

    def test_elevation_04(self) -> None:
        self.assertEqual(
            parse(""" alt., 250 m. """),
            [Elevation(elevation=250.0, units="m")],
        )

    def test_elevation_05(self) -> None:
        self.assertEqual(
            parse("""Alto.: 834m/2735ft."""),
            [Elevation(elevation=834.0, units="m")],
        )

    def test_elevation_06(self) -> None:
        self.assertEqual(
            parse("""Elev. ca, 200 m."""),
            [
                Elevation(elevation=200.0, units="m", about=True),
            ],
        )

    def test_elevation_07(self) -> None:
        self.assertEqual(
            parse("""975m/3200ft"""),
            [Elevation(elevation=975.0, units="m")],
        )

    def test_elevation_08(self) -> None:
        traits = parse("""Elev. ca. 460 - 470 ft""")
        self.assertEqual(traits[0].units, "m")
        self.assertAlmostEqual(traits[0].elevation, 140.208)
        self.assertAlmostEqual(traits[0].elevation_high, 143.256)

    def test_elevation_09(self) -> None:
        self.assertEqual(
            parse("""elev: 737m. (2417 ft.)"""),
            [Elevation(elevation=737.0, units="m")],
        )

    def test_elevation_10(self) -> None:
        self.assertEqual(
            parse(
                """Elev.
                1400- 1500 m.
                """,
            ),
            [Elevation(elevation=1400.0, elevation_high=1500.0, units="m")],
        )

    def test_elevation_11(self) -> None:
        self.assertEqual(
            parse("""Elev 85’."""),
            [Elevation(elevation=25.908, units="m")],
        )

    def test_elevation_12(self) -> None:
        self.assertEqual(
            parse("""120 ft. elev. (35 m) ±40 ft."""),
            [
                Elevation(elevation=36.576, units="m", about=True),
                Elevation(elevation=12.192, units="m"),
            ],
        )
