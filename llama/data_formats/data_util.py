from copy import copy


def lift_annotations(labels: list[dict]) -> list[dict]:
    """
    Lift annotations to the same level as other fields for CSV output.

    Note that this also collapses single items value lists into a single item.
    """
    news = []
    for lb in labels:
        for key, values in lb["annotations"].items():
            vals = [v for v in values if v]
            if len(vals) == 0:
                lb["annotations"][key] = ""
            elif len(vals) == 1:
                lb["annotations"][key] = vals[0]
            else:
                lb["annotations"][key] = vals

        lb |= copy(lb["annotations"])
        del lb["annotations"]

        from pprint import pp

        pp(lb)

        news.append(lb)
    return news
