import pytest

from datacleanr.core.transforms import TRANSFORMS

from .conftest import load_cases

CASES = load_cases("transforms.json")


@pytest.mark.parametrize(
    ("transform_id", "case"),
    [(transform_id, case) for transform_id, cases in CASES.items() for case in cases],
    ids=lambda value: value["description"] if isinstance(value, dict) else value,
)
def test_shared_cases(transform_id, case):
    assert TRANSFORMS[transform_id](case["input"]) == case["expected"]


def test_every_transform_has_shared_cases():
    assert sorted(CASES) == sorted(TRANSFORMS)
