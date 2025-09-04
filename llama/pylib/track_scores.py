from dataclasses import dataclass, field, make_dataclass

import dspy
import Levenshtein
from rich import print as rprint

from llama.model_data.herbarium_label import DWC, OUTPUT_FIELDS

Traits = make_dataclass(
    "Traits",
    [(f, str, field(default="")) for f in OUTPUT_FIELDS],
)

TraitScores = make_dataclass(
    "TraitScores",
    [(f, float, field(default=0.0)) for f in OUTPUT_FIELDS],
)


@dataclass
class TrackScores:
    total_score: float = 0.0
    trues: Traits = field(default_factory=Traits)  # type: ignore [reportGeneralTypeIssues]
    preds: Traits = field(default_factory=Traits)  # type: ignore [reportGeneralTypeIssues]
    scores: TraitScores = field(default_factory=TraitScores)  # type: ignore [reportGeneralTypeIssues]

    @classmethod
    def track_scores(
        cls, *, example: dspy.Example, prediction: dspy.Prediction
    ) -> "TrackScores":
        """Save the score results for each trait field."""
        score = cls()

        for fld in OUTPUT_FIELDS:
            true = getattr(example, fld)
            pred = getattr(prediction, fld)

            setattr(score.trues, fld, true)
            setattr(score.preds, fld, pred)

            true = " ".join(true)
            pred = " ".join(pred)

            value = Levenshtein.ratio(true, pred)
            setattr(score.scores, fld, value)
            score.total_score += value

        score.total_score /= len(OUTPUT_FIELDS)

        return score

    def display(self) -> None:
        for fld in OUTPUT_FIELDS:
            true = getattr(self.trues, fld)
            pred = getattr(self.preds, fld)

            true = " ".join(true)
            pred = " ".join(pred)

            true_folded = true.casefold()
            pred_folded = pred.casefold()
            dwc = DWC[fld]
            if true_folded == pred_folded:
                rprint(f"[green]{dwc:<28} {true}")
            else:
                rprint(f"[red]{dwc:<28} {true} [/red]!= [yellow]{pred}")
        rprint(f"[blue]Score = {(self.total_score * 100.0):6.2f}")

    @staticmethod
    def summarize_scores(scores: list) -> None:
        rprint("\n[blue]Score summary\n")
        count = float(len(scores))
        for fld in OUTPUT_FIELDS:
            dwc = DWC[fld]
            score: float = sum(s["scores"][fld] for s in scores)
            rprint(f"[blue]{dwc:<28} {score / count * 100.0:6.2f}")
        total_score = sum(s["total_score"] for s in scores) / count * 100.0
        rprint(f"\n[blue]{'Total Score':<28} {total_score:6.2f}\n")
