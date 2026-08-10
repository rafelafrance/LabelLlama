import unittest
from textwrap import dedent

from llama.parser_utils.parser_cleaner import ParserCleaner


class TestParserUtil(unittest.TestCase):
    # ---------------------------------------------------------------------
    def test_llm_reply_to_dict_01(self) -> None:
        columns = [
            "identifiedBy",
            "identifiedByID",
            "locality",
            "country",
            "stateProvince",
            "county",
            "municipality",
            "waterBody",
            "habitat",
            "occurrenceRemarks",
        ]
        text = dedent("""
            << ## identifiedBy ##
            S. W. Dunkle

            << ## identifiedByID ##

            << ## dateIdentified ##

            << ## locality ##
            ITALY: REGIONE LAZIO Mignone River @ Verginese Stream, near Castle Rota 14 m

            << ## country ##
            Italy

            << ## stateProvince ##
            REGIONE LAZIO

            << ## county ##

            << ## municipality ##

            << ## waterBody ##
            Mignone River @ Verginese Stream

            << ## habitat ##

            << ## occurrenceRemarks ##""")
        # Yes, the parse is iffy, but I'm testing the split itself
        expect = {
            "identifiedBy": "S. W. Dunkle",
            "identifiedByID": "",
            "locality": (
                "ITALY: REGIONE LAZIO Mignone River @ Verginese Stream, near "
                "Castle Rota 14 m"
            ),
            "country": "Italy",
            "stateProvince": "REGIONE LAZIO",
            "county": "",
            "municipality": "",
            "waterBody": "Mignone River @ Verginese Stream",
            "habitat": "",
            "occurrenceRemarks": "",
        }
        actual = ParserCleaner.llm_reply_to_dict(text, columns)
        assert actual == expect
