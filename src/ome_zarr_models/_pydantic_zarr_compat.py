"""
Compatibility layer over the pydantic-zarr versions this package supports.

pydantic-zarr 0.11 changed three things this package relies on:

- A group read without its members is a ``BaseGroupSpec``. ``GroupSpec.members``
  can no longer be ``None``, and ``GroupSpec.from_zarr`` lost its ``depth``
  parameter.
- ``to_flat`` returns the groups in a hierarchy as ``BaseGroupSpec``, which is
  a base class of ``GroupSpec``, not a subclass.
- The zarr-python IO methods (``from_zarr``, ``to_zarr``) are deprecated, and
  removed in 0.12. Nodes are read by loading their stored metadata documents
  with zarr-python and passing them to ``from_stored_metadata_json``.

Every place in this package that reads a Zarr node into a pydantic-zarr model,
or asks whether a model from a flat hierarchy is a group, goes through this
module. Once the minimum supported pydantic-zarr is 0.11, the legacy branches
can be deleted and this module inlined.

Type checking runs against pydantic-zarr >= 0.11 (see .pre-commit-config.yaml).
A ``# type: ignore[..., unused-ignore]`` elsewhere in the package marks an
error that only one of the supported versions raises; drop the comment along
with the legacy branches. One such source: from 0.11, mypy resolves
pydantic-zarr's ``AnyArraySpec`` / ``AnyGroupSpec`` aliases to ``Any``.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pydantic_zarr.v2
import pydantic_zarr.v3
from zarr.core.buffer import default_buffer_prototype

if TYPE_CHECKING:
    from typing import TypeVar

    import zarr
    from typing_extensions import TypeIs

    # Bound by the classes, not the ``AnyGroupSpec`` aliases: under mypy the
    # aliases resolve to ``Any`` from pydantic-zarr 0.11.
    TGroupv2 = TypeVar("TGroupv2", bound=pydantic_zarr.v2.GroupSpec[Any, Any])
    TGroupv3 = TypeVar("TGroupv3", bound=pydantic_zarr.v3.GroupSpec[Any, Any])

__all__ = [
    "HAS_STORED_METADATA_API",
    "is_group_spec",
    "read_array_v2",
    "read_array_v3",
    "read_group_shallow_v2",
    "read_group_shallow_v3",
    "read_group_v2",
    "read_group_v3",
]

#: True for pydantic-zarr >= 0.11, which has ``BaseGroupSpec`` and the
#: ``{from,to}_stored_metadata_json`` API, and has dropped ``from_zarr(depth=...)``.
HAS_STORED_METADATA_API: bool = hasattr(pydantic_zarr.v3, "BaseGroupSpec")

# Classes every group spec (with or without members) is an instance of.
_GROUP_SPEC_CLASSES: tuple[type, ...] = (
    (pydantic_zarr.v2.BaseGroupSpec, pydantic_zarr.v3.BaseGroupSpec)
    if HAS_STORED_METADATA_API
    else (pydantic_zarr.v2.GroupSpec, pydantic_zarr.v3.GroupSpec)
)

# Store keys of zarr-python's consolidated metadata record (Zarr V2), which
# records the hierarchy below a group rather than being part of its metadata.
_V2_CONSOLIDATED_KEY = ".zmetadata"


def is_group_spec(
    node: object,
) -> TypeIs[pydantic_zarr.v2.BaseGroupSpec[Any] | pydantic_zarr.v3.BaseGroupSpec[Any]]:
    """
    Whether ``node`` models a Zarr group, with or without its members.

    Use this instead of ``isinstance(node, GroupSpec)`` on the values of
    ``to_flat()``: from pydantic-zarr 0.11 those are ``BaseGroupSpec``.
    """
    return isinstance(node, _GROUP_SPEC_CLASSES)


def _own_documents(node: zarr.Array[Any] | zarr.Group) -> dict[str, Any]:
    """
    Read the metadata documents a store holds for ``node`` itself.

    The documents are keyed by store key.

    ``consolidated_metadata`` is dropped, matching ``from_zarr``: it is
    zarr-python's record of the hierarchy below a group, not the group's own
    metadata.
    """
    documents: dict[str, Any] = {}
    for key, buffer in node.metadata.to_buffer_dict(default_buffer_prototype()).items():
        if key == _V2_CONSOLIDATED_KEY:
            continue
        document = json.loads(buffer.to_bytes())
        if isinstance(document, dict):
            document.pop("consolidated_metadata", None)
        documents[key] = document
    return documents


def _hierarchy_documents(group: zarr.Group) -> dict[str, Any]:
    """
    Read the metadata documents of ``group`` and every node below it.

    The documents are keyed by store key relative to ``group``: the mapping
    ``from_stored_metadata_json`` takes.
    """
    documents = _own_documents(group)
    for path, member in group.members(max_depth=None):
        for key, document in _own_documents(member).items():
            documents[f"{path}/{key}"] = document
    return documents


def read_array_v2(array: zarr.Array[Any]) -> pydantic_zarr.v2.ArraySpec[Any]:
    """Read a Zarr V2 array's metadata."""
    if HAS_STORED_METADATA_API:
        return pydantic_zarr.v2.ArraySpec.from_stored_metadata_json(
            _own_documents(array)
        )
    return pydantic_zarr.v2.ArraySpec.from_zarr(array)


def read_array_v3(array: zarr.Array[Any]) -> pydantic_zarr.v3.ArraySpec[Any]:
    """Read a Zarr V3 array's metadata."""
    if HAS_STORED_METADATA_API:
        return pydantic_zarr.v3.ArraySpec.from_stored_metadata_json(
            _own_documents(array)
        )
    return pydantic_zarr.v3.ArraySpec.from_zarr(array)


def read_group_shallow_v2(group: zarr.Group) -> pydantic_zarr.v2.BaseGroupSpec[Any]:
    """
    Read a Zarr V2 group's own metadata, without listing or reading its members.

    Works on unlistable stores. Use only the ``attributes`` of the result: on
    pydantic-zarr < 0.11 it is a ``GroupSpec`` with ``members=None``.
    """
    if HAS_STORED_METADATA_API:
        return pydantic_zarr.v2.BaseGroupSpec.from_stored_metadata_json(
            _own_documents(group)
        )
    return pydantic_zarr.v2.GroupSpec.from_zarr(group, depth=0)  # type: ignore[call-arg]


def read_group_shallow_v3(group: zarr.Group) -> pydantic_zarr.v3.BaseGroupSpec[Any]:
    """
    Read a Zarr V3 group's own metadata, without listing or reading its members.

    Works on unlistable stores. Use only the ``attributes`` of the result: on
    pydantic-zarr < 0.11 it is a ``GroupSpec`` with ``members=None``.
    """
    if HAS_STORED_METADATA_API:
        return pydantic_zarr.v3.BaseGroupSpec.from_stored_metadata_json(
            _own_documents(group)
        )
    return pydantic_zarr.v3.GroupSpec.from_zarr(group, depth=0)  # type: ignore[call-arg]


def read_group_v2(cls: type[TGroupv2], group: zarr.Group) -> TGroupv2:
    """Read a whole Zarr V2 hierarchy into ``cls``."""
    if HAS_STORED_METADATA_API:
        return cls.from_stored_metadata_json(_hierarchy_documents(group))
    # Call pydantic-zarr's implementation directly: ``cls.from_zarr`` may be an
    # override in this package that calls back into this function.
    return pydantic_zarr.v2.GroupSpec.from_zarr.__func__(cls, group)  # type: ignore[attr-defined, no-any-return]


def read_group_v3(cls: type[TGroupv3], group: zarr.Group) -> TGroupv3:
    """Read a whole Zarr V3 hierarchy into ``cls``."""
    if HAS_STORED_METADATA_API:
        return cls.from_stored_metadata_json(_hierarchy_documents(group))
    # Call pydantic-zarr's implementation directly: ``cls.from_zarr`` may be an
    # override in this package that calls back into this function.
    return pydantic_zarr.v3.GroupSpec.from_zarr.__func__(cls, group)  # type: ignore[attr-defined, no-any-return]
