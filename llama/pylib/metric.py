import dspy
import Levenshtein


def metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    score: float = 0.0
    for field in example.labels():
        true = " ".join(example[field])
        pred = " ".join(prediction[field])
        score += Levenshtein.ratio(true, pred)
    return score
