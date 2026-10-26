import json
from pathlib import Path

import pytest

SHARED_CASES = Path(__file__).resolve().parents[2] / "shared" / "test-cases"


def load_cases(name: str):
    """Loads a shared test case file, the same one the web version's tests read."""
    return json.loads((SHARED_CASES / name).read_text(encoding="utf-8"))


@pytest.fixture
def shared_file():
    """Path to a sample file in shared/test-cases/files/."""
    return lambda name: SHARED_CASES / "files" / name
