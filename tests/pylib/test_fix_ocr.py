from textwrap import dedent

from llama.pylib import fix_ocr


# ---------------------------------------------------------------------
def test_clean_text_01() -> None:
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
    expect = (
        "F. H. SARGENT Paspalum urvillei Steud. Locality Picayune, Miss. "
        "Habitat Waste ground. Date May 29, 1966."
    )
    actual = fix_ocr.prepare_for_parse(text)
    assert actual == expect


# ---------------------------------------------------------------------
def test_remove_identical_lines_01() -> None:
    text = "line 1\nline 2\nline 2\nline 3\n"
    expect = "line 1\nline 2\nline 3"
    actual = fix_ocr.remove_identical_lines(text)
    assert actual == expect


def test_remove_identical_lines_02() -> None:
    text = "line 1\nline 2\nline 1\nline 3\n"
    expect = "line 1\nline 2\nline 3"
    actual = fix_ocr.remove_identical_lines(text)
    assert actual == expect


def test_remove_identical_lines_03() -> None:
    text = "line 1\n \nline 2\n\nline 1\n\nline 3\n"
    expect = "line 1\n\nline 2\n\n\nline 3"
    actual = fix_ocr.remove_identical_lines(text)
    assert actual == expect


# ---------------------------------------------------------------------
def test_join_lines_01() -> None:
    # Single breaks become spaces; two-or-more breaks stay as a blank line.
    assert fix_ocr.join_lines("a b\nc d\n\ne f") == "a b c d\n\ne f"


def test_join_lines_02() -> None:
    # A run of three breaks collapses to a single blank line.
    assert fix_ocr.join_lines("a\n\n\nb") == "a\n\nb"


def test_join_lines_03() -> None:
    # A literal "<br>" in the text is content, not a break sentinel.
    assert fix_ocr.join_lines("real <br> text\nline2") == "real <br> text line2"


# ---------------------------------------------------------------------
def test_fix_entities_01() -> None:
    assert fix_ocr.fix_entities("a<br/>b") == "a\nb"


def test_fix_entities_02() -> None:
    assert fix_ocr.fix_entities("a<br />b") == "a\nb"


def test_fix_entities_03() -> None:
    assert fix_ocr.fix_entities("a<br >b") == "a\nb"


def test_fix_entities_04() -> None:
    assert fix_ocr.fix_entities("&lt;tag&gt; &amp;") == "<tag> &"


def test_fix_entities_05() -> None:
    # Entities beyond lt/gt/amp are decoded too.
    assert fix_ocr.fix_entities('say &quot;hi&quot;') == 'say "hi"'


def test_fix_entities_06() -> None:
    assert fix_ocr.fix_entities("it&#39;s") == "it's"


def test_fix_entities_07() -> None:
    # A non-breaking space becomes a regular space.
    assert fix_ocr.fix_entities("say&nbsp;hello") == "say hello"


def test_fix_entities_08() -> None:
    # Double-encoding is unwrapped only one level.
    assert fix_ocr.fix_entities("&amp;lt;") == "&lt;"


def test_fix_entities_09() -> None:
    # A bare ampersand that is not an entity is left alone.
    assert fix_ocr.fix_entities("AT&T stock") == "AT&T stock"


# ---------------------------------------------------------------------
def test_html_to_md_01() -> None:
    assert fix_ocr.html_to_md("<b>don't</b>") == "don't"


def test_html_to_md_02() -> None:
    assert fix_ocr.html_to_md("<b>hello, world!</b>") == "hello, world!"


def test_html_to_md_03() -> None:
    assert fix_ocr.html_to_md("<i>text</i>") == "text"


def test_html_to_md_04() -> None:
    # snake_case tokens are not mangled by the emphasis-stripping regex.
    assert (
        fix_ocr.html_to_md("gene BRCA_1 and my_file_name here")
        == "gene BRCA_1 and my_file_name here"
    )


def test_html_to_md_05() -> None:
    # Arithmetic with asterisks is left intact.
    assert fix_ocr.html_to_md("2 * 3 * 4") == "2 * 3 * 4"


# ---------------------------------------------------------------------
def test_setup_filter_pattern_01() -> None:
    pattern = fix_ocr.setup_filter_pattern(("database",))
    assert pattern.search("big database") is not None
    assert pattern.search("big data") is None


def test_filter_lines_custom_pattern_01() -> None:
    pattern = fix_ocr.setup_filter_pattern(("database",))
    assert fix_ocr.filter_lines("keep\ndatabase line", pattern=pattern) == "keep"


def test_filter_lines_default_01() -> None:
    assert fix_ocr.filter_lines("keep\nSciences dept\nhere") == "keep\nhere"
