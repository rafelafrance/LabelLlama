import unittest
from textwrap import dedent

from llama.lm import preprocess


class TestPreprocess(unittest.TestCase):
    # ---------------------------------------------------------------------
    def test_clean_text_01(self) -> None:
        text = dedent("""
            HERBARIUM
            F. H. SARGENT
            Paspalum urvillei Steud.
            Locality
            Picayune, Miss.
            Habitat
            Waste ground.
            Date
            May 29, 1966.
            """)
        expect = " ".join(
            """
            F. H. SARGENT Paspalum urvillei Steud. Locality Picayune, Miss.
            Habitat Waste ground. Date May 29, 1966.
            """.split()
        )
        actual = preprocess.clean_text(text)
        self.assertEqual(actual, expect)
