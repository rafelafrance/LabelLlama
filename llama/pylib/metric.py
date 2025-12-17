import dspy
import Levenshtein


def metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    score: float = 0.0
    for field in example.labels():
        true: str = " ".join(example[field])
        pred: str = " ".join(prediction[field])
        score += Levenshtein.ratio(true, pred)
    score /= len(example.labels())
    return score
