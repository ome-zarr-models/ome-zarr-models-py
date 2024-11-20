from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any, TypeVar, Generic

TAttr = TypeVar("TAttr", bound=Mapping[str, Any])
TMembers = TypeVar("TMembers", bound=Group | Array)

@dataclass(kw_only=True, slots=True, frozen=True)
class Group(Generic[TAttr, TMembers]):
    attributes: TAttr
    members: Mapping[str, Group | Array]

@dataclass(kw_only=True, slots=True, frozen=True)
class Array(Generic[TAttr]):
    attributes: TAttr
    shape: tuple[int, ...]
    dtype: str