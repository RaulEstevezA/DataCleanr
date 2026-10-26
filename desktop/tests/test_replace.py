import pytest

from datacleanr.core.replace import ReplaceOptions, create_replace_transform

from .conftest import load_cases

CASES = load_cases("replace.json")


@pytest.mark.parametrize("case", CASES, ids=[case["description"] for case in CASES])
def test_shared_cases(case):
    options = case["options"]
    transform = create_replace_transform(
        ReplaceOptions(
            find=options["find"],
            replacement=options["replacement"],
            whole_cell=options["wholeCell"],
            ignore_case=options["ignoreCase"],
        )
    )
    assert transform(case["input"]) == case["expected"]


def test_backslashes_in_replacement_are_literal():
    transform = create_replace_transform(ReplaceOptions("a", r"\1\n", whole_cell=False, ignore_case=False))
    assert transform("xa") == r"x\1\n"
