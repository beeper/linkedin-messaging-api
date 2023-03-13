#! /usr/bin/env python

"""
Checks for TODO comments and makes sure they have an associated issue. Formats that are
accepted are:

TODO (#1)
TODO (#1)
TODO (project#1)
TODO (namespace/project#1)
TODO (namespace/namespace/project#1)

Additionally, the TODO can be postfixed with ``:``.
"""

import re
import sys
from pathlib import Path
from typing import Pattern

from termcolor import cprint

todo_re = re.compile(r"\s*#\s*TODO:?\s*")
accounted_for_todo = re.compile(r"\s*#\s*TODO:?\s*\(([\w-]+(/[\w-]+)*)?#\d+\)")


def noqa_re(error_id: str = "") -> Pattern:
    return re.compile(rf"#\s*noqa(:\s*{error_id})?\s*\n$")


def eprint(*strings: str):
    cprint(" ".join(strings), "red", end="", attrs=["bold"])


def check_file(path: Path) -> bool:
    print(f"Checking {path.absolute()}...")  # noqa: T001
    file = path.open()
    valid = True

    for i, line in enumerate(file, start=1):
        if todo_re.match(line) and not accounted_for_todo.match(line):
            eprint(f"{i}: {line}")
            valid = False

    file.close()
    return valid


valid = True
for path in sys.argv[1:]:
    if path.endswith(".py"):
        valid &= check_file(Path(path).absolute())

if "CHANGELOG.md" in sys.argv:
    """
    Checks that the version in the CHANGELOG is the same as the version in ``__init__.py``.
    """
    print("Checking version in CHANGELOG is the same as version in __init__")  # noqa: T001
    with open(Path("linkedin_messaging/__init__.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                version = eval(line.split()[-1])
                break
        else:  # nobreak
            raise AssertionError("No version in linkedin_messaging/__init__.py")

    with open(Path("CHANGELOG.md")) as f:
        assert f.readline().strip() == f"# v{version}", "Version mismatch: CHANGELOG"

sys.exit(0 if valid else 1)
