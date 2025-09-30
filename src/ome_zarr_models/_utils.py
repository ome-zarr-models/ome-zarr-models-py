"""
Private utilities.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import MISSING, fields, is_dataclass
from typing import TYPE_CHECKING, Any, TypeVar

import pydantic
import pydantic_zarr.v2
import pydantic_zarr.v3
from pydantic import create_model

from ome_zarr_models.base import BaseAttrsv2, BaseAttrsv3
from ome_zarr_models.common.validation import (
    check_array_path,
    check_group_path,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    import zarr
    from zarr.abc.store import Store

    from ome_zarr_models._v06.base import BaseGroupv06
    from ome_zarr_models.v04.base import BaseGroupv04
    from ome_zarr_models.v05.base import BaseGroupv05

TBaseGroupv2 = TypeVar("TBaseGroupv2", bound="BaseGroupv04[Any]")
TAttrsv2 = TypeVar("TAttrsv2", bound=BaseAttrsv2)


def _from_zarr_v2(
    group: zarr.Group,
    group_cls: type[TBaseGroupv2],
    attrs_cls: type[TAttrsv2],
) -> TBaseGroupv2:
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
    group_spec_in: pydantic_zarr.v2.AnyGroupSpec
    group_spec_in = pydantic_zarr.v2.GroupSpec.from_zarr(group, depth=0)
    attributes = attrs_cls.model_validate(group_spec_in.attributes)

    members_tree_flat: dict[
        str, pydantic_zarr.v2.AnyGroupSpec | pydantic_zarr.v2.AnyArraySpec
    ] = {}

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
        check_group_path(group, group_path, expected_zarr_version=2)
        group_flat = required_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    # Optional group paths
    optional_groups = attrs_cls.get_optional_group_paths(attributes)
    for group_path in optional_groups:
        try:
            check_group_path(group, group_path, expected_zarr_version=2)
        except FileNotFoundError:
            continue
        group_flat = optional_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    members_normalized: pydantic_zarr.v2.AnyGroupSpec = (
        pydantic_zarr.v2.GroupSpec.from_flat(members_tree_flat)
    )
    return group_cls(members=members_normalized.members, attributes=attributes)


TBaseGroupv3 = TypeVar("TBaseGroupv3", bound="BaseGroupv05[Any] | BaseGroupv06[Any]")
TAttrsv3 = TypeVar("TAttrsv3", bound=BaseAttrsv3)


def _from_zarr_v3(
    group: zarr.Group,
    group_cls: type[TBaseGroupv3],
    attrs_cls: type[TAttrsv3],
) -> TBaseGroupv3:
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
    group_spec_in: pydantic_zarr.v3.AnyGroupSpec
    group_spec_in = pydantic_zarr.v3.GroupSpec.from_zarr(group, depth=0)
    ome_attributes = attrs_cls.model_validate(group.attrs.asdict()["ome"])

    members_tree_flat: dict[
        str, pydantic_zarr.v3.AnyGroupSpec | pydantic_zarr.v3.AnyArraySpec
    ] = {}

    # Required array paths
    for array_path in attrs_cls.get_array_paths(ome_attributes):
        array_spec = check_array_path(group, array_path, expected_zarr_version=3)
        members_tree_flat["/" + array_path] = array_spec

    # Optional array paths
    for array_path in attrs_cls.get_optional_array_paths(ome_attributes):
        try:
            array_spec = check_array_path(group, array_path, expected_zarr_version=3)
        except ValueError:
            continue
        members_tree_flat["/" + array_path] = array_spec

    # Required group paths
    required_groups = attrs_cls.get_group_paths(ome_attributes)
    for group_path in required_groups:
        check_group_path(group, group_path, expected_zarr_version=3)
        group_flat = required_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    # Optional group paths
    optional_groups = attrs_cls.get_optional_group_paths(ome_attributes)
    for group_path in optional_groups:
        try:
            check_group_path(group, group_path, expected_zarr_version=3)
        except FileNotFoundError:
            continue
        group_flat = optional_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    members_normalized: pydantic_zarr.v3.AnyGroupSpec
    members_normalized = pydantic_zarr.v3.GroupSpec.from_flat(members_tree_flat)
    return group_cls(  # type: ignore[return-value]
        members=members_normalized.members, attributes=group_spec_in.attributes
    )


def get_store_path(store: Store) -> str:
    """
    Get a path from a zarr store
    """
    if hasattr(store, "path"):
        return store.path  # type: ignore[no-any-return]

    return ""


T = TypeVar("T")


def duplicates(values: Iterable[T]) -> dict[T, int]:
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
