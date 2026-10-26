"""Number to text exactly like JavaScript's String(number).

Excel stores numbers as floats. Both versions turn them into text, and Python's repr()
differs from JavaScript in some cases (433.0 vs 433, 1e-05 vs 0.00001, 1e+16 vs
10000000000000000). This follows the ECMAScript Number::toString algorithm.
"""

import math
from decimal import Decimal


def js_number_to_string(value: float) -> str:
    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"
    if value == 0:
        return "0"
    if value < 0:
        return "-" + js_number_to_string(-value)

    # repr() gives the shortest digits that read back as the same float, like JavaScript
    _, digit_tuple, exponent = Decimal(repr(float(value))).as_tuple()
    digits = "".join(map(str, digit_tuple)).rstrip("0")
    exponent += len("".join(map(str, digit_tuple))) - len(digits)
    k = len(digits)
    # value = 0.digits × 10^n
    n = exponent + k

    if k <= n <= 21:
        return digits + "0" * (n - k)
    if 0 < n <= 21:
        return digits[:n] + "." + digits[n:]
    if -6 < n <= 0:
        return "0." + "0" * (-n) + digits
    sign = "+" if n - 1 >= 0 else "-"
    mantissa = digits if k == 1 else digits[0] + "." + digits[1:]
    return f"{mantissa}e{sign}{abs(n - 1)}"
