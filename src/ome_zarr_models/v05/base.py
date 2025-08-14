from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel
from pydantic_zarr.v3 import GroupSpec

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


# T = TypeVar("T", bound="BaseOMEAttrs")


class BaseGroupv05(BaseGroup, GroupSpec[BaseZarrAttrs[T], Any], Generic[T]):
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

    def _check_members_exist(self) -> None:
        if self.members is None:
            raise RuntimeError("Zarr group has no members")
