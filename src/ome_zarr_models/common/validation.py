from collections.abc import Sequence
from typing import TypeVar, overload

import zarr
import zarr.errors
from pydantic import StringConstraints
from pydantic_zarr.v2 import ArraySpec as ArraySpecv2
from pydantic_zarr.v2 import GroupSpec as GroupSpecv2
from pydantic_zarr.v3 import ArraySpec as ArraySpecv3
from pydantic_zarr.v3 import GroupSpec as GroupSpecv3

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


def check_array_path(group: zarr.Group, array_path: str) -> ArraySpecv2 | ArraySpecv3:
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
        if array.metadata.zarr_format == 2:
            array_spec = ArraySpecv2.from_zarr(array)
        else:
            array_spec = ArraySpecv3.from_zarr(array)
    except FileNotFoundError as e:
        msg = (
            f"Expected to find an array at {array_path}, but no array was found there."
        )
        raise ValueError(msg) from e
    except zarr.errors.ContainsGroupError as e:
        msg = (
            f"Expected to find an array at {array_path}, "
            "but a group was found there instead."
        )
        raise ValueError(msg) from e

    return array_spec


def check_length(
    sequence: Sequence[T], *, valid_lengths: Sequence[int], variable_name: str
) -> None:
    """
    Check if the length of a sequence is valid.

    Raises
    ------
    ValueError
        If the sequence is not a valid length.
    """
    if len(sequence) not in valid_lengths:
        msg = (
            f"Length of {variable_name} ({len(sequence)}) not valid. "
            f"Allowed lengths are {valid_lengths}."
        )
        raise ValueError(msg)


@overload
def check_array_spec(spec: GroupSpecv2, path: str) -> ArraySpecv2: ...


@overload
def check_array_spec(spec: GroupSpecv3, path: str) -> ArraySpecv3: ...  # type: ignore[overload-cannot-match]


def check_array_spec(
    spec: GroupSpecv2 | GroupSpecv3, path: str
) -> ArraySpecv2 | ArraySpecv3:
    """
    Check that a path within a group is an array.

    Raises
    ------
    RuntimeError :
        If path is a group.
    """
    new_spec = spec.members[path]
    if not isinstance(new_spec, ArraySpecv2 | ArraySpecv3):
        raise RuntimeError(f"Node at path '{path}' is a group, expected an array")
    return new_spec


@overload
def check_group_spec(spec: GroupSpecv2, path: str) -> GroupSpecv2: ...


@overload
def check_group_spec(spec: GroupSpecv3, path: str) -> GroupSpecv3: ...  # type: ignore[overload-cannot-match]


def check_group_spec(
    spec: GroupSpecv2 | GroupSpecv3, path: str
) -> GroupSpecv2 | GroupSpecv3:
    """
    Check that a path within a group is a group.

    Raises
    ------
    RuntimeError :
        If path is an array.
    """
    if spec.members is None:
        raise ValueError("Specification has no members.")
    new_spec = spec.members[path]
    if not isinstance(new_spec, GroupSpecv2 | GroupSpecv3):
        raise RuntimeError(f"Node at path '{path}' is an array, expected an group")
    return new_spec
