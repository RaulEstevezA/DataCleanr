"""Text encoding detection. Mirrors web/src/core/encoding.ts.

Decodes file bytes guessing the encoding, so accents and "ñ" display correctly:
1. A UTF-16 byte order mark wins.
2. Otherwise, if the bytes are valid UTF-8 they are UTF-8 (BOM removed).
3. Otherwise they are Windows-1252, what Excel uses for "CSV" on Spanish/Western Windows.
"""

import codecs

UTF8 = "utf-8"
UTF16LE = "utf-16le"
UTF16BE = "utf-16be"
WINDOWS_1252 = "windows-1252"


def _undefined_cp1252_as_c1(error: UnicodeDecodeError) -> tuple[str, int]:
    # Bytes 0x81, 0x8D, 0x8F, 0x90 and 0x9D have no character in Windows-1252. Browsers map them
    # to the C1 control with the same code (WHATWG encoding standard); Python raises. Do as browsers do.
    byte = error.object[error.start]
    return chr(byte), error.start + 1


codecs.register_error("datacleanr-c1", _undefined_cp1252_as_c1)


def decode_text(data: bytes) -> tuple[str, str]:
    """Returns (text, encoding name). Encoding names match the web version."""
    if data[:2] == b"\xff\xfe":
        return data[2:].decode("utf-16-le"), UTF16LE
    if data[:2] == b"\xfe\xff":
        return data[2:].decode("utf-16-be"), UTF16BE
    try:
        # utf-8-sig removes the BOM, like the browser's TextDecoder
        return data.decode("utf-8-sig"), UTF8
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="datacleanr-c1"), WINDOWS_1252
