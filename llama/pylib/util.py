EXACT = 1.0  # Scores equaling this are blue
HAPPY = 0.9  # Scores above this are green
OK = 0.75  # Scores below this are red


def score_color(score: float) -> str:
    if score >= 1.0:
        return "blue"
    if score >= HAPPY:
        return "green"
    if score >= OK:
        return "yellow"
    return "red"
