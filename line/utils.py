from typing import List


def find_indexes(s: str, ch: str) -> List[int]:
    return [i for i, letter in enumerate(s) if letter == ch]
