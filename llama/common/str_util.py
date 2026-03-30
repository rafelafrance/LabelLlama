def compress(text: str) -> str:
    return " ".join(text.split())


def dedent(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln]
    return "\n".join(lines)
