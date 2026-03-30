def elevation(units: str) -> str:
    lc = units.lower()
    match lc:
        case lc if lc.startswith("f"):
            return "ft"
        case lc if lc.startswith("m"):
            return "m"
        case _:
            return units
