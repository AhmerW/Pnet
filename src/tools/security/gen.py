import secrets
import string
import typing

def randstr(length : int = 12, combination : str = None) -> str:
    if not combination:
        combination = string.ascii_letters
    if isinstance(combination, list):
        combination = ''.join([str(x) for x in combination])
    return ''.join(
        secrets.choice(combination) for _ in range(0, length, 1)
    )
