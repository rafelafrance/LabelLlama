import re

ABOUT_TERMS = r"(?: +- | -+ | \b about \b | \b approx \b | \b approximate \b "
ABOUT_TERMS += r" | \b ca \b | ± )"

ABOUT_RE = re.compile(ABOUT_TERMS, flags=re.IGNORECASE | re.VERBOSE)


def is_about(value: str) -> bool:
    return bool(ABOUT_RE.search(value))
