from typing import Any

# @dataclass
# class CliArgs:
#     @classmethod
#     def from_command_line(cls: CliArgs) -> CliArgs:
#         parser = argparse.ArgumentParser()
#
#         for f in fields(cls):
#             arg_name = f"--{f.name.replace('_', '-')}"
#             if f.type is bool:
#                 parser.add_argument(arg_name, action="store_true")
#             else:
#                 parser.add_argument(arg_name, type=f.type, default=f.default)
#
#         args = parser.parse_args()
#         return cls(**vars(args))


def to_args(func: Any, *args: list[Any], **kwargs: Any) -> list[str]:
    """
    Simplify adding arguments to script calls in a notebook.

    Function arguments are easier to work with than twitchy strings.
    Yes, it's a brutal hack.
    """
    args_out = []

    if func:
        args_out.append(func)

    args_out += [f"--{a.replace('_', '-')}" for a in args]

    for key, value in kwargs.items():
        args_out.append(f"--{key.replace('_', '-')}")
        args_out.append(str(value))

    return args_out
