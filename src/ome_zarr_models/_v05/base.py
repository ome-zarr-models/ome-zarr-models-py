from typing import Generic, Literal, TypeVar

from ome_zarr_models.base import BaseAttrs, BaseGroup

T = TypeVar("T", bound="BaseOMEAttrs")


class BaseZarrAttrs(BaseAttrs, Generic[T]):
    """
    Base class for zarr attributes in an OME-Zarr group.
    """

    ome: T


class BaseOMEAttrs(BaseAttrs):
    """
    Base class for attributes under an OME-Zarr group"""

    version: Literal["0.5"]


class BaseGroupv05(BaseGroup[BaseZarrAttrs[T]], Generic[T]):
    """
    Base class for all v0.5 OME-Zarr groups.
    """

    @property
    def ome_zarr_version(self) -> Literal["0.5"]:
        """
        OME-Zarr version.
        """
        return "0.5"
