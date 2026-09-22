import unittest

from llama.llm_fields.location.trsQuad import TrsQuad


class TestTrsQuad(unittest.TestCase):
    def test_trs_quad_01(self) -> None:
        """The "quad" label is removed."""
        assert TrsQuad("", "quad 12").trsQuad == "12"

    def test_trs_quad_02(self) -> None:
        """Inflected forms of the label are removed."""
        assert TrsQuad("", "quadrangle 5").trsQuad == "5"

    def test_trs_quad_03(self) -> None:
        """The "q" label is removed."""
        assert TrsQuad("", "q 7").trsQuad == "7"

    def test_trs_quad_04(self) -> None:
        """A value without a label is unchanged."""
        assert TrsQuad("", "12").trsQuad == "12"

    def test_trs_quad_05(self) -> None:
        """Empty inputs and empty-value notations stay empty."""
        assert TrsQuad("", "").trsQuad == ""
        assert TrsQuad("", "none").trsQuad == ""

    def test_trs_quad_10(self) -> None:
        """The regex is case insensitive."""
        assert TrsQuad("", "Quad 12").trsQuad == "12"

    def test_trs_quad_11(self) -> None:
        """The 'q.' abbreviation with its dot is removed."""
        assert TrsQuad("", "q. 7").trsQuad == "7"

    def test_trs_quad_12(self) -> None:
        """A value that only starts like a label is kept."""
        assert TrsQuad("", "Quail Creek").trsQuad == "Quail Creek"
