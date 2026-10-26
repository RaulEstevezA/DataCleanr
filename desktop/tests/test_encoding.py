import pytest

from datacleanr.core.encoding import decode_text

from .conftest import load_cases

CASES = load_cases("encoding.json")


@pytest.mark.parametrize("case", CASES, ids=[case["description"] for case in CASES])
def test_shared_cases(case):
    assert decode_text(bytes.fromhex(case["bytes"])) == (case["expectedText"], case["expectedEncoding"])


def test_undefined_windows_1252_bytes_do_not_fail():
    # "é" (0xE9) makes it invalid UTF-8; 0x81 has no Windows-1252 character
    assert decode_text(b"caf\xe9 \x81") == ("café \x81", "windows-1252")
