"""Grouping of similar values in a column (fuzzy matching). Mirrors web/src/core/similar.ts."""

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

import numpy as np
from rapidfuzz import fuzz, process

from .text import JS_WHITESPACE, js_trim

LEGAL_FORMS = {
    "sl", "sa", "slu", "sll", "slne", "sau", "scp", "cb", "sc", "scoop", "sccl",
    "inc", "ltd", "llc", "plc", "corp", "co", "gmbh", "ag", "sas", "sarl", "srl", "spa", "bv", "nv",
}  # fmt: skip

_REPEATED_SPACES = re.compile(f"[{JS_WHITESPACE}]{{2,}}")


@dataclass(frozen=True)
class SimilarOptions:
    # Minimum similarity (0-100) for two values to be grouped. Same scale as RapidFuzz fuzz.ratio.
    threshold: float
    # Ignore trailing legal forms (S.L., S.A., Inc...) when comparing
    ignore_legal_forms: bool


@dataclass(frozen=True)
class Variant:
    value: str
    count: int


@dataclass(frozen=True)
class SimilarGroup:
    # Most frequent first
    variants: list[Variant]
    # Proposed value: the most frequent clean variant (no surrounding or repeated spaces), else the most frequent
    suggested: str


def comparison_key(value: str, ignore_legal_forms: bool) -> str:
    """Key used to compare values: lowercase, no accents, no punctuation, no spaces.

    "Trans Grau S.L." -> "transgrausl", or "transgrau" when ignoring legal forms.
    """
    without_accents = "".join(
        char for char in unicodedata.normalize("NFD", value) if not unicodedata.category(char).startswith("M")
    )
    simplified = without_accents.lower().replace(".", "")
    tokens = "".join(char if char.isalnum() else " " for char in simplified).split()

    if ignore_legal_forms:
        while len(tokens) > 1:
            last = tokens[-1]
            if last in LEGAL_FORMS:
                tokens.pop()
                continue
            # "S. L." becomes the single-letter tokens "s", "l"
            if len(tokens) > 2 and len(last) == 1 and len(tokens[-2]) == 1 and tokens[-2] + last in LEGAL_FORMS:
                del tokens[-2:]
                continue
            break
    return "".join(tokens)


def similarity(a: str, b: str) -> float:
    """Similarity 0-100 (normalized Indel similarity, RapidFuzz fuzz.ratio)."""
    return fuzz.ratio(a, b)


def _is_clean(value: str) -> bool:
    return value == js_trim(value) and not _REPEATED_SPACES.search(value)


def group_similar_values(values: list[str], options: SimilarOptions) -> list[SimilarGroup]:
    """Groups values of a column that probably mean the same thing.

    1. Values with the same comparison key are always together.
    2. Keys are clustered greedily, most frequent first: a key joins the first cluster
       whose leader is at least `threshold` similar (no chaining).
    Only groups with two or more distinct variants are returned. Ordering uses code points
    (not locale) so both versions produce the same groups in the same order.
    """
    counts = Counter(value for value in values if js_trim(value) != "")

    buckets: dict[str, list[Variant]] = {}
    for value, count in counts.items():
        key = comparison_key(value, options.ignore_legal_forms)
        if key:
            buckets.setdefault(key, []).append(Variant(value, count))

    def total(variants: list[Variant]) -> int:
        return sum(variant.count for variant in variants)

    clusters: list[tuple[str, list[Variant]]] = []
    leaders: list[str] = []
    for key, variants in sorted(buckets.items(), key=lambda item: (-total(item[1]), item[0])):
        # Score against every leader at once in native code; the first one above the threshold wins
        match = None
        if leaders:
            scores = process.cdist([key], leaders, scorer=fuzz.ratio, dtype=np.float64)[0]
            above = np.flatnonzero(scores >= options.threshold)
            match = int(above[0]) if above.size else None
        if match is None:
            clusters.append((key, list(variants)))
            leaders.append(key)
        else:
            clusters[match][1].extend(variants)

    groups = []
    for _leader, members in sorted(clusters, key=lambda cluster: (-total(cluster[1]), cluster[0])):
        if len(members) < 2:
            continue
        ordered = sorted(members, key=lambda variant: (-variant.count, variant.value))
        clean = next((variant for variant in ordered if _is_clean(variant.value)), ordered[0])
        groups.append(SimilarGroup(ordered, clean.value))
    return groups
