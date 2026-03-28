from typing import Any


def to_args(*args: str, **kwargs: Any) -> list[str]:
    """
    Simplify adding arguments to script calls in a notebook.

    Function arguments are easier to work with than twitchy strings.
    Yes, it's a brutal hack.
    """
    args_out = []

    args_out += [f"--{a.replace('_', '-')}" for a in args]

    for key, value in kwargs.items():
        args_out.append(f"--{key.replace('_', '-')}")
        args_out.append(str(value))

    return args_out
