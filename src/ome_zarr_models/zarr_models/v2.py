from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Union

TAttr = TypeVar("TAttr", bound=Mapping[str, Any])
TMembers = TypeVar("TMembers", bound=Union["Group", "Array"])


@dataclass(kw_only=True, slots=True, frozen=True)
class Group(Generic[TAttr, TMembers]):
    """
    Model of a zarr group.
    """

    attributes: TAttr
    members: Mapping[str, Group | Array]


@dataclass(kw_only=True, slots=True, frozen=True)
class Array(Generic[TAttr]):
    """Model of a zarr array."""

    attributes: TAttr
    shape: tuple[int, ...]
    dtype: str
