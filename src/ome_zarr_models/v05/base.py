from __future__ import annotations

from typing import Generic, Literal, TypeVar, Union

from pydantic import BaseModel
from pydantic_zarr.v3 import ArraySpec, GroupSpec

from ome_zarr_models.base import BaseAttrs, BaseGroup


class BaseOMEAttrs(BaseAttrs):
    """
    Base class for attributes under an OME-Zarr group.
    """

    version: Literal["0.5"]


T = TypeVar("T", bound="BaseOMEAttrs")


class BaseZarrAttrs(BaseModel, Generic[T]):
    """
    Base class for zarr attributes in an OME-Zarr group.
    """

    ome: T


class BaseGroupv05(
    BaseGroup,
    GroupSpec[BaseZarrAttrs[T], Union["GroupSpec", "ArraySpec"]],  # type: ignore[type-arg]
    Generic[T],
):
    """
    Base class for all v0.5 OME-Zarr groups.
    """

    @property
    def ome_zarr_version(self) -> Literal["0.5"]:
        """
        OME-Zarr version.
        """
        return "0.5"

    @property
    def ome_attributes(self) -> T:
        """
        OME attributes.
        """
        return self.attributes.ome
