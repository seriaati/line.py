from typing import Sequence


def find_indexes(s: str, ch: str) -> Sequence[int]:
    return [i for i, letter in enumerate(s) if letter == ch]
