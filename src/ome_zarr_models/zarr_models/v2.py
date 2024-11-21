from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any, TypeVar, Generic, Union
from typing_extensions import Self

TAttr = TypeVar("TAttr", bound=Mapping[str, Any])
TMembers = TypeVar("TMembers", bound = Union["Group, Array"])

@dataclass(kw_only=True, slots=True, frozen=True)
class Group(Generic[TAttr, TMembers]):
    attributes: TAttr
    members: Mapping[str, Group | Array]

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:
        ...

    def to_zarr():
        ...

@dataclass(kw_only=True, slots=True, frozen=True)
class Array(Generic[TAttr]):
    attributes: TAttr
    shape: tuple[int, ...]
    dtype: str

    def to_zarr():
        ...

    def from_zarr():
        ...
