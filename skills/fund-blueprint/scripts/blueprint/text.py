"""Small text helpers shared by scoring and the report."""
from __future__ import annotations

from typing import List


def join_words(words: List[str]) -> str:
    if len(words) < 3:
        return " and ".join(words)
    return f"{', '.join(words[:-1])}, and {words[-1]}"


def lower_first(label: str) -> str:
    """Lowercase for use mid-sentence, but keep acronyms such as LP, DDQ, and NDAs."""
    first = label.split()[0]
    return label if first[:2].isupper() else label[0].lower() + label[1:]
