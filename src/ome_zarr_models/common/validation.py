from typing import TypeVar

from pydantic import StringConstraints

__all__ = ["AlphaNumericConstraint", "unique_items_validator"]

AlphaNumericConstraint = StringConstraints(pattern="^[a-zA-Z0-9]*$")
"""Require a string to only contain letters and numbers"""


T = TypeVar("T")


def unique_items_validator(values: list[T]) -> list[T]:
    """
    Make sure a list contains unique items.
    """
    for ind, value in enumerate(values, start=1):
        if value in values[ind:]:
            raise ValueError(f"Duplicate values found in {values}.")
    return values
