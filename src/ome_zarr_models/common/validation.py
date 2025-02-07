from typing import TypeVar

import zarr
import zarr.errors
from pydantic import StringConstraints
from pydantic_zarr.v2 import ArraySpec

__all__ = [
    "AlphaNumericConstraint",
    "RGBHexConstraint",
    "check_array_path",
    "unique_items_validator",
]

AlphaNumericConstraint = StringConstraints(pattern="^[a-zA-Z0-9]*$")
"""Require a string to only contain letters and numbers"""

RGBHexConstraint = StringConstraints(pattern=r"[0-9a-fA-F]{6}")
"""Require a string to be a valid RGB hex string"""

T = TypeVar("T")


def unique_items_validator(values: list[T]) -> list[T]:
    """
    Make sure a list contains unique items.
    """
    for ind, value in enumerate(values, start=1):
        if value in values[ind:]:
            raise ValueError(f"Duplicate values found in {values}.")
    return values


def check_array_path(group: zarr.Group, array_path: str) -> ArraySpec:
    """
    Check if an array exists at a given path in a group.

    Returns
    -------
    ArraySpec :
        If the path exists, it's ArraySpec is returned.

    Raises
    ------
    ValueError
        If the array doesn't exist.
    """
    try:
        array = zarr.open_array(store=group.store, path=array_path, mode="r")
        array_spec = ArraySpec.from_zarr(array)
    except zarr.errors.ArrayNotFoundError as e:
        msg = (
            f"Expected to find an array at {array_path}, "
            "but no array was found there."
        )
        raise ValueError(msg) from e
    except zarr.errors.ContainsGroupError as e:
        msg = (
            f"Expected to find an array at {array_path}, "
            "but a group was found there instead."
        )
        raise ValueError(msg) from e

    return array_spec
