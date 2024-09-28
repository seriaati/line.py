from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def find_indexes(s: str, ch: str) -> Sequence[int]:
    """Find all indexes of a character in a string.

    Args:
        s: The string to search in.
        ch: The character to search for.

    Returns:
        A list of all indexes of the character in the string.
    """
    return [i for i, letter in enumerate(s) if letter == ch]
