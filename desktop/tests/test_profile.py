import json

import pytest

from datacleanr.core.dataset import Dataset
from datacleanr.core.profile import ProfileError, parse_profile, run_profile, serialize_profile

from .conftest import load_cases

CASES = load_cases("profile.json")


@pytest.mark.parametrize("case", CASES["run"], ids=[c["description"] for c in CASES["run"]])
def test_run(case):
    dataset = Dataset("a.csv", "csv", case["columns"], case["rows"], list(range(len(case["rows"]))), delimiter=";")
    results = run_profile(dataset, parse_profile(json.dumps(case["profile"])))
    summary = [
        {"status": r.status, "reason": r.reason, "count": r.count}
        if r.reason
        else {"status": r.status, "count": r.count}
        for r in results
    ]
    assert summary == case["expected"]["steps"]
    assert results[-1].dataset.rows == case["expected"]["rows"]
    assert results[-1].dataset.row_ids == case["expected"]["rowIds"]


@pytest.mark.parametrize("case", CASES["invalid"], ids=[c["description"] for c in CASES["invalid"]])
def test_rejects_invalid(case):
    with pytest.raises(ProfileError) as error:
        parse_profile(case["input"])
    assert error.value.reason == case["reason"]


def test_round_trip():
    profile = parse_profile(json.dumps(CASES["run"][0]["profile"]))
    assert parse_profile(serialize_profile(profile)) == profile
