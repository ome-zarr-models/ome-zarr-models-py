from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from pydantic_zarr.v2 import AnyGroupSpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import (
    check_array_path,
    check_group_path,
)
from ome_zarr_models.v04.base import BaseGroupv04

TCls = TypeVar("TCls", bound=BaseGroupv04[Any])
TAttrs = TypeVar("TAttrs", bound=BaseAttrs)

if TYPE_CHECKING:
    import zarr
    from pydantic_zarr.v2 import AnyArraySpec, AnyGroupSpec


def _from_zarr(
    group: zarr.Group,
    group_cls: type[TCls],
    attrs_cls: type[TAttrs],
) -> TCls:
    """
    Create a GroupSpec from a potentially unlistable Zarr group.

    This uses methods on the attribute class to get required and optional
    paths to ararys and groups, and then manually constructs the GroupSpec
    from those paths.

    Parameters
    ----------
    group :
        Zarr group to create GroupSpec from.
    group_cls :
        Class of the Group to return.
    attrs_cls :
        Attributes class.
    """
    # on unlistable storage backends, the members of this group will be {}
    group_spec: AnyGroupSpec = GroupSpec.from_zarr(group, depth=0)
    attributes = attrs_cls.model_validate(group_spec.attributes)

    members_tree_flat: dict[str, AnyGroupSpec | AnyArraySpec] = {}

    # Required array paths
    for array_path in attrs_cls.get_array_paths(attributes):
        array_spec = check_array_path(group, array_path, expected_zarr_version=2)
        members_tree_flat["/" + array_path] = array_spec

    # Optional array paths
    for array_path in attrs_cls.get_optional_array_paths(attributes):
        try:
            array_spec = check_array_path(group, array_path, expected_zarr_version=2)
        except ValueError:
            continue
        members_tree_flat["/" + array_path] = array_spec

    # Required group paths
    required_groups = attrs_cls.get_group_paths(attributes)
    for group_path in required_groups:
        group_spec = check_group_path(group, group_path, expected_zarr_version=2)
        group_flat = required_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    # Optional group paths
    optional_groups = attrs_cls.get_optional_group_paths(attributes)
    for group_path in optional_groups:
        try:
            group_spec = check_group_path(group, group_path, expected_zarr_version=2)
        except FileNotFoundError:
            continue
        group_flat = optional_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    members_normalized: AnyGroupSpec = GroupSpec.from_flat(members_tree_flat)
    return group_cls(members=members_normalized.members, attributes=attributes)
