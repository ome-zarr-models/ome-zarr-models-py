from typing import TYPE_CHECKING, Any, TypeVar

import zarr
from pydantic_zarr.v2 import AnyGroupSpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import check_array_path
from ome_zarr_models.v04.base import BaseGroupv04

TCls = TypeVar("TCls", bound=BaseGroupv04[Any])
TAttrs = TypeVar("TAttrs", bound=BaseAttrs)

if TYPE_CHECKING:
    from pydantic_zarr.v2 import AnyArraySpec, AnyGroupSpec


def _from_zarr(
    group: zarr.Group,
    group_cls: type[TCls],
    attrs_cls: type[TAttrs],
) -> TCls:
    """
    Create a GroupSpec from a potentially unlistable Zarr group.

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

    for array_path in attrs_cls.get_array_paths(attributes):
        array_spec = check_array_path(
            group, f"{group.path}/{array_path}", expected_zarr_version=2
        )
        members_tree_flat["/" + array_path] = array_spec

    for array_path in attrs_cls.get_optional_array_paths(attributes):
        try:
            array_spec = check_array_path(
                group, f"{group.path}/{array_path}", expected_zarr_version=2
            )
        except ValueError:
            continue
        members_tree_flat["/" + array_path] = array_spec

    members_normalized: AnyGroupSpec = GroupSpec.from_flat(members_tree_flat)
    return group_cls(members=members_normalized.members, attributes=attributes)
