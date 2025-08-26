# Need to import `annotations` for the pydantic_zarr TypeAlias strings to work
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeVar, overload

import zarr
import zarr.errors
from pydantic import StringConstraints
from pydantic_zarr.v2 import AnyArraySpec as AnyArraySpecv2
from pydantic_zarr.v2 import AnyGroupSpec as AnyGroupSpecv2
from pydantic_zarr.v2 import ArraySpec as ArraySpecv2
from pydantic_zarr.v2 import GroupSpec as GroupSpecv2
from pydantic_zarr.v3 import AnyArraySpec as AnyArraySpecv3
from pydantic_zarr.v3 import AnyGroupSpec as AnyGroupSpecv3
from pydantic_zarr.v3 import ArraySpec as ArraySpecv3
from pydantic_zarr.v3 import GroupSpec as GroupSpecv3

if TYPE_CHECKING:
    from collections.abc import Sequence


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

    Raises
    ------
    ValueError
        If duplicate values are found in *values*.
    """
    for ind, value in enumerate(values, start=1):
        if value in values[ind:]:
            raise ValueError(f"Duplicate values found in {values}.")
    return values


@overload
def check_array_path(
    group: zarr.Group,
    array_path: str,
    *,
    expected_zarr_version: Literal[2],
) -> AnyArraySpecv2: ...


@overload
def check_array_path(
    group: zarr.Group,
    array_path: str,
    *,
    expected_zarr_version: Literal[3],
) -> AnyArraySpecv3: ...


def check_array_path(
    group: zarr.Group,
    array_path: str,
    *,
    expected_zarr_version: Literal[2, 3],
) -> AnyArraySpecv2 | AnyArraySpecv3:
    """
    Check if an array exists at a given path in a group.

    Returns
    -------
    ArraySpec
        If the path exists, it's ArraySpec is returned.

    Raises
    ------
    ValueError
        If the array doesn't exist, or the array is not the expected Zarr version.
    """
    try:
        array = zarr.open_array(store=group.store, path=array_path, mode="r")
        array_spec: AnyArraySpecv2 | AnyArraySpecv3
        if array.metadata.zarr_format == 2:
            if expected_zarr_version == 3:
                raise ValueError("Expected Zarr v3 array, but got v2 array")
            array_spec = ArraySpecv2.from_zarr(array)
        else:
            if expected_zarr_version == 2:
                raise ValueError("Expected Zarr v2 array, but got v3 array")
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
def check_array_spec(spec: AnyGroupSpecv2, path: str) -> AnyArraySpecv2: ...


@overload
def check_array_spec(spec: AnyGroupSpecv3, path: str) -> AnyArraySpecv3: ...


def check_array_spec(
    spec: AnyGroupSpecv2 | AnyGroupSpecv3, path: str
) -> AnyArraySpecv2 | AnyArraySpecv3:
    """
    Check that a path within a group is an array.

    Raises
    ------
    ValueError
        If the node at *path* is not an array.
    """
    if spec.members is None:
        raise ValueError(f"members=None for {spec}")
    new_spec = spec.members[path]
    if not isinstance(new_spec, ArraySpecv2 | ArraySpecv3):
        raise ValueError(f"Node at path '{path}' is a group, expected an array")
    return new_spec


@overload
def check_group_spec(spec: AnyGroupSpecv2, path: str) -> AnyGroupSpecv2: ...


@overload
def check_group_spec(spec: AnyGroupSpecv3, path: str) -> AnyGroupSpecv3: ...


def check_group_spec(
    spec: AnyGroupSpecv2 | AnyGroupSpecv3, path: str
) -> AnyGroupSpecv2 | AnyGroupSpecv3:
    """
    Check that a path within a group is a group.

    Raises
    ------
    ValueError
        If the node at *path* is not a group.
    """
    if spec.members is None:
        raise ValueError("Specification has no members.")
    new_spec = spec.members[path]
    if not isinstance(new_spec, GroupSpecv2 | GroupSpecv3):
        raise ValueError(
            f"Node at path '{path}' is not a GroupSpec (got {type(new_spec)=})"
        )
    return new_spec
