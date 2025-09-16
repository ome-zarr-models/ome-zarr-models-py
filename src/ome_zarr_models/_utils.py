"""
Private utilities.
"""

from collections import Counter
from collections.abc import Hashable, Iterable
from dataclasses import MISSING, fields, is_dataclass
from typing import TYPE_CHECKING, Any, TypeVar

import pydantic
import zarr
from pydantic import create_model
from pydantic_zarr.v2 import GroupSpec as GroupSpecv2
from zarr.abc.store import Store

from ome_zarr_models.base import BaseAttrsv2
from ome_zarr_models.common.validation import (
    check_array_path,
    check_group_path,
)
from ome_zarr_models.v04.base import BaseGroupv04

if TYPE_CHECKING:
    from pydantic_zarr.v2 import (
        AnyArraySpec as AnyArraySpecv2,
    )
    from pydantic_zarr.v2 import (
        AnyGroupSpec as AnyGroupSpecv2,
    )

TBaseGroup04 = TypeVar("TBaseGroup04", bound=BaseGroupv04[Any])
TAttrs = TypeVar("TAttrs", bound=BaseAttrsv2)


def _from_zarr_v2(
    group: zarr.Group,
    group_cls: type[TBaseGroup04],
    attrs_cls: type[TAttrs],
) -> TBaseGroup04:
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
    group_spec: AnyGroupSpecv2 = GroupSpecv2.from_zarr(group, depth=0)
    attributes = attrs_cls.model_validate(group_spec.attributes)

    members_tree_flat: dict[str, AnyGroupSpecv2 | AnyArraySpecv2] = {}

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

    members_normalized: AnyGroupSpecv2 = GroupSpecv2.from_flat(members_tree_flat)
    return group_cls(members=members_normalized.members, attributes=attributes)


def get_store_path(store: Store) -> str:
    """
    Get a path from a zarr store
    """
    if hasattr(store, "path"):
        return store.path  # type: ignore[no-any-return]

    return ""


def duplicates(values: Iterable[Hashable]) -> dict[Hashable, int]:
    """
    Takes a sequence of hashable elements and returns a dict where the keys are the
    elements of the input that occurred at least once, and the values are the
    frequencies of those elements.
    """
    counts = Counter(values)
    return {k: v for k, v in counts.items() if v > 1}


def dataclass_to_pydantic(dataclass_type: type) -> type[pydantic.BaseModel]:
    """Convert a dataclass to a Pydantic model.

    Parameters
    ----------
    dataclass_type : type
        The dataclass to convert to a Pydantic model.

    Returns
    -------
    type[pydantic.BaseModel] a Pydantic model class.
    """
    if not is_dataclass(dataclass_type):
        raise TypeError(f"{dataclass_type} is not a dataclass")

    field_definitions = {}
    for _field in fields(dataclass_type):
        if _field.default is not MISSING:
            # Default value is provided
            field_definitions[_field.name] = (_field.type, _field.default)
        elif _field.default_factory is not MISSING:
            # Default factory is provided
            field_definitions[_field.name] = (_field.type, _field.default_factory())
        else:
            # No default value
            field_definitions[_field.name] = (_field.type, Ellipsis)

    return create_model(dataclass_type.__name__, **field_definitions)  # type: ignore[no-any-return, call-overload]
