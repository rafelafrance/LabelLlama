from typing import Any

import dspy
import Levenshtein


class Metric:
    def __init__(self, output_fields: list[str]) -> None:
        self.output_fields: list[str] = output_fields
        self.count: int = 0
        self.field_totals: dict[str, float] = dict.fromkeys(output_fields, 0.0)
        self.averages: dict[str, float] = dict.fromkeys(output_fields, 0.0)

    def score(
        self, expected: dict[str, list[str]], actual: dict[str, list[str]]
    ) -> float:
        self.count += 1
        score: float = 0.0
        for field in self.output_fields:
            true: str = " ".join(expected[field])
            pred: str = " ".join(actual[field])
            score += Levenshtein.ratio(true, pred)
            self.field_totals[field] += score
        score /= len(self.output_fields)
        return score

    def average(self) -> float:
        grand: float = 0.0
        for field in self.output_fields:
            self.averages[field] = self.field_totals[field] / self.count
            grand += self.averages[field]

        grand /= len(self.output_fields)

        return grand


def metric(
    example: dspy.Example, prediction: dspy.Prediction, _trace: Any = None
) -> float:
    score: float = 0.0
    for field in example.labels():
        true: str = " ".join(example[field])
        pred: str = " ".join(prediction[field])
        score += Levenshtein.ratio(true, pred)
    score /= len(example.labels())
    return score


def feedback_metric(
    example: dspy.Example,
    prediction: dspy.Prediction,
    _trace: Any = None,
    _pred_name: Any = None,
    _pred_trace: Any = None,
) -> dspy.Prediction:
    score: float = 0.0
    feedback = "Feedback for specimen:\n"

    for field in example.labels():
        true: str = " ".join(example[field])
        pred: str = " ".join(prediction[field])

        dist: float = Levenshtein.ratio(true, pred)
        score += dist

        if dist == 0.0 and true == "":
            feedback += f"  ✅ {field}: was correctly left blank\n"
        elif dist == 0.0:
            feedback += f"  ✅ {field}: correctly identified as {example[field]!r}\n"
        elif true == "":
            feedback += (
                f"  ❌ {field}: the field should have been blank, "
                f"but you predicted {prediction[field]!r}\n"
            )
        elif pred == "":
            feedback += (
                f"  ❌ {field}: you should have predicted {example[field]!r}, "
                "but you completely missed it\n"
            )
        else:
            feedback += (
                f"  ❌ {field}: expected {example[field]!r}, "
                f"but you predicted {prediction[field]!r}\n"
            )

    return dspy.Prediction(score=score, feedback=feedback)
