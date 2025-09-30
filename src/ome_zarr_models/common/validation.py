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

from ome_zarr_models.common.coordinate_transformations import VectorScale

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
        array = zarr.open_array(
            store=group.store_path,
            path=array_path,
            mode="r",
            zarr_format=expected_zarr_version,
        )
    except FileNotFoundError as e:
        msg = (
            f"Expected to find an array at {array_path}, but no array was found there."
        )
        raise ValueError(msg) from e
    except (zarr.errors.ContainsGroupError, zarr.errors.NodeTypeValidationError) as e:
        msg = (
            f"Expected to find an array at {array_path}, "
            "but a group was found there instead."
        )
        raise ValueError(msg) from e

    array_spec: AnyArraySpecv2 | AnyArraySpecv3
    if array.metadata.zarr_format == 2:
        if expected_zarr_version == 3:
            raise ValueError("Expected Zarr v3 array, but got v2 array")
        array_spec = ArraySpecv2.from_zarr(array)
    else:
        if expected_zarr_version == 2:
            raise ValueError("Expected Zarr v2 array, but got v3 array")
        array_spec = ArraySpecv3.from_zarr(array)

    return array_spec


@overload
def check_group_path(
    group: zarr.Group,
    group_path: str,
    *,
    expected_zarr_version: Literal[2],
) -> AnyGroupSpecv2: ...


@overload
def check_group_path(
    group: zarr.Group,
    group_path: str,
    *,
    expected_zarr_version: Literal[3],
) -> AnyGroupSpecv3: ...


def check_group_path(
    group: zarr.Group,
    group_path: str,
    *,
    expected_zarr_version: Literal[2, 3],
) -> AnyGroupSpecv2 | AnyGroupSpecv3:
    """
    Check if a group exists at a given path in a group.

    Returns
    -------
    GroupSpec
        If the path exists, it's GroupSpec is returned.

    Raises
    ------
    ValueError
        If the group doesn't exist, or the group is not the expected Zarr version.
    """
    try:
        group = zarr.open_group(
            store=group.store_path,
            path=group_path,
            mode="r",
            zarr_format=expected_zarr_version,
        )
    except FileNotFoundError as e:
        msg = f"Expected to find a group at {group_path}, but no group was found there."
        raise FileNotFoundError(msg) from e
    except zarr.errors.ContainsArrayError as e:
        msg = (
            f"Expected to find an group at {group_path}, "
            "but an array was found there instead."
        )
        raise zarr.errors.ContainsArrayError(msg) from e

    group_spec: AnyGroupSpecv2 | AnyGroupSpecv3
    if group.metadata.zarr_format == 2:
        if expected_zarr_version == 3:
            raise ValueError("Expected Zarr v3 array, but got v2 array")
        group_spec = GroupSpecv2.from_zarr(group, depth=0)
    else:
        if expected_zarr_version == 2:
            raise ValueError("Expected Zarr v2 array, but got v3 array")
        group_spec = GroupSpecv3.from_zarr(group, depth=0)

    return group_spec


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


def check_ordered_scales(scales: list[VectorScale]) -> None:
    """
    Given a list of scales, make sure they are ordered from low to high.

    Raises
    ------
    ValueError
        If any items in one set of scales is smaller than any item in
        the preceding set of scales.
    """
    for i in range(len(scales) - 1):
        s1, s2 = scales[i].scale, scales[i + 1].scale
        is_ordered = all(s1[j] <= s2[j] for j in range(len(s1)))
        if not is_ordered:
            raise ValueError(
                f"Dataset {i} has a lower resolution (scales = {s1}) "
                f"than dataset {i + 1} (scales = {s2})."
            )
