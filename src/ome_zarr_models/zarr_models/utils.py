from typing import TypeVar


T = TypeVar("T")


def _unique_items_validator(values: list[T]) -> list[T]:
    for ind, value in enumerate(values, start=1):
        if value in values[ind:]:
            raise ValueError(f"Non-unique values in {values}.")
    return values
